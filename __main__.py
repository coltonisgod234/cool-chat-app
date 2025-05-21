"""
Chat Application Main Module
Run with: python -m newsrc
"""
from newsrc.api.web_server import app

if __name__ == "__main__":
    print("Starting Cool Chat App...")
    app.run(debug=True, port=5100)