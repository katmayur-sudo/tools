"""Cut each short's soundtrack from the main mix and add a follow-card tail.

Usage: python3 shorts_audio.py <shorts.json> <audio_dir> <out_dir>
The tail is the music bed (no voice) plus a click and a bell, then the whole short is
loudness-normalised to -14 LUFS.
"""
import json
import subprocess
import sys


def click_bell(path):
    from make_audio import SR, bell, click, write_wav
    import numpy as np
    x = np.zeros(int(1.6 * SR))
    c, b = click(), bell()
    x[:len(c)] += c
    x[int(0.15 * SR):int(0.15 * SR) + len(b)] += b
    write_wav(path, x)


def main():
    conf_path, audio, out = sys.argv[1:4]
    conf = json.load(open(conf_path))
    tail = conf["tail_seconds"]
    click_bell(f"{audio}/clickbell.wav")
    for sh in conf["shorts"]:
        a, b = sh["a"], sh["b"]
        click = 1100  # the follow button is clicked 1.1 s into the tail
        graph = (f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={b - a - 0.25}:d=0.25[main];"
                 f"[1:a]atrim={b}:{b + tail},asetpts=PTS-STARTPTS,volume=0.35,afade=t=in:d=0.2,afade=t=out:st={tail - 0.6}:d=0.6[bed];"
                 f"[2:a]adelay={click}|{click},volume=0.5[clk];"
                 f"[bed][clk]amix=inputs=2:normalize=0:duration=first,atrim=0:{tail}[tail];"
                 f"[main][tail]concat=n=2:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=9[out]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{audio}/mix.wav", "-i", f"{audio}/music.wav",
                        "-i", f"{audio}/clickbell.wav", "-filter_complex", graph,
                        "-map", "[out]", "-ar", "48000", f"{out}/{sh['id']}_audio.wav"], check=True)
        print("audio", sh["id"], round(b - a + tail, 2), "s")


if __name__ == "__main__":
    main()
