import feedparser
from datetime import datetime,timezone

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
