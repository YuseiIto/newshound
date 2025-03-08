import feedparser
from dateutil import parser as dateparser

class Feed:
    def __init__(self, feed_url):
        self.feed_url = feed_url
        self.feed = feedparser.parse(feed_url)
        self.sorted_entries = sorted(
            self.entries, key=lambda x: dateparser.parse(x.published), reverse=True
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
            lambda entry: dateparser.parse(entry.published) # There is entry.published_parsed field, but it's not timezone aware so parsing it by dateutil
            > timestamp,
            self.sorted_entries,
        ))
