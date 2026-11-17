# Bill of materials v1 — part selection (P3), 2026-11-17

Part selection for the v1 architecture ([`ARCHITECTURE.md`](ARCHITECTURE.md), decisions D-01…D-16).
Four groups were selected in parallel; every LCSC number was checked live on 2026-11-17 against the LCSC product record (exact MPN + manufacturer) and the JLCPCB parts library (stock, Basic / Extended), and every IC, power part, protection part and connector against its datasheet (page cited in the `DS check` column).

| File | Content |
|---|---|
| [`bom/bom_v1_all.csv`](bom/bom_v1_all.csv) | all groups in one table (playbook field order + group, qty, fit) |
| [`bom/bom_G1.md`](bom/bom_G1.md) | sheet 01 power tree, sheet 07 power stage (power board) |
| [`bom/bom_G2.md`](bom/bom_G2.md) | sheet 02 AFE / cell monitor, sheet 04 current sense |
| [`bom/bom_G3.md`](bom/bom_G3.md) | sheet 03 MCU, sheet 08 IO / front panel, sheet 10 memory / sensors |
| [`bom/bom_G4.md`](bom/bom_G4.md) | sheet 05 aux outputs, sheet 06 communications, sheet 09 wireless |

Each group file has the full table, cost, Extended / THT / low-stock lists, the re-resolution of the wrong LCSC numbers found in the 2026-11 schematic, unverified items, design-impacting findings and questions.

## Summary

| Group | Fitted placements | Unique LCSC | Cost / board @ 100 (est.) |
|---|---|---|---|
| G1 power tree + power stage | 198 | 76 | ≈ $54.3 (16 × 100 V TOLL FETs ≈ $17.4; two 100 W resistors + standoffs ≈ $13.9) |
| G2 AFE + current sense | 177 | 53 | ≈ $25.8 (INA240A1-Q1 alone $13.1; ≈ $14.7 with the non-Q INA240A1) |
| G3 MCU + IO + memory | 98 | 38 | ≈ $13.0 |
| G4 comms + wireless + aux | 109 | 41 | ≈ $12.5 |
| **Total** | **≈ 580** | **165 (104 Extended)** | **≈ $105 est.** — excludes PCB, assembly, hand soldering, copper bars, aluminium plate, enclosure |

* Spot check by the integrator (10 key parts, LCSC product API, 2026-11-17): STM32G473RCT6 C529361, BQ76952PFBR C2862742, IPT015N10N5 C108964, WSLP5931L2000FEA C413492, LM5013QDDARQ1 C5219285, CA-IS3050CW C41784143, CA-IS3082WX C970942, TPS3828-33DBVR C20032, AO3400A C20917, SS8050 C2150 — all match MPN and manufacturer.
* Unverified: 1 row (G3 C311 supercap, DNP — no number chosen yet).
* 29 LCSC numbers are shared between groups (common passives, test hooks, connectors) — they become single BOM lines in KiCad.
* **Counted twice, to fix at schematic time:** the shunt WSLP5931 (C413492, listed in G1 and G2) and the board-to-board header (C56496, listed in G1 and G2). Each physical part gets one reference on one sheet.

## Design changes forced by part selection (owner decisions pending)

| # | Source | Change | Why |
|---|---|---|---|
| P-01 | G1 | All MLCCs on 58 V nodes → 250 V (mostly 2220), ≈ +$2.4 | 100 V parts fail the 2× voltage rule |
| P-02 | G1 | Supply-tap fuse moved to the power board at the B+ lug; new `VSUP_TAP` pin on the B2B | tap trace and B2B pin were unfused from the pack |
| P-03 | G1 | Blocking diodes in the pre-charge and pre-discharge paths | P-FET body diodes bypassed the open FET banks |
| P-04 | G1 | LM5013-Q1 is non-synchronous: external Schottky SS520, new RON / feedback / 22 µH inductor | datasheet application circuit |
| P-05 | G1 | Shunt alternative Milliohm HolRS3920 (C558625, ±50 ppm, 14 468 in stock) | Vishay 0.2 mΩ is ±225 ppm (G2 F-4), 937 in stock |
| P-06 | G2 | Latch power-up delay moved to its own RC + diode | the 100 nF on CLR_N slowed the short-circuit trip ≈ 12 µs (≈ 0.75 → 1.2 kA) |
| P-07 | G2 | C_BAT1 → 1 µF 250 V | 2× rule |
| P-08 | G2 | Transistor symbols with numbered pins (`Transistor_BJT:SS8050`, `Transistor_FET:2N7002`) | lettered-pin symbols do not map to SOT-23 pads |
| P-09 | G3 | Watchdog TPS3823 → **TPS3828-33** (open drain) + 10 k pull-up | push-pull output fights SWD and hides MCU resets from the kill gate (breaks D-02) |
| P-10 | G3 | Green LEDs on +5V via the 5 V-tolerant expander; red / photoMOS on +3V3 | green Vf up to 3.1 V |
| P-11 | G3 | HSE: 5032 two-pad footprint, 33 pF caps; NTC mux CD4051 → TMUX1308; flash GD25Q64 primary | crystal CL, mux on-resistance at 3.3 V, flash stock |
| P-12 | G4 | EXT_OUT FET SQ2318AES → AO3400A + 5.6 V gate clamp | SQ2318AES not specified at 3.3 V gate drive |
| P-13 | G2/G3/G4 | −40 °C rated replacements for RJ45, JST XH / GH, DIP, button, buzzer — or accept −25/−30 °C parts | D-14 rating −40…+85 °C |

Further questions (INA240 grade, X5R policy, ESP32 module variant, buzzer fit, supercap, terminal torque, R_PRE stock, stack height, …) are listed per group in the group files and are asked in the next owner round.
