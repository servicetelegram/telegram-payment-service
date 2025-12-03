import os
from flask import Flask, request, abort
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ======= TOKEN DEL BOT =======
# (DA NON METTERE NEL CODICE — VIENE PRESO DALLE VARIABILI D'AMBIENTE DI DETA)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN non impostato. Inseriscilo nelle Environment Variables di Deta Space.")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# ======= LINK STRIPE (CORRETTI) =======
PREZZI = {
    "30": "eVq00c5gS1qUda3acv9oc0a",
    "100": "8x2dR29x80mQfib0BV9oc0b",
    "250": "aFa4gs38K7Pi2vpbgz9oc0c",
    "600": "bJe28k38KfhK6LFacv9oc0g",
    "1500": "3cIfZaeRs1qUc5Z1FZ9oc0j"
}

crediti_utente = {}

# ======= FUNZIONI DI BASE =======
def debug_print(msg):
    try:
        print(msg, flush=True)
    except:
        pass

def menu_principale(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 Comprare Crediti", callback_data="crediti"))
    markup.add(InlineKeyboardButton("⚡ Servizi Disponibili", callback_data="servizi"))
    markup.add(InlineKeyboardButton("ℹ️ Informazioni", callback_data="info"))
    markup.add(InlineKeyboardButton("🆘 Supporto", callback_data="supporto"))

    bot.send_message(
        chat_id,
        "🚀 *Benvenuto nel Bot Premium!*\nScegli un'opzione dal menu:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ======= COMANDO /START =======
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    crediti_utente.setdefault(chat_id, 0)
    menu_principale(chat_id)

# ======= MENU PACCHETTI =======
def mostra_pacchetti(chat_id, msg_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💠 30 Crediti – 1,99€", url=f"https://buy.stripe.com/{PREZZI['30']}"))
    markup.add(InlineKeyboardButton("🔷 100 Crediti – 4,99€", url=f"https://buy.stripe.com/{PREZZI['100']}"))
    markup.add(InlineKeyboardButton("🔵 250 Crediti – 9,99€", url=f"https://buy.stripe.com/{PREZZI['250']}"))
    markup.add(InlineKeyboardButton("🟣 600 Crediti – 19,99€", url=f"https://buy.stripe.com/{PREZZI['600']}"))
    markup.add(InlineKeyboardButton("🟡 1500 Crediti – 39,99€", url=f"https://buy.stripe.com/{PREZZI['1500']}"))

    bot.edit_message_text(
        "💳 *Scegli il tuo Pacchetto Crediti:*\n\nPiù crediti acquisti, più risparmi! 🔥",
        chat_id,
        msg_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ======= CALLBACK BUTTON HANDLER =======
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        if call.data == "crediti":
            mostra_pacchetti(call.message.chat.id, call.message.message_id)

        elif call.data == "servizi":
            bot.edit_message_text(
                "⚡ *Servizi disponibili con crediti:*\n\n"
                "• 🧠 Risposte AI\n"
                "• 🔍 Ricerca avanzata\n"
                "• 📄 Generazione testi\n"
                "• 🎨 Generazione immagini\n"
                "• 🔧 E molto altro...\n\n"
                "Acquista un pacchetto per iniziare!",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )

        elif call.data == "info":
            bot.edit_message_text(
                "ℹ️ *Informazioni*\n\n"
                "• I crediti non scadono mai\n"
                "• Pagamenti sicuri tramite Stripe\n"
                "• Assistenza sempre disponibile",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )

        elif call.data == "supporto":
            bot.edit_message_text(
                "🆘 *Supporto*\n\nContatta l’assistenza:\n@IlTuoUsernameSupporto",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )

    except Exception as e:
        debug_print(f"Callback error: {e}")

# ======= FLASK SERVER PER IL WEBHOOK =======
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot attivo!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") != "application/json":
        abort(400)
    
    raw = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(raw)
    bot.process_new_updates([update])
    return "OK", 200

# ======= RUN =======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
