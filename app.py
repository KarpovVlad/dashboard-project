from flask import Flask
from controllers.feed_controller import feed_blueprint
import threading
from services.feed_service import fetch_feed, parse_and_store_feed
import time

app = Flask(__name__)

app.register_blueprint(feed_blueprint)

def fetch_data_periodically():
    while True:
        feed_data = fetch_feed()
        if feed_data:
            parse_and_store_feed(feed_data)
            print("Фід успішно завантажено та оброблено")
        time.sleep(900)

threading.Thread(target=fetch_data_periodically, daemon=True).start()

@app.template_filter('clean_price')
def clean_price(value):
    try:
        return float(value.replace(",", "").replace(" ", ""))
    except ValueError:
        return 0.0


if __name__ == '__main__':
    app.run(debug=True)
