"""
take_screenshots.py -- retakes the report screenshots of the Taj Ritheek site in the black and
silver theme (dark, 1440x900), then four database screenshots rendered from real MySQL output.

Same approach as e2e_clickthrough.py: the database is snapshotted first and restored afterwards
(dbsnap.py), so no test rows remain. The rejected payment in d03 runs inside a transaction that is
rolled back, and the snapshot is restored once more at the very end.

Needs the site running (bash app_site/run.sh) and Playwright installed.
Run:  python3 app_site/tests/take_screenshots.py
Writes w01..w15 and d01..d04 PNGs into review-3/screenshots/.
"""
import html
import os
import re
import sys
import time
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from mysql.connector import Error
from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbsnap  # noqa: E402
import db  # noqa: E402  (app_site/api/db.py, put on the path by dbsnap)

BASE = os.environ.get("SHOT_BASE", "http://localhost:5173")
OUT = Path(__file__).resolve().parents[2] / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
GUEST = "Meera Krishnan"
EMAIL = "meera.krishnan@example.test"      # example.test: cleanup_manual.sql can find it if ever needed
VIEW = {"width": 1440, "height": 900}


def done(name):
    print(f"  saved {name}.png", flush=True)


# ---------------------------------------------------------------------------- the website
def web_shots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=VIEW, color_scheme="dark")
        # dark theme, and skip the opening doors (they play once per session)
        ctx.add_init_script("try{localStorage.setItem('taj-theme','dark');sessionStorage.setItem('taj-doors','1')}catch(e){}")
        pg = ctx.new_page()
        pg.set_default_timeout(10000)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))

        def shot(name, wait=0):
            if wait:
                pg.wait_for_timeout(wait)
            pg.screenshot(path=str(OUT / f"{name}.png"))
            done(name)

        def scroll_to(locator, offset=110):
            """Bring an element near the top of the viewport (works with the Lenis smooth scroller)."""
            y = locator.evaluate("(el, off) => el.getBoundingClientRect().top + window.scrollY - off", offset)
            pg.evaluate("y => window.scrollTo(0, Math.max(0, y))", y)
            pg.wait_for_timeout(1400)

        def open_page(path, ready):
            pg.goto(BASE + path)
            pg.wait_for_selector(ready)

        # -- pages with the sample data as it is
        open_page("/", "text=The key rack")
        shot("w01_front_desk", wait=4800)

        open_page("/timeline", "text=Room 301")
        shot("w02_timeline", wait=3500)

        open_page("/guests", "text=Priya Sharma")
        shot("w13_guests", wait=2600)

        open_page("/reports", "text=Revenue collected by month")
        pg.wait_for_timeout(1500)
        scroll_to(pg.locator("#r-occ"), offset=40)          # occupancy gauge and the in-house table draw in
        scroll_to(pg.locator("#r-rev"), offset=40)          # revenue and service bars draw in
        pg.wait_for_timeout(3200)                           # let every chart finish
        scroll_to(pg.locator("#r-occ"), offset=40)
        shot("w14_reports", wait=2800)

        open_page("/", "text=The key rack")
        pg.wait_for_timeout(2500)
        pg.keyboard.press("Control+k")
        pg.keyboard.type("sharma")
        pg.get_by_role("option").filter(has_text="Priya Sharma").wait_for()
        shot("w15_command_palette", wait=900)
        pg.keyboard.press("Escape")

        # -- the guest journey with a test guest
        def fill_booking(check_in, check_out, room, plan=None, adults=None, guest_new=False):
            open_page("/book", "text=Choose a room and a rate")
            dates = pg.locator("input[type=date]")
            dates.nth(0).fill(check_in)
            dates.nth(1).fill(check_out)
            if adults:
                for _ in range(adults - 2):
                    pg.get_by_role("button", name="More adults").click()
            pg.wait_for_timeout(800)
            card = pg.get_by_role("listitem").filter(has=pg.get_by_role("radio", name=room))
            pg.get_by_role("radio", name=room).click()
            if plan:
                card.get_by_role("button", name=re.compile(plan)).click()
            if guest_new:
                pg.get_by_role("radio", name="New guest").click()
                pg.get_by_label("Full name").fill(GUEST)
                pg.get_by_label("Email").fill(EMAIL)
            else:
                pg.get_by_label("Guest on file").select_option(label=f"{GUEST} ({EMAIL})")

        # w03: dates, room and rate chosen, the booking slip showing the price
        fill_booking("2031-02-10", "2031-02-12", "Room 102, Standard", plan="Flexible", guest_new=True)
        scroll_to(pg.locator("h2", has_text="The stay"), offset=40)
        expect(pg.get_by_label("Booking estimate")).to_contain_text("2,500.00")
        shot("w03_book_room", wait=900)

        # w04: confirmed
        pg.get_by_role("button", name="Confirm booking").click()
        pg.wait_for_selector(f"text=Reserved for {GUEST}")
        scroll_to(pg.get_by_text(f"Reserved for {GUEST}"), offset=320)
        shot("w04_booking_confirmed", wait=2400)

        # w05: the same room and dates again, refused by the overlap trigger
        fill_booking("2031-02-10", "2031-02-12", "Room 102, Standard", plan="Flexible")
        pg.get_by_role("button", name="Confirm booking").click()
        expect(pg.get_by_role("alert").filter(has_text="overlapping")).to_be_visible()
        scroll_to(pg.locator("h2", has_text="The stay"), offset=40)
        shot("w05_overlap_rejected", wait=1200)

        # w06: four adults in a two-person room, refused by the capacity trigger
        fill_booking("2031-03-03", "2031-03-05", "Room 101, Standard", adults=4)
        pg.get_by_role("button", name="Confirm booking").click()
        expect(pg.get_by_role("alert").filter(has_text="capacity")).to_be_visible()
        scroll_to(pg.locator("h2", has_text="The stay"), offset=40)
        shot("w06_capacity_rejected", wait=1200)

        # w07: check in
        open_page("/stays", f"text={GUEST}")
        pg.locator("li", has_text=GUEST).get_by_role("button", name="Check in").click()
        pg.get_by_role("dialog").get_by_role("button", name="Check in").click()
        pg.wait_for_selector("text=Welcome, Meera")
        shot("w07_checkin", wait=2400)
        pg.get_by_role("button", name="Done").click()

        # w08: a guest request charged to the room in one step
        open_page("/services", "text=New request")
        pg.get_by_label("Guest and room").select_option(label=f"Room 102, {GUEST}")
        pg.get_by_role("button", name="Minibar").click()
        pg.get_by_role("button", name="Log and charge").click()
        pg.wait_for_selector("text=Charged to the room")
        pg.evaluate("window.scrollTo(0, 0)")
        shot("w08_service_charge", wait=1300)

        # w10: the bill before check-out (subtotal, 5% tax, total)
        open_page("/stays?tab=inhouse", f"text={GUEST}")
        pg.locator("li", has_text=GUEST).get_by_role("button", name="Preview bill").click()
        pg.wait_for_selector("text=Total due")
        shot("w10_bill", wait=2600)
        pg.get_by_role("button", name="Check out and issue invoice").click()
        pg.wait_for_selector("text=now with housekeeping")
        pg.get_by_role("button", name="Open the receipt").click()

        # w11: an overpayment, refused by the payment trigger
        pg.wait_for_selector("text=Record a payment")
        pg.wait_for_timeout(1500)
        label = pg.locator("label", has_text="Amount, up to").inner_text()
        balance = re.sub(r"[^\d.]", "", label.split("up to", 1)[1])
        pg.get_by_label("Amount, up to").fill("999999")
        pg.get_by_role("button", name="Record payment").click()
        alert = pg.get_by_role("alert").filter(has_text="exceed")
        expect(alert).to_be_visible()
        scroll_to(pg.get_by_text("Record a payment"), offset=430)
        shot("w11_overpay_rejected", wait=1200)

        # w12: paid in full, the wax seal pressed on the receipt
        pg.get_by_label("Amount, up to").fill(balance)
        pg.get_by_role("button", name="Record payment").click()
        pg.wait_for_selector("text=Paid in full")
        expect(pg.get_by_role("img", name="Paid in full")).to_be_visible()
        pg.wait_for_timeout(2400)
        scroll_to(pg.get_by_text("Payments received"), offset=380)
        shot("w12_paid", wait=1500)

        # w09: housekeeping picks up the room the guest just left
        open_page("/housekeeping", "text=Room 102 needs cleaning")
        pg.get_by_role("button", name="Add a task").click()
        pg.get_by_role("button", name="Add to the board").click()
        pg.wait_for_selector("text=Task added")
        pg.wait_for_timeout(1000)
        card = pg.locator("li", has_text="Room 102").filter(has_text="Post-checkout").first
        card.get_by_role("button", name="Start").click()
        shot("w09_housekeeping", wait=1800)

        print("  page errors:", errors[:5] or "none")
        browser.close()


# ---------------------------------------------------------------------------- the database
def cell(v):
    if v is None:
        return "NULL"
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, (date, Decimal)):
        return str(v)
    if isinstance(v, (bytes, bytearray)):
        return v.decode()
    return str(v)


def grid(cols, rows):
    """Format rows the way the mysql client does."""
    data = [[cell(v) for v in r] for r in rows]
    widths = [max([len(c)] + [len(r[i]) for r in data]) for i, c in enumerate(cols)]
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    out = [line, "| " + " | ".join(c.ljust(w) for c, w in zip(cols, widths)) + " |", line]
    for r in data:
        out.append("| " + " | ".join(v.ljust(w) for v, w in zip(r, widths)) + " |")
    out.append(line)
    return out


class Session:
    """Runs statements on one real connection and keeps a mysql-style transcript."""

    def __init__(self):
        self.conn = db.get_connection()
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self.lines = []

    def run(self, sql, shown=None, keep=None):
        self.lines.append(("prompt", f"mysql> {shown or sql};"))
        t0 = time.perf_counter()
        try:
            self.cur.execute(sql)
            rows = self.cur.fetchall() if self.cur.with_rows else None
        except Error as e:
            self.lines.append(("error", f"ERROR {e.errno} ({e.sqlstate}): {e.msg}"))
            self.lines.append(("plain", ""))
            return None
        took = time.perf_counter() - t0
        if rows is None:
            n = self.cur.rowcount if self.cur.rowcount > 0 else 0
            self.lines.append(("plain", f"Query OK, {n} rows affected ({took:.2f} sec)"))
        else:
            cols = [d[0] for d in self.cur.description]
            if keep:
                idx = [cols.index(k) for k in keep]
                cols = keep
                rows = [[r[i] for i in idx] for r in rows]
            for ln in grid(cols, rows):
                self.lines.append(("table", ln))
            self.lines.append(("plain", f"{len(rows)} row{'s' if len(rows) != 1 else ''} in set ({took:.2f} sec)"))
        self.lines.append(("plain", ""))
        return rows

    def note(self, text):
        self.lines.append(("note", text))

    def close(self):
        self.cur.close()
        self.conn.close()


TERMINAL = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:#070708;}}
body{{min-height:100vh;box-sizing:border-box;padding:46px 52px;font-family:"SF Mono",Menlo,Consolas,monospace;}}
.win{{border:1px solid #2A2A2E;background:#0F0F11;box-shadow:0 30px 60px -30px #000;}}
.bar{{display:flex;align-items:center;gap:8px;padding:12px 16px;border-bottom:1px solid #2A2A2E;color:#8E9196;font-size:13px;}}
.dot{{width:11px;height:11px;border-radius:50%;background:#2A2A2E;}}
.title{{margin-left:14px;letter-spacing:.02em;}}
pre{{margin:0;padding:22px 26px 26px;font:inherit;font-size:15px;line-height:1.55;color:#E3E5E8;white-space:pre-wrap;}}
.prompt{{color:#F7F7F5;}} .prompt b{{color:#8E9196;font-weight:400;}}
.table{{color:#C3C6CB;}} .plain{{color:#8E9196;}} .error{{color:#E07A75;}} .note{{color:#8E9196;font-style:italic;}}
</style></head><body><div class="win"><div class="bar"><span class="dot"></span><span class="dot"></span><span class="dot"></span>
<span class="title">{title}</span></div><pre>{body}</pre></div></body></html>"""


def render(pg, name, title, lines):
    body = []
    for kind, text in lines:
        t = html.escape(text)
        if kind == "prompt":
            t = t.replace("mysql&gt;", "<b>mysql&gt;</b>", 1)
        body.append(f'<span class="{kind}">{t}</span>')
    pg.set_content(TERMINAL.format(title=html.escape(title), body="\n".join(body)))
    pg.wait_for_timeout(200)
    pg.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    done(name)


def db_shots():
    s = Session()
    s.cur.execute("SELECT VERSION(), DATABASE()")
    version, schema = s.cur.fetchone()
    title = f"mysql  {schema}  (server {version})"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport=VIEW)

        s.lines = []
        s.run("SHOW TABLES")
        render(pg, "d01_tables", title, s.lines)

        s.lines = []
        s.run("SELECT * FROM v_current_occupancy")
        render(pg, "d02_view", title, s.lines)

        s.lines = []
        check = ("SELECT invoice_id, total, status, "
                 "(SELECT COUNT(*) FROM payment WHERE invoice_id = 1) AS payments "
                 "FROM invoice WHERE invoice_id = 1")
        s.run(check)
        s.run("START TRANSACTION")
        s.run("INSERT INTO payment (invoice_id, amount, payment_method) VALUES (1, 9999999, 'cash')")
        s.run("ROLLBACK")
        s.run(check)
        s.note("-- trg_payment_limit_insert refused the payment; the transaction was rolled back and nothing changed.")
        render(pg, "d03_trigger_rejection", title, s.lines)

        s.lines = []
        s.run("SHOW TRIGGERS", keep=["Trigger", "Event", "Table", "Timing"])
        s.note("-- columns shown: Trigger, Event, Table, Timing (the full SHOW TRIGGERS output also carries each body)")
        render(pg, "d04_triggers", title, s.lines)
        browser.close()
    s.close()


if __name__ == "__main__":
    snap = dbsnap.take()
    try:
        print("Website (dark theme, 1440x900):")
        web_shots()
    finally:
        print("Rows the screenshots created (now being removed):")
        print("\n".join(dbsnap.created(snap)) or "  none")
        dbsnap.restore(snap)
        print("Database restored.")
    try:
        print("Database (real MySQL output):")
        db_shots()
    finally:
        dbsnap.restore(snap)   # resets AUTO_INCREMENT again, in case the rolled-back INSERT reserved an id
        print("Database checked and restored again. Done.")
