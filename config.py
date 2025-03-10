import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    """ Class for holging configurable values """
    discord_bot_token: str
    database_file: str
    polling_interval_minutes: int

    @classmethod
    def load(cls):
        # Load environment variables from .env file
        load_dotenv()
        # Get Discord Bot Token from environment variables
        discord_bot_token  = os.environ.get("DISCORD_BOT_TOKEN")
        if not discord_bot_token:
            print("DISCORD_BOT_TOKEN is not set")
            exit(1)

        # Get database file path from environment variables (default: newshound.db)
        database_file= os.environ.get("DATABASE_FILE", "newshound.db")
        polling_interval_minutes = int(os.environ.get("POLLING_INTERVAL_MIN",10))  # Polling interval (minutes)
        return cls(discord_bot_token,database_file,polling_interval_minutes)
