while read p; do
	youtube-dl $p --no-playlist --extract-audio --audio-format mp3 --download-archive fin.txt
done < songs.txt
