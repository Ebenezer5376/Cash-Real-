import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ParseMode
from datetime import datetime, timedelta

TOKEN = "8281838161:AAFXzvuUpcMcN__gBvMgnCewDRuAGiuR5y8"
users = {}

# Canaux obligatoires
REQUIRED_CHANNELS = ["@telechager75", "@parisportifsz"]

# Tableau du menu (bouton "Valider mes abonnements" supprimé)
def main_menu():
    return ReplyKeyboardMarkup(
        [["💰 Mon Solde", "👥 Parrainage"],
         ["🎁 Bonus 1XBET / MELBET", "💸 Retrait"],
         ["👉 Rejoindre canal de retrait", "🎁 Bonus 7j/7j"],
         ["📞 Support"]],
        resize_keyboard=True
    )

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id not in users:
        users[user_id] = {
            "solde": 0,
            "last_bonus": None,
            "bonus_days": 0,
            "cycle_end_date": None,
            "check_passed": False,
            "welcome_bonus": 0
        }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Check", callback_data="check_channels")]
    ])
    await update.message.reply_text(
        "👋 Bienvenue sur *Cash_Real* 🌀\n\n"
        "✅ Gagne plus de 5000 FCFA chaque jour en rejoignant seulement des canaux Telegram de nos partenaires.\n\n"
        "➡️ Rejoins nos canaux :\n"
        "   - [Cash_Real1](https://t.me/telechager75)\n"
        "   - [Cash_Real2](https://t.me/parisportifsz)\n\n"
        "⌛ Clique sur *✅ Check* après avoir rejoint tous les canaux pour accéder au menu de plus vous devez vérifier chaque jour s'il y a des nouveaux canaux à rejoindre.\n"
        "⚠️ Après vérification, si tu n’es pas abonné à tous les canaux, le gain pourra être retiré.\n\n"
        "🎁 Bonus spécial : Utilise le *CODE PROMO 👉 BUSS6* pour créer ton compte 1XBET/MELBET et envoie ton ID. Tu recevras 4000 FCFA après vérification ✅",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

# Gestion du bouton ✅Check
async def check_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if not users[user_id]["check_passed"]:
        users[user_id]["check_passed"] = True
        users[user_id]["solde"] += 2000
        users[user_id]["welcome_bonus"] = 2000

        # Supprimer le bouton du message d’accueil
        await query.edit_message_reply_markup(reply_markup=None)

        # Envoyer le message de validation avec boutons Abonné / Non abonné
        await context.bot.send_message(
            chat_id=user_id,
            text="🛡️ Vérification des abonnements\n"
                 "Es-tu bien abonné à tous les canaux obligatoires ?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Abonné", callback_data=f"subscription_yes_{user_id}")],
                [InlineKeyboardButton("❌ Non abonné", callback_data=f"subscription_no_{user_id}")]
            ])
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Vous devez vous abonner à tous les canaux ❌\n"
                 "Cliquez sur ✅Check après avoir rejoint tous les canaux.",
            parse_mode=ParseMode.MARKDOWN
        )

# Gestion réponse de validation
async def subscription_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data.startswith("subscription_yes"):
        await query.edit_message_text(
            "✅ Merci pour votre fidélité !\n"
            "💰 Vous avez gagné *2000 FCFA* désormais crédité sur votre compte *Cash Real*.\n\n"
            "⚠️ NB: Si vous pensez nous tricher, sans rejoindre les canaux indiqués votre retrait pourrait être bloqué.",
            parse_mode=ParseMode.MARKDOWN
        )

        # Envoyer le menu principal
        await context.bot.send_message(
            chat_id=user_id,
            text="🎛️ 𝗠𝗲𝗻𝘂 𝗣𝗿𝗶𝗻𝗰𝗶𝗽𝗮𝗹",
            reply_markup=main_menu()
        )

    elif data.startswith("subscription_no"):
        if users[user_id]["welcome_bonus"] > 0:
            users[user_id]["solde"] -= users[user_id]["welcome_bonus"]
            users[user_id]["welcome_bonus"] = 0
        await query.edit_message_text(
            "❌ Ton bonus de bienvenue a été retiré car tu n'es pas abonné à tous les canaux.\n"
            "Rejoins tous les canaux et clique sur ✅Check pour obtenir à nouveau le bonus."
        )

# Vérification manuelle des abonnements (utilisable si besoin)
async def validate_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id not in users or not users[user_id]["check_passed"]:
        await update.message.reply_text(
            "❌ Tu dois d'abord rejoindre les canaux et cliquer sur ✅Check."
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Abonné", callback_data=f"subscription_yes_{user_id}")],
        [InlineKeyboardButton("❌ Non abonné", callback_data=f"subscription_no_{user_id}")]
    ])
    await update.message.reply_text(
        "🛡️ Vérification des abonnements\n"
        "Es-tu bien abonné à tous les canaux obligatoires ?",
        reply_markup=keyboard
    )

# Gestion du menu principal
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    text = update.message.text
    response = ""

    if user_id not in users:
        await update.message.reply_text("⚠️ Tape /start pour commencer.")
        return

    if not users[user_id]["check_passed"]:
        await update.message.reply_text(
            "❌ Tu dois d'abord rejoindre tous les canaux et cliquer sur ✅Check pour accéder au menu."
        )
        return

    if text == "💰 Mon Solde":
        response = f"🎛️ *Menu Principal*\n\n💰 Ton solde actuel est : {users[user_id]['solde']} FCFA"

    elif text == "👥 Parrainage":
        response = "🎛️ *Menu Principal*\n\n👥 Invite tes amis et gagne 500 FCFA par inscription valide ✅"

    elif text == "🎁 Bonus 1XBET / MELBET":
        response = "🎛️ *Menu Principal*\n\n🎁 Utilise le *CODE PROMO: BUSS6* et envoie ton ID 1XBET ou MELBET au 📞Support 𝗖𝗮𝘀𝗵 𝗥𝗲𝗮𝗹.\nTu recevras 4000 FCFA après vérification ✅."

    elif text == "💸 Retrait":
        solde = users[user_id]['solde']
        if solde >= 14000:
            response = "🎛️ *Menu Principal*\n\n💸 Tu peux demander un retrait ✅ Contacte 👉 @telechargeur1"
        else:
            response = f"🎛️ *Menu Principal*\n\n⚠️ Retrait dispo à partir de 14.000 FCFA. Ton solde : {solde} FCFA"

    elif text == "👉 Rejoindre canal de retrait":
        await update.message.reply_text(
            "🎛️ *Menu Principal*\n\n🔔 Rejoins notre canal officiel des retraits pour ne rien manquer !\n"
            "👉 [Accéder au canal](https://t.me/+z1IFM9Q2v3ljYmZk)",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    elif text == "🎁 Bonus 7j/7j":
        today = datetime.now().date()
        last_bonus = users[user_id].get("last_bonus")
        bonus_days = users[user_id].get("bonus_days", 0)
        cycle_end_date = users[user_id].get("cycle_end_date")

        if cycle_end_date and today < cycle_end_date:
            response = f"🎛️ *Menu Principal*\n\n⏳ Ton cycle de 7 jours est terminé. Tu pourras recommencer le {cycle_end_date} ✅"
        elif last_bonus == today:
            response = "🎛️ *Menu Principal*\n\n⚠️ Tu as déjà réclamé ton bonus aujourd'hui. Reviens demain ✅"
        else:
            users[user_id]["solde"] += 143
            users[user_id]["last_bonus"] = today
            users[user_id]["bonus_days"] = bonus_days + 1

            if users[user_id]["bonus_days"] >= 7:
                users[user_id]["cycle_end_date"] = today + timedelta(days=30)
                response = (
                    "🎛️ *Menu Principal*\n\n🎉 Félicitations ! Tu as terminé ton cycle de 7 jours ✅\n"
                    "💰 Tes 7 jours de bonus ont été crédités.\n"
                    f"📅 Nouveau cycle possible le {users[user_id]['cycle_end_date']}."
                )
            else:
                response = (
                    f"🎛️ *Menu Principal*\n\n🎉 Félicitations ! Tu as gagné *143 FCFA* aujourd'hui ✅\n"
                    f"📅 Progression : {users[user_id]['bonus_days']} / 7 jours\n\n"
                    "👉 Reviens demain pour compléter ton cycle de 7 jours."
                )

    elif text == "📞 Support":
        response = "🎛️ *Menu Principal*\n\n📞 Contacte le support ici 👉 @telechargeur1"

    if response:
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# ⚡ Création de l'application
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), menu))
app.add_handler(CallbackQueryHandler(check_channels, pattern="check_channels"))
app.add_handler(CallbackQueryHandler(subscription_response, pattern="subscription_"))

print("🤖 Cash_Real est en marche...")

# 🟢 Lancer le bot
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(app.initialize())
loop.run_until_complete(app.start())
loop.run_until_complete(app.updater.start_polling())
loop.run_forever()