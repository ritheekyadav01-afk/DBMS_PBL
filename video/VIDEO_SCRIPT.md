# 5-minute video: script and shot list

Record your screen with your voice (QuickTime: File > New Screen Recording, or Zoom). Keep it between 4:30 and 5:00. Have these open first: the Review 3 deck PDF, the live site (or the local site), and the repo README.

| Time | On screen | Say (in your own words) |
|---|---|---|
| 0:00-0:20 | Title slide of the Review 3 deck | Name, ID, Project 12: Hotel Reservation and Guest Services Management System. One line: it keeps rooms, bookings, services and bills consistent. |
| 0:20-0:50 | Problem and objectives slides | Hotels double-book rooms and miss charges when data is scattered. Goal: one database that enforces the rules itself. |
| 0:50-1:35 | ER diagram (README or deck), then normalization slide | 12 tables, 3 areas: inventory, guest activity, billing. Normalized to 3NF; two documented exceptions guarded by triggers. Reservation and Stay are separate because a booking can be cancelled before arrival. |
| 1:35-2:10 | Constraints / triggers slide | 8 business rules live in the database: overlap, capacity, dates, non-negative, overpayment, and three consistency triggers. So no front end can bypass them. |
| 2:10-4:00 | **Live prototype** (Taj Ritheek site) | 1) Front desk dashboard. 2) Book a room, then try to book the same dates again: show the rejection message. 3) Check in. 4) Post a service charge. 5) Check out and show the bill. 6) Try to overpay: rejected. Pay in full: paid seal. 7) Open Reservation timeline, drag a booking. 8) Reports page. |
| 4:00-4:30 | Testing slide | Every rule was deliberately broken against live MySQL and rejected. Transactions roll back cleanly. Automated end-to-end test with screenshots. |
| 4:30-5:00 | Results slide, then the GitHub repo page | What was delivered: schema, triggers, views, 3 front ends. Future work: roles, dynamic pricing, online booking. Repo and report links are in the README. Thank you. |

## Upload steps

1. Save the recording as an .mp4.
2. Upload to your personal Google Drive.
3. Right-click the file > Share > General access > **Anyone with the link** > Viewer > Copy link.
4. Open the link in a private/incognito window to confirm it plays without signing in.
5. Paste the link into `video/VIDEO_LINK.md` (replace the placeholder), then commit and push.
