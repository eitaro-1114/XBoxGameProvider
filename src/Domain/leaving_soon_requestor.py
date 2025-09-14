import json
from pathlib import Path
from typing import Final

import requests
from Domain import logger
from Domain.xbox_game import XboxGame

# Xbox Game Passの全ゲームを取得するためのリクエスト URL
_GAMES_REQUEST_URL: Final = (
    "https://catalog.gamepass.com/products?market=JP&language=ja&hydration=MobileDetailsForConsole"
)

# Xbox Game Passの「まもなく終了」リストを取得するためのリクエスト URL
_LEAVING_SOON_REQUEST_URL: Final = (
    "https://catalog.gamepass.com/sigls/v2?id=393f05bf-e596-4ef6-9487-6d4fa0eab987&market=JP&language=ja-JP"
)

# 前回取得した「まもなく終了」ゲームのIDリストを保存するキャッシュファイルのパス
_LEAVING_GAME_IDS_CACHE_PATH: Final = Path(__file__).parent.parent / ".data" / "leaving_game_ids.json"

_logger: Final = logger.get_logger(__name__)


def _request_leaving_ids() -> list[str]:
    """Xbox Game Passの「まもなく終了」に登録されているゲームのIDリストを取得する。
    まもなく終了のページは https://www.xbox.com/ja-jp/play/gallery/leaving-soon から確認できる。

    Returns:
        list[str]: まもなく終了するゲームのIDリスト
    """
    response = requests.get(_LEAVING_SOON_REQUEST_URL)
    response.raise_for_status()

    game_ids: list[str] = []

    data = response.json()
    for item in data:
        if "id" in item:
            game_ids.append(item["id"])

    _logger.info("Leaving soon games: %s", game_ids)

    return game_ids


def get_leaving_games(use_cache: bool = True) -> list[XboxGame]:
    """まもなく終了するゲームの情報を取得する。

    Args:
        use_cache (bool, optional): キャッシュを使用するかどうか. Defaults to True.

    Returns:
        list[XboxGame]: まもなく終了するゲームのリスト
    """

    # まもなく終了するゲームのIDリストを取得
    ids = _request_leaving_ids()

    if use_cache:
        # 前回取得したIDリストをキャッシュファイルから読み込み
        cached_ids: list[str] = []
        if _LEAVING_GAME_IDS_CACHE_PATH.exists():
            with open(_LEAVING_GAME_IDS_CACHE_PATH, "r", encoding="utf-8") as f:
                cached_ids = json.load(f)

        # 前回取得したIDリストと比較して、新しいIDを検出
        new_ids = [game_id for game_id in ids if game_id not in cached_ids]
    else:
        new_ids = ids

    if not new_ids:
        _logger.info("No new leaving soon games.")
        return []

    payload = {"Products": new_ids}
    headers = {"Content-Type": "application/json"}

    # まもなく終了するゲームの情報を取得
    response = requests.post(_GAMES_REQUEST_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    games = []

    # まもなく終了するゲームの情報を抽出
    products = data.get("Products", [])
    for product_id in products:
        product = products[product_id]

        game = XboxGame.create(product)

        games.append(game)

    # 現在のIDリストをキャッシュファイルに保存
    _LEAVING_GAME_IDS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_LEAVING_GAME_IDS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(ids, f)

    return games


def clear_cache() -> None:
    """キャッシュファイルを削除する。"""
    if _LEAVING_GAME_IDS_CACHE_PATH.exists():
        _LEAVING_GAME_IDS_CACHE_PATH.unlink()
        _logger.info("Cache file deleted: %s", _LEAVING_GAME_IDS_CACHE_PATH)
    else:
        _logger.info("Cache file does not exist: %s", _LEAVING_GAME_IDS_CACHE_PATH)
