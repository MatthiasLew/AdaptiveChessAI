# Architektura

GUI PySide6 korzysta z logiki python-chess przez `HumanVsBotSession` i `MatchRunner`.

Nowy przebieg: `MainWindow → CampaignScreen → Campaign → HumanVsBotSession → BaseBot`. `CampaignWorker` wykonuje ruch i zapis w wątku roboczym; widgety aktualizuje wyłącznie wątek GUI. Każdy ruch trafia przez callback sesji do SQLite.

Jeden plik SQLite reprezentuje kampanię. Wersjonowany dokument JSON jest zapisywany transakcyjnie z kontrolą numeru rewizji. Ta pierwsza implementacja przechowuje cały dokument; przy większych badaniach warto rozdzielić ruchy i partie na tabele. Dwa procesy nie mogą po cichu nadpisać sobie zmian.

Stan aktywnej gry zawiera profil sprzed partii i ruchy UCI. Wznowienie odtwarza historię bez wyboru nowych ruchów, a dopiero potem ewentualną zaległą odpowiedź bota. Zapobiega to podwójnemu naliczaniu uczenia. Finalizacja partii i checkpoint są jedną transakcją.

`campaign_tournament` tworzy stały harmonogram par i kolorów. GUI uruchamia skrypt w QProcess. Każda partia wczytuje osobne boty z checkpointów, adaptive ma `training=False`; profile są porównywane przed i po meczu. Wyniki zatwierdza się po całej partii. Zatrzymana partia jest rozgrywana ponownie przy wznowieniu. Zmiana kodu aplikacji lub wersji środowiska blokuje wznowienie turnieju, aby nie mieszać wyników.

Starsze `GameScreen`, `ExperimentsScreen` i skrypty serii pozostają kompatybilne i nie modyfikują kampanii. Bazy SQLite są lokalne i ignorowane przez Git.
