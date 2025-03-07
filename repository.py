import sqlite3
from config import Config
from datetime import datetime, timezone

class Repository:
    def __init__(self,config: Config):
        self._config = config
        self._conn = sqlite3.connect(config.database_file)

    def __del__(self):
        self._conn.close()

    def get_subscriptions_all(self):
        cursor = self._conn.cursor()
        cursor.execute("SELECT channel_id, feed_url,last_checked FROM subscriptions")
        subscriptions = cursor.fetchall()
        return subscriptions

    def get_subscriptions(self,channel_id:str)->list[str]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT feed_url FROM subscriptions WHERE channel_id = ?", (channel_id,)
        )
        subscriptions = cursor.fetchall()
        return [row[0] for row in subscriptions]  # Return list of feed_url


    def add_subscription(self,channel_id:str, feed_url:str)->bool:
        """Add subscription information to the database"""
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "INSERT INTO subscriptions (channel_id, feed_url, last_checked) VALUES (?, ?, ?)",
                (channel_id, feed_url, datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate Subscription


    def update_last_checked(self,channel_id:str, feed_url:str):
        """Update last checked timestamp"""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE subscriptions SET last_checked = ? WHERE channel_id = ? AND feed_url = ?",
            (datetime.now(timezone.utc).isoformat(), channel_id, feed_url),
        )
        self._conn.commit()

    def remove_subscription(self,channel_id:str, feed_url:str):
        """Remove subscription information from the database"""
        cursor = self._conn.cursor()
        cursor.execute(
            "DELETE FROM subscriptions WHERE channel_id = ? AND feed_url = ?",
            (channel_id, feed_url),
        )
        self._conn.commit()
