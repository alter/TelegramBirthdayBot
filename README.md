# Telegram Birthday Bot

Bot for birthday notifications in Telegram chats/groups.

## Setup

1. Clone repository:
```bash
git clone https://github.com/alter/TelegramBirthdayBot.git
cd TelegramBirthdayBot
```

2. Create `.env` file with your settings:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token  # Get from @BotFather
TELEGRAM_CHAT_ID=your_chat_id      # Chat/Group ID where bot will send notifications
CSV_PATH=/app/data/birthdays.csv   # Path to CSV file inside container
```

3. Prepare birthdays data file:
```bash
mkdir -p data
touch data/birthdays.csv
```

4. Add birthdays to `data/birthdays.csv`:
```csv
John Doe,01-01,@johndoe
Jane Doe,31-12,@janedoe
```

Required CSV format:
- No header row
- Three columns: Name, Date (DD-MM), Telegram Username
- Telegram Username is optional
- Date must be in DD-MM format
- Each field should be trimmed from spaces

5. Build and run:
```bash
docker-compose build
docker-compose up -d
```

## Commands

- `/start` - Start bot
- `/help` - Show available commands
- `/today` - Show today's birthdays
- `/birthdays` - Show all birthdays sorted by months from current

## Features

- Daily notifications at 8:00 AM (Moscow time)
- Auto-check birthdays on bot startup
- Birthdays list ordered from current month
- Support for optional Telegram usernames (@mentions)
