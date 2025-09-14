import asyncio
import os

print(os.getenv("PYTHONPATH"))
from typing import Final

from discord import Client, Intents, Message
from Domain.server import server_thread

_TOKEN: Final = os.getenv("BOT_TOKEN")
if not _TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

_intents: Final = Intents.all()
_client: Final = Client(intents=_intents)

# 定期送信タスクを管理する辞書
_periodic_tasks = {}


# 起動時に動作する処理
@_client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print("ログインしました")


# メッセージ受信時の処理
@_client.event
async def on_message(message: Message):
    if message.author.bot:
        return

    # Botへのメンション + /ready コマンド
    if _client.user in message.mentions and message.content.strip().endswith("/ready"):
        channel_id = message.channel.id
        if channel_id not in _periodic_tasks:
            task = asyncio.create_task(periodic_message(message.channel))
            _periodic_tasks[channel_id] = task
            await message.channel.send("10秒ごとにメッセージを送信します。")

    # Botへのメンション + /end コマンド
    if _client.user in message.mentions and message.content.strip().endswith("/end"):
        channel_id = message.channel.id
        task = _periodic_tasks.pop(channel_id, None)
        if task:
            task.cancel()
            await message.channel.send("定期メッセージを終了しました。")
        else:
            await message.channel.send("定期メッセージは実行されていません。")


# 定期的に発言するタスク
async def periodic_message(channel):
    while True:
        await channel.send("定期メッセージです")
        await asyncio.sleep(10)  # 10秒ごとに発言


# サーバースレッドの起動
server_thread()

# Botの起動とDiscordサーバーへの接続
_client.run(_TOKEN)
