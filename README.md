# Newshound 🐕‍🦺📰

<p align="center">
 <img src="newshound.png" alt="newshound logo" width="120px" height="120px"/>
</p>

Newshound is a Discord bot that sniffs out the latest news from your favorite RSS feeds and delivers it straight to your Discord server. Never miss a headline again - let Newshound do the digging for you!

## ✨ Features

-   **Subscribe to RSS Feeds:** Teach Newshound new tricks with the `/subscribe` command.
-   **Automatic News Delivery:** Newshound automatically fetches and barks out new articles from subscribed feeds.
-   **Unsubscribe with Ease:** Use the `/unsubscribe` command to manage which feeds Newshound fetches.
-   **Customizable Formatting:** Control the appearance of posts by making the simple change of code - make Newshound look its best!

## 🚀 Getting Started

### Prerequisites

-   Python 3.9 or higher
-   [Rye](https://rye-up.com/) for managing dependencies (keeps your project well-groomed!)
-   Docker (optional, for containerized deployment - a comfy kennel for Newshound)
-   A Discord Bot Token (See [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yuseiito/newshound.git
    cd newshound
    ```

2.  **Install dependencies using Rye:**

    ```bash
    rye sync
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the project root with the following content:

    ```
    DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
    DATABASE_FILE=newshound.db
    ```

    Replace `YOUR_DISCORD_BOT_TOKEN` with your actual Discord Bot Token.

4.  **(Optional) Run database migrations:**

    ```bash
    rye run alembic upgrade head
    ```

    This command sets up the database schema - ensures Newshound's got a solid foundation!

### Running the Bot

**Locally:**

```bash
rye run python newshound.py
```

**With Docker:**

1.  **Build the Docker image:**

    ```bash
    docker build -t newshound .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -d --name newshound-container -v newshound_data:/app -e DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN -e DATABASE_FILE=/app/newshound.db newshound
    ```

    Replace `YOUR_DISCORD_BOT_TOKEN` with your actual Discord Bot Token.

## ⚙️ Commands

-   `/subscribe <feed_url>`: Subscribes the current channel to the specified RSS feed.
-   `/unsubscribe`: Opens an interactive menu to manage which feeds are fetched.

## 🛠️ Configuration

The following environment variables can be configured:

-   `DISCORD_BOT_TOKEN`: The Discord Bot Token.
-   `DATABASE_FILE`: The path to the SQLite database file (where Newshound keeps its bones - err, data!).

## 🐳 Deployment

Newshound is designed to be easily deployed with [Coolify](https://coolify.io/). Simply connect your repository to Coolify and configure the necessary environment variables.

## 🤝 Contributing

Woof woof! Contributions are always welcome. Feel free to fork the repository, make your changes, and submit a pull request. Let's make Newshound the best news-fetching bot around!

## 📝 License

This project is licensed under the [GPL v3](LICENSE).
