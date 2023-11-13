yt-dlp --skip-download --flat-playlist --print "%(title)s ||| %(id)s" $1 | grep -E $2 | awk -F ' \\|\\|\\| ' '{print $2}' > $3
