"""Build a self-contained, scrubbable preview of a storyboard (no render needed).

Usage: python3 preview.py <storyboard.json> <film_dir> <out.html> [--inline] [--music music.wav]
--inline embeds every referenced asset (and the music) as data URIs, so the single HTML file works
anywhere: a browser, a Claude chat artifact, or as an email attachment. Space toggles play/pause.
"""
import base64
import json
import mimetypes
import pathlib
import sys

ENGINE = pathlib.Path(__file__).with_name("film.html")

PLAYER = """
<div id="bar" style="position:fixed;left:0;right:0;bottom:0;height:64px;background:rgba(10,10,12,.92);display:flex;align-items:center;gap:18px;padding:0 24px;z-index:99;font:600 16px Inter,sans-serif;color:#fff">
  <button id="pp" style="width:44px;height:44px;border-radius:50%;border:0;background:#fff;font-size:18px;cursor:pointer">▶</button>
  <input id="sc" type="range" min="0" max="1000" value="0" style="flex:1">
  <span id="tc" style="width:110px;text-align:right">0.0 s</span>
</div>
<script>
(() => {
  const sb = __SB__, dur = window.setFilm(sb), stage = document.getElementById("stage");
  const audio = __AUDIO__ ? new Audio(__AUDIO__) : null;
  let playing = false, t0 = 0, base = 0, t = 0;
  const fit = () => { const s = Math.min(innerWidth / 1920, (innerHeight - 64) / 1080);
    document.documentElement.style.cssText = document.body.style.cssText = `width:100vw;height:100vh;overflow:hidden;background:#0A0A0C;--accent:${sb.accent};--canvas:${sb.canvas ?? "#F4F4F4"}`;
    stage.style.cssText = `position:absolute;left:${(innerWidth - 1920 * s) / 2}px;top:${(innerHeight - 64 - 1080 * s) / 2}px;width:1920px;height:1080px;transform:scale(${s});transform-origin:0 0;overflow:hidden;background:var(--canvas)`; };
  addEventListener("resize", fit); fit();
  const draw = () => { window.renderAt(t); sc.value = String(Math.round(1000 * t / dur)); tc.textContent = t.toFixed(1) + " / " + dur.toFixed(1) + " s"; };
  const loop = now => { if (!playing) return; t = base + (now - t0) / 1000; if (t >= dur) { t = dur - 0.001; playing = false; pp.textContent = "▶"; audio && audio.pause(); } draw(); requestAnimationFrame(loop); };
  const play = () => { if (t >= dur - .01) t = 0; playing = true; base = t; t0 = performance.now(); pp.textContent = "❚❚"; if (audio) { audio.currentTime = t; audio.play(); } requestAnimationFrame(loop); };
  const pause = () => { playing = false; pp.textContent = "▶"; audio && audio.pause(); };
  pp.onclick = () => playing ? pause() : play();
  sc.oninput = () => { t = dur * sc.value / 1000; base = t; t0 = performance.now(); if (audio) audio.currentTime = t; draw(); };
  addEventListener("keydown", e => { if (e.code === "Space") { e.preventDefault(); playing ? pause() : play(); } });
  draw();
})();
</script>
"""


def data_uri(path):
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def main():
    sb_path, film_dir, out = sys.argv[1:4]
    inline = "--inline" in sys.argv
    music = sys.argv[sys.argv.index("--music") + 1] if "--music" in sys.argv else None
    sb = json.load(open(sb_path))
    film_dir = pathlib.Path(film_dir)
    if inline:
        def swap(v):
            p = film_dir / v
            return data_uri(p) if isinstance(v, str) and p.is_file() else v
        sb["logo"] = swap(sb.get("logo", ""))
        for sc in sb["scenes"]:
            for k in ("image", "plate", "peek"):
                if k in sc:
                    sc[k] = swap(sc[k])
    if music and inline and not music.endswith(".mp3"):
        # keep the single-file preview small: embed a 128 kbps MP3 instead of the WAV
        import subprocess, tempfile
        mp3 = pathlib.Path(tempfile.mkdtemp()) / "music.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", music, "-b:a", "128k", str(mp3)], check=True)
        music = str(mp3)
    audio = json.dumps(data_uri(pathlib.Path(music)) if (music and inline) else music)
    html = ENGINE.read_text()
    html = html.replace('<div id="stage"></div>', '<div id="stage"></div>' + PLAYER.replace("__SB__", json.dumps(sb)).replace("__AUDIO__", audio), 1)
    # the player script must run after the engine script defines setFilm/renderAt
    engine_end = html.rindex("</script>")
    player_start = html.index('<div id="bar"')
    player = html[player_start:html.index("</script>", player_start) + 9]
    html = html.replace(player, "", 1)
    engine_end = html.rindex("</script>") + 9
    html = html[:engine_end] + player + html[engine_end:]
    pathlib.Path(out).write_text(html)
    print(f"preview -> {out} ({pathlib.Path(out).stat().st_size // 1024} KB{', assets inlined' if inline else ''})")


if __name__ == "__main__":
    main()
