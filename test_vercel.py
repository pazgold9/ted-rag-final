#!/usr/bin/env python3
"""
סקריפט בדיקה מפורט ל-Vercel deployment
"""
import requests
import json
from datetime import datetime

APP_URL = "https://ted-rag-final.vercel.app"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_stats():
    """בדיקת endpoint /api/stats"""
    print_section("בדיקת GET /api/stats")
    
    try:
        response = requests.get(f"{APP_URL}/api/stats", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("\n✅ הצלחה! תשובה:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # בדיקת שדות נדרשים
                required = ["chunk_size", "overlap_ratio", "top_k"]
                missing = [k for k in required if k not in data]
                if missing:
                    print(f"\n⚠️ אזהרה: שדות חסרים: {missing}")
                else:
                    print("\n✅ כל השדות הנדרשים קיימים")
                    
            except json.JSONDecodeError:
                print(f"\n❌ שגיאה: התשובה לא JSON תקין")
                print(f"תשובה: {response.text[:500]}")
        else:
            print(f"\n❌ שגיאה! Status Code: {response.status_code}")
            print(f"תשובה: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - השרת לא הגיב בזמן")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - לא ניתן להתחבר לשרת")
    except Exception as e:
        print(f"❌ שגיאה: {e}")

def test_prompt():
    """בדיקת endpoint /api/prompt"""
    print_section("בדיקת POST /api/prompt")
    
    test_question = "Find a TED talk about fear"
    payload = {"question": test_question}
    
    print(f"שולח שאלה: {test_question}")
    
    try:
        response = requests.post(
            f"{APP_URL}/api/prompt",
            json=payload,
            timeout=60,  # יותר זמן כי זה עלול לקחת זמן
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("\n✅ הצלחה! תשובה:")
                
                # בדיקת שדות נדרשים
                required_keys = ["response", "context", "Augmented_prompt"]
                missing = [k for k in required_keys if k not in data]
                
                if missing:
                    print(f"❌ שדות חסרים: {missing}")
                else:
                    print("✅ כל השדות הנדרשים קיימים")
                    
                    # בדיקת response
                    if data.get('response'):
                        print(f"\n📝 תשובת המודל (100 תווים ראשונים):")
                        print(data['response'][:100] + "...")
                    else:
                        print("⚠️ תשובת המודל ריקה")
                    
                    # בדיקת context
                    context = data.get('context', [])
                    if isinstance(context, list) and len(context) > 0:
                        print(f"\n📚 נמצאו {len(context)} chunks ב-context")
                        first_chunk = context[0]
                        required_chunk_keys = ["talk_id", "title", "chunk", "score"]
                        chunk_missing = [k for k in required_chunk_keys if k not in first_chunk]
                        if chunk_missing:
                            print(f"⚠️ שדות חסרים ב-context: {chunk_missing}")
                        else:
                            print("✅ מבנה ה-context תקין")
                    else:
                        print("⚠️ Context ריק או לא רשימה")
                    
                    # בדיקת System Prompt
                    aug_prompt = data.get('Augmented_prompt', {})
                    system_prompt = aug_prompt.get('System', '')
                    if "You are a TED Talk assistant" in system_prompt:
                        print("✅ System Prompt תקין")
                    else:
                        print("⚠️ System Prompt לא נמצא או לא תקין")
                
                # הדפסת תשובה מלאה (מוגבלת)
                print("\n📄 תשובה מלאה (מוגבלת):")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")
                
            except json.JSONDecodeError:
                print(f"\n❌ שגיאה: התשובה לא JSON תקין")
                print(f"תשובה: {response.text[:500]}")
        else:
            print(f"\n❌ שגיאה! Status Code: {response.status_code}")
            print(f"תשובה: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - השרת לא הגיב בזמן (עלול להיות תקין אם זה לוקח זמן)")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - לא ניתן להתחבר לשרת")
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()

def main():
    print(f"\n{'='*60}")
    print(f"  בדיקת Vercel Deployment")
    print(f"  URL: {APP_URL}")
    print(f"  זמן: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # בדיקת stats
    test_stats()
    
    # בדיקת prompt
    test_prompt()
    
    print_section("סיום בדיקות")
    print("\n💡 טיפים לפתרון בעיות:")
    print("1. ודא שמשתני הסביבה מוגדרים ב-Vercel:")
    print("   - LLMOD_API_KEY")
    print("   - PINECONE_API_KEY")
    print("   - PINECONE_INDEX_HOST")
    print("2. בדוק את ה-logs ב-Vercel Dashboard")
    print("3. ודא ש-rag_config.json קיים ב-root של הפרויקט")
    print("4. בדוק שה-deployment הצליח ב-Vercel Dashboard\n")

if __name__ == "__main__":
    main()


