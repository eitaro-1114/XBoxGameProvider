import asyncio
import os
from datetime import datetime, timedelta
from typing import Final, Optional
from zoneinfo import ZoneInfo

from discord import Client, Intents, Interaction, Object, TextChannel
from discord.app_commands import CommandTree
from discord.ext import tasks
from Domain.leaving_soon_requestor import clear_cache, get_leaving_games
from Domain.logger import get_logger

_GUILD_ID: Final = Object(id=os.getenv("GUILD_ID"))
_logger: Final = get_logger(__name__)


class XBoxGameClient(Client):
    _TARGET_HOUR: Final = 18
    _TZ: Final = ZoneInfo("Asia/Tokyo")

    def __init__(self, command_prefix: str, intents: Intents) -> None:
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.tree = CommandTree(self)

        # 内部状態
        self.__channel_id: Optional[int] = None

        self.__setup_commands()

    async def on_ready(self) -> None:
        _logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

        synced = await self.tree.sync(guild=_GUILD_ID)

        _logger.info(f"Synced {len(synced)} commands to guild {_GUILD_ID.id}")

    @tasks.loop(hours=24)
    async def observe_leaving_games(self) -> None:
        channel = self.get_channel(self.__channel_id)

        if channel is None:
            _logger.warning("Channel is None, stopping the task.")
            return

        await self.__send_leaving_soon_games(channel)

    @observe_leaving_games.before_loop
    async def before_observe_leaving_games(self) -> None:
        await self.wait_until_ready()

        # 毎日指定した時刻まで待機
        now = datetime.now(self._TZ)
        target = datetime(now.year, now.month, now.day, self._TARGET_HOUR, 0, 0, tzinfo=self._TZ)
        if target <= now:
            target += timedelta(days=1)

        await asyncio.sleep((target - now).total_seconds())

    def __setup_commands(self) -> None:
        """Botのスラッシュコマンドを設定する"""

        @self.tree.command(
            name="ready",
            description=f"毎日{self._TARGET_HOUR}時にXBox Game Passのまもなく終了するゲーム情報を送信します",
            guild=_GUILD_ID,
        )
        async def ready(interaction: Interaction) -> None:
            """指定した時刻にXBox Game Passのまもなく終了するゲーム情報を送信します"""
            if self.__channel_id is not None:
                await interaction.response.send_message("すでに /ready が実行されています。")
                return

            self.__channel_id = interaction.channel.id
            await interaction.response.send_message(
                f"毎日{self._TARGET_HOUR}時にXBox Game Passのまもなく終了するゲーム情報を送信します"
            )

            self.observe_leaving_games.start()

        @self.tree.command(name="end", description="/ready で行う処理を停止します", guild=_GUILD_ID)
        async def end(interaction: Interaction) -> None:
            """ready で行う処理を停止します"""

            if self.__channel_id is None:
                await interaction.response.send_message("まだ /ready が実行されていません。")
                return

            self.__channel_id = None
            await interaction.response.send_message("/ready で行う処理を停止しました。")

            self.observe_leaving_games.cancel()

        @self.tree.command(
            name="request", description="まもなく終了するゲームの情報を取得して送信します", guild=_GUILD_ID
        )
        async def request(interaction: Interaction) -> None:
            """まもなく終了するゲームの情報を取得して送信します"""

            await interaction.response.send_message("まもなく終了するゲームの情報を取得しています...")

            channel = interaction.channel
            if not isinstance(channel, TextChannel):
                await interaction.followup.send("このコマンドはテキストチャンネルでのみ使用できます。")
                return

            await self.__send_leaving_soon_games(channel, use_cache=False)

        @self.tree.command(
            name="clear", description="まもなく終了するゲームの情報のキャッシュをクリアします", guild=_GUILD_ID
        )
        async def clear(interaction: Interaction) -> None:
            """まもなく終了するゲームの情報のキャッシュをクリアします"""
            clear_cache()

            await interaction.response.send_message("キャッシュをクリアしました。")

    async def __send_leaving_soon_games(self, channel: TextChannel, use_cache: bool = True) -> None:
        """まもなく終了するゲームの情報を取得して指定したチャンネルに送信する。"""

        leaving_games = get_leaving_games(use_cache=use_cache)

        if not leaving_games:
            await channel.send("まもなく終了するゲームはありません。")
            return

        for game in leaving_games:
            message = f"""
            ## 【終了予定】{game.title}\n{game.image_url}\n```{game.description}```
            """

            await channel.send(message)

            # Discordのレート制限を避けるために少し待機
            await asyncio.sleep(1)
