from flask import Flask, jsonify, render_template, request
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

            response = requests.post(API_URL, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                generated_text = result[0]['generated_text'] if result else ""
                return self.parse_questions_and_answers(generated_text)
            else:
                return self.fallback_question_generation(text)
        except Exception as e:
            print(f"Error with Hugging Face API: {e}")
            return self.fallback_question_generation(text)

    def fallback_question_generation(self, text):
        """Fallback method to generate questions when API fails"""
        sentences = text.split('.')
        questions = []

        keywords = ['what', 'how', 'why', 'when', 'where']

        for i, sentence in enumerate(sentences[:5]):
            if len(sentence.strip()) > 20:

                question_type = keywords[i % len(keywords)]

                if question_type == 'what':
                    question = f"What is the main concept discussed in: '{sentence.strip()}'?"
                elif question_type == 'how':
                    question = f"How does this relate to the topic: '{sentence.strip()}'?"
                elif question_type == 'why':
                    question = f"Why is this important: '{sentence.strip()}'?"
                elif question_type == 'when':
                    question = f"When might this apply: '{sentence.strip()}'?"
                else:
                    question = f"Where would you use this information: '{sentence.strip()}'?"

                questions.append({
                    'question': question,
                    'answer': sentence.strip(),
                    'difficulty': 'medium'
                })
        return questions[:5]

    def parse_questions_and_answers(self, generated_text):
        """Parsing generated text to extract questions and answers"""
        questions = []
        lines = generated_text.split('\n')

        current_question = ""
        current_answer = ""

        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_question and current_answer:
                    questions.append({
                        'question': current_question,
                        'answer': current_answer,
                        'difficulty': 'medium'
                    })
                current_question = line[2:].strip()
                current_answer = ""
            elif line.startswith('A:'):
                current_answer = line[2:].strip()
            elif current_question and not current_answer:
                current_question += " " + line
            elif current_answer:
                current_answer += " " + line

        if current_question and current_answer:
            questions.append({
                'question': current_question,
                'answer': current_answer,
                'difficulty': 'medium'
            })

        return questions[:5]

@app.route('/')
def index():
    """Rendering main page"""
    return render_template('index.html')

@app.route('/generate_flashcards', methods=['POST'])
def generate_flashcards():
    """Generating flashcards from study notes"""
    try:
        data = request.get_json()
        study_text = data.get('text', '')
        topic = data.get('topic', 'General')

        if not study_text:
            return jsonify({'error': 'No text provided'}), 400

        generator = QuestionGenerator()
        questions = generator.generate_questions_huggingface(study_text)

        # Saving flashcards to the database
        saved_flashcards = []
        for q in questions:
            flashcard_id = db.save_flashcard(
                q['question'],
                q['answer'],
                topic,
                q.get('difficulty', 'medium')
            )
            if flashcard_id:
                saved_flashcards.append({
                    'id': flashcard_id,
                    'question': q['question'],
                    'answer': q['answer'],
                    'topic': topic,
                    'difficulty': q.get('difficulty', 'medium')
                })

        # Saving session
        session_id = db.save_study_session(f"Session - {topic}", study_text)

        return jsonify({
            'success':True,
            'flashcards': saved_flashcards,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/get_flashcards', methods=['GET'])
def get_flashcards():
    """Retrieving saved flashcards"""
    try:
        topic = request.args.get('topic')
        flashcards = db.get_all_flashcards(topic)
        return jsonify({
            'flashcards': flashcards
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
