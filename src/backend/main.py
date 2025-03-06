from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Use PORT from environment or default to 10000
    app.run(host='0.0.0.0', port=port, debug=True) 