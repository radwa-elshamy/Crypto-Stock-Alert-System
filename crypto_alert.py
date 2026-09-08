"""
Crypto & Stock Alert System
Monitor prices and get instant alerts via Email or Telegram

Requirements:
    pip install customtkinter requests playsound
"""

import customtkinter as ctk
import threading
import json
import time
import smtplib
import os
from datetime import datetime
from tkinter import messagebox
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "alert_config.json"

CRYPTO_IDS = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "BNB": "binancecoin",
    "Solana (SOL)": "solana",
    "Ripple (XRP)": "ripple",
    "Dogecoin (DOGE)": "dogecoin",
    "Cardano (ADA)": "cardano",
    "Polygon (MATIC)": "matic-network",
}

STOCK_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"]


def get_crypto_price(coin_id):
    """Get current crypto price from CoinGecko (free, no API key)."""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        price = data[coin_id]["usd"]
        change = data[coin_id].get("usd_24h_change", 0)
        return price, round(change, 2)
    except Exception as e:
        return None, None


def get_stock_price(symbol):
    """Get stock price from Yahoo Finance (free)."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        prev = data["chart"]["result"][0]["meta"]["chartPreviousClose"]
        change = ((price - prev) / prev) * 100
        return price, round(change, 2)
    except Exception as e:
        return None, None


def send_email_alert(smtp_config, subject, body):
    """Send email alert."""
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_config["email"]
        msg["To"] = smtp_config["email"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_config["email"], smtp_config["password"])
            server.send_message(msg)
        return True
    except Exception as e:
        return False


def send_telegram_alert(token, chat_id, message):
    """Send Telegram alert."""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
        return True
    except Exception:
        return False


class AlertApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("💹 Crypto & Stock Alert System")
        self.geometry("950x720")
        self.resizable(True, True)

        self.alerts = []
        self.is_monitoring = False
        self.stop_event = threading.Event()
        self.config = self._load_config()

        self._build_ui()
        self._refresh_prices()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"email": "", "email_password": "", "telegram_token": "", "telegram_chat_id": ""}

    def _save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#0D1117", corner_radius=0, height=65)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="💹 Crypto & Stock Alert System",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color="#F0B429").pack(side="left", padx=20, pady=16)
        ctk.CTkLabel(header, text="Real-time price monitoring & instant alerts",
                     font=ctk.CTkFont(size=12), text_color="#8B9467").pack(side="right", padx=20)

        # Main
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=16, pady=12)

        # Left panel
        left = ctk.CTkFrame(main, width=300, corner_radius=12)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        # Add alert section
        ctk.CTkLabel(left, text="➕ Add New Alert", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(16, 4), padx=16, anchor="w")

        # Asset type
        ctk.CTkLabel(left, text="Asset Type", font=ctk.CTkFont(size=12)).pack(pady=(8, 2), padx=16, anchor="w")
        self.asset_type = ctk.StringVar(value="Crypto")
        ctk.CTkSegmentedButton(left, values=["Crypto", "Stock"], variable=self.asset_type,
                                command=self._on_asset_type_change).pack(padx=16, fill="x")

        ctk.CTkLabel(left, text="Asset", font=ctk.CTkFont(size=12)).pack(pady=(8, 2), padx=16, anchor="w")
        self.asset_menu_var = ctk.StringVar(value="Bitcoin (BTC)")
        self.asset_menu = ctk.CTkOptionMenu(left, values=list(CRYPTO_IDS.keys()), variable=self.asset_menu_var)
        self.asset_menu.pack(padx=16, fill="x")

        ctk.CTkLabel(left, text="Alert Condition", font=ctk.CTkFont(size=12)).pack(pady=(8, 2), padx=16, anchor="w")
        self.condition_var = ctk.StringVar(value="Price drops below")
        ctk.CTkOptionMenu(left, values=["Price drops below", "Price rises above",
                                         "24h change drops below %", "24h change rises above %"],
                           variable=self.condition_var).pack(padx=16, fill="x")

        ctk.CTkLabel(left, text="Target Value", font=ctk.CTkFont(size=12)).pack(pady=(8, 2), padx=16, anchor="w")
        self.target_entry = ctk.CTkEntry(left, placeholder_text="e.g. 45000", height=36)
        self.target_entry.pack(padx=16, fill="x")

        ctk.CTkLabel(left, text="Alert Method", font=ctk.CTkFont(size=12)).pack(pady=(8, 2), padx=16, anchor="w")
        self.alert_method = ctk.StringVar(value="App Notification")
        ctk.CTkOptionMenu(left, values=["App Notification", "Email", "Telegram", "All"],
                           variable=self.alert_method).pack(padx=16, fill="x")

        ctk.CTkButton(left, text="➕ Add Alert", command=self._add_alert, height=38,
                      fg_color="#F0B429", text_color="black", hover_color="#D4A017",
                      font=ctk.CTkFont(size=13, weight="bold")).pack(padx=16, pady=(12, 4), fill="x")

        ctk.CTkLabel(left, text="─" * 34, text_color="#333").pack(padx=16, pady=4)

        # Check interval
        ctk.CTkLabel(left, text="Check Every", font=ctk.CTkFont(size=12)).pack(pady=(4, 2), padx=16, anchor="w")
        self.interval_var = ctk.StringVar(value="60 seconds")
        ctk.CTkOptionMenu(left, values=["30 seconds", "60 seconds", "5 minutes", "15 minutes"],
                           variable=self.interval_var).pack(padx=16, fill="x")

        self.monitor_btn = ctk.CTkButton(left, text="▶ Start Monitoring", command=self._toggle_monitoring,
                                          height=40, fg_color="#1A8F4A", hover_color="#157A3E",
                                          font=ctk.CTkFont(size=13, weight="bold"))
        self.monitor_btn.pack(padx=16, pady=(10, 4), fill="x")

        ctk.CTkButton(left, text="⚙️ Notification Settings", command=self._open_settings,
                      height=34, fg_color="#2C3E50").pack(padx=16, pady=(0, 16), fill="x")

        # Right panel with tabs
        right = ctk.CTkFrame(main, corner_radius=12)
        right.pack(side="right", fill="both", expand=True)

        self.tabs = ctk.CTkTabview(right)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)

        self.tabs.add("📊 Live Prices")
        self.tabs.add("🔔 My Alerts")
        self.tabs.add("📋 Alert History")

        # Live prices tab
        prices_tab = self.tabs.tab("📊 Live Prices")

        refresh_row = ctk.CTkFrame(prices_tab, fg_color="transparent")
        refresh_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(refresh_row, text="Top Crypto & Stocks — Live",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        ctk.CTkButton(refresh_row, text="🔄 Refresh", width=80, height=28,
                      command=self._refresh_prices, fg_color="#1A5276").pack(side="right")

        self.prices_scroll = ctk.CTkScrollableFrame(prices_tab, corner_radius=8)
        self.prices_scroll.pack(fill="both", expand=True)

        # Alerts tab
        alerts_tab = self.tabs.tab("🔔 My Alerts")
        self.alerts_scroll = ctk.CTkScrollableFrame(alerts_tab, corner_radius=8)
        self.alerts_scroll.pack(fill="both", expand=True)

        # History tab
        history_tab = self.tabs.tab("📋 Alert History")
        self.history_text = ctk.CTkTextbox(history_tab, font=ctk.CTkFont(family="Courier", size=11))
        self.history_text.pack(fill="both", expand=True)

        # Status bar
        self.status_label = ctk.CTkLabel(right, text="⏸ Not monitoring",
                                          font=ctk.CTkFont(size=11), text_color="#7F8C8D")
        self.status_label.pack(pady=(0, 8))

    def _on_asset_type_change(self, value):
        if value == "Crypto":
            self.asset_menu.configure(values=list(CRYPTO_IDS.keys()))
            self.asset_menu_var.set("Bitcoin (BTC)")
        else:
            self.asset_menu.configure(values=STOCK_SYMBOLS)
            self.asset_menu_var.set("AAPL")

    def _refresh_prices(self):
        for w in self.prices_scroll.winfo_children():
            w.destroy()

        def fetch():
            coins = list(CRYPTO_IDS.items())[:6]
            for name, coin_id in coins:
                price, change = get_crypto_price(coin_id)
                if price:
                    self.after(0, self._add_price_row, name, f"${price:,.2f}", change, "crypto")
            for sym in STOCK_SYMBOLS[:4]:
                price, change = get_stock_price(sym)
                if price:
                    self.after(0, self._add_price_row, sym, f"${price:,.2f}", change, "stock")

        threading.Thread(target=fetch, daemon=True).start()

    def _add_price_row(self, name, price, change, asset_type):
        color = "#1C2833" if len(self.prices_scroll.winfo_children()) % 2 == 0 else "#212F3D"
        row = ctk.CTkFrame(self.prices_scroll, fg_color=color, corner_radius=6)
        row.pack(fill="x", pady=1, padx=2)

        icon = "₿" if asset_type == "crypto" else "📈"
        ctk.CTkLabel(row, text=f"{icon} {name}", font=ctk.CTkFont(size=12, weight="bold"),
                     width=200, anchor="w").pack(side="left", padx=12, pady=8)
        ctk.CTkLabel(row, text=price, font=ctk.CTkFont(size=12),
                     text_color="#F0B429", width=120).pack(side="left")
        if change is not None:
            change_color = "#2ECC71" if change >= 0 else "#E74C3C"
            arrow = "▲" if change >= 0 else "▼"
            ctk.CTkLabel(row, text=f"{arrow} {abs(change):.2f}%",
                         font=ctk.CTkFont(size=12), text_color=change_color).pack(side="left", padx=12)

        ctk.CTkButton(row, text="Set Alert", width=80, height=26,
                      fg_color="#1A5276", font=ctk.CTkFont(size=11),
                      command=lambda n=name: self._quick_alert(n)).pack(side="right", padx=12)

    def _quick_alert(self, name):
        self.asset_menu_var.set(name)

    def _add_alert(self):
        asset = self.asset_menu_var.get()
        condition = self.condition_var.get()
        target = self.target_entry.get().strip()
        method = self.alert_method.get()

        if not target:
            messagebox.showerror("Missing", "Enter a target value.")
            return
        try:
            float(target)
        except ValueError:
            messagebox.showerror("Invalid", "Target must be a number.")
            return

        alert = {
            "id": len(self.alerts) + 1,
            "asset": asset,
            "asset_type": self.asset_type.get(),
            "condition": condition,
            "target": float(target),
            "method": method,
            "active": True,
            "triggered": False,
        }
        self.alerts.append(alert)
        self._render_alerts()
        self.target_entry.delete(0, "end")
        self._log_history(f"Alert added: {asset} — {condition} {target}")

    def _render_alerts(self):
        for w in self.alerts_scroll.winfo_children():
            w.destroy()

        if not self.alerts:
            ctk.CTkLabel(self.alerts_scroll, text="No alerts yet. Add one from the left panel.",
                         text_color="#555").pack(pady=40)
            return

        for alert in self.alerts:
            card = ctk.CTkFrame(self.alerts_scroll,
                                fg_color="#1A5276" if alert["active"] else "#2C3E50",
                                corner_radius=8)
            card.pack(fill="x", pady=3, padx=2)

            info = f"{'✅' if alert['triggered'] else '🔔'} {alert['asset']} — {alert['condition']} {alert['target']}"
            ctk.CTkLabel(card, text=info, font=ctk.CTkFont(size=12), anchor="w").pack(side="left", padx=12, pady=10)
            ctk.CTkLabel(card, text=alert["method"], font=ctk.CTkFont(size=11),
                         text_color="#AED6F1").pack(side="left", padx=8)

            ctk.CTkButton(card, text="🗑", width=32, height=28, fg_color="#922B21",
                          command=lambda a=alert: self._remove_alert(a)).pack(side="right", padx=8)

    def _remove_alert(self, alert):
        self.alerts.remove(alert)
        self._render_alerts()

    def _toggle_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.stop_event.clear()
            self.monitor_btn.configure(text="⏹ Stop Monitoring", fg_color="#922B21")
            self.status_label.configure(text="✅ Monitoring active...", text_color="#2ECC71")
            thread = threading.Thread(target=self._monitor_loop, daemon=True)
            thread.start()
        else:
            self.is_monitoring = False
            self.stop_event.set()
            self.monitor_btn.configure(text="▶ Start Monitoring", fg_color="#1A8F4A")
            self.status_label.configure(text="⏸ Not monitoring", text_color="#7F8C8D")

    def _monitor_loop(self):
        interval_map = {"30 seconds": 30, "60 seconds": 60, "5 minutes": 300, "15 minutes": 900}
        while not self.stop_event.is_set():
            interval = interval_map.get(self.interval_var.get(), 60)
            self.after(0, self._check_alerts)
            self.stop_event.wait(interval)

    def _check_alerts(self):
        for alert in self.alerts:
            if not alert["active"] or alert["triggered"]:
                continue

            asset_type = alert["asset_type"]
            asset = alert["asset"]
            condition = alert["condition"]
            target = alert["target"]

            if asset_type == "Crypto":
                coin_id = CRYPTO_IDS.get(asset, "bitcoin")
                price, change = get_crypto_price(coin_id)
            else:
                price, change = get_stock_price(asset)

            if price is None:
                continue

            triggered = False
            if condition == "Price drops below" and price < target:
                triggered = True
            elif condition == "Price rises above" and price > target:
                triggered = True
            elif condition == "24h change drops below %" and change and change < target:
                triggered = True
            elif condition == "24h change rises above %" and change and change > target:
                triggered = True

            if triggered:
                alert["triggered"] = True
                msg = f"🚨 ALERT: {asset} — {condition} {target}\nCurrent: ${price:,.2f}"
                self._fire_alert(alert, msg)
                self._log_history(f"TRIGGERED: {msg}")
                self._render_alerts()
                self.after(0, lambda m=msg: messagebox.showinfo("Price Alert Triggered!", m))

        ts = datetime.now().strftime("%H:%M:%S")
        self.after(0, lambda: self.status_label.configure(text=f"✅ Last checked: {ts}"))

    def _fire_alert(self, alert, message):
        method = alert.get("method", "App Notification")
        if method in ("Email", "All") and self.config.get("email"):
            threading.Thread(target=send_email_alert, args=(
                self.config, "Price Alert!", message), daemon=True).start()
        if method in ("Telegram", "All") and self.config.get("telegram_token"):
            threading.Thread(target=send_telegram_alert, args=(
                self.config["telegram_token"], self.config["telegram_chat_id"], message), daemon=True).start()

    def _log_history(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_text.insert("end", f"[{ts}] {msg}\n")
        self.history_text.see("end")

    def _open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Notification Settings")
        win.geometry("420x380")

        ctk.CTkLabel(win, text="📧 Email Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(16, 4), padx=20, anchor="w")
        email_entry = ctk.CTkEntry(win, placeholder_text="Gmail address", height=36)
        email_entry.pack(padx=20, fill="x")
        email_entry.insert(0, self.config.get("email", ""))

        ctk.CTkLabel(win, text="App Password (not your Gmail password)", font=ctk.CTkFont(size=11)).pack(pady=(8, 2), padx=20, anchor="w")
        pwd_entry = ctk.CTkEntry(win, placeholder_text="Gmail App Password", show="*", height=36)
        pwd_entry.pack(padx=20, fill="x")
        pwd_entry.insert(0, self.config.get("email_password", ""))

        ctk.CTkLabel(win, text="🤖 Telegram Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(16, 4), padx=20, anchor="w")
        token_entry = ctk.CTkEntry(win, placeholder_text="Bot Token from @BotFather", height=36)
        token_entry.pack(padx=20, fill="x")
        token_entry.insert(0, self.config.get("telegram_token", ""))

        ctk.CTkLabel(win, text="Chat ID (message @userinfobot to get yours)", font=ctk.CTkFont(size=11)).pack(pady=(8, 2), padx=20, anchor="w")
        chat_entry = ctk.CTkEntry(win, placeholder_text="Telegram Chat ID", height=36)
        chat_entry.pack(padx=20, fill="x")
        chat_entry.insert(0, self.config.get("telegram_chat_id", ""))

        def save():
            self.config["email"] = email_entry.get()
            self.config["email_password"] = pwd_entry.get()
            self.config["telegram_token"] = token_entry.get()
            self.config["telegram_chat_id"] = chat_entry.get()
            self._save_config()
            win.destroy()
            messagebox.showinfo("Saved", "Settings saved!")

        ctk.CTkButton(win, text="💾 Save Settings", command=save, height=40,
                      fg_color="#1A5276").pack(padx=20, pady=16, fill="x")


if __name__ == "__main__":
    app = AlertApp()
    app.mainloop()
