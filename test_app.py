"""
Minimal Flask app for testing Marcus integration APIs
"""

import os
from flask import Flask, render_template
from flask_cors import CORS

# Import only the working APIs
from src.api.marcus_prediction_api import prediction_api
from src.api.marcus_analytics_api import analytics_api

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register only the working blueprints
app.register_blueprint(prediction_api)
app.register_blueprint(analytics_api)

# Serve the main frontend
@app.route("/")
def index():
    """Serve the main frontend application."""
    return render_template("index.html")

# Health check endpoint
@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "marcus-integration-test"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)