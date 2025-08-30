from flask import Flask, render_template
import requests
from database import DatabaseManager
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

# Initializing database
db = DatabaseManager()
db.initialize_database()

class QuestionGenerator:
    """Function to initializing Hugging Face API and generate questions"""
    def __init__(self):
        self.api_key = Config.HUGGING_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def generate_questions_huggingface(self, text):
        """Generate questions using Hugging Face API"""
        try:
            # Used text generation model for creating questions
            API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

            # Prompt for question generation
            prompt = f"""Generate 5 study questions and answers from this text. Format as Q: question A: answer
            Text: {text[:1000]}"""

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }

            response = requests.post(API_URL, headers=self.headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                generated_text = result[0]['generated_text'] if result else ""
                return self.parse_questions_and_answers(generated_text)
            else:
                return self.fallback_question_generation(text)
        except Exception as e:
            print(f"Error with Hugging Face API: {e}")
            return self.fallback_question_generation(text)

@app.route('/')
def index():
    """Serves the main page"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
