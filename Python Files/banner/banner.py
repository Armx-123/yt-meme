from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
from subs import get_subscriber_count
import cv2
import numpy as np
import os

# Create a black background image of custom dimensions (2560x1440)
width, height = 2560, 1440
background = Image.new('RGB', (width, height), (0, 0, 0))

# Function to add images to the background while maintaining aspect ratio
def add_images(base_image, image_paths, positions, sizes):
    for image_path, pos, size in zip(image_paths, positions, sizes):
        img = Image.open(image_path)
        
        # Calculate the new size while maintaining the aspect ratio
        aspect_ratio = img.width / img.height
        if img.width > img.height:
            new_width = size
            new_height = int(size / aspect_ratio)
        else:
            new_height = size
            new_width = int(size * aspect_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)  # Resize while maintaining aspect ratio
        
        base_image.paste(img, pos, img.convert('RGBA'))
    return base_image

# Function to add text and emojis to the background using Pilmoji
def add_texts_and_emojis(base_image, texts, positions, font_paths, font_sizes):
    with Pilmoji(base_image) as pilmoji:
        for text, pos, font_path, font_size in zip(texts, positions, font_paths, font_sizes):
            font = ImageFont.truetype(font_path, font_size)
            pilmoji.text(pos, text, fill="white", font=font)
    return base_image

# Function to create an image with rounded corners
def image(image, r, t, c):
    c += (255,)  # Ensure the color includes the alpha channel

    h, w = image.shape[:2]
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # Create new image with transparency (four-channel)
    new_image = np.zeros((h + 2 * t, w + 2 * t, 4), np.uint8)

    # Draw four rounded corners
    cv2.ellipse(new_image, (int(r + t / 2), int(r + t / 2)), (r, r), 180, 0, 90, c, t)
    cv2.ellipse(new_image, (int(w - r + 3 * t / 2 - 1), int(r + t / 2)), (r, r), 270, 0, 90, c, t)
    cv2.ellipse(new_image, (int(r + t / 2), int(h - r + 3 * t / 2 - 1)), (r, r), 90, 0, 90, c, t)
    cv2.ellipse(new_image, (int(w - r + 3 * t / 2 - 1), int(h - r + 3 * t / 2 - 1)), (r, r), 0, 0, 90, c, t)

    # Draw four edges
    cv2.line(new_image, (int(r + t / 2), int(t / 2)), (int(w - r + 3 * t / 2 - 1), int(t / 2)), c, t)
    cv2.line(new_image, (int(t / 2), int(r + t / 2)), (int(t / 2), int(h - r + 3 * t / 2)), c, t)
    cv2.line(new_image, (int(r + t / 2), int(h + 3 * t / 2)), (int(w - r + 3 * t / 2 - 1), int(h + 3 * t / 2)), c, t)
    cv2.line(new_image, (int(w + 3 * t / 2), int(r + t / 2)), (int(w + 3 * t / 2), int(h - r + 3 * t / 2)), c, t)

    # Generate masks for proper blending
    mask = new_image[:, :, 3].copy()
    mask = cv2.floodFill(mask, None, (int(w / 2 + t), int(h / 2 + t)), 128)[1]
    mask[mask != 128] = 0
    mask[mask == 128] = 1
    mask = np.stack((mask, mask, mask, mask), axis=2)

    # Blend images respecting alpha channel
    temp = np.zeros_like(new_image)
    temp[(t - 1):(h + t - 1), (t - 1):(w + t - 1), :] = image

    new_image = np.where(mask, temp, new_image)

    # Set proper alpha channel in new image
    temp_alpha = new_image[:, :, 3].copy()
    new_image[:, :, 3] = cv2.floodFill(temp_alpha, None, (int(w / 2 + t), int(h / 2 + t)), 255)[1]

    return new_image

def create_progress_bar(start, current, target, width=400, height=50, bar_color_start=(0, 255, 0, 255), bar_color_end=(0, 128, 0, 255), bg_color=(255, 255, 255, 255)):
    """
    Creates an image of a progress bar with a gradient based on start, current, and target values.

    Parameters:
    - start: The starting value.
    - current: The current value.
    - target: The target value.
    - width: The width of the progress bar image.
    - height: The height of the progress bar image.
    - bar_color_start: The starting color of the progress bar gradient with alpha.
    - bar_color_end: The ending color of the progress bar gradient with alpha.
    - bg_color: The background color of the image with alpha (default is white with full opacity).

    Returns:
    - An Image object representing the progress bar.
    """
    # Calculate the progress percentage
    progress = (current - start) / (target - start)
    progress = max(0, min(1, progress))  # Ensure the progress is between 0 and 1

    # Ensure colors are tuples
    if not isinstance(bg_color, tuple) or not isinstance(bar_color_start, tuple) or not isinstance(bar_color_end, tuple):
        raise TypeError("bg_color, bar_color_start, and bar_color_end must be tuples")

    # Create a blank image with the specified background color
    image = Image.new('RGBA', (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Calculate the width of the progress bar
    progress_width = int(progress * width)

    # Generate gradient colors for the progress bar
    def interpolate_color(start_color, end_color, factor):
        return tuple([
            int(start_color[i] + (end_color[i] - start_color[i]) * factor)
            for i in range(4)
        ])

    for x in range(progress_width):
        factor = x / (progress_width - 1) if progress_width > 1 else 0
        current_color = interpolate_color(bar_color_start, bar_color_end, factor)
        draw.line([(x, 0), (x, height)], fill=current_color)

    return image


# Example usage:
if __name__ == "__main__":
    api_key = os.environ['API']
    channel_id = 'UCT0vmR76yrI__1W2W6ELMxA'  # Replace with your actual channel ID
    subscriber_count = int(get_subscriber_count(api_key, channel_id))


    # Define start and target values based on subscriber count
    if subscriber_count == 0:
        start_value = 0
        target_value = 100
    elif 100 <= subscriber_count <= 999:
        start_value = 100
        target_value = 300
    elif 1000 <= subscriber_count < 1000000:
        start_value = (subscriber_count // 100) * 100
        target_value = start_value + 100
    else:
        start_value = max(0, subscriber_count - subscriber_count // 20)
        target_value = subscriber_count + subscriber_count // 20

    current_value = subscriber_count

    width = 4000
    height = 250
    bar_color_start = (65, 113, 222, 255)  # Start color
    bar_color_end =  (176, 119, 243, 255) # End color
    bg_color = (0, 0, 0, 255)  # Background color

    # Create and save the progress bar
    progress_bar = create_progress_bar(start_value, current_value, target_value, width, height, bar_color_start, bar_color_end, bg_color)
    progress_bar.save('progress_bar.png')

    # Create rounded progress bar image
    progress_bar_cv = cv2.imread('progress_bar.png', cv2.IMREAD_UNCHANGED)
    new_img = image(progress_bar_cv, 125, 15, (255, 255, 255))
    cv2.imwrite('curved_progress_bar.png', new_img)

    # Remove the original progress bar image
    os.remove("progress_bar.png")

    # Define image paths, positions, and sizes
    image_paths = ['curved_progress_bar.png']
    image_positions = [(900, 800)]
    image_sizes = [800]  # Single integer size for each image

    # Format the start and target values
    def format_subscriber_count(value):
        if value >= 1000000:
            return f"{value / 1000000:.1f}M"
        elif value >= 1000:
            return f"{value / 1000:.1f}K"
        return str(value)

    formatted_start_value = format_subscriber_count(start_value)
    formatted_target_value = format_subscriber_count(target_value)

    # Define texts, their positions, font paths, and sizes
    texts = ['Hello World!', 'SUBSCRIBE!', f'{formatted_start_value} Subs', f'{formatted_target_value} Subs']  # Replace with your texts
    text_positions = [(50, 50), (900, 500), (850, 850), (1650, 850)]
    text_font_path = 'Data/LO.ttf'  # Replace with your font path for text
    text_font_sizes = [40, 150, 50, 50]  # Font sizes for each text

    # Define emojis, their positions, font paths, and sizes
    emojis = ['🥳', '🎊', '🎉', '🤩'] if current_value == target_value else ['', '', '', '']
    emoji_positions = [(1600, 860)]
    emoji_font_path = 'Data/NotoColorEmoji.ttf'  # Replace with your font path for emojis
    emoji_font_sizes = [50]  # Font sizes for each emoji

    # Combine texts and emojis into one list for drawing
    combined_texts = texts + emojis
    combined_positions = text_positions + emoji_positions
    combined_font_paths = [text_font_path] * len(texts) + [emoji_font_path] * len(emojis)
    combined_font_sizes = text_font_sizes + emoji_font_sizes

    # Add images, texts, and emojis to the background
    background = add_images(background, image_paths, image_positions, image_sizes)
    background = add_texts_and_emojis(background, combined_texts, combined_positions, combined_font_paths, combined_font_sizes)
    background.save('composite_image.png')
