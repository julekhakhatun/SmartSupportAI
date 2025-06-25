from flask import Blueprint, Response, request, jsonify, stream_with_context
from models import db, PromptCache
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np
import os

embedding_model = None
docs = None
index = None

# Load Gemini API key and set model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

ai_routes = Blueprint('ai_routes', __name__)


@ai_routes.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt")

    if not data or "prompt" not in data:
        return jsonify({"error": "Missing prompt"}), 400
    
    query = prompt

    # Check cache
    cached = PromptCache.query.filter_by(prompt=prompt).first()
    if cached:
        return jsonify({'response': cached.response, 'cached': True})


    # Return the AI-generated answer
    response = model.generate_content(prompt)

    # Store in cache
    new_entry = PromptCache(prompt=prompt, response=response.text)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'response':  response.text, 'cached': False})

    
    

    
    
        


