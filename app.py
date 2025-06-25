from flask import Flask, render_template, Response, request, stream_with_context, jsonify
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import faiss
from flask_cors import CORS
import numpy as np
import os


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Example documents (replace with your FAQ or support content)
docs = [
    "Reset your password via Settings > Account.",
    "Update your email form profile settings.",
    "Our support team is available at support@example.com.",
    "To delete your account, go to Account Settings and click 'Delete Account'."
]

# Build FAISS index using sentence-transformers

doc_embeddings = embedding_model.encode(docs).astype("float32")
index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(doc_embeddings)


# Now import routes AFTER defining the shared variables

from dotenv import load_dotenv
from models import PromptCache, db
from views import index as index_view
from ai_routes import ai_routes
from rag_routes import rag_routes
from transformers import pipeline
import os

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

#print("Gemini API Key:", os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'

db.init_app(app)


with app.app_context():
    db.create_all()

# Provide shared objects to the blueprint
ai_routes.embedding_model = embedding_model
ai_routes.docs = docs
ai_routes.index = index

app.register_blueprint(ai_routes)
app.register_blueprint(rag_routes)

@app.route("/test")
def test():
    return "OK"

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    print("=== /prompt endpoint hit ===")
    data = request.get_json()
    print("Recieved data: ", data)

    prompt = data.get('prompt') if data else None
    if not prompt:
        print("Missing prompt")
        return jsonify({'error': 'Prompt is required'}), 400

    #Check cache
    cached = PromptCache.query.filter_by(prompt=prompt).first()
    if cached:
        print("Catched hit")
        return jsonify({'response': cached.response, 'cached': True})
    
    
    # Generate new response (mock example)
    response = f"Processed response for: {prompt}"
    print("Generated response: ", response)

    # Store in cache
    new_entry = PromptCache(prompt=prompt, response=response)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'response': response, 'çached': False})
 
@app.route("/")
def index():
    return render_template("index.html", project_name="SmartSupport AI")

@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"msg": "Hello, world!"})

@app.route("/api/query", methods=["POST"])
def query_sql():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    sql = "SELECT region, SUM(sales) FROM sales_data GROUP BY region"

    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    result = [dict(zip(columns, row)) for row in rows]
    return jsonify({"sql": sql, "result": result})

if __name__ == "__main__":
    try:
        print("embedding_model working:", embedding_model.encode(["test"]).shape)
    except Exception as e:
        print("embedding_model error:", e)

    app.run(host="127.0.0.1", port=8000, debug=True)
        

    app.run(host="127.0.0.1", port=8000, debug=True)






