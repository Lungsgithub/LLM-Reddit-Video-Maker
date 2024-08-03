# LLM-Reddit-Video-Maker
 Create TTS reddit videos but source the stories from an LLM

## Motivation 🤔

These videos on TikTok, YouTube and Instagram get MILLIONS of views across all platforms and require very little effort. The only original thing being done is the editing and gathering of all materials...
... but what if we can automate even the materials? 🤔

## Requirements
- Python 3.11.2
- Ollama installed
- dolphin-mistral model installed(you can change this to your liking by simply modifying "model" = "dollphin-mistral")

## Installation 👩‍💻

Install Ollama & dolphin-mistral
(for this consult the Ollama Documentation)

Clone this repository

Run `pip install -r requirements.txt`

Add an Background Video (rename in script if need be)

Add model from piper[https://github.com/rhasspy/piper/blob/master/VOICES.md]

Run `python main.py`

## Roadmap
- [✅] prompting through Ollama
- [✅] video creation through ffmpeg
- [✅] overlay(of story)
- [✅] TTS
- [✅] Take TTS local
- [❌] Add TUI
- [❌] Add Background music
