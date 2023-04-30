import openai
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,MessageHandler, Filters


bot_token = ''
openai.api_key = ""


# Define the function that uses the ChatGPT model to generate a response
def generate_greeting(event_type, name):
    prompt = f"Generate a {event_type} greeting message for {name}:\n\n"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=3024,
        n=1,
        stop=None,
        temperature=1.1,
    )
    greeting_text = response.choices[0].text.strip()
    return greeting_text

# Define the function that handles the /start command
def start(update, context):
    user = update.message.from_user
    context.bot.send_message(chat_id=update.message.chat_id, 
                             text=f"Hello {user.first_name}! This bot can help you create a greeting text for different events. Please select an event type from the list below. To see info about bot and available commands type /help command", 
                             reply_markup=get_events_keyboard())

# Define the function that gets the events keyboard
def get_events_keyboard():
    events = ['birthday', 'prom', 'wedding', 'graduation', 'New Year', 'christmas', 'valentine', 'easter', 'thanksgiving', 'halloween']
    keyboard = [[InlineKeyboardButton(event.capitalize(), callback_data=event)] for event in events]
    return InlineKeyboardMarkup(keyboard)

# Define the function that handles the event selection
def event_selected(update, context):
    query = update.callback_query
    context.user_data['event_type'] = query.data
    context.bot.send_message(chat_id=query.message.chat_id, 
                             text=f"Please provide the name of the person for whom you would like to generate a {query.data} greeting message.")
    query.answer()

# Define the function that handles the name input
def name_input(update, context):
    message = update.message.text
    event_type = context.user_data.get('event_type')
    if event_type:
        name = message.title()
        greeting_text = generate_greeting(event_type, name)
        context.bot.send_message(chat_id=update.message.chat_id, text=greeting_text)
        context.user_data.pop('event_type', None)
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="I'm sorry, I don't understand. Please select an event type from the list below or type /help")

# Define the function that handles the /help command
def help(update, context):
    help_text = """
This bot can help you create a greeting text for different events.
Events:
    Birthday
    Prom
    Wedding
    Graduation
    New Year
    Christmas
    Valentine
    Easter
    Thanksgiving
    Halloween

Available commands:
/start - start the bot and follow this flow:
    1. Choose type of event
    2. Type name of the person to be greeted.
To generate a new greeting text type againg command /start
/help - show this help message
    """
    context.bot.send_message(chat_id=update.message.chat_id, text=help_text)

# Set up the Telegram bot
updater = Updater(token=bot_token, use_context=True)

# Create a command handler for /help
updater.dispatcher.add_handler(CommandHandler('help', help))

# Create a command handler for /start
updater.dispatcher.add_handler(CommandHandler('start', start))

# Create a callback query handler for event selection
updater.dispatcher.add_handler(CallbackQueryHandler(event_selected))

# Create a message handler for name input
updater.dispatcher.add_handler(MessageHandler(Filters.text, name_input))

# Start the bot
updater.start_polling()
