# openai-playground

## Possible Projects

### LectureStream
1. Async cron job or ETL pipeline that periodically takes new links from links.txt and produces video transcriptions from them
  * Input: links.txt
  * Output: SRT files with transcription data of all videos in links.txt
  * yt-dlp to download video audio and convert to right format
  * whisper.cpp to transcribe videos with timestamps and spoken words
  * Can all be done in a bash script with GNU parallel
2. Async cron job or ETL pipeline that takes in transcription data and uploads to search DB
  * Input: SRT files with transcription data
  * Output: transcription data in search DB
  * (v1) Upload to [typesense DB](https://typesense.org/docs/guide/tips-for-searching-common-types-of-data.html#long-pieces-of-text) for raw search
  * (v2) Convert to embeddings and upload to vector DB or SQLite
    * Look at [Simon Willison's blog post](https://simonwillison.net/2023/Oct/23/embeddings/) for implementation ideas
3. Web service that provides fast search of all this data
  * Input: query term
  * Output: list of videos and timestamps where query term was mentioned
  * [Axum web service](https://docs.rs/axum/latest/axum/) and [incorporating multithreading](https://github.com/tokio-rs/tokio/discussions/4839)
  * (v1) Query typesense DB and output list of timestamps in each video that links to specific part of embedded video
  * (v2) Query vector DB and give list of similar videos
  * (v3) Look at [RAG (retrieval augmented generation)](https://github.com/pchunduri6/rag-demystified) to incorporate Q&A interface for educational content

### Other Datasets to Play With:
* Podcasts
* Personal notes
* Personal Github repo
* Pirated movies/TV shows
* Anime/manga
* Work: Workplace posts and videos
* Finance news (Nikkei), podcasts, articles (CNBC, WSJ), docs (10K, 10Q, earnings calls, etc.)
* SLA/SLO/SLIs metrics bot for developers to monitor service
* Gov docs on laws, transportation, urban planning, etc.

## Dependencies and Setup Instructions

### Setup VEnv and Install Dependencies:
```bash
python3.10 -m venv <env_name>
source env/bin/activate  # Activate virtual env
python3 -m pip install <dependency_name>
python3 -m pip freeze > requirements.txt  # Get curr list of deps in python venv and output to requirements.txt file
deactivate
```

Dependencies:
```bash
ffmpeg-python
whispercpp
numpy
openai
yt-dlp
faster-whisper
```
NOTE: [`whispercpp` Python bindings lib](https://github.com/aarnphm/whispercpp)
Use `pip install git+https://github.com/aarnphm/whispercpp.git -vv` to install the latest version.

### Run Script:
```bash
source env/bin/activate  # Activate virtual env
OMP_NUM_THREADS=4 python3 transcribe_audio.py  # Set # threads via env var: https://github.com/guillaumekln/faster-whisper#comparing-performance-against-other-implementations
```

### Using yt-dlp Audio on Mac M1:
```bash
# Download Youtube video with highest quality as .wav file
yt-dlp --ffmpeg-location /opt/local/bin/ffmpeg  --extract-audio --audio-format wav --audio-quality 0 "<youtube_url>"
# Download from multiple links in parallel (install GNU parallel)
parallel --jobs 4 yt-dlp --ffmpeg-location /opt/local/bin/ffmpeg  --extract-audio --audio-format wav --audio-quality 0 ::: "<youtube_url_1>" "<youtube_url_2>" ... "<youtube_url_n>"
parallel -j+0 --progress -a links.txt yt-dlp --ffmpeg-location /opt/local/bin/ffmpeg --extract-audio --audio-format wav --audio-quality 0
# -a <file> will execute the following commmand with each line as input in parallel
# -j+0 will run with # jobs = # CPU cores + 0
# Multiple ::: will generate all combinations of input (via nested loop)
# Pipe input: find example.* -print | parallel echo File
# Perf diff on 12 videos in links.txt:
# W/o parallel: 66.29s user 3.78s system 62% cpu 1:51.28 total
# W/ parallel: 72.51s user 9.54s system 277% cpu 29.608 total"""

# Convert to 16 khz (whisper.cpp only works on 16-bit wav files)
ffmpeg -i <input_name>.wav -ar 16000 -ac 1 -c:a pcm_s16le <output_name>.wav
```
[yt-dlp Docs](https://github.com/yt-dlp/yt-dlp#usage-and-options)
[GNU Parallel Docs](https://www.gnu.org/software/parallel/parallel_tutorial.html)

NOTE: Add ffmpeg to path:
```
sudo cp ./ffmpeg /usr/local/bin
sudo chmod ugo+x /usr/local/bin/ffmpeg
export PATH="/usr/local/bin:$PATH"
# Restart terminal
which ffmpeg
```

### Using whisper.cpp on Mac M1:
```bash
bash ./models/download-ggml-model.sh <model_name>
make
./main -m models/ggml-<model_name>.bin -f ../sample_audios/output.wav
```

[List of Whisper Models in GGML Format](https://huggingface.co/ggerganov/whisper.cpp)

### Typesense
* Followed [installation docs](https://typesense.org/docs/guide/install-typesense.html#mac-via-homebrew)
* Start typesense server:
```
export TYPESENSE_API_KEY=xyz
./typesense-server --data-dir=$(pwd)/typesense-data --api-key=$TYPESENSE_API_KEY --enable-cors
```
* Install Python client: `pip3 install typesense`
* Future resources to look into:
  * [Search Analytics](https://typesense.org/docs/guide/search-analytics.html#search-analytics)
  * [Updating Typesense Index](https://typesense.org/docs/guide/syncing-data-into-typesense.html#sync-changes-in-bulk-periodically)

### Benchmarking Tools
* [rewrk](https://github.com/lnx-search/rewrk)
* [k6.js](https://k6.io/blog/learning-js-through-load-testing/)

### Performance
* Video download and processing time: ~0.8 - 1 sec
* Transcription of 13:28 video:
    * Python API (num_procs=4): 1286.38 seconds (over 20 mins!)
    * Python API (num_procs=1): 942.03 seconds
    * Bash command: 56.07 seconds
* Why tf is the python API for whisper.cpp so much slower than the raw bash command??
