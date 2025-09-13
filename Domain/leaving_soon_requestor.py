from typing import Final

import requests
from Domain import logger

# Xbox Game Passの「まもなく終了」リストを取得するためのリクエスト URL
_REQUEST_URL: Final = (
    "https://catalog.gamepass.com/sigls/v2?id=393f05bf-e596-4ef6-9487-6d4fa0eab987&market=JP&language=ja-JP"
)

_logger: Final = logger.get_logger(__name__)


def request_leavings() -> list[str]:
    """Xbox Game Passの「まもなく終了」に登録されているゲームのIDリストを取得する。
    まもなく終了のページは https://www.xbox.com/ja-jp/play/gallery/leaving-soon から確認できる。

    Returns:
        list[str]: まもなく終了するゲームのIDリスト
    """
    response = requests.get(_REQUEST_URL)
    response.raise_for_status()

    game_ids: list[str] = []

    data = response.json()
    for item in data:
        if "id" in item:
            game_ids.append(item["id"])

    _logger.info("Leaving soon games: %s", game_ids)

    return game_ids


if __name__ == "__main__":
    request_leavings()
