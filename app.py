from flask import Flask, render_template, Response, request, stream_with_context, jsonify
from flask_cors import CORS
import numpy as np
import os

# Now import routes AFTER defining the shared variables

from dotenv import load_dotenv
from models import PromptCache, db
from views import index as index_view
from ai_routes import ai_routes
from rag_routes import rag_routes
from transformers import pipeline
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(ai_routes)
app.register_blueprint(rag_routes)

@app.route("/test")
def test():
    return "OK"
 
@app.route("/")
def index():
    return render_template("index.html", project_name="SmartSupport AI")

@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"msg": "Hello, world!"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)





