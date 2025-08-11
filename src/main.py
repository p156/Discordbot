#モジュールの呼び出し
import discord
import os
import re
import numpy as np
from discord import app_commands
from discord.ext import commands
from keep import keep_alive
from parse import parse



#接続に必要なオブジェクトを生成
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)




#アクティビティステータス
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    bot.tree.clear_commands(guild=None)
    await client.change_presence(activity=discord.CustomActivity(name="ダイスを振るときは心して振れ"))
    await tree.sync()


#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    if message.author.bot:
        return

    #メッセージが送信されたチャンネルへメッセージを送信
    if message.content.startswith("#help"):
        await message.channel.send("bot導入したサーバで下記のように書き込むとダイスを振った結果を教えてくれます")
        await message.channel.send("入力例")
        await message.channel.send("#dice 1d100")
        await message.channel.send("#dice 1d3 + 2")
        await message.channel.send("#dice 1d6 + 1d3")

    if not re.match(r'#dice .*', message.content, re.IGNORECASE):
      return

    # 前処理：大文字Dを小文字dに変換、空白除去
    content = message.content.replace('#dice ', '').replace(' ', '').lower()
    dice_sets = content.split('+')
    formatted_expression = ' + '.join(dice_sets)

    total_result = 0
    response_parts = []

    for dice_set in dice_sets:
        if 'd' not in dice_set:
            # 単なる数値（例: "+5"）
            value = int(dice_set)
            total_result += value
            response_parts.append(str(value))
        else:
            # ダイスのロール処理（例: "2d6"）
            try:
                num_dice, die_size = map(int, dice_set.split('d'))
                rolls = [np.random.randint(1, die_size + 1) for _ in range(num_dice)]
                total_result += sum(rolls)
                roll_str = ' + '.join(str(r) for r in rolls)
                response_parts.append(roll_str)
            except ValueError:
                await message.reply(f"無効なダイス式: {dice_set}", mention_author=True)
                return

# レスポンス構築
    response = f"{formatted_expression}: {' + '.join(response_parts)} = {total_result}"
    await message.reply(response, mention_author=True)

#過労死用プログラム
keep_alive()
try:
    client.run(os.environ['TOKEN'])
except:
    os.system("kill")