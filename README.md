#APLIKACJA DO SZUKANIA ZEGARÓW
>Aplikacja typu tinder do zegarków, wykorzystuje system api do pobierania zegarków z https://www.thewatchapi.com
>Oraz pobiera dane przez ai gemini, aby aplikacja działała płynnie oraz szukała idealnych zegarków dla klienta
---
###Konfiguracja
1. Sklonuj repozytorium:
    ```bash
    git clone https://github.com/trakerek/WatchFinder.git
    cd WatchFinder
    ```
2. Instaluje zależności z pyproject.toml:
    ```bash
    uv venv
    source .venv/bin/activate  # na Windowsie: .venv\Scripts\activate
    uv pip sync pyproject.toml
    ```
3. Tworzenie pliku .env
Trzeba Stworzyc plik 'secrets.env' w WatchFinder/src/projektpy oraz dodac klucze według wzoru:
    ```bash 
    apikey2 = "klucz do https://www.thewatchapi.com" 
    gptapi = "klucz do gemini api z https://aistudio.google.com"
    ```
4. Uruchamia testowo projekt bez tworzenia builda
    ```bash
    uv run flet run
    ```
###Budowanie Aplikacji
```bash 
uv run flet build windows -v
``` - tworzy build z plikiem binarnym do windowsa
```bash
uv run flet build apk -v
``` - tworzy build z aplikacja do zainstalowania na telefon

## Licencja

Ten projekt jest licencjonowany na warunkach licencji MIT – szczegóły znajdziesz w pliku [LICENSE](LICENSE).
