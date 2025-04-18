import socket
import re

import numpy as np
import cv2
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
    
    heatmap = np.hstack((heatmap1, heatmap2, heatmap3))
    
    mask = np.hstack((mask1, mask2, mask3))
    
    min_dist = np.min(heatmap)
    max_dist = np.max(heatmap)
    normalized = ((heatmap - min_dist) / (max_dist - min_dist) * 255).astype(np.uint8)
    
    heatmap_colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
    
    filtered_heatmap = heatmap_colored.copy()
    filtered_heatmap[~mask] = [0, 0, 0]
    
    scale_factor = 30
    heatmap_scaled = cv2.resize(filtered_heatmap, 
                              (3*nH * scale_factor, nV * scale_factor), 
                              interpolation=cv2.INTER_NEAREST)
    
    segment_width = nH * scale_factor // SEGMENTS_H
    
    for oak_idx in range(3):  # 3 kolumny (IP1, IP2, IP3)
        oak_x_start = oak_idx * nH * scale_factor
        
        for h_idx in range(1, SEGMENTS_H):
            x = oak_x_start + h_idx * segment_width
            cv2.line(heatmap_scaled, (x, 0), (x, nV*scale_factor), (255, 255, 255), 1)
    
    for i in range(1, 3):
        x = i * nH * scale_factor
        cv2.line(heatmap_scaled, (x, 0), (x, nV*scale_factor), (255, 255, 255), 2)
    
    for y in range(nV):
        for x in range(3*nH):
            text_x = x * scale_factor + 5
            text_y = y * scale_factor + scale_factor//2
            distance = heatmap[y, x]
            
            text_color = (255, 255, 255)
            
            if x < nH:  # IP1
                if not mask1[y, x % nH]:
                    text_color = (128, 128, 128)
            elif x < 2*nH:  # IP2
                if not mask2[y, x % nH]:
                    text_color = (128, 128, 128)
            else:  # IP3
                if not mask3[y, x % nH]:
                    text_color = (128, 128, 128)
            
            cv2.putText(heatmap_scaled, f"{distance:.1f}", (text_x, text_y),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.3, text_color, 1)
    
    for segment_idx in range(9):
        oak_idx = segment_idx // SEGMENTS_H
        segment_in_oak = segment_idx % SEGMENTS_H
        
        segment_x = oak_idx * nH * scale_factor + segment_in_oak * segment_width + segment_width // 2
        segment_y = nV * scale_factor - 10
        
        color = (0, 255, 0) if presence[segment_idx] else (0, 0, 255)  # Zielony dla 1, Czerwony dla 0
        
        cv2.putText(heatmap_scaled, f"S{segment_idx+1}:{presence[segment_idx]}", 
                   (segment_x - 25, segment_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return heatmap_scaled, presence


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
        #print(header)

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


print("Sterowanie:")
print("  1 - wybierz IP1 do modyfikacji progów")
print("  2 - wybierz IP2 do modyfikacji progów")
print("  3 - wybierz IP3 do modyfikacji progów")
print("  z - zmniejsz maksymalny próg dla aktywnego IP o 0.1")
print("  x - zwiększ maksymalny próg dla aktywnego IP o 0.1")
print("  q - zakończ program")

# Początkowo aktywne IP1
active_ip = 1

while True:
    try:
        tt = time.time()
        
        distances1 = read_frame(OAK_IP1)
        distances2 = read_frame(OAK_IP2)
        distances3 = read_frame(OAK_IP3)
        
        distances = distances1 + distances2 + distances3
        print(f"Czas: {time.time()-tt:.3f}s")
        
        thresh_info = f"IP1: min={MIN_THRESHOLD1:.1f} max={MAX_THRESHOLD1:.1f} | "
        thresh_info += f"IP2: min={MIN_THRESHOLD2:.1f} max={MAX_THRESHOLD2:.1f} | "
        thresh_info += f"IP3: min={MIN_THRESHOLD3:.1f} max={MAX_THRESHOLD3:.1f} | "
        thresh_info += f"Aktywne IP{active_ip}"
        print(thresh_info)
        
        heatmap, presence = create_heatmap(distances1, distances2, distances3, nH, nV)
        
        presence_text = f"Obecność w segmentach: {presence}"
        print(presence_text)
        
        cv2.putText(heatmap, f"IP1: min={MIN_THRESHOLD1:.1f} max={MAX_THRESHOLD1:.1f}", 
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(heatmap, f"IP2: min={MIN_THRESHOLD2:.1f} max={MAX_THRESHOLD2:.1f}", 
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(heatmap, f"IP3: min={MIN_THRESHOLD3:.1f} max={MAX_THRESHOLD3:.1f}", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(heatmap, f"Aktywne IP{active_ip}", 
                    (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        cv2.imshow("Depth Heatmap", heatmap)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('1'):
            active_ip = 1
            print(f"Wybrano IP1 do modyfikacji progów")
        elif key == ord('2'):
            active_ip = 2
            print(f"Wybrano IP2 do modyfikacji progów")
        elif key == ord('3'):
            active_ip = 3
            print(f"Wybrano IP3 do modyfikacji progów")
        elif key == ord('z'):
            # Zmniejsz maksymalny próg o 0.1 dla aktywnego IP
            if active_ip == 1:
                MIN_THRESHOLD_VAL = MIN_THRESHOLD1
                MAX_THRESHOLD1 = max(MIN_THRESHOLD_VAL, MAX_THRESHOLD1 - 0.1)
                print(f"Zmniejszono maksymalny próg dla IP1: {MAX_THRESHOLD1:.1f}")
            elif active_ip == 2:
                MIN_THRESHOLD_VAL = MIN_THRESHOLD2
                MAX_THRESHOLD2 = max(MIN_THRESHOLD_VAL, MAX_THRESHOLD2 - 0.1)
                print(f"Zmniejszono maksymalny próg dla IP2: {MAX_THRESHOLD2:.1f}")
            elif active_ip == 3:
                MIN_THRESHOLD_VAL = MIN_THRESHOLD3
                MAX_THRESHOLD3 = max(MIN_THRESHOLD_VAL, MAX_THRESHOLD3 - 0.1)
                print(f"Zmniejszono maksymalny próg dla IP3: {MAX_THRESHOLD3:.1f}")
        elif key == ord('x'):
            # Zwiększ maksymalny próg o 0.1 dla aktywnego IP
            if active_ip == 1:
                MAX_THRESHOLD1 = MAX_THRESHOLD1 + 0.1
                print(f"Zwiększono maksymalny próg dla IP1: {MAX_THRESHOLD1:.1f}")
            elif active_ip == 2:
                MAX_THRESHOLD2 = MAX_THRESHOLD2 + 0.1
                print(f"Zwiększono maksymalny próg dla IP2: {MAX_THRESHOLD2:.1f}")
            elif active_ip == 3:
                MAX_THRESHOLD3 = MAX_THRESHOLD3 + 0.1
                print(f"Zwiększono maksymalny próg dla IP3: {MAX_THRESHOLD3:.1f}")
                
    except Exception as e:
        print(f"Błąd: {e}")
        time.sleep(1)

cv2.destroyAllWindows()
