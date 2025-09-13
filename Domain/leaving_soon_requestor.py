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


def get_leaving_games() -> list[XboxGame]:
    """まもなく終了するゲームの情報を取得する。

    Returns:
        list[XboxGame]: まもなく終了するゲームのリスト
    """

    # まもなく終了するゲームのIDリストを取得
    ids = _request_leaving_ids()

    payload = {"Products": ids}
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

    return games
