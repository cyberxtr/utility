"""Telegram Bot implementation with button-based categories."""
import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes)

from . import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = set(
    int(i) for i in os.environ.get("TELEGRAM_ADMIN_IDS", "").split() if i)


def build_keyboard(parent_id=None):
    categories = db.get_categories(parent_id)
    keyboard = [[
        InlineKeyboardButton(cat[1], callback_data=f"cat:{cat[0]}")
    ] for cat in categories]
    if parent_id is not None:
        keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db.add_subscriber(update.effective_user.id)
    keyboard = build_keyboard(None)
    await update.message.reply_text("Select category:", reply_markup=keyboard)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "back":
        await query.edit_message_text(
            "Select category:", reply_markup=build_keyboard(None))
        return
    if data.startswith("cat:"):
        cat_id = int(data.split(":", 1)[1])
        subcats = db.get_categories(cat_id)
        files = db.get_files(cat_id)
        if subcats:
            await query.edit_message_text(
                "Select category:", reply_markup=build_keyboard(cat_id))
        else:
            for file_id, name in files:
                await context.bot.send_document(query.message.chat_id,
                                                file_id,
                                                caption=name)
            await query.answer("Done")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Not authorized")
        return
    msg = update.message.text.partition(" ")[2]
    for user_id in db.get_subscribers():
        try:
            await context.bot.send_message(user_id, msg)
        except Exception as exc:  # ignore user block errors
            logger.warning("Failed to send to %s: %s", user_id, exc)


def main() -> None:
    db.init_db()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CallbackQueryHandler(on_button))
    application.run_polling()


if __name__ == "__main__":
    main()
