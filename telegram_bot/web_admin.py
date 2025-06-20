"""Simple Flask admin panel for the Telegram bot."""
import os
from flask import (Flask, redirect, render_template, request, url_for)

from . import db

ADMIN_TOKEN = os.environ.get("WEB_ADMIN_TOKEN", "secret")

app = Flask(__name__)

def check_auth(token: str) -> bool:
    return token == ADMIN_TOKEN

@app.before_first_request
def init() -> None:
    db.init_db()

@app.route("/")
def index():
    if not check_auth(request.args.get("token", "")):
        return "Not authorized", 403
    cats = db.get_categories(None)
    return render_template("index.html", categories=cats)

@app.route("/category/add", methods=["POST"])
def add_category_view():
    if not check_auth(request.args.get("token", "")):
        return "Not authorized", 403
    name = request.form["name"]
    parent = request.form.get("parent")
    parent_id = int(parent) if parent else None
    db.add_category(name, parent_id)
    return redirect(url_for("index", token=request.args.get("token")))

@app.route("/broadcast", methods=["POST"])
def broadcast():
    if not check_auth(request.args.get("token", "")):
        return "Not authorized", 403
    from telegram import Bot
    bot = Bot(os.environ.get("TELEGRAM_BOT_TOKEN"))
    msg = request.form["msg"]
    for user_id in db.get_subscribers():
        try:
            bot.send_message(user_id, msg)
        except Exception:
            pass
    return redirect(url_for("index", token=request.args.get("token")))

if __name__ == "__main__":
    app.run(debug=True)
