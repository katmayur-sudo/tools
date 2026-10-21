"""Devanagari -> Latin romanization, so Hindi/Hinglish words can be force-aligned (MMS_FA only knows a-z)
and shown as Roman-Hinglish captions.
  roman("नहीं है")            -> "naheen hai"   (alignment form: one letter per sound, plain a-z)
  roman("नहीं है", True)      -> "nahin hai"    (readable Hinglish caption form)
Latin text passes through unchanged, so mixed Hinglish tokens ("protein वाला") work too.
usage: translit.py "<text>" [--readable]"""
import re, sys

CONS = {"क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n", "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "n",
        "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n", "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
        "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m", "य": "y", "र": "r", "ल": "l", "ळ": "l", "व": "v",
        "श": "sh", "ष": "sh", "स": "s", "ह": "h",
        "क़": "q", "ख़": "kh", "ग़": "gh", "ज़": "z", "ड़": "r", "ढ़": "rh", "फ़": "f", "य़": "y", "ऩ": "n", "ऱ": "r"}
NUKTA = {"क": "क़", "ख": "ख़", "ग": "ग़", "ज": "ज़", "ड": "ड़", "ढ": "ढ़", "फ": "फ़", "य": "य़", "न": "ऩ", "र": "ऱ"}
VOW = {"अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo", "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o",
       "औ": "au", "ऑ": "o", "ऍ": "e", "ऎ": "e", "ऒ": "o"}
MATRA = {"ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo", "ृ": "ri", "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
         "ॉ": "o", "ॅ": "e", "ॆ": "e", "ॊ": "o"}
VIRAMA, NUK, ANUS, CANDRA, VISARGA = "्", "़", "ं", "ँ", "ः"
DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
# how people actually type common words in Hinglish (readable mode); everything else goes through the rules below
COMMON = {"हम": "hum", "तुम": "tum", "मैं": "main", "हूँ": "hoon", "हूं": "hoon", "है": "hai", "हैं": "hain", "नहीं": "nahi",
          "में": "mein", "मे": "mein", "क्या": "kya", "कि": "ki", "और": "aur", "यह": "yeh", "ये": "ye", "वह": "woh", "वो": "wo",
          "कुछ": "kuch", "सब": "sab", "अब": "ab", "लेकिन": "lekin", "अच्छा": "accha", "बहुत": "bahut", "ज़रूरी": "zaroori",
          "जरूरी": "zaroori", "ज़्यादा": "zyada", "ज्यादा": "zyada", "कम": "kam", "तो": "toh", "भी": "bhi", "ही": "hi",
          "आप": "aap", "आपको": "aapko", "आपका": "aapka", "आपकी": "aapki", "आपके": "aapke", "हमें": "humein", "मुझे": "mujhe",
          "क्यों": "kyun", "कैसे": "kaise", "कहाँ": "kahan", "यहाँ": "yahan", "वहाँ": "wahan", "दोस्तों": "doston", "वाला": "wala",
          "वाली": "wali", "वाले": "wale", "बात": "baat", "दिन": "din", "रोज़": "roz", "रोज": "roz"}
DEVA = re.compile(r"[ऀ-ॿ]")


def _word(w, readable=False):
    if readable and w in COMMON: return COMMON[w]
    # syllables: [consonant or None, vowel or "a" (inherent) or "" (virama), nasal/visarga]
    syl, i = [], 0
    while i < len(w):
        c = w[i]
        if i + 1 < len(w) and w[i + 1] == NUK and c in NUKTA:
            c = NUKTA[c]; i += 1
        if c in CONS:
            v = "a"
            if i + 1 < len(w) and w[i + 1] in MATRA: v = MATRA[w[i + 1]]; i += 1
            elif i + 1 < len(w) and w[i + 1] == VIRAMA: v = ""; i += 1
            syl.append([CONS[c], v, ""])
        elif c in VOW:
            syl.append([None, VOW[c], ""])
        elif c in (ANUS, CANDRA, VISARGA) and syl:
            syl[-1][2] += "h" if c == VISARGA else "n"
        elif c == NUK:
            pass
        else:
            syl.append([None, c, ""])                    # digits, latin, punctuation
        i += 1
    # schwa deletion: drop the inherent "a" word-finally, and medially in V C(a) C V (Hindi pronunciation)
    n = len(syl)
    if n > 1 and syl[-1][0] and syl[-1][1] == "a" and not syl[-1][2]:
        syl[-1][1] = ""
    for k in range(n - 2, 0, -1):                       # right to left: samajhna, not samjhana
        cur, prv, nxt = syl[k], syl[k - 1], syl[k + 1]
        if cur[0] and cur[1] == "a" and not cur[2] and prv[1] and nxt[0] and nxt[1]:
            cur[1] = ""
    out = ""
    for k, (c, v, x) in enumerate(syl):
        if x == "n" and k + 1 < n and syl[k + 1][0] in ("p", "ph", "b", "bh", "m"): x = "m"
        if readable and x == "n" and k == n - 1 and v in ("ee", "e"): v = {"ee": "i", "e": "ei"}[v]   # nahin, mein
        out += (c or "") + v + x
    if readable:
        out = out.replace("chchh", "cch").replace("aaoo", "au").replace("aaaa", "aa")
        out = re.sub(r"(aa|ee|oo)$", lambda m: {"aa": "a", "ee": "i", "oo": "u"}[m.group(1)], out)   # kitna, bhi, tu
    return out


def roman(text, readable=False):
    text = text.translate(DIGITS).replace("।", ".").replace("॥", ".")
    if not DEVA.search(text): return text
    parts = re.split(r"([ऀ-ॿ]+)", text)
    return "".join(_word(p, readable) if DEVA.match(p) else p for p in parts)


if __name__ == "__main__":
    print(roman(sys.argv[1], "--readable" in sys.argv))
