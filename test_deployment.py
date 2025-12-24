import requests
import json

# --- שים לב: וודא שזו הכתובת שלך ---
APP_URL = "https://ted-rag-final.vercel.app"


def verify_deployment():
    url = f"{APP_URL}/api/prompt"

    # שאלה לדוגמה
    payload = {"question": "What is the main idea of the talk about fear?"}

    print(f"Testing: {url}...")
    try:
        response = requests.post(url, json=payload)

        # בדיקה 1: האם השרת הגיב בכלל?
        if response.status_code != 200:
            print(f"❌ Error! Status Code: {response.status_code}")
            print(response.text)
            return

        data = response.json()

        # בדיקה 2: האם כל השדות הנדרשים קיימים?
        required_keys = ["response", "context", "Augmented_prompt"]
        missing = [key for key in required_keys if key not in data]

        if missing:
            print(f"❌ נכשל! שדות חסרים ב-JSON: {missing}")
            return

        # בדיקה 3: האם ה-Context הוא רשימה ויש בו מידע?
        if not isinstance(data['context'], list) or len(data['context']) == 0:
            print("⚠️ אזהרה: חזר Context ריק (אולי לא נמצאו תוצאות, או בעיה ב-Pinecone).")
        else:
            # בדיקת מבנה ה-Context
            first_chunk = data['context'][0]
            if not all(k in first_chunk for k in ["talk_id", "title", "chunk", "score"]):
                print("❌ נכשל! המבנה הפנימי של ה-context לא תקין.")
                print(f"קיבלנו: {first_chunk.keys()}")
                return

        # בדיקה 4: האם הפרומפט המערכת (System Prompt) מופיע?
        system_prompt = data['Augmented_prompt'].get('System', '')
        if "You are a TED Talk assistant" not in system_prompt:
            print("❌ נכשל! ה-System Prompt לא תואם להוראות המטלה.")
            return

        print("\n✅✅✅ הכל תקין! המערכת עובדת לפי הדרישות.")
        print("-" * 30)
        print(f"תשובת המודל: {data['response']}")

    except Exception as e:
        print(f"❌ שגיאה בהרצה: {e}")


# הרצת הבדיקה
verify_deployment()