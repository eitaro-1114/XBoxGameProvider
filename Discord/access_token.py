import json
from pathlib import Path
from typing import Final

_ACCESS_TOKEN_JSON_PATH: Final = Path(__file__).parent / ".data" / "access_token.json"


def load_access_token() -> str:
    """保存されているDiscord Botのアクセストークンを読み込む。

    Returns:
        str: 読み込んだアクセストークン
    """

    if not _ACCESS_TOKEN_JSON_PATH.exists():
        raise FileNotFoundError(f"{_ACCESS_TOKEN_JSON_PATH} does not exist")

    with open(_ACCESS_TOKEN_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["Token"]
