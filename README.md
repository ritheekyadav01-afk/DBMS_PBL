# Hotel Reservation and Guest Services Management System

**Project 12 · DBMS Project-Based Learning (PBL)**
Dandigam Ritheek · AI-ML · Woxsen University · Student ID 25WU0102057 · 2026

A relational database system in MySQL 8, normalized to 3NF, for managing hotel rooms, reservations, guest stays, in-stay services, housekeeping and billing. Business rules are enforced inside the database (10 triggers, 8 CHECK constraints), and three front ends sit on top of it.

> ### ▶ [Try it now: live demo (no install)](https://ritheekyadav01-afk.github.io/taj-ritheek/)
> Opens in any browser and runs on built-in sample data, so no database is needed. The full MySQL-backed version is under [Run the prototype](#run-the-prototype) below.

![Front desk](./review-3/screenshots/w01_front_desk.png)

| | |
|---|---|
| **Live demo** | [ritheekyadav01-afk.github.io/taj-ritheek](https://ritheekyadav01-afk.github.io/taj-ritheek/) (sample data runs in the browser) |
| **Video presentation (5 min)** | see [`video/VIDEO_LINK.md`](./video/VIDEO_LINK.md) |
| **Final report** | [`report/Final_Report.pdf`](./report/Final_Report.pdf) |

## Submission contents

| Item | Location |
|---|---|
| Review 1 deck (PDF) | [`review-1/Review1_Hotel_Deck.pdf`](./review-1/Review1_Hotel_Deck.pdf) |
| Review 2 deck (PDF) | [`review-2/Review2_Hotel_Deck.pdf`](./review-2/Review2_Hotel_Deck.pdf) |
| Review 3 (final) deck (PDF) | [`review-3/Review3_Hotel_Deck.pdf`](./review-3/Review3_Hotel_Deck.pdf) |
| Final report (PDF) | [`report/Final_Report.pdf`](./report/Final_Report.pdf) |
| ER diagram | below, and [`docs/er_diagram.png`](./docs/er_diagram.png) |
| Working prototype | [`review-3/`](./review-3) |
| Video link document | [`video/VIDEO_LINK.md`](./video/VIDEO_LINK.md) |
| HackerRank profile report (DOCX + PDF) | [`hackerrank/HackerRank_Ritheek_DBMS.docx`](./hackerrank/HackerRank_Ritheek_DBMS.docx), [`hackerrank/HackerRank_Ritheek_DBMS.pdf`](./hackerrank/HackerRank_Ritheek_DBMS.pdf) |
| LeetCode profile report (DOCX + PDF) | [`leetcode/LeetCode_Ritheek_DBMS.docx`](./leetcode/LeetCode_Ritheek_DBMS.docx), [`leetcode/LeetCode_Ritheek_DBMS.pdf`](./leetcode/LeetCode_Ritheek_DBMS.pdf) |

## ER diagram

Rendered from the implemented schema (`review-3/db/01_schema.sql`). 12 tables, 14 foreign keys.

```mermaid
erDiagram
    room_type ||--o{ room : "classifies"
    room_type ||--o{ rate_plan : "priced by"
    guest ||--o{ reservation : "makes"
    room ||--o{ reservation : "is booked in"
    rate_plan ||--o{ reservation : "applies to"
    reservation ||--o| stay : "becomes"
    stay ||--o{ service_request : "raises"
    service_request ||--o| service_charge : "billed as"
    stay ||--o{ service_charge : "accrues"
    room ||--o{ housekeeping_task : "needs"
    stay ||--o{ housekeeping_task : "may trigger"
    staff ||--o{ housekeeping_task : "is assigned"
    stay ||--o| invoice : "settled by"
    invoice ||--o{ payment : "receives"

    room_type {
        int type_id PK
        varchar type_name UK
        int capacity
        varchar description
    }
    room {
        int room_id PK
        varchar room_number UK
        int type_id FK
        enum status
    }
    rate_plan {
        int rate_plan_id PK
        int type_id FK
        varchar plan_name
        decimal nightly_rate
        varchar description
    }
    guest {
        int guest_id PK
        varchar full_name
        varchar email UK
        varchar phone
    }
    reservation {
        int reservation_id PK
        int guest_id FK
        int room_id FK
        int rate_plan_id FK
        enum reservation_status
        date planned_check_in
        date planned_check_out
        int adults
        int children
        datetime created_at
    }
    stay {
        int stay_id PK
        int reservation_id FK, UK
        datetime actual_check_in
        datetime actual_check_out
    }
    staff {
        int staff_id PK
        varchar full_name
        varchar role
    }
    housekeeping_task {
        int task_id PK
        int room_id FK
        int stay_id FK
        varchar task_type
        int assigned_to FK
        enum task_status
        datetime scheduled_at
        datetime completed_at
    }
    service_request {
        int service_request_id PK
        int stay_id FK
        varchar service_name
        datetime requested_at
        enum status
    }
    service_charge {
        int charge_id PK
        int stay_id FK
        int service_request_id FK
        varchar description
        decimal amount
        datetime charged_at
    }
    invoice {
        int invoice_id PK
        int stay_id FK, UK
        date invoice_date
        decimal subtotal
        decimal tax
        decimal total
        enum status
    }
    payment {
        int payment_id PK
        int invoice_id FK
        date payment_date
        decimal amount
        enum payment_method
        enum payment_status
    }
```

## Screenshots

All captured from the running prototype and the live MySQL database (`review-3/screenshots/`).

**Front desk dashboard**

![Front desk dashboard](./review-3/screenshots/w01_front_desk.png)

**Reservation timeline**

![Reservation timeline](./review-3/screenshots/w02_timeline.png)

**Book a room**

![Book a room](./review-3/screenshots/w03_book_room.png)

**Booking confirmed**

![Booking confirmed](./review-3/screenshots/w04_booking_confirmed.png)

**Overlapping booking rejected by the database**

![Overlapping booking rejected by the database](./review-3/screenshots/w05_overlap_rejected.png)

**Capacity rule rejects too many occupants**

![Capacity rule rejects too many occupants](./review-3/screenshots/w06_capacity_rejected.png)

**Check-in**

![Check-in](./review-3/screenshots/w07_checkin.png)

**Service charge posted**

![Service charge posted](./review-3/screenshots/w08_service_charge.png)

**Housekeeping board**

![Housekeeping board](./review-3/screenshots/w09_housekeeping.png)

**Bill preview at check-out**

![Bill preview at check-out](./review-3/screenshots/w10_bill.png)

**Overpayment rejected by the database**

![Overpayment rejected by the database](./review-3/screenshots/w11_overpay_rejected.png)

**Invoice paid**

![Invoice paid](./review-3/screenshots/w12_paid.png)

**Guests**

![Guests](./review-3/screenshots/w13_guests.png)

**Reports**

![Reports](./review-3/screenshots/w14_reports.png)

**Command palette (Ctrl K)**

![Command palette (Ctrl K)](./review-3/screenshots/w15_command_palette.png)

**Database: 12 tables**

![Database: 12 tables](./review-3/screenshots/d01_tables.png)

**Database: view v_current_occupancy**

![Database: view v_current_occupancy](./review-3/screenshots/d02_view.png)

**Database: trigger rejects an overpayment and rolls back**

![Database: trigger rejects an overpayment and rolls back](./review-3/screenshots/d03_trigger_rejection.png)

**Database: triggers**

![Database: triggers](./review-3/screenshots/d04_triggers.png)

## Repository layout

```
review-1/   problem statement, scope, initial ER and schema (deck)
review-2/   normalization, data dictionary, DDL, triggers, sample data, queries (deck + sql/)
review-3/   final deck and the working prototype
  db/         01_schema.sql ... 05_queries.sql
  app/        Python command-line app
  app_web/    Streamlit web UI
  app_site/   React + Vite front end, Flask API, tests ("Taj Ritheek")
  docs/       how-to-run guides, validation tests, sample run logs
report/     final report (PDF)
video/      link to the 5-minute video presentation
```

## Design highlights

- **3NF** with two documented exceptions (`service_charge.stay_id`, `housekeeping_task.room_id`), guarded by triggers.
- **8 business rules in the database:** no overlapping bookings, occupants within capacity, check-out after check-in, non-negative charges, no overpayment, rate plan matches room type, charge stay matches request stay, task room matches stay room.
- **8 reporting views:** current occupancy, vacant rooms, cancellations, housekeeping status, guest history, service revenue, total revenue, occupancy rate.
- **Atomic operations:** every multi-step action runs as one transaction; all SQL is parameterized.

## Run the prototype

Requirements: MySQL 8, Python 3.10+, Node 18+ (only for the React site).

```bash
# 1. Create the database (from the repo root)
mysql -u root -p < review-3/db/01_schema.sql
mysql -u root -p hotel_pbl < review-3/db/02_triggers.sql
mysql -u root -p hotel_pbl < review-3/db/03_sample_data.sql
mysql -u root -p hotel_pbl < review-3/db/04_views_reports.sql

# 2. Configure credentials (never committed)
cp review-3/app/.env.example review-3/app/.env     # then edit the password

# 3a. Command-line app
pip install -r review-3/app/requirements.txt
python review-3/app/main.py

# 3b. Streamlit web UI
pip install -r review-3/app_web/requirements.txt
streamlit run review-3/app_web/app.py

# 3c. React + Flask site
bash review-3/app_site/run.sh
```

Detailed guides: [`how_to_run.md`](./review-3/docs/how_to_run.md), [`how_to_run_web.md`](./review-3/docs/how_to_run_web.md), [`how_to_run_site.md`](./review-3/docs/how_to_run_site.md). Test results: [`validation_tests.md`](./review-3/docs/validation_tests.md).
