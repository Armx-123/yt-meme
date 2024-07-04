import requests
import json
from urllib.parse import urlparse, urlunparse
from moviepy.editor import VideoFileClip, AudioFileClip
from length import get_video_duration  # Assuming this is your custom module
from download import download_video    # Assuming this is your custom module
from pick import pick                  # Assuming this is your custom module
import os
import time
TOKEN = os.environ['RYNX']
CHANNEL_ID = '1240324282094190642'
file_path = "video_urls.json"
SEND_message_proxy_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
GET_MESSAGES_URL = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
DELETE_message_proxy_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages/{{message_id}}"

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json"
}

def send_message(message):
    if not message.strip():
        return {"error": "Message is empty."}
    data = {"content": message}
    response = requests.post(SEND_message_proxy_url, headers=headers, json=data)
    return response.json()

def transform_reddit_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'v.redd.it':
        path_parts = parsed_url.path.split('/')
        if len(path_parts) > 1 and path_parts[-1].startswith('DASH_'):
            path_parts[-1] = 'DASH_AUDIO_128.mp4'
            new_path = '/'.join(path_parts)
            new_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                new_path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            return new_url
    return url

def get_audio_url_from_video_url(video_url):
    return transform_reddit_url(video_url)

def download_audio(audio_url, output_path):
    response = requests.get(audio_url)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download audio from URL: {audio_url}")
        return False

def download_and_combine_audio_video(video_url, output_path):
    audio_url = get_audio_url_from_video_url(video_url)
    
    video_file = download_video(video_url, "temp_video.mp4")
    audio_file = download_audio(audio_url, "temp_audio.mp3")  # Save audio as MP3

    if video_file and audio_file:
        video_clip = VideoFileClip(video_file)
        audio_clip = AudioFileClip(audio_file)

        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_path, codec='libx264')

        video_clip.close()
        audio_clip.close()
    else:
        print(f"Error downloading video or audio: {video_url}, {audio_url}")

def get_latest_message_url():
    response = requests.get(GET_MESSAGES_URL, headers=headers)
    messages = response.json()
    if not messages:
        return None

    latest_message = messages[0]
    embeds = latest_message.get('embeds', [])
    if embeds:
        for embed in embeds:
            if embed['type'] == 'video':
                video_info = embed.get('video', {})
                video_url = video_info.get('url')
                return video_url
    return None

def delete_latest_message():
    response = requests.get(GET_MESSAGES_URL, headers=headers)
    messages = response.json()
    if not messages:
        return False

    latest_message = messages[0]
    message_id = latest_message['id']
    url = DELETE_message_proxy_url.format(message_id=message_id)
    response = requests.delete(url, headers=headers)
    return response.status_code == 204

length = 0
with open(file_path, 'r') as file:
    data = json.load(file)

index = 0
l = len(data)
while l > 0:
    send_message(pick(file_path))
    index += 1
    l -= 1
    print(f"index: {index} length: {l}")
    time.sleep(20)

i = 0

# while length < 600:
#     latest_url = get_latest_message_url()
#     if latest_url is None:
#         break

#     dur = int(get_video_duration(latest_url))
#     print(dur)
#     if 2 <= dur <= 20:
#         video_url = latest_url
#         output_path = f"Videos/combined_video_{i}.mp4"
#         download_and_combine_audio_video(video_url, output_path)
#         length += dur

#     i += 1
#     delete_latest_message()
