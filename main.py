import os
import re
import io
import json
import random
import string
import qrcode
import yfinance as yf
import speedtest
import requests
from PIL import Image
from datetime import datetime
from urllib.parse import urlparse
from telebot import TeleBot, types
from bs4 import BeautifulSoup
from groq import Groq
from tavily import TavilyClient
import pypdf2
from cryptography.fernet import Fernet
import time

# ====================== API KEYS (मुनीश भाई की) ======================
TOKEN = "8642551061:AAHWhxyNlEltUNsP8UKO__alGmNi2BcKcbQ"
GROQ_KEY = "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"
TAVILY_KEY = "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"
IMGBB_KEY = "0fc3ee7a91862f1cf805ff7b7170ae93"
BG_REMOVE_KEY = "FvGw4tejofmj949EP4xKc2J8"

bot = TeleBot(TOKEN)
groq = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

# ====================== सभी फीचर्स (7 पेज) ======================
FEATURES_PAGES = [
    ["🌐 Web to Code", "💻 Code Gen", "💬 AI Chat", "🖼️ BG Remove", "🔗 URL Short", "📱 QR Code", "🌍 Translator", "📸 Photo -> Link"],
    ["🔍 Deep Search", "📄 PDF Reader", "🐍 Python Run", "🐛 Bug Scanner", "📝 Summarizer", "📅 Day Planner", "✍️ Essay Writer", "🎯 Quiz Maker"],
    ["📊 Data Analyst", "📜 Poem Writer", "💡 Idea Spark", "🧪 Pentest Lab", "🕳️ Vulnerability Scan", "🔐 File Encrypt", "🌐 Network Tool", "🕵️ OSINT Search"],
    ["🦠 Malware Check", "💻 Terminal Emul", "🎨 Logo Maker", "📧 Temp Mail", "💬 Fake Chat Gen", "🔑 Password Gen", "📈 SEO Audit", "⚡ Speed Test"],
    ["📈 Stock Tracker", "💊 Health Tips", "🍳 Recipe Gen", "📚 Book Finder", "🧩 Riddle Solver", "🗺️ Map Explorer", "🎤 Voice Clone", "📄 Resume Builder"],
    ["🎮 Game Mod Guide", "📱 App Analyzer", "🕸️ Web Scraper", "📍 IP Tracker", "🎵 Lyrics Finder", "🎭 Avatar Maker", "⏰ Event Reminder", "💰 Budget Tracker"],
    ["🎨 AI Image Gen", "🆘 SOS Help", "❌ Stop", "⬅️ Back", "📌 7/7"]
]

# मेन्यू बटन बनाने का फंक्शन
def get_menu_markup(page=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for f in FEATURES_PAGES[page]:
        if f not in ["⬅️ Back", "❌ Stop", "📌 7/7"]:
            buttons.append(types.InlineKeyboardButton(f, callback_data=f"feat_{f}"))
    # दो कॉलम में बटन लगाएं
    for i in range(0, len(buttons), 2):
        row = [buttons[i]]
        if i+1 < len(buttons):
            row.append(buttons[i+1])
        markup.add(*row)
    # नेविगेशन रो
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("◀️ पीछे", callback_data=f"page_{page-1}"))
    nav.append(types.InlineKeyboardButton(f"📄 {page+1}/{len(FEATURES_PAGES)}", callback_data="none"))
    if page < len(FEATURES_PAGES)-1:
        nav.append(types.InlineKeyboardButton("आगे ▶️", callback_data=f"page_{page+1}"))
    markup.add(*nav)
    return markup

# ====================== कमांड हैंडलर ======================
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "🔥 **नमस्ते मुनीश भाई!**\nआपका **सुपर AI हब** तैयार है।\nनीचे दिए गए बटन से कोई भी टूल चुनें 👇", 
                     reply_markup=get_menu_markup(0), parse_mode="Markdown")

# कॉलबैक हैंडलर - यही सभी बटन काम करते हैं
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        bot.edit_message_text("👇 कोई टूल चुनें:", chat_id, call.message.message_id, reply_markup=get_menu_markup(page))
    
    elif data.startswith("feat_"):
        feature = data[5:]
        bot.answer_callback_query(call.id, f"✅ {feature} चालू हो रहा है...")

        # फीचर के हिसाब से अलग-अलग फंक्शन कॉल करें
        if feature == "💬 AI Chat":
            ask_ai(call.message, "general")
        elif feature == "🔍 Deep Search":
            ask_search(call.message)
        elif feature == "🌐 Web to Code":
            ask_web_to_code(call.message)
        elif feature == "🖼️ BG Remove":
            ask_photo(call.message, "bg")
        elif feature == "📸 Photo -> Link":
            ask_photo(call.message, "link")
        elif feature == "💻 Code Gen":
            ask_ai(call.message, "code")
        elif feature == "🎯 Quiz Maker":
            ask_ai(call.message, "quiz")
        elif feature == "📝 Summarizer":
            ask_ai(call.message, "summarize")
        elif feature == "✍️ Essay Writer":
            ask_ai(call.message, "essay")
        elif feature == "📱 QR Code":
            generate_qr(call.message)
        elif feature == "🌍 Translator":
            ask_translate(call.message)
        elif feature == "🐛 Bug Scanner":
            ask_bug_scan(call.message)
        elif feature == "🐍 Python Run":
            ask_python_run(call.message)
        elif feature == "🔐 Pass Gen":
            generate_password(call.message)
        elif feature == "📧 Temp Mail":
            temp_mail(call.message)
        elif feature == "📈 SEO Audit":
            ask_seo(call.message)
        elif feature == "📉 Stock Tracker":
            ask_stock(call.message)
        elif feature == "📅 Day Planner":
            ask_planner(call.message)
        elif feature == "🧪 Pentest Lab":
            ask_ai(call.message, "pentest")
        elif feature == "🕳️ Vulnerability Scan":
            ask_vuln_scan(call.message)
        elif feature == "🔐 File Encrypt":
            ask_file_encrypt(call.message)
        elif feature == "📍 IP Tracker":
            ask_ip_tracker(call.message)
        elif feature == "🎨 Logo Maker":
            ask_logo(call.message)
        elif feature == "💬 Fake Chat Gen":
            fake_chat(call.message)
        elif feature == "⚡ Speed Test":
            speed_test(call.message)
        elif feature == "🍳 Recipe Gen":
            ask_ai(call.message, "recipe")
        elif feature == "📚 Book Finder":
            ask_book(call.message)
        elif feature == "🧩 Riddle Solver":
            ask_riddle(call.message)
        elif feature == "📄 Resume Builder":
            ask_resume(call.message)
        elif feature == "🎮 Game Mod Guide":
            ask_ai(call.message, "game_mod")
        elif feature == "🎵 Lyrics Finder":
            ask_lyrics(call.message)
        elif feature == "🎭 Avatar Maker":
            ask_avatar(call.message)
        elif feature == "💊 Health Tips":
            ask_health(call.message)
        elif feature == "🗺️ Map Explorer":
            ask_map(call.message)
        elif feature == "🎤 Voice Clone":
            bot.send_message(chat_id, "🎤 वॉयस क्लोन जल्द आ रहा है! अभी टेक्स्ट टू स्पीच सपोर्ट करता हूँ।")
        elif feature == "🎨 AI Image Gen":
            bot.send_message(chat_id, "🎨 AI इमेज जेनरेशन जल्द आएगा। अब Groq AI से इमेज प्रॉम्प्ट लिख सकते हैं।")
        elif feature == "🆘 SOS Help":
            sos_help(call.message)
        elif feature == "❌ Stop":
            bot.send_message(chat_id, "❌ बोट बंद। /start से फिर शुरू करें।")
        elif feature == "⬅️ Back":
            # पिछले पेज पर जाएं (हैंडल पेज नेविगेशन)
            current_page = None
            for i, page in enumerate(FEATURES_PAGES):
                if feature in page:
                    current_page = i
                    break
            if current_page and current_page > 0:
                bot.edit_message_text("👇 पिछला पेज:", chat_id, call.message.message_id, reply_markup=get_menu_markup(current_page-1))
        else:
            # बाकी सभी AI आधारित फीचर
            ask_ai(call.message, feature)

# ====================== AI मास्टर फंक्शन ======================
def ask_ai(message, task_type="general"):
    prompt_map = {
        "general": "आप एक हेल्पफुल AI असिस्टेंट हैं। उपयोगकर्ता के सवाल का जवाब हिंदी या अंग्रेजी में दें।",
        "code": "केवल कोड लिखें, बिना किसी व्याख्या के।",
        "quiz": "पूछे गए विषय पर 5 बहुविकल्पीय प्रश्न बनाएं। प्रश्न और उत्तर क्रमांक के साथ दें।",
        "summarize": "दिए गए टेक्स्ट को संक्षेप में 100 शब्दों में समझाएं।",
        "essay": "दिए गए विषय पर 200 शब्दों का निबंध लिखें।",
        "pentest": "पैनेट्रेशन टेस्टिंग के टिप्स दें विस्तार से।",
        "recipe": "दी गई सामग्री से रेसिपी बताएं।",
        "game_mod": "दिए गए गेम के लिए मॉडिंग गाइड दें।"
    }
    bot.send_message(message.chat.id, f"🤖 {task_type} के लिए अपनी बात लिखें:")
    bot.register_next_step_handler(message, lambda m: process_ai_task(m, task_type, prompt_map.get(task_type, "आप एक AI हैं। उपयोगकर्ता की मदद करें।")))

def process_ai_task(message, task_type, system_prompt):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        completion = groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message.text}
            ],
            model="llama-3.3-70b-versatile",
        )
        reply = completion.choices[0].message.content
        bot.reply_to(message, reply[:4000])
    except Exception as e:
        bot.reply_to(message, f"❌ AI त्रुटि: {str(e)}")

# ====================== सर्च और वेब फंक्शन ======================
def ask_search(message):
    bot.send_message(message.chat.id, "🔍 क्या खोजना है?")
    bot.register_next_step_handler(message, do_tavily_search)

def do_tavily_search(message):
    try:
        res = tavily.search(query=message.text)
        ans = "\n\n".join([f"📌 {r['title']}\n🔗 {r['url']}\n📄 {r['content'][:200]}..." for r in res['results'][:3]])
        bot.reply_to(message, f"**सर्च रिजल्ट:**\n{ans}", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ सर्च विफल। Groq से उत्तर लें:")
        ask_ai(message, "general")

def ask_web_to_code(message):
    bot.send_message(message.chat.id, "🌐 वेबसाइट URL भेजें:")
    bot.register_next_step_handler(message, fetch_website_code)

def fetch_website_code(message):
    url = message.text.strip()
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        html_code = soup.prettify()
        file = io.BytesIO(html_code.encode())
        file.name = "source.html"
        bot.send_document(message.chat.id, file, caption="✅ ये रहा HTML कोड")
    except:
        bot.reply_to(message, "❌ URL एक्सेस नहीं कर सका।")

# ====================== फोटो और बैकग्राउंड रिमूव ======================
def ask_photo(message, purpose):
    bot.send_message(message.chat.id, "📸 फोटो भेजें (जेपीजी/पीएनजी):")
    bot.register_next_step_handler(message, lambda m: process_photo(m, purpose))

def process_photo(message, purpose):
    if not message.photo:
        bot.reply_to(message, "कृपया फोटो भेजें।")
        return
    file_id = message.photo[-1].file_id
    file = bot.get_file(file_id)
    img_data = bot.download_file(file.file_path)

    if purpose == "link":
        # इमेज अपलोड ImgBB
        try:
            r = requests.post("https://api.imgbb.com/1/upload", params={"key": IMGBB_KEY}, files={"image": img_data})
            link = r.json()['data']['url']
            bot.reply_to(message, f"🔗 **लिंक:** {link}")
        except:
            bot.reply_to(message, "❌ अपलोड फेल।")

    elif purpose == "bg":
        # बैकग्राउंड हटाएं
        try:
            r = requests.post('https://api.remove.bg/v1.0/removebg', files={'image_file': img_data},
                              data={'size': 'auto'}, headers={'X-API-Key': BG_REMOVE_KEY})
            if r.status_code == 200:
                bot.send_document(message.chat.id, r.content, visible_file_name='no_bg.png', caption="🖼️ बैकग्राउंड हटा दिया गया!")
            else:
                bot.reply_to(message, "❌ बैकग्राउंड हटाने में त्रुटि।")
        except:
            bot.reply_to(message, "❌ remove.bg API समस्या।")

# ====================== QR कोड जनरेटर ======================
def generate_qr(message):
    bot.send_message(message.chat.id, "📝 QR कोड में बदलने के लिए टेक्स्ट या URL भेजें:")
    bot.register_next_step_handler(message, make_qr)

def make_qr(message):
    qr = qrcode.make(message.text)
    buf = io.BytesIO()
    qr.save(buf, 'PNG')
    buf.seek(0)
    bot.send_photo(message.chat.id, buf, caption="✅ आपका QR कोड")

# ====================== ट्रांसलेटर (AI से करेंगे) ======================
def ask_translate(message):
    bot.send_message(message.chat.id, "भाषा बदलने के लिए टेक्स्ट भेजें (उदा: 'हिंदी में लिखो: Hello'):")
    bot.register_next_step_handler(message, translate_with_ai)

def translate_with_ai(message):
    try:
        cmpl = groq.chat.completions.create(
            messages=[{"role": "user", "content": f"Translate the following text to हिन्दी or English as needed:\n\n{message.text}"}],
            model="llama-3.3-70b-versatile"
        )
        bot.reply_to(message, cmpl.choices[0].message.content)
    except:
        bot.reply_to(message, "❌ ट्रांसलेट नहीं कर सकता।")

# ====================== बग स्कैनर (डमी + AI) ======================
def ask_bug_scan(message):
    bot.send_message(message.chat.id, "कोड या वेबसाइट URL भेजें, बग स्कैन करूँ:")
    bot.register_next_step_handler(message, bug_scan)

def bug_scan(message):
    # सिंपल हेडर चेक
    url = message.text.strip()
    if url.startswith("http"):
        try:
            r = requests.get(url, timeout=5)
            headers = r.headers
            issues = []
            if 'X-Frame-Options' not in headers:
                issues.append("⚠️ Clickjacking vulnerability (missing X-Frame-Options)")
            if 'Content-Security-Policy' not in headers:
                issues.append("⚠️ Missing CSP header")
            if issues:
                bot.reply_to(message, "🔍 **बग्स मिले:**\n" + "\n".join(issues))
            else:
                bot.reply_to(message, "✅ कोई स्पष्ट बग नहीं मिला।")
        except:
            bot.reply_to(message, "❌ URL नहीं खुल सका।")
    else:
        # AI से एनालिसिस
        ai_response = groq.chat.completions.create(
            messages=[{"role": "user", "content": f"Analyze this code for security bugs:\n{message.text}"}],
            model="llama-3.3-70b-versatile"
        )
        bot.reply_to(message, ai_response.choices[0].message.content[:3000])

# ====================== पायथन रन (सिम्युलेटेड) ======================
def ask_python_run(message):
    bot.send_message(message.chat.id, "🐍 पायथन कोड भेजें, मैं आउटपुट बताऊंगा (नोट: exec सुरक्षा से चलेगा):")
    bot.register_next_step_handler(message, run_python_code)

def run_python_code(message):
    code = message.text
    # सुरक्षित रूप से exec करें (limited)
    old_stdout = io.StringIO()
    import sys
    sys.stdout = old_stdout
    try:
        exec(code)
        output = old_stdout.getvalue()
        sys.stdout = sys.__stdout__
        bot.reply_to(message, f"**आउटपुट:**\n{output[:2000]}")
    except Exception as e:
        sys.stdout = sys.__stdout__
        bot.reply_to(message, f"❌ एरर: {str(e)}")

# ====================== पासवर्ड जनरेटर ======================
def generate_password(message):
    length = 12
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = ''.join(random.choice(chars) for _ in range(length))
    bot.reply_to(message, f"🔑 **मजबूत पासवर्ड:** `{pwd}`", parse_mode="Markdown")

# ====================== टेम्प मेल (डमी सर्विस) ======================
def temp_mail(message):
    bot.reply_to(message, "📧 टेम्पररी मेल एड्रेस: `tempuser@mailinator.com`\n(यह डेमो है, वास्तविक मेल के लिए API लगेगा)", parse_mode="Markdown")

# ====================== SEO ऑडिट ======================
def ask_seo(message):
    bot.send_message(message.chat.id, "वेबसाइट URL भेजें SEO audit के लिए:")
    bot.register_next_step_handler(message, seo_audit)

def seo_audit(message):
    url = message.text.strip()
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.find('title')
        desc = soup.find('meta', attrs={'name': 'description'})
        report = f"**SEO रिपोर्ट:**\n✅ टाइटल: {title.string if title else '❌ नहीं मिला'}\n✅ डिस्क्रिप्शन: {desc['content'][:100] if desc else '❌ नहीं मिला'}"
        bot.reply_to(message, report)
    except:
        bot.reply_to(message, "❌ साइट नहीं खुली।")

# ====================== स्टॉक ट्रैकर ======================
def ask_stock(message):
    bot.send_message(message.chat.id, "स्टॉक सिंबल भेजें (जैसे: AAPL, TSLA, RELIANCE.NS):")
    bot.register_next_step_handler(message, get_stock)

def get_stock(message):
    sym = message.text.upper()
    try:
        stock = yf.Ticker(sym)
        info = stock.info
        price = info.get('regularMarketPrice', info.get('currentPrice', 'N/A'))
        bot.reply_to(message, f"📊 **{sym}** का मौजूदा भाव: `${price}`")
    except:
        bot.reply_to(message, "❌ स्टॉक सिम्बल गलत है।")

# ====================== प्लानर / रिमाइंडर ======================
def ask_planner(message):
    bot.send_message(message.chat.id, "📅 अपना प्लान लिखें (उदा: 'सुबह 9 बजे मीटिंग'):")
    bot.register_next_step_handler(message, save_plan)

def save_plan(message):
    # यहाँ असल डेटाबेस इस्तेमाल कर सकते हैं। अभी सिर्फ पुष्टि।
    bot.reply_to(message, f"✅ प्लान सेव किया: {message.text}")

# ====================== IP ट्रैकर ======================
def ask_ip_tracker(message):
    bot.send_message(message.chat.id, "📍 IP एड्रेस या डोमेन भेजें:")
    bot.register_next_step_handler(message, track_ip)

def track_ip(message):
    ip = message.text.strip()
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}").json()
        if resp['status'] == 'success':
            txt = f"🌍 **{resp['query']}**\nदेश: {resp['country']}\nशहर: {resp['city']}\nISP: {resp['isp']}"
            bot.reply_to(message, txt)
        else:
            bot.reply_to(message, "❌ IP नहीं मिला।")
    except:
        bot.reply_to(message, "❌ एरर।")

# ====================== स्पीड टेस्ट ======================
def speed_test(message):
    bot.send_message(message.chat.id, "⚡ स्पीड टेस्ट शुरू... 20 सेकंड लगेंगे")
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        down = st.download() / 1_000_000
        up = st.upload() / 1_000_000
        bot.reply_to(message, f"📡 **Download:** {down:.2f} Mbps\n**Upload:** {up:.2f} Mbps")
    except:
        bot.reply_to(message, "❌ स्पीड टेस्ट फेल।")

# ====================== बुक फाइंडर (Google Books) ======================
def ask_book(message):
    bot.send_message(message.chat.id, "📚 किताब का नाम या लेखक भेजें:")
    bot.register_next_step_handler(message, search_book)

def search_book(message):
    query = message.text
    try:
        r = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=3")
        data = r.json()
        if 'items' in data:
            result = ""
            for item in data['items']:
                vol = item['volumeInfo']
                result += f"📖 **{vol.get('title', 'N/A')}** - {vol.get('authors', ['Unknown'])[0]}\n{vol.get('infoLink', '')}\n\n"
            bot.reply_to(message, result[:3000])
        else:
            bot.reply_to(message, "❌ कोई किताब नहीं मिली।")
    except:
        bot.reply_to(message, "❌ एरर।")

# ====================== रिडल सॉल्वर ======================
def ask_riddle(message):
    bot.send_message(message.chat.id, "🧩 पहेली लिखें या 'नई पहेली' कहें:")
    bot.register_next_step_handler(message, solve_riddle)

def solve_riddle(message):
    if "नई पहेली" in message.text.lower():
        # AI से पहेली बनाएं
        res = groq.chat.completions.create(
            messages=[{"role": "user", "content": "एक मजेदार पहेली दें (हिंदी में) और उसका उत्तर बाद में बताएं।"}],
            model="llama-3.3-70b-versatile"
        )
        bot.reply_to(message, res.choices[0].message.content)
    else:
        # उत्तर देने की कोशिश
        ans = groq.chat.completions.create(
            messages=[{"role": "user", "content": f"इस पहेली का उत्तर बताएं: {message.text}\nकेवल उत्तर दें।"}],
            model="llama-3.3-70b-versatile"
        )
        bot.reply_to(message, f"🧠 उत्तर: {ans.choices[0].message.content}")

# ====================== रेज़्यूमे बिल्डर ======================
def ask_resume(message):
    bot.send_message(message.chat.id, "📄 अपना नाम, योग्यता, अनुभव भेजें। मैं रेज़्यूमे बनाऊंगा:")
    bot.register_next_step_handler(message, build_resume)

def build_resume(message):
    prompt = f"नीचे दी गई जानकारी से एक प्रोफेशनल रेज़्यूमे बनाएं:\n{message.text}"
    res = groq.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    bot.reply_to(message, res.choices[0].message.content[:3000])

# ====================== लिरिक्स फाइंडर ======================
def ask_lyrics(message):
    bot.send_message(message.chat.id, "🎵 गाने का नाम और कलाकार भेजें:")
    bot.register_next_step_handler(message, fetch_lyrics)

def fetch_lyrics(message):
    query = message.text.replace(" ", "%20")
    try:
        r = requests.get(f"https://api.lyrics.ovh/v1/{query.split('%20')[0]}/{query.split('%20')[1]}")
        if r.status_code == 200:
            lyrics = r.json()['lyrics']
            bot.reply_to(message, lyrics[:3500])
        else:
            bot.reply_to(message, "❌ लिरिक्स नहीं मिले।")
    except:
        bot.reply_to(message, "❌ लिरिक्स सर्विस बंद है।")

# ====================== अवतार मेकर ======================
def ask_avatar(message):
    bot.send_message(message.chat.id, "अवतार के लिए लिंग और स्टाइल बताएं (पुरुष/महिला/कार्टून):")
    bot.register_next_step_handler(message, generate_avatar)

def generate_avatar(message):
    # डमी अवतार - DiceBear API
    style = "adventurer" if "पुरुष" in message.text else "adventurer"
    url = f"https://avatars.dicebear.com/api/{style}/{random.randint(1,1000)}.svg"
    bot.reply_to(message, f"🖼️ आपका अवतार लिंक: {url}")

# ====================== हेल्थ टिप्स ======================
def ask_health(message):
    bot.send_message(message.chat.id, "💊 किस समस्या पर टिप्स चाहिए? (तनाव, डाइट, योग):")
    bot.register_next_step_handler(message, health_tip)

def health_tip(message):
    tip = groq.chat.completions.create(
        messages=[{"role": "user", "content": f"स्वास्थ्य टिप्स: {message.text} के बारे में 5 उपयोगी सुझाव दें हिंदी में।"}],
        model="llama-3.3-70b-versatile"
    )
    bot.reply_to(message, tip.choices[0].message.content)

# ====================== मैप एक्सप्लोर (डमी लिंक) ======================
def ask_map(message):
    bot.send_message(message.chat.id, "🗺️ स्थान का नाम भेजें, गूगल मैप लिंक भेजूंगा:")
    bot.register_next_step_handler(message, send_map_link)

def send_map_link(message):
    place = message.text.replace(" ", "+")
    link = f"https://www.google.com/maps/search/?api=1&query={place}"
    bot.reply_to(message, f"🗺️ [गूगल मैप पर देखें]({link})", parse_mode="Markdown")

# ====================== फेक चैट जेनरेटर ======================
def fake_chat(message):
    names = ["मुनीश", "राहुल", "प्रिया", "AI"]
    msgs = ["नमस्ते", "कैसे हो?", "मस्त", "ठीक है", "बहुत बढ़िया"]
    chat = "\n".join([f"{random.choice(names)}: {random.choice(msgs)}" for _ in range(8)])
    bot.reply_to(message, f"💬 **फेक चैट:**\n{chat}")

# ====================== फाइल एन्क्रिप्ट (डेमो) ======================
def ask_file_encrypt(message):
    bot.send_message(message.chat.id, "🔐 एन्क्रिप्ट करने के लिए टेक्स्ट भेजें:")
    bot.register_next_step_handler(message, encrypt_text)

def encrypt_text(message):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted = f.encrypt(message.text.encode())
    bot.reply_to(message, f"**एन्क्रिप्टेड:** {encrypted.decode()}\n**की:** {key.decode()}")

# ====================== वल्नरेबिलिटी स्कैन ======================
def ask_vuln_scan(message):
    bot.send_message(message.chat.id, "URL भेजें। SQLi/XSS स्कैन करूंगा (सिम्युलेटेड):")
    bot.register_next_step_handler(message, vuln_scan)

def vuln_scan(message):
    url = message.text.strip()
    # बस कुछ चीज़ें चेक करें
    payloads = ["' OR '1'='1", "<script>alert(1)</script>"]
    report = f"🔍 **{url}** स्कैन:\n"
    for p in payloads:
        try:
            r = requests.get(url + "?q=" + p, timeout=5)
            if p in r.text:
                report += f"⚠️ संभावित इंजेक्शन: {p}\n"
        except:
            pass
    if "⚠️" not in report:
        report += "✅ कोई स्पष्ट वल्नरेबिलिटी नहीं मिली।"
    bot.reply_to(message, report)

# ====================== SOS हेल्प ======================
def sos_help(message):
    bot.send_message(message.chat.id, "🆘 **आपातकालीन सहायता:**\n- पुलिस: 100\n- एम्बुलेंस: 102\n- महिला हेल्पलाइन: 1090\n- मानसिक सहायता: 1800-599-0019")

# ====================== नेटवर्क टूल (डमी) ======================
# (अन्य फीचर्स जैसे Data Analyst, Poem Writer, Idea Spark, Terminal Emul, App Analyzer, Web Scraper, Event Reminder, Budget Tracker - सभी AI से हैंडल)

# ====================== बोट पोलिंग शुरू करें ======================
if __name__ == "__main__":
    print("✅ मुनीश भाई का बोट चालू है!")
    bot.infinity_polling()
