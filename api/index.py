from flask import Flask, request, jsonify
import os
import json
from openai import OpenAI
from pinecone import Pinecone

app = Flask(__name__)

# --- 1. טעינת קונפיגורציה ---
# מנסה לטעון מהתיקייה למעלה (Vercel) או מהתיקייה הנוכחית (מקומי)
try:
    with open(os.path.join(os.path.dirname(__file__), '../rag_config.json'), 'r') as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    with open('rag_config.json', 'r') as f:
        CONFIG = json.load(f)

# --- 2. אתחול לקוחות (Clients) ---
# הערה: המפתחות יילקחו ממשתני הסביבה ב-Vercel
client = OpenAI(
    api_key=os.environ.get("LLMOD_API_KEY"),
    base_url="https://api.llmod.ai/v1"
)

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(host=os.environ.get("PINECONE_INDEX_HOST"))

# שמות המודלים לפי דף ההוראות
EMBEDDING_MODEL = "RPRTHPB-text-embedding-3-small"
CHAT_MODEL = "RPRTHPB-gpt-5-mini"

# --- 3. System Prompt (חובה לפי המטלה) ---
SYSTEM_PROMPT = """You are a TED Talk assistant that answers questions strictly and
only based on the TED dataset context provided to you (metadata
and transcript passages).
You must not use any external
knowledge, the open internet, or information that is not explicitly
contained in the retrieved context.
If the answer cannot be
determined from the provided context, respond: "I don't know
based on the provided TED data."
Always explain your answer
using the given context, quoting or paraphrasing the relevant
transcript or metadata when helpful.
You may add additional clarifications (e.g., response style), but you must
keep the above constraints."""

# --- 4. נתיב סטטיסטיקות (חובה לפי המטלה) ---
@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        "chunk_size": CONFIG["chunk_size"],
        "overlap_ratio": CONFIG["overlap_ratio"],
        "top_k": CONFIG["top_k"]
    })

# --- 5. נתיב השאילתה (הלוגיקה המרכזית) ---
@app.route('/api/prompt', methods=['POST'])
def handle_prompt():
    data = request.json
    user_question = data.get('question')
    
    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # א. יצירת Embedding לשאלה
        emb_response = client.embeddings.create(
            input=user_question,
            model=EMBEDDING_MODEL
        )
        question_embedding = emb_response.data[0].embedding

        # ב. חיפוש ב-Pinecone
        search_results = index.query(
            vector=question_embedding,
            top_k=CONFIG["top_k"],
            include_metadata=True
        )

        # ג. בניית Context ורשימת תוצאות ל-JSON
        context_text = ""
        context_list_json = []

        for match in search_results['matches']:
            meta = match['metadata']
            score = match['score']
            
            # בניית הטקסט למודל
            chunk_text = meta.get('text', '') # או 'chunk' תלוי איך שמרת במחברת
            title = meta.get('title', 'Unknown')
            talk_id = meta.get('talk_id', 'Unknown')
            
            context_string = f"Title: {title}\nTalk ID: {talk_id}\nContent: {chunk_text}\n\n"
            context_text += context_string
            
            # שמירה לפורמט התשובה הסופי
            context_list_json.append({
                "talk_id": str(talk_id),
                "title": title,
                "chunk": chunk_text,
                "score": score
            })

        # ד. שליחה למודל השפה
        final_system_prompt = SYSTEM_PROMPT + f"\n\nContext:\n{context_text}"
        
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": user_question}
            ]
        )
        
        ai_response = completion.choices[0].message.content

        # ה. החזרת התשובה הסופית
        return jsonify({
            "response": ai_response,
            "context": context_list_json,
            "Augmented_prompt": {
                "System": SYSTEM_PROMPT,
                "User": user_question
            }
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# להרצה מקומית אם צריך
if __name__ == '__main__':
    app.run(debug=True, port=3000)
