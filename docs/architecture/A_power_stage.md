> Detailed section; where it conflicts with ../ARCHITECTURE.md, ARCHITECTURE.md wins.

# A — Power stage, current sense and independent safety trip

Architecture part A for the 16S LFP ESS BMS (target: beat Daly / JBD / JK). This is **architecture only**: no schematic or KiCad file was changed.
Date: 2026-11-17. Basis: `PROJECT.md` decisions log (owner, 2026-11-17), `instruction.md` §3 and §8, `instructions.md` §2–4, and `docs/research/00_SUMMARY.md`, `01_bq76952_features.md` and `04_shunt_powerpath.md`. This part builds on those reports and does not repeat their option studies.

**Binding owner decisions used here (PROJECT.md §5, 2026-11-17):**
* on-board back-to-back high-side N-MOSFET banks driven by BQ76952 CHG / DSG, with PCHG / PDSG;
* 200 A continuous, LFP only, 100 V FETs;
* STM32G473RCT6;
* the v1 feature set;
* an MCU-independent safety trip.

### Legend and sources

| Tag | Document (revision) | Used for |
|---|---|---|
| **DS** | TI BQ76952 data sheet SLUSE13B (Nov 2021) | AFE limits, drivers, protections |
| **TRM** | TI BQ76952 Technical Reference Manual SLUUBY2B (May 2022) | FET control, DDSG / DCHG, pre-discharge |
| **AN09** | TI SLUAA09A "Multiple FETs with the BQ769x2" (Mar 2022) | parallel FETs, CP1, PNP turn-off, reverse charge |
| **INA** | TI INA240-Q1 data sheet SBOS808E (Dec 2021) | current amplifier |
| **TPS** | TI TPS382x data sheet (2025 revision, local copy) | watchdog timing |
| **IPT** | Infineon IPT015N10N5 data sheet Rev 2.4 (2023-05-04) | main MOSFET |
| **R04** / **R01** | `docs/research/04_shunt_powerpath.md` / `01_bq76952_features.md` | earlier research, cited where reused |

* `calc` = my arithmetic. `est.` = an engineering estimate, not from a document. Neither is a measurement; every power, thermal and short-circuit figure needs a bench test.
* **Part data source.** All LCSC numbers were checked live on 2026-11-17 through the `jlcsearch.tscircuit.com` JSON API (`/components/list.json?search=…`, `/resistors/list.json`, `/capacitors/list.json`, `/headers/list.json`). Where noted, an `lcsc.com/product-detail` page was opened as well.
  * **Stock** is the jlcsearch figure on that day. "n/r" means jlcsearch returned no stock value. This is normal for JLC Basic passives. For an Extended part it may mean zero stock (see the unverified list).
  * **B/E** = JLC Basic / Extended, from the jlcsearch `is_basic` flag.
* Where a part's data sheet was **not** opened, its ratings come from the LCSC listing text and are marked "(listing)".

---

## 1. Summary of the choices

| Item | Choice | Why |
|---|---|---|
| Switch | 2 banks × **8 × Infineon IPT015N10N5** (TOLL, 100 V, 1.5 mΩ max) in **common-drain**, high side: CHG bank sources on `BAT+`, DSG bank sources on `PACK+`, all drains on `FET_MID` | Owner decision. The Infineon part is **cheaper and better stocked** on LCSC than the HUAYI part: C108964 shows 38 948 pcs at $1.34 (1+) / $0.75 (1000+); C2979263 shows 11 353 pcs at $2.38 / $1.39. It also has a full data sheet (IPT p.3–5) |
| Gate drive | BQ76952 CHG / DSG with **CP1 = 2.2 µF**; per-FET 10 Ω gate resistors; 10 MΩ gate-source per bank; 16 V gate-source zeners; a **PNP local turn-off loop per bank** (AN09 Fig 5-2) with a collector resistor `R_OFF` that sets the turn-off speed | AN09 p.6–7, p.11–12, p.14, p.21 |
| Pre-charge / pre-discharge | PDSG → P-FET IRF9540NS + **50 Ω / 100 W aluminium-housed resistor bolted to the plate**. PCHG → second IRF9540NS + 100 Ω / 50 W (populate per owner) | The existing R_PRE1 field LCSC (C463124) is **not a resistor** (it is an NCP1236 controller). A TO-263 part cannot survive pre-discharge into a shorted bus for the full 2.55 s timeout (§4) |
| Clamp | `BAT+`–`BAT-`: 4 × 5.0SMDJ60CA (5 kW) + 4 × 2.2 µF / 100 V. `PACK+`–`PACK-`: freewheel / clamp 2 × SMCJ60A + 2 × 2.2 µF / 100 V. Turn-off deliberately slowed to t_f ≈ 15–20 µs | No SM8S58A / 60A is on LCSC (search returned only 28 V and 36 V parts). The real protection is the controlled di/dt (§6) |
| Shunt | 2 × Vishay WSLP5931L2000FEA (C413492, 937 pcs) in parallel = 100 µΩ, at `BAT-` | R04 §1. TCR 125 ppm against TI's ≤ 50 ppm (DS p.75): compensate with an NTC on the shunt (owner question Q11) |
| Current sense | Separate Kelvin filters: BQ = 2 × 200 Ω per leg + 100 nF. INA240A1-Q1 (TSSOP, **C553123**) = 2 × 10 Ω per leg + 22 nF, supplied from **+3V3_A** (ratiometric with the MCU ADC) | DS p.65 and p.76; INA p.15 and p.19 |
| Fast OC trip | `ISENSE_OUT` → TLV1702-Q1 dual open-collector window (+600 A / −300 A) → **SN74AUP1G74 D-FF latch** (`OC_TRIP_N`, latched, powers up tripped, cleared only by an `OC_CLR` edge while no OC is present). STM32G473 COMP + DAC can add a firmware-set second window that can only *set* the latch | Owner: latched, MCU-independent. The BQ SCD sees the current through a 20 µs filter, so it is the backup, not the primary short-circuit trip (§7.4) |
| Gate-kill | AND logic (2 × 74LVC1G11 + 74LVC1G04) → BSS123 level shifters → **AO3407A P-FET per bank** that shorts the bank gate bus to its source through `R_OFF`. The same logic drives `AFE_DFETOFF` (BOTHOFF) from the non-AFE sources only | §8. **Always kills both banks** (body-diode rule, §8.2) |
| Heater | **Low-side (N-side) switch, heater fed from `PACK+`**, returned to `PACK-`; CSD19534Q5A (100 V) with gate drive from +12V; ≤ 5 A | Runs from the charger while CHG is blocked at < 0 °C, and the shunt reads the heater current correctly (§9.2) |
| Ext. outputs | EXT_OUT1 / EXT_OUT2 = the existing Q_POS / Q_NEG low-side channel, part corrected to SQ2318AES-T1_BE3 (C3280170). EXT_OUT1 is diode-OR-ed with the BQ FUSE pin for an MCU-independent breaker shunt-trip | §9.1 |
| Boards | **Recommended: two stacked boards.** Power board ≈ 150 × 100 mm, 4 layers, 2 oz outer, on an Al plate. Control board 160 × 100 mm, 1 oz, above it. Joined by a 2 × 15 2.54 mm board-to-board connector. Alternative: one 220 × 100 mm board | §10 |

---

## 2. ASCII block diagram

```
 BATTERY+ ══[J_BP M6 200A]══ BAT+ ═══════════════════════════════════════════════════════╗
   │                          │ ├─[D_TVS_B1..4 5.0SMDJ60CA ×4 + C_B1..4 2.2µF/100V]─► BAT-  ║
   │                          │ ├─ D_BAT1 ─R─ BQ BAT (pin 47) ;  CP1 2.2µF CP1↔BAT          ║
   │                          │ └─ Q_PDSG1 (IRF9540NS, S=BAT+, G←PDSG via 1MΩ G-S) ─ R_PRE1 50Ω/100W ─► PACK+
   │        CHG BANK (8×IPT015N10N5)                 DSG BANK (8×IPT015N10N5)              ║
   │   S=BAT+ ┌───────────────┐ D        D ┌───────────────┐ S=PACK+                       ║
   │  ════════│ Q_CHG1..8     │══ FET_MID ══│ Q_DSG1..8     │════════════ PACK+ ══[J_PP M6]══► inverter +
   │          └──┬────────────┘ (Cu bar)    └────────────┬──┘              │                ║
   │        GATE_CHG bus (10Ω/FET)               GATE_DSG bus (10Ω/FET)    ├─ R 10k ─ BQ LD (41)
   │   ┌───────┼───────────┐                ┌──────────┼────────┐        ├─ R 10k ─ BQ PACK (42)
   │   │ R_CHG 100Ω ← BQ CHG(45)            │ R_DSG 100Ω ← BQ DSG(43)     ├─[D_TVS_P1..2 SMCJ60A + C 2.2µF]─► PACK-
   │   │ Q_CHG_OFF PNP + R_OFF → BAT+       │ Q_DSG_OFF PNP + R_OFF → PACK+└─ Q_PCHG1 + R_PCHG1 100Ω → BAT+ (G←PCHG 40)
   │   │ Q_KILL_C P-FET + R_OFF → BAT+      │ Q_KILL_D P-FET + R_OFF → PACK+
   │   │ D_GZ 16V, R_GS 10MΩ                │ D_GZ 16V, R_GS 10MΩ
   │   └───────▲───────────┘                └──────────▲────────┘
   │           │ KILL (active-high, via BSS123 level shift + 1 nF speed-up)
   │           └──────────────────┬──────────────────────┘
   │                       U_KILL3 74LVC1G04 ◄── KILL_N ◄── U_KILL2 AND(AFE_DFETOFF, AFE_FLT_DSG_N, AFE_FLT_CHG_N)
   │                                                            ▲
   │                       AFE_DFETOFF ◄── U_KILL1 AND(FET_EN, OC_TRIP_N, MCU_NRST) ──► BQ DFETOFF (30) = BOTHOFF
   │
 BATTERY− ══[J_BM M6]══ BAT- (=GND_PWR star, R_NT1) ══[R_SH1 ∥ R_SH2  2×0.2 mΩ]══ PACK- ══[J_PM M6]══► inverter −
                              Kelvin a/b                         Kelvin a/b
                                │ 2×200Ω/leg → SRP/SRN (18/20), 100nF diff at the BQ   (BQ CC, SCD/OCD/OCC)
                                └ 2×10Ω/leg → 22nF → U_ISENSE1 INA240A1-Q1 (VS=+3V3_A, REF1=VS, REF2=GND)
                                                     └ ISENSE_OUT ─► MCU ADC
                                                     └ RC 1k/470pF ─► U_OCP1 TLV1702 window (2.85 V / 1.04 V)
                                                                       └─(open coll., wired-OR)─► CLR_N of U_LATCH1
                                     MCU COMP+DAC (optional) ─ BAT54-type diode ─► same CLR_N node (OC_SET_MCU_N)
                                     U_LATCH1 SN74AUP1G74: D=1, CLK=OC_CLR (edge), Q = OC_TRIP_N (latched)

 HEATER: PACK+ ─ fuse (harness) ─ J_HTR ─ heater pad ─ J_HTR ─ Q_HTR1 CSD19534Q5A (S=PACK-) ; gate +12V ← HEATER_EN
 EXT:    +12V ─ coil ─ J_EXT ─ Q_EXT1/2 SQ2318AES (S=GND_PWR) + SS34 flyback ; gate ← EXT_OUT1 (OR BQ FUSE) / EXT_OUT2
```

---

## 3. Net outline (power board unless stated)

| Net | From → to | Notes |
|---|---|---|
| `BAT+` | J_BP lug → Cu bar → sources of Q_CHG1–8; TVS / MLCC to `BAT-`; Q_PDSG1 source; R_PCHG1; collectors of Q_CHG_OFF / Q_KILL_C (through R_OFF); via a sense track and the board-to-board connector (B2B) → D_BAT1 → BQ BAT (control board) | High current. Kelvin sense take-off at the lug, not along the bar |
| `FET_MID` | All 16 drain tabs (TOLL tab = drain, IPT p.1) | One central copper island + bar. Hot node: insulated gap pad to the plate |
| `PACK+` | Sources of Q_DSG1–8 → Cu bar → J_PP lug; R_PRE1 output; Q_PCHG1 source; TVS / MLCC to `PACK-`; collectors of Q_DSG_OFF / Q_KILL_D through R_OFF; 10 kΩ → `AFE_LD`; 10 kΩ → `AFE_PACK`; heater supply | |
| `GATE_CHG` / `GATE_DSG` | Bank gate bus: 10 Ω to each FET gate; R_CHG / R_DSG 100 Ω from the BQ pin; 10 MΩ + 16 V zener to the bank source; PNP emitter; kill P-FET source | Keep the bus short, between the two rows |
| `AFE_CHG`, `AFE_DSG`, `AFE_PCHG`, `AFE_PDSG` | BQ pins 45 / 43 / 40 / 39 (control board) → B2B → gate networks | New names (§12) |
| `BAT-` | J_BM lug → shunt battery side; **single star `GND_PWR` tie (R_NT1) at the shunt battery-side Kelvin point**; BQ VSS reference | No pack current may flow in `GND_PWR` |
| `PACK-` | Shunt pack side → J_PM lug; TVS return; heater FET source | |
| `SH_P_a/b`, `SH_N_a/b` | Kelvin taps at the inner pad edge of each shunt (R04 §1.4) | Two separate tightly coupled pairs: BQ pair and INA pair |
| `ISENSE_OUT` | INA240 OUT → B2B → MCU ADC; → RC → U_OCP1 | |
| `OC_TRIP_N`, `OC_CLR`, `FET_EN`, `MCU_NRST`, `AFE_FLT_DSG_N`, `AFE_FLT_CHG_N`, `AFE_DFETOFF`, `KILL_N` | Safety logic on the power board ("safety island"), each via the B2B | §8 |
| `+3V3`, `+3V3_A`, `+12V`, `GND_PWR` | From the control board via the B2B | Loss of `+3V3` → BOTHOFF (§8.4) |

---

## 4. Power path

### 4.1 FET bank

| Parameter | Value | Source |
|---|---|---|
| V(BR)DSS | 100 V min | IPT p.4 |
| RDS(on) at 10 V | 1.3 typ / 1.5 max mΩ (150 A, 25 °C) | IPT p.4 |
| VGS(th) / plateau | 2.2–3.8 V / 4.4 V | IPT p.4 |
| VGS max | ±20 V | IPT p.3 |
| Ciss | 12 nF typ / 16 nF max | IPT p.4 |
| Qg (0–10 V) | 169 typ / 211 max nC; Qgd 34 / 51 nC | IPT p.4 |
| RthJC | 0.4 K/W max | IPT p.3 |
| EAS | 775 mJ (150 A, RGS = 25 Ω) | IPT p.3 |
| Body diode VSD | 0.85 V typ at 100 A | IPT p.5 |
| BQ rule | FET voltage ≈ 5 V DC to 10 V peak per series cell. With 11 V overdrive, VGS max must be ≥ 15 V | DS p.69 |

**Voltage margin (calc).** 58.4 V × (100 / 58.4) = 1.71×. TI's "10 V peak per cell" rule asks for 160 V at 16S (DS p.69), so **100 V does not meet TI's peak guideline**. It is acceptable only with the controlled turn-off and clamp in §6, proven by a short-circuit test. This is the owner's decision; the risk is raised as Q6 and not changed here.

**Count: 8 per bank, 16 total.** Common-drain (AN09 p.3 Fig 1-1 topology).
* The CHG bank blocks charge current.
* The DSG bank blocks discharge current. It is the bank that interrupts a short.

**Gate network per bank:**
* **Per-FET gate resistor 10 Ω.** AN09 p.8 uses 51 Ω per gate to stop oscillation between parallel FETs. 10 Ω is chosen because the bank speed is set by `R_OFF` (below). Raise it to 22–51 Ω if ringing is seen.
* **R_CHG / R_DSG = 100 Ω** from the BQ pin to the bus. This is the minimum TI recommends (AN09 p.14 for CHG, p.26 for DSG).
* **Gate-source 10 MΩ per bank** (AN09 p.14, p.25: about 1.1 µA load). With 2 banks plus leakage the total is < 5 µA (est.), against the ≈ 40 µA the pump can hold at 10 V (AN09 p.14).
* **Gate-source zener 16 V**, 2 per bank, one at each end of the row (AN09 Fig 1-1 uses 16 V D2 / D5). It clamps +16 V and −0.7 V. This matters on DSG, where `PACK+` swings.
* **PNP turn-off loop** (AN09 Fig 5-2 p.9; result Fig 6-10 / 6-12 p.11–12, Fig 8-17 p.21):
  * emitter = gate bus, base = BQ-pin side of R_CHG / R_DSG, collector → `R_OFF` → bank source;
  * the PNP turns on when the pin pulls below the bus;
  * **BAS21 clamp across B–E**, because VEBO of the MMBT5401 is 5 V (listing) and the R_G drop at turn-on must not reverse-break the junction.
  * `R_OFF` (start at 22 Ω, 1206) sets the bank turn-off current, and so di/dt (§6). AN09 p.13 names this resistor (R35) as the speed adjuster but does not characterise it, so it must be tuned on the bench.
* **Reverse-charge clamp** (AN09 §2–3 p.4–5; Q6 circuit): footprint only, DNP by default (Q12).

**CP1 sizing (calc, AN09 Eq. 2 p.7).**
* Equivalent gate capacitance per FET = Qg / VGS = 169 nC / 10 V = 16.9 nF typ (21 nF max).
* For 16 FETs switched together: 270 nF typ / 338 nF max.
* V2 = 11 V × 2.2 / (2.2 + 0.27) = **9.8 V typ** (9.5 V max).
* With 470 nF it would be 11 × 0.47 / 0.74 = 7.0 V, which is too low.
* **Choose 2.2 µF**, the maximum allowed: 100–2200 nF (DS p.20) and "larger than 2.2 µF not recommended" (AN09 p.6). This matches TI's 400 nF + 2.2 µF → 9 V example (DS p.65).
* Turning the banks on one after the other (PDSG then DSG, as the BQ does in PREDISCHARGE mode, DS p.45) halves the droop.
* CP1 is limited to 85 V (DS p.9), and BAT + 13 V = 71.4 V at 58.4 V, so it is OK (calc).
* Use a 50 V X7R 0805 (CC0805KKX7R9BB225) for DC-bias margin. It sits on the control board at the BQ.

**Timing of the BQ drivers (DS p.20, at CL = 20 nF):**
* tON 21–40 µs.
* DSG off 2–20 µs.
* CHG off 46–65 µs.
* The DSG turn-off pulses toward LD for ≈ 100–200 µs and then relies on the gate-source resistor (DS p.72). With 8 FETs and no PNP the turn-off is slow and "should be avoided" (AN09 p.19), which is why the PNP loop is mandatory.

### 4.2 Pre-discharge (PDSG) and pre-charge (PCHG)

**PDSG drive.**
* Output is max(VLD, VBAT) − 7.47…9.7 V, and it sinks only 30 µA (DS p.12). So the P-FET gate is about −8.4 V, inside the ±20 V rating of a standard P-FET.
* Use **1 MΩ gate-source** (DS p.45: "1 MΩ or larger").
* Topology: Q_PDSG1 source on `BAT+`, drain → R_PRE1 → `PACK+`.

**Sequence.** With PREDISCHARGE enabled, the BQ turns PDSG on first, then DSG on, then PDSG off (DS p.45; TRM p.35). Exit happens when LD is within *Predischarge Stop Delta* of the top of stack (10–2550 mV, checked every 250 ms) or on *Predischarge Timeout* (10 ms–2.55 s). **On timeout the device turns DSG on anyway** (TRM p.169).

**Sizing for the inverter DC-link capacitance. C_bus is an ASSUMPTION of 2–10 mF; the owner must give the real value (Q1).** All rows calc, V = 58.4 V, R = 50 Ω:

| C_bus | τ = RC | Time to ΔV ≤ 2.5 V = τ·ln(58.4/2.5) | Energy into R = ½CV² | Peak I / peak P |
|---|---|---|---|---|
| 2 mF | 0.10 s | 0.32 s | 3.4 J | 1.17 A / 68 W |
| 5 mF | 0.25 s | 0.79 s | 8.5 J | 1.17 A / 68 W |
| 10 mF | 0.50 s | 1.58 s | 17.1 J | 1.17 A / 68 W |

**Settings.**
* Predischarge Timeout = **2.55 s** (255 × 10 ms, the maximum).
* Stop Delta = **2.5 V**.
* A 10 mF bus completes in 1.58 s, inside the timeout (calc).
* The residual 2.5 V step at DSG-on puts ½ × 10 mF × 2.5² = 31 mJ into the bank, which is negligible (calc).

**Two hazards that set the resistor:**
1. **Short on the bus during pre-discharge.** The resistor sees 68 W until the timeout, then DSG turns on into the short and SCD / the OC latch trips.
   * Energy = 68 W × 2.55 s = **174 J per attempt** (calc).
   * A TO-263 thick-film part (the PWR263S family) cannot take this. Its pulse curve was not read, and LCSC shows PWR263S-35-50R0F (C1356480) with no stock.
   * → **Use an aluminium-housed resistor bolted to the Al plate.** The live part is **HoRX-100W-50R-5% (C2985693, 100 W, 9 pcs, Extended)**. Stock is low, so the owner must accept a consigned or equivalent part (for example any 50 Ω, ≥ 50 W aluminium-housed resistor).
   * Firmware must abort (`FET_EN` low) if `PACK+` has not risen by a set amount after 200 ms, and must limit retries.
   * Use the SCDL latch (TRM p.39–42, via R01) so time-based SCD recovery cannot loop.
2. **Inverter standby load during pre-discharge.** A load of I_sb leaves ΔV = I_sb × 50 Ω across the resistor.
   * At 0.2 A that is 10 V, so Stop Delta is never reached. On timeout DSG closes onto a 10 V step: 10 V / (≈ 5 mΩ loop) ≈ 2 kA inrush, which trips SCD.
   * **The owner must state the inverter's input current before its DC link is up (Q1).** If it is > 0.05 A, use 25 Ω (2 resistors in parallel; peak 2.3 A / 136 W) or an inverter-side enable.

**PCHG (pre-charge for deeply discharged cells).**
* Topology: Q_PCHG1 source on `PACK+`, drain → R_PCHG1 → `BAT+`. Gate from PCHG = max(VPACK, VBAT) − 8.4 V (DS p.12), 1 MΩ gate-source.
* With **100 Ω**: (58.4 − 32 V) / 100 Ω = 0.26 A and 7.0 W at 2.0 V/cell (calc), falling to 0.18 A / 3.4 W at 2.5 V/cell.
* R_PCHG1 = RX24/50W-100Ω±1% (C49375386, 13 pcs) on the plate.
* PRECHARGE mode runs while the minimum cell is below *Precharge Start Voltage* (TRM p.35, p.169).
* **The PCHG path is outside the hardware kill** on purpose: it is the recovery-charge route after a hardware CUV (§8.2). Populate per Q8.

### 4.3 TVS, snubber, LD / PACK / BAT connections

* **Battery side** (`BAT+`–`BAT-`, at the CHG-bank input, < 20 mm loop):
  * **4 × 5.0SMDJ60CA**: 60 V standoff, VBR 66.7 V, Vc 96.8 V at 51.7 A, 5 kW (listing).
  * 4 × 2.2 µF / 100 V X7R 1210 (CL32B225KCJSNNE).
  * Bidirectional is fine here.
* **Pack side** (`PACK+`–`PACK-`):
  * 2 × SMCJ60A, unidirectional, cathode on `PACK+`. Forward conduction is the **freewheel path** for the load-cable inductance when DSG opens. Without it `PACK+` swings negative and the DSG bank sees VBAT + |V_PACK| (AN09 p.4, p.24).
  * 2 × 2.2 µF / 100 V.
  * The freewheel peak current can be ≈ 0.8 kA for ≈ 0.3 ms (calc in §6). The SMC IFSM limits were not read, so a **power-diode footprint** (≥ 100 V, TO-277 / D2PAK class, part not chosen) sits in parallel. Decide after the short-circuit test.
* **Optional RC snubber** across each bank (drain to source): 10 Ω + 100 nF / 100 V, DNP, tuned on the bench.
* **LD**: 10 kΩ (1206) to `PACK+` (DS p.72; AN09 p.5).
* **PACK**: 10 kΩ to `PACK+` (DS p.65).
* Each of LD and PACK has a BAS21 from VSS (anode) to the pin (cathode), so they are not driven below VSS (AN09 p.4: D6 / D8).
* **BAT**: series diode + R + C, with the diode not shared with the REG0 NPN collector diode (DS p.64, p.75 §17). C ≥ 1 µF (AN09 p.15). This belongs to the AFE part, but the `BAT+` sense comes over the B2B from the lug-side Kelvin point.
* **SHUTDOWN / no supply**: the 10 MΩ gate-source resistors and zeners hold both banks off. TI notes that the CHG pin may fall to VSS in SHUTDOWN, while the gate-source zener and resistor hold the gate at the source (AN09 p.14).

### 4.4 Losses at 200 A (calc; hot factor est.)

Basis:
* RDS(on) max 1.5 mΩ × 1.6 hot factor at Tj ≈ 100 °C = 2.4 mΩ. **The factor 1.6 is est.; IPT's RDS(on)-vs-Tj diagram exists, but it was not read numerically.**
* Typical: 1.3 mΩ × 1.5 = 1.95 mΩ.
* 8 per bank, 2 banks in series, 10 % current imbalance on the worst FET.

| Item | Typ | Worst | Notes |
|---|---|---|---|
| FETs, 16 × (25 A)² × R | 16 × 625 × 1.95 mΩ = **19.5 W** | 16 × 625 × 2.4 mΩ = **24.0 W** | worst single FET (27.5 A)² × 2.4 mΩ = 1.8 W |
| Shunt, 200² × 100 µΩ | 4.0 W | 4.4 W (+10 % tolerance / heating) | 2 W per part (10 W rating each) |
| Cu bars 10 × 3 mm, ≈ 3 × 100 mm path | 3 × 2.3 W = 6.9 W | — | ρ_Cu 1.72 µΩ·cm, 30 mm² → 57 µΩ / 100 mm |
| PCB pours + lug contacts (4 × ≈ 20–30 µΩ est.) | 3 W | 6 W | est. |
| **Total** | **≈ 33 W** | **≈ 41 W** | R04 gave 25–35 W with fewer copper terms |

### 4.5 Thermal approach (est.)

* **Path:** TOLL tab → `FET_MID` 2 oz pour → filled thermal-via field (≈ 50 × 0.3 mm vias under each tab) → bottom 2 oz → **1.0 mm insulating gap pad (≥ 3 W/m·K)** → aluminium base plate / enclosure.
  * `FET_MID`, `BAT+` and `PACK+` are live, so the pad must insulate; 58 V is trivial for any silicone pad.
* **Per FET (est.):** RthJC 0.4 (IPT p.3) + vias ≈ 4 K/W + pad ≈ 3 K/W ≈ **7–8 K/W** junction-to-plate. At 1.8 W that is +14 K.
* **System (est.):** with 40 °C ambient and Tj ≤ 100 °C (the basis of the hot factor), the plate must stay ≤ 70 °C. So plate-to-ambient ≤ 30 K / 41 W ≈ **0.75 K/W**. That needs a finned aluminium case (the Daly approach) or bolting to the ESS cabinet wall. **Owner question Q14:** who provides the heatsink, and what is the ambient?
* **Placement:**
  * Shunts ≥ 15 mm from the FET rows on their own copper island, with the shunt NTC against them (R04 §1.3 / 1.5).
  * One NTC on `FET_MID` (`NTC_FET`) for OTF (DS / TRM via R01 1c).
  * R_PRE1 / R_PCHG1 bolted to the plate, away from the shunt.

### 4.6 Copper, bars, lugs, stack-up

* **Power board stack-up:** 4 layers, **2 oz outer / 1 oz inner** (JLC capability, R04 §1.5). `BAT+`, `FET_MID` and `PACK+` are poured on all 4 layers and stitched.
  * Sheet resistance of all four layers in parallel ≈ 0.082 mΩ/□ (R04 §1.5). That is not enough alone, hence the bars.
* **Bars:** tinned Cu 10 × 3 mm on mask-free strips: `BAT+` row, `FET_MID` centre and `PACK+` row; plus 10 × 3 mm from the `BAT-` lug → shunts → `PACK-` lug. Hand- or selective-soldered after PCBA (JLC SMT does not place bars, assumption from R04).
* **Lugs:** 4 × **XFCN T68160200-1400** (C45384693, 4 674 pcs, Extended): **200 A, M6, 8 legs, 14 mm high**. Data from the `lcsc.com/product-detail/C45384693.html` listing.
  * There is one per node, with a footprint for a second in parallel if the 200 A rating has no stated temperature-rise basis (unverified).
  * No M8 PCB terminal was found on LCSC. Würth REDCUBE M8 (press-fit) is DigiKey-only (R04). Q5.

### 4.7 Short-circuit energy and SOA — see §6

---

## 5. On-board shunt and current sense

### 5.1 Shunt

* **R_SH1 ∥ R_SH2 = 2 × WSLP5931L2000FEA** (C413492, 937 pcs, Extended; listing: 0.2 mΩ, 1 %, ±125 ppm/°C, 10 W, 5931).
  * Total 100 µΩ.
  * 20 mV at 200 A and 50 mV at 500 A, against the ±200 mV CC range (DS p.15; R04 §1.2).
  * 4 W at 200 A (calc).
* **"Better part" check.** No ≤ 50 ppm, ≤ 0.2 mΩ SMD shunt with LCSC stock was found (R04 §1.3; Isabellenhütte BVR is not on LCSC).
  * TI asks for ≤ 50 ppm (DS p.75). The residual error is 125 ppm × 30–40 K ≈ 0.4–0.5 % (R04, calc), to be compensated with `NTC_SHUNT`. Q11.
* **500 A pulse:** 12.5 W per part, above the 10 W continuous rating. The pulse curve is unverified. The owner must give the duration (Q2).
* **Polarity** (current through the shunt in discharge flows `PACK-` → `BAT-`):
  * BQ: SRP = battery side, so charge reads positive (DS pin table, via R04 §1.4).
  * INA: IN+ = `PACK-` side, so **discharge reads positive** (ISENSE_OUT above mid-scale).

### 5.2 Kelvin filters (two separate networks)

| Network | Parts | τ (calc) | Source |
|---|---|---|---|
| BQ SRP / SRN | 2 × 200 Ω per leg (one per shunt tap, averaging) = 100 Ω effective + **100 nF** differential at the BQ (opt. 100 pF diff; opt. 100 nF each to VSS) | differential (100 + 100) Ω × 100 nF = **20 µs** | DS p.65, p.76 ("filter at the device, traces in parallel") |
| INA240 IN+ / IN− | 2 × 10 Ω per leg = 5 Ω effective + **22 nF** differential at the INA | (5 + 5) Ω × 22 nF = 0.22 µs (≈ 720 kHz, above the INA 400 kHz BW) | INA p.19: series R ≤ 10 Ω |

* Route the two pairs as separately coupled pairs from the taps. Lay out the averaging resistors symmetrically (R04 §1.4).
* The 20 µs BQ filter matters for SCD timing (§7.4).

### 5.3 INA240A1-Q1

* **Part: INA240A1QPWRQ1, TSSOP-8, C553123** (1 913 pcs, Extended). The SOIC Q1 part C2057377 returned no stock today.
* Gain 20 V/V (INA p.3, via R04).
* Supply: VS = **+3V3_A** (2.7–5.5 V).
* Mid-supply output by REF1 = VS, REF2 = GND, so the output is ratiometric at VS/2 (INA p.15 §8.4.3.2). Using the MCU's analog rail makes ISENSE_OUT ratiometric to the ADC reference and to the comparator thresholds. Q13 if the owner prefers `+3V3`.
* **Transfer (calc):** ISENSE_OUT = 1.65 V + 20 × 100 µΩ × I = **1.65 V + 2.0 mV/A**.
  * Linear band GND + 50 mV … VS − 200 mV (INA p.5 gain-error conditions) → **−800 A … +725 A**.
  * 12-bit ADC → 0.40 A per LSB.
* Gain error 0.20 % max (INA p.5). BW 400 kHz, settling 9.6 µs, slew 2 V/µs (INA p.6).

### 5.4 BQ76952 protection settings with 100 µΩ (proposal; thresholds calc from DS p.22 accuracy)

| Protection | Setting | Nominal | Worst-case window | Delay | Comment |
|---|---|---|---|---|---|
| SCD | 80 mV | 800 A | 680–920 A (±15 %) | "fastest" (8 µs at 3 mV, 600 ns at 25 mV overdrive) | Backup to the OC latch (§7.4). Use SCDL latch |
| OCD1 | 56 mV | 560 A | 510–610 A (±5 mV) | per the 500 A pulse length (Q2), e.g. 10–20 ms | Lets 500 A pulses pass |
| OCD2 | 30 mV | 300 A | 260–340 A (±4 mV) | 0.4 s | |
| OCD3 (CC1, firmware-free AFE tier) | 210 A | 210 A | CC accuracy | 10–60 s | TRM via R01 |
| **OCC** | **26 mV** | 260 A | **220–300 A** (±4 mV) | 100 ms | **R04's 22 mV is too low:** 22 − 4 = 18 mV = 180 A, which would trip a 200 A charge |
| Units / gain | USER_AMPS = 100 mA; CC Gain = 74.77 | | | | R01 §4 (TRM p.20, p.127) |
| Fast-turn-off masks | DSG FET Protections A = 0x80 or 0xE4; CHG FET Protections A = 0x18 or 0x98 | | | | Other values delay turn-off by up to 250 ms / 1 s (TRM p.34) |

### 5.5 Bidirectional latched OC window (MCU-independent)

* **Input.** ISENSE_OUT → RC 1 kΩ / 470 pF (τ 0.47 µs, noise blanking) → both inputs of **TLV1702AQDGKRQ1** (C130036, 1 795 pcs, Extended).
  * Listing: dual, rail-to-rail input, open-collector, 2.2–36 V, 560 ns propagation. Its data sheet was not read.
  * Supply +3V3_A.
* **Thresholds** from one divider on +3V3_A (ratiometric with the INA):
  * R1 13.7 k / R2 54.9 k / R3 31.6 k (E96, 0.1 % preferred).
  * V_HI = 3.3 × 86.5 / 100.2 = **2.849 V → +599 A** (discharge).
  * V_LO = 3.3 × 31.6 / 100.2 = **1.041 V → −305 A** (charge).
  * All calc. Owner to confirm the window (Q3).
  * Error budget (calc): shunt 1 % + TCR 0.6 % + INA 0.2 % + divider 0.2 % ≈ **±2 % ≈ ±12 A** at 600 A.
* **Latch: SN74AUP1G74DCUR** (C140267, 17 455 pcs, Extended). The 74LVC1G74 variants (C70285, C503431, C548408) appear on LCSC but returned no stock.
  * Comparator outputs wired-OR, pulled up 10 k to +3V3 → **CLR_N**, with 100 nF to GND on CLR_N. So **CLR_N is held low for ≈ 1 ms at power-up → the latch powers up tripped** (fail-safe and self-test).
  * Q (push-pull) = **`OC_TRIP_N`** (low = tripped).
  * D = VCC; CLK = **`OC_CLR`** (MCU, 100 k pull-down). A rising edge sets Q = 1 only if CLR_N is high, because CLR dominates. So the latch **cannot be cleared while the over-current persists**.
  * PRE_N tied high.
* **Optional firmware tier:** STM32G473 COMPx (INP = ISENSE_OUT pin, INM = internal DACx) → COMPx_OUT pin → small Schottky (cathode to the pin) → the same CLR_N node (`OC_SET_MCU_N`).
  * It can only *set* the latch, never block it. While the MCU is in reset the pin is Hi-Z, so it causes no false trip.
  * Use it for a tighter, adjustable charge-side or derated limit.
  * **G473 COMP / DAC pin mapping not verified** (ST DS not opened; MCU part of the architecture).
* **Outputs of `OC_TRIP_N`:** into U_KILL1 (§8); to an MCU EXTI; to a fault LED via the I/O expander (MCU part).

---

## 6. Short-circuit energy and SOA check (all calc / est.; must be proven by test)

**Assumptions (est.):**
* Prospective short ≈ 58 V / 7 mΩ ≈ **8 kA** (R04 §2.5).
* Battery-side loop L_bat ≈ 0.5 µH (cells, busbars and cable to the BMS). Load-side L_load ≈ 1.0 µH.
* Initial di/dt = 58.4 V / 1.5 µH ≈ **39 A/µs**.

**Current at turn-off:**

| Path | Trip point | Delay to gate at plateau | I at start of current fall |
|---|---|---|---|
| OC latch (primary) | 600 A | ≈ 1.5 µs detect + 0.2 µs kill-FET + ≈ 2.2 µs gate 11 V → 4.4 V (≈ 0.66 µC at ≈ 0.3 A via R_OFF 22 Ω) | 600 + 39 × 3.9 ≈ **0.75 kA** (0.9 kA with margin) |
| BQ SCD only (latch failed) | 800 A ± 15 % on the **filtered** signal | + 20 µs filter lag + DSG pin / PNP ≈ 2–5 µs | 800 + 39 × 25 ≈ **1.6–1.8 kA** |

**Turn-off design rule.** The current-fall time t_f is set by `R_OFF` (and the DNP gate-source C). The battery-side overshoot is V = 58.4 V + L_bat · I / t_f.

| I_off | t_f | Overshoot at `BAT+` | ½·L_bat·I² (to TVS + FETs) | FET linear energy ≈ ½ · V_DS · I · t_f (all 8 DSG FETs) | Per FET (2× imbalance) |
|---|---|---|---|---|---|
| 0.8 kA | 5 µs | 58 + 80 = 138 V → TVS clamps, FETs avalanche | 0.16 J | — | **unsafe** |
| 0.8 kA | 15 µs | 58 + 27 = **85 V** | 0.16 J | ½ × 85 × 800 × 15 µs = 0.51 J | ≈ 130 mJ |
| 0.8 kA | 20 µs | 58 + 20 = **78 V** | 0.16 J | 0.62 J | ≈ 155 mJ |
| 1.7 kA (SCD-only) | 20 µs | 58 + 42 = 100 V | 0.72 J | 1.4 J | ≈ 350 mJ |

* **Target t_f = 15–20 µs.** The overshoot then stays below the 5.0SMDJ60CA knee region (VBR min 66.7 V, Vc 96.8 V at 51.7 A, listing), so the TVS array takes only a part of the current.
  * Per-FET energy of 130–155 mJ is far below EAS 775 mJ (IPT p.3). EAS is an avalanche rating, not linear SOA, so it is only an indication of thermal capacity.
  * **The SOA (IPT Diagram 3, p.6) must be read at 80–100 V for 10–20 µs pulses.** It is a graph and was not read numerically (unverified). The check needed: ≈ 100–200 A per FET at 80–90 V for 15–20 µs.
* **Load side (calc).** When DSG opens, L_load carries ≈ 0.8 kA through the `PACK-`→`PACK+` freewheel path (SMCJ60A forward + power-diode footprint). It decays with τ ≈ L / R ≈ 1 µH / 3 mΩ ≈ 0.33 ms, so I²t ≈ 0.8k² × 0.33 ms / 2 ≈ 105 A²s. The diode surge rating was not read (unverified).
* **SCD-only case** (OC latch failed): 1.7 kA at 100 V is at the limit of a 100 V part. This is a double-fault case; it is the main reason Q6 exists.
* **Bench test (mandatory):** a short with a defined 1–2 µH loop at 58 V. Measure I_off, V_DS, V_BAT+ and t_f. Iterate `R_OFF` (10–100 Ω), the per-FET R_G and the snubber. Run it with the OC latch enabled and disabled (SCD-only).

---

## 7. Timing chains (µs; calc / est. except where cited)

### 7.1 OC latch → hardware kill (primary, MCU-independent)

| Step | Time | Source |
|---|---|---|
| INA240 output lag at 400 kHz BW | ≈ 0.4 µs | INA p.6 (BW), est. |
| RC 1 k / 470 pF | 0.47 µs | calc |
| TLV1702 propagation | 0.56 µs | listing (DS not read) |
| CLR_N → Q (AUP1G74) + 74LVC1G11 → 74LVC1G04 | ≈ 0.03 µs | est. (listing 13.5 ns @ 4.5 V for the LVC1G11; slower at 3.3 V) |
| BSS123 on + 1 nF speed-up → AO3407A on | ≈ 0.2 µs | est. |
| Gate bus 11 V → plateau 4.4 V through R_OFF 22 Ω | ≈ 2.2 µs | calc (IPT Qg) |
| **Current begins to fall** | **≈ 3.9 µs** after crossing 600 A | calc |
| Current fall (designed) | 15–20 µs | §6 |
| **Interrupted** | **≈ 20–25 µs** | calc |
| In parallel: `AFE_DFETOFF` low → BQ turns off CHG / DSG / PCHG / PDSG | not specified | **unverified** (no DFETOFF response time in DS / TRM) |

### 7.2 BQ SCD path (autonomous, backup)

Filter lag ≈ 20 µs (calc) + SCD detect 0.6–8 µs (DS p.22) + DSG fall 2–20 µs at 20 nF (DS p.20; with the PNP, set by R_OFF) → **≈ 25–45 µs** to start of fall.

### 7.3 Other kill sources

| Source | Chain | Time |
|---|---|---|
| `FET_EN` low (firmware) | GPIO → U_KILL1 → U_KILL2 → U_KILL3 → kill FETs | ≈ 2.5 µs to plateau (calc) |
| MCU watchdog expiry | TPS3823 timeout **0.9 / 1.6 / 2.5 s** (min / typ / max, TPS p.7) → RESET low (td ≈ 200 ms) → `MCU_NRST` low → kill; FET_EN goes Hi-Z → 100 k pull-down → kill | ≈ 2.5 µs after RESET |
| AFE fault (DDSG / DCHG) | BQ decision (immediate with the Prot A values above, TRM p.34) → DDSG / DCHG low → U_KILL2 → kill | DDSG / DCHG delay **unverified** (R01 §9); the BQ's own driver acts at the same time |
| BQ HWD (host watchdog) | config, 2–5 s → FETs off → DDSG / DCHG | TRM via R01 3e |

### 7.4 Why the latch, not SCD, is the primary short-circuit trip

TI's 100 Ω / 100 nF CC filter (DS p.65, p.76) delays SRP–SRN by ≈ 20 µs differential (calc). At 39 A/µs a "800 A" SCD setting therefore trips at ≈ 1.6 kA of real current. Reducing the BQ filter would hurt CC accuracy. The INA path has ≈ 1.5 µs total lag, so it sets the interrupt current (≈ 0.75 kA). This is the engineering argument for keeping the INA + latch (R04 §3.2).

---

## 8. Independent gate-kill

### 8.1 Logic (powered from +3V3; all inputs active-low = "OK when high")

```
FET_EN (100k PD) ──┐
OC_TRIP_N ─────────┼─ U_KILL1 74LVC1G11 (AND3) ── AFE_DFETOFF ──► BQ DFETOFF pin 30 (BOTHOFF, active-low)
MCU_NRST ──────────┘                                  │
AFE_FLT_DSG_N (100k PD) ──┐                           │
AFE_FLT_CHG_N (100k PD) ──┼─ U_KILL2 74LVC1G11 (AND3) ┘── KILL_N ──► MCU readback
                          │                                 │
                          └─────────────────────── U_KILL3 74LVC1G04 ── KILL (active-high)
                                                                 │
              ┌──────────────────────────────────────────────────┴───────────────────┐
     Q_KLS_C BSS123 (G←KILL, 100Ω; S=GND_PWR)                         Q_KLS_D BSS123 (same)
        D ─ BAS21 ─ 47k ∥ 1nF/100V ─► gate of Q_KILL_C AO3407A            D ─ BAS21 ─ 47k ∥ 1nF ─► gate of Q_KILL_D
        Q_KILL_C: S = GATE_CHG, D = R_OFF → BAT+;                         Q_KILL_D: S = GATE_DSG, D = R_OFF → PACK+;
        100k + BZT52C16S (16 V) G-S                                       100k + 16 V zener G-S
```

* **Action.** The kill P-FET shorts the bank gate bus to the bank source through `R_OFF` (same value as the PNP loop, so the BQ path and the kill path give the same di/dt).
  * When the kill is released, it draws no current from the charge pump (BSS123 off; only leakage through 147 kΩ).
  * When active, the steady current is ≈ 58 V / 47 k ≈ 1.2 mA per bank, 72 mW in the 47 k (calc; use a 0805 or 1206 rated ≥ 150 V).
  * The 1 nF capacitor gives a ≈ 70 nC kick that charges the AO3407A gate in < 0.2 µs (calc).
  * The BAS21 blocks reverse current if `PACK+` swings below `GND_PWR`.
* **Overriding a live BQ driver.** The pump supplies only ≈ 200 µA into a short and the DSG pin a few mA when pulled down (AN09 p.14, p.25, Fig 9-2). A 4 A-class P-FET wins easily.
  * AN09 warns that pulling one driver also droops the other through the shared CP1, leaving a FET in source-follower mode. That is a second reason to **always kill both banks together and also assert DFETOFF / BOTHOFF** (AN09 p.14, p.25).
* **DFETOFF uses only the non-AFE sources** (FET_EN, OC_TRIP_N, MCU_NRST).
  * Feeding DDSG / DCHG back into DFETOFF could deadlock: BOTHOFF would keep a fault output asserted after the AFE fault clears (inferred from TRM p.34 / p.60).
  * BOTHOFF disables CHG, PCHG, DSG and PDSG (DS p.48).
  * DFETOFF polarity = active-low with the pin's internal weak pull-down enabled, so a Hi-Z logic output also asserts it (TRM p.57–58 OPT bits). The TI example also uses active-low (DS p.68).
* **DDSG / DCHG configuration** (TRM p.56–61):
  * polarity active-low (OPT[5] = 1);
  * drive high from REG1 (OPT[3] = 1, OPT[1] = 1);
  * Hi-Z in SHUTDOWN, read as a fault by the 100 k pull-down.
  * They are fault signals, not FET-state mirrors: "faults that would normally cause the DSG driver to be disabled" (TRM p.60).
  * Firmware must **not** use DSG_PDSG_OFF, CHG_PCHG_OFF or FET_CONTROL while DDSG / DCHG mode is set (TRM p.34). Use ALL_FETS_OFF / ON and the pins.

### 8.2 Body-diode rule (why the kill is never single-direction)

In series-FET mode, the BQ turns the "off" FET back on when significant current flows through its body diode (TRM p.33; DS p.45). TI names the CUV case explicitly: DSG off, CHG on, charging current → DSG must turn on.

DDSG stays asserted while the fault persists (TRM p.60). A DSG-only hardware kill would therefore hold the DSG bank off during recovery charging and force 200 A through its body diodes: ≈ 0.85 V × 200 A ≈ **170 W** (IPT p.5 VSD; calc). That destroys the bank.

**Rule: every hardware kill turns off both banks.** Consequences:
* **COV / OCC (DCHG) also blocks discharge while asserted.** This is acceptable only if the BQ hardware limits sit *above* the firmware limits, so they act only when firmware charge control has failed. Example: firmware OV 3.60 V / BQ COV 3.75 V; firmware UV 2.80 V / BQ CUV 2.50 V. Q7.
* **After a hardware CUV the pack can still be recovery-charged through PCHG**, which is outside the kill (§4.2).

### 8.3 Fail-safe states

| Condition | FET_EN | OC_TRIP_N | MCU_NRST | DDSG / DCHG | Result |
|---|---|---|---|---|---|
| MCU in reset / watchdog reset | Hi-Z → 100 k PD → 0 | held (latched state kept) | 0 | as AFE | **Both banks killed + BOTHOFF** |
| MCU unpowered, +3V3 lost | 0 | latch unpowered → 0 | 0 | REG1-driven, may be high | Logic outputs 0 → **DFETOFF asserted (BOTHOFF, AFE acts)**. The hardware kill FETs are **not** driven (BSS123 gate = 0), so protection relies on the AFE in this state. LVC / AUP inputs are Ioff-tolerant of REG1 high (listing "overvoltage-tolerant inputs") |
| AFE in SHUTDOWN | as MCU | — | — | Hi-Z → PD → fault | Killed. The AFE drivers are off too; FETs held off by 10 MΩ + zeners |
| AFE DEEPSLEEP | — | — | — | active | FETs disabled by the AFE (DS p.51) |
| Board-to-board connector unplugged (stack option) | PD on the power board → 0 | PD | PD | PD | Killed; DFETOFF lost with the B2B → its internal pull-down (TRM p.58) → BOTHOFF |
| Power-up | 0 until firmware | **tripped** (CLR_N RC) | 0 during POR | per AFE (TI default FET_EN = 0, FET Test mode, R01 §0.1) | All off until firmware self-test clears the latch and sets FET_EN |

**Rule for the power-tree part:** `+3V3` must stay on whenever the FETs may be on (sleep with FETs on included). Otherwise BOTHOFF drops the bus.

### 8.4 Reset path

1. **OC latch:** firmware checks that ISENSE_OUT is back inside the window, then gives a rising edge on `OC_CLR`. CLR dominates, so the clear is ignored while an over-current persists. Firmware limits retries (e.g. 3, then lockout until the button or an app command).
2. **AFE faults:** per the AFE recovery configuration (autonomous hysteresis for COV / CUV / temperature; SCDL / OCDL latched with LD-detect, time or command recovery; TRM via R01 1d).
3. **FET_EN:** firmware.
4. **Re-close:** when the AFE re-enables DSG it goes through PREDISCHARGE first (DS p.45), so re-closing into a short is resistor-limited.

---

## 9. Optional outputs

### 9.1 EXT_OUT1 / EXT_OUT2 (external contactor or breaker shunt-trip)

* Reuse the Q_POS1 / Q_NEG1 low-side channel: N-FET source on `GND_PWR`, drain to a 2-pin terminal, coil from `+12V`, SS34 flyback (C2837271, 479 217 pcs).
* **Part correction.** The project field SQ2318EY / **C148416 is a different part** (LCSC now: WSP4805, a dual P-FET, SOP-8). The live replacement is **SQ2318AES-T1_BE3 (C3280170, 8 981 pcs**; listing: 40 V, 8 A, 31 mΩ at 10 V, VGS(th) 2.5 V).
  * Its RDS(on) at a 3.3 V gate is not listed, so drive the gate at ≥ 4.5 V from a small buffer on +5V (part not chosen), or confirm the 3.3 V figure in the Vishay data sheet (unverified).
* **Symbol.** `Device:Q_NMOS` D / G / S pins do not map to SOT-23 pads 1 / 2 / 3 (PROJECT.md §8 Q4). Use a symbol with numbered pins (e.g. `Q_NMOS_GSD`: 1 = G, 2 = S, 3 = D) after checking the SQ2318AES pin-out in its data sheet.
* **EXT_OUT1 + FUSE.** The BQ FUSE pin (DS p.12, p.49–50; drives an NFET gate, PF-triggered) is diode-OR-ed (2 × BAS21) with the MCU's `EXT_OUT1` onto the EXT1 gate, with 100 k to GND. A permanent fail can then trip a DC-breaker shunt-trip coil **without the MCU**.
  * Check the FUSE pin's high level against the FET VGS (unverified: FUSE drive figures in R01 come from a garbled figure).
* **Rating:** coil current ≤ 1 A from +12V. The budget is the power-tree part's job (LM5164 class). Q10 asks the coil type.

### 9.2 Heater-pad output — choice: **N-side (low-side) switch, heater powered from `PACK+`**

| Option | For | Against |
|---|---|---|
| **N-side, from PACK+ (chosen)** | At < 0 °C, CHG is blocked (UTC) but a charger still holds `PACK+` up. The heater then warms the cells **from charger energy**, which is the purpose of an LFP heater. With DSG on, it can also self-heat from the pack. The return is `PACK-`, so pack-sourced heater current passes the shunt and is counted, while charger-sourced current is not (correct SOC). Simple N-FET referenced to `PACK-` ≈ `GND_PWR` (≤ 50 mV apart at 500 A, calc); gate from +12V | Heater harness at pack potential; needs a fuse in the harness |
| P-side high-side switch | Heater return at ground | Needs a high-side P-FET or driver at 58 V; no functional gain |
| 12 V heater from `+12V` | Low-voltage harness | 100–200 W at 12 V = 8–17 A; the 12 V buck (1 A class) cannot supply it |

* **Circuit:** `PACK+` → harness fuse (owner, e.g. 7.5 A blade) → J_HTR pin 1 → heater pad → J_HTR pin 2 → **Q_HTR1 CSD19534Q5A** (C114200, 585 pcs; listing: 100 V, 50 A, 17.6 mΩ at 6 V, SON-5×6) → `PACK-`.
  * Gate: +12V through 100 Ω via a BSS123 + MMBT5401 level stage from `HEATER_EN`, with a 10 k gate pull-down. HEATER_EN low or Hi-Z → off.
  * SS310-class 100 V flyback across the pad (C47018526, 19 932 pcs).
* **Rating:** ≤ 5 A continuous (240 W at 48 V): 5² × 17.6 mΩ = 0.44 W (calc). PWM at ≤ 1 Hz from the shared timer (MCU part).
* **Thermal safety:** the firmware thermostat uses the cell NTCs. A hardware over-temperature cut (a bimetal in the pad, or the AFE OT via KILL) is recommended (Q9).

---

## 10. Board size and mechanics

### 10.1 Recommendation: **two stacked boards** (power board below, control board above)

| Criterion | One board ≈ 220 × 100 mm | **Power board ≈ 150 × 100 + control board 160 × 100 (stacked)** |
|---|---|---|
| Footprint | 220 × 100 | **≈ 160 × 100** (Daly 164 × 66; JK / JBD 300 × 100 per R04 §4) |
| Copper | Whole board 2 oz outer: fine-pitch MCU / ESP32 / AFE on 2 oz (JLC 2 oz min track / gap not checked, unverified) | Control board stays 1 oz (cheap, fine pitch); only the power board is 2 oz |
| Thermal | Plate under the whole board; AFE / MCU share the hot board | Power board alone on the plate; control board 12–15 mm above, cooler; AFE far from 30–40 W |
| Variants | One rating | Same control board for 100 / 150 / 200 A power boards (4 / 6 / 8 FETs per bank) |
| Re-use | New outline | Keeps the existing 160 × 100 outline and its isolation slot |
| Cost / risk | 1 PCB, 1 assembly, no B2B; Kelvin and gate traces short | 2 PCBs + B2B pair; Kelvin pair and gate drives cross the connector |
| Noise | Power and analog on one board | Physical separation; a clean single `GND_PWR` tie at the shunt is easier |

**Recommendation: stack.**
* It is the most compact (≈ 160 × 100, about half the JK / JBD area).
* It keeps fine-pitch control at 1 oz.
* It isolates heat.
* It gives power variants.

The cost is a B2B connector and careful pinout. **Choose the single 220 × 100 board** if the owner wants one PCBA and a flat enclosure. The power-stage design in this part is the same for both (Q4).

### 10.2 Board-to-board connector (stack option)

2 × 15, 2.54 mm. Female **C5337168** (2.54-2*15P, Extended; listing: 2.5 A/pin). The mating male header was **not found in stock** (C56496 returned no stock): unverified.

Pin groups (est. 30 pins):
* **HV group, at one end, with a spare pin as a gap:** `AFE_CHG`, `AFE_DSG`, `AFE_PCHG`, `AFE_PDSG`, `AFE_LD`, `AFE_PACK`, `BAT_SNS`, `AFE_FUSE`.
* **Kelvin:** `SRP_K`, `SRN_K` (BQ pair, adjacent, flanked by `GND_PWR`).
* **Analog:** `ISENSE_OUT`, `NTC_FET`, `NTC_SHUNT`.
* **Logic:** `OC_TRIP_N`, `OC_CLR`, `FET_EN`, `MCU_NRST`, `AFE_FLT_DSG_N`, `AFE_FLT_CHG_N`, `AFE_DFETOFF`, `KILL_N`, `OC_SET_MCU_N`, `HEATER_EN`.
* **Rails:** `+12V`, `+3V3`, `+3V3_A`, `GND_PWR` × 3.

At 2.54 mm pitch the pad gap is ≈ 1.5 mm, which exceeds the 0.6 mm IPC-2221B B2 value for 51–100 V.

### 10.3 Lug and connector positions (power board, est. layout)

```
  y=100 ┌──────────────────────────────────────────────────────────────┐
        │ [J_BM B− M6]   BAT- bar ── R_SH1 R_SH2 ── PACK- bar  [J_PM P− M6]│
  y≈75  │   TVS_B(ret)   NTC_SHUNT  INA240 + window + latch     TVS_P(ret) │
  y≈62  │            ═══ B2B 2×15 (to control board above) ═══  kill logic │
        │  PACK+ bar ═══════ DSG sources (8 × TOLL, drains down) ═══════ │
  y≈40  │  ─────────────────── FET_MID bar / island ─────────────────── │
        │  BAT+ bar ═══════ CHG sources (8 × TOLL, drains up) ══════════ │
  y≈10  │ [J_BP B+ M6] TVS_B ×4 + MLCC          R_PRE1 / R_PCHG1 on plate [J_PP P+ M6]│
  y=0   └──────────────────────────────────────────────────────────────┘
        x=0                                                       x≈150
```

* Battery lugs on the left edge, load lugs on the right edge, so cable runs are straight.
* B+ / B− lugs 50–60 mm apart, which keeps the clamp loop short.
* M3 mounting holes at the corners plus 2 in the middle, carrying both the plate clamp and the standoffs.

### 10.4 Creepage / clearance (58.4 V max; transient ≈ 100 V at the clamp)

* **IPC-2221B Table 6-1, 51–100 V:** external uncoated conductors 0.6 mm (B2, sea level, as quoted in `instruction.md` §8). 1.5 mm is needed at > 3050 m (B3, from memory of the table, **unverified**).
* **Design rule proposed:**
  * **≥ 2.0 mm** between `BAT+` / `FET_MID` / `PACK+` and `BAT-` / `PACK-` / `GND_PWR` copper on outer layers;
  * ≥ 1.0 mm between HV-group B2B pins;
  * ≥ 4 mm around lug bodies;
  * inner layers ≥ 0.5 mm.
  * This margin covers B3 (high altitude), conductive dust in ESS cabinets, and IEC 60664-1 pollution degree 2 (≈ 1.25 mm at 63 V for material group III, **unverified**, from memory).
* **Note:** across an open FET pair, `PACK+` to `BAT+` can reach 58.4 V in normal use and ≈ 117 V if a parallel pack is connected reversed. That exceeds the 100 V FET rating anyway (Q12). Use ≥ 2 mm there too.
* Conformal coating would allow the B4 values, but is not assumed.

---

## 11. Parts table

LCSC numbers verified live on 2026-11-17 via `jlcsearch.tscircuit.com` (JSON API) unless the Source column says otherwise. "listing" = ratings from the LCSC description, data sheet not read.

| Ref-to-be | Function | Part | LCSC | Stock | B/E | Key rating | Source |
|---|---|---|---|---|---|---|---|
| Q_CHG1–8, Q_DSG1–8 | Main FET banks | Infineon IPT015N10N5 (HSOF-8 / TOLL) | C108964 | 38 948 | E | 100 V, 1.5 mΩ max, Qg 169 nC, RthJC 0.4 K/W | jlcsearch; IPT Rev 2.4 p.3–5 |
| (alt.) | Second source | HUAYI HYG015N10NS1TA (TOLL-8L) | C2979263 | 11 353 | E | 100 V, 1.5 mΩ @10 V, 205 nC (listing) | jlcsearch |
| R_G_C1–8, R_G_D1–8 | Per-FET gate R | 10 Ω 1 % 0603 (0603WAF100JT5E) | C22859 | n/r | B | 0.1 W | jlcsearch resistors |
| R_CHG, R_DSG | Pin series R | 100 Ω 1 % 0603 | C22775 | n/r | B | ≥ 100 Ω per AN09 p.14 | jlcsearch |
| R_GS_C, R_GS_D | Gate-source | 10 MΩ 1 % 0603 | C7250 | n/r | B | AN09 p.14 | jlcsearch |
| D_GZ_C1/2, D_GZ_D1/2, D_KZ_C/D | Gate zeners 16 V | BZT52C16S (SOD-323) | C19077449 | 56 108 | E | 15.3–17.1 V, 200 mW (listing) | jlcsearch |
| Q_CHG_OFF, Q_DSG_OFF | PNP turn-off loop | MMBT5401 (hFE 200–300) | C8326 | 616 368 | B | 150 V, 600 mA (listing) | jlcsearch |
| D_BE_C, D_BE_D, D_KB_C/D, D_LD, D_PK, D_FUSE×2 | B-E clamp / blocking / pin diodes | BAS21 (SOT-23) | C7502725 | 154 583 | E | 200 V class (BAS21W listing) | jlcsearch |
| R_OFF_C, R_OFF_D (×2 each: PNP and kill) | Turn-off speed | 22 Ω 1 % 1206 (start value, tune) | C17958 | n/r | B | 0.25 W; pulse duty low | jlcsearch |
| C_CP1 | Charge-pump cap 2.2 µF | CC0805KKX7R9BB225 | C125847 | n/r | E | 50 V X7R | jlcsearch capacitors |
| Q_PDSG1, Q_PCHG1 | Pre-discharge / pre-charge P-FET | IRF9540NSTRLPBF (D2PAK) | C33903 | 37 014 | E | −100 V, 23 A, 117 mΩ (listing) | jlcsearch |
| R_PDSG_GS, R_PCHG_GS | P-FET gate-source 1 MΩ | 0603 1 MΩ | not looked up | — | — | DS p.45 | **unverified** |
| R_PRE1 | Pre-discharge R 50 Ω | HoRX-100W-50R-5% (Al-housed, bolt) | C2985693 | 9 | E | 100 W, 50 Ω | jlcsearch (low stock) |
| R_PCHG1 | Pre-charge R 100 Ω | RX24/50W-100Ω±1% (Al-housed) | C49375386 | 13 | E | 50 W | jlcsearch (low stock) |
| D_TVS_B1–4 | Battery-side clamp | 5.0SMDJ60CA (SMC) | C2990413 | 2 389 | E | 5 kW, VRWM 60 V, VBR 66.7 V, Vc 96.8 V @ 51.7 A (listing) | jlcsearch |
| D_TVS_P1–2 | Pack-side clamp / freewheel | SMCJ60A (DO-214AB) | C2996503 | 2 629 | E | 1.5 kW, 60 V uni (listing) | jlcsearch |
| C_B1–4, C_P1–2 | Bank MLCC 2.2 µF | CL32B225KCJSNNE (1210) | C55151 | n/r | E | 100 V X7R | jlcsearch capacitors |
| C_SNB, R_SNB | RC snubber (DNP) | 100 nF 100 V 0805 + 10 Ω 1206 | C28233 (cap) / C17958 class | n/r | B | — | jlcsearch |
| D_FW | Power freewheel diode (DNP footprint) | ≥ 100 V TO-277 / D2PAK | not chosen | — | — | — | **unverified** |
| R_SH1, R_SH2 | Shunt 2 × 0.2 mΩ | Vishay WSLP5931L2000FEA | C413492 | 937 | E | 10 W, 1 %, ±125 ppm (listing) | jlcsearch |
| R_K_BQ×4 | BQ Kelvin averaging | 200 Ω 1 % 0603 | C8218 | n/r | B | — | jlcsearch |
| C_SRP | BQ diff filter 100 nF | CC0603KRX7R9BB104 | C14663 | n/r | B | 50 V X7R | jlcsearch |
| R_K_INA×4 | INA Kelvin averaging | 10 Ω 1 % 0603 | C22859 | n/r | B | — | jlcsearch |
| C_K_INA | INA diff filter 22 nF | 0603 C0G / X7R 22 nF | not looked up | — | — | — | **unverified** |
| U_ISENSE1 | Current amplifier | INA240A1QPWRQ1 (TSSOP-8) | C553123 | 1 913 | E | G = 20, −4…80 V CM, 400 kHz (INA p.3–6) | jlcsearch |
| U_OCP1 | Window comparator | TLV1702AQDGKRQ1 (VSSOP-8) | C130036 | 1 795 | E | dual, open collector, 560 ns (listing) | jlcsearch |
| R_TH1–3 | Window divider 13.7 k / 54.9 k / 31.6 k | 0603 0.1 % | not looked up | — | — | — | **unverified** |
| U_LATCH1 | OC latch | SN74AUP1G74DCUR (VSSOP-8) | C140267 | 17 455 | E | D-FF with PRE / CLR (listing) | jlcsearch |
| U_KILL1, U_KILL2 | 3-input AND | 74LVC1G11GV,125-JSM (SOT-23-6) | C53114319 | 14 614 | E | 1.65–5.5 V, overvoltage-tolerant inputs (listing) | jlcsearch (clone brand; no TI / Nexperia stock seen) |
| U_KILL3 | Inverter | SN74LVC1G04DCKR (SC-70-5) | C2983744 | 19 202 | E | — | jlcsearch |
| Q_KLS_C, Q_KLS_D, Q_HTR_LS | Level shift 100 V | BSS123 (SOT-23) | C7420338 | 822 704 | E | 100 V, 170 mA, 1.4 V th (listing) | jlcsearch |
| Q_KILL_C, Q_KILL_D | Kill P-FET | AO3407A (SOT-23) | C347478 | 117 696 | E | −30 V, 4.2 A, 37 mΩ (listing); **VGS max not in listing** | jlcsearch |
| R_KS (47 k ×2) | Kill gate R | 0805 47 k 1 % | C17713 | n/r | B | 150 V class (0805) | jlcsearch |
| C_KS (1 nF ×2) | Speed-up | 0603B102K101NT (100 V X7R) | C43847 | n/r | E | — | jlcsearch |
| R_PD (100 k) | Fail-safe pull-downs | 0603 100 k 1 % | C25803 | n/r | B | — | jlcsearch |
| R_LD, R_PACK | LD / PACK series 10 k | 0805 10 k 1 % | C17414 | n/r | B | — | jlcsearch |
| Q_EXT1, Q_EXT2 | Ext. output FETs | SQ2318AES-T1_BE3 (SOT-23) | C3280170 | 8 981 | E | 40 V, 8 A, 31 mΩ @10 V (listing) | jlcsearch |
| D_FLY_EXT1/2 | Coil flyback | SS34 (SMA) | C2837271 | 479 217 | E | 40 V, 3 A | jlcsearch |
| Q_HTR1 | Heater switch | CSD19534Q5A (SON-5×6) | C114200 | 585 | E | 100 V, 50 A, 17.6 mΩ @6 V (listing) | jlcsearch |
| Q_HTR_HS | Heater gate high-side | MMBT5401 | C8326 | 616 368 | B | — | jlcsearch |
| D_HTR | Heater flyback | SS310 (SMA) | C47018526 | 19 932 | E | 100 V, 3 A | jlcsearch |
| J_BP, J_BM, J_PP, J_PM | Power lugs | XFCN T68160200-1400 | C45384693 | 4 674 | E | 200 A, M6, 8 legs, 14 mm | jlcsearch + lcsc.com product page |
| J_B2B (power board) | Board-to-board, female 2×15 | 2.54-2*15P | C5337168 | n/r (listed in stock by the headers endpoint: 1 187) | E | 2.5 A/pin (listing) | jlcsearch headers |
| J_B2B (control board) | Mating male 2×15 | — | — | — | — | — | **unverified** (C56496 returned no stock) |
| Cu bars | 10 × 3 mm tinned Cu | custom | — | — | — | 57 µΩ / 100 mm (calc) | not an LCSC part |
| Gap pad, Al plate | Thermal | custom | — | — | — | ≥ 3 W/m·K, 1 mm | not an LCSC part |

**Project field errors found while verifying (report only; nothing was edited):**
* R_PRE1 field **C463124** = NCP1236AD100R2G (a flyback controller), not PWR263S-20-50R0J.
* Q_POS1 / Q_NEG1 / Q_PRE1 field **C148416** = WSP4805 (dual P-FET, SOP-8), not SQ2318EY.

---

## 12. Interface signals

Contract names are used unchanged. **New** names are marked ★ and exist only in this table.

| Signal | Dir. (from → to) | Level / type | Default / fail-safe | Notes |
|---|---|---|---|---|
| `AFE_DFETOFF` | U_KILL1 → BQ DFETOFF (pin 30); MCU may read back | 3.3 V logic, active-low = BOTHOFF | BQ internal weak PD → asserted | Driven by the AND logic, **not** directly by an MCU pin |
| `AFE_FLT_DSG_N` | BQ DDSG (32) → U_KILL2, MCU | REG1 3.3 V push-pull, low = fault | 100 k PD → fault | DDSG mode (TRM p.56–61) |
| `AFE_FLT_CHG_N` | BQ DCHG (31) → U_KILL2, MCU | as above | 100 k PD → fault | DCHG mode |
| `ISENSE_OUT` | INA240 → MCU ADC, U_OCP1 | 0.05–3.1 V, 1.65 V + 2 mV/A | — | §5.3 |
| `OC_TRIP_N` | U_LATCH1 Q → U_KILL1, MCU EXTI | 3.3 V, low = tripped (latched) | powers up low | §5.5 |
| `OC_CLR` | MCU → U_LATCH1 CLK | rising edge clears | 100 k PD | ignored while OC present |
| `FET_EN` | MCU → U_KILL1 | high = permit | 100 k PD → kill | |
| `KILL_N` | U_KILL2 → MCU readback (and U_KILL3) | low = kill active | — | |
| ★ `KILL` | U_KILL3 → Q_KLS_C/D gates | high = kill active | 0 when unpowered (see §8.3) | |
| ★ `MCU_NRST` | TPS3823 RESET / MCU NRST → U_KILL1 | low = reset | — | Watchdog expiry kill (TPS p.7, p.13) |
| ★ `OC_SET_MCU_N` | MCU COMPx_OUT → diode → latch CLR_N | push-pull via diode, low = set | Hi-Z in reset | optional firmware window |
| ★ `AFE_CHG`, `AFE_DSG` | BQ pins 45 / 43 → gate networks (via B2B) | up to BAT + 13 V | — | HV group |
| ★ `AFE_PCHG`, `AFE_PDSG` | BQ pins 40 / 39 → P-FET gates | BAT − 8.4 V | — | HV group |
| ★ `AFE_LD`, `AFE_PACK` | `PACK+` → 10 k → BQ 41 / 42 | 0–80 V | — | HV group |
| ★ `BAT_SNS` | `BAT+` Kelvin at the lug → BQ BAT network | pack V | — | HV group |
| ★ `AFE_FUSE` | BQ FUSE (38) → EXT1 gate OR | NFET gate drive | 100 k PD | §9.1 |
| ★ `SRP_K`, `SRN_K` | Shunt Kelvin averaging → BQ filter | ±0.2 V | — | Pair; DS p.76 |
| ★ `GATE_CHG`, `GATE_DSG`, `FET_MID` | power nodes on the power board | — | — | |
| ★ `NTC_FET`, `NTC_SHUNT` | NTCs on `FET_MID` and on the shunt → AFE TS pin / MCU | — | — | TS-pin plan in the AFE part |
| `HEATER_EN` | MCU → heater level stage | high = on | PD → off | |
| `EXT_OUT1`, `EXT_OUT2` | MCU → EXT gate drive | high = on | PD → off | EXT_OUT1 OR `AFE_FUSE` |
| ★ `EXT1_COIL_N`, `EXT2_COIL_N`, ★ `HTR_RTN` | FET drains → terminals | up to +12V / pack V | — | |
| `+12V`, `+3V3`, `+3V3_A`, `GND_PWR` | control → power board | — | — | `+3V3` must stay on while the FETs are allowed on |
| `BAT+`, `BAT-`, `PACK+`, `PACK-` | lugs | — | — | |

---

## 13. Open questions for the owner (not decided here)

1. **C_bus**: the real inverter DC-link capacitance (2–10 mF was assumed) and the inverter's input current before its DC link is up. This sets R_PRE1 = 50 Ω or 25 Ω and the predischarge settings (§4.2).
2. **500 A peak duration and repetition**: sets the OCD1 delay and the shunt / FET pulse check.
3. **OC window**: +600 A / −305 A as proposed? Should the firmware COMP tier be fitted?
4. **Board form**: two-board stack (recommended) or one 220 × 100 mm board?
5. **Lugs**: M6 200 A XFCN PCB terminals (LCSC) acceptable, or M8 (press-fit REDCUBE from DigiKey, consigned)? What cable cross-section is used?
6. **100 V FET margin**: TI's guideline asks ≈ 160 V peak at 16S (DS p.69). Keep 100 V and accept the controlled-turn-off + clamp design, proven by a short-circuit test (with a 120–150 V TOLL fallback if the test fails), or re-open the FET voltage now?
7. **Hard-fault policy**: any AFE fault (COV / OCC / SCD / OCD / CUV …) turns **both** banks off (body-diode rule, §8.2). Accept, with firmware limits set inside the BQ limits? Which faults should drive DDSG / DCHG?
8. **PCHG** path: populate (100 Ω / 50 W, recovery charge after a hardware CUV) or DNP?
9. **Heater**: pad voltage (pack-voltage pad assumed), power (≤ 240 W assumed), harness fuse, and whether a hardware thermostat is required.
10. **EXT_OUT1 / 2**: coil voltage and current (12 V assumed). Should EXT_OUT1 be tied to the BQ FUSE (permanent fail → breaker trip)?
11. **Shunt TCR** 125 ppm (TI asks ≤ 50 ppm): accept with NTC compensation, or source a low-TCR part outside LCSC?
12. **Reverse-connected parallel pack**: 117 V across the open DSG bank exceeds 100 V. Fit the AN09 reverse-charge clamp footprint? Is the system fuse per pack provided?
13. **INA240 supply**: `+3V3_A` (recommended, ratiometric) or `+3V3`?
14. **Heatsink and ambient**: enclosure / plate supplier and maximum ambient (40 °C assumed; ≤ 0.75 K/W plate-to-ambient needed).
15. **Assembly**: are hand-soldered copper bars and through-hole lugs after JLC PCBA acceptable?
16. **Extended parts**: almost all power parts are JLC Extended. OK for cost?

---

## 14. Unverified list

* **Data sheets not read** (ratings above come from LCSC listings): TLV1702, SN74AUP1G74, 74LVC1G11 (JSM clone), SN74LVC1G04, AO3407A (VGS max), BSS123, MMBT5401 (VEBO), BAS21, BZT52C16S, IRF9540NS (SOA), CSD19534Q5A, SQ2318AES (RDS(on) at 3.3 V, pin-out), 5.0SMDJ60CA / SMCJ60A (surge curves, IFSM), WSLP5931 (pulse and overload curve), XFCN T68160200 (200 A basis, temperature rise), HoRX / RX24 (pulse and energy ratings), C5337168 header.
* **IPT015N10N5**: the SOA (Diagram 3) and RDS(on)-vs-Tj curves are graphs; they were not read numerically. The hot factor 1.6 is est.
* **BQ76952**:
  * DFETOFF / BOTHOFF response time;
  * DDSG / DCHG response time;
  * whether DDSG / DCHG follow the "FET Protections A–C" masks;
  * FUSE pin drive level (R01 garbled figure);
  * CC Gain range (AN32 vs TRM, R01 §9).
* **STM32G473 COMP / DAC** pin mapping and COMPx_OUT alternate functions (ST data sheet not opened).
* **IPC-2221B B3 1.5 mm** and **IEC 60664-1 ≈ 1.25 mm** values (from memory). JLC 2 oz outer-layer minimum track / gap.
* **Stock not reported** by jlcsearch for Basic passives (C22859, C22775, C7250, C8218, C14663, C17958, C17713, C25803, C17414, C28233) and for C125847, C55151 and C43847. Stock low for C2985693 (9) and C49375386 (13).
* **No LCSC part found or chosen**: SM8S58A / 60A, M8 PCB terminals, mating male 2 × 15 header, power freewheel diode, 22 nF INA filter cap, 1 MΩ P-FET gate-source resistors, 0.1 % divider resistors, +5V gate buffer for EXT outputs, heater fuse.
* **All loss, thermal, short-circuit, inductance and timing figures** are calc / est. and need the bench tests in §6 and §4.5.

---

### Sources (web)

* Part data: `https://jlcsearch.tscircuit.com/components/list.json?search=<MPN or Cxxxx>`, plus the `/resistors/`, `/capacitors/` and `/headers/` `list.json` endpoints (2026-11-17).
* `https://www.lcsc.com/product-detail/C45384693.html` (XFCN terminal data); `https://www.lcsc.com/product-detail/C70285.html` (SN74LVC1G74DCUR, no stock shown).
* Infineon IPT015N10N5 data sheet Rev 2.4: `https://www.infineon.com/dgdl/Infineon-IPT015N10N5-DS-v02_02-EN.pdf?fileId=5546d462518ffd8501524e9f36d03c6d`
* TI documents SLUSE13B, SLUUBY2B, SLUAA09A, SBOS808E and TPS382x: local copies from the research pass (see `docs/research/01_bq76952_features.md` §0).
