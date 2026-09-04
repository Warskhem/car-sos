# 🚨 CAR SOS — Project Presentation

> A QR‑code based emergency response system for vehicles.
> Turn any vehicle sticker into a lifesaving alert with a single smartphone scan.

---

## Slide 1 — Title

# Car SOS
### Emergency Response System for Vehicles
**Turning every vehicle sticker into a lifesaving tool**

*Presenter Name | Date | Course/Event*

> **Speaker notes:**
> "Good morning/afternoon everyone. Today I'll present Car SOS — a project that lets anyone, in the critical first minutes after an accident or breakdown, instantly notify the driver's loved ones with their exact location. No special hardware, no mobile app installation — just a printed QR code and any smartphone camera."

---

## Slide 2 — The Problem

# The Problem
### Why do drivers need help they can't always ask for?

- 🕐 **The "Golden Hour"** — survival rates drop sharply when help is delayed
- 🚗 **Stranded & vulnerable drivers** — the elderly, solo travellers, breakdowns on remote roads
- 🙋 **Bystanders can't help** — witnesses want to assist but don't know *who* to contact
- 🔒 **Privacy dilemma** — exposing full contact info to strangers is risky
- 📱 **App fatigue** — victims' emergency apps are often not installed or not set up
- 💸 **Cost barriers** — GPS trackers, roadside subscriptions are expensive

> **Speaker notes:**
> "Every year, millions of accidents happen. The people most likely to find the victim first are bystanders or other drivers — not emergency services. In those critical minutes, a bystander usually has no way to reach the victim's family. Car SOS solves exactly this gap."

---

## Slide 3 — Our Solution

# The Solution: Car SOS

**A printable QR-code sticker + a smart web platform.**

- 📇 Each vehicle gets a **unique QR code sticker** (placed on the windshield)
- 📱 Any phone scans it — **no app required**
- 📍 **Auto-captures the rescuer's GPS location** (they're at the scene)
- ☎️ **Instantly calls the primary emergency contact** with a spoken alert
- 📨 **Sends an SMS** with a Google Maps location link
- 🗂️ **Logs every SOS event** for the owner and administrator

> **Speaker notes:**
> "The beauty is simplicity. The rescuer just points their camera at the sticker. The system identifies the vehicle, grabs the rescue location, and does the rest automatically — a voice call plus an SMS with a live map link to the primary contact."

---

## Slide 4 — How It Works (Flow)

# How It Works

```
[ Office ]                                    [ Field ]
──────────                                    ─────────
 Admin generates QR codes + stickers
        │
        ’—►  Vehicle owner claims a code, registers vehicle + 3 contacts
                      │
                      ’—►  Sticker printed & placed on windshield
                                    │
                    ┌───────────────┴───────────────┐
                    │    ACCIDENT / BREAKDOWN        │
                    │    Rescuer scans the sticker    │
                    └───────────────┬───────────────┘
                                    ’—► System captures GPS
                                    ’—► Auto-calls PRIMARY contact (voice)
                                    ’—► Sends SMS with map link
                                    ’—► Optional: send SOS to ALL contacts
                                    ’—► Saved to SOS history + admin log
```

> **Speaker notes:**
> "Walk through the flow: the admin produces the codes, the owner claims and registers their vehicle and up to three emergency contacts, and the sticker goes on the glass. When an accident happens, scanning the sticker automatically calls the primary contact and sends the location. There's also a big manual SOS button that alerts all three contacts."

---

## Slide 5 — Key Features

# Key Features

| | |
|---|---|
| 📱 **Zero-install scanning** | Works with any smartphone camera |
| 📍 **Automatic GPS capture** | Rescuer's live location sent to contacts |
| ☎️ **Auto-alert primary** | Fires the moment the page loads |
| 🗣️ **Voice call + SMS** | Spoken alert with vehicle info + map link |
| 🔒 **Privacy protected** | Contacts notified without exposing owner's info |
| 🧪 **Demo / simulation mode** | Full showcase without paid telecom services |
| 🖨️ **Printable sticker** | High-res PNG generated for glass mounting |
| 🛠️ **Admin dashboard** | Generate/export QR codes, view all users & logs |
| 📊 **SOS analytics** | Real-time stats on the dashboard |
| 📜 **SOS history** | Every user can review their past alerts |

> **Speaker notes:**
> "Highlighting the standout differentiators: zero-install scanning, automatic GPS, and privacy. Every bystander becomes a potential first responder, while the driver's personal information stays hidden."

---

## Slide 6 — The Services

# Services Delivered

1. **QR Code Generation & Management** — unique secure codes, bulk generation, CSV export
2. **Vehicle Registration** — link a vehicle to a QR code with full details
3. **Emergency Contacts** — up to 3 prioritized contacts per owner
4. **Automated Voice Alerts** — Plivo-powered call with spoken vehicle + location info
5. **GPS Location SMS** — text message with a live map link
6. **Emergency Beep / Flash** — attention-grabbing audio + visual on the SOS page
7. **Sticker Generation** — printable, ready-to-mount window sticker (PNG)
8. **SOS History & Admin Analytics** — full audit trail + dashboard statistics

> **Speaker notes:**
> "Group the services into three buckets: preparation (QR codes, registration, stickers), response (voice calls, SMS with location), and management (history, admin analytics)."

---

## Slide 7 — Technical Architecture

# Technical Architecture

| Layer | Technology | Role |
|---|---|---|
| **Web Framework** | Flask (Python) | Backend server & routing |
| **Database** | SQLite + SQLAlchemy ORM | Users, QR codes, vehicles, contacts, SOS logs |
| **Auth** | Flask-Login + Werkzeug | User & admin login, password hashing |
| **QR Generation** | qrcode[pil] + `secrets` | Unique 8-char codes + QR images |
| **Telecom** | Plivo REST API | Voice calls & SMS |
| **Stickers** | Pillow (PIL) | Printable sticker PNG |
| **Audio** | Custom WAV generator | Emergency beeps |

### Data Model
`User` ⟷ `Vehicle` ⟷ `QRCode` · `User` ⟷ `EmergencyContact` (×3) · `SOSLog` (event audit)

> **Speaker notes:**
> "The stack is clean and lightweight: Flask serving the web app, SQLite for storage, Plivo as the telecom provider for calls and SMS. It's fully open-source and easily modifiable — a strong advantage for a student or community project."

---

## Slide 8 — Live Demo

# Live Demo

1. **Admin** → generate a QR code
2. **Scan / open** the code → register a vehicle + 3 contacts
3. **Open the SOS page** → GPS capture + **auto-alert primary**
4. **Press SOS** → alert all contacts (simulated without Plivo)
5. **Check** SOS history + admin dashboard

*Runs locally at `http://127.0.0.1:5000`*

> **Speaker notes:**
> "I'll walk through this live. The app runs in demo mode (simulated calls/SMS) so we can show the full experience without a paid telecom account. Take screenshots as we go for your slides."

---

## Slide 9 — Advantages ✅

# Advantages

- 🏷️ **Zero hardware cost** — only a printed sticker
- 📱 **No app for rescuers** — universal scan & assist
- ⚡ **Fast response** — GPS auto-captured, primary auto-dialled
- 🙏 **Good Samaritan friendly** — passersby can help safely
- 🔒 **Privacy preserving** — owner's info hidden from strangers
- 📈 **Scalable & cheap** — bulk QR generation, low per-vehicle cost
- 🗂️ **Data-driven** — SOS analytics for fleet/community monitoring
- 🧩 **Open-source & extensible** — Flask + SQLite, easy to customize
- 🧪 **Demo mode** — presentable without paid services

> **Speaker notes:**
> "The biggest wins are cost, accessibility, and privacy. Any phone can trigger an alert, the owner's data stays hidden, and the system is inexpensive to scale to an entire fleet or community."

---

## Slide 10 — Disadvantages / Limitations ⚠️

# Disadvantages / Limitations

- 📶 **Needs caller's phone & signal** — no GPS/data = degraded response
- 💳 **Plivo (paid) required** for real calls/SMS — demo isn't a real alert
- 🔧 **Hardcoded config** — `SITE_URL` set to a dev sandbox (needs production setup)
- 🔐 **Default credentials** — default admin (`admin123`) & hardcoded secret key need hardening
- 🚫 **No owner confirmation step** — any scan auto-triggers; risk of false positives
- 🚑 **Limited coverage** — no ambulance/police/insurance API integration
- 🌐 **Single-language UI** — English-only spoken alerts
- 🗄️ **SQLite** — fine for small scale, not for very large deployments
- 📲 **No push notifications** — relies on SMS + voice only

> **Speaker notes:**
> "Be honest here — it shows the project is realistic and well-scoped. The main gaps are needing a paid telecom provider for real alerts, some production hardening, and safeguards against accidental triggers. These are the natural next steps in the development phase."

---

## Slide 11 — Does It Benefit the Community?

# Community Benefit: An Overwhelming Yes

- 🚑 **Faster emergency response** — help claims the critical first minutes
- 🤝 **Empowers bystanders** — any citizen becomes a first responder
- 👵 **Protects vulnerable drivers** — elderly, solo travellers, fleets
- 💰 **Cost-effective program** — NGOs, local gov, taxi/transport fleets can deploy affordably
- 📊 **Road-safety insights** — SOS data helps identify accident-prone areas
- 🎓 **Awareness & preparedness** — promotes mutual aid and readiness

> **Speaker notes:**
> "Focus on real-world impact: faster help, empowered bystanders, protection for the most vulnerable, and a low-cost model that community programs can actually afford to run at scale."

---

## Slide 12 — Next Steps / Roadmap

# Next Steps & Roadmap

**Completed**
- ✅ Full working web application (Flask + SQLite + Plivo-ready)
- ✅ QR generation, registration, SOS triggering, history, admin tools

**Development Phase (Next)**
- 🔒 Production hardening — remove default credentials, use env secrets
- 📍 Real location URLs instead of "Location not available" placeholders
- ⚠️ Add owner confirmation / false-positive safeguards
- 🌍 Multi-language spoken + UI support
- 🚑 Integrate ambulance / police / insurance alerting
- 📱 Optional mobile app & push notifications

> **Speaker notes:**
> "The project is fully functional already. The roadmap focuses on hardening it for real-world use and expanding coverage. These are the tasks we'll tackle in the ongoing development phase."

---

## Slide 13 — Summary

# Summary

| | |
|---|---|
| **What** | QR-based emergency alert system for vehicles |
| **Why** | Speed saves lives; bystanders need a way to help |
| **How** | Scan sticker → auto-call primary + send GPS SMS |
| **Built with** | Flask, SQLite, Plivo, QR/Pillow |
| **Strength** | Zero hardware, no app, privacy-safe, low cost |
| **Gaps** | Needs production hardening & paid telecom |
| **Impact** | Strong community benefit for road safety |

> **Speaker notes:**
> "To wrap up: Car SOS is a practical, low-cost, privacy-respecting system that turns any smartphone into a lifesaving tool, helping the most vulnerable drivers get help faster."

---

## Slide 14 — Thank You / Q&A

# Thank You 🙏
### Questions & Discussion

**Contact / Demo:**
- Local app: `http://127.0.0.1:5000`
- Admin login: `admin@carsos.com` / `admin123`

> **Speaker notes:**
> "Open the floor for questions. Offer a live demo. Mention the project is open-source and welcomes contributions."
