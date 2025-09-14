import os
from typing import Final

from discord import Intents
from Discord.client import XBoxGameClient

# 自パッケージ
from Domain.server import server_thread

_TOKEN: Final = os.getenv("BOT_TOKEN")
if not _TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Discordクライアントの初期化
_intents: Final = Intents.default()
_intents.message_content = True
_client: Final = XBoxGameClient(command_prefix="!", intents=_intents)

# デプロイ用サーバーを起動
server_thread()

# Botを起動
_client.run(_TOKEN)
