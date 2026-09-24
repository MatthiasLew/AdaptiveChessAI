# Nadpisywanie kampanii po potwierdzeniu okna zapisu

Przyczyna błędu: okno zapisu oferowało nadpisanie istniejącej ścieżki, ale
`Campaign.create()` zawsze używało wyłącznego tworzenia pliku (`xb`).

GUI używa teraz potwierdzenia nadpisania w oknie zapisu i ustawia domyślne
rozszerzenie `.sqlite3` przed potwierdzeniem. Nowa kampania jest najpierw
budowana i walidowana w tymczasowej bazie. Dla istniejącej kampanii:

1. Blokowana jest równoległa modyfikacja bazy.
2. Poprzedni stan bazy trafia do unikalnego pliku w sąsiednim folderze `backups`.
3. Nowa kampania zastępuje dokument w transakcji, z podniesieniem rewizji.

Niepoprawne ustawienia lub nieudana kopia nie zastępują poprzedniej kampanii.
Stare okno aplikacji nie może zapisać swojego stanu nad nową kampanią, ponieważ
jego rewizja jest już nieaktualna. Standardowe wywołanie backendowego `create`
bez jawnego trybu nadpisania nadal odrzuca istniejący plik.

Po powodzeniu GUI pokazuje ścieżkę do kopii zapasowej. Nie modyfikowano zapisów
użytkownika podczas wdrażania ani testowania tej poprawki.

Walidacja: 35/35 testów nadpisywania, anulowania okna zapisu, kopii, błędnych
ustawień, błędu utworzenia kopii, konfliktu starej sesji oraz regresji kampanii.
