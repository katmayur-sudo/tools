"""Epidemic Sound via its MCP server (streamable HTTP JSON-RPC). The key is read from EPIDEMIC_SOUND_API_KEY
or a .env file in the working directory, and is never printed.
usage: epidemic.py search "<term>" [bpm_min bpm_max]     music without vocals, >= 80s
       epidemic.py sfx "<term>" [max_ms]
       epidemic.py music <id> out.wav | epidemic.py sfxget <id> out.wav
       epidemic.py tools                                  list MCP tools"""
import json, os, pathlib, re, sys, urllib.error, urllib.request

URL = "https://www.epidemicsound.com/a/mcp-service/mcp"


def key():
    k = os.environ.get("EPIDEMIC_SOUND_API_KEY")
    env = pathlib.Path(".env")
    if not k and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("EPIDEMIC_SOUND_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k: sys.exit("Set EPIDEMIC_SOUND_API_KEY (environment or .env) to your Epidemic MCP key.")
    return k


KEY = key()


def post(msg, sid=None):
    h = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if sid: h["Mcp-Session-Id"] = sid
    try:
        with urllib.request.urlopen(urllib.request.Request(URL, data=json.dumps(msg).encode(), headers=h), timeout=120) as r:
            body = r.read().decode(); sid = r.headers.get("Mcp-Session-Id") or sid
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
    if body.lstrip().startswith("{"): return json.loads(body), sid
    out = None
    for line in body.splitlines():
        if line.startswith("data:"):
            try: out = json.loads(line[5:].strip())
            except Exception: pass
    return out, sid


_, SID = post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                                                                            "clientInfo": {"name": "short-reel-editor", "version": "1.0"}}})
post({"jsonrpc": "2.0", "method": "notifications/initialized"}, SID)


def call(tool, args):
    r, _ = post({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": tool, "arguments": args}}, SID)
    r = r.get("result", r)
    return json.loads(r["content"][0]["text"]) if "content" in r else r


def nodes(o):
    if isinstance(o, dict):
        if "nodes" in o: return o["nodes"]
        for v in o.values():
            x = nodes(v)
            if x is not None: return x


cmd = sys.argv[1]
if cmd == "tools":
    r, _ = post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, SID)
    for t in r["result"]["tools"]: print("##", t["name"], "-", (t.get("description") or "")[:140].replace("\n", " "))
elif cmd == "search":
    f = {"vocals": False, "duration": {"min": 80000}}
    if len(sys.argv) > 4: f["bpm"] = {"min": int(sys.argv[3]), "max": int(sys.argv[4])}
    for n in nodes(call("SearchRecordings", {"query": {"term": sys.argv[2]}, "filter": f, "first": 12})) or []:
        r = n["recording"]
        print(r["id"], "|", r["title"], "|", r["bpm"], "bpm |", r["audioFile"]["durationInMilliseconds"] // 1000, "s |",
              ", ".join(t["displayName"] for t in r["tags"][:6]), "|", r["audioFile"]["lqmp3Url"])
elif cmd == "sfx":
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
    for n in nodes(call("SearchSoundEffects", {"query": {"term": sys.argv[2]}, "filter": {"duration": {"max": mx}}, "first": 6})) or []:
        s = n.get("soundEffect", n)
        print(s.get("id"), "|", s.get("title"), "|", s.get("audioFile", {}).get("durationInMilliseconds"), "ms")
elif cmd in ("music", "sfxget"):
    tool = "DownloadRecording" if cmd == "music" else "DownloadSoundEffect"
    opts = {"fileType": "WAV", "stemType": "FULL"} if cmd == "music" else {"fileType": "WAV"}
    m = re.search(r'https://[^"\s]+', json.dumps(call(tool, {"id": sys.argv[2], "options": opts})))
    if not m: sys.exit("no download url returned")
    urllib.request.urlretrieve(m.group(0).rstrip('\\'), sys.argv[3]); print("saved", sys.argv[3])
