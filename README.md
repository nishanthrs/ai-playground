# openai-playground

### Authentication:
Set via env vars in python3 venv:
```
export OPENAI_API_KEY="<openapi_secret_key>"
```

### Install Dependencies:
```bash
source env/bin/activate  # Activate virtual env
pip3 install <dependency_name>
deactivate
```

### Run Script:
```bash
source env/bin/activate  # Activate virtual env
python3 open_ai_embeddings_gen.py
```

### Using yt-dlp Audio on Mac M1:
```bash
yt-dlp --ffmpeg-location ffmpeg  --extract-audio --audio-format wav --audio-quality 0 "<youtube_url>" ffmpeg -i <input_name>.wav -ar 16000 -ac 1 -c:a pcm_s16le <output_name>.wav
```
[Docs](https://github.com/yt-dlp/yt-dlp#usage-and-options)
NOTE: Alias ffmpeg path so you don't have to type out the entire path:
`alias ffmpeg='/Users/nishanthrs/ffmpeg'` in `.bash_profile`

### Using whisper.cpp on Mac M1:
```bash
bash ./models/download-ggml-model.sh <model_name>
make
./main -m models/ggml-<model_name>.bin -f ../sample_audios/output.wav
```

[List of Whisper Models in GGML Format](https://huggingface.co/ggerganov/whisper.cpp)
