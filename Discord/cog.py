from typing import Final

from discord.ext import commands, tasks


class ReadyCog(commands.Cog):
    _READY_COMMAND: Final = "ready"
    _END_COMMAND: Final = "end"

    _TARGET_TIME: Final = 16
    """テンプレートメッセージを送信する時刻（24時間制）"""

    def __init__(self, bot: commands.Bot) -> None:
        self.__bot = bot
        self.__channel_id = None
        self.__daily_task.start()

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
        """タスク開始前の待機"""
        await self.__bot.wait_until_ready()
        now = self.__bot.loop.time()

        target_time = (self._TARGET_TIME - (now % 24)) % 24
        await self.__bot.loop.sleep(target_time)
