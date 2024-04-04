from moviepy.editor import *
import os
import whisper

def video_to_text(videopath) -> str:
    # print("Loading video...")
    video = VideoFileClip(videopath)
    filename = os.path.basename(video.filename)
    filename_without_extension = os.path.splitext(filename)[0]
    # print(filename_without_extension)

    if not os.path.exists(f"data/{filename_without_extension}"):
        os.makedirs(f"data/{filename_without_extension}")

    # print("Extracting audio...")
    audio = video.audio
    audio.write_audiofile(f"data/{filename_without_extension}/{filename_without_extension}.wav", verbose=False, logger=None)

    # print("Transcribing audio...")
    model = whisper.load_model("base")
    result = model.transcribe(f"data/{filename_without_extension}/{filename_without_extension}.wav", verbose=None)
    #print(result["text"])

    with open(f"data/{filename_without_extension}/{filename_without_extension}.txt", "w", encoding="utf-8") as file:
        file.write(result["text"])

    return result["text"]