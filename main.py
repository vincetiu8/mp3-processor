import os

import pydub
from pydub import AudioSegment
import eyed3


def match_target_amplitude(audio: pydub.AudioSegment, target_db: float) -> pydub.AudioSegment:
    change_in_db = target_db - audio.dBFS
    return audio.apply_gain(change_in_db)


def detect_leading_silence(audio: pydub.AudioSegment, silence_threshold: float = -50, chunk_size: int = 10) -> int:
    trim_ms = 0

    assert chunk_size > 0  # to avoid infinite loop
    while audio[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold and trim_ms < len(audio):
        trim_ms += chunk_size

    return trim_ms


if __name__ == "__main__":
    if not os.path.isdir("output"):
        os.mkdir("output")

    for folder in sorted(os.listdir("car-songs")):
        if not os.path.isdir(f"output/{folder}"):
            os.mkdir(f"output/{folder}")

        for i, filename in enumerate(sorted(os.listdir(f"car-songs/{folder}"))):
            if os.path.isfile(f"output/{folder}/{filename}"):
                continue

            print(f"processing {filename}")
            sound = AudioSegment.from_file(f"car-songs/{folder}/{filename}", "mp3")
            normalized_sound = match_target_amplitude(sound, -15.0)
            start_trim = detect_leading_silence(normalized_sound)
            end_trim = detect_leading_silence(normalized_sound.reverse())
            final_sound = normalized_sound[start_trim:len(normalized_sound) - end_trim]
            final_sound.export(f"output/{folder}/{filename}", format="mp3")

            audio_file = eyed3.load(f"output/{folder}/{filename}")
            info = filename.strip(".mp3").split(" - ")[-2:]
            audio_file.tag.artist = info[1]
            audio_file.tag.album = folder
            audio_file.tag.album_artist = "Various Artists"
            audio_file.tag.title = info[0]
            audio_file.tag.track_num = i + 1
            audio_file.tag.save()
