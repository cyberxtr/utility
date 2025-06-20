# Telegram Button Bot

This directory contains a simple Telegram bot and a web-based admin panel.
The bot organizes files into categories using inline buttons and allows
broadcasting messages to all subscribers.

## Setup

1. Install dependencies:
   ```bash
   pip install flask python-telegram-bot==20.3
   ```

2. Set environment variables:
   - `TELEGRAM_BOT_TOKEN` – your bot token.
   - `TELEGRAM_ADMIN_IDS` – space separated list of Telegram user ids.
   - `WEB_ADMIN_TOKEN` – token for the web admin panel.

3. Run the bot:
   ```bash
   python -m telegram_bot.bot
   ```

4. Run the web admin panel:
   ```bash
   python -m telegram_bot.web_admin
   ```
   Open `http://localhost:5000/?token=<WEB_ADMIN_TOKEN>` to manage categories
   and broadcast messages.
