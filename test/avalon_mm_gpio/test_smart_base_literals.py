#!/usr/bin/env python3

import math

def _ent_dec(buf):
    """Get the entropy of a decimal byte-string [0-9]"""
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
    if ent: # avoid -0.0
        ent = -ent
    return ent, nsyms

def _ent_hex(buf):
    """Get the entropy of a decimal byte-string [0-9a-z]"""
    freqs = [0] * 16
    norm_buf = []
    if buf.startswith(b'0x'):
        buf = buf[2:]
    for b in buf:
        if ord('0') <= b <= ord('9'):
            norm_buf.append(b - ord('0'))
        elif ord('a') <= b <= ord('f'):
            norm_buf.append(b - ord('a') + 10)
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
    if ent: # avoid -0.0
        ent = -ent
    return ent, nsyms

def _is_pretty_base_hex(n):
    if n < 0:
        n = -n

    if n == 0:
        return False

    if math.log10(n) == int(math.log10(n)):
        return False
    if math.log2(n) == int(math.log2(n)) and n >= 16:
        return True

    d = str(n).encode('utf8')
    h = hex(n).encode('utf8')[2:]
    dl, hl = len(d), len(h)
    ed, nsymsd = _ent_dec(d)
    eh, nsymsh = _ent_hex(h)
    frac_unique_d = nsymsd / dl
    frac_unique_h = nsymsh / hl

    if frac_unique_d < frac_unique_h:
        return False
    elif frac_unique_h < frac_unique_d:
        return True

    if n < 1000:
        return False

    if ed < eh:
        return False
    elif eh < ed:
        return True

    return False


for n in (1, 4, 9, 10, 11, 12, 13, 14, 15, 16, 42, 99, 100, 101, 243, 256, 1000, 1024, 4000, 4096, 1223334444, 603979776):
    is_hex = _is_pretty_base_hex(n)
    base_fmt = ":x" if is_hex else ":d"
    fmt = "n: {} n hex: {} smrt_ltrl: {}{" + base_fmt + "}"
    print(fmt.format(n, hex(n), "0x" if is_hex else "", n))
