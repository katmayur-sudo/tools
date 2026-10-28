# DeepFilterNet3 speech enhancement (removes background noise): python denoise.py in.wav out.wav (48 kHz mono)
import sys, types
import torchaudio
m = types.ModuleType("torchaudio.backend.common"); m.AudioMetaData = object   # df only imports this name
sys.modules["torchaudio.backend"] = types.ModuleType("torchaudio.backend"); sys.modules["torchaudio.backend.common"] = m
import numpy as np, soundfile as sf, torch
from df.enhance import enhance, init_df
model, state, _ = init_df()
x, sr = sf.read(sys.argv[1], dtype="float32")
assert sr == state.sr(), (sr, state.sr())
y = enhance(model, state, torch.from_numpy(x[None]))
sf.write(sys.argv[2], y.squeeze(0).numpy(), sr)
print("enhanced", len(x) / sr, "s")
