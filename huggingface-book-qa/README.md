# Book Q&A Telegram Bot

Upload a book and ask questions about it.

## Tech Stack

- python-telegram-bot
- sentence-transformers (Hugging Face)
- PyPDF2
- torch
- transformers

## Setup

1. Get bot token from @BotFather on Telegram
2. Create `.env` file with `TELEGRAM_BOT_TOKEN=your_token`
3. Run `python telegram_bot.py`

## Usage

1. Send `/load_book`
2. Upload a PDF or TXT file
3. Ask questions about the book

## Commands

- `/start` - Start
- `/load_book` - Upload book
- `/summary` - Info
- `/help` - Help
