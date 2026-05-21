# 🧺 Centralized Laundry Tracker

A real-time, cross-platform IoT state management system designed to track washing machine availability across residential college networks. 

This project bridges a Telegram Bot interface with a live Streamlit Web Dashboard, utilizing a centralized Supabase database to provide users with real-time countdowns, automated waitlists, and instant push notifications.

## ✨ Core Features

* **📱 Cross-Platform Synchronization:** Actions taken on the Telegram bot (locking a machine, joining a waitlist) instantly reflect on the web dashboard, and vice versa.
* **⏱️ Client-Side Timer Injection:** The web dashboard utilizes polyglot programming (Python injecting JavaScript/HTML) to offload live, second-by-second countdowns to the client browser, completely bypassing server timezone desyncs.
* **🧹 Asynchronous Global Sweeper:** A self-healing background engine (`reminder.py`) continuously monitors the database for expired timers, automatically unlocking machines and resetting system states without manual intervention.
* **🔔 Smart Queueing & Double-Alarms:** Features a waitlist system that notifies queued users the second a machine is free, alongside an "Early Warning" system that pings current users 5 minutes before their cycle ends.

## 🛠️ Tech Stack

* **Backend / Engine:** Python 3, `asyncio`
* **Web Frontend:** Streamlit, Injected JavaScript/HTML, `streamlit-autorefresh`
* **Bot Interface:** `python-telegram-bot`
* **Database:** Supabase (PostgreSQL)

## 🏗️ System Architecture

1. **`app.py`**: The Streamlit web dashboard providing a live visual grid of machine states.
2. **`laundry_bot.py`**: The Telegram bot serving as the primary mobile UI for users to lock machines and join waitlists.
3. **`reminder.py`**: The continuous asynchronous background loop handling push notifications and database sweeping.

