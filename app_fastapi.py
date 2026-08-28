
import os
import uuid
import re
import asyncio
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn

app = FastAPI(title="APK Patcher Pro")

UPLOAD_FOLDER = os.path.expanduser("~/apkpatcher/uploads")
TOOL_PATH = os.path.expanduser("~/apkpatcher/APKPatcher.jar")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PATCH_FLAGS = {
    'ssl': '-ssl',
    'vpn': '-v',
    'paid': '-paid',
    'rmads': '-rmads',
    'rmss': '-rmss',
    'rmusb': '-rmusb',
    'fix': '-fix',
    'pine': '-pine',
    'pine2': '-pine2',
    'pkg': '-pkg',
    'tg': '-tg',
    'u': '-u'
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>☠️ APK Patcher Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #00ffcc;
            font-family: 'Courier New', monospace;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            background: #141414;
            padding: 30px;
            border-radius: 20px;
            border: 1px solid #00ffcc;
            width: 950px;
            max-width: 100%;
            box-shadow: 0 0 50px rgba(0, 255, 204, 0.1);
        }
        h1 {
            text-align: center;
            color: #ff00ff;
            text-shadow: 0 0 20px #ff00ff;
            font-size: 28px;
            margin-bottom: 5px;
        }
        .subtitle {
            text-align: center;
            color: #888;
            font-size: 13px;
            margin-bottom: 20px;
        }
        .main-layout {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .left-panel, .right-panel {
            flex: 1;
            min-width: 300px;
        }
        label {
            display: block;
            margin: 12px 0 5px;
            color: #ffaa00;
            font-weight: bold;
        }
        input[type="file"], input[type="text"] {
            width: 100%;
            padding: 10px;
            background: #1a1a1a;
            color: #fff;
            border: 1px solid #333;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
        }
        .patch-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin: 10px 0;
        }
        .patch-grid label {
            display: flex;
            align-items: center;
            gap: 8px;
            background: #1a1a1a;
            padding: 6px 10px;
            border-radius: 6px;
            border: 1px solid #2a2a2a;
            cursor: pointer;
            margin: 0;
            font-weight: normal;
            color: #ccc;
            font-size: 13px;
            transition: 0.2s;
        }
        .patch-grid label:hover {
            border-color: #00ffcc;
            background: #1f1f1f;
        }
        .patch-grid input[type="checkbox"] {
            width: 14px;
            height: 14px;
            accent-color: #ff00ff;
        }
        .advanced-section {
            background: #111;
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px dashed #333;
        }
        .btn {
            background: #ff00ff;
            color: #000;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
            transition: 0.3s;
        }
        .btn:hover {
            background: #00ffcc;
            box-shadow: 0 0 30px #00ffcc;
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .terminal {
            background: #0a0a0a;
            border: 1px solid #00ffcc;
            border-radius: 8px;
            padding: 12px;
            height: 420px;
            overflow-y: auto;
            font-size: 12px;
            white-space: pre-wrap;
            word-break: break-all;
            margin-top: 10px;
        }
        .terminal .error { color: #ff4444; }
        .terminal .success { color: #00ff88; }
        .terminal .info { color: #ffaa00; }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 8px;
            font-size: 12px;
            color: #666;
        }
        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #00ffcc;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            vertical-align: middle;
            margin-right: 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
<div class="container">
    <h1>☠️ APK Patcher Pro</h1>
    <div class="subtitle">⚡ مشغل بواسطة FastAPI الفائق</div>

    <div class="main-layout">
        <div class="left-panel">
            <form id="uploadForm">
                <label>📁 اختر ملف APK:</label>
                <input type="file" name="apk" accept=".apk" required>

                <label>🔧 اختر التصحيحات:</label>
                <div class="patch-grid">
                    <label><input type="checkbox" name="patches" value="ssl" checked> 🔓 SSL Bypass</label>
                    <label><input type="checkbox" name="patches" value="vpn"> 🌐 VPN Bypass</label>
                    <label><input type="checkbox" name="patches" value="paid"> 💰 فتح المدفوع</label>
                    <label><input type="checkbox" name="patches" value="rmads"> 🚫 إزالة الإعلانات</label>
                    <label><input type="checkbox" name="patches" value="rmss"> 📸 تعطيل التصوير</label>
                    <label><input type="checkbox" name="patches" value="rmusb"> 🔌 تعطيل USB</label>
                    <label><input type="checkbox" name="patches" value="fix"> 📱 تجاوز الجهاز</label>
                    <label><input type="checkbox" name="patches" value="pine"> 🧩 Pine Xposed</label>
                    <label><input type="checkbox" name="patches" value="pine2"> 🧩 Pine2 Xposed</label>
                    <label><input type="checkbox" name="patches" value="pkg"> 📦 Spoof Package</label>
                    <label><input type="checkbox" name="patches" value="tg"> ✈️ Telegram Plus</label>
                    <label><input type="checkbox" name="patches" value="u"> 📄 Unsigned APK</label>
                </div>

                <div class="advanced-section">
                    <label>🆔 Android ID (16 Hex chars):</label>
                    <input type="text" name="android_id" placeholder="7e9f51f096bd5c83">
                    <label style="margin-top:8px;">📂 مسار وحدات Xposed:</label>
                    <input type="text" name="xposed_path" placeholder="/path/to/module.apk">
                </div>

                <button type="submit" class="btn" id="submitBtn">⚡ تنفيذ التصحيح</button>
            </form>
        </div>

        <div class="right-panel">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:#888;font-size:12px;">📟 Terminal</span>
                <button onclick="clearTerminal()" style="background:#222;color:#888;border:1px solid #333;border-radius:4px;padding:2px 10px;cursor:pointer;font-size:11px;">🧹 مسح</button>
            </div>
            <div class="terminal" id="terminal">[⏳] جاهز للبدء...</div>
            <div class="status-bar">
                <span id="statusText" style="color:#00ffcc">● جاهز</span>
                <span id="timeText">⏱️ 00:00</span>
            </div>
        </div>
    </div>
</div>

<script>
let startTime = 0, timerInterval = null, isProcessing = false;

function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    document.getElementById('timeText').textContent = `⏱️ ${String(Math.floor(elapsed / 60)).padStart(2, '0')}:${String(elapsed % 60).padStart(2, '0')}`;
}

function appendTerminal(text, type = 'info') {
    const terminal = document.getElementById('terminal');
    const line = document.createElement('div');
    line.className = type;
    line.textContent = text;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

function clearTerminal() {
    document.getElementById('terminal').innerHTML = '';
    appendTerminal('[⏳] تم مسح الشاشة', 'info');
}

document.getElementById('uploadForm').onsubmit = async (e) => {
    e.preventDefault();
    if (isProcessing) return;
    isProcessing = true;

    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submitBtn');

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading-spinner"></span> جاري التنفيذ...';

    startTime = Date.now();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(updateTimer, 1000);

    terminal.innerHTML = '';
    appendTerminal('[🚀] بدء المعالجة...', 'info');
    appendTerminal(`[📁] الملف: ${formData.get('apk')?.name || ''}`, 'info');

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || errData.error || 'حدث خطأ أثناء المعالجة');
        }

        const blob = await response.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'patched.apk';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        appendTerminal('[✅] تم تصحيح الملف وتنزيله بنجاح!', 'success');
        appendTerminal(`[📦] الحجم: ${(blob.size / (1024 * 1024)).toFixed(2)} MB`, 'success');
        document.getElementById('statusText').textContent = '● اكتمل';
        document.getElementById('statusText').style.color = '#00ff88';

    } catch (err) {
        appendTerminal(`[❌] ${err.message}`, 'error');
        document.getElementById('statusText').textContent = '● فشل';
        document.getElementById('statusText').style.color = '#ff4444';
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '⚡ تنفيذ التصحيح';
        clearInterval(timerInterval);
        isProcessing = false;
    }
};
</script>
</body>
</html>
'''

def cleanup_files(*paths):
    for p in paths:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE

@app.post("/upload")
async def upload(
    background_tasks: BackgroundTasks,
    apk: UploadFile = File(...),
    patches: List[str] = Form(default=[]),
    android_id: Optional[str] = Form(default=""),
    xposed_path: Optional[str] = Form(default="")
):
    if not os.path.exists(TOOL_PATH):
        raise HTTPException(status_code=500, detail=f"ملف الأداة غير موجود في المسار: {TOOL_PATH}")

    if not apk.filename.lower().endswith(".apk"):
        raise HTTPException(status_code=400, detail="يجب اختيار ملف بصيغة .apk فقط")

    if not patches:
        raise HTTPException(status_code=400, detail="يرجى اختيار تصحيح واحد على الأقل")

    unique_id = str(uuid.uuid4())[:8]
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_input.apk")

    with open(input_path, "wb") as f:
        content = await apk.read()
        f.write(content)

    cmd = ["java", "-jar", TOOL_PATH, "-i", input_path]

    for p in patches:
        if p in PATCH_FLAGS:
            cmd.append(PATCH_FLAGS[p])

    if 'fix' in patches and android_id:
        android_id = android_id.strip()
        if len(android_id) == 16 and re.match(r'^[0-9a-fA-F]{16}$', android_id):
            cmd.extend(['-id', android_id])
        else:
            cleanup_files(input_path)
            raise HTTPException(status_code=400, detail="Android ID يجب أن يكون 16 خانة سداسية عشرية (Hex)")

    if ('pine' in patches or 'pine2' in patches) and xposed_path:
        paths = xposed_path.strip().split()
        if paths:
            cmd.extend(['-l'] + paths)

    if '-ssl' not in cmd and any(p in ['vpn', 'paid', 'rmads', 'rmss', 'rmusb', 'fix', 'pine', 'pine2', 'pkg', 'tg'] for p in patches):
        cmd.append('-ssl')

    # تنفيذ أمر الباتش بشكل غير متزامن
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
    except asyncio.TimeoutError:
        cleanup_files(input_path)
        raise HTTPException(status_code=500, detail="انتهت مهلة معالجة الملف (Timeout)")
    except Exception as e:
        cleanup_files(input_path)
        raise HTTPException(status_code=500, detail=str(e))

    # البحث عن الملف الناتج
    output_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.apk') and unique_id in f and 'input' not in f]

    if output_files:
        output_path = os.path.join(UPLOAD_FOLDER, output_files[0])
        # جدولة حذف الملفات بعد انتهاء التحميل
        background_tasks.add_task(cleanup_files, input_path, output_path)
        return FileResponse(
            path=output_path,
            filename=f"patched_{unique_id}.apk",
            media_type="application/vnd.android.package-archive"
        )
    else:
        cleanup_files(input_path)
        err_msg = (stdout.decode() + stderr.decode())[:1000]
        raise HTTPException(status_code=500, detail=f"فشل إنتاج الـ APK المعدل. مخرجات الأداة: {err_msg}")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)

python3 app_fastapi.py

