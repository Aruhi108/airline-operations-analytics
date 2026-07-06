# Business Insights & Recommendations
## Airline Operations Analytics — 2025 Annual Review

*All figures below are computed directly from `data/airline_flights_clean.csv` (12,000 flights, Jan–Dec 2025).*

---

## 🔍 Key Business Insights

**1. Overall on-time performance is 82.5%**, meaning roughly **1 in 6 flights** arrives more than 15 minutes late or is cancelled — below the ~80% industry benchmark floor most carriers target, but with real room to close the gap on specific airlines and routes.

**2. Reliability varies meaningfully by airline**, from Falcon Jet (best, ~8.0 min average departure delay, 84% on-time) to Summit Airlines (worst, ~9.6 min average delay, 82% on-time). The spread is modest in this dataset — reinforcing that delay problems are **route- and day-specific rather than purely an airline-wide issue**.

**3. A small set of routes drive disproportionate delay risk.** Routes such as **LAX–ORD (14.6 min avg delay)**, **ORD–BOS (13.3 min)**, and **MIA–SEA (13.1 min)** run well above the network average, despite healthy flight volume (100+ flights each) — these are not statistical noise, they are structurally congested routes.

**4. Delays are heavily right-skewed, not normally distributed.** The IQR-based outlier analysis flagged **20.2% of flights** as statistical delay outliers. This confirms that **reporting only the average delay hides the real story** — a small number of severely delayed flights (some 300+ minutes) pull the average up while most flights are close to on-time.

**5. Cancellations are low (1.8%) but concentrated in controllable causes.** Of 211 cancellations, **mechanical issues (28%)** and **crew unavailability (22%)** — both within the airline's operational control — account for half of all cancellations, versus weather (24%) and air traffic control (26%), which are largely uncontrollable.

**6. Friday and Thursday are the worst days for delays** (9.6–9.8 min average), while **Wednesday is the best** (7.9 min) — a pattern consistent with real-world end-of-week congestion and crew/aircraft turnaround pressure building through the week.

**7. Weather is not the dominant delay driver in this network.** Counterintuitively, "Windy" (10.9 min) and "Storm" (9.9 min) conditions show only modestly higher delays than "Clear" (9.0 min) — suggesting **operational and scheduling factors (aircraft turnaround, crew scheduling, gate congestion) are at least as important as weather** in explaining delays.

**8. Revenue is heavily concentrated in the West and South regions** ($212.6M and $198.9M respectively), together contributing **67% of total network revenue**, while the Midwest region contributes only $67.4M — a potential signal of under-scheduled capacity or under-marketed routes in the Midwest.

**9. Fleet load factor is healthy and evenly distributed** (79.2%–80.0% across all five aircraft types), with **Boeing 787 running highest (80.0%)**. No aircraft type is meaningfully under-utilized, suggesting current fleet-to-route assignment is reasonably efficient — capacity growth should focus on adding frequency on high-demand routes rather than reassigning aircraft types.

**10. Customer satisfaction (avg 3.0/5) shows almost no correlation with delay severity** in this dataset — "Severe Delay" flights actually average the same satisfaction (3.01) as "On-Time" flights (2.99). This is a genuinely useful (if initially surprising) finding: it suggests **satisfaction is being driven by factors this dataset doesn't yet capture** (e.g., service quality, seat comfort, communication during disruption) rather than delay length alone — a strong candidate for a follow-up driver analysis.

**11. Survey response rate is 76.4%**, meaning nearly a quarter of flights have no satisfaction feedback at all — a data-completeness gap that should be addressed before satisfaction is used to justify major operational decisions.

**12. Top 5 routes by revenue (LAX–JFK, SEA–MIA, BOS–SEA, JFK–LAX, MIA–LAX) are all long-haul, coast-to-coast or coast-to-Miami routes**, each generating over $11M in annual revenue — confirming that premium long-distance routes, not short regional hops, are the network's commercial backbone.

---

## ✅ Recommendations

1. **Target the top 5–8 chronically delayed routes (e.g., LAX–ORD, ORD–BOS, MIA–SEA) for a dedicated operational review** — likely candidates are gate/turnaround scheduling and slot congestion at the connecting hub, not weather.

2. **Prioritize mechanical-readiness and crew-scheduling investments over weather mitigation.** Since mechanical issues and crew unavailability drive half of all cancellations and weather is a smaller delay factor than expected, the highest-ROI fix is tightening maintenance turnaround and crew reserve staffing — both controllable levers.

3. **Add Thursday/Friday-specific buffer time or additional ground crew staffing** to absorb the predictable end-of-week delay spike, rather than applying uniform buffers across all weekdays.

4. **Investigate Midwest region under-performance** — determine whether it reflects genuine lower demand or under-scheduled capacity/marketing; a modest frequency increase on high-load-factor Midwest routes could capture incremental revenue.

5. **Do not use delay data alone to explain customer satisfaction.** Commission a proper satisfaction-driver analysis (e.g., regression against service, communication, comfort variables) before investing further in delay-reduction as a satisfaction lever — the current data suggests other factors matter more.

6. **Close the survey response gap** (currently 76.4%) through post-flight app prompts or incentives — a quarter of flights currently have zero satisfaction signal, weakening the reliability of any satisfaction-based decision.

7. **Protect and grow the top 5 long-haul revenue routes** with capacity and pricing priority — these routes are the commercial backbone of the network and should be insulated from schedule cuts even during cost-reduction cycles.

8. **Continue the current fleet allocation strategy** (load factors are healthy and balanced across aircraft types) — reallocate effort toward route frequency optimization rather than fleet-mix changes in the near term.
