from moviepy.editor import VideoFileClip, AudioFileClip
import cv2
from PIL import ImageFont, ImageDraw, Image
import os
import numpy as np

def extract_audio(input_video_path, output_audio_path):
    video_clip = VideoFileClip(input_video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(output_audio_path, codec='mp3')

def add_text_to_video(input_video_path, output_video_path, text_info, custom_font_path=None):
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_video_path = output_video_path + '.mp4'
    out = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size, isColor=True)

    current_text_infos = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        # Check if we need to update the text
        current_text_infos = [text_info for text_info in text_info
                              if text_info['timestamp'] <= current_timestamp <= text_info.get('end_timestamp', float('inf'))]

        for current_text_info in current_text_infos:
            text = current_text_info['text']
            font_scale = current_text_info.get('font_scale', 1)
            color = current_text_info.get('color', (255, 255, 255))
            border_color = current_text_info.get('border_color', (0, 0, 0))  # Border color
            thickness = current_text_info.get('thickness', 2)
            position = current_text_info.get('position', (50, 50))  # Default position if not specified

            if custom_font_path is not None:
                # Load custom font with PIL
                pil_img = Image.fromarray(frame)
                draw = ImageDraw.Draw(pil_img)
                font = ImageFont.truetype(custom_font_path, size=int(font_scale * 10))
                text_size = draw.textbbox(position, text, font=font)
                # Adjust Y-position considering text size
                position = (position[0], position[1] + text_size[1])

                # Draw border first
                draw.text(position, text, font=font, fill=border_color, stroke_width=thickness)
                # Draw text over the border
                draw.text(position, text, font=font, fill=color)

                frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            else:
                # Use default font
                font = cv2.FONT_HERSHEY_SIMPLEX
                text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness)
                # Adjust Y-position considering text size
                position = (position[0], position[1] + text_size[1])

                # Draw border first
                cv2.putText(frame, text, position, font, font_scale, border_color, thickness * 2, cv2.LINE_AA)
                # Draw text over the border
                cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

        out.write(frame)

    cap.release()
    out.release()

def combine_video_and_audio(input_video_path, input_audio_path, output_path):
    video_clip = VideoFileClip(input_video_path)
    audio_clip = AudioFileClip(input_audio_path)

    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_path, codec='libx264', audio_codec='libmp3lame', temp_audiofile='temp_audio.mp3', remove_temp=True)

if __name__ == "__main__":
    original_video_path = 'assets/inro.mp4'
    custom_font_path = 'assets/font.ttf'  # Replace with the path to your custom font file
    output_audio_path = 'extracted_audio.mp3'
    output_video_with_text_path = 'output_video_with_text'
    final_output_path = 'Python Files/final_output.mp4'

    # Extract audio from the original video
    extract_audio(original_video_path, output_audio_path)
    import random

# Sample data for the arrays
    with open("Data/Part.txt","r")as f:
        part =f.readline()

        emojis = [""]
        sentence = f'Memes that I stole from the internet | {part}'



    print(sentence)
    # Add text to the video at specific timestamps with optional end_timestamps
    text_info = [
        
        {'text': 'Memes', 'font_scale': 15, 'color': (255, 255, 255), 'border_color': (0, 0, 0), 'thickness': 20, 'timestamp': 0.0, 'end_timestamp': 2.66, 'position': (180, 30)},
        {'text': 'That I', 'font_scale': 18, 'color': (255, 255, 255), 'border_color': (0, 0, 0), 'thickness': 18, 'timestamp': 0.0, 'end_timestamp': 2.66, 'position': (340, 230)},
        {'text': 'borrowed from', 'font_scale': 15, 'color': (255, 255, 255), 'border_color': (0, 0, 0), 'thickness': 20, 'timestamp': 0.0, 'end_timestamp': 2.66, 'position': (100, 400)},
        {'text': 'Discord', 'font_scale': 15, 'color': (255, 255, 255), 'border_color': (0, 0, 0), 'thickness': 20, 'timestamp': 0.0, 'end_timestamp': 2.66, 'position': (440, 600)},
        {'text':"V"+part, 'font_scale': 20, 'color': (255, 255, 255), 'border_color': (0, 0, 0), 'thickness': 20, 'timestamp': 2.66, 'end_timestamp': 3.03, 'position': (270, 250)},
    ]
    add_text_to_video(original_video_path, output_video_with_text_path, text_info, custom_font_path)

    # Combine the video with added text and the extracted audio
    combine_video_and_audio(output_video_with_text_path + '.mp4', output_audio_path, final_output_path)

    # Delete intermediate files
    os.remove(output_audio_path)
    os.remove(output_video_with_text_path + '.mp4')

    with open("Data/title.txt", "w", encoding="utf-8") as f:
        f.write(sentence)
