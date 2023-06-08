# Bash script equivalent at https://github.com/ggerganov/whisper.cpp/blob/master/examples/yt-wsp.sh

from whispercpp import Whisper

import ffmpeg
import numpy as np
import os
import time

w = Whisper.from_pretrained(model_name="whisper.cpp/models/ggml-small.en.bin")

start_time = time.time()
try:
    sample_rate = 16000
    youtube_vid_output, _ = ffmpeg.input(
        "sample_audios/How Animators Created the Spider-Verse ｜ WIRED [l-wUKu_V2Lk].wav",
        threads=0,
    ).output(
        "-", format="s16le", acodec="pcm_s16le", ac=1, ar=sample_rate
    ).run(
        cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True
    )
except ffmpeg.Error as e:
    raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}")
end_time = time.time()
print(f"Video download and processing time: {end_time - start_time}")

youtube_vid_audio_bits = np.frombuffer(youtube_vid_output, dtype=np.int16).flatten().astype(np.float32) / 32768.0

transcribed_text = w.transcribe(youtube_vid_audio_bits, num_proc=4)
end_time_2 = time.time()
print(f"Transcription time: {end_time_2 - end_time}")

f = open("How_Animators_Created_the_Spiderverse.txt", "w")
f.write(transcribed_text)
f.close()
