from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from deep_translator import GoogleTranslator

app = FastAPI(title="Light Translator API")

# Модель для валидации входных данных (Pydantic)
class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "en"
    source_lang: str = "auto"

# Эндпоинт API для перевода
@app.post("/api/translate")
async def translate_text(request: TranslateRequest):
    try:
        translated = GoogleTranslator(
            source=request.source_lang, 
            target=request.target_lang
        ).translate(text=request.text)
        
        return {
            "original": request.text,
            "translated": translated,
            "target_lang": request.target_lang
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка перевода: {str(e)}")

# Отдача фронтенда
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Translator</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root { 
            --primary: #8b5cf6; 
            --primary-hover: #7c3aed;
            --bg: #0f172a; 
            --card: #1e293b;
            --border: #334155;
            --text: #f1f5f9;
            --text-muted: #cbd5e1;
            --success-bg: #14532d;
            --success-text: #bbf7d0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg); 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            margin: 0;
            color: var(--text);
        }
        
        .container { 
            background: var(--card); 
            padding: 2rem; 
            border-radius: 16px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.3); 
            width: 90%; 
            max-width: 500px;
            border: 1px solid var(--border);
        }
        
        h1 { 
            color: var(--text); 
            text-align: center; 
            margin-bottom: 1.5rem; 
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        textarea { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid var(--border); 
            border-radius: 8px; 
            resize: vertical; 
            min-height: 100px; 
            font-size: 1rem;
            font-family: inherit;
            background: var(--bg);
            color: var(--text);
            transition: border-color 0.2s;
        }
        
        textarea:focus { 
            outline: none; 
            border-color: var(--primary); 
        }
        
        textarea::placeholder {
            color: var(--text-muted);
        }
        
        .controls { 
            display: flex; 
            gap: 10px; 
            margin: 1rem 0; 
        }
        
        select, button { 
            padding: 10px 16px; 
            border-radius: 8px; 
            border: none; 
            font-size: 0.9rem; 
            cursor: pointer;
            font-family: inherit;
            font-weight: 500;
        }
        
        select { 
            background: var(--bg); 
            color: var(--text); 
            flex: 1;
            border: 2px solid var(--border);
            transition: border-color 0.2s;
        }
        
        select:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        button { 
            background: var(--primary); 
            color: white; 
            font-weight: 600; 
            transition: background 0.2s;
        }
        
        button:hover { 
            background: var(--primary-hover);
        }
        
        button:disabled { 
            opacity: 0.5; 
            cursor: not-allowed; 
        }
        
        .result { 
            margin-top: 1rem; 
            padding: 1rem; 
            background: var(--success-bg); 
            border-radius: 8px; 
            color: var(--success-text); 
            min-height: 60px; 
            word-break: break-word; 
            display: none;
            border: 1px solid #166534;
        }
        
        .result.show {
            display: block;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @media (max-width: 640px) {
            .container {
                padding: 1.5rem;
            }
            
            h1 {
                font-size: 1.3rem;
            }
            
            .controls {
                flex-direction: column;
            }
            
            select, button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Легкий переводчик</h1>
        <textarea id="inputText" placeholder="Введите текст для перевода..."></textarea>
        <div class="controls">
            <select id="targetLang">
                <option value="en">Английский</option>
                <option value="ru">Русский</option>
                <option value="es">Испанский</option>
                <option value="de">Немецкий</option>
                <option value="zh-CN">Китайский</option>
            </select>
            <button id="translateBtn">Перевести</button>
        </div>
        <div id="result" class="result"></div>
    </div>

    <script>
        const btn = document.getElementById('translateBtn');
        const input = document.getElementById('inputText');
        const result = document.getElementById('result');
        const lang = document.getElementById('targetLang');

        btn.addEventListener('click', async () => {
            if (!input.value.trim()) return;
            
            btn.disabled = true;
            btn.textContent = 'Перевожу...';
            result.classList.remove('show');

            try {
                const res = await fetch('/api/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: input.value, target_lang: lang.value })
                });
                
                const data = await res.json();
                if (res.ok) {
                    result.textContent = data.translated;
                    result.classList.add('show');
                } else {
                    alert(data.detail || 'Ошибка при переводе');
                }
            } catch (err) {
                alert('Ошибка соединения с сервером');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Перевести';
            }
        });
    </script>
</body>
</html>
"""