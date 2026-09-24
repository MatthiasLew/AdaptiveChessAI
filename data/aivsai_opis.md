# aivsai - Astra kontra cztery boty

Data: 23.09.2026. Wszystkie biale ruchy wybral Astra i wprowadzil klikaniem w widocznym oknie aplikacji. To demonstracja AI kontra AI, nie dane uczestnika-czlowieka. Pole human w bazie oznacza miejsce gracza w interfejsie.

Ustawienia: jedna partia na metode, biale Astra, glebokosc 1, budzet 500 wezlow, seed 42.

| Bot | Wynik bialych | Ruch konczacy (numer) | Mat |
| --- | --- | --- | --- |
| td | 1-0 | 18 | Qb7# |
| imitation | 1-0 | 18 | Qxb7# |
| static | 1-0 | 18 | Qb7# |
| adaptive | 1-0 | 17 | Qxb7# |

Zapis kampanii: aivsai.sqlite3. Partie: aivsai.pgn. Zweryfikowano legalnosc wszystkich ruchow, maty, zgodnosc wynikow i pozycji koncowych oraz integralnosc SQLite. Brak aktywnej, niedokonczonej partii.

To cztery partie treningowe/demonstracyjne; nie uruchamiano oceny zamrozonych checkpointow ani turnieju. Jedna partia na metode nie wystarcza do oceny skutecznosci uczenia.
