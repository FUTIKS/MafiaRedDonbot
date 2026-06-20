"""
Durable mirror of the bot's in-memory game state.

The bot runs as a single asyncio process (see management/commands/bot.py), so the
module-level dicts in ``mafia_bot.utils`` stay the authoritative working copy at
runtime.  Redis is only a *mirror* that lets state survive a process/container
restart.

Design — "write-through snapshot + rehydrate":
  * On startup ``rehydrate_all()`` loads every mirrored global back into the
    in-process dicts (mutating them IN PLACE) and resumes timers/games.
  * ``snapshot_loop()`` re-mirrors everything every few seconds.  Because the bot
    is single-threaded asyncio, building one snapshot is atomic w.r.t. the game
    loop, so no per-write hooks are needed in the ~40 mutation sites scattered
    across the handlers.

Not mirrored (rebuilt in-process):
  * ``game_tasks``  – asyncio.Task   (recreated by run_game_in_background)
  * ``game_locks``  – asyncio.Lock   (recreated lazily on acquire)
  * ``USER_LANG_CACHE`` – read-through cache of a DB column (self-heals from DB)

``games_state`` nests ``set`` objects and ``int``-keyed dicts, so serialization is
custom (see ``dumps``/``loads`` and ``_intify_keys``).
"""
import asyncio
import json
import logging

from django.conf import settings
from redis import asyncio as aioredis

from mafia_bot import utils

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Client singleton
# --------------------------------------------------------------------------- #
_redis = None


def get_redis() -> "aioredis.Redis":
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


# --------------------------------------------------------------------------- #
# Key scheme (everything namespaced under "mafia:")
# --------------------------------------------------------------------------- #
K_GAME = "mafia:game:{}"            # per game_id (one JSON blob each)
K_GAME_INDEX = "mafia:game:index"   # SET of live game_ids

# Each flat global is mirrored as ONE JSON blob.  Replacing the whole blob on
# every snapshot means deletions need no special handling — the next snapshot
# simply no longer contains the popped key.
FLAT_GLOBALS = (
    "writing_allowed_groups",
    "chat_id_game_id",
    "team_chat_sessions",
    "active_role_used",
    "notify_users",
    "group_users",
    "giveaways",
    "stones_taken",
    "gsend_taken",
    "last_wishes",
)
K_FLAT = "mafia:flat:{}"


# --------------------------------------------------------------------------- #
# Set-aware JSON (sets are not JSON-native; we tag them so they round-trip)
# --------------------------------------------------------------------------- #
_SET_TAG = "__set__"


def _default(o):
    if isinstance(o, set):
        return {_SET_TAG: list(o)}
    raise TypeError(f"{type(o)} is not JSON-serializable: {o!r}")


def _object_hook(d):
    if len(d) == 1 and _SET_TAG in d:
        return set(d[_SET_TAG])
    return d


def dumps(obj) -> str:
    return json.dumps(obj, default=_default, ensure_ascii=False)


def loads(s: str):
    return json.loads(s, object_hook=_object_hook)


def _intify_keys(obj):
    """Recursively turn all-digit dict keys back into ``int``.

    Game/flat blobs nest dicts keyed by tg_id / chat_id (``effects``,
    ``kills.shooted``, ``users_map``, ``notify_users`` ...).  JSON forces object
    keys to strings, so after a reload those numeric lookups would miss.  This
    restores them.  ``stones_taken`` may use a username (non-numeric) key, which
    correctly stays a string.
    """
    if isinstance(obj, dict):
        return {
            (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): _intify_keys(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_intify_keys(v) for v in obj]
    return obj


# --------------------------------------------------------------------------- #
# games_state — per-game blobs + index
# --------------------------------------------------------------------------- #
_RUNTIME_EVENT_KEYS = ("night_event", "hang_event", "confirm_event")


def _strip_for_snapshot(game: dict) -> dict:
    """Return a JSON-safe shallow copy with asyncio.Event runtime handles dropped.

    ``pending_*`` sets stay (set-tagged by ``dumps``).  The loop recreates the
    Events via ``prepare_*_pending`` before every ``await event.wait()``, so a
    rehydrated game (events = None) is structurally valid.  This runs synchronously
    (no await), so it is atomic against the single-threaded game loop.
    """
    g = dict(game)
    rt = dict(game.get("runtime", {}))
    for k in _RUNTIME_EVENT_KEYS:
        rt[k] = None
    g["runtime"] = rt
    return g


async def save_game(game_id: int, game: dict) -> None:
    """Atomically mirror one game.  Never raises into the caller."""
    try:
        payload = dumps(_strip_for_snapshot(game))  # build fully before SET (no torn write)
        r = get_redis()
        await r.set(K_GAME.format(game_id), payload)
        await r.sadd(K_GAME_INDEX, game_id)
    except Exception:
        logger.exception("save_game(%s) failed", game_id)


async def load_game(game_id: int):
    raw = await get_redis().get(K_GAME.format(game_id))
    return _intify_keys(loads(raw)) if raw else None


async def delete_game(game_id: int) -> None:
    try:
        r = get_redis()
        await r.delete(K_GAME.format(game_id))
        await r.srem(K_GAME_INDEX, game_id)
    except Exception:
        logger.exception("delete_game(%s) failed", game_id)


# --------------------------------------------------------------------------- #
# Snapshot — mirror everything (called periodically; cheap, single-threaded)
# --------------------------------------------------------------------------- #
async def snapshot_once() -> None:
    r = get_redis()
    # games: write every live game, then prune Redis entries for games that ended
    live_ids = set(utils.games_state.keys())
    for gid, game in list(utils.games_state.items()):
        await save_game(gid, game)
    try:
        stale = {int(x) for x in await r.smembers(K_GAME_INDEX)} - live_ids
        for gid in stale:
            await delete_game(gid)
    except Exception:
        logger.exception("snapshot_once: index reconcile failed")

    # flat globals: one blob each (whole-value replace handles deletions)
    for name in FLAT_GLOBALS:
        try:
            await r.set(K_FLAT.format(name), dumps(getattr(utils, name)))
        except Exception:
            logger.exception("snapshot_once: flat %s failed", name)


async def snapshot_loop(interval: int = 8) -> None:
    while True:
        await asyncio.sleep(interval)
        try:
            await snapshot_once()
        except Exception:
            logger.exception("snapshot_loop iteration failed")


# --------------------------------------------------------------------------- #
# Rehydrate on startup.  MUST mutate utils.* dicts IN PLACE — handlers imported
# the names by value (``from mafia_bot.utils import giveaways``), so rebinding
# ``utils.giveaways = {...}`` would desync every importer.
# --------------------------------------------------------------------------- #
def _replace_in_place(target, value) -> None:
    if isinstance(target, dict):
        target.clear()
        target.update(value or {})
    elif isinstance(target, list):
        target[:] = value or []


async def rehydrate_all() -> None:
    """Load every mirrored global back into the in-process dicts, then resume
    timers/games.  Tolerates Redis being unavailable (fresh start)."""
    try:
        await get_redis().ping()
    except Exception:
        logger.exception("Redis unavailable at startup — starting with empty state")
        return

    await _rehydrate_flat()
    await _rehydrate_giveaways()
    await _rehydrate_games()


async def _rehydrate_flat() -> None:
    r = get_redis()
    for name in FLAT_GLOBALS:
        try:
            raw = await r.get(K_FLAT.format(name))
            if raw is None:
                continue
            value = _intify_keys(loads(raw))
            _replace_in_place(getattr(utils, name), value)
        except Exception:
            logger.exception("_rehydrate_flat: %s failed", name)


async def _rehydrate_giveaways() -> None:
    """Re-arm the payout timer for every restored giveaway.  ``finish_giveaway``
    self-corrects via ``end_at - now`` (fires immediately if already elapsed)."""
    if not utils.giveaways:
        return
    try:
        from mafia_bot.handlers.command_handlers import finish_giveaway
        from dispatcher import bot
    except Exception:
        logger.exception("_rehydrate_giveaways: import failed")
        return
    for chat_id in list(utils.giveaways.keys()):
        try:
            asyncio.create_task(finish_giveaway(chat_id, bot))
        except Exception:
            logger.exception("_rehydrate_giveaways: re-arm %s failed", chat_id)


async def _rehydrate_games() -> None:
    """Clean up games that were live when the process died.

    ``start_game`` (game_handler.py) is written to run a game from Day 1 with a
    fresh intro and is NOT resumable mid-loop — re-invoking it would replay the
    intro and corrupt state.  So on restart we do NOT silently leave a dead game
    in limbo (the current behaviour) nor risk a broken resume; instead we tear the
    game down cleanly and notify the group, which also frees the chat for a new
    ``/game``.  (A true mid-game resume would require making ``start_game``
    resumable — tracked as future work.)
    """
    from asgiref.sync import sync_to_async
    from mafia_bot.models import Game
    from mafia_bot.handlers.main_functions import send_safe_message, get_lang_text
    from mafia_bot.handlers.command_handlers import stop_registration

    r = get_redis()
    try:
        ids = [int(x) for x in await r.smembers(K_GAME_INDEX)]
    except Exception:
        logger.exception("_rehydrate_games: cannot read index")
        return

    for game_id in ids:
        chat_id = None
        try:
            game = await load_game(game_id)
            chat_id = (game or {}).get("meta", {}).get("chat_id")
            db_game = await sync_to_async(Game.objects.filter(id=game_id).first)()

            # already finished / never active → just drop the mirror
            if not db_game or db_game.is_ended or not db_game.is_active_game:
                utils.games_state.pop(game_id, None)
                if chat_id is not None:
                    utils.chat_id_game_id.pop(chat_id, None)
                    utils.writing_allowed_groups.pop(chat_id, None)
                await delete_game(game_id)
                continue

            if not db_game.is_started:
                # lobby phase → canonical registration teardown
                await stop_registration(chat_id=db_game.chat_id, instant=True)
            else:
                # in-progress game → end it cleanly and notify the group
                await sync_to_async(
                    Game.objects.filter(id=game_id).update
                )(is_active_game=False, is_started=False, is_ended=True)
                if chat_id is not None:
                    t = get_lang_text(chat_id)
                    msg = t.get("game_aborted_restart") if isinstance(t, dict) else None
                    await send_safe_message(
                        chat_id,
                        text=msg or "♻️ Bot qayta ishga tushdi — joriy o'yin to'xtatildi. /game bilan yangisini boshlang.",
                    )

            utils.games_state.pop(game_id, None)
            if chat_id is not None:
                utils.chat_id_game_id.pop(chat_id, None)
                utils.writing_allowed_groups.pop(chat_id, None)
            await delete_game(game_id)
        except Exception:
            logger.exception("_rehydrate_games: failed to clean up game %s", game_id)
