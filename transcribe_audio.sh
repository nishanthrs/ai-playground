# Setup whisper.cpp model path
# TODO: Add whisper setup cmds in some other setup script
# bash ./whisper.cpp/models/download-ggml-model.sh $1
# make ./whisper.cpp
whisper_cpp_model_path="./whisper.cpp/models/ggml-small.en.bin"
whisper_cpp_exec_path="./whisper.cpp/main"
# Setup directories for diff audio formats
raw_audios_dir_name="raw_audios"
processed_audios_dir_name="processed_audios"
transcriptions_dir_name="transcriptions"
mkdir -p $raw_audios_dir_name
mkdir -p $processed_audios_dir_name
mkdir -p $transcriptions_dir_name
# Download YT audio data from links.txt as .wav files (by line in parallel)
parallel -j+0 --progress -a links.txt yt-dlp --ffmpeg-location /opt/local/bin/ffmpeg --extract-audio --audio-format wav --audio-quality 0 --restrict-filenames
mv *.wav $raw_audios_dir_name/
# Convert audio files to 16 khz (whisper.cpp only works on 16-bit wav files)
parallel -j+0 ffmpeg -i "$raw_audios_dir_name/{}" -ar 16000 -ac 1 -c:a pcm_s16le "$processed_audios_dir_name/{.}.wav" ::: $(ls $raw_audios_dir_name)
# Remove raw audio files
rm -rf $raw_audios_dir_name
# Transcribe audio via whisper.cpp model
parallel -j+0 $whisper_cpp_exec_path -m $whisper_cpp_model_path -f "$processed_audios_dir_name/{}" --output-srt --output-file "$transcriptions_dir_name/{.}" ::: $(ls $processed_audios_dir_name)
