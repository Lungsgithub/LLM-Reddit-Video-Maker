from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont
import json
import textwrap
import os

def split_video_if_necessary(video, max_duration=60):
    if video.duration <= max_duration:
        video.write_videofile("final_story_video.mp4", codec="libx264", audio_codec="aac")
    else:
        parts = []
        start = 0
        while start < video.duration:
            end = min(start + max_duration, video.duration)
            parts.append(video.subclip(start, end))
            start = end
        for i, part in enumerate(parts):
            part.write_videofile(f"final_story_video_part{i + 1}.mp4", codec="libx264", audio_codec="aac")

def create_reddit_style_text_image(text, size, font_size=24):
    # Define a smaller size for the overlay
    overlay_width = int(size[0] * 0.35)  # Reduce width padding
    overlay_height = int(size[1] * 0.7)  # Reduce height padding
    
    img = Image.new('RGBA', (overlay_width, overlay_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.truetype("LiberationSerif-Bold.ttf", font_size + 6)
    small_text_font = ImageFont.truetype("LiberationSerif-Regular.ttf", font_size - 4)
    text_font = ImageFont.truetype("LiberationSerif-Regular.ttf", font_size)

    title = "AM I THE ASSHOLE?"
    username = "u/throwaway12345"
    subreddit = "r/AmItheAsshole"

    wrapped_text = textwrap.fill(text, width=60)
    story_lines = wrapped_text.split('\n')
    story_height = sum([draw.textbbox((0, 0), line, font=text_font)[3] for line in story_lines])

    total_height = story_height + 160  # Increase height to accommodate all text and title
    img = Image.new('RGBA', (overlay_width, total_height), (255, 255, 255, 255))

    # Draw rounded rectangle for background
    corner_radius = 20
    rounded_rectangle = Image.new('RGBA', img.size, (255, 255, 255, 0))
    mask = Image.new('L', img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([(0, 0), img.size], radius=corner_radius, fill=255)
    rounded_rectangle.paste(img, (0, 0), mask)

    draw = ImageDraw.Draw(rounded_rectangle)

    x = overlay_width / 2  # Center the text horizontally
    y = 20  # Starting y position for the top-left text

    draw.text((x, y), subreddit, font=small_text_font, fill="black", anchor="mm")
    y += 30

    draw.text((x, y), username, font=small_text_font, fill="black", anchor="mm")
    y += 50  # Adding extra space after username

    draw.text((x, y), title, font=title_font, fill="black", anchor="mm")
    y += 40  # Adding extra space after title

    for line in story_lines:
        draw.text((x, y), line, font=text_font, fill="black", anchor="mm")
        y += 30

    return rounded_rectangle

with open('story.json', 'r') as f:
    data = json.load(f)

story_text = data['story']

# Text-to-speech conversion
tts = gTTS(text=story_text, lang='en')
tts.save("story.mp3")

# Speed up audio
audio = AudioSegment.from_file("story.mp3")
speed = 1.2
new_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)})
new_audio = new_audio.set_frame_rate(audio.frame_rate)
new_audio.export("story_fast.mp3", format="mp3")

# Load video and audio
background_video = VideoFileClip("Background.webm")
audio_clip = AudioFileClip("story_fast.mp3")

audio_duration = audio_clip.duration
video_duration = background_video.duration

if (audio_duration > video_duration):
    loops = int(audio_duration // video_duration) + 1
    background_video = concatenate_videoclips([background_video] * loops)

final_video = background_video.subclip(0, audio_duration)

# Create text image with rounded rectangle
size = (final_video.w, final_video.h)
text_img = create_reddit_style_text_image(story_text, size)
text_img_path = "text.png"
text_img.save(text_img_path)

# Overlay text image on video
text_clip = ImageClip(text_img_path, duration=audio_duration).set_position(('center', 'center')).set_opacity(1)
final_video = CompositeVideoClip([final_video, text_clip])
final_video = final_video.set_audio(audio_clip)

# Split video if necessary
split_video_if_necessary(final_video, max_duration=60)

# Cleanup
os.remove("story.mp3")
os.remove("story_fast.mp3")
os.remove("story.json")
os.remove(text_img_path)