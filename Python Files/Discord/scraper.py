import discord
from discord.ext import commands
import requests
import re
import os
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

# Discord authorization token
header = {'authorization': os.environ['AC_TOKEN']}
json_file_lock = Lock()
file ='video_urls.json'
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("/Neo"))
    print("Bot is Ready")

    # Send embed with meme counts
    total_count, server_counts = await scrape_and_get_total()
    await send_embed(user_id=831419437617643591, total_count=total_count, server_counts=server_counts)
    await bot.close()

async def send_embed(user_id, total_count, server_counts):
    user = await bot.fetch_user(user_id)
    if user:
        embed = discord.Embed(
            title="Meme Count",
            description=f"Total memes scraped: {total_count}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Memes scraped from various servers.")

        for server_name, count in server_counts.items():
            embed.add_field(name=f"Server: {server_name}", value=f"Memes scraped: {count}", inline=False)

        try:
            await user.send(embed=embed)
            print(f"Embed sent to {user.name}")
        except discord.Forbidden:
            print("I don't have permission to send messages to this user.")
        except discord.HTTPException as e:
            print(f"Failed to send embed: {e}")
    else:
        print("User not found.")

def extract_links(message_content):
    # Regular expression to find URLs in the message content
    url_pattern = r'https?://\S+'
    return re.findall(url_pattern, message_content)

def get_all_messages(channel_id, limit=100):
    all_messages = []
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100"

    while len(all_messages) < limit:
        response = requests.get(url, headers=header, timeout=35)
        if response.status_code == 200:
            messages = response.json()
            if not messages:
                break
            all_messages.extend(messages)
            if len(all_messages) >= limit:
                break
            # Set the URL to fetch messages before the last message in the current batch
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100&before={messages[-1]['id']}"
        else:
            # Print error message if request fails
            print(f"Failed to fetch messages for channel {channel_id}. Status code: {response.status_code}")
            break

    return all_messages[:limit]

def extract_video_attachments(messages):
    video_urls = []
    for message in messages:
        if 'attachments' in message and message['attachments']:
            for attachment in message['attachments']:
                if 'content_type' in attachment and attachment['content_type'].startswith('video'):
                    video_urls.append(attachment['url'])
    return video_urls

def save_urls_to_json(video_urls, file_name):
    with json_file_lock:
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r') as f:
                    existing_urls = set(json.load(f))
            except (json.JSONDecodeError, FileNotFoundError):
                existing_urls = set()
        else:
            existing_urls = set()

        new_urls = [url for url in video_urls if url not in existing_urls]
        all_urls = list(existing_urls.union(new_urls))

        with open(file_name, 'w') as f:
            json.dump(all_urls, f, indent=3)

    return new_urls

def get_channel_info(channel_id):
    url = f"https://discord.com/api/v9/channels/{channel_id}"
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch channel info for {channel_id}. Status code: {response.status_code}")
        return None

def get_guild_name(guild_id):
    url = f"https://discord.com/api/v9/guilds/{guild_id}"
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return response.json().get('name')
    else:
        print(f"Failed to fetch guild info for {guild_id}. Status code: {response.status_code}")
        return None

def scrape(channel_id):
    channel_info = get_channel_info(channel_id)
    if channel_info:
        guild_id = channel_info.get('guild_id')
        guild_name = get_guild_name(guild_id) if guild_id else "Unknown Server"
    else:
        guild_name = "Unknown Server"

    all_messages = get_all_messages(channel_id, limit=100)

    if all_messages:
        video_urls = extract_video_attachments(all_messages)
        new_urls = save_urls_to_json(video_urls, file)
        print(f"{len(new_urls)} found from {guild_name}")
        return len(new_urls), guild_name
    else:
        return 0, guild_name

async def scrape_and_get_total():
    channel_ids = [
        "1205372043772690444",
        "988639133947818064",
        "1221919254295871648",
        "934062419733536768",
        "1283117002055221271",
        "1221919422802038834",
        "1215421749424947311",
        "1185354338420400279",
        "1239483516589445162",
        "935989994735169546"
    ]

    total_count = 0
    server_counts = {}

    with ThreadPoolExecutor() as executor:
        results = executor.map(scrape, channel_ids)

    for result, server_name in results:
        total_count += result
        if server_name in server_counts:
            server_counts[server_name] += result
        else:
            server_counts[server_name] = result

    print(f"Total memes: {total_count}")
    return total_count, server_counts

bot.run(os.environ['RYNX'])
