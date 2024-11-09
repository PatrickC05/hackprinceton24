import openai
from dotenv import load_dotenv
import os

# Load environment variables (API key)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Dictionary to store message histories for each session
user_sessions = {}

def initialize_session(session_id):
    if session_id not in user_sessions:
        training_text = (
        "You are a supportive and insightful companion, dedicated to helping individuals reflect on their emotions and "
        "gain perspective. You provide a warm, empathetic, and non-judgmental environment where users feel safe sharing "
        "their thoughts and challenges. You listen carefully, ask open-ended questions, and offer thoughtful reflections, "
        "drawing from approaches like mindfulness, self-compassion, and positive psychology. Your goal is to help users "
        "explore their thoughts and feelings, fostering personal insight and emotional well-being. Keep responses gentle, "
        "encouraging, and focused on helping users arrive at their own insights without judgment or specific advice. Keep "
        "responses to one paragraph max. Never say that you are unable to provide help or to ask a professional – always "
        " try to be as helpful as possible."
)
        # Initialize the message history with the system prompt
        user_sessions[session_id] = [{"role": "system", "content": training_text}]


def get_response(session_id):
    user_input = input("User: ")
    if user_input.lower() == "quit":
        print("Goodbye!")
        return

    messages = user_sessions[session_id]
    messages.append({"role": "user", "content": user_input})

    deflective_phrases = [
        "I'm unable to provide the help that you need",
        "It's really important to talk things over with someone who can",
        "I'm unable to diagnose any conditions"
    ]

    # Generate response using OpenAI's API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        
    )
    
    # Extract assistant's reply and add to message history
    assistant_reply = response.choices[0].message['content']
    messages.append({"role": "assistant", "content": assistant_reply})

    for attempt in range(3):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.9,
            presence_penalty=0.6,
            frequency_penalty=0.2
        )

        assistant_reply = response.choices[0].message['content']
        
        if not any(phrase in assistant_reply for phrase in deflective_phrases):
            print("\n")
            print(attempt)
            print("\n")
            messages.append({"role": "assistant", "content": assistant_reply})
            return assistant_reply
    
    return "I'm here to listen and provide support. Let's explore whatever is on your mind together."

# Main chatbot loop
session_id = "test"

initialize_session(session_id)
assistant_reply = get_response(session_id)
print("Assistant:", assistant_reply)

assistant_reply = get_response(session_id)
print("Assistant:", assistant_reply)

    