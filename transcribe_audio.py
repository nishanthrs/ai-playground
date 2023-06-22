# Bash script equivalent at https://github.com/ggerganov/whisper.cpp/blob/master/examples/yt-wsp.sh

from whispercpp import Whisper
from typing import Any, List

import ffmpeg
import numpy as np
import os
import subprocess
import time


def load_stt_model(model_name: str):
    w = Whisper.from_pretrained(model_name=model_name)
    return w


def download_audio_bash(youtube_url: str) -> None:
    start_time = time.time()
    subprocess.run(
        [
            "yt-dlp",
            "--extract-audio",
            "--audio-format",
            "wav",
            "--audio-quality",
            "0",
            youtube_url
        ]
    )
    end_time = time.time()
    print(f"Video download time: {end_time - start_time} seconds")


def process_audio_py(input_audio_filepath: str, output_audio_filepath: str) -> Any:
    start_time = time.time()
    try:
        sample_rate = "16k"
        youtube_vid_output, err = ffmpeg.input(
            input_audio_filepath,
            threads=0,
        ).output(
            output_audio_filepath,
            format="s16le",
            acodec="pcm_s16le",
            ac=1,
            ar=sample_rate
        ).run(
            cmd=["ffmpeg", "-nostdin"],
            capture_stdout=True,
            capture_stderr=True
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e
    youtube_vid_audio_bits = np.frombuffer(
        youtube_vid_output, dtype=np.int16
    ).flatten().astype(np.float32) / 32768.0
    end_time = time.time()
    print(f"Video download and processing time: {end_time - start_time}")
    return youtube_vid_audio_bits


def process_audio_bash(input_audio_filepath: str) -> None:
    start_time = time.time()
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            input_audio_filepath,
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            "output_1.wav"
        ]
    )
    end_time = time.time()
    print(f"Video processing time: {end_time - start_time} seconds")


def transcribe_audio_py(stt_model, audio_file_bits, output_filepath: str) -> None:
    start_time = time.time()
    transcribed_text = stt_model.transcribe(audio_file_bits)
    end_time = time.time()
    print(f"Transcription time: {end_time - start_time}")

    f = open(output_filepath, "w")
    f.write(transcribed_text)
    f.close()


def transcribe_audio_bash(audio_input_filepath: str, output_filepath: str) -> None:
    # TODO: Broken right now; fix it since it's way more efficient!
    start_time = time.time()
    subprocess.run(["ls", "-l"])
    subprocess.run(
        [
            "./whisper.cpp/main",
            "-m",
            "./whisper.cpp/models/ggml-small.en.bin",
            "-f",
            audio_input_filepath,
            "--output-srt",
            "--output-file",
            output_filepath,
        ]
    )
    end_time = time.time()
    print(f"Transcription time: {end_time - start_time} seconds")


def main():
    # ~3.5 seconds
    download_audio_bash("https://www.youtube.com/watch?v=l-wUKu_V2Lk&ab_channel=WIRED")
    # ~4 seconds
    process_audio_bash(
        "How Animators Created the Spider-Verse ｜ WIRED [l-wUKu_V2Lk].wav",
    )
    # ~115 seconds
    transcribe_audio_bash("output_1.wav", "output_1")

    # whisper_model = load_stt_model("whisper.cpp/models/ggml-small.en.bin")
    # audio_bits = process_audio_py(
    #     "sample_audios/How Animators Created the Spider-Verse ｜ WIRED [l-wUKu_V2Lk].wav",
    #     "output.wav"
    # )
    # transcribe_audio_py(whisper_model, audio_bits, "How_Animators_Created_the_Spiderverse.txt")

if __name__ == "__main__":
    main()
