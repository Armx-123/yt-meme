import discord
from discord.ext import commands
import aiohttp  # Library for asynchronous downloads
import os

async def download_attachments(channel,folder):
    async with aiohttp.ClientSession() as session:  # Create a session for downloads
        # Create the downloads folder if it doesn't exist
        os.makedirs("downloads", exist_ok=True)

        all_downloaded = True  # Flag to track download completion

        async for message in channel.history():
            for attachment in message.attachments:
                filename = attachment.filename  # Get the attachment filename
                url = attachment.url
                async with session.get(url) as response:  # Download the attachment
                    if response.status == 200:  # Check for successful download
                        data = await response.read()

                        # Ensure filename includes extension
                        if not filename.endswith(os.path.splitext(filename)[1]):
                            filename = f"{filename}{os.path.splitext(filename)[1]}"

                        filepath = f"{folder}/{filename}"  # Construct filepath
                        with open(filepath, "wb") as f:
                            f.write(data)
                            print(f"Downloaded attachment: {filename}")
                    else:
                        print(f"Failed to download attachment: {filename} (Status: {response.status})")
                        all_downloaded = False  # Set flag to False if any download fails

            # Exit loop if all attachments downloaded or an error occurs
            if not all_downloaded:
                break

        if all_downloaded:
            print("All attachments downloaded. Closing bot...")
            await client.close()

intents = discord.Intents.default()
intents.messages = True  # Subscribe to message events

# Initialize bot with intents
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    channel = client.get_channel(1237776605817077790)  # Replace CHANNEL_ID with the ID of the channel you want to download attachments from
    await download_attachments(channel,"Data")
#   await download_attachments(channel,"temp")

client.run(os.environ['TOKEN'])


