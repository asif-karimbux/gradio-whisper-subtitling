import gradio as gr
import cv2
import openai
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import pysrt
import concurrent.futures
import math
from multiprocessing import cpu_count

import requests

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/Cellar/imagemagick/7.1.1-8_1/bin/convert"})

openai.api_key = os.getenv("OPENAI_API_KEY")

def process_video_chunk(chunk_path, language):
    # Process a video chunk and add subtitles to it

    # Read video chunk
    video_chunk = VideoFileClip(chunk_path)

    # Extract audio from video chunk
    audio_path = chunk_path.replace(".mp4", "") + ".mp3"
    video_chunk.audio.write_audiofile(audio_path)

    # Transcribe the audio
    audio_file = open(audio_path, "rb")
    srt_text = openai.Audio.transcribe("whisper-1", audio_file, response_format='srt', language=language)

    # Save subtitles to SRT file
    srt_path = chunk_path.replace(".mp4", "") + ".srt"
    with open(srt_path, 'w') as f:
        f.write(srt_text)

    # Open subtitles using pysrt
    subs = pysrt.open(srt_path, encoding='utf-8')
    subtitles_items = []

    for i in subs:
        my_tup = ((i.start.seconds, i.end.seconds), i.text)
        subtitles_items.append(my_tup)

    # Generate subtitles clip
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=16, color='white')
    subtitles = SubtitlesClip(subtitles_items, generator)

    # Composite video chunk with subtitles
    result = CompositeVideoClip([video_chunk, subtitles.set_pos(('center', 'bottom'))])

    return result

def add_subtitles_to_video(input_video, language):
    # Process the video and add subtitles using parallel processing

    # Read the input video
    video = VideoFileClip(input_video.name)

    # Split the video into equal-sized chunks
    chunk_duration = 250  # Duration of each video chunk in seconds
    total_duration = video.duration
    num_chunks = math.ceil(total_duration / chunk_duration)

    # Process video chunks in parallel
    processed_chunks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        futures = []
        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, total_duration)
            chunk = video.subclip(start_time, end_time)
            chunk_path = f"chunk_{i}.mp4"
            chunk.write_videofile(chunk_path, codec='libx264', audio_codec="aac")
            future = executor.submit(process_video_chunk, chunk_path, language)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            processed_chunk = future.result()
            processed_chunks.append(processed_chunk)

    # Concatenate the processed video chunks
    final_video = concatenate_videoclips(processed_chunks)

    # Save the final video with subtitles
    subtitled_video_path = "subtitled_video.mp4"
    final_video.write_videofile(subtitled_video_path, codec='libx264', audio_codec="aac")

    # Remove files with "chunk" in the filename
    for filename in os.listdir():
        if "chunk" in filename:
            os.remove(filename)

    return subtitled_video_path

# Gradio interface
input_video = gr.inputs.File(label="Upload a video")
language_options = ["en", "es", "fr"]
language_dropdown = gr.inputs.Dropdown(choices=language_options, label="Output language for the whisper subtitles")
output_video = gr.outputs.Video(label="Video with subtitles")

iface = gr.Interface(fn=add_subtitles_to_video, inputs=[input_video, language_dropdown], outputs=output_video, title="Video Subtitle Generator", flagging_options=None)
iface.launch()
