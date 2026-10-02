# =========================================================
#  KONFIGURACJA BOTA KURSÓW — tu zmieniasz wszystko
# =========================================================
#
# symbol  – symbol z Yahoo Finance
# name    – nazwa w powiadomieniu
# group   – sekcja w porannym podsumowaniu
# dec     – ile miejsc po przecinku pokazywać
# pct     – alert, gdy dzienna zmiana przekroczy X% (kolejne alerty
#           przy 2x, 3x progu, np. 0.5% -> 1.0% -> 1.5%)
# mult    – mnożnik (np. JPY pokazujemy za 100 jenów)
# above   – lista poziomów: alert, gdy kurs przebije je W GÓRĘ
# below   – lista poziomów: alert, gdy kurs spadnie PONIŻEJ
#
# Przykład własnych progów:
#   {"symbol": "EURPLN=X", ..., "above": [4.35], "below": [4.20]},

LOOKBACK = 30  # ile ostatnich sesji brać pod uwagę przy "najwyżej/najniżej od X sesji"

INSTRUMENTS = [
    # --- Waluty do złotówki ---
    {"symbol": "EURPLN=X", "name": "EUR/PLN",     "group": "Waluty / PLN", "dec": 4, "pct": 0.5, "above": [], "below": []},
    {"symbol": "USDPLN=X", "name": "USD/PLN",     "group": "Waluty / PLN", "dec": 4, "pct": 0.7, "above": [], "below": []},
    {"symbol": "GBPPLN=X", "name": "GBP/PLN",     "group": "Waluty / PLN", "dec": 4, "pct": 0.7, "above": [], "below": []},
    {"symbol": "JPYPLN=X", "name": "100 JPY/PLN", "group": "Waluty / PLN", "dec": 4, "pct": 0.8, "mult": 100, "above": [], "below": []},

    # --- Główne pary forex ---
    {"symbol": "EURUSD=X", "name": "EUR/USD", "group": "Forex", "dec": 4, "pct": 0.6, "above": [], "below": []},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "group": "Forex", "dec": 4, "pct": 0.6, "above": [], "below": []},
    {"symbol": "JPY=X",    "name": "USD/JPY", "group": "Forex", "dec": 2, "pct": 0.7, "above": [], "below": []},

    # --- Metale szlachetne ---
    {"symbol": "GC=F", "name": "Złoto (USD/oz)",  "group": "Metale", "dec": 1, "pct": 1.5, "above": [], "below": []},
    {"symbol": "SI=F", "name": "Srebro (USD/oz)", "group": "Metale", "dec": 2, "pct": 2.5, "above": [], "below": []},

    # --- Ropa naftowa ---
    {"symbol": "BZ=F", "name": "Ropa Brent (USD/bbl)", "group": "Ropa", "dec": 2, "pct": 2.0, "above": [], "below": []},
    {"symbol": "CL=F", "name": "Ropa WTI (USD/bbl)",   "group": "Ropa", "dec": 2, "pct": 2.0, "above": [], "below": []},

    # --- Opcjonalnie: metale przemysłowe (odkomentuj, jeśli chcesz) ---
    # {"symbol": "ALI=F", "name": "Aluminium (USD/t)", "group": "Metale", "dec": 0, "pct": 2.0, "above": [], "below": []},
    # {"symbol": "HG=F",  "name": "Miedź (USD/lb)",    "group": "Metale", "dec": 3, "pct": 2.0, "above": [], "below": []},
]
