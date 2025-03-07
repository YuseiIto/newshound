import discord
from discord.ext import commands, tasks
import feedparser
from datetime import datetime, timezone
import logging

from config import Config
from migrations import run_migrations
from repository import Repository

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()


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
            Repository(config).update_last_checked(channel_id, feed_url)  # Update the last checked time
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


class Feed:
    def __init__(self, feed_url):
        self.feed_url = feed_url
        self.feed = feedparser.parse(feed_url)
        self.sorted_entries = sorted(
            self.entries, key=lambda x: x.published_parsed, reverse=True
        )

    @property
    def pretty_label(self):
        return f"**{self.title}** ({self.url})" if self.title else self.url

    @property
    def title_or_url(self):
        return self.feed.feed.get("title", self.feed_url)

    @property
    def title(self):
        return self.feed.feed.get("title")

    @property
    def entries(self):
        return self.feed.entries

    @property
    def url(self):
        return self.feed_url

    def recent_entries(self, count=5):
        return self.entries[:count]

    def newer_entries_than(self, timestamp):
        return list(filter(
            lambda entry: datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            > timestamp,
            self.sorted_entries,
        ))


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

    view = await UnsubscribeSelectView.create(
        bot, ctx.channel.id, subscriptions
    )  # Create UnsubscribeSelectView
    await ctx.reply("Select the feed to unsubscribe from:", view=view)  # Pass the view


# Confirm Button
class ConfirmButton(discord.ui.Button):
    def __init__(self, feed_url: str):
        super().__init__(style=discord.ButtonStyle.danger, label="Unsubscribe")
        self.feed_url = feed_url

    async def callback(self, interaction: discord.Interaction):
        Repository(config).remove_subscription(interaction.channel_id, self.feed_url)
        await interaction.message.edit(
            content=f"Unsubscribed from {self.feed_url}.", view=None
        )  # Remove View


class CancelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Cancel")

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.edit(
            content="Unsubscription canceled. Subscription settings have not been changed.",
            view=None,
        )  # Remove View


class ConfirmSelectionView(discord.ui.View):
    def __init__(self, feed_url, channel_id):
        super().__init__()
        self.channel_id = channel_id
        self.add_item(ConfirmButton(feed_url))
        self.add_item(CancelButton())


# Select Menu to choose the feed
class UnsubscribeSelect(discord.ui.Select):
    def __init__(
        self, feed_data: list[tuple[str, str]]
    ):  # List of tuples of feed_url and feed_name
        options = []
        for feed_url, feed_name in feed_data:
            label = (
                feed_name if feed_name else feed_url
            )  # Use feed name if available, otherwise use URL
            options.append(discord.SelectOption(label=label, value=feed_url))
        super().__init__(
            placeholder="Select a feed to unsubscribe from...", options=options
        )  # Initialize SelectMenu

    async def callback(self, interaction: discord.Interaction):
        #  Update View to reflect button states
        feed_url = self.values[0]
        await interaction.response.edit_message(
            content=f"Are you sure want to unsubscribe from {feed_url}?",
            view=ConfirmSelectionView(feed_url, interaction.channel_id),
        )


class UnsubscribeSelectView(discord.ui.View):
    def __init__(self, bot, subscriptions: list[str], feed_data: list[tuple[str, str]]):
        super().__init__()
        self.add_item(UnsubscribeSelect(feed_data))  # Add SelectMenu
        self.add_item(CancelButton())
        # super().__init__(timeout=180) #Timeout setting

    @classmethod
    async def create(cls, bot, channel_id: int, subscriptions: list[str]):
        feed_data = []
        for feed_url in subscriptions:
            try:
                feed = feedparser.parse(feed_url)
                feed_name = feed.feed.get("title", None)
            except:
                feed_name = None
            feed_data.append((feed_url, feed_name))

        return cls(bot, subscriptions, feed_data)


if __name__ == "__main__":
    run_migrations(config)
    # Start the bot
    bot.run(config.discord_bot_token, log_handler=log_handler)
