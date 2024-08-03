from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont
from piper.voice import PiperVoice
import json
import wave
import textwrap
import os
import random

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
    overlay_width = int(size[0] * 0.6)  # Smaller width (60% of video width)
    overlay_height = size[1]  # Full height
    
    img = Image.new('RGBA', (overlay_width, overlay_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.truetype("LiberationSerif-Bold.ttf", font_size + 6)
    small_text_font = ImageFont.truetype("LiberationSerif-Regular.ttf", font_size - 4)
    text_font = ImageFont.truetype("LiberationSerif-Regular.ttf", font_size)

    title = "AM I THE ASSHOLE?"
    username = "u/throwaway12345"
    subreddit = "r/AmItheAsshole"

    wrapped_text = textwrap.fill(text, width=40)  # Adjust width for vertical format
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

model = "models/en_US-amy-medium.onnx"
voice = PiperVoice.load(model)
wav_file = wave.open("story.wav", "w")
audio = voice.synthesize(story_text,wav_file)


# Speed up audio
audio = AudioSegment.from_file("story.wav")
speed = 1.1
new_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)})
new_audio = new_audio.set_frame_rate(audio.frame_rate)
new_audio.export("story_fast.wav", format="wav")

# Load video and audio
background_video = VideoFileClip("Background.mp4")
audio_clip = AudioFileClip("story_fast.wav")

audio_duration = audio_clip.duration
video_duration = background_video.duration

if audio_duration > video_duration:
    loops = int(audio_duration // video_duration) + 1
    background_video = concatenate_videoclips([background_video] * loops)

# Resize background video to vertical (9:16) format
background_video = background_video.resize(height=1920)
background_video = background_video.crop(x_center=background_video.w // 2, width=1080)

# Calculate a random start time ensuring the audio fits within the video length
max_start_time = max(0, video_duration - audio_duration)
start_time = random.uniform(0, max_start_time)

# Create final video subclip from random start time
final_video = background_video.subclip(start_time, start_time + audio_duration)

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
split_video_if_necessary(final_video, max_duration=59)

# Cleanup
os.remove("story.wav")
os.remove("story_fast.wav")
os.remove(text_img_path)
