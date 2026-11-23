# Speech segments from the cleaned voice (level-based, same rules as tighten.py), padded into shortened gaps.
import json, subprocess, sys, numpy as np
SR, HOP = 48000, 480
FLOOR, LOUD, DIP, LEAD, TAIL = -40, -27, 6, 18, 22
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","voice_clean.wav","-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True,check=True).stdout, np.float32)
db = 20*np.log10(np.sqrt(np.convolve(x**2, np.ones(2*HOP)/(2*HOP), "same")[::HOP])+1e-9)
on = db > FLOOR; segs=[]; i=0
while i < len(on):
    if not on[i]: i+=1; continue
    j=i
    while j<len(on) and (on[j] or on[j:j+DIP+1].any()): j+=1
    segs.append((i,j)); i=j
# retakes, false starts and mic-handling noises (sound-file seconds), decided from phrases.json
EXCLUDE=[(15.3,20.85),(79.0,84.0),(90.4,91.7),(97.9,98.55)]
segs=[(a,b) for a,b in segs if not any(x*100<=a and b<=y*100 for x,y in EXCLUDE)]
cut=[]
for a,b in segs:  # trim a sound run that straddles an excluded range
    for x,y in EXCLUDE:
        if a<x*100<b: b=int(x*100)
        if a<y*100<b: a=int(y*100)
    if b-a>3: cut.append((a,b))
segs=cut
kept=[]
for a,b in segs:
    loud=np.flatnonzero(db[a:b]>LOUD)
    if len(loud): kept.append([max(a,a+loud[0]-LEAD)/100, min(b,a+loud[-1]+1+TAIL)/100])
# merge segments separated by tiny gaps, then pad each into the gap (gap target 0.14 s, 0.28 s at sentence-length pauses)
m=[kept[0]]
for a,b in kept[1:]:
    if a-m[-1][1]<0.12: m[-1][1]=b
    else: m.append([a,b])
out=[]
for k,(a,b) in enumerate(m):
    gb = a-m[k-1][1] if k else a
    ga = m[k+1][0]-b if k+1<len(m) else 0.3
    tb = (0.28 if gb>0.6 else 0.14)/2; ta=(0.28 if ga>0.6 else 0.14)/2
    a2=max(0,a-min(gb/2,tb)); b2=b+min(ga/2,ta)
    out.append([round(round(a2*30)/30,4), round(round(b2*30)/30,4)])
tot=sum(b-a for a,b in out)
json.dump(out,open("segments.json","w"))
print(len(segs),"sound segs,",len(segs)-len(kept),"breath/noise dropped,",len(out),"cuts, total",round(tot,2),"s")
