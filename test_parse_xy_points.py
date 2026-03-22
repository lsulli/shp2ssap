import re
from typing import List

_SPLIT_RE = re.compile(r"[\s;|:=]+")
_DECIMAL_COMMA_RE = re.compile(r"(\d),(\d)")


def parse_xy_points(text: str) -> List[List[float]]:
    points: List[List[float]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Sostituisce solo le virgole decimali (es. 1,5 → 1.5), non quelle separatori
        line = _DECIMAL_COMMA_RE.sub(r"\1.\2", line)
        # Rimuove le virgole rimanenti (usate come separatori di lista)
        line = line.replace(",", " ")
        parts = [p for p in _SPLIT_RE.split(line) if p and p.strip()]

        # Estrai solo i valori numerici, scartando quelli testuali
        numeric_parts = []
        for p in parts:
            try:
                numeric_parts.append(float(p))
            except ValueError:
                continue  # scarta i valori non numerici

        if len(numeric_parts) < 2:
            continue

        # Prendi i primi due valori numerici come x, y
        points.append([numeric_parts[0], numeric_parts[1]])

    return points






# ── Test cases ────────────────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, result, expected):
        nonlocal passed, failed
        if result == expected:
            print(f"  ✅ PASS  {name}")
            passed += 1
        else:
            print(f"  ❌ FAIL  {name}")
            print(f"          expected: {expected}")
            print(f"          got:      {result}")
            failed += 1

    print("=" * 60)
    print("TEST: parse_xy_points")
    print("=" * 60)

    # 1. Riga normale con spazio
    check(
        "Riga normale (spazio)",
        parse_xy_points("1.5 3.2"),
        [[1.5, 3.2]],
    )

    # 2. Riga con virgola come decimale
    check(
        "Virgola come separatore decimale",
        parse_xy_points("1,5 3,2"),
        [[1.5, 3.2]],
    )

    # 3. Riga con etichetta testuale davanti e virgole come separatori
    check(
        "Etichetta testuale prima dei numeri, attributo testuale prima dei numeri",
        parse_xy_points("id_stringa, label:, 1.5, 3.2"),
        [[1.5, 3.2]],
    )

    # 4. Riga con testo misto
    check(
        "Testo misto (x=1.5 y=3.2) o (x like 1.5 y like 3.2)",
        parse_xy_points("x=1.5 y=3.2"),
        [[1.5, 3.2]],
    )

    # 5. Separatore punto e virgola
    check(
        "Separatore semicolon",
        parse_xy_points("2.0;4.5"),
        [[2.0, 4.5]],
    )

    # 6. Riga con solo testo → scartata
    check(
        "Solo testo → nessun punto",
        parse_xy_points("hello world"),
        [],
    )

    # 7. Riga con un solo numero → scartata
    check(
        "Un solo numero → nessun punto",
        parse_xy_points("42"),
        [],
    )

    # 8. Righe multiple miste
    check(
        "Righe multiple miste",
        parse_xy_points("A 1.0 2.0\n3.5 bad 7.1\n\n5.0 6.0"),
        [[1.0, 2.0], [3.5, 7.1], [5.0, 6.0]],
    )

    # 9. Riga vuota → ignorata
    check(
        "Righe vuote ignorate",
        parse_xy_points("\n\n1.0 2.0\n\n"),
        [[1.0, 2.0]],
    )

    # 10. Numeri negativi
    check(
        "Numeri negativi",
        parse_xy_points("-1.5 -3.2"),
        [[-1.5, -3.2]],
    )

    # 11. Carattere non numerico generico come separatore → ignorata
    check(
        "Carattere non numerico generico come separatore → nessun punto",
        parse_xy_points("1,5e3,2"),
        [],
    )

    # 12. Tab come separatore
    check(
        "Tab come separatore",
        parse_xy_points("1,5	3,2"),
        [[1.5, 3.2]],
    )

    print("=" * 60)
    print(f"Risultato: {passed} passed, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
