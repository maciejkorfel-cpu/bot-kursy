"""
Bot kursów walut i metali -> Telegram.

Tryby:
  python bot.py check    – sprawdza kursy i wysyła alerty (uruchamiany co godzinę)
  python bot.py summary  – wysyła poranne podsumowanie
  python bot.py test     – wysyła wiadomość testową
"""
import json
import math
import os
import sys
from pathlib import Path

import requests
import yfinance as yf

from config import INSTRUMENTS, LOOKBACK

STATE_FILE = Path(__file__).with_name("state.json")
TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


# ---------- pomocnicze ----------

def send(text: str) -> None:
    if not TOKEN or not CHAT_ID:
        print("[brak TELEGRAM_TOKEN / TELEGRAM_CHAT_ID] Wiadomość:\n" + text)
        return
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML",
              "disable_web_page_preview": True},
        timeout=20,
    )
    r.raise_for_status()


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def fmt(value: float, dec: int) -> str:
    return f"{value:,.{dec}f}".replace(",", " ").replace(".", ",")


def fetch(inst: dict) -> dict | None:
    """Pobiera dzienne notowania; ostatni wiersz = bieżąca cena dzisiejszej sesji."""
    hist = yf.Ticker(inst["symbol"]).history(period="3mo", interval="1d")
    closes = hist["Close"].dropna()
    if len(closes) < 3:
        return None
    m = inst.get("mult", 1)
    price = float(closes.iloc[-1]) * m
    prev = float(closes.iloc[-2]) * m
    window = closes.iloc[-(LOOKBACK + 1):-1] * m
    return {
        "price": price,
        "prev": prev,
        "chg": (price / prev - 1) * 100,
        "hi": float(window.max()),
        "lo": float(window.min()),
        "date": closes.index[-1].date().isoformat(),
    }


# ---------- tryby ----------

def check() -> None:
    state = load_state()
    alerts, errors = [], []

    for inst in INSTRUMENTS:
        try:
            d = fetch(inst)
        except Exception as e:  # pojedynczy instrument nie wywala całego bota
            errors.append(f"{inst['name']}: {e}")
            continue
        if not d:
            errors.append(f"{inst['name']}: brak danych")
            continue

        name, dec = inst["name"], inst["dec"]
        p = fmt(d["price"], dec)
        s = state.setdefault(inst["symbol"], {})
        day = d["date"]

        # 1) Duża zmiana dzienna (eskalacja co wielokrotność progu)
        step = math.floor(abs(d["chg"]) / inst["pct"])
        if s.get("chg_day") != day:
            s["chg_day"], s["chg_step"] = day, 0
        if step >= 1 and step > s.get("chg_step", 0):
            s["chg_step"] = step
            arrow = "🟢▲" if d["chg"] > 0 else "🔴▼"
            alerts.append(f"{arrow} <b>{name}</b> {d['chg']:+.2f}% dziś → {p}")

        # 2) Najwyżej / najniżej od LOOKBACK sesji (raz dziennie)
        if d["price"] > d["hi"] and s.get("hi_day") != day:
            s["hi_day"] = day
            alerts.append(f"📈 <b>{name}</b> najwyżej od {LOOKBACK} sesji: {p}")
        if d["price"] < d["lo"] and s.get("lo_day") != day:
            s["lo_day"] = day
            alerts.append(f"📉 <b>{name}</b> najniżej od {LOOKBACK} sesji: {p}")

        # 3) Twoje poziomy cenowe (alert tylko w momencie przebicia)
        for lvl in inst.get("above", []):
            key, now = f"above_{lvl}", d["price"] >= lvl
            if now and not s.get(key, False):
                alerts.append(f"🎯 <b>{name}</b> powyżej {fmt(lvl, dec)} → {p}")
            s[key] = now
        for lvl in inst.get("below", []):
            key, now = f"below_{lvl}", d["price"] <= lvl
            if now and not s.get(key, False):
                alerts.append(f"🎯 <b>{name}</b> poniżej {fmt(lvl, dec)} → {p}")
            s[key] = now

    save_state(state)

    if alerts:
        send("\n".join(alerts))
    if errors:
        print("Błędy:\n" + "\n".join(errors))
        if len(errors) == len(INSTRUMENTS):
            send("⚠️ Bot kursów: nie udało się pobrać żadnych danych.")
    print(f"OK – alertów: {len(alerts)}, błędów: {len(errors)}")


def summary() -> None:
    lines = ["☀️ <b>Kursy – podsumowanie</b>"]
    group = None
    for inst in INSTRUMENTS:
        try:
            d = fetch(inst)
        except Exception:
            d = None
        if inst["group"] != group:
            group = inst["group"]
            lines.append(f"\n<b>{group}</b>")
        if not d:
            lines.append(f"{inst['name']}: brak danych")
            continue
        arrow = "▲" if d["chg"] > 0 else ("▼" if d["chg"] < 0 else "•")
        lines.append(f"{arrow} {inst['name']}: {fmt(d['price'], inst['dec'])} ({d['chg']:+.2f}%)")
    send("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": check, "summary": summary,
     "test": lambda: send("✅ Bot kursów działa.")}[mode]()
