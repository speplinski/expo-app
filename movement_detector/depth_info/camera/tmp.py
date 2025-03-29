import socket
import re

import numpy as np
import time

nH = 22
nV = 14

OAK_IP1 = "192.168.70.64"
OAK_IP2 = "192.168.70.62"
OAK_IP3 = "192.168.70.65"

# Podział na 9 segmentów (3 kolumny dla każdego IP)
SEGMENTS_H = 3  # Liczba segmentów w poziomie dla każdego IP

# Wartości progów filtrowania dla każdego źródła
MIN_THRESHOLD1 = 1.7 # IP1
MAX_THRESHOLD1 = 3.2

MIN_THRESHOLD2 = 1.7 # IP2
MAX_THRESHOLD2 = 2.8

MIN_THRESHOLD3 = 1.7 # IP3
MAX_THRESHOLD3 = 2.8

def check_segments_presence(heatmap1, heatmap2, heatmap3, mask1, mask2, mask3):
    result = [0] * 9

    segment_width = nH // SEGMENTS_H

    for ip_idx, mask in enumerate([mask1, mask2, mask3]):
        for seg_idx in range(SEGMENTS_H):

            start_col = seg_idx * segment_width
            end_col = start_col + segment_width if seg_idx < SEGMENTS_H-1 else nH

            segment_mask = mask[:, start_col:end_col]

            result_idx = ip_idx * SEGMENTS_H + seg_idx

            if np.any(segment_mask):
                result[result_idx] = 1

    return result

def create_heatmap(distances1, distances2, distances3, nH, nV):
    heatmap1 = np.array(distances1).reshape(nV, nH)
    heatmap2 = np.array(distances2).reshape(nV, nH)
    heatmap3 = np.array(distances3).reshape(nV, nH)

    mask1 = (heatmap1 >= MIN_THRESHOLD1) & (heatmap1 <= MAX_THRESHOLD1)
    mask2 = (heatmap2 >= MIN_THRESHOLD2) & (heatmap2 <= MAX_THRESHOLD2)
    mask3 = (heatmap3 >= MIN_THRESHOLD3) & (heatmap3 <= MAX_THRESHOLD3)

    presence = check_segments_presence(heatmap1, heatmap2, heatmap3, mask1, mask2, mask3)

    return presence

def read_frame(OAK_IP):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((OAK_IP, 65432))

        HLEN = 32

        chunks = []
        bytes_recd = 0
        while bytes_recd < HLEN:
            chunk = sock.recv(min(HLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        header = str(b''.join(chunks), encoding="ascii")

        header_s = re.split(' +', header)
        if header_s[0] == "HEAD":
            MESLEN = int(header_s[1])

            chunks = []
            bytes_recd = 0
            while bytes_recd < MESLEN:
                chunk = sock.recv(min(MESLEN - bytes_recd, 2048))
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            msg = str(b''.join(chunks), encoding="ascii")

            distances = []
            dets = msg.split("|")
            for det in dets:
                distances.append(float(det))

    return distances

while True:
    try:
        distances1 = read_frame(OAK_IP1)
        distances2 = read_frame(OAK_IP2)
        distances3 = read_frame(OAK_IP3)

        distances = distances1 + distances2 + distances3

        presence = create_heatmap(distances1, distances2, distances3, nH, nV)


    except Exception as e:
        print(f"Błąd: {e}")
        time.sleep(1)
