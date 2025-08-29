from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for popup chat

# Enhanced website structure with more keywords for better matching
WEBSITE_STRUCTURE = {
    "home": {
        "url": "/",
        "keywords": ["home", "homepage", "main", "index", "landing", "start"],
        "description": "Main homepage"
    },
    "about": {
        "url": "/about",
        "keywords": ["about", "about us", "who we are", "company", "team", "story"],
        "description": "About us page"
    },
    "contact": {
        "url": "/contact",
        "keywords": ["contact", "contact us", "reach us", "get in touch", "phone", "email", "address"],
        "description": "Contact information and form"
    },
    "services": {
        "url": "/services",
        "keywords": ["services", "what we do", "offerings", "products", "solutions"],
        "description": "Our services page"
    },
    "donation": {
        "url": "/donate",
        "keywords": ["donate", "donation", "contribute", "support us", "give", "charity"],
        "description": "Make a donation"
    },
    "blog": {
        "url": "/blog",
        "keywords": ["blog", "articles", "news", "posts", "updates", "insights"],
        "description": "Latest blog posts and articles"
    },
    "faq": {
        "url": "/faq",
        "keywords": ["faq", "frequently asked questions", "help", "questions", "support", "answers"],
        "description": "Frequently asked questions"
    },
    "privacy": {
        "url": "/privacy",
        "keywords": ["privacy", "privacy policy", "data protection", "gdpr", "policy"],
        "description": "Privacy policy"
    },
    "terms": {
        "url": "/terms",
        "keywords": ["terms", "terms of service", "conditions", "legal", "agreement"],
        "description": "Terms of service"
    },
    "portfolio": {
        "url": "/portfolio",
        "keywords": ["portfolio", "work", "projects", "gallery", "showcase", "examples"],
        "description": "Our portfolio and work samples"
    },
    "careers": {
        "url": "/careers",
        "keywords": ["careers", "jobs", "employment", "hiring", "work with us", "opportunities"],
        "description": "Career opportunities"
    },
    "login": {
        "url": "/login",
        "keywords": ["login", "sign in", "log in", "access", "account"],
        "description": "User login page"
    },
    "register": {
        "url": "/register",
        "keywords": ["register", "sign up", "create account", "join", "signup"],
        "description": "User registration page"
    }
}

class PopupWebsiteChatbot:
    def __init__(self, website_structure):
        self.website_structure = website_structure
        self.greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "hola", "sup"]
        self.help_keywords = ["help", "what can you do", "commands", "options", "assist", "guide", "menu"]
        self.search_keywords = ["find", "where", "show", "locate", "search", "looking for", "need", "want"]
        self.thanks_keywords = ["thank", "thanks", "thank you", "thx", "appreciate"]
        self.goodbye_keywords = ["bye", "goodbye", "see you", "later", "exit", "quit"]
    
    def normalize_text(self, text):
        """Normalize text for better matching"""
        return re.sub(r'[^\w\s]', '', text.lower().strip())
    
    def calculate_page_score(self, page_info, user_input):
        """Calculate relevance score for a page based on user input"""
        score = 0
        normalized_input = self.normalize_text(user_input)
        
        for keyword in page_info["keywords"]:
            keyword_lower = keyword.lower()
            
            # Exact keyword match
            if keyword_lower == normalized_input:
                score += 20
            # Keyword appears in input
            elif keyword_lower in normalized_input:
                score += 10
            # Individual words match
            else:
                keyword_words = keyword_lower.split()
                input_words = normalized_input.split()
                matches = sum(1 for word in keyword_words if word in input_words)
                if matches > 0:
                    score += matches * 3
        
        return score
    
    def find_page(self, user_input):
        """Find the most relevant page based on user input with scoring"""
        page_scores = {}
        
        for page_name, page_info in self.website_structure.items():
            score = self.calculate_page_score(page_info, user_input)
            if score > 0:
                page_scores[page_name] = score
        
        if page_scores:
            # Get the best match
            best_page = max(page_scores, key=page_scores.get)
            # If score is very low, suggest multiple options
            if page_scores[best_page] < 5:
                return None, None
            return best_page, self.website_structure[best_page]
        
        return None, None
    
    def get_suggested_pages(self, count=6):
        """Get a list of suggested page names for help responses"""
        popular_pages = ["home", "about", "contact", "services", "donation", "blog"]
        available_pages = list(self.website_structure.keys())
        
        # Return popular pages that exist, then fill with others
        suggestions = [page for page in popular_pages if page in available_pages]
        remaining = [page for page in available_pages if page not in suggestions]
        
        return (suggestions + remaining)[:count]
    
    def generate_response(self, user_input):
        """Generate contextual response based on user input"""
        if not user_input.strip():
            return {
                "message": "Please ask me something! I can help you find pages on our website.",
                "type": "empty_input"
            }
        
        normalized_input = self.normalize_text(user_input)
        
        # Handle greetings
        if any(greeting in normalized_input for greeting in self.greetings):
            return {
                "message": "👋 Hello! I'm CHRIS, your website assistant. I can help you quickly navigate to any page on our website. What are you looking for today?",
                "type": "greeting",
                "pages": self.get_suggested_pages(4)
            }
        
        # Handle thanks
        if any(thanks in normalized_input for thanks in self.thanks_keywords):
            return {
                "message": "😊 You're welcome! Is there anything else I can help you find on our website?",
                "type": "thanks"
            }
        
        # Handle goodbyes
        if any(bye in normalized_input for bye in self.goodbye_keywords):
            return {
                "message": "👋 Goodbye! Feel free to ask me anytime if you need help finding pages on our website.",
                "type": "goodbye"
            }
        
        # Handle help requests
        if any(help_word in normalized_input for help_word in self.help_keywords):
            return {
                "message": "🔍 I can help you find any page on our website! Here are some popular pages you can ask about:",
                "type": "help",
                "pages": self.get_suggested_pages(8)
            }
        
        # Look for specific page requests
        page_name, page_info = self.find_page(user_input)
        
        if page_info:
            # Create more natural response based on what they asked
            if any(word in normalized_input for word in ["where", "find", "locate"]):
                message = f"📍 The {page_info['description']} can be found here:"
            elif any(word in normalized_input for word in ["show", "take me", "go to"]):
                message = f"✅ Here's the {page_info['description']}:"
            else:
                message = f"✅ Found it! {page_info['description']}:"
            
            return {
                "message": message,
                "type": "page_found",
                "page_name": page_name,
                "url": page_info["url"],
                "description": page_info["description"]
            }
        
        # Handle general search queries
        if any(search_word in normalized_input for search_word in self.search_keywords):
            return {
                "message": "🔍 I couldn't find that specific page. Here are all the pages I can help you locate:",
                "type": "search_help",
                "pages": list(self.website_structure.keys())
            }
        
        # Default response with suggestions
        return {
            "message": "🤔 I'm not sure what you're looking for. I can help you find these popular pages:",
            "type": "not_found",
            "pages": self.get_suggested_pages(6)
        }

# Initialize enhanced chatbot
chatbot = PopupWebsiteChatbot(WEBSITE_STRUCTURE)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with better error handling and logging"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip() if data else ''
        
        if not user_message:
            return jsonify({
                "error": "Please enter a message",
                "message": "Please ask me something! I can help you find pages on our website.",
                "type": "empty_input"
            }), 400
        
        # Generate response using enhanced chatbot
        response = chatbot.generate_response(user_message)
        
        # Add timestamp in a format suitable for popup display
        response['timestamp'] = datetime.now().strftime("%H:%M")
        
        # Add session info for debugging (optional)
        response['debug'] = {
            "input_length": len(user_message),
            "normalized_input": chatbot.normalize_text(user_message),
            "available_pages": len(WEBSITE_STRUCTURE)
        }
        
        return jsonify(response)
    
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Chat error: {str(e)}")
        
        return jsonify({
            "error": "Something went wrong",
            "message": "😅 Sorry, I had a little hiccup. Please try asking again!",
            "type": "error",
            "timestamp": datetime.now().strftime("%H:%M")
        }), 500

@app.route('/pages')
def get_pages():
    """API endpoint to get all available pages with enhanced structure"""
    return jsonify({
        "pages": WEBSITE_STRUCTURE,
        "total_pages": len(WEBSITE_STRUCTURE),
        "page_names": list(WEBSITE_STRUCTURE.keys()),
        "categories": {
            "main": ["home", "about", "contact", "services"],
            "user": ["login", "register", "careers"],
            "content": ["blog", "portfolio", "faq"],
            "legal": ["privacy", "terms"],
            "support": ["donation"]
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint for popup to verify connection"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "chatbot": "ready",
        "pages_available": len(WEBSITE_STRUCTURE)
    })

# Error handlers for better popup experience
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "This endpoint doesn't exist. Try /chat for chatbot or /pages for page list.",
        "type": "not_found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed",
        "message": "This endpoint requires a different HTTP method.",
        "type": "method_error"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "😅 Something went wrong on our end. Please try again!",
        "type": "server_error"
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)