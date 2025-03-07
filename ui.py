import discord
from config import Config
from repository import Repository
from feed import Feed

# Confirm Button
class ConfirmButton(discord.ui.Button):
    def __init__(self, feed_url: str):
        super().__init__(style=discord.ButtonStyle.danger, label="Unsubscribe")
        self.feed_url = feed_url

    async def callback(self, interaction: discord.Interaction):
        Repository(Config.load()).remove_subscription(interaction.channel_id, self.feed_url)
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
            feed = Feed(feed_url)
            feed_name = feed.title if feed.title else feed_url
            feed_data.append((feed_url, feed_name))

        return cls(bot, subscriptions, feed_data)
