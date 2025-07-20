from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import requests
from telegram.ext import MessageHandler, filters
import re


# Telegram Bot Token
BOT_TOKEN = "TOKEN"

# Set to store chat IDs of subscribed users
SUBSCRIBERS = set()

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

SERVER_URL = "http://127.0.0.1:8000/api/"  # Replace with your actual server URL


# Handle messages Command
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle text that are not commands
    """

    API_URL = "https://api-inference.huggingface.co/models/joeddav/xlm-roberta-large-xnli"
    headers = {"Authorization": f"Bearer TOKEN"}
    text = update.message.text
    numbers = re.findall('[0-9]+', text)
    if len(numbers) == 1:
        fridge_id = numbers[0]
    else:
        fridge_id = None#suppongo sia il fridge id
    data = {
        "inputs": text,
        "parameters": {
            "candidate_labels": ["help", "stop", "status", "behaviour"]
        }
    }

    response = requests.post(API_URL, headers=headers, json=data)
    result = response.json()

    chat_id = update.effective_chat.id

    prediction = result["labels"][0]
    if prediction == "help":
        await help_command(update, context)
    elif prediction == "stop":
        await stop(update, context)
    elif prediction == "status":
        await status_command(update, context, fridge_id)
    elif prediction == "behaviour":
        await behaviour_command(update, context,fridge_id)



# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, id=None):
    """
    Handle /start command: Add the user to the subscriber list and send chat_id to the server.
    """
    chat_id = update.effective_chat.id
    user_name = update.effective_chat.username

    # Extract fridge ID from command arguments
    if context.args:
        fridge_id = context.args[0]
    else:
        fridge_id = id


    if not fridge_id:
        await update.message.reply_text("Please provide a fridge ID.")
        return
    
    # Notify the server with chat_id and username
    payload = {
        'chat_id': chat_id,
        'username': user_name,
        'fridge_id': fridge_id,
    }
    try:
        method = f'{SERVER_URL}store_chat_id/'
        response = requests.post(method, json=payload)
        if response.status_code == 200:
            await update.message.reply_text("You are now subscribed to fridge updates!")
            await update.message.reply_text("Write /help to see the available commands.")
        else:
            await update.message.reply_text("Subscription failed. Please try again later.")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text("An error occurred. Please try again later.")
        print(f"Error sending chat_id to server: {e}")

    # Add user to local subscribers set
    SUBSCRIBERS.add(chat_id)



# Stop Command
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /stop command: Remove the user from the subscriber list.
    """
    chat_id = update.effective_chat.id
    if chat_id in SUBSCRIBERS:
        SUBSCRIBERS.remove(chat_id)
        await update.message.reply_text("You have unsubscribed from fridge updates.")
    else:
        await update.message.reply_text("You are not subscribed.")



# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command: Display a list of available commands.
    """
    await update.message.reply_text(
        "/start - Subscribe to fridge updates\n"
        "/stop - Unsubscribe from fridge updates\n"
        "/help - Show this help message\n"
        "/status - Show sensors status of a given fridge if authorized\n"
        "/behaviour - Predict user behaviour"
    )



# Status Command
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE, id=None):
    """
    Handle /status command: Send sensors status.
    """
    if context.args:
        fridge_id = context.args[0]
    else:
        fridge_id = id


    if not fridge_id:
        await update.message.reply_text("Please provide a fridge ID.")
        return

    # Get sensors status from the server
    try:
        method = f'{SERVER_URL}get_least_recent_data/'
        payload = {
            'fridge_number': fridge_id,
            'chat_id': update.effective_chat.id,
        }
        response = requests.get(method, json=payload)
        if response.status_code == 200:
            data = response.json()
            status_message = f"🆔 Fridge ID: {data['fridge']}\n" \
                             f"🌡️ Internal Temperature: {data['int_temp']}°C\n" \
                             f"🌡️ External Temperature: {data['ext_temp']}°C\n" \
                             f"💧 Internal Humidity: {data['int_hum']}%\n" \
                             f"⚡ Power Consumption: {data['power_consumption']}W"
            await update.message.reply_text(status_message)
        else:
            await update.message.reply_text("Fridge not found.")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text("An error occurred. Please try again later.")
        print(f"Error getting sensors status: {e}")
    


# Behaviour Command
async def behaviour_command(update: Update, context: ContextTypes.DEFAULT_TYPE, id=None):
    """
    Handle /behaviour command: User behaviour.
    """
    if context.args:
        fridge_id = context.args[0]
    else:
        fridge_id = id

    if not fridge_id:
        await update.message.reply_text("Please provide a fridge ID.")
        return

    chat_id = update.effective_chat.id
    method = f'{SERVER_URL}data/predict/' + str(fridge_id)
    response = requests.get(method)
    if response.status_code == 200:
        res = response.json()
        prediction = res.get('value')

        if prediction == 0:
            await context.bot.send_message(chat_id=chat_id, text='You are acting on the right track')
        elif prediction == 2:
            await context.bot.send_message(chat_id=chat_id, text='You are doing well, but you can do better')
        else:
            await context.bot.send_message(chat_id=chat_id, text='You are acting irresponsibly')
    else:
        await context.bot.send_message(chat_id=chat_id, text='Error')



"""
# Function to send a message to a specific user
async def send_message_to_user(chat_id: int, message: str):
    
    Send a message to a specific user.
    
    await bot.send_message(chat_id=chat_id, text=message)
    
    """
# Bot Setup
def main():
    """
    Start the bot and handle updates.
    """
    # Initialize the bot application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("behaviour", behaviour_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start polling for updates
    application.run_polling()

if __name__ == "__main__":
    print("Bot is running...")
    main()
