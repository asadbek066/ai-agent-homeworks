import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from book_qa import BookKnowledgeBase

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN not found in .env")
    exit(1)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

kb = BookKnowledgeBase()
user_books = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Welcome to Book Q&A Bot\n\nSend a book file then ask questions about it.\n\nCommands: /load_book /summary /help"
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Send a book file (PDF/TXT)\nWait for processing\nAsk questions\n\nCommands: /start /load_book /summary"
    await update.message.reply_text(msg)

async def load_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a book file (PDF or TXT)")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = kb.get_book_summary()
    await update.message.reply_text(text)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    user_id = update.effective_user.id
    
    if not (document.file_name.endswith('.pdf') or document.file_name.endswith('.txt')):
        await update.message.reply_text("Send PDF or TXT file only")
        return
    
    msg = await update.message.reply_text("Downloading...")
    
    try:
        file = await context.bot.get_file(document.file_id)
        books_dir = Path("books")
        books_dir.mkdir(exist_ok=True)
        
        file_path = books_dir / document.file_name
        await file.download_to_drive(file_path)
        
        await msg.edit_text("Processing book...")
        
        success = kb.load_book(str(file_path))
        
        if success:
            user_books[user_id] = file_path
            await msg.edit_text(f"Book loaded: {kb.book_name}\nChunks: {len(kb.documents)}\n\nReady to answer questions!")
        else:
            await msg.edit_text("Failed to process book")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"Error: {str(e)}")

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    user_id = update.effective_user.id
    
    if not kb.documents:
        await update.message.reply_text("No book loaded. Use /load_book")
        return
    
    msg = await update.message.reply_text("Searching...")
    
    try:
        answer, chunks = kb.answer_question(question, top_k=2, short=True)
        response = f"Q: {question}\n\nA: {answer}"
        await msg.edit_text(response)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"Error: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Error:", exc_info=context.error)

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("load_book", load_book))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    application.add_error_handler(error_handler)
    
    print("Bot starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
