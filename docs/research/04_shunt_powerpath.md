# 04 — On-board shunt and power path (research, report only)

Date: 2026-11-17. Scope: 16S LFP ESS BMS (40–58.4 V; scope note 7S–16S, NMC to 67.2 V), requirement ±200 A continuous / 500 A peak (`instructions.md` §2.1), owner direction "shunt on the board, compact, compete with Daly / JBD / JK" (PROJECT.md §5, last row).
Nothing in the project was changed.

**Legend.**
* **DS p.N**: datasheet page, from the local copies in `bms_work/review/ds/`. BQ76952 = TI SLUSE13B (Nov 2021). INA240-Q1 = SBOS808E. TLV3501 = local copy.
* **(calc)**: my arithmetic. **(est.)**: estimate, not quoted.
* **Verified**: the part page was opened live on 2026-11-17.

**Stock and price could not be verified for any part.** The JLCPCB and LCSC part pages load stock and price with JavaScript, so WebFetch never received them. A direct query to the LCSC / JLC JSON API was refused by the session permission system. Where a price is given, it comes from a search-engine snippet and is marked as such. Every LCSC number below was seen on a live JLC or LCSC page unless marked otherwise.

---

## 0. Summary of the recommendation

| Item | Recommendation |
|---|---|
| Shunt value | **100 µΩ total**, built as **2 × 200 µΩ Vishay WSLP5931L2000FEA (C413492) in parallel**, 5931 metal strip, 10 W each, ±125 ppm/°C |
| BQ76952 CC | 200 A → 20 mV, which is 10 % of the ±200 mV range. 500 A → 50 mV. Both in range (calc) |
| BQ76952 SCD | 80 mV → **800 A nominal** (680–920 A at ±15 %), delay 1–2 steps (15–30 µs) |
| INA240 | Change to **INA240A1-Q1 (gain 20, C2057377)** on **+3V3**. ±500 A then maps to 0.65–2.65 V, and the ADC can no longer see more than 3.3 V |
| Comparator | Keep it, but make it a **bidirectional window (±600 A) with a hardware latch**. The latch acts on the FET gates through an independent gate-kill and on DFETOFF / CFETOFF. Today's TLV3501 is disabled (SHDN at V+), so fix that |
| Power path | **(B-HS) On-board back-to-back high-side N-FETs driven by the BQ76952 CHG / DSG charge pump**, with PNP turn-off accelerators. 100 V TOLL. 8 per direction for 200 A, 6 for 150 A, 4 for 100 A. Pre-discharge through PDSG + P-FET + the existing R_PRE1 50 Ω. Fallback if the 2-lug compactness of the Chinese style wins: (B-LS) low-side with UCC27524 (see §2.4) |
| FET | HUAYI **HYG015N10NS1TA (C2979263)**, cost-optimised. Infineon **IPT015N10N5 (C108964)** is the reference / premium choice |
| Board | **160 × 100 mm is not viable for 200 A continuous** with the present control circuitry. Choose one: grow to about **220 × 100 mm**, or derate the 160 × 100 board to about **100–120 A continuous** (with heatsink plate), or split into a control board plus a stacked power board. Competitors: Daly 200 A at 164 × 66 × 21 mm (potted, aluminium case); JK PB2A16S20P and JBD UP16S010 at 300 × 100 mm |

---

## 1. On-board shunt

### 1.1 Limits that set the value

| Limit | Source | Value |
|---|---|---|
| CC input range (SRP–SRN) for measurement | BQ76952 DS p.15 §7.15; p.37 §10.3 | −0.2 V … +0.2 V |
| CC resolution (CC1, 16-bit) | DS p.15 note 2 | 1 LSB ≈ 7.6 µV; gain 131 454 LSB/V typ |
| CC offset, uncalibrated | DS p.15 | ±1 LSB (≈ 7.6 µV) |
| SRP / SRN without measuring (fault) | DS p.9 recommended (line "SRP, SRN without measuring current") | −0.2 … +0.75 V |
| SCD thresholds | DS p.22 | 10, 20, 40, 60, 80, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500 mV; accuracy ±15 % (≥ 20 mV), ±35 % (10 mV) |
| SCD delay | DS p.22 | 15–450 µs in 15 µs steps; fastest about 8 µs at 3 mV overdrive and 600 ns at 25 mV overdrive |
| OCD1 / OCD2 | DS p.22 | 4–200 mV in 2 mV steps; accuracy ±4 mV (20–56 mV), ±5 mV (56–100 mV); delay 10–425 ms |
| OCC | DS p.22 | 4–124 mV in 2 mV steps |
| TI guidance | DS p.37 §10.3; p.68–69 §16.2.2; p.75 §18.1 | Use about 1 mΩ or less for 200 A normal current. TCR ≤ 50 ppm. Parallel resistors are OK with good Kelvin connections. 100 Ω + 0.1 µF filter at the BQ pins |
| INA240 | INA240-Q1 DS p.4–6 | VCM −4…80 V; VS 2.7–5.5 V; output linear GND+50 mV … VS−200 mV; BW 400 kHz; gains 20 / 50 / 100 / 200 |

TI precedent: TIDA-010247 (48–1500 V ESS BMU, BQ76972) uses **one 0.3 mΩ, 15 W, 25 ppm shunt** (TIDUF20B p.24). TIDA-010208 (16S, 27 A) uses 2 × 2 mΩ 2 W 50 ppm in parallel (TIDUEY5 p.13 §3, "two parallel 2-mΩ, 2-W, 50-PPM").

### 1.2 Value comparison (all calc)

| R | V at 200 A | V at 500 A | P at 200 A | P at 500 A | CC1 LSB in A | SCD settings available (A) | Verdict |
|---|---|---|---|---|---|---|---|
| 50 µΩ | 10 mV | 25 mV | 2 W | 12.5 W | 0.15 A | 200 (±35 %), 400, 800, 1200, 1600, 2000 … | Coarse. Low-current SOC accuracy suffers. The SCD grid is too coarse at the low end |
| **100 µΩ** | **20 mV** | **50 mV** | **4 W** | **25 W** | **0.076 A** | 100, 200, 400, 600, **800**, 1000, 1250, 1500 … | **Best balance.** Fault voltage stays small (1 kA → 0.1 V) |
| 200 µΩ | 40 mV | 100 mV | 8 W | 50 W | 0.038 A | 50 … 500, 625, **750**, 875, 1000 | Good resolution, but 8 W continuous is hard on FR4 plus FETs. 1 kA → 0.2 V, at the CC limit |
| 300 µΩ | 60 mV | 150 mV | 12 W | 75 W | 0.025 A | … 500, 583, 667, 833 … | Too hot for a compact board. TIDA-010247 accepts it with a 15 W part |

**Choice: 100 µΩ.**
* 200 A uses 10 % of the CC range and 500 A uses 25 %, so there is headroom for charge or discharge peaks.
* Dissipation is 4 W at 200 A.
* SCD can sit at 800 A with 600 A and 1000 A neighbours.
* At a 1–1.5 kA turn-off current, SRP–SRN is 0.10–0.15 V, well inside the 0.75 V no-damage window.
* Low-current accuracy after board-offset calibration is about 10 mA per µV of residual offset (calc). That is adequate for ESS idle currents of ≥ 0.5 A.

### 1.3 Parts (LCSC / JLC numbers seen live; stock not verifiable, see header)

| # | MPN | Mfr | R | Tol | TCR | Power | Size | LCSC / JLC | Class | Verified on | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | **WSLP5931L2000FEA** | Vishay | 0.2 mΩ | 1 % | ±125 ppm | 10 W | 5931 (15 × 7.75 mm) | **C413492** | Extended | jlcpcb.com/partdetail/VishayIntertech-WSLP5931L2000FEA/C413492 | **Recommended, 2 in parallel = 100 µΩ.** A search snippet showed 1 527 in stock (not live) |
| S2 | WSLP5931L1000FEA | Vishay | 0.1 mΩ | 1 % | ±300 ppm | 15 W | 5931 | C2091034 | – | lcsc.com product page | Single-part option. TCR is 6× the TI recommendation (DS p.75): +40 °C self-heating gives 1.2 % error |
| S3 | PEWM5930FL100S9 | RESI | 0.1 mΩ | 1 % | ±200 ppm | 15 W | 5930 | C49437820 | – | lcsc.com/product-detail/C49437820.html | Budget single-part. Datasheet not read |
| S4 | ASR-S-7-0.1F | Shenzhen Yezhan | 0.1 mΩ | 1 % | ±200 ppm | 15 W | 5930 | C6075508 | – | lcsc.com/product-detail/C6075508.html | Budget. The listing says "solder pad splitter", so check the land pattern |
| S5 | BAS-M-R0001-AR-5.0 | Isabellenhütte | 0.1 mΩ | 5 % | ±50 ppm | 36 W | not stated on page (BAS = busbar style, bolted; **not verified**) | C19842016 | – | lcsc.com/product-detail/C19842016.html | Lowest TCR on LCSC. Not SMT-assemblable by JLC (assumption) |
| – | CSS2H-5930R-L100F / -L200F | Bourns | 0.1 / 0.2 mΩ | 1 % | ±150 ppm (L200, third-party copy of datasheet) | 15 W @70 °C / 10 W @130 °C | 5930 | **no LCSC listing found** | – | – | The project has an unused `R_Shunt_CSS2H-5930` footprint in `footprints.pretty/` |
| – | BVR-Z-R0002 (0.2 mΩ, 4026, <±20 ppm) | Isabellenhütte | | | | 5 W | 4026 | **no LCSC listing found** | – | RS / DigiKey only | Best metrology; would need consigned parts |

**Why 2 × S1 rather than one 100 µΩ part:**
1. The TCR is 125 ppm instead of 200–300 ppm, which halves or better the self-heating error.
2. The heat is split over two packages and four pad areas, so each part sees 2 W at 200 A and 12.5 W at 500 A.
3. It is a Vishay part, so the datasheet quality is known.

Residual TCR error is 125 ppm × 30–40 °C ≈ 0.4–0.5 % at full load (calc). Place RT_BOARD (the board NTC) against the shunt pair and compensate in firmware.

**Short-term overload at 500 A was not checked.** The WSLP short-time-overload clause was not read (the Vishay PDF link returned 404). The owner must also give the 500 A pulse duration.

### 1.4 Kelvin footprint and layout

* **Sense pads.** Use 4-terminal sense taps at the inner edge of each copper termination, where the alloy element begins. The pad TCR in the data sheets includes the copper terminations; sensing at the inner edge lowers the copper share (general metal-strip practice, not quoted from a Vishay page). Make a project footprint "WSLP5931 + Kelvin taps", modelled on the existing `R_Shunt_CSS2H-5930`.
* **Two shunts in parallel.** Take the sense line from each shunt through its own **equal resistor** into a summing node: SH_P = average of the 2 top taps, SH_N = average of the 2 bottom taps.
  * Use 2 × 100 Ω on the BQ branch; the BQ's own 100 Ω is then split into 2 × 200 Ω per side.
  * Use 2 × 10 Ω on the INA branch.
  * This also averages any current imbalance between the shunts. Place the parts symmetrically, with identical copper on both.
* **Separate filters** (today SRP / SRN share nets with the INA filter; requirements review C9):
  * BQ: 100 Ω per leg + 0.1 µF differential, placed at the BQ76952 (DS p.75 §18.1).
  * INA240: the existing R_K1 / R_K2 10 Ω + C_K1 100 nF, placed at the INA.
  * Route the two pairs as separate tightly coupled pairs from the shunt taps.
* **Ground reference.** The shunt sits at **B− (VSS)**; the BQ76952 requires a low-side shunt (DS p.37). SH_P is the battery side ("charging current gives positive SRP", DS pin table). R_NT1 stays as the single star tie of `GND_PWR` to the battery side of the shunt. All control-circuit ground returns land on that side.

### 1.5 Copper, lugs, assembly

* **JLC stack-up** (jlcpcb.com/capabilities/pcb-capabilities): multilayer outer copper 1 oz or **2 oz**; inner 0.5 oz (default), 1 oz or 2 oz. Drill up to 6.3 mm; larger holes are routed, so M6 (6.5 mm) and M8 (8.5 mm) plated holes are feasible. There is no heavy copper above 2 oz on multilayer.
  * **Recommendation:** 4-layer, **2 oz outer / 1 oz inner** (a change from today's 1 oz all layers, `instructions.md` §4).
* **Sheet resistance (calc).**
  * 1 oz = 0.49 mΩ/□; 2 oz = 0.25 mΩ/□.
  * All four layers stitched (2+1+1+2 oz) = 0.082 mΩ/□.
  * A 30 mm wide × 60 mm long power path is 2 □ = 0.16 mΩ, which is **6.6 W at 200 A**. That is too much heat on its own, so the PCB copper alone cannot carry 200 A.
* **Copper bars (Chinese practice).** Use tinned copper bars soldered on mask-free strips along the FET drain / source rows and from the lug to the shunt.
  * Example: 10 × 2 mm bar, 20 mm² → 0.86 mΩ/m, so 100 mm = 86 µΩ = 3.4 W at 200 A (calc).
  * Use 10 × 3 mm where possible (2.3 W per 100 mm).
  * JLC SMT cannot place custom bars (**assumption, not checked**), so they are hand- or selective-soldered after PCBA.
* **Lugs.**
  * **Option L1:** M8 studs or nuts through 8.5 mm plated holes clamped through the copper bar, so the lug presses on the bar and not on the PCB. Cheap; needs a mechanical assembly step.
  * **Option L2:** Würth REDCUBE M8 press-fit terminals, e.g. 7461108 (DigiKey: 240 A, ≈ $8.5–11 per unit). The Würth datasheet says: press-fit only, no reflow or wave; PCB 1.6–3.2 mm; 1.475 mm holes; needs a press tool. **No LCSC listing found.**
  * Count: low-side architecture needs **2 lugs** (B−, P−); high-side needs **4 lugs** (B+, P+, B−, P−). See §2.
* **Thermal rise of the shunts (est.).**
  * 2 W per part at 200 A, on 2 oz pads tied to a copper bar: about +20–30 °C above board (est.). It must not sit next to the FET rows; give it ≥ 15 mm and its own copper island.
  * At 500 A each part sees 12.5 W, above its 10 W continuous rating. Acceptable only for short pulses; check the duration against the WSLP pulse curve.

---

## 2. Power-path architecture

### 2.1 Options

* **(A) External contactors** (today): main + negative + pre-charge relay, coil drivers on sheet 05. Pack current still crosses the board, because the shunt is now on the board.
* **(B-LS) Low-side back-to-back N-FET bank** (Daly / JBD / JK style). Two FET banks in series on the B−/P− path. The BQ76952 supplies DDSG / DCHG logic outputs, and an external gate driver (UCC27524) drives the banks.
  * Note on naming: TI's low-side figure and most Chinese boards use a **common-drain** pair (DSG source at B−, CHG source at P−; SLUAA84A p.3 Fig 1-2).
  * A true common-source pair would need a floating gate supply referenced to the mid node. I found no evidence that the named competitors use common-source; treat that as unverified.
* **(B-HS) High-side back-to-back N-FET bank** driven by the BQ76952 CHG / DSG charge pump (TI default; DS p.68 "designed for use with high-side NFET protection"). Series common-drain pair between BAT+ and PACK+.
* **(C) Hybrid**: on-board FET bank sized for 100 A, plus the existing coil drivers kept as an AUX output for an external contactor or a DC-breaker shunt-trip coil.

### 2.2 TI reference designs found

| Design | Topology | Current | Notes | Source |
|---|---|---|---|---|
| TIDA-010208 (TIDUEY5) | BQ76952, **high-side** N-FET | **27 A** charge / discharge | SCD 200 A / 300 µs; 2 × 2 mΩ shunt; pre-discharge 160 mA at 48 V; "Max pack+ 120 V" | ti.com/lit/pdf/tiduey5 p.3, p.13 |
| TIDA-010216 (TIDUF14) | BQ76952, **low-side**, 5 pairs N-FET, UCC27524 dual 5 A driver, UCC27517 for pre-discharge, LM5163 12 V | not read (page text not retrievable) | Closest TI analogue to the Chinese style | ti.com/tool/TIDA-010216 |
| TIDA-010247 (TIDUF20B) | 2 × BQ76972 stacked, **high-side** N-FET with discrete turn-off (P-FET Q54, Q64 / Q65) | not stated | 0.3 mΩ / 15 W / 25 ppm shunt | ti.com/tool/TIDA-010247; TIDUF20B p.11 §2.2.3, p.24 |
| SLUAA84A | Low-side with BQ769x2 | – | DDSG / DCHG are "logic signals not intended to drive FETs" (p.31). PNP turn-off for CHG (Fig 2-4). PCHG / PDSG must be level-shifted for low-side (§8, p.29) | ti.com/lit/pdf/SLUAA84 |
| SLUA952; SLYP856 | Parallel paths; parallel-FET high-power seminar (PNP turn-off speed-up) | – | Found, **not read** | ti.com/lit/pdf/slua952; ti.com/lit/ml/slyp856/slyp856.pdf |

**No TI reference design for a 100–200 A BQ76952 high-side pack was found.** TIDA-010208 is the high-side starting point and must be scaled.

### 2.3 MOSFET candidates (100 V; LCSC numbers seen live)

| MPN | Mfr | Pkg | RDS(on) @10 V | Qg | Other | LCSC / JLC | Class | Price |
|---|---|---|---|---|---|---|---|---|
| **HYG015N10NS1TA** | HUAYI | TOLL-8 | 1.2 typ (DS snippet) / **1.5 mΩ** (JLC page) | 205 nC (JLC page) | 380 A | **C2979263** | Extended | ≈ $1.63 @10 (LCSC datasheet-page snippet, not live) |
| **IPT015N10N5** | Infineon | HSOF-8 (TOLL) | **1.3 typ / 1.5 max mΩ** @150 A; 2.0 max @6 V | 169 typ / 211 max nC | ID 353 A; EAS 775 mJ; RthJC 0.4 K/W max; VGS ±20 V (DS rev 2.2 p.3–4) | **C108964** | Extended | not seen |
| CMSL012N10 | Cmos | TOLL-8 | 1.0 mΩ (listing) | 184 nC | 450 A | C53310613 | – | not seen; datasheet not read |
| CSD19536KTT | TI | TO-263-3 (D²PAK) | 2.2 mΩ @6 V (JLC page) | not read | 200 A | C2687963 | Extended | not seen |
| NCEP020N10LL | NCE | TOLL | not shown | – | 330 A | C2686687 (search result only, page not opened) | – | – |
| CRSS042N10N | CRMicro | TO-263 | 4.2 mΩ | – | – | C410926 (datasheet URL only) | – | Too high RDS for this use |

PDFN5x6 (e.g. VBsemi BSC027N10NS5-VB, C22395984, from search only) is about 2.7 mΩ class. It would need 12–16 parts per direction, so it is not recommended.

**80 V parts are not recommended.** TI advises 5 V DC to 10 V peak per series cell (DS p.68). 100 V gives 1.7× margin on 58.4 V LFP but only 1.49× on 67.2 V NMC 16S. If 16S NMC stays in scope, choose a 120–150 V TOLL (not looked up) or limit NMC to ≤ 14S.

### 2.4 Comparison at 100 / 150 / 200 A (IPT015N10N5 or HYG015N10NS1TA)

Basis (calc):
* Hot RDS(on) taken as 1.5 mΩ × 1.6 = 2.4 mΩ per FET at Tj ≈ 100 °C. The 1.6 factor is the typical OptiMOS normalised curve shape, **not read from the figure**.
* Current flows through both banks (DSG and CHG in series).
* Loss = 2 × I² × 2.4 mΩ / n, with n FETs per bank.

| | 100 A | 150 A | 200 A |
|---|---|---|---|
| FETs per bank / total | 4 / 8 | 6 / 12 | 8 / 16 |
| Bank R (hot) | 0.60 mΩ | 0.40 mΩ | 0.30 mΩ |
| FET loss, both banks (hot max) | 12 W | 18 W | 24 W |
| FET loss, both banks (typ, 1.3 × 1.5) | 7.8 W | 11.7 W | 15.6 W |
| + shunt (100 µΩ) | 1 W | 2.3 W | 4 W |
| + copper / bars / lugs (est.) | 1–2 W | 3–4 W | 5–7 W |
| **Total in BMS** | **≈ 10–15 W** | **≈ 17–24 W** | **≈ 25–35 W** |
| Cooling needed | Board + copper; a plate is advisable | Aluminium plate under FET rows (thermal vias + gap pad) | Plate or heatsink case, as on Daly |

Free-air FR4 160 × 100 mm at +40 °C rise sheds about 10–13 W (h ≈ 10 W/m²K, two faces) (est.). That is why 200 A needs a metal case or heatsink.

| Criterion | (A) External contactors | (B-LS) Low-side N-FET, UCC27524 | (B-HS) High-side N-FET, BQ charge pump | (C) Hybrid |
|---|---|---|---|---|
| Switch count | 2 contactors + pre-charge relay (off-board) | 8 / 12 / 16 TOLL | 8 / 12 / 16 TOLL | 4 + 4 TOLL + AUX contactor driver |
| Loss at 200 A in BMS | shunt + copper ≈ 9 W; contacts off-board (≈ 0.1–0.3 mΩ each, est.) | ≈ 25–35 W | ≈ 25–35 W | rated 100 A on FETs |
| Gate drive | 3 × coil drivers (today's SQ2318 on 3.3 V GPIO is not characterised, review D1). 12 V buck too small for coils (review P4) | DDSG / DCHG → UCC27524 (C465729, Extended) on 12 V from LM5164. Strong (4–5 A) turn-off. CHG bank needs a PNP / level circuit because P− goes below B− with a charger and DSG off (SLUAA84A Fig 2-4) | BQ CHG / DSG, 11 V overdrive (DS p.20: 10–13 V). Turn-off at 20 nF load: DSG 2–20 µs, CHG 46–65 µs (DS p.20). With 8 × 169–205 nC the DSG turn-off is about 70 µs (calc), so **PNP accelerators per bank are mandatory** | as B |
| SC turn-off | Contactor cannot interrupt fast; needs a fuse | Fast (driver-limited, µs). Easy to over-speed, giving an inductive kick | Slow without help; fast with PNP. TI warns that too fast a turn-off gives a large transient (DS p.20 note 5) | as B |
| Pre-charge | J_PRE1 + R_PRE1 + relay (today) | No native support: PDSG / PCHG are BAT-referenced and must be level-shifted (SLUAA84A §8 p.29). TIDA-010216 uses a separate UCC27517 + FET + resistor under MCU control | **Native PDSG**: P-FET + R_PRE1 50 Ω. BQ sequences pre-discharge, then DSG (DS p.45 §11.5.2). PCHG for deeply discharged cells | as B |
| BQ features used | none (FET drivers unused) | DDSG / DCHG used as FET logic. **Uses up the two pins that are NTC4 and the board NTC today** (R4 needs 4–8 NTC; re-plan TS pins). Body-diode protection is still configured, but the LD / PACK measurement relationship changes (SLUAA84A §7) | All native: CHG / DSG, PDSG / PCHG, LD load-detect recovery (p.45), PACK voltage, body-diode protection (p.45), FUSE drive | as B |
| Ground / comms | P− = B− | **P− floats when DSG is off.** CAN and RS-485 are already isolated (ISO7721 + B0505), so comms are OK. Any future non-isolated I/O (wake button, dry contact, AUX 12 V out) must be isolated | P− = B− always. Simplest system ground | as B |
| High-current lugs on board | 2 (shunt only) | **2** (B−, P−); B+ is a sense wire only | **4** (B+, P+, B−, P−) | 2 or 4 |
| TVS / snubber | coil flyback only | See §2.5 | See §2.5 | See §2.5 |
| Board area, power stage (est.) | ≈ 50 × 40 mm (shunt pair + 2 lugs) | ≈ 120 × 50 mm at 200 A (2 rows × 8 TOLL at about 13 mm pitch + bars + 2 lugs + driver) | ≈ 130 × 60 mm at 200 A (as LS + 2 extra lugs + PNPs + PDSG path) | ≈ 80 × 50 mm at 100 A |
| BOM, board-mounted power stage (est.) | ≈ $25–30 (shunts $4, lugs $17–22). **External contactors 2 × $30–80 + relay ≈ $65–165 per pack (est.)** | ≈ $60–70: 16 × HYG $26, driver $1, shunts $4, 2 lugs $17–22, TVS $2–4, bars $5, plate + pad $8 | ≈ $80–90: as LS + 2 lugs, PNPs / P-FET ≈ $1 | ≈ $45 + optional external contactor |
| Infineon instead of HUAYI | – | + ≈ $30–50 (est.) | + ≈ $30–50 (est.) | + ≈ $15–25 |
| Fit to "compete with Daly / JBD / JK" | No: different product class (rack BMS) | Yes: same architecture as competitors, cheapest | Yes: more autonomous protection and features, slightly bigger | Middle |

### 2.5 Inductive kick, SOA and TVS (calc, est.; must be proven by test)

* **Prospective short-circuit current.**
  * 16S LFP 280 Ah: cell DCIR about 0.2–0.25 mΩ, so the stack is about 3.5–4 mΩ (est.).
  * Cables, fuse and busbars add about 2–4 mΩ; the FET banks add about 0.6 mΩ.
  * Total about 7 mΩ, so 58 V / 7 mΩ ≈ **8 kA** prospective.
* **Current at turn-off.**
  * Loop inductance about 1–2 µH gives di/dt ≈ 30–60 A/µs.
  * With SCD at 800 A plus 15 µs delay plus turn-off time, the FETs interrupt about **1.2–1.6 kA**.
* **Energy.** ½LI² ≈ 0.7–2.5 J has to go into TVS and/or FET avalanche.
  * IPT015N10N5 EAS is 775 mJ single pulse at 150 A (DS p.3). Parallel FETs do not share avalanche reliably, so do not rely on it.
* **TVS placement.**
  1. Across BAT+ to B− at the FET input: clamps the cell-side overshoot.
  2. Across PACK+ to PACK−: the load-side swing goes negative.
* **TVS part.** Use a 6.6 kW class (SM8S, DO-218AB; SM8S60A: VBR min 66.7 V, Vc 96.8 V at 68.2 A, DOWO table found by search).
  * Vc at the real current (hundreds of A) will exceed 100 V. So turn-off must be **slowed deliberately**, with gate resistance chosen so di/dt × L stays inside the TVS clamp current, and the FET SOA must cover the linear turn-off interval.
  * **No LCSC number for an SM8S58A / 60A was found** (only SM8S40A C314432 and SM8S24A C7528496 datasheets). The project's D1 SMCJ64A (C284346, unverified) is far too small for this job.
  * Add an RC snubber plus about 4 × 2.2 µF / 100 V X7R ceramics across each FET bank (est.).
* **SOA.** The IPT015N10N5 SOA figure was **not readable** in the extracted text. Read the 10 µs and 100 µs lines at 60–100 V before fixing the gate resistance.
  * Plan a short-circuit test with a 1–2 µH loop.
  * Expect to iterate R_G off between about 2 and 10 Ω per FET, and the PNP base resistor.

### 2.6 Gate-drive specifics for (B-HS)

* **CP1 capacitor.** 470 nF (100–2200 nF allowed, DS p.20).
  * CP1 limit is min(85 V, VBAT + 15 V) (DS p.7). At 67.2 V + 13 V max overdrive = 80.2 V, so it is OK.
  * For 11 V overdrive the FET VGS max must be ≥ 15 V (DS p.68). Both FETs are ±20 V.
* **Gate network per FET.** 10 Ω gate resistor; one shared 1 MΩ gate-source resistor per bank. PDSG / PCHG need ≥ 1 MΩ gate-source on their P-FETs (DS p.45).
* **Accelerator per bank.** A PNP (≥ 100 V, SOT-23 / SOT-89) emitter on the bank gate bus, collector on the bank source (PACK+ for DSG, BAT+ for CHG), base to the BQ pin through about 1–2 kΩ with a diode bypass, as in SLUAA84A Fig 2-4 adapted to high-side and in SLYP856. **Part not chosen; no LCSC number given.**
* **Independent gate-kill** for the latch in §3: a small N-FET or NPN that pulls each PNP base low.
* **Pre-discharge.** PDSG drives a 100 V P-FET (not chosen) in series with R_PRE1 50 Ω / 25 W (C463124, existing, unverified).
  * τ = 50 Ω × C_bus; 5 mF gives 0.25 s (calc).
  * Energy into R = ½CV² = 8.4 J at 58 V and 5 mF (calc).
  * Peak current 1.17 A (review D3).
  * Configure the BQ pre-discharge timeout and stop-delta (TRM, not read).

---

## 3. Short-circuit protection chain

### 3.1 BQ76952 settings with 100 µΩ (proposal, calc)

| Protection | Setting | Current | Delay | Comment |
|---|---|---|---|---|
| SCD | 80 mV | 800 A (680–920 A at ±15 %) | 15–30 µs (1–2 steps) | Autonomous; latching variant plus LD load-detect recovery available (DS p.45). Must sit above the 500 A peak |
| OCD1 | 56 mV | 560 A (±50 A at ±5 mV) | 10–20 ms | Lets a 500 A pulse through for its rated time. **Owner must give the 500 A duration** |
| OCD2 | 30 mV | 300 A (±40 A) | 0.4 s | – |
| OCD3 (firmware, CC-based) | 210 A | – | 10–60 s | Continuous limit |
| OCC | 22 mV | 220 A | 100 ms | Charge side |

Accuracy reference: DS p.22.

### 3.2 Is INA240 + comparator still needed?

**Keep it, repurposed.** The BQ76952 SCD is already an MCU-independent, hardware, latching discharge trip. The INA path adds three things:
1. **Diversity and redundancy.** A second, independent channel for the safety case (UL 1973 / IEC 62619 single-fault), relevant to the "more features than Daly" goal.
2. **Charge-direction fast trip.** BQ OCC is ms-scale only (DS p.22), so the INA path is the only fast charge-direction trip.
3. **A 400 kHz bandwidth signal** for the MCU: fast current logging and FET-stress monitoring.

**Changes required** (requirements review C1–C5, M7):

| Fix | Detail |
|---|---|
| Gain | INA240A2 → **INA240A1-Q1 (C2057377**, SOIC-8, Extended; verified on jlcpcb.com/partdetail/TexasInstruments-INA240A1QDRQ1/C2057377). Gain 20 V/V (INA240 DS p.3) |
| Supply | INA240 VS from +5V → **+3V3** (VS 2.7–5.5 V, DS p.4). REF1 = +3V3, REF2 = GND keeps 1.65 V mid-scale. This fixes the ADC_I_SENSE > 3.3 V issue (M7) |
| Transfer function | ADC_I_SENSE = 1.65 V + 2.0 mV/A (calc). ±500 A → 0.65 … 2.65 V. Linear to +725 A (VS − 0.2 V) and −800 A (GND + 0.05 V). 12-bit ADC gives 0.4 A per LSB |
| Comparator | TLV3501 SHDN is at V+, so the part is **disabled** (DS p.4 note 1). Tie SHDN to V−. Make a **window**: two comparators (TLV3502 dual, same family, **LCSC not looked up**) at 1.65 ± 1.2 V = **2.85 V / 0.45 V → ±600 A** |
| Latch | Use a D-flip-flop or SR latch (e.g. 74LVC1G74 class, **part not chosen**) set by either comparator and cleared only by the MCU (OCP_RESET) and power-on reset |
| Latch output (OCP_TRIP_N, latched) | (a) drives the **independent gate-kill** of §2.6, so the hardware path does not go through the BQ; (b) pulls **DFETOFF and CFETOFF** low so the BQ state agrees (DFETOFF / CFETOFF response time **not in the datasheet**, unverified); (c) feeds an MCU EXTI and the LED |
| MCU pin | PA8 has no TIM1_BKIN (review M8). Keep it as EXTI |
| Alternative (cheaper) | Delete the comparator and rely on BQ SCD, with DDSG / DCHG or ALERT driving the gate-kill. This saves about $1.5 and 8 parts but loses fast charge-side trip and diversity |

---

## 4. Does 160 × 100 mm work?

**Competitor sizes** (retail / manual hosts, not manufacturer drawings):

| BMS | Size | Source |
|---|---|---|
| Daly 16S 48 V 200 A smart BMS | **164 × 66 × 21 mm**, 380 g; same case for 150 A and 200 A | manual on manuals.plus; desertcart listing |
| JK PB2A16S20P (200 A, 2 A active balance) | **300 × 100 × 24 mm** | nkon.nl / evlithium / JK manual quotes |
| JBD UP16S010 16S 200 A | **300 × 100 × 38 mm** | JBD datasheet PDF (cdn.shopify …JBD-UP16S010…pdf) |
| Heltec 16S 200 A | 300 × 100 × 38 mm (search summary) | heltec-energy.com manual |

**Assessment.**
* The present board is 160 × 100 mm, 4-layer. It already carries the AFE, MCU, the isolated comms with a milled slot, five supplies and 16 × 2512 balance resistors on the bottom.
* A 200 A power stage needs about 120–130 × 50–60 mm (§2.4), which is roughly **40–50 % of the board**. It also needs a heatsink plate under it and a 15 mm thermal and creepage keep-out from the AFE and the shunt sense lines.
* JK and JBD spend 300 × 100 mm on 200 A. Daly reaches 164 × 66 mm only with a dense single-function layout potted in a finned aluminium case.

**Options for the owner:**
1. **220 × 100 mm single board**, 2 oz outer: power stage on one 100 mm end, control on the other. 200 A with an aluminium base plate. Still about 27 % smaller than JK and JBD.
2. **Keep 160 × 100 mm and rate it 100 A continuous / 300 A peak** (4 + 4 FETs, 2 lugs). This is the Daly "100 A" class and is realistic on a plate.
3. **Two boards:** control at 160 × 100 mm plus a stacked 160 × 60 mm power board (FETs, shunt, lugs, 2 oz). Board-to-board signals are the gate drives, Kelvin pair, BAT+ / PACK+ sense and NTC. This allows one control board for 100 / 150 / 200 A power variants.

---

## 5. Recommendation and circuit outline (for owner decision)

**Recommended:** (B-HS) high-side, 100 µΩ (2 × 200 µΩ) shunt at B−, INA240A1 + window comparator + latch, board 220 × 100 mm (or option 3).

**Why high-side over the cheaper low-side:**
1. TI designed the BQ76952 for high-side drive (DS p.68).
2. It uses PDSG / PCHG / LD / PACK and body-diode protection natively, which fits the owner's "use every useful BQ76952 feature".
3. It keeps DCHG / DDSG free for thermistors or fault outputs, so R4 stays met.
4. The system ground P− = B− never floats.

**Switch to (B-LS) if** the 2-lug size and the lowest cost matter more. It is the Daly / JBD architecture; the isolated comms already cover its ground problem.

### Blocks and nets (new names in `CODE` style)

```
BATTERY+ ──(lug J_BP, M8)──┬── BAT_PLUS ──[TVS D_TVS_BAT: SM8S-class to B−]
                           │      │
                           │   [Q_CHG1..8  HYG015N10NS1TA / IPT015N10N5, TOLL, sources = BAT_PLUS,
                           │      drains = FET_MID]         gates = GATE_CHG (10 Ω each)
                           │      │  PNP accelerator Q_CHG_OFF: E=GATE_CHG, C=BAT_PLUS, B←CHG (BQ pin 45) via R/D
                           │   FET_MID (copper bar)
                           │      │
                           │   [Q_DSG1..8 same part; drains = FET_MID, sources = PACK_PLUS]
                           │      gates = GATE_DSG (10 Ω each); PNP Q_DSG_OFF: E=GATE_DSG, C=PACK_PLUS, B←DSG (pin 43)
                           │   PACK_PLUS ──(lug J_PP, M8)── to inverter +
                           │      ├─ R 10 kΩ → BQ LD (pin 41);  PACK_PLUS → R → BQ PACK pin
                           │      └─[TVS D_TVS_PACK PACK_PLUS→PACK_MINUS] + RC snubber
                           ├── R/D → V_BAT_FILT (BQ BAT, existing D_BAT1 / C_BAT1)
                           └── Pre-discharge: Q_PDSG (100 V P-FET, S=BAT_PLUS side, G←PDSG pin 39, 1 MΩ G-S)
                                   → R_PRE1 50 Ω 25 W (existing) → PACK_PLUS
                               (optional PCHG: Q_PCHG P-FET + R → BAT_PLUS from PACK_PLUS)

BATTERY− ──(lug J_BM, M8)── B_MINUS (=GND_PWR star via R_NT1) ──[R_SH1 ∥ R_SH2 WSLP5931L2000FEA, C413492]── PACK_MINUS ──(lug J_PM, M8)── inverter −
   Kelvin taps: SH_P_a/b (battery side), SH_N_a/b (pack side)
     ├─ 2×200 Ω averaging → 100 Ω-equivalent → SRP / SRN (pins 18 / 20) + 0.1 µF diff at BQ
     └─ 2×10 Ω averaging → AMP_IN+ / AMP_IN− → C_K1 100 nF → U_ISENSE1 INA240A1-Q1 (C2057377), VS = +3V3
            ADC_I_SENSE → MCU PA0
            ADC_I_SENSE → U_OCP1 window (dual comparator), V_TH_HI 2.85 V, V_TH_LO 0.45 V
                       → U_LATCH (D-FF) → OCP_LATCH_N
                            ├─ GATE_KILL: Q_KILL_C / Q_KILL_D pull PNP bases → both banks off (independent of BQ, MCU)
                            ├─ BQ DFETOFF / CFETOFF (active low)
                            ├─ MCU EXTI (PA8) + LED D_OCP1
                            └─ cleared by MCU OCP_RESET (GPIO, PA15 or a free pin) and POR

BQ76952: CP1 470 nF; SCD 80 mV / 15–30 µs; OCD1 56 mV / 10–20 ms; OCD2 30 mV / 0.4 s; OCC 22 mV / 100 ms;
         series-FET mode, body-diode protection on; predischarge enabled; FUSE pin optional (chemical fuse or breaker trip)
NTC: one NTC on the FET bar (FET_MID copper) and RT_BOARD moved next to R_SH1/2 for TCR compensation
AUX (option C): keep one existing coil driver as BRK_TRIP output (DC breaker shunt-trip) for permanent fault
Cooling: TOLL rows over a solid 2 oz pour + thermal via field → 1.5–2 mm gap pad → aluminium base plate / case
PCB: 4-layer, 2 oz outer / 1 oz inner; tinned Cu bars 10×2–3 mm soldered on mask-free strips; M8 holes 8.5 mm
```

### Owner decisions needed

1. **Architecture:** B-HS (recommended) or B-LS (Daly / JBD style, 2 lugs, cheaper), or keep A, or C.
2. **Rating and size:** 200 A on 220 × 100 mm, or 100 A on 160 × 100 mm, or the two-board split.
3. **Chemistry scope:** if 16S NMC (67.2 V) stays, use 120–150 V FETs (not yet selected).
4. **500 A peak duration**, so OCD1 and the shunt pulse rating can be set.
5. **Busbar method:** soldered bars + M8 bolts, or Würth REDCUBE press-fit (needs a press).

### Not verified / open

* **Stock, price and Basic / Extended:** stock and price for every LCSC part (dynamic page; API call refused). Basic / Extended is confirmed only where the JLC page was opened: C413492, C2979263, C108964, C2687963, C2057377, C465729 are all Extended.
* **Datasheet items not read:**
  * IPT015N10N5 SOA curve (image).
  * HUAYI datasheet (the 1.2 vs 1.5 mΩ figure is inconsistent between LCSC and JLC).
  * WSLP5931 pulse and overload curve (Vishay PDF 404).
  * TIDUF14 (TIDA-010216) current rating and FET part.
  * SLUA952 and SLYP856 contents.
  * BQ76952 TRM (pre-discharge timeout, DFETOFF response time, TS pin re-assignment).
* **No LCSC numbers found** for: SM8S58A / 60A TVS, Bourns CSS2H-5930 0.1 / 0.2 mΩ, Isabellenhütte BVR, Würth REDCUBE. PNP accelerator, P-FET, dual comparator and latch parts are not chosen yet.
* **Competitor dimensions** come from retail and manual-host pages, not from manufacturer drawings.
* **All loss, thermal, short-circuit-current and cost figures** are calc / est. and need bench verification (thermal run at 100 / 150 / 200 A; short-circuit test with a defined loop inductance).

### Sources

* BQ76952 DS SLUSE13B (local `ds/bq76952.txt`): p.7, 9, 15, 20, 22, 37, 45, 49, 68–69, 75.
* INA240-Q1 DS (local): p.3–6. TLV3501 DS (local): p.4.
* TIDA-010208 / TIDUEY5: https://ti.com/lit/pdf/tiduey5
* TIDA-010216: https://www.ti.com/tool/TIDA-010216 ; https://ti.com/document-viewer/lit/html/tiduf14
* TIDA-010247 / TIDUF20B: https://ti.com/tool/TIDA-010247 ; https://edgeworker.ti.com/lit/pdf/tiduf20
* SLUAA84A: https://ti.com/lit/pdf/SLUAA84 · SLUA952: https://edgeworker.ti.com/lit/pdf/slua952 · SLYP856: https://www.ti.com/lit/ml/slyp856/slyp856.pdf
* Parts:
  * https://jlcpcb.com/partdetail/VishayIntertech-WSLP5931L2000FEA/C413492
  * https://lcsc.com/product-detail/Current-Sense-Resistors-Shunt-Resistors_Vishay-Intertech-WSLP5931L1000FEA_C2091034.html
  * https://www.lcsc.com/product-detail/C49437820.html
  * https://www.lcsc.com/product-detail/C6075508.html
  * https://www.lcsc.com/product-detail/C19842016.html
  * https://jlcpcb.com/partdetail/HUAYI-HYG015N10NS1TA/C2979263
  * https://jlcpcb.com/partdetail/InfineonTechnologies-IPT015N10N5ATMA1/C108964 (DS: Infineon IPT015N10N5 rev 2.2)
  * https://www.lcsc.com/product-detail/C53310613.html
  * https://jlcpcb.com/partdetail/TexasInstruments-CSD19536KTT/C2687963
  * https://jlcpcb.com/partdetail/TexasInstruments-INA240A1QDRQ1/C2057377
  * https://jlcpcb.com/partdetail/TexasInstruments-UCC27524DR/C465729
* JLC capabilities: https://jlcpcb.com/capabilities/pcb-capabilities
* Würth REDCUBE: https://www.we-online.com/katalog/datasheet/7461059.pdf ; https://azcus.digikey.com/en/products/detail/w%C3%BCrth-elektronik/7461108/2682521
* Competitors:
  * Daly: https://manuals.plus/asin/B0F5MN9K9R ; https://www.desertcart.com.cy/products/737062912
  * JK: https://nkon.nl/en/jk-bms-pb2a16s20p.html
  * JBD: https://cdn.shopify.com/s/files/1/0606/5199/5298/files/JBD-UP16S010-L16S-200A-200A-B-U-R-C-A03.pdf
  * Heltec: https://www.heltec-energy.com/uploads/16S-100A-200A-Communication-BMS-Compatible-With-Inverters-User-Manual.pdf
