import os
from typing import Final

from discord import Intents
from Discord.cog import ReadyCog
from discord.ext import commands

# 自パッケージ
from Domain.server import server_thread

_TOKEN: Final = os.getenv("BOT_TOKEN")
if not _TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

_intents: Final = Intents.default()
_bot: Final = commands.Bot(command_prefix="!", intents=_intents)


# サーバースレッドの起動
server_thread()

_bot.add_cog(ReadyCog(_bot))
_bot.run(_TOKEN)
