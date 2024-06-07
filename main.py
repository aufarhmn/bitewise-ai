from flask import Flask 
from flask_cors import CORS

# ENVIRONMENT VARIABLES
from dotenv import load_dotenv
load_dotenv()

# FLASK APP
app = Flask(__name__) 
CORS(app)

# ROUTES
from src.blueprints.index import ai_blueprint
app.register_blueprint(ai_blueprint)

# HOME ROUTE
@app.route('/')
def index():
    return "Hello from BiteWise API Service!"

# RUN APP
if __name__ == "__main__":
    app.run(debug=True)
