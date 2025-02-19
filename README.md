# Newshound 📰

![Newshound Logo](newshound.png)

Newshound is a Discord bot that delivers news from your favorite RSS feeds directly to your server.
Stay informed without ever leaving Discord!

> newshound [noun] a reporter who puts a lot of effort into discovering new stories [Cambridge English Dictionary](https://dictionary.cambridge.org/dictionary/english/newshound)

## ✨ Features

-   **Subscribe to RSS Feeds:** Use the `/subscribe` command to add your favorite RSS feeds to a channel.
-   **Automatic News Delivery:** Newshound automatically fetches and posts new articles from subscribed feeds.
-   **Unsubscribe with Ease:** Use the `/unsubscribe` command to manage your subscriptions with an interactive menu.
-   **Customizable Formatting:** Control the appearance of news posts with flexible manner.

## 🚀 Getting Started

### Prerequisites

-   Python 3.9 or higher
-   [Rye](https://rye-up.com/) for managing dependencies
-   Docker (optional, for containerized deployment)
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

    This command sets up the database schema.

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
   replace `YOUR_DISCORD_BOT_TOKEN` with your actual Discord Bot Token.

## ⚙️ Commands

-   `/subscribe <feed_url>`: Subscribes the current channel to the specified RSS feed.
-   `/unsubscribe`: Opens an interactive menu to unsubscribe from feeds.

## 🛠️ Configuration

The following environment variables can be configured:

-   `DISCORD_BOT_TOKEN`: The Discord Bot Token.
-   `DATABASE_FILE`: The path to the SQLite database file.

## 🐳 Deployment

Newshound is designed to be easily deployed with [Coolify](https://coolify.io/). 
Simply connect your repository to Coolify and configure the necessary environment variables.

## 🤝 Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## 📝 License

This project is licensed under the [GPL v3](LICENSE).
