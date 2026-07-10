"""
Bezpiecznie podmienia tekst w firmware na dokladnym zakresie bajtow (offset..offset+len),
bez przesuwania jakichkolwiek innych danych w pliku.

Zasada bezpieczenstwa: nowy tekst NIE MOZE byc dluzszy w bajtach niz oryginalny slot.
Jesli jest krotszy - dopelniany jest bajtami 0x00 do pelnej dlugosci oryginalu (reszta
slotu, ktora byla oryginalnie oceniona jako "wlasnosc" tego stringu). Bajt bezposrednio
PO slocie nigdy nie jest dotykany.

Uzycie: python patch_strings.py <plik_wejsciowy.bin> <plik_wyjsciowy.bin> [grupa ...]

Bez podania grupy - wykonywana jest tylko grupa "bezpieczna" (najnizsze ryzyko).
Podaj np. "bezpieczna eksperymentalna" aby wykonac obie.

Definicje podmian sa w liscie PATCHES nizej.
"""
import sys

PATCHES = [
    # grupa,          offset,   dlugosc, oryginal_gbk_lub_ascii, nowy tekst (ascii)
    # --- "bezpieczna": izolowany string ASCII, malo prawdopodobne ze cos zalezy od dlugosci ---
    ("bezpieczna",     0xb97ea, 7,       "English",              "Polski"),

    # --- "eksperymentalna": stale 4-bajtowe sloty z 2 znakami GBK, gesto upakowane w tabeli.
    #     WYZSZE RYZYKO: nie potwierdzone czy slot MUSI byc GBK (2 znaki), czy przyjmie
    #     dowolne bajty ASCII bez problemu. Budzet bajtowy jest bardzo mały (4 B), stad
    #     same skroty, nie pelne slowa. ---
    ("eksperymentalna", 0xb7998, 4,      "设置",                 "Ust"),   # Ustawienia
    ("eksperymentalna", 0xb79cc, 4,      "系统",                 "Syst"),  # System
    ("eksperymentalna", 0xb967c, 4,      "语言",                 "Jez"),   # Jezyk
    ("eksperymentalna", 0xb9388, 4,      "版本",                 "Wers"),  # Wersja
    ("eksperymentalna", 0xb97d6, 4,      "关于",                 "Info"),  # O programie (chinski uproszczony)
]

def encode_expected(expected):
    """Oryginalny tekst moze byc ASCII albo GBK (chinski) - kodujemy odpowiednio."""
    try:
        return expected.encode('ascii')
    except UnicodeEncodeError:
        return expected.encode('gbk')

def main():
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    active_groups = set(sys.argv[3:]) if len(sys.argv) > 3 else {"bezpieczna"}

    with open(in_path, 'rb') as f:
        data = bytearray(f.read())

    applied = 0
    for group, offset, length, expected, new_text in PATCHES:
        if group not in active_groups:
            print(f"(pominięto, grupa {group!r} nieaktywna: 0x{offset:x} {expected!r})")
            continue

        expected_bytes = encode_expected(expected)
        current = bytes(data[offset:offset+len(expected_bytes)])
        if current != expected_bytes:
            print(f"UWAGA: pod 0x{offset:x} oczekiwano {expected_bytes!r}, znaleziono {current!r} - PRZERYWAM.")
            sys.exit(1)

        new_bytes = new_text.encode('ascii')
        if len(new_bytes) > length:
            print(f"UWAGA: {new_text!r} ({len(new_bytes)} B) nie mieści się w slocie {length} B pod 0x{offset:x} - PRZERYWAM.")
            sys.exit(1)

        padded = new_bytes + b'\x00' * (length - len(new_bytes))
        data[offset:offset+length] = padded
        print(f"[{group}] 0x{offset:x}: {expected!r} -> {new_text!r} (dopełnione do {length} B)")
        applied += 1

    with open(out_path, 'wb') as f:
        f.write(data)
    print(f"\nZastosowano {applied} podmian(y). Zapisano: {out_path}")

if __name__ == '__main__':
    main()
