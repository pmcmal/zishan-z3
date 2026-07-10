"""
Odtwarza sekwencje napisow (ASCII + GBK, zakonczonych bajtem 0x00) w podanym
zakresie pliku firmware. Przydatne do "czytania" tabeli tekstow menu.
Uzycie: python dump_string_table.py <plik.bin> <start_hex> <end_hex> <plik_wyjsciowy.txt>
Przyklad: python dump_string_table.py z3app.bin b6000 b9dfb wynik.txt
"""
import sys

def try_decode_cstring(data, i):
    """Probuje zdekodowac napis zakonczony 0x00 od pozycji i (ASCII lub GBK).
    Zwraca (tekst, dlugosc_w_bajtach_wraz_z_terminatorem) albo None."""
    j = i
    n = len(data)
    raw = bytearray()
    while j < n:
        b = data[j]
        if b == 0x00:
            break
        if 0x20 <= b <= 0x7e:
            raw.append(b)
            j += 1
        elif 0x81 <= b <= 0xFE and j+1 < n and 0x40 <= data[j+1] <= 0xFE and data[j+1] != 0x7F:
            raw.append(b)
            raw.append(data[j+1])
            j += 2
        else:
            return None
    if j >= n or j == i:
        return None
    try:
        text = raw.decode('gbk')
    except Exception:
        return None
    return (text, j - i + 1)

def main():
    path = sys.argv[1]
    start = int(sys.argv[2], 16)
    end = int(sys.argv[3], 16)
    out_path = sys.argv[4]
    with open(path, 'rb') as f:
        data = f.read()

    with open(out_path, 'w', encoding='utf-8') as out:
        i = start
        while i < end:
            b = data[i]
            if b == 0x00:
                i += 1
                continue
            result = try_decode_cstring(data, i)
            if result:
                text, blen = result
                out.write(f"0x{i:06x} (len={blen-1}): {text!r}\n")
                i += blen
            else:
                out.write(f"0x{i:06x}: <bajt niebedacy tekstem 0x{b:02x}>\n")
                i += 1

if __name__ == '__main__':
    main()
