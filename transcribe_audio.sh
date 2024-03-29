# Setup whisper.cpp model path
# TODO: Add whisper setup cmds in some other setup script
# git clone git@github.com:ggerganov/whisper.cpp.git
# bash ./whisper.cpp/models/download-ggml-model.sh small.en
# make ./whisper.cpp
# CoreML support:
# 1. Create venv with Python3.10
# 2. Install dependencies (with the right versions!): 3 pip pkgs and Xcode
# 3. ./whisper.cpp/./models/generate-coreml-model.sh small.en
# 4. make clean && WHISPER_COREML=1 make -j
whisper_cpp_model_path="./whisper.cpp/models/ggml-small.en.bin"
whisper_cpp_exec_path="./whisper.cpp/main"
# Setup directories for diff audio formats
raw_audios_dir_name="raw_audios"
processed_audios_dir_name="processed_audios"
transcriptions_dir_name="transcriptions"
video_metadata_dir_name="metadata"
mkdir -p $raw_audios_dir_name
mkdir -p $processed_audios_dir_name
mkdir -p $transcriptions_dir_name
mkdir -p $video_metadata_dir_name

# Due to machine memory and disk constraints (Mac M1; 16 GB RAM; 512 GB SSD), parallel runs out of memory when running through a file of 20+ lecture playlists
# Instead, we'll chunk the links input into separate files and go through each chunk sequentially
# Might toy around with parallel --compress in the future, but that's too much work right now; this solution should work fine
for file in "$1"/*; do
    # Download YT audio data from links text file as .wav files (by line in parallel)
    parallel -q -j+0 --progress -a $file yt-dlp --ffmpeg-location /opt/local/bin/ffmpeg --extract-audio --audio-format wav --audio-quality 0 --restrict-filenames  --write-info-json
    mv *.wav $raw_audios_dir_name/
    mv *.info.json $video_metadata_dir_name/
    # Convert audio files to 16 khz (whisper.cpp only works on 16-bit wav files)
    parallel -j+0 ffmpeg -i "$raw_audios_dir_name/{}" -ar 16000 -ac 1 -c:a pcm_s16le "$processed_audios_dir_name/{.}.wav" ::: $(ls $raw_audios_dir_name)
    # Remove raw audio files
    rm -rf $raw_audios_dir_name

    echo "Downloaded and processed audio for links in $file!"

    # Transcribe audio via whisper.cpp model
    # Using parallel with this is slower (~8 mins for links_subset.txt):
    # parallel -j+0 $whisper_cpp_exec_path -m $whisper_cpp_model_path -f "$processed_audios_dir_name/{}" --output-srt --output-file "$transcriptions_dir_name/{.}" ::: $(ls $processed_audios_dir_name)
    # Reason is that multiple processes leads to multiple threads in each process competing each other for resources. More details here:
    # https://github.com/ggerganov/whisper.cpp/issues/1408
    # Looks like memory is often the main constraint in training and inference: https://github.com/ggerganov/whisper.cpp/issues/200#issuecomment-1334103821
    # Multithreaded support is built in; passing in multiple files via -f flag runs much faster (~6-7 mins): https://github.com/ggerganov/whisper.cpp/issues/22
    # CoreML model on Mac M1 runs even faster! (~3 mins): https://github.com/ggerganov/whisper.cpp#core-ml-support
    # ls $processed_audios_dir_name | xargs -I {} basename {} .wav | xargs -I {} $whisper_cpp_exec_path -t 1 -m $whisper_cpp_model_path -f "$processed_audios_dir_name/{}.wav" --output-srt --output-file "$transcriptions_dir_name/$(basename {})"

    # echo "Transcribed audio for links in $file!"
done
