from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# הוספת הנתיב לשימוש ב-utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import CONFIG, get_openai_client, get_pinecone_index, EMBEDDING_MODEL, CHAT_MODEL, SYSTEM_PROMPT

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # קריאת ה-body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            user_question = data.get('question')
            
            if not user_question:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No question provided"}).encode('utf-8'))
                return
            
            # אתחול לקוחות
            client = get_openai_client()
            index = get_pinecone_index()
            
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
                chunk_text = meta.get('text', '')
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
            response_data = {
                "response": ai_response,
                "context": context_list_json,
                "Augmented_prompt": {
                    "System": SYSTEM_PROMPT,
                    "User": user_question
                }
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

