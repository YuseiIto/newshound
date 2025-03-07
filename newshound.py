import discord
from discord.ext import commands, tasks
from datetime import datetime

from config import Config
from migrations import run_migrations
from repository import Repository
from feed import Feed
import ui

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True

config = Config.load()


class NewshoundBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        polling_task.start()
        print("Bot setup completed")


bot = NewshoundBot(intents)

CONTENT_HEADER_TEMPLATE = (
    "### :new: New articles from {feed_title} at {time} ({entries_count} articles)"
)
CONTENT_ITEM_TEMPLATE = (
    "- {title}\t[Read more](<{link}>)"  # use <> to force link not to enriched
)


async def send_feed_updates(channel, feed, entries):
    """Sends feed updates to a Discord channel."""
    if entries and len(entries) > 0:
        content = CONTENT_HEADER_TEMPLATE.format(
            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            entries_count=len(entries),
            feed_title=feed.title,
        )
        for entry in entries:
            content += "\n" + CONTENT_ITEM_TEMPLATE.format(
                title=entry.title, link=entry.link
            )

        content += "\n\n"
        await channel.send(content=content)


# Fetch news from RSS feeds and send to the channel
async def fetch_and_send_news():
    subscriptions = Repository(config).get_subscriptions_all()  # Get all subscriptions
    for channel_id, feed_url, last_checked_str in subscriptions:
        try:
            feed = Feed(feed_url)
            last_checked = datetime.fromisoformat(last_checked_str)
            entries = feed.newer_entries_than(last_checked)
            entries.reverse()
            channel = bot.get_channel(channel_id)
            if channel:
                await send_feed_updates(channel, feed, entries)
            Repository(config).update_last_checked(
                channel_id, feed_url
            )  # Update the last checked time
        except Exception as e:
            print(
                f"Failed to retrieve or send RSS feed: {feed_url}, Error: {e}"
            )  # Debugging


# Periodic polling task
@tasks.loop(minutes=config.polling_interval_minutes)
async def polling_task():
    await fetch_and_send_news()


@bot.event
async def on_ready():
    print(f"Connected: {bot.user} logged in")


# /subscribe Command
@bot.command(name="subscribe")
async def subscribe(ctx, feed_url: str):
    feed = Feed(feed_url)
    repo = Repository(config)
    if not repo.add_subscription(ctx.channel.id, feed_url):
        await ctx.reply("Already subscribed to this feed.")
        return

    await ctx.reply(f"Started subscribing to {feed.pretty_label} in this channel.")
    try:
        await send_feed_updates(ctx.channel, feed, feed.recent_entries())
    except Exception as e:
        print(f"Failed to send initial articles: {feed_url}, Error: {e}")
    repo.update_last_checked(ctx.channel.id, feed_url)  # Update last checked time


# /unsubscribe Command
@bot.command(name="unsubscribe")
async def unsubscribe(ctx):
    subscriptions = Repository(config).get_subscriptions(ctx.channel.id)
    if not subscriptions:
        await ctx.reply("Not subscribed to any feeds in this channel.")
        return

    view = await ui.UnsubscribeSelectView.create(
        bot, ctx.channel.id, subscriptions
    )  # Create UnsubscribeSelectView
    await ctx.reply("Select the feed to unsubscribe from:", view=view)  # Pass the view


if __name__ == "__main__":
    run_migrations(config)
    # Start the bot
    bot.run(config.discord_bot_token)
