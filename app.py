from flask import Flask, render_template
from database import DatabaseManager
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

# Initializing database
db = DatabaseManager()
db.initialize_database()

@app.route('/')
def index():
    """Serves the main page"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
