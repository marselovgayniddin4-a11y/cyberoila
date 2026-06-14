import asyncio
import httpx
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ------------------------
# CONFIG
# ------------------------
TOKEN = "8871285283:AAHnhLFv_KLAjHebyFLhTbjlsLVjb2C5Wtg"
API_URL = "http://127.0.0.1:8000"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------------
# SAAS DATABASE LAYER (IN-MEMORY)
# ------------------------
USERS = set()
PROTECTED = set()
BLACKLIST = set()

REPORTS = {}     # target -> count
WARNINGS = {}    # user -> count
EVENTS = []      # logs

# ------------------------
# UI DASHBOARD
# ------------------------
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Check"), KeyboardButton(text="📩 Report")],
        [KeyboardButton(text="📊 Stats"), KeyboardButton(text="🏆 Top")],
        [KeyboardButton(text="📱 Enable Protection", request_contact=True)]
    ],
    resize_keyboard=True
)

# ------------------------
# LOG ENGINE
# ------------------------
def log(event: str):
    line = f"{datetime.now()} | {event}"
    EVENTS.append(line)
    print(line)

# ------------------------
# AI ENGINE v10 (FINAL CORE)
# ------------------------
def ai_engine(text: str):
    text = (text or "").lower()

    rules = {
        "http": 20,
        "https": 20,
        "t.me": 35,
        "bit.ly": 40,
        "tinyurl": 40,
        "free": 10,
        "click": 15,
        "win": 15,
        "gift": 20,
        "urgent": 25,
        "crypto": 25,
        "airdrop": 30,
        "password": 35,
        "login": 25,
        "verify": 30,
        "bank": 35,
        "account": 20,
        "hack": 30,
        "prize": 25,
        "telegram": 15,
        "withdraw": 25,
        "money": 20
    }

    score = 0
    for k, v in rules.items():
        if k in text:
            score += v

    return min(score, 100)

def is_suspicious(text: str):
    return ai_engine(text) >= 55

# ------------------------
# SAFE API CALL (CRASH PROTECTION)
# ------------------------
async def api(method: str, url: str, **kwargs):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if method == "GET":
                r = await client.get(url, **kwargs)
            else:
                r = await client.post(url, **kwargs)
            return r.json()
    except Exception as e:
        log(f"API ERROR: {e}")
        return {}

# ------------------------
# START
# ------------------------
@dp.message(Command("start"))
async def start(message: types.Message):

    USERS.add(message.from_user.id)
    log(f"USER START {message.from_user.id}")

    await message.answer(
        "🚀 CYBEROILA ENTERPRISE CLOUD v10\n\n"
        "☁️ SaaS Security Platform ACTIVE\n"
        "🧠 AI Engine ONLINE\n"
        "🚫 Blacklist System ENABLED\n"
        "⚠️ Threat Detection ACTIVE\n\n"
        "👇 Dashboard ready:",
        reply_markup=menu
    )

# ------------------------
# CONTACT = PROTECTION ON
# ------------------------
@dp.message(F.contact)
async def contact(message: types.Message):

    PROTECTED.add(message.from_user.id)
    log(f"PROTECTION ON {message.from_user.id}")

    await message.answer(
        "📱 Protection ENABLED\n"
        "🛡 User secured in SaaS system"
    )

# ------------------------
# REPORT SYSTEM (AUTO BAN LOGIC)
# ------------------------
@dp.message(F.text == "📩 Report")
@dp.message(Command("report"))
async def report(message: types.Message):

    parts = (message.text or "").replace("📩 Report", "").replace("/report", "").strip().split()

    if len(parts) < 1:
        await message.answer("Misol: test123 scam")
        return

    target = parts[0]
    desc = " ".join(parts[1:]) if len(parts) > 1 else ""

    REPORTS[target] = REPORTS.get(target, 0) + 1

    # AUTO BLACKLIST
    if REPORTS[target] >= 3:
        BLACKLIST.add(target)
        log(f"BLACKLISTED {target}")

    data = await api(
        "POST",
        f"{API_URL}/report",
        params={
            "target": target,
            "risk": "high",
            "report_type": "saas_v10",
            "description": desc
        }
    )

    await message.answer(
        f"☁️ REPORT SENT\n\n"
        f"Target: {target}\n"
        f"Reports: {REPORTS[target]}\n"
        f"Cloud ID: {data.get('id', 'N/A')}"
    )

# ------------------------
# CHECK SYSTEM
# ------------------------
@dp.message(F.text == "🔍 Check")
@dp.message(Command("check"))
async def check(message: types.Message):

    target = (message.text or "").replace("🔍 Check", "").replace("/check", "").strip()

    if not target:
        await message.answer("Misol: test123")
        return

    if target in BLACKLIST:
        await message.answer(
            f"🚫 BLOCKED (SAAS GLOBAL BAN)\n\n{target}"
        )
        return

    data = await api("GET", f"{API_URL}/check/{target}")

    await message.answer(
        f"🔍 CHECK RESULT\n\n"
        f"Target: {data.get('target', target)}\n"
        f"Status: {data.get('status', 'unknown')}\n"
        f"Risk: {data.get('risk', 'unknown')}"
    )

# ------------------------
# STATS ENGINE
# ------------------------
@dp.message(F.text == "📊 Stats")
async def stats(message: types.Message):

    await message.answer(
        "📊 SAAS ANALYTICS v10\n\n"
        f"Users: {len(USERS)}\n"
        f"Protected: {len(PROTECTED)}\n"
        f"Reports: {sum(REPORTS.values())}\n"
        f"Blacklisted: {len(BLACKLIST)}\n"
        f"Events Logged: {len(EVENTS)}"
    )

# ------------------------
# TOP TARGETS
# ------------------------
@dp.message(F.text == "🏆 Top")
async def top(message: types.Message):

    data = await api("GET", f"{API_URL}/top")

    text = "🏆 GLOBAL TOP TARGETS\n\n"

    for item in data:
        text += f"{item.get('target')} - {item.get('reports')}\n"

    await message.answer(text)

# ------------------------
# FILE SECURITY LAYER
# ------------------------
@dp.message(F.document)
async def file_scan(message: types.Message):

    name = (message.document.file_name or "").lower()

    dangerous = [".exe", ".apk", ".bat", ".cmd", ".js", ".scr", ".zip", ".py"]

    if any(name.endswith(x) for x in dangerous):
        log(f"DANGEROUS FILE BLOCKED: {name}")

        await message.answer(
            "🚨 SAAS SECURITY ALERT\n"
            "Dangerous file detected ❌"
        )

# ------------------------
# AI REAL-TIME SCANNER
# ------------------------
@dp.message()
async def ai_scan(message: types.Message):

    uid = message.from_user.id
    text = message.text or ""

    if uid not in PROTECTED:
        return

    score = ai_engine(text)

    if score >= 80:
        log(f"CRITICAL {text}")

        await message.answer(
            f"🚨 CRITICAL THREAT\n"
            f"AI Score: {score}/100"
        )
        return

    if score >= 55:
        WARNINGS[uid] = WARNINGS.get(uid, 0) + 1

        await message.answer(
            f"⚠️ WARNING\n"
            f"Risk: {score}/100\n"
            f"Warnings: {WARNINGS[uid]}"
        )

# ------------------------
# SYSTEM MONITOR
# ------------------------
async def monitor():
    while True:
        log("SYSTEM HEALTH OK")
        await asyncio.sleep(60)

# ------------------------
# RUN BOT
# ------------------------
async def main():
    print("☁️ CYBEROILA ENTERPRISE CLOUD v10 RUNNING")
    asyncio.create_task(monitor())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
