# Import required libraries
import nltk
from nltk.chat.util import Chat, reflections
import random
import spacy
from datetime import datetime
import json
import os

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    print("SpaCy model loaded successfully!")
except:
    print("Error loading SpaCy. Make sure you ran: python -m spacy download en_core_web_sm")

# Download required NLTK data (only if not already downloaded)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

# Advanced NLP processing function
def process_with_nlp(user_input):
    """
    Process user input with SpaCy for advanced understanding
    """
    doc = nlp(user_input)
    
    # Extract named entities (people, places, organizations, etc.)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Extract key nouns and verbs
    nouns = [token.text for token in doc if token.pos_ == "NOUN"]
    verbs = [token.text for token in doc if token.pos_ == "VERB"]
    
    # Analyze sentiment (basic)
    sentiment = "neutral"
    if any(word in user_input.lower() for word in ["good", "great", "excellent", "love", "happy"]):
        sentiment = "positive"
    elif any(word in user_input.lower() for word in ["bad", "terrible", "hate", "sad", "angry"]):
        sentiment = "negative"
    
    return {
        "entities": entities,
        "nouns": nouns,
        "verbs": verbs,
        "sentiment": sentiment
    }

    # Smart response based on NLP analysis
def get_smart_response(user_input):
    """
    Generate intelligent responses based on NLP analysis
    """
    analysis = process_with_nlp(user_input)
    
    # Check for location entities
    for entity, label in analysis["entities"]:
        if label in ["GPE", "LOC"]:  # GPE = Geo-Political Entity, LOC = Location
            return f"Oh, {entity}! That's a wonderful place! How can I help you today?"
    
    # Check for person names
    for entity, label in analysis["entities"]:
        if label == "PERSON":
            return f"Nice to meet you, {entity}! What can I do for you?"
    
    return None  # Return None if no special entity found
 
conversation_history = []

def load_existing_conversations():
    """
    Load previous conversations from file if it exists
    """
    global conversation_history
    if os.path.exists("conversation_log.json"):
        try:
            with open("conversation_log.json", "r") as f:
                conversation_history = json.load(f)
                print(f"Loaded {len(conversation_history)} previous messages.")
        except:
            conversation_history = []
    else:
        conversation_history = []

def log_conversation(user_input, bot_response):
    """
    Log conversation to history and save to file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conversation_entry = {
        "timestamp": timestamp,
        "user": user_input,
        "bot": bot_response
    }
    
    conversation_history.append(conversation_entry)
    
    # Save to file (appending to existing conversations)
    with open("conversation_log.json", "w") as f:
        json.dump(conversation_history, f, indent=4)

def display_conversation_stats():
    """
    Display statistics about the conversation
    """
    print("\n" + "="*50)
    print("📊 Conversation Statistics:")
    print("="*50)
    print(f"Total messages in history: {len(conversation_history)}")
    
    if conversation_history:
        print(f"First conversation: {conversation_history[0]['timestamp']}")
        print(f"Latest conversation: {conversation_history[-1]['timestamp']}")
    
    print(f"Conversation saved to: conversation_log.json")
    print("="*50)

# Define pairs of patterns and responses
pairs = [

    [
        r"my name is (.*)",
        ["Nice to meet you, %1! How can I help you today?",
         "Hello %1! What brings you here?"]
    ],
    
    # Location detection (improved)
    [
        r"(.*) from (.*)",
        ["Oh, you're from %2! That's interesting! How can I assist you?",
         "%2 sounds like a nice place! What can I do for you?"]
    ],
    
    [
        r"i live in (.*)|i am in (.*)",
        ["Great! How's everything in your area?",
         "Nice! What brings you here today?"]
    ],

    # Greetings
    [
        r"hi|hello|hey|hola",
        ["Hello! How can I help you today?", 
         "Hi there! What can I do for you?", 
         "Hey! Nice to meet you!"]
    ],
    
    # How are you
    [
        r"how are you|how do you do",
        ["I'm doing great, thank you for asking!", 
         "I'm a chatbot, so I'm always good! How about you?"]
    ],
    
    # Name questions
    [
        r"what is your name|who are you",
        ["I'm a chatbot created using NLP!", 
         "You can call me ChatBot. I'm here to assist you!"]
    ],
    
    # Help requests
    [
        r"help|can you help|need help",
        ["Of course! I can answer your questions. Just ask me anything!", 
         "I'm here to help! What do you need?"]
    ],
    
    # Goodbye
    [
        r"bye|goodbye|see you|exit|quit",
        ["Goodbye! Have a great day!", 
         "See you later!", 
         "Bye! Come back soon!"]
    ],
    
    # Default response
    [
        r"(.*)",
        ["I'm not sure I understand. Can you rephrase that?", 
         "Interesting! Tell me more.", 
         "Could you please elaborate?"]
    ]
]

# Create the chatbot using Chat class
def start_chatbot():
    # Load previous conversations
    load_existing_conversations()
    
    print("\n" + "="*50)
    print("🤖 Welcome to the AI Chatbot with NLP!")
    print("="*50)
    print("You can start chatting now. Type 'bye' or 'quit' to exit.\n")
    
    chatbot = Chat(pairs, reflections)
    
    # Custom conversation loop with NLP and logging
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
            bot_response = "Goodbye! Have a great day!"
            print(f"Bot: {bot_response}")
            log_conversation(user_input, bot_response)
            break
        
        # Try smart NLP response first
        smart_reply = get_smart_response(user_input)
        
        if smart_reply:
            print(f"Bot: {smart_reply}")
            log_conversation(user_input, smart_reply)
        else:
            # Fall back to pattern matching
            response = chatbot.respond(user_input)
            print(f"Bot: {response}")
            log_conversation(user_input, response)
    
    # Show stats at the end
    display_conversation_stats()

# Main program
if __name__ == "__main__":
    print("Initializing chatbot...")
    start_chatbot()