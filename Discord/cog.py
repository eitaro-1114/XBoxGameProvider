import asyncio
from datetime import datetime, timedelta
from typing import Final
from zoneinfo import ZoneInfo

from discord.ext import commands, tasks


class ReadyCog(commands.Cog):
    _READY_COMMAND: Final = "ready"
    _END_COMMAND: Final = "end"

    _TZ_NAME: Final = "Asia/Tokyo"

    _TARGET_TIME: Final = 16
    """テンプレートメッセージを送信する時刻（24時間制）"""

    def __init__(self, bot: commands.Bot) -> None:
        self.__bot = bot
        self.__channel_id = None

    async def cog_load(self) -> None:
        self.__daily_task.start()

    async def cog_unload(self) -> None:
        self.__daily_task.cancel()

    @commands.command(name=_READY_COMMAND)
    async def ready(self, ctx: commands.Context) -> None:
        """毎日16時にテンプレートメッセージを送信するコマンド"""
        if self.__channel_id is not None:
            await ctx.send("すでに /ready が実行されています。")
            return

        self.__channel_id = ctx.channel.id
        await ctx.send("毎日16時にテンプレートメッセージを送信します。")

    @commands.command(name=_END_COMMAND)
    async def end(self, ctx: commands.Context) -> None:
        """/ready で行う処理を停止するコマンド"""
        if self.__channel_id is None:
            await ctx.send("まだ /ready が実行されていません。")
            return

        self.__channel_id = None
        await ctx.send("/ready で行う処理を停止しました。")

    @tasks.loop(hours=24)
    async def __daily_task(self) -> None:
        """毎日16時にテンプレートメッセージを送信するタスク"""
        if self.__channel_id is None:
            return

        channel = self.__bot.get_channel(self.__channel_id)
        if channel is not None:
            await channel.send("これはテンプレートメッセージです。")

    @__daily_task.before_loop
    async def before_daily_task(self) -> None:
        # Bot が ready になるのを待つ
        await self.__bot.wait_until_ready()

        # 使うタイムゾーン
        tz = ZoneInfo(self._TZ_NAME)

        # 現在のタイムゾーンつき時刻
        now = datetime.now(tz)

        # 「今日の 16:00」を tz 付きで作る
        target = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=self._TARGET_TIME,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=tz,
        )

        # もし既に今日の 16:00 を過ぎている（または同時刻に開始したくない）なら翌日にする
        # 「同時刻に即時送信したい」場合は <= を < に変える
        if target <= now:
            target += timedelta(days=1)

        # 待つ秒数（float）
        delay_seconds = (target - now).total_seconds()

        # 実際に待機（event loop 内なので asyncio.sleep を使う）
        await asyncio.sleep(delay_seconds)
