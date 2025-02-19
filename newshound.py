import discord
from discord.ext import commands, tasks
import feedparser
import sqlite3
import asyncio
import os
from dotenv import load_dotenv

# Alembic関連のインポート
from alembic import command
from alembic.config import Config

# .envファイルから環境変数をロード
load_dotenv()

# 環境変数からDiscord Bot Tokenを取得
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("DISCORD_BOT_TOKENが設定されていません")
    exit(1)

# 環境変数からデータベースファイルのパスを取得 (デフォルトは"newshound.db")
DATABASE_FILE = os.environ.get("DATABASE_FILE", "newshound.db")
POLLING_INTERVAL_MINUTES = 1  # ポーリング間隔 (分)

# Botの初期化
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{DATABASE_FILE}") # sqlalchemy.urlを動的に設定
    try:
        command.upgrade(alembic_cfg, "head") # headは最新のリビジョンを意味する
    except Exception as e:
        print(f"マイグレーションエラー: {e}")


# 購読情報をデータベースから取得
def get_subscriptions(channel_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT feed_url FROM subscriptions WHERE channel_id = ?", (channel_id,))
    subscriptions = cursor.fetchall()
    conn.close()
    return [row[0] for row in subscriptions] # feed_url のリストを返す

# 購読情報をデータベースに登録
def add_subscription(channel_id, feed_url):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subscriptions (channel_id, feed_url) VALUES (?, ?)", (channel_id, feed_url))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # 重複購読

# 購読情報をデータベースから削除
def remove_subscription(channel_id, feed_url):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscriptions WHERE channel_id = ? AND feed_url = ?", (channel_id, feed_url))
    conn.commit()
    conn.close()


# RSSフィードからニュースを取得し、チャンネルに送信
async def fetch_and_send_news():
    subscriptions = get_subscriptions_all() # すべての購読を取得
    for channel_id, feed_url in subscriptions:
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                channel = bot.get_channel(channel_id)
                if channel:
                    # 最新の記事を最大5件送信 (調整可能)
                    for entry in feed.entries[:5]:
                        embed = discord.Embed(
                            title=entry.title,
                            url=entry.link,
                            description=entry.get('summary', '記事概要はありません'), # summaryがなければデフォルト値を表示
                            color=discord.Color.blue()
                        )
                        await channel.send(embed=embed)
                else:
                    print(f"チャンネルが見つかりません: {channel_id}") #デバッグ用
        except Exception as e:
            print(f"RSSフィードの取得または送信に失敗: {feed_url}, エラー: {e}") #デバッグ用

def get_subscriptions_all():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, feed_url FROM subscriptions")
    subscriptions = cursor.fetchall()
    conn.close()
    return subscriptions


# 定期ポーリングタスク
@tasks.loop(minutes=POLLING_INTERVAL_MINUTES)
async def polling_task():
    await fetch_and_send_news()

# Bot起動時の処理
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました')
    run_migrations() # マイグレーションを実行
    polling_task.start()

# /subscribe コマンド
@bot.command(name='subscribe')
async def subscribe(ctx, feed_url: str):
    try:
        feed = feedparser.parse(feed_url)
        feed_name = feed.feed.get('title', None) # タイトルを取得
    except:
        feed_name = None

    if add_subscription(ctx.channel.id, feed_url):
        if feed_name:
            await ctx.send(f"このチャンネルで **{feed_name}** ({feed_url}) の購読を開始しました。")
        else:
            await ctx.send(f"このチャンネルで {feed_url} の購読を開始しました。")
    else:
        await ctx.send("すでに購読しています。")

# /unsubscribe コマンド
@bot.command(name='unsubscribe')
async def unsubscribe(ctx):
    subscriptions = get_subscriptions(ctx.channel.id)
    if not subscriptions:
        await ctx.reply("このチャンネルでは何も購読していません。")
        return

    view = await UnsubscribeSelectView.create(bot, ctx.channel.id, subscriptions) # UnsubscribeSelectViewを作成
    await ctx.reply("購読解除するフィードを選択してください:", view=view)  # viewを渡す

# 確認ボタン
class ConfirmButton(discord.ui.Button):
    def __init__(self, feed_url: str):
        super().__init__(style=discord.ButtonStyle.danger, label="確認")
        self.feed_url = feed_url

    async def callback(self, interaction: discord.Interaction):
        remove_subscription(interaction.channel_id, self.feed_url)
        await interaction.message.edit(content=f"{self.feed_url} の購読を解除しました。", view=None) # Viewを削除

class CancelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="キャンセル")

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.edit(content="購読解除をとりやめました。購読設定は変更されていません。", view=None) # Viewを削除


class ConfirmSelectionView(discord.ui.View):
    def __init__(self, feed_url,channel_id):
        super().__init__()
        self.channel_id = channel_id
        self.add_item(ConfirmButton(feed_url))
        self.add_item(CancelButton())

# フィードを選択するSelectMenu
class UnsubscribeSelect(discord.ui.Select):
    def __init__(self, feed_data: list[tuple[str,str]]): # feed_urlとfeed_nameのタプルのリストを受け取る
        options = []
        for feed_url, feed_name in feed_data:
            label = feed_name if feed_name else feed_url # フィード名があればそれを、なければURLをラベルにする
            options.append(discord.SelectOption(label=label, value=feed_url))
        super().__init__(placeholder="購読解除するフィードを選択...", options=options) # SelectMenuを初期化

    async def callback(self, interaction: discord.Interaction):
        #  Viewを更新して、ボタンの状態を反映する
        feed_url = self.values[0]
        await interaction.response.edit_message(content=f"本当に{feed_url} を購読解除しますか?",view=ConfirmSelectionView(feed_url,interaction.channel_id))


class UnsubscribeSelectView(discord.ui.View):
    def __init__(self, bot,subscriptions: list[str], feed_data: list[tuple[str,str]]):
        super().__init__()
        self.add_item(UnsubscribeSelect(feed_data))  # SelectMenuを追加
        self.add_item(CancelButton())
        #super().__init__(timeout=180) #タイムアウト設定

    @classmethod
    async def create(cls, bot, channel_id: int, subscriptions: list[str]):
        feed_data = []
        for feed_url in subscriptions:
            try:
                feed = feedparser.parse(feed_url)
                feed_name = feed.feed.get('title', None)
            except:
                feed_name = None
            feed_data.append((feed_url, feed_name))

        return cls(bot, subscriptions, feed_data)


# Botの起動
bot.run(TOKEN)
