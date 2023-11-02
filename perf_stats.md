# Collection of Perf Stats of Whisper.cpp Inference

*NOTE: whisper.cpp is meant for leveraging the Apple ARM-based chips to its maximum capabilities to run inference as fast as possible. whisper.cpp doesn't make a lot of sense if you have a GPU, but if you have a normal CPU or especially Apple Silicon (CPU + GPU + Neural Engine + AMX), that is the best use case for whisper.cpp. Reference: https://news.ycombinator.com/item?id=33877893*

## whisper.cpp CoreML model on links.txt (12 links, ~11 hours of audio)

Machine Specs: Apple M1 Pro, 16 GB RAM, 512 GB disk, 14-core GPU, Metal 3

whisper_print_timings:     load time =   203.15 ms
whisper_print_timings:     fallbacks =   0 p /   0 h
whisper_print_timings:      mel time =  1250.73 ms
whisper_print_timings:   sample time =  1366.33 ms /  2889 runs (    0.47 ms per run)
whisper_print_timings:   encode time =  4060.25 ms /    26 runs (  156.16 ms per run)
whisper_print_timings:   decode time = 17333.79 ms /  2864 runs (    6.05 ms per run)
whisper_print_timings:   prompt time =  1029.96 ms /    25 runs (   41.20 ms per run)
whisper_print_timings:    total time = 25748.65 ms
ggml_metal_free: deallocating
./transcribe_audio.sh links.txt  296.46s user 31.87s system 23% cpu 23:31.42 total

The Apple M1 ARM silicon chip is so freaking good. Amazing that ML model inference can be run on consumer-grade devices.

*NOTE: The normal whisper.cpp model would hang the entire laptop and take an indefinite amount of time to process this much audio. On a smaller sample size of 4 links and ~1.5 hours of audio, it would take ~6 mins.*
