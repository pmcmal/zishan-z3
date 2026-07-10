"""
Bezpiecznie podmienia tekst w firmware na dokladnym zakresie bajtow (offset..offset+len),
bez przesuwania jakichkolwiek innych danych w pliku.

Zasada bezpieczenstwa: nowy tekst NIE MOZE byc dluzszy w bajtach niz oryginalny slot.
Jesli jest krotszy - dopelniany jest bajtami 0x00 do pelnej dlugosci oryginalu.

Uzycie: python patch_strings.py <plik_wejsciowy.bin> <plik_wyjsciowy.bin>

Definicje podmian sa w liscie PATCHES nizej - kazda to (offset_hex, oryginalna_dlugosc_bajtow,
oczekiwany_oryginalny_tekst_do_weryfikacji, nowy_tekst).
"""
import sys

PATCHES = [
    # offset,   dlugosc, oryginal (do weryfikacji), nowy tekst
    (0xb97ea,   7,       "English",                 "Polski"),
]

def main():
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    with open(in_path, 'rb') as f:
        data = bytearray(f.read())

    for offset, length, expected, new_text in PATCHES:
        current = data[offset:offset+length]
        current_text = current.split(b'\x00')[0].decode('ascii', errors='replace')
        if current_text != expected:
            print(f"UWAGA: pod 0x{offset:x} oczekiwano {expected!r}, znaleziono {current_text!r} - PRZERYWAM.")
            sys.exit(1)

        new_bytes = new_text.encode('ascii')
        if len(new_bytes) > length:
            print(f"UWAGA: {new_text!r} ({len(new_bytes)} B) nie mieści się w slocie {length} B pod 0x{offset:x} - PRZERYWAM.")
            sys.exit(1)

        padded = new_bytes + b'\x00' * (length - len(new_bytes))
        data[offset:offset+length] = padded
        print(f"0x{offset:x}: {expected!r} -> {new_text!r} (dopełnione do {length} B)")

    with open(out_path, 'wb') as f:
        f.write(data)
    print(f"\nZapisano: {out_path}")

if __name__ == '__main__':
    main()
