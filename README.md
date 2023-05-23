# Subtitling with Whisper
A gradio app that allows uploading of a video and multithreads the audio for subtitling using Whisper

## Description
Add subtitles to any video using the Whisper API.

The app takes an arbitrarty video, extracts the audio as mp3 and then multithreads chunks to the Whisper API

### Installing
* Clone this repo
* Ensure your python environment has the necessary dependencies
  * ImageMagick and Ghostscript
* Ensure you are exporting an 'OPENAI_API_KEY'
* Moviepy fonts require pointing to an Imagemagick install dir

### Executing program
* ```python gradio_whisper_video_subtitle_app.py```
* An public interview with Greg is included for you to use

### Observations
* Whisper API seems to handle English, French and Spanish subtitling well (not a native speaker but they seem okay). 
* Getting moviepy to add fonts is a little tricky
  * Install ImageMagick: ```brew install imagemagick```
  * Install Ghostscript: ```brew install ghostscript```
  * moviepy config on line 14 of the script then points to the fonts source (this could be different dependening on where you install)
  * I used brew so it looks like ```change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/Cellar/imagemagick/7.1.1-8_1/bin/convert"})```
