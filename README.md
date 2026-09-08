[README (1).md](https://github.com/user-attachments/files/31952289/README.1.md)
# 💹 Crypto & Stock Alert System

> Never miss the perfect buy or sell moment again.

A desktop app that monitors cryptocurrency and stock prices in real-time and sends you instant alerts via Email or Telegram when your target price is hit — no coding required.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 What It Looks Like

```
┌─────────────────────────────────────────────────────┐
│  💹 Crypto & Stock Alert System                     │
├──────────────────┬──────────────────────────────────┤
│  Search Settings │  📊 Live Prices                  │
│                  │                                  │
│  Asset: Bitcoin  │  ₿ Bitcoin    $67,420  ▲ 2.3%   │
│  Condition:      │  ₿ Ethereum   $3,521   ▲ 1.1%   │
│  drops below     │  📈 AAPL      $189.5   ▼ 0.3%   │
│  Target: 60000   │  📈 TSLA      $245.2   ▲ 4.2%   │
│  Method: Email   │                                  │
│                  │  🔔 My Alerts                    │
│ [▶ Start Monitor]│  BTC < $60,000  → Email          │
│                  │  ETH > $4,000   → Telegram       │
│  ✅ 3 leads found│                                  │
└──────────────────┴──────────────────────────────────┘
```

---

## ✨ Features

- **Live prices** — Bitcoin, Ethereum, Solana, BNB, XRP + AAPL, TSLA, NVDA, GOOGL and more
- **Unlimited alerts** — Price drops below / rises above / 24h % change
- **Instant notifications** — Email (Gmail) + Telegram bot
- **Flexible intervals** — Check every 30 seconds, 1 min, 5 min, or 15 min
- **Alert history** — Full log of every triggered alert
- **No API key needed** — Uses free CoinGecko + Yahoo Finance APIs
- **Beautiful dark UI** — Built with CustomTkinter

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install customtkinter requests
```

### 2. Run the app
```bash
python crypto_alert.py
```

### 3. Set your first alert
1. Select asset (e.g. Bitcoin)
2. Choose condition (e.g. "Price drops below")
3. Enter target value (e.g. 60000)
4. Choose alert method (Email / Telegram / App)
5. Click **Add Alert**
6. Click **▶ Start Monitoring**

---

## 📧 Email Setup (Gmail)

1. Go to Google Account → Security → App Passwords
2. Create an App Password for "Mail"
3. In the app: click **⚙️ Notification Settings**
4. Enter your Gmail + the App Password

## 🤖 Telegram Setup

1. Message @BotFather on Telegram → `/newbot` → copy your token
2. Message @userinfobot to get your Chat ID
3. In the app: enter Token + Chat ID in settings

---

## 📋 Example Alert Scenarios

| Asset | Condition | Target | Use Case |
|-------|-----------|--------|----------|
| Bitcoin | drops below | $55,000 | Buy the dip |
| Ethereum | rises above | $4,500 | Take profit |
| TSLA | drops below | $200 | Buy opportunity |
| BTC | 24h change below | -10% | Panic sell alert |
| NVDA | rises above | $900 | Breakout alert |

---

## 📁 File Structure

```
crypto-stock-alert/
├── crypto_alert.py      # Main application
├── alert_config.json    # Saved settings (auto-created)
├── requirements.txt
└── README.md
```

---

## 🛠 Requirements

```
customtkinter>=5.2.0
requests>=2.31.0
Python 3.10+
```

---

## 💡 Supported Assets

**Crypto:** Bitcoin, Ethereum, BNB, Solana, XRP, Dogecoin, Cardano, Polygon

**Stocks:** AAPL, GOOGL, MSFT, AMZN, TSLA, META, NVDA, NFLX (add any Yahoo Finance symbol)

---

## 📞 Support & Custom Orders

Need a custom version? Contact me on:
- Fiverr: [your-fiverr-link]
- Email: radwa.elshamy16@gmail.com

---

## 📜 License
MIT License — free to use and modify for personal use.
