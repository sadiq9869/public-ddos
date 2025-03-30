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

# Setup logging 📝✍️
logging.basicConfig(filename='bot.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Insert your Telegram bot token here 🔑🔒
bot = telebot.TeleBot('7898888817:AAHfJQUBpUyxj2LS0v6XZ-ufQok262RPJ70')

# Overlord user IDs 👑👑
overlord_id = ["1866961136", "1807014348"]

# Group and channel details 🌐📡
GROUP_IDS = ["-1002328886935", "-1002669651081"]  # @freeddos_group12 and Vip Hacker Ddos
CHANNEL_IDS = ["-1002308316749"]  # @ddos_server69
GROUP_USERNAME = "@freeddos_group12"
CHANNEL_USERNAME = "@ddos_server69"
VIP_HACKER_DDOS_ID = "-1002669651081"  # Vip Hacker Ddos channel ID
SUPPORT_CONTACT = "@Sadiq9869"  # Overlord @Sadiq9869
PURCHASE_CONTACT = "@Rohan2349"  # Overlord @Rohan2349

# Default cooldown and attack limits ⏳⏰
COOLDOWN_TIME = 15
ATTACK_LIMIT = 10  # Default daily attack limit for non-overlords
USER_MAX_DURATION = 180  # Default max attack duration for regular users (public)
USER_OVERLORD_DURATION = 600  # Default max attack duration for overlords
PAID_USER_DURATION = 600  # Max attack duration for paid users
MAX_REFERRAL_BONUS = 5  # Max extra strikes from referrals

# To store paid users (for Thunder Arsenal) 💎💰
PAID_USERS = {}  # user_id -> expiry datetime

global_pending_attack = None
global_last_attack_time = None
pending_feedback = {}
global_attack_running = False
overlord_attack_running = False  # Separate flag for overlord attacks
attack_lock = threading.Lock()
overlord_attack_lock = threading.Lock()  # Separate lock for overlord attacks

# Files to store user data, feedback hashes, referrals, attack history, ranks, and paid users 📂📁
USER_FILE = "users.txt"
FEEDBACK_HASH_FILE = "feedback_hashes.txt"
REFERRAL_FILE = "referrals.txt"
HISTORY_FILE = "attack_history.txt"
RANK_FILE = "ranks.txt"
PAID_USERS_FILE = "paid_users.txt"

# Dictionary to store user states, feedback hashes, referral data, attack history, and ranks 📊📈
user_data = {}
feedback_hashes = set()
referral_data = {}  # To store referral counts
attack_history = {}  # To store attack history (user_id -> list of attacks)
user_ranks = {}  # To store user ranks (user_id -> rank)
global_last_attack_time = None

# Thunder Rank System 🏆🎖️
RANKS = {
    0: "Rookie Operative 🐣👶",
    10: "Cyber Enforcer 🛡️💂",
    25: "Thunder Soldier ⚔️🪖",
    50: "Elite Striker 🌟✨",
    100: "Thunder Lord 👑🔥"
}

# Daily Missions 🎯📋
DAILY_MISSIONS = {
    "attacks": {"task": "Launch 3 Attacks 🚀💥", "count": 3, "reward": 1},
    "invites": {"task": "Invite 1 Friend 📩🤝", "count": 1, "reward": 1}
}

# 🎯 Random Image URLs 🖼️📸
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

# Custom emoji theme for @freeddos_group12 🌩️⚡
custom_emojis = ["⚡", "🌩️", "🔥", "💥", "🎯", "⏳", "📸", "✅", "❌", "🛑", "💾", "🌐", "🔋"]

# Example feedback images (replace with actual URLs or file IDs) 📷🖼️
EXAMPLE_FEEDBACK_IMAGE_1 = "https://example.com/bgmi_feedback_677ping.jpg"  # First image with 677 ping
EXAMPLE_FEEDBACK_IMAGE_2 = "https://example.com/bgmi_feedback_lobby.jpg"   # Second image (lobby)

# Branded footer for all messages 🖌️🎨
def branded_footer():
    return f"\n\n⚡ **Powered by {GROUP_USERNAME}** ⚡💪\n🌩️ **feedback channel:** {CHANNEL_USERNAME} 📡🔗"

# Price list in INR (Updated with new offer, emojis, and Overlord references) 💰💸
PRICE_LIST = (
    "🌐🌐🔠🔠🔠🔠 🔠🔠🔠🔠💯💯\n"
    "🔤🔤🔤🔤🔤\n"
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
    "🔥 **SPECIAL OFFER!** 🔥💥\n"
    "⏰ **1H DDOS SELL ON ₹20** ⏰⏳\n"
    "💥 **Not 600sec but Very Effective!** 💥⚡\n"
    f"📩 **DM to Buy from Overlord {PURCHASE_CONTACT}** 📩💌\n\n"
    "💎 **Why Upgrade to Thunder Arsenal?** 💎✨\n"
    "✅ Unlimited Attacks Anytime! 🚀💥\n"
    "✅ No Cooldowns, Ever! ⏳❌\n"
    "✅ No Feedback, Ever! 📸❌\n"
    "✅ No Need To Join Channel! 📡❌\n"
    "✅ **Massive Attack Duration: 600s (Free Users: 180s)!** ⏰⏱️\n"
    "✅ Priority Support by Overlord {SUPPORT_CONTACT}! 🛠️🤗\n"
    "✅ Custom Attack Profiles! 🎨🖌️\n\n"
    "🌟 **Elite Operative Stories** 🌟📖\n"
    "👤 \"Thunder Arsenal ke saath maine BGMI mein sabko dho diya! Unstoppable!\" - @CyberEnforcer 💪🔥\n"
    "👤 \"600s duration ne mujhe legend bana diya! Best bot ever!\" - @ThunderLordX 🏆🎉\n\n"
    "📜 **Join the Thunder Hub to Unlock Full Power!** 📜🔓\n"
    f"🔗 **Strike Force:** {GROUP_USERNAME} 🤝👥\n"
    f"🔗 **Command Hub:** {CHANNEL_USERNAME} 📡🌐\n"
    "👑 **Buy Key from Overlord Seller** 👑💸\n"
    f"➡️ **DM Overlord {PURCHASE_CONTACT}** 📩💌\n"
    f"📞 **Support by Overlord {SUPPORT_CONTACT}** 📞🤗\n"
    f"{branded_footer()}"
)

def is_user_in_group(user_id):
    try:
        member = bot.get_chat_member(GROUP_IDS[0], user_id)  # Check only @freeddos_group12
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_IDS[0], user_id)  # Check only @ddos_server69
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def is_paid_user(user_id):
    """Check if user is a paid Thunder Arsenal user and their subscription is active. 💎💰"""
    if user_id in PAID_USERS:
        expiry = PAID_USERS[user_id]
        if datetime.datetime.now() < expiry:
            return True
        else:
            del PAID_USERS[user_id]  # Remove expired subscription
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

# Simulate attack progress with updates 🚀💥
def simulate_attack(chat_id, target, port, time_duration, remaining_attacks, user_name, is_overlord=False, is_paid=False):
    global global_attack_running, overlord_attack_running
    interval = time_duration / 10  # Update every 10% of the duration
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
                     f"⏳ **Strike Duration:** {time_duration}s ⏰⏱️\n"
                     f"⚡ **Remaining Strikes:** {remaining_attacks} 💣💥\n"
                     f"⏳ **Operation Progress:** 100% 🏁🎯"
                     f"{branded_footer()} 😍✨")
    if is_overlord:
        with overlord_attack_lock:
            overlord_attack_running = False
    elif is_paid:
        pass  # Paid users can run multiple attacks, no lock needed
    else:
        with attack_lock:
            global_attack_running = False

# Automatic promotion every 10 minutes 📢📣
def auto_promotion():
    while True:
        for group_id in GROUP_IDS:
            try:
                bot.send_message(group_id, 
                    "🌩️ **The Thunder Command Awaits!** 🌩️⚡\n"
                    "💥 Join the Elite Strike Force and Unleash Chaos! 💥🔥\n"
                    f"⚡ **Join {GROUP_USERNAME} and {CHANNEL_USERNAME} to Strike!** ⚡🤝👥\n"
                    f"🔋 **Upgrade to Thunder Arsenal for 600s Attack Duration (Free: {USER_MAX_DURATION}s)!** 🔋⏰⏱️\n"
                    "🔗 **Check Plans:** /start 📜📋\n"
                    "🎮 **Dominate the Cyber Battlefield!** 🎮🌐💻"
                    f"{branded_footer()} 😍🎉",
                    parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Error in auto-promotion: {e}")
        time.sleep(600)  # 10 minutes

# Start auto-promotion in a separate thread 🧵🪡
promotion_thread = threading.Thread(target=auto_promotion, daemon=True)
promotion_thread.start()

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

    # Check if user came via referral 📩🤝
    command = message.text.split()
    if len(command) > 1:
        referrer_id = command[1]
        if referrer_id in referral_data and referrer_id != user_id:
            referral_data[referrer_id] = referral_data.get(referrer_id, 0) + 1
            user_data[referrer_id]['mission_invites'] += 1
            if user_data[referrer_id].get('referral_bonus', 0) < MAX_REFERRAL_BONUS:
                user_data[referrer_id]['referral_bonus'] = user_data[referrer_id].get('referral_bonus', 0) + 1
                bot.send_message(referrer_id, 
                                 f"🎉 **New Operative Recruited!** 🎉🎊\n"
                                 f"⚡ **You Earned 1 Extra Strike!** ⚡💥🔥\n"
                                 f"💥 **Total Extra Strikes:** {user_data[referrer_id]['referral_bonus']} 🎁✨"
                                 f"{branded_footer()} 😍🤗")
            update_user_rank(referrer_id, 2)  # 2 points for a referral
            save_referrals()
            save_users()

    response = (f"🌩️ **Welcome to Thunder Command, {user_name}!** 🌩️😍✨\n"
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
                f"💎 **Want 600s Attack Duration? Upgrade to Thunder Arsenal! (Free: {USER_MAX_DURATION}s)** 💎⏰⏱️\n"
                f"{PRICE_LIST}")
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['myinfo'])
def my_info(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)

    # Check if user is in group and channel (skip for overlords and paid users) 🔍👀
    if not is_overlord and not is_paid and not is_user_in_group(user_id):
        bot.reply_to(message, f"🌪️ **Operative, Join the Elite Strike Force First!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} to Access Thunder Command!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return
    if not is_overlord and not is_paid and not is_user_in_channel(user_id):
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
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)

    # Check if user is in group and channel (skip for overlords and paid users) 🔍👀
    if not is_overlord and not is_paid and not is_user_in_group(user_id):
        bot.reply_to(message, f"🌪️ **Operative, Join the Elite Strike Force First!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} to Access Thunder Command!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return
    if not is_overlord and not is_paid and not is_user_in_channel(user_id):
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

    mission_status = (
        f"📜 **Daily Mission Briefing** 📜📋\n\n"
        f"🎯 **Mission 1: {DAILY_MISSIONS['attacks']['task']}** 🚀💥\n"
        f"⚡ **Progress:** {user['mission_attacks']}/{DAILY_MISSIONS['attacks']['count']} 📈📊\n"
        f"🎁 **Reward:** {DAILY_MISSIONS['attacks']['reward']} Extra Strike 🎉🎁\n\n"
        f"📩 **Mission 2: {DAILY_MISSIONS['invites']['task']}** 🤝👥\n"
        f"⚡ **Progress:** {user['mission_invites']}/{DAILY_MISSIONS['invites']['count']} 📈📊\n"
        f"🎁 **Reward:** {DAILY_MISSIONS['invites']['reward']} Extra Strike 🎉🎁\n\n"
        f"⏳ **Missions Reset At:** {user['mission_reset'].replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)} ⏰⏱️"
        f"{branded_footer()} 😍🤗"
    )
    bot.reply_to(message, mission_status)

@bot.message_handler(commands=['history'])
def attack_history_command(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)

    # Check if user is in group and channel (skip for overlords and paid users) 🔍👀
    if not is_overlord and not is_paid and not is_user_in_group(user_id):
        bot.reply_to(message, f"🌪️ **Operative, Join the Elite Strike Force First!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} to Access Thunder Command!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return
    if not is_overlord and not is_paid and not is_user_in_channel(user_id):
        bot.reply_to(message, f"🔥 **Operative, Sync with the Command Hub!** 🔥❗⚠️\n"
                              f"⚡ **Join {CHANNEL_USERNAME} to Access Thunder Command!** ⚡📡🌐"
                              f"{branded_footer()} 😓😢")
        return

    if user_id not in attack_history or not attack_history[user_id]:
        bot.reply_to(message, "📜 **Your Strike Log is Empty!** 📜📋\n"
                              "⚡ **No Strikes Launched Yet!** ⚡😢💔"
                              f"{branded_footer()} 😓😢")
        return

    history = attack_history[user_id][-5:]  # Show last 5 attacks
    history_text = "\n".join([f"🎯 **Target:** {entry['target']}:{entry['port']} 🔒 | **Duration:** {entry['duration']}s ⏰ | "
                              f"**Status:** {entry['status']} ✅ | **Time:** {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} ⏱️" 
                              for entry in history])
    bot.reply_to(message, 
                 f"📜 **Your Last 5 Strikes!** 📜📋\n\n"
                 f"{history_text}\n\n"
                 f"⚡ **Launch More Strikes to Dominate!** ⚡🚀💥"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global global_attack_running, overlord_attack_running
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)

    # Overlords and paid users can use bot anywhere; non-overlords must be in allowed groups 🔍👀
    if not is_overlord and not is_paid and str(message.chat.id) not in GROUP_IDS:
        bot.reply_to(message, "🌪️ **Operative, This Weapon Only Works in Authorized Warzones!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} or Vip Hacker Ddos to Strike!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return

    # Check if user is in group and channel (skip for overlords and paid users) 🔍👀
    if not is_overlord and not is_paid and not is_user_in_group(user_id):
        bot.reply_to(message, f"🌪️ **Operative, Join the Elite Strike Force First!** 🌪️❗⚠️\n"
                              f"⚡ **Join {GROUP_USERNAME} to Access Thunder Command!** ⚡🤝👥"
                              f"{branded_footer()} 😓😢")
        return
    if not is_overlord and not is_paid and not is_user_in_channel(user_id):
        bot.reply_to(message, f"🔥 **Operative, Sync with the Command Hub!** 🔥❗⚠️\n"
                              f"⚡ **Join {CHANNEL_USERNAME} to Access Thunder Command!** ⚡📡🌐"
                              f"{branded_footer()} 😓😢")
        return

    # Feedback requirement only for non-overlords and non-paid users 📸🖼️
    if not is_overlord and not is_paid and pending_feedback.get(user_id, False):
        bot.reply_to(message, "💥 **Operative, We Need Your Battle Intel!** 💥❗⚠️\n"
                              "📸 **Submit a BGMI Screenshot to Continue Striking!** 📸🖼️\n"
                              f"🛠️ **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗"
                              f"{branded_footer()} 😓😢")
        return

    if len(command) != 4:
        bot.reply_to(message, "❌ **Invalid Command Format!** ❌🚫\n"
                              "📜 **Usage:** /attack <IP> <PORT> <TIME> 📋\n"
                              "📌 **Examples:**\n"
                              "1️⃣ /attack 192.168.1.1 80 180 💻🌐\n"
                              "2️⃣ /attack 10.0.0.1 443 120 🌐💻\n"
                              "3️⃣ /attack 172.16.0.1 8080 150 🎮🕹️"
                              f"{branded_footer()} 😓😢")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        time_duration = int(time_duration)
        port = int(port)
    except ValueError:
        bot.reply_to(message, "❌ **Invalid Input!** ❌🚫\n"
                              "⚠️ **Port and Time must be numbers!** ⚠️🔢\n"
                              "📜 **Usage:** /attack <IP> <PORT> <TIME> 📋\n"
                              "📌 **Examples:**\n"
                              "1️⃣ /attack 192.168.1.1 80 180 💻🌐\n"
                              "2️⃣ /attack 10.0.0.1 443 120 🌐💻\n"
                              "3️⃣ /attack 172.16.0.1 8080 150 🎮🕹️"
                              f"{branded_footer()} 😓😢")
        return

    max_duration = USER_OVERLORD_DURATION if is_overlord else (PAID_USER_DURATION if is_paid else USER_MAX_DURATION)
    if time_duration > max_duration:
        bot.reply_to(message, f"⏰ **Time Limit Exceeded!** ⏰⏳\n"
                              f"⚠️ **Max Duration:** {max_duration}s for {'Overlords 👑👑' if is_overlord else 'Thunder Arsenal Operatives 💎✨' if is_paid else 'Free Users 🐣👶'} ⏱️\n"
                              "📜 **Usage:** /attack <IP> <PORT> <TIME> 📋\n"
                              "📌 **Examples:**\n"
                              "1️⃣ /attack 192.168.1.1 80 180 💻🌐\n"
                              "2️⃣ /attack 10.0.0.1 443 120 🌐💻\n"
                              "3️⃣ /attack 172.16.0.1 8080 150 🎮🕹️"
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

    # Reset daily attacks if needed 🔄♻️
    if (now - user['last_reset']).days >= 1:
        user['attacks'] = 0
        user['last_reset'] = now
        save_users()

    total_attacks = user['attacks'] - user.get('referral_bonus', 0)
    remaining_attacks = ATTACK_LIMIT + user.get('referral_bonus', 0) - total_attacks

    if not (is_overlord or is_paid) and remaining_attacks <= 0:
        bot.reply_to(message, "❌ **Out of Strikes!** ❌🚫\n"
                              "⚠️ **You've used all your daily strikes!** ⚠️💣\n"
                              "⏳ **Strikes reset daily, or upgrade to Thunder Arsenal for unlimited strikes!** 💎✨\n"
                              f"📞 **Need More Strikes? Contact Overlord {PURCHASE_CONTACT}** 📩💌"
                              f"{branded_footer()} 😓😢")
        return

    # Cooldown check for non-overlords and non-paid users ⏳⏰
    if not (is_overlord or is_paid) and user['last_attack']:
        time_since_last_attack = (now - user['last_attack']).total_seconds()
        if time_since_last_attack < COOLDOWN_TIME:
            remaining_cooldown = int(COOLDOWN_TIME - time_since_last_attack)
            bot.reply_to(message, f"⏳ **Cooldown Active!** ⏳⏰\n"
                                  f"⚠️ **Please wait {remaining_cooldown}s before launching another strike!** ⚠️⏱️\n"
                                  f"💎 **Upgrade to Thunder Arsenal for No Cooldowns!** 💎✨"
                                  f"{branded_footer()} 😓😢")
            return

    # Check if another attack is running 🔄♻️
    if is_overlord:
        if overlord_attack_running:
            bot.reply_to(message, "⚡ **Overlord Strike in Progress!** ⚡👑\n"
                                  "⏳ **Please wait for the current strike to complete!** ⏳⏰"
                                  f"{branded_footer()} 😓😢")
            return
    elif is_paid:
        pass  # Paid users can run multiple attacks
    else:
        if global_attack_running:
            bot.reply_to(message, "⚡ **Global Strike in Progress!** ⚡🌍\n"
                                  "⏳ **Please wait for the current strike to complete!** ⏳⏰\n"
                                  "💎 **Upgrade to Thunder Arsenal to bypass this!** 💎✨"
                                  f"{branded_footer()} 😓😢")
            return

    user['last_attack'] = now
    user['attacks'] += 1
    user['mission_attacks'] += 1
    save_users()

    # Update attack history 📜📋
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

    # Update rank points 📈📊
    update_user_rank(user_id, 1)  # 1 point per attack

    # Check daily mission completion 🎯📋
    if user['mission_attacks'] >= DAILY_MISSIONS['attacks']['count']:
        user['referral_bonus'] += DAILY_MISSIONS['attacks']['reward']
        user['mission_attacks'] = 0  # Reset mission progress
        bot.send_message(user_id, 
                         f"🎉 **Mission Completed!** 🎉🎊\n"
                         f"📜 **{DAILY_MISSIONS['attacks']['task']}** ✅✔️\n"
                         f"🎁 **Reward:** {DAILY_MISSIONS['attacks']['reward']} Extra Strike!** ⚡💥"
                         f"{branded_footer()} 😍🤗")
        save_users()

    # Start the attack simulation 🚀💥
    if is_overlord:
        with overlord_attack_lock:
            overlord_attack_running = True
    elif not is_paid:
        with attack_lock:
            global_attack_running = True

    remaining_attacks = "Unlimited" if (is_overlord or is_paid) else (ATTACK_LIMIT + user.get('referral_bonus', 0) - (user['attacks'] - user.get('referral_bonus', 0)))
    threading.Thread(target=simulate_attack, args=(message.chat.id, target, port, time_duration, remaining_attacks, user_name, is_overlord, is_paid)).start()

    bot.reply_to(message, 
                 f"⚡ **Thunder Strike Initiated!** ⚡🚀\n"
                 f"🎯 **Target:** `{target}:{port}` 🔒🔍\n"
                 f"⏳ **Duration:** {time_duration}s ⏰⏱️\n"
                 f"⚡ **Remaining Strikes:** {remaining_attacks} 💣💥\n"
                 f"🌩️ **Operation Started!** 🌩️⚡💪"
                 f"{branded_footer()} 😎🤩")

    # Request feedback from non-overlords and non-paid users 📸🖼️
    if not (is_overlord or is_paid):
        pending_feedback[user_id] = True
        bot.send_message(user_id, 
                         f"📸 **Operative, We Need Your Battle Intel!** 📸🖼️\n"
                         "💥 **Please send a BGMI screenshot to continue striking!** 💥🔥\n"
                         f"🛠️ **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗"
                         f"{branded_footer()} 😍🤗")

@bot.message_handler(content_types=['photo'])
def handle_feedback(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)

    if not pending_feedback.get(user_id, False):
        bot.reply_to(message, "❌ **No Feedback Required!** ❌🚫\n"
                              "⚡ **Launch a strike first with /attack!** ⚡💣💥"
                              f"{branded_footer()} 😓😢")
        return

    if is_overlord or is_paid:
        bot.reply_to(message, "❌ **Feedback Not Required!** ❌🚫\n"
                              "⚡ **Overlords and Thunder Arsenal Operatives don't need to submit feedback!** ⚡💎✨"
                              f"{branded_footer()} 😍🤗")
        return

    image_hash = hash_image(message.photo[-1].file_id)
    if not image_hash:
        bot.reply_to(message, "❌ **Error Processing Image!** ❌🚫\n"
                              "⚠️ **Please try uploading the screenshot again!** ⚠️📸\n"
                              f"🛠️ **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗"
                              f"{branded_footer()} 😓😢")
        return

    if image_hash in feedback_hashes:
        bot.reply_to(message, "❌ **Duplicate Feedback!** ❌🚫\n"
                              "⚠️ **This screenshot has already been submitted!** ⚠️📸\n"
                              "📸 **Please send a new BGMI screenshot!** 📸🖼️\n"
                              f"🛠️ **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗"
                              f"{branded_footer()} 😓😢")
        return

    save_feedback_hash(image_hash)
    pending_feedback[user_id] = False
    bot.reply_to(message, 
                 "✅ **Feedback Received!** ✅✔️\n"
                 "⚡ **You're ready to launch more strikes!** ⚡🚀💥\n"
                 "💥 **Use /attack to strike again!** 💥🔥"
                 f"{branded_footer()} 😍🤗")
    set_message_reaction(message.chat.id, message.message_id, "✅")

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in overlord_id

    user_commands = (
        "📜 **User Commands** 📜📋\n\n"
        "⚡ **Everyone can use these commands!** ⚡💪\n\n"
        "📌 **/start** - Begin your journey with Thunder Command! 🚀🌟\n"
        "   - Example: /start ✨\n\n"
        "📌 **/myinfo** - Check your operative profile and stats! 👤🌟\n"
        "   - Example: /myinfo 📊\n\n"
        "📌 **/missions** - View your daily missions and rewards! 🎯📋\n"
        "   - Example: /missions 🎁\n\n"
        "📌 **/history** - See your last 5 strikes! 📜📋\n"
        "   - Example: /history 💥\n\n"
        "📌 **/attack <IP> <PORT> <TIME>** - Launch a Thunder Strike! 💥🔥\n"
        "   - Examples:\n"
        "     1️⃣ /attack 192.168.1.1 80 180 💻🌐\n"
        "     2️⃣ /attack 10.0.0.1 443 120 🌐💻\n"
        "     3️⃣ /attack 172.16.0.1 8080 150 🎮🕹️\n\n"
    )

    overlord_commands = (
        "👑 **Overlord Commands** 👑👑\n\n"
        "⚡ **Only Overlords can use these commands!** ⚡💪\n\n"
        "📌 **/stats** - View bot usage stats! 📊📈\n"
        "   - Example: /stats ✨\n\n"
        "📌 **/broadcast <message>** - Send a message to all users! 📢📣\n"
        "   - Examples:\n"
        "     1️⃣ /broadcast New update released! Check it out! 🚀🌟\n"
        "     2️⃣ /broadcast Thunder Arsenal sale ends soon! 💎✨\n"
        "     3️⃣ /broadcast Join our event in @freeddos_group12! 🎉🎊\n\n"
    )

    if is_overlord:
        response = f"{user_commands}\n{overlord_commands}\n📞 **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗\n{branded_footer()} 😍🤗"
    else:
        response = f"{user_commands}\n📞 **Need Help? Contact Overlord {SUPPORT_CONTACT}** 📞🤗\n{branded_footer()} 😍🤗"

    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Access Denied!** ❌🚫\n"
                              "⚠️ **Only Overlords can use this command!** ⚠️👑👑"
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
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Access Denied!** ❌🚫\n"
                              "⚠️ **Only Overlords can use this command!** ⚠️👑👑"
                              f"{branded_footer()} 😓😢")
        return

    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, "❌ **Invalid Command Format!** ❌🚫\n"
                              "📜 **Usage:** /broadcast <message> 📋\n"
                              "📌 **Examples:**\n"
                              "1️⃣ /broadcast New update released! Check it out! 🚀🌟\n"
                              "2️⃣ /broadcast Thunder Arsenal sale ends soon! 💎✨\n"
                              "3️⃣ /broadcast Join our event in @freeddos_group12! 🎉🎊"
                              f"{branded_footer()} 😓😢")
        return

    broadcast_message = command[1]
    for user_id in user_data:
        try:
            bot.send_message(user_id, 
                             f"📢 **Broadcast from Overlord** 📢📣\n\n"
                             f"{broadcast_message}\n\n"
                             f"⚡ **Stay tuned for more updates!** ⚡🌟"
                             f"{branded_footer()} 😍🤗")
        except Exception as e:
            logging.error(f"Error broadcasting to {user_id}: {e}")
    bot.reply_to(message, "✅ **Broadcast Sent!** ✅✔️\n"
                          f"📢 **Message sent to all operatives!** 📢📣"
                          f"{branded_footer()} 😍🤗")

# Start the bot 🚀🌟
bot.polling()