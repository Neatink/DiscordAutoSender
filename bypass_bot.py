from threading import Thread
from flask import Flask
import logging
import os

logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Bot Alive")
    return "bot alive"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def alive():
    t = Thread(target=run)
    t.start()