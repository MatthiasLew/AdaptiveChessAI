# Wersja desktopowa Windows

Gotowy program znajduje się po budowie w `dist/AdaptiveChessAI/AdaptiveChessAI.exe`. Przenoś cały folder **AdaptiveChessAI**, razem z `_internal`; sam EXE nie wystarcza. W tej paczce użytkownik nie instaluje Pythona. Uruchomienie bez argumentów otwiera GUI. Dane zapisuj w wybranym własnym folderze. Domyślna lokalizacja spakowanej aplikacji korzysta z katalogu danych użytkownika, a nie katalogu instalacji.

## Odtworzenie paczki

Zweryfikowane środowisko: Windows x64 i Python 3.13.15. Lock zawiera dokładne wersje zależności z lokalnej budowy.

```powershell
python -m venv venv
venv/Scripts/python.exe -m pip install -r requirements-desktop-windows.lock
venv/Scripts/python.exe scripts/build_desktop.py
venv/Scripts/python.exe scripts/smoke_desktop.py dist/AdaptiveChessAI/AdaptiveChessAI.exe
```

Builder ustawia ścieżkę importów projektu i ogranicza PATH procesu budującego do Pythona oraz Windows. Chroni to przed przypadkowym dołączaniem niezgodnych bibliotek DLL z innych narzędzi. Manifest środowiska i hash źródeł trafiają do paczki. Zbudowany program korzysta z tych samych modułów co wersja źródłowa.

Test paczki uruchamia GUI offscreen, starszy skrypt, pełny zestaw eksperymentów, pełną syntetyczną kampanię czterech metod, ocenę checkpointów i turniej oraz ponowne wznowienie. Sprawdza wyniki, niezmienność modeli, eksporty i poprawne kodowanie UTF-8 wyjścia procesów. Pracuje w katalogu tymczasowym poza repozytorium; partie testowe nie są danymi badawczymi.

Workflow `quality.yml` zawiera testy Windows/Linux oraz budowę i test paczki Windows z artefaktem do pobrania. Sam zapis workflow nie jest dowodem uruchomienia GitHub Actions; bieżące dowody lokalne są w [walidacji](WALIDACJA_2026-09-15.md). Paczka nie jest podpisanym instalatorem ani wersją zweryfikowaną na wszystkich komputerach. Linux/macOS wymagają osobnych natywnych buildów.

Podstawa pakowania: [dokumentacja PyInstaller](https://pyinstaller.org/en/stable/operating-mode.html).
