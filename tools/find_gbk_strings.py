"""
Skanuje plik binarny firmware w poszukiwaniu ciagow bajtow, ktore sa poprawnym
kodowaniem GBK i faktycznie dekoduja sie na chinskie znaki (CJK).
Uzycie: python find_gbk_strings.py <plik.bin> <plik_wyjsciowy.txt>
"""
import sys

def is_gbk_lead(b):
    return 0x81 <= b <= 0xFE

def is_gbk_trail(b):
    return 0x40 <= b <= 0xFE and b != 0x7F

def scan_gbk(data, min_chars=2):
    results = []
    i = 0
    n = len(data)
    while i < n - 1:
        if is_gbk_lead(data[i]) and is_gbk_trail(data[i+1]):
            start = i
            chars = bytearray()
            while i < n - 1 and is_gbk_lead(data[i]) and is_gbk_trail(data[i+1]):
                chars += data[i:i+2]
                i += 2
            if len(chars)//2 >= min_chars:
                try:
                    text = chars.decode('gbk')
                    if any('一' <= c <= '鿿' for c in text):
                        results.append((start, text))
                except Exception:
                    pass
        else:
            i += 1
    return results

def main():
    path = sys.argv[1]
    out_path = sys.argv[2]
    with open(path, 'rb') as f:
        data = f.read()
    results = scan_gbk(data)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Znaleziono {len(results)} fragmentow GBK\n\n")
        for off, text in results:
            f.write(f"0x{off:06x} ({len(text)} znakow): {text}\n")
    print(f"Znaleziono {len(results)}, zapisano do {out_path}")

if __name__ == '__main__':
    main()
