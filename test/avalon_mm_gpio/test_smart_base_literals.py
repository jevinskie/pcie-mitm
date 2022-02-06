#!/usr/bin/env python3

import math

def ent_dec(buf):
    freqs = [0] * 10
    norm_buf = []
    for b in buf:
        if ord('0') <= b <= ord('9'):
            norm_buf.append(b - ord('0'))
        else:
            raise ValueError(f"not a decimal digit: '{chr(b)}'")
    for b in norm_buf:
        freqs[b] += 1
    num_bytes = len(norm_buf)
    freqs = map(lambda cnt: cnt / num_bytes, freqs)
    ent = 0
    nsyms = 0
    for freq in freqs:
        if freq == 0:
            continue
        nsyms += 1
        ent += freq * math.log2(freq)
    if ent:
        ent *= -1
    return ent, nsyms

def ent_hex(buf):
    freqs = [0] * 16
    norm_buf = []
    if buf.startswith(b'0x'):
        buf = buf[2:]
    for b in buf:
        if ord('0') <= b <= ord('9'):
            norm_buf.append(b - ord('0'))
        elif ord('a') <= b <= ord('f'):
            norm_buf.append(b - ord('a') + 10)
        elif ord('A') <= b <= ord('F'):
            norm_buf.append(b - ord('A') + 10)
        else:
            raise ValueError(f"not a hex digit: '{chr(b)}'")
    for b in norm_buf:
        freqs[b] += 1
    num_bytes = len(norm_buf)
    freqs = map(lambda cnt: cnt / num_bytes, freqs)
    ent = 0
    nsyms = 0
    for freq in freqs:
        if freq == 0:
            continue
        nsyms += 1
        ent += freq * math.log2(freq)
    if ent:
        ent *= -1
    return ent, nsyms

def smrt_ltrl(n):
    d = str(n).encode('utf8')
    h = hex(n).encode('utf8')[2:]
    dl, hl = len(d), len(h)
    ed, nsymsd = ent_dec(d)
    eh, nsymsh = ent_hex(h)
    print(f"d: {d} ed: {ed:0.3f} nsymsd: {nsymsd}")
    print(f"h: {h} ed: {eh:0.3f} nsymsh: {nsymsh}")
    frac_unique_d = nsymsd / dl
    frac_unique_h = nsymsh / hl
    print(f"frac_unique: d: {frac_unique_d:0.3f} h: {frac_unique_h:0.3f}")
    nzd = d.count(b'0')
    nzh = h.count(b'0')
    print(f"nzd: {nzd} nzh: {nzh}")

    if frac_unique_d < frac_unique_h:
        return str(n)
    elif frac_unique_h < frac_unique_d:
        return hex(n)

    if ed < eh:
        return str(n)
    elif eh < ed:
        return hex(n)

    return str(n)

for n in (1, 4, 16, 42, 243, 256, 1000, 1024, 4000, 4096, 1223334444, 603979776):
    print(f"n: {n} n hex: {hex(n)} smrt_ltrl: {smrt_ltrl(n)}")
