#!/usr/bin/env python3

import math

import numpy as np
import scipy.special as sc

from rich import print as rprint

def ent(buf):
    freqs = [0] * 256
    for b in buf:
        freqs[b] += 1
    num_bytes = len(buf)
    freqs = map(lambda cnt: cnt / num_bytes, freqs)
    ent = 0
    for freq in freqs:
        if freq == 0:
            continue
        ent += freq * math.log2(freq)
    ent *= -1
    return ent

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
    for freq in freqs:
        if freq == 0:
            continue
        ent += freq * math.log2(freq)
    ent *= -1
    return ent

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
    for freq in freqs:
        if freq == 0:
            continue
        ent += freq * math.log2(freq)
    ent *= -1
    return ent

def binary_entropy(x):
    return -(sc.xlogy(x, x) + sc.xlog1py(1 - x, -x)) / np.log(2)

def smrt_ltrl(n):
    return n

for n in (1, 4, 16, 42, 243, 256, 1000, 1024, 4000, 4096):
    print(f"n: {n} n hex: {hex(n)} smrt_ltrl: {smrt_ltrl(n)}")
    print("ent:     (dec) {:0.3f}".format(ent(str(n).encode('utf8'))))
    print("ent:     (hex) {:0.3f}".format(ent(hex(n)[2:].encode('utf8'))))
    print("ent_dec: (dec) {:0.3f}".format(ent_dec(str(n).encode('utf8'))))
    print("ent_hex: (hex) {:0.3f}".format(ent_hex(hex(n).encode('utf8'))))