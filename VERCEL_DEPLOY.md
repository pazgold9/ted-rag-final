# הוראות Deployment ל-Vercel

## קבצים שנוצרו עבור Vercel:

1. **`vercel.json`** - קובץ קונפיגורציה של Vercel
2. **`api/prompt.py`** - Serverless function עבור `/api/prompt`
3. **`api/stats.py`** - Serverless function עבור `/api/stats`
4. **`utils.py`** - קובץ שירות משותף עם לוגיקה משותפת
5. **`requirements.txt`** - רשימת התלויות
6. **`.vercelignore`** - קבצים להתעלם מהם בזמן deployment

## שלבי Deployment:

### 1. הכנת Repository:
```bash
# ודא שכל הקבצים נשמרו ב-git
git add .
git commit -m "Add Vercel deployment files"
git push
```

### 2. התחברות ל-Vercel:

1. היכנס ל-[https://vercel.com](https://vercel.com)
2. לחץ על "New Project"
3. בחר את ה-repository שלך

### 3. הגדרת משתני סביבה (Environment Variables):

**חובה להגדיר את המשתנים הבאים ב-Vercel:**

- `LLMOD_API_KEY` - המפתח API ל-LLMOD
- `PINECONE_API_KEY` - המפתח API ל-Pinecone
- `PINECONE_INDEX_HOST` - כתובת ה-Host של האינדקס ב-Pinecone

**איך להגדיר:**
1. ב-Vercel Dashboard → Settings → Environment Variables
2. הוסף כל משתנה עם הערך שלו
3. ודא שהוא מוגדר עבור Production, Preview ו-Development

### 4. Deployment:

1. לחץ על "Deploy"
2. Vercel יבצע build אוטומטי
3. לאחר ה-build, תקבל URL כמו: `https://your-project.vercel.app`

### 5. בדיקה:

#### בדיקת `/api/stats`:
```bash
curl https://your-project.vercel.app/api/stats
```

צריך להחזיר:
```json
{
  "chunk_size": 512,
  "overlap_ratio": 0.15,
  "top_k": 8
}
```

#### בדיקת `/api/prompt`:
```bash
curl -X POST https://your-project.vercel.app/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"question": "Find a TED talk about fear"}'
```

### 6. עדכון test_deployment.py:

עדכן את המשתנה `APP_URL` בקובץ `test_deployment.py` עם ה-URL החדש:

```python
APP_URL = "https://your-project.vercel.app"
```

## הערות חשובות:

1. **קובץ rag_config.json** - ודא שהוא נשמר ב-root של הפרויקט
2. **משתני סביבה** - ללא המשתנים הנדרשים, הפונקציות לא יעבדו
3. **Pinecone Index** - ודא שהאינדקס פעיל ונגיש
4. **Budget** - מומלץ לבדוק את השימוש ב-budget אחרי כל deployment

## פתרון בעיות:

### שגיאת Import:
אם יש שגיאות import, ודא ש-`utils.py` נמצא ב-root של הפרויקט.

### שגיאת Config:
אם יש שגיאה בטעינת `rag_config.json`, ודא שהקובץ קיים ב-root.

### שגיאת API Keys:
אם יש שגיאות של authentication, בדוק שמשתני הסביבה הוגדרו נכון ב-Vercel.

## קישורים שימושיים:

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

