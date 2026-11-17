# ESS-BMS-16S — System architecture (integrated)

Integrated architecture of the 16S LFP energy-storage BMS, built from four detailed sections:

* **A**: power stage, current sense, independent trip ([docs_architecture/A_power_stage.md](docs_architecture/A_power_stage.md))
* **B**: power tree, budgets, sleep / wake / ship, input protection ([docs_architecture/B_power_tree.md](docs_architecture/B_power_tree.md))
* **C**: AFE integration (BQ76952) ([docs_architecture/C_afe.md](docs_architecture/C_afe.md))
* **D**: MCU, communications, I/O, connectors, sheet plan ([docs_architecture/D_mcu_comms_io.md](docs_architecture/D_mcu_comms_io.md))

Date 2026-11-17. **Status: architecture proposal.** No KiCad file has changed. Where this file and a section disagree, this file wins.

**Evidence rules.**
* Every number comes from a section, with that section's source, or is marked `calc` (arithmetic done here).
* LCSC numbers and stock were checked live by the section authors on 2026-11-17. They were **not** re-checked here; their status is carried over.
* Items marked **INTEGRATOR PROPOSAL — owner to confirm** resolve a conflict between sections. They are not owner decisions.

---

## 1. Purpose and scope

The goal is a compact 16S LFP BMS for stationary storage that does more than the Daly / JBD / JK class of boards (research summary, `docs/research/00_SUMMARY.md`).

**Owner decisions in force** (decisions log in `PROJECT.md` §5, all dated 2026-11-17):

| Decision | Consequence for the architecture |
|---|---|
| Power switching = on-board back-to-back high-side N-FET banks driven by BQ76952 CHG / DSG, with PCHG / PDSG pre-charge. Contactor channels become optional outputs | Section A; contactor drivers become `EXT_OUT1/2` |
| 200 A continuous, **LFP only** (100 V FETs; 16S NMC out of scope) | A §4; margins in §6 below |
| MCU = **STM32G473RCT6** (LQFP-64, 3 FDCAN). Not AEC-Q | D §2 |
| v1 feature set: sleep / wake + button, SOC LEDs + RUN / ALM, 2 dry contacts, heater output, parallel packs (RJ45 × 4, 2nd RS-485, 2nd CAN, DIP address), RTC + FRAM + 8 MB flash, firmware update, ESP32-C3, improved balancing (TI NPN + active-balancer header), MCU-independent safety trip | All sections |
| Public showcase repository; documentation mandatory; no personal paths | This file |
| Licence CERN-OHL-S-2.0 (hardware), MIT (`tools/`) | – |

Older decisions (2026-11-16) still apply: complete the schematic first, the PCB layout restarts later, and requirement gaps are reported to the owner before any circuit change.

---

## 2. System block diagram (two-board stack, section A §10 recommendation)

```
                    ┌─────────────────────────── CONTROL BOARD 160 × 100 mm, 4 L, 1 oz ───────────────────────────┐
 cell harness ──────┤ J_CELL1 Micro-Fit 2×9 ─ R_VC/C_DF ─ U_AFE1 BQ76952 ─ SS8050 balancing ─ J_ABAL1 (ext. bal.) │
 (CELL_0..16,       │       BAT_SNS (pin 18) ─ D_BAT1/R/C ─ BAT ; D_REG0 ─ FCX495 ─ REGIN → AFE_REG1 3.3 V island   │
  BAT_SNS, NTC1-4)  │ J_NTC1 ─ TS1/TS3/HDQ             I2C1+CRC (PA15/PB7, pull-ups on AFE_REG1)              │
                    │ 01 VSUP ─ LM5013/LM5164 → +5V ─ TPS7B82 → +3V3 / +3V3_A ; TLV62569 → +3V3_ESP ; LM5163 → +12V │
                    │      TPS22918 → B0505S-2WR3 (2 W) ══ +5V_ISO / GND_ISO ══ 2 × CA-IS3050CW, 2 × CA-IS3082WX     │
                    │ 03 U301 STM32G473RCT6 ─ TPS3823 ─ LSE/HSE ─ SWD     10 FRAM + 8 MB flash + NTC mux             │
                    │ 08 2 × TCA9535: LEDs, DIP, enables, dry contacts   09 ESP32-C3-MINI-1 (board edge)              │
                    │ 06 RJ45 × 4 (INV-CAN, INV-485, LINK-IN, LINK-OUT)  + isolated USB-C service (CH340C + ISO7721) │
                    └───────────────────┬────────── J_B2B 2 × 15, 2.54 mm (HV / Kelvin / analog / logic / rails) ─────┘
                                        │  AFE_CHG/DSG/PCHG/PDSG/LD/PACK/FUSE, SRP/SRN Kelvin, ISENSE_OUT, NTC_FET,
                                        │  NTC_SHUNT, OC_TRIP_N, OC_CLR, FET_EN, MCU_NRST, AFE_FLT_*, AFE_DFETOFF,
                                        │  KILL_N, HEATER_EN, +12V, +3V3, +3V3_A, GND_PWR × 3
                    ┌───────────────────┴────────── POWER BOARD ≈ 150 × 100 mm, 4 L, 2 oz outer, on Al plate ────────┐
 BATTERY+ ═[M6]═ BAT+ ═ CHG bank 8 × IPT015N10N5 ═ FET_MID ═ DSG bank 8 × IPT015N10N5 ═ PACK+ ═[M6]═ load / charger + │
   supply tap ─► │  4 × 5.0SMDJ60CA clamp      PNP turn-off + AO3407A kill per bank      2 × SMCJ60A clamp / freewheel │
   (to VSUP via  │  PDSG: IRF9540NS + 50 Ω/100 W   PCHG: IRF9540NS + 100 Ω/50 W          heater FET CSD19534Q5A       │
    B2B / lead)  │  07 gate-kill AND logic ("safety island")                                                          │
 BATTERY− ═[M6]═ BAT- (GND_PWR star) ═ 2 × WSLP5931 (100 µΩ) ═ PACK- ═[M6]═ load / charger −                         │
                 │  04 INA240A1 → ISENSE_OUT → TLV1702 window → SN74AUP1G74 latch → OC_TRIP_N                        │
                    └────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The single-board alternative (≈ 220 × 100 mm) uses the same circuits without J_B2B (decision D-03).

---

## 3. Sheet plan

References become numeric per sheet (D §7). Power symbols keep the `#PWRnxx` scheme. **INTEGRATOR PROPOSAL — owner to confirm:** the control-board half of J_B2B sits on sheet 02, because most of its HV pins are AFE pins.

| Sheet | File | Range | Board | Section | Main parts |
|---|---|---|---|---|---|
| 01 | `01_Power_Supply` | 1xx | control | B | F_SUP / F_AUX, R_DAMP, D2 / D3, D_TVS1, U1 (+5V), U5 (+12V), U3 (+3V3) + FB → `+3V3_A`, U6 (+3V3_ESP), U7 + U4 (`+5V_ISO`), power latch (`PWR_EN`, Q_BTN, Q_ALRT, D_OR), `VBAT_MCU` OR, J_AUX |
| 02 | `02_AFE_Cell_Monitor` | 2xx | control | C | U_AFE1, J_CELL1, R_VC / C_DF, Q_BL / R_BL / R_BB / D_BB, REG0 NPN, BAT / CP1 network, NTC filters, J_NTC1/2, J_ABAL1, FUSE driver (DNP), control-side J_B2B |
| 03 | `03_MCU_Control` | 3xx | control | D | U301 G473, decoupling, Y301 / Y302, VBAT, U302 TPS3823, BOOT0, J301 SWD |
| 04 | `04_Current_Sensing` | 4xx | power | A | R_SH1/2, Kelvin filters, U_ISENSE1 INA240A1, U_OCP1 TLV1702 + divider, U_LATCH1, `NTC_SHUNT` |
| 05 | `05_Aux_Outputs` (rename of Power_Actuators) | 5xx | both | A + D | A: heater FET (power board), EXT_OUT1/2 drivers. D: fan driver + J502, dry contacts U501/U502 + J501 |
| 06 | `06_Communications` | 6xx | control | D | U601–U604, TVS, CMC (DNP), termination DIPs, J601–J604, USB-C service U605–U607 + J605 |
| 07 | `07_Power_Stage` (new) | 7xx | power | A | FET banks, gate networks, PNP turn-off, PDSG / PCHG, clamps, gate-kill logic U_KILL1–3 + kill FETs, lugs, power-side J_B2B, `NTC_FET` |
| 08 | `08_IO_Front_Panel` (new) | 8xx | control | D | U801 / U802, LEDs D801–D806, SW801 address DIP, SW802 button, BZ801 + Q801, J801 |
| 09 | `09_Wireless` (new) | 9xx | control | D | U901 ESP32-C3, EN RC, straps, DNP ROM-flash straps |
| 10 | `10_Memory_Sensors` (new) | 1001–1099 | control | D | U1001 FRAM, U1002 flash, U1003 NTC mux, MCU NTC inputs |

With the two-board option, sheets 04, 07 and the heater half of 05 form the separate power-board project.

---

## 4. Power tree, rail budget and operating states

### 4.1 Tree (B §1, reconciled)

```
BAT+ (cell side of the FETs) ─ F_SUP 2 A ─ R_DAMP 2 Ω ─ D2 SS320 ─┐
J_AUX 9–58 V ─ F_AUX ─ D3 ES2D ──────────────────────────────────┴─ VSUP (D_TVS1 SMCJ60A, 4 × 2.2 µF 100 V)
   VSUP ─ U1 (EN = PWR_EN) ─► +5V trunk ─┬─ U3 TPS7B8233-Q1 ─► +3V3 ─┬─ FB ─► +3V3_A (VDDA, VREF+, INA240, TLV1702, NTC bias)
                                         │                          └─ MCU, logic, gate-kill logic, LEDs, dry-contact LEDs, buzzer
                                         ├─ U6 TLV62569 (EN_ESP) ─► +3V3_ESP
                                         ├─ U7 TPS22918 (EN_ISO) ─► U4 B0505S-2WR3 ═► +5V_ISO / GND_ISO
                                         └─ J_ABAL1 pin 3 (100 mA PTC)
   VSUP ─ U5 LM5163-Q1 (EN_12V) ─► +12V (switched leaf): fan, heater gate stage, optional EXT coils
AFE island: BAT_SNS ─ REG0 NPN ─ REGIN → REG1 = AFE_REG1 3.3 V (≤ 5 mA): DDSG / DCHG high level, I2C, ALERT and
            WAKE_BTN_N pull-ups, wake inverters Q_BTN / Q_ALRT, VBAT_MCU (with +3V3)
```

Changes made during integration (each **INTEGRATOR PROPOSAL — owner to confirm**):

* **`+3V3_SENSE` / `EN_SENSE` / U8 dropped** (conflict 6, §5.4). The INA240, the window comparator and its divider go on `+3V3_A`, as in A. The OC latch stays on `+3V3`.
* **SOC / RUN / ALM LEDs, dry-contact LEDs and the buzzer are on `+3V3`**, as in D's circuits. B had budgeted them on `+5V`.
* **No separate ESP load switch.** D's U902 is dropped; the TLV62569 EN pin does the job (B §5.1).
* **`+12V` is kept** as B's switched leaf. A's heater FET and D's fan both need it (conflict 8).
* **The `+5V` trunk converter is upgraded to LM5013-Q1** (B's option A′), because the merged peak exceeds the LM5164's 1 A (table below; decision D-08).

### 4.2 Rail budget (every load from A, B, C, D; peak = all worst cases at once)

| Rail | Source | Typ / peak (mA) | Limit | Peak % | Basis |
|---|---|---|---|---|---|
| `VSUP` | BAT+ tap | ≈ 21 / ≈ 290 at 51.2 V; ≈ 460 at 32 V | F_SUP 2 A | 23 % | calc from the rows below, η 0.85 (B est.) |
| `+5V` | U1 | 164 / **962** | LM5164 1 A (valley 0.95 A min) → **96 % ✗**; LM5013-Q1 3.5 A → **27 % ✓** | see note | calc: U3 233 + U6 272 + U4 input 357 (300 / 0.84) + J_ABAL1 100 (PTC hold, C) |
| `+3V3` | U3 TPS7B8233-Q1 | 79 / 233 | 300 mA | **78 %** | B's 60 / 114, plus LEDs 12 (B), dry-contact LEDs 5 / 10 (B), buzzer 0 / 95 (D, MLT p.2), NTC dividers 1.5 (calc: 9 × 3.3 V / 20 kΩ) |
| `+3V3_A` | ferrite from +3V3 | ≈ 7 / ≈ 11 | ferrite rating not checked | – | VDDA 3 / 6 (B est.), INA240 + comparator 2.3 / 3.4 (B), NTC bias 1.5 (calc) |
| `+3V3_ESP` | U6 TLV62569 | 30 / 350 | 2 A | 18 % | B (ESP p.21) |
| `+5V_ISO` | U7 + U4 B0505S-2WR3 | ≈ 20 / **300** | 400 mA; **min. load 40 mA** | **75 %** | D §3.4: CAN 2 × 73, RS-485 2 × ≈ 70 (ISO1500 figure as proxy), 2 × 6.8 quiescent |
| `+12V` | U5 LM5163-Q1 | 0 / 151 | ≈ 0.47 A DC (B calc) | 32 % | fan 150 (B, unverified) + heater gate stage ≈ 1.2 (calc: 12 V / 10 kΩ) |
| `+12V` with EXT coils | U5 = LM5164-Q1 | 0 / 651 hold | 1 A | 65 % | + 2 × 250 hold (B). **One coil pull-in ≤ 0.40 A only** (calc: 800 − 250 − 150) |
| `AFE_REG1` | BQ76952 REG1 | 0.015 / 1.75 | 5 mA budget (C §3.4) | 35 % | calc: 2 × 3.3 V / 470 kΩ = 14 µA, I2C 2 × 3.3 V / 4.7 kΩ = 1.4 mA (both low), ALERT 0.33 mA, button 3.3 µA, VBAT 0.5 µA |

Notes:
* **U3 dissipation** at peak: (5 − 3.3) V × 0.233 A = 0.40 W → +25 °C at 63.9 °C/W (calc, B's RθJA). The buzzer causes most of this (decision D-31).
* **`+5V_ISO` below its minimum load** in Standby (≈ 15–20 mA, D Q15) can rise above the 5.5 V bus-side maximum of the CA-IS parts (D §3.2). Measure at bring-up, or add the ≈ 15 mA dummy load from B §3.6.
* **J801 front-panel loads** (D §3.6) are not budgeted (unverified).

### 4.3 Operating states (B §4.2 and §6, updated for the recommended `FET_EN` pull-down, decision D-01)

| State | AFE | FETs / `PACK+` | Board rails | MCU | Wake sources | I_pack at 51.2 V, 25 °C |
|---|---|---|---|---|---|---|
| **Ship** | SHUTDOWN | off | off | off | TS2 button, LD (charger) | **≈ 8 µA** (B §6.2) |
| **Sleep** (recommended: output **off**) | SLEEP, protections on | off (BOTHOFF via the DFETOFF pull-down) | off (`PWR_EN` low) | off, RTC on `VBAT_MCU` | button, charger, AFE fault (`AFE_ALERT`), Remote-ON opto (DNP) | **≈ 54 µA** est. (B's 47 µA itemisation with 470 kΩ instead of 1 MΩ pull-downs, calc +7.4 µA; AFE SLEEP current with the drivers off is not specified, B's 24 µA used) |
| Sleep, option "output live" (Seplos-style) | SLEEP, DSG source-follower | live | off | off | + load current (Wake Comparator) | ≈ 54 µA with source-follower; **≈ 71 µA** with C's Chg Pump Control 0x01 (41 µA overdrive, B §6.1) |
| **Standby** | NORMAL ↔ SLEEP | on (output live) | on; ISO on, ESP off / BLE, `+12V` off | Stop 1 | CAN / RS-485 RX, button, ALERT, RTC, `PG_5V` | **≈ 5.9 mA** est. (B's 5.2 mA + sense rail now always on + CA-IS iso load, calc) |
| **Run** | NORMAL | per protection | on | 170 MHz | – | **≈ 19 mA** typ, ≈ 26 mA with WiFi (B §6.3) |
| **Fault** | NORMAL, FET(s) off by AFE or kill | off | on | Run: log, ALM, DRY1/2 | recovery per AFE / firmware | as Run |

Wake latency: ≈ 0.21 s from Sleep, ≈ 0.5 s from Ship (B §4.2). Board self-consumption returns on the cell side of the shunt, so firmware adds it to SOC (B §11.8).

---

## 5. Protection architecture

### 5.1 Layers (ordered: firmware < AFE < hardware latch)

All current thresholds are on a 100 µΩ shunt. AFE values are from C §8.2; A §5.4 agrees except where marked.

| Quantity | Firmware (MCU) | AFE (autonomous, BQ76952) | Hardware latch / kill (MCU-independent) | Action |
|---|---|---|---|---|
| Cell over-voltage | charge stop ≤ 3.60 V (A §8.2 example) | **COV 3.643 V** (code 72, ±25 mV), 1.0 s; COVL 3. PF SOV 3.80 V, 5 s | via DCHG → U_KILL2 | CHG off + both banks killed (body-diode rule, A §8.2) |
| Cell under-voltage | discharge stop 2.80 V (A) | **CUV 2.479 V**, 2.0 s; auto-SHUTDOWN 2.3 V / cell or 36 V, 10 s; PF SUV 2.0 V, 5 s | via DDSG → U_KILL2 | both banks off; recovery charge through PCHG (not gated by DDSG / DCHG) |
| Discharge current | continuous 200 A rating, derated by temperature | **OCD3 220 A, 30 s** (C; A said 210 A, see §5.5) → OCD2 300 A ±40 A, 0.4 s → OCD1 560 A ±50 A, 19.8 ms → **SCD 800 A** (680–920 A), SCDL latched | **window +599 A** (±12 A), ≈ 3.9 µs to start of current fall, latched | DSG off / kill both |
| Charge current | charger request (owner value) | **OCC 260 A** (220–300 A), 99 ms. PF SOCC 300 A | **window −305 A** (±12 A), latched | CHG off / kill both |
| MCU-dependent fast tier | COMP3 / COMP4 + DAC → TIM8 break → `FET_EN` = 0 (D §2.3) | – | acts through U_KILL1 | kill both + BOTHOFF |
| Temperature | thermostat (heater), derating, `NTC_SHUNT` / `NTC_BAL` / `NTC_AMB` | OTC 45 / UTC 0 / OTD 60 / UTD −20 °C (cells); **OTF 85 °C** (FET NTC on CFETOFF); OTINT 85 °C; PF SOT 70 / SOTF 100 °C | – | FETs off per direction |
| Watchdog | IWDG backstop | HWD 10 s (C; A gave 2–5 s) | TPS3823 0.9 / 1.6 / 2.5 s → `MCU_NRST` → kill | kill both |
| Pre-discharge | abort if `PACK+` has not risen after 200 ms; limited retries (A §4.2) | PDSG, timeout 2.55 s, stop delta 2.5 V (A, see §5.5) | – | – |
| Permanent fail | – | PF A / B / C / D enables per C §8.2; FUSE output if fitted | FUSE → breaker / fuse driver (C §7) | PF, FETs off, optional fuse |

**Flags:**
* OCD1 (510–610 A) overlaps the latch window (588–612 A). This is acceptable because the latch is faster, but it means OCD1 only acts on 510–588 A events.
* PF SOCC 300 A sits at the top of OCC's tolerance and 2 % below the latch minimum (293 A, calc). C / owner to re-check the ordering (decision D-36).

### 5.2 Gate-kill logic (A §8, with conflict 1 resolved)

```
FET_EN   (PB6, 100 kΩ PD) ──────┐
OC_TRIP_N (U_LATCH1 Q) ─────────┼─ U_KILL1 74LVC1G11 AND3 ──► AFE_DFETOFF ──(B2B)──► BQ DFETOFF pin 30 = BOTHOFF (active-low)
MCU_NRST (TPS3823 / NRST) ──────┘   (+3V3 supply)               │                     + 100 kΩ to VSS at the pin  ◄ INTEGRATOR PROPOSAL
                                                                ├──► U801 P07  DFETOFF_RB (self-test read-back)
AFE_FLT_DSG_N (DDSG, 470 kΩ PD) ┐                               │
AFE_FLT_CHG_N (DCHG, 470 kΩ PD) ┼─ U_KILL2 74LVC1G11 AND3 ◄─────┘
                                └──► KILL_N ──► MCU PB4 (EXTI4) ; LED_ALM_HW option
                                       └─ U_KILL3 74LVC1G04 ─► KILL ─► 2 × BSS123 ─► AO3407A per bank:
                                            GATE_CHG → R_OFF → BAT+   and   GATE_DSG → R_OFF → PACK+  (gate to source, never to VSS)
```

* Every kill turns off **both** banks (body-diode rule, A §8.2).
* `AFE_DFETOFF` uses only the non-AFE sources, so BOTHOFF cannot deadlock a cleared AFE fault (A §8.1).
* C's Q_DOFF1, R_DOFF1 (10 kΩ pull-up to REG1) and D_DOFF1 are **removed**. The pull-up would turn an unplugged B2B or an unpowered AND gate into "FETs allowed". The 74LVC1G11 output is Hi-Z when unpowered (Ioff), so the external pull-down asserts BOTHOFF. A relied on the BQ's internal weak pull-down instead, which is an OTP option and is absent on a blank part.

### 5.3 Fail-safe state table

| Condition | FET_EN | OC_TRIP_N | MCU_NRST | DDSG / DCHG | DFETOFF pin | Kill FETs | Result |
|---|---|---|---|---|---|---|---|
| MCU reset / watchdog / internal reset | Hi-Z → 0 | latched state kept | 0 | as AFE | low | driven | **Both banks off + BOTHOFF** (every MCU reset drops the output, decision D-02) |
| `FET_EN` = 0 (firmware or TIM8 break) | 0 | – | 1 | – | low | driven | both off, ≈ 2.5 µs to plateau (A §7.3) |
| `+3V3` lost / board off (Sleep, Ship, brown-out) | 0 | latch unpowered | 0 | REG1-driven, or Hi-Z in SHUTDOWN | Hi-Z → 100 kΩ PD → **asserted** | not driven | AFE holds all FETs off; 10 MΩ + 16 V zeners hold the gates |
| AFE SHUTDOWN | – | – | – | Hi-Z → PD → "fault" | – | driven if +3V3 is on | killed; the AFE drivers are off too |
| AFE DEEPSLEEP (not used) | – | – | – | active | – | – | FETs off by the AFE |
| OC latch tripped | – | 0 | – | – | low | driven | killed until an `OC_CLR` edge with no OC present |
| B2B unplugged | PD → 0 (power board) | PD | PD | PD | PD at the AFE pin | driven if the power board has +3V3; else off | killed + BOTHOFF |
| Power-up | 0 until firmware | **tripped** (CLR_N RC 10 kΩ × 100 nF ≈ 1 ms) | 0 during POR | per AFE (FET Test mode until OTP) | low | driven | all off until the self-test clears the latch and sets `FET_EN` |
| Sense rail off | not applicable: there is no switched sense rail (§5.4) | | | | | | |

### 5.4 Sense rail interlock (conflict 6)

**INTEGRATOR PROPOSAL — owner to confirm: delete `+3V3_SENSE`, `EN_SENSE` and U8.**

* INA240A1 VS and REF1, TLV1702 and the 13.7 k / 54.9 k / 31.6 k divider go on `+3V3_A`. This is A's arrangement, ratiometric with the MCU VREF+ (`ISENSE_OUT` = VS/2 + 2.0 mV/A).
* SN74AUP1G74 and its CLR_N pull-up / RC stay on `+3V3`.
* This leaves no state in which `+3V3` is on, the FETs may be on, and the trip is blind. Board off ⇒ AND unpowered ⇒ BOTHOFF.
* Cost: about 2.3 mA on +3V3 (≈ 0.26 mA from the pack, calc) in Standby and Fault.
* **If U8 is kept anyway**, all of the following are needed:
  * the latch, its CLR_N pull-up and the RC must move onto `+3V3_SENSE`, so the latch powers up tripped every time the rail comes on;
  * `OC_TRIP_N` gets a 100 kΩ pull-down, so an unpowered (Ioff, Hi-Z) latch reads "tripped";
  * the INA240, the comparator and the divider must share `+3V3_SENSE`, so the ratiometric tie to VREF+ is lost.
  * `EN_SENSE` off then implies FETs off by construction.

### 5.5 Threshold reconciliation (conflict 9)

| Item | A | C | Resolved |
|---|---|---|---|
| OCC | 26 mV, 260 A, 100 ms (A: R04's 22 mV is too low) | 13 / 28 → 26 mV, 99 ms | **agree, 26 mV** |
| OCD1 | 56 mV, 10–20 ms | 28 / 4 → 56 mV, 19.8 ms | **agree** |
| OCD2 | 30 mV, 0.4 s | 15 / 119 → 30 mV, 399 ms | **agree** |
| OCD3 | 210 A, 10–60 s | −2200 userA = 220 A, 30 s | **220 A, 30 s** (C owns the image; 10 % above the rating). INTEGRATOR PROPOSAL |
| SCD | 80 mV, delay "fastest", SCDL | 4 / 3 → 80 mV, **30 µs**, SCDL 1 | **80 mV, fastest delay.** INTEGRATOR PROPOSAL. A's SCD-only double fault already reaches ≈ 1.7 kA at 100 V; each extra µs adds ≈ 39 A, so 30 µs gives ≈ 2.9 kA (calc). Fallback 15 µs (one 15 µs step; research 04, DS p.22) if inverter inrush causes nuisance trips |
| Window | +599 A / −305 A | – | as A (decision D-21) |
| Predischarge | timeout 2.55 s, stop delta 2.5 V | 250 / 100 → 2.5 s, 1.0 V | **2.55 s / 2.5 V** (A sizes R_PRE1). INTEGRATOR PROPOSAL. With 1.0 V, an inverter standby load above 20 mA (calc: 1.0 V / 50 Ω) would always end on timeout |
| COV / CUV | example 3.75 / 2.50 V | 3.643 / 2.479 V | **C's values**: 3.643 V protects LFP better; firmware stays at ≤ 3.60 V |
| HWD | 2–5 s | 10 s | **10 s** (C; decision D-37) |

### 5.6 Timing chain (A §7, calc / est.)

| Path | Chain | Start of current fall | Interrupted |
|---|---|---|---|
| OC latch (primary) | INA 0.4 + RC 0.47 + TLV1702 0.56 + logic 0.03 + BSS123 / AO3407A 0.2 + gate to plateau 2.2 µs | **≈ 3.9 µs** after crossing 600 A (≈ 0.75 kA at turn-off) | **≈ 20–25 µs** (t_f 15–20 µs set by R_OFF) |
| BQ SCD (backup) | 20 µs filter lag + 0.6–8 µs detect + 2–20 µs DSG fall | ≈ 25–45 µs with the fastest delay (+30 µs with C's setting) | – |
| `FET_EN` / TIM8 break | GPIO → AND chain → kill FET | ≈ 2.5 µs to plateau | – |
| Watchdog | TPS3823 0.9 / 1.6 / 2.5 s → RESET → kill | + 2.5 µs | – |
| AFE fault (DDSG / DCHG) | BQ decision → pin → U_KILL2 | **unverified** (no TI number) | – |
| DFETOFF / BOTHOFF | AND → BQ | **unverified** | – |

---

## 6. Over-voltage and margin table (conflict 7)

Margin = (abs max − worst case) / abs max. Rows under 10 % are flagged ⚠.

| Node | Nominal | Max steady | Transient (source) | Clamp | Weakest abs max | Margin | |
|---|---|---|---|---|---|---|---|
| `BAT+` lug / FET V_DS | 51.2 V | 58.4 V | **78–85 V** at 0.8 kA, t_f 20 / 15 µs (A §6); **100 V** SCD-only double fault | 4 × 5.0SMDJ60CA: VBR 66.7 V min, Vc 96.8 V @ 51.7 A (listing) | IPT015N10N5 100 V | 15 % (design case); **0 %** (double fault) | ⚠ |
| Open banks, parallel pack reversed | – | ≈ 117 V (A §10.4) | – | – | 100 V | **negative** | ⚠ |
| Clamp at rated Vc | – | – | if the TVS reaches 96.8 V | – | 100 V | 3 % | ⚠ |
| `VSUP` (LM5164 / LM5013 VIN, C_IN) | 51.2 V | 58.4 V | via R_DAMP 2 Ω from BAT+ | SMCJ60A: ≈ 91 V at BAT+ = 96.8 V (B est.); ≈ 93 V at BAT+ = 100 V (calc, B's method); ≤ 85 V in A's design case | 100 V (VIN, C_IN rating) | 9 % / 7 % / 15 % | ⚠ |
| `PACK+` → BQ LD / PACK (10 kΩ series) | 51.2 V | 58.4 V (charger) | charger / load-cable kick (not computed) | 2 × SMCJ60A, Vc 96.8 V @ 15.5 A | LD / PACK pin range 0–80 V (DS p.10); abs max not quoted in the sections | negative at full clamp; current-limited by 10 kΩ | ⚠ verify |
| AFE `BAT` (BAT_SNS tap → 1N4148WS → 100 Ω → 1 µF) | 50.7 V | 57.9 V | ≤ +4.8 V for a 20 µs, +26.6 V event (calc, τ = 100 µs) | none at the pin | 74 V while the pump runs (research 01: CP1 ≤ 85 V) | 15 % | |
| `CP1` (BAT + 11…13 V) | – | 71.4 V (A) | ≈ 75.7 V | – | 85 V (DS p.9) | 16 % / 11 % | at the line |
| `VC16`, cell taps | 51.2 V | 58.4 V | part of the lug overshoot, depending on where L_bat sits (not computed) | none (no common-mode caps, C) | 85 V (DS p.7–8) | 31 % steady | ⚠ unverified |
| REG0 path (1N4148WS, FCX495) | – | 58.4 V | reverse only if BAT_SNS collapses | – | 100 V / 150 V | 42 % | |
| Gate–source of the banks | 11 V overdrive | – | – | 16 V zener (15.3–17.1 V) | VGS ±20 V | 14 % | |
| BSS123 kill level shifters | – | 58.4 V | 85 V / 100 V via the gate bus | – | 100 V | 15 % / 0 % | ⚠ double fault |
| `+5V_ISO` | 5.0 V | unregulated, 12 % load regulation | light load below 40 mA | – | CA-IS bus side 5.5 V max (D) | unknown | ⚠ measure |
| Isolation barrier | – | – | – | – | B0505S-2WR3 1500 VDC / 1 min, against 5 kVrms transceivers and the ≥ 2.5 kVrms requirement | **not met** | ⚠ D-09 |

**Conclusion.** In the design case the chain fits with 15 % at the FETs and the LM5164. It does not fit in the double fault (latch failed, SCD only), with a reversed parallel pack, or if the TVS reaches its rated clamp. All of these rest on the mandatory short-circuit bench test (A §6) and decision D-04.

---

## 7. AFE summary (section C)

* **Part:** BQ76952PFBR (C2862742, 11 814 in stock) rather than BQ7695202PFBR (83 in stock). CRC and REG1 come from the EOL OTP image.
* **Host link:** I2C Fast + CRC (Comm Type 0x12), 400 kHz, on MCU I2C1 PA15 / PB7 (both FT_f). SPI is rejected: it would cost the CFETOFF / HDQ NTC inputs. No isolator is needed, because the AFE and MCU share `GND_PWR`.
* **Pull-ups.** **INTEGRATOR PROPOSAL:** 4.7 kΩ (C's value, FAQ 4.7–10 k) **to `AFE_REG1`** (B's rail), with 100 Ω series at the AFE.
* **Pin highlights:**

| Pin(s) | Use |
|---|---|
| VC0–15 / VC16 | R_VC 100 Ω (20 Ω on VC16), C_DF 220 nF, no common-mode caps; VC0 tied to VSS on the PCB |
| TS1 / TS3 / HDQ | pack NTCs 1–3, 1 nF |
| TS2 | wake from SHUTDOWN via BAV170 to `WAKE_BTN_RAW` |
| CFETOFF | FET-bank NTC (OTF, MCU-independent) |
| DFETOFF | BOTHOFF, driven by the gate-kill AND (§5.2) |
| DDSG / DCHG | REG1 push-pull, active-low fault outputs (0xAA) |
| ALERT | open-drain, 10 kΩ to `AFE_REG1` |
| REG0 / REGIN / BREG | FCX495TA + 3.3 kΩ + separate diode, 22 nF, 10 MΩ |
| CP1 | 2.2 µF 50 V |
| BAT | BAT_SNS (J_CELL1 pin 18) → 1N4148WS → 100 Ω → 1 µF 100 V |
| LD / PACK | 10 kΩ 1206 to `PACK+` |
| FUSE | DNP driver to a pack-powered breaker / fuse coil (§10 conflict 10.s) |

* **Balancing:** TI NPN option (SS8050 + 33 Ω 1 W + 220 Ω + 1N4148WS). About 118–129 mA per cell; odd / even groups, ≤ 8 cells; ≤ 3.0 W on the bank; ≈ 25 h per 1 % of 280 Ah. Plus the J_ABAL1 active-balancer header (`BAL_EXT_EN`).
* **LFP image highlights:** the thresholds in §5.1; USER_AMPS 100 mA; CC Gain 74.768 (then calibrated); Body Diode Threshold 1000 mA; Sleep Current / Wake Comparator 1 A; balancing Min Cell V 3400 mV; SEAL with customer keys; runtime PF-to-OTP allowed at pack voltage.
* **Production:** OTP at 11.5 V on BAT_SNS / CELL_16 with no cells, 2-point cell calibration, board offset, CC gain, then OTP write and lock (C §9).

Full table and pin list: [C §2, §8](docs_architecture/C_afe.md).

---

## 8. MCU pin map (STM32G473RCT6 LQFP-64, D §2.2 reconciled)

ROM = what the bootloader does with BOOT0 = 1 (AN2606 Rev 62). **Bold rows** changed during integration.

| Pin | Port | Net | Function / AF | Dir | Default / external | Type | Note |
|---|---|---|---|---|---|---|---|
| 1 | VBAT | **`VBAT_MCU`** | RTC backup | S | **BAT54C OR (+3V3, AFE_REG1)** (B), 100 nF; supercap DNP | – | D had +3V3 only |
| 2 | PC13 | **`WAKE_BTN_N`** | EXTI13 / WKUP2 | in | **1 MΩ pull-up to `AFE_REG1`** (B) | FT | was 100 kΩ to +3V3 (D). With +3V3 off, that pull-up would hold Q_BTN on and the board could never sleep |
| 3 / 4 | PC14 / PC15 | `OSC32_IN/OUT` | LSE 32.768 kHz | – | FC-135, 18 pF, LSEDRV = 11 | FT | |
| 5 / 6 | PF0 / PF1 | `OSC_IN/OUT` | HSE 8 MHz | – | – | FT_fa / FT_a | |
| 7 | PG10-NRST | `MCU_NRST` | NRST | bi | TPS3823 RESET, SWD, 100 nF | FT | also a U_KILL1 input |
| 8 | PC0 | `HEATER_EN` | TIM1_CH1 AF2 | out | 100 kΩ PD | FT_a | |
| 9 | PC1 | `EXT_OUT1` | TIM1_CH2 AF2 | out | 100 kΩ PD | TT_a | |
| 10 | PC2 | `EXT_OUT2` | TIM1_CH3 AF2 | out | 100 kΩ PD | FT_a | |
| 11 | PC3 | `FAN_PWM` | TIM1_CH4 AF2 | out | 100 kΩ PD | TT_a | 25 kHz |
| 12 | PA0 | `ISENSE_OUT` | ADC12_IN1 + COMP3_INP | an | INA240 on `+3V3_A` ⇒ ≤ VDDA | TT_a | |
| 13 | PA1 | `RS485_INV_DE` | USART2_RTS_DE AF7 | out | CA-IS3082 DE pull-down | TT_a | |
| 14 | PA2 | `RS485_INV_TX` | USART2_TX AF7 | out | – | FT_a | ROM TX: harmless |
| 15, 31, 47, 63 | VSS | `GND_PWR` | – | S | – | – | |
| 16, 32, 48, 64 | VDD | `+3V3` | – | S | 4 × 100 nF + 4.7 µF | – | |
| 17 | PA3 | `RS485_INV_RX` | USART2_RX AF7 | in | – | TT_a | not a flash port |
| 18 | PA4 | `FRAM_CS_N` | GPIO | out | 10 kΩ PU | TT_a | |
| 19–21 | PA5–PA7 | `SPI1_SCK/MISO/MOSI` | SPI1 AF5 | – | – | TT_a | FRAM + flash |
| 22 | PC4 | `EXP_SCL` | I2C2_SCL AF4 | od | 4.7 kΩ PU to +3V3 | FT_fa | |
| **23** | **PC5** | **`PG_5V`** | GPIO / EXTI5 | in | U1 PGOOD, PU to +3V3 (B) | TT_a | +3V3-referenced, so TT is fine. Was `AFE_ALERT` |
| 24 | PB0 | `ISENSE_OUT` (2nd) | ADC1_IN15 + COMP4_INP | an | – | TT_a | |
| 25 | PB1 | `RS485_LINK_DE` | LPUART1_RTS_DE AF12 | out | DE PD | TT_a | |
| 26 | PB2 | `NTC_SHUNT` | ADC2_IN12 | an | 10 kΩ from `+3V3_A` | TT_a | |
| 27 / 28 / 29 | VSSA / VREF+ / VDDA | `GND_PWR` / `+3V3_A` / `+3V3_A` | – | S | 100 nF + 1 µF / 10 nF + 1 µF | – | |
| 30 / 33 | PB10 / PB11 | `RS485_LINK_RX/TX` | LPUART1 AF8 | – | – | TT_a | |
| 34 / 35 | PB12 / PB13 | `CAN_LINK_RX/TX` | FDCAN2 AF9 | – | TX 4.7 kΩ PU | TT_a | |
| 36 | PB14 | `NTC_MUX` | ADC1_IN5 | an | CD4051 output | TT_a | |
| 37 | PB15 | `BUZZER` | TIM15_CH2 AF1 | out | 100 kΩ PD | TT_a | |
| **38** | **PC6** | **`PWR_HOLD`** | GPIO | out | **1 MΩ PD** + `PWR_EN` RC hold ≈ 0.76 s (B) | FT_f | D had a pull-up. The RC rides through the 200 ms TPS3823 reset; a hung MCU is reset, not held on |
| 39 | PC7 | `FLASH_CS_N` | GPIO | out | 10 kΩ PU | FT_f | |
| 40 | PC8 | `OC_TRIP_N` | EXTI8 | in | latch output | FT_f | |
| 41 | PC9 | `FAN_TACH` | TIM3_CH4 AF2 | in | 10 kΩ PU, 1 kΩ series | FT_f | |
| 42 | PA8 | `EXP_SDA` | I2C2_SDA AF4 | od | 4.7 kΩ PU | FT_a | |
| 43 / 44 | PA9 / PA10 | `SVC_TX/RX` | USART1 AF7 | – | – | FT_fda | ROM flash port (USB-C) |
| 45 / 46 | PA11 / PA12 | `CAN_INV_RX/TX` | FDCAN1 AF9 | – | TX 4.7 kΩ PU | FT_u | |
| 49 / 50 | PA13 / PA14 | `SWDIO` / `SWCLK` | SWD | – | internal | FT_f | |
| 51 | PA15 | `AFE_SCL` | I2C1_SCL AF4 | od | **4.7 kΩ to `AFE_REG1`** + 100 Ω | FT_f | FT required, checked |
| 52 / 53 | PC10 / PC11 | `ESP_RXD` / `ESP_TXD` | UART4 AF5 | – | 1 kΩ series | FT / FT_f | |
| 54 | PC12 | `WDI` | GPIO | out | floating = WDT disabled | FT | |
| 55 | PD2 | `OC_CLR` | GPIO | out | 100 kΩ PD | FT | |
| 56 | PB3 | `SWO` | TRACESWO | out | – | FT | |
| 57 | PB4 | `KILL_N` | EXTI4 | in | U_KILL2 output | FT_c | |
| 58 | PB5 | `AFE_RST_SHUT` | GPIO | out | 10 kΩ PD | FT_f | |
| 59 | PB6 | `FET_EN` | TIM8_CH1 AF5 | out | 100 kΩ PD → kill | FT_c | TIM8 break forces 0 |
| 60 | PB7 | `AFE_SDA` | I2C1_SDA AF4 | od | **4.7 kΩ to `AFE_REG1`** + 100 Ω | FT_f | |
| 61 | PB8-BOOT0 | `MCU_BOOT0` | BOOT0 | in | 10 kΩ PD | FT_f | |
| **62** | **PB9** | **`AFE_ALERT`** | GPIO / EXTI9 | in | **10 kΩ PU to `AFE_REG1`** | **FT_f** | moved from PC5 (TT_a). PB9 is not used by the ROM (AN2606 Table 101). FT abs max = VDD + 4.0 V = 4.0 V at VDD = 0 (DS473 p.78) ≥ 3.3 V |

EXTI lines in use: 4, 5 (`PG_5V`), 8, 9 (`AFE_ALERT`), 13; no conflict. A WKUP pin is not needed for `AFE_ALERT`: Standby uses Stop 1, which wakes from any EXTI, and Sleep powers the MCU off and wakes through Q_ALRT → `PWR_EN` (B §4).

**Expanders (D §2.4), changes:**
* U801 P07 = `DFETOFF_RB` (new).
* U801 P14 = spare (was `EN_SENSE`).
* U802 P14 = **`EN_12V`** (new, 100 kΩ PD; it had no pin).
* The remaining assignments are as in D.

**Dropped / unplaced:**
* `OC_SET_MCU_N` is dropped. It would need a COMPx_OUT pin, and D's COMP → TIM8 break → `FET_EN` gives the same effect on the FETs.
* `RTC_WAKE` (B option) has no pin: PC13 RTC_OUT1 carries `WAKE_BTN_N`. Its footprint stays DNP and unconnected until an RTC_OUT alternative is found (unverified).

---

## 9. Communications and connectors (D §3)

* **Isolated CAN × 2:** CA-IS3050CW (SOIC16-WB, CAN FD 5 Mbps, 5 kVrms, 8 mm creepage, logic side 3.0–5.5 V on `+3V3`). Firmware sets 500 kbit/s classic for inverters; FD is possible on the pack link.
* **Isolated RS-485 × 2:** CA-IS3082WX (500 kbps, 1/8 UL, true fail-safe receiver, DE internal pull-down, 8 mm creepage). Bias resistors DNP.
* **Isolated supply:** one `GND_ISO` domain, B0505S-2WR3 2 W behind TPS22918 (`EN_ISO`, ≈ 1 ms ramp). `+5V_ISO` is **not** exported on any RJ45.
* **Terminations:**
  * CAN: split 2 × 60.4 Ω + 4.7 nF, one DIP pole per leg (SW601a/b, SW602a/b). The inverter port is ON by default; the link port is ON only at the chain ends.
  * RS-485: 120 Ω through one pole (SW601c / SW602c).
  * The DIPs sit on the isolated side, about 17–21 mA per pole against a 25 mA listing rating (unverified).
* **TVS:** PESD1CAN per CAN port and PSM712 per RS-485 port, ≤ 5 mm from the RJ45. CMC ACT45B-510 is a DNP footprint.
* **Creepage:**
  * ≥ 8 mm slot / gap under each isolator, in a row along the connector edge (D §4). This meets the ≥ 6.5 mm target.
  * RJ45 shields go to `CHASSIS` via 1 nF 2 kV ∥ 1 MΩ to `GND_ISO` (values unverified).
  * USB-C service has its own domain `GND_USB` (CH340C + ISO7721DR). Never merge it with `GND_PWR`.
  * Power board: ≥ 2.0 mm between HV and return copper on outer layers, ≥ 1.0 mm between HV B2B pins, ≥ 4 mm around lugs (A §10.4).

**RJ45 pinout** (Seplos / PACE / JBD / Daly convention; LINK-IN and LINK-OUT wired 1:1):

| Pin | J601 INV-CAN | J602 INV-485 | J603 / J604 LINK |
|---|---|---|---|
| 1 | NC (opt. `RS485_INV_B`, DNP) | `RS485_INV_B` | `RS485_LINK_B` |
| 2 | NC (opt. `RS485_INV_A`) | `RS485_INV_A` | `RS485_LINK_A` |
| 3, 6 | `GND_ISO` | `GND_ISO` | `GND_ISO` |
| 4 | `CANH_INV` | NC | `CANH_LINK` |
| 5 | `CANL_INV` | NC | `CANL_LINK` |
| 7 | NC (opt. `RS485_INV_A`) | `RS485_INV_A` | `RS485_LINK_A` (opt. `ADDR_OUT`) |
| 8 | NC (opt. `RS485_INV_B`) | `RS485_INV_B` | `RS485_LINK_B` (opt. `ADDR_IN`) |

CAN-link on pins 4 / 5 means a link bus cannot mix brands (D §3.5).

Other connectors:
* J301 SWD 2 × 5 1.27 mm;
* J605 USB-C;
* J801 front panel (optional);
* J_CELL1 Micro-Fit 2 × 9;
* J_NTC1 XH-8;
* J_ABAL1 XH-4;
* J502 fan PH-3;
* J501 dry contacts (part not found);
* J_HTR, J_EXT1/2, J_FUSE1 (DNP);
* power lugs 4 × M6 200 A.

---

## 10. Reconciled interface-signal table

PD = pull-down, PU = pull-up. Sections: A, B, C, D; **I** = changed by the integrator (INTEGRATOR PROPOSAL — owner to confirm).

| Signal | Source → destination | MCU pin / port | Pull resistor | Default / fail-safe | From |
|---|---|---|---|---|---|
| `AFE_DFETOFF` | U_KILL1 AND3 → BQ DFETOFF (pin 30), active-low | – (read-back on U801 P07) | **100 kΩ PD at the BQ pin** | asserted (BOTHOFF) | A, C, D, **I** |
| `DFETOFF_RB` | `AFE_DFETOFF` node → U801 P07 | U801 P07 | – | – | **I** |
| `FET_EN` | MCU → U_KILL1, high = permit | PB6 TIM8_CH1 | 100 kΩ PD | kill | A, D (B wanted a PU: D-01) |
| `MCU_NRST` | TPS3823 / NRST → U_KILL1 | NRST | internal PU | low in reset → kill | A, D |
| `OC_TRIP_N` | U_LATCH1 Q → U_KILL1, MCU | PC8 EXTI8 | – (100 kΩ PD only if U8 is kept) | powers up tripped | A, C, D |
| `OC_CLR` | MCU → latch CLK, rising edge | PD2 | 100 kΩ PD | no clear | A, D |
| `KILL_N` | U_KILL2 → MCU, U_KILL3 | PB4 EXTI4 | – | low = kill | A, D |
| `KILL` | U_KILL3 → BSS123 gates | – | – | 0 unpowered | A |
| `AFE_FLT_DSG_N` / `AFE_FLT_CHG_N` | BQ DDSG / DCHG → U_KILL2, U801 P04 / P05 | U801 P04 / P05 | **470 kΩ PD** | Hi-Z → fault | A, C (100 k), B (1 M), **I** |
| `AFE_ALERT` | BQ ALERT (open-drain) → MCU, Q_ALRT gate | **PB9 EXTI9** | **10 kΩ PU to `AFE_REG1`** | high | C, B, D, **I** |
| `AFE_SCL` / `AFE_SDA` | MCU I2C1 ↔ BQ | PA15 / PB7 | **4.7 kΩ PU to `AFE_REG1`** + 100 Ω series | idle high; dead when the AFE is off | C, B, D, **I** |
| `AFE_RST_SHUT` | MCU → BQ RST_SHUT | PB5 | 10 kΩ PD | normal | C, D |
| `AFE_REG1` | BQ REG1 → island | – | – | off only in SHUTDOWN | C, B |
| `WAKE_BTN_N` | button (via BAV170) → MCU, Q_BTN gate | PC13 EXTI13 | **1 MΩ PU to `AFE_REG1`** | released | B, C, D, **I** |
| `WAKE_BTN_RAW` | button contact → D_WAKE1 cathode; J801; Remote-ON opto | – | – | – | C, B, D |
| `AFE_TS2_WAKE` | BQ TS2 → D_WAKE1 anode | – | – | – | C |
| `PWR_HOLD` | MCU → `PWR_EN` OR | PC6 | **1 MΩ PD** | off (RC hold 0.76 s) | B, D, **I** |
| `PWR_EN` | OR node → U1 EN/UVLO | – | 1 MΩ ∥ 1 µF | off | B |
| `PG_5V` | U1 PGOOD → MCU | **PC5 EXTI5** | PU to +3V3 | – | B, **I** |
| `EN_ISO` / `EN_ESP` | MCU → U7 / U6 EN | U801 P10 / P11 | 100 kΩ PD | off | B, D |
| `EN_12V` | MCU → U5 EN | **U802 P14** | 100 kΩ PD | off | B, **I** |
| `EN_SENSE`, `+3V3_SENSE` | – | – | – | **deleted** (§5.4) | B, **I** |
| `ESP_EN` / `ESP_BOOT` | U801 → ESP EN / GPIO9 | U801 P12 / P13 | RC / internal PU | ESP held / SPI boot | D |
| `ISENSE_OUT` | INA240 → MCU ADC + COMP, U_OCP1 | PA0, PB0 | – | 1.65 V at 0 A | A, D |
| `NTC_FET` | RT_FET1 → BQ CFETOFF | – | internal 18 k | – | A, C |
| `NTC_SHUNT` | NTC at the shunt → MCU | PB2 | 10 kΩ from `+3V3_A` | – | A, C, D |
| `NTC_PACK4..6`, `NTC_BAL`, `NTC_AMB` | NTCs → CD4051 → MCU | PB14 (`NTC_MUX`) | 10 kΩ from `+3V3_A` | – | C, D |
| `MUX_S0..2`, `MUX_INH` | U802 → CD4051 | U802 P10–P13 | INH 100 kΩ PU | mux off | D |
| `HEATER_EN` | MCU → heater level stage (+12V) | PC0 | PD (100 kΩ at the MCU, 10 kΩ at the gate) | off | A, D |
| `EXT_OUT1` / `EXT_OUT2` | MCU → EXT gate drive | PC1 / PC2 | 100 kΩ PD | off | A, D |
| `AFE_FUSE` | BQ FUSE → Q_FU1 (DNP, C §7) | – | 100 kΩ PD | off | C, A, **I** (A's OR into EXT1 dropped) |
| `BAL_EXT_EN` | MCU → Q_ABAL1 | U801 P15 | 100 kΩ PD | off | C, D |
| `FAN_PWM` / `FAN_TACH` | MCU ↔ fan | PC3 / PC9 | PD / 10 kΩ PU | off | D, B |
| `BUZZER` | MCU → Q801 | PB15 | 100 kΩ PD | silent | D |
| `DRY1` / `DRY2` | U801 → photoMOS LED | U801 P16 / P17 | – | open | D, B |
| `LED_SOC1..6`, `LED_RUN`, `LED_ALM` | U802 → LEDs (anodes on +3V3) | U802 P00–P07 | 1 kΩ series | off | D, **I** (B had 5 V) |
| `DIP_ADDR0..3`, `DI_AUX1` | SW801 / input → U801 | U801 P00–P03, P06 | 10 kΩ PU | – | D |
| `EXP_SCL` / `EXP_SDA` | MCU I2C2 ↔ U801 / U802 / J801 | PC4 / PA8 | 4.7 kΩ PU to +3V3 | – | D |
| `CAN_INV_TX/RX`, `CAN_LINK_TX/RX` | MCU ↔ U601 / U602 | PA12 / PA11, PB13 / PB12 | TX 4.7 kΩ PU | recessive | D |
| `RS485_INV_TX/RX/DE`, `RS485_LINK_TX/RX/DE` | MCU ↔ U603 / U604 | PA2 / PA3 / PA1, PB11 / PB10 / PB1 | DE internal PD | receive | D |
| `SVC_TX/RX` | MCU ↔ ISO7721 ↔ CH340C | PA9 / PA10 | – | – | D |
| `ESP_RXD` / `ESP_TXD` | MCU ↔ ESP UART0 | PC10 / PC11 | 1 kΩ series | Hi-Z while the ESP is off | D |
| `SPI1_*`, `FRAM_CS_N`, `FLASH_CS_N` | MCU ↔ U1001 / U1002 | PA5–PA7, PA4, PC7 | CS 10 kΩ PU | deselected | D |
| `WDI` | MCU → TPS3823 | PC12 | floating | WDT disabled until firmware drives it | D |
| `VBAT_MCU` | BAT54C (+3V3, `AFE_REG1`) → VBAT | pin 1 | – | – | B (`MCU_VBAT`), D, **I** (one name) |
| `AFE_CHG` / `AFE_DSG` | BQ 45 / 43 → gate networks (B2B HV) | – | – | – | A, C |
| `AFE_PCHG` / `AFE_PDSG` | BQ 40 / 39 → P-FET gates | – | 1 MΩ G–S | off | A, C |
| `AFE_LD` / `AFE_PACK` | `PACK+` → 10 kΩ → BQ 41 / 42 | – | – | – | A, C |
| `BAT_SNS` | **J_CELL1 pin 18** (2nd CELL_16 contact) → BAT / REG0 diodes | – | – | – | C, B (A had the lug Kelvin via B2B), **I** |
| `SHUNT_K_BAT` / `SHUNT_K_PACK` | shunt Kelvin (2 × 200 Ω per leg) → BQ SRP / SRN filter | – | – | – | C names, A circuit (A: `SRP_K` / `SRN_K`), **I** |
| `INA_K_P` / `INA_K_N` | shunt Kelvin (2 × 10 Ω per leg) → INA240 | – | – | – | A (`SH_P/N_a/b`), **I** (new names) |
| `GATE_CHG`, `GATE_DSG`, `FET_MID` | power nodes | – | 10 MΩ G–S | off | A |
| `VSUP`, `VSUP_F`, `AUX_IN`, `FORCE_ON` | supply tap / AUX | – | AUX 100 kΩ bleeder | – | B |
| `REMOTE_ON` (DNP) | inverter dry contact → opto → `WAKE_BTN_RAW` | – | – | – | B |
| `RTC_WAKE` (DNP) | – | **no pin** | – | – | B, **I** |
| `OC_SET_MCU_N` | – | **dropped** | – | – | A, D, **I** |
| Rails | `+12V`, `+5V`, `+3V3`, `+3V3_A`, `+3V3_ESP`, `+5V_ISO`, `GND_PWR`, `GND_ISO`, `GND_USB`, `CHASSIS`, `BAT±`, `PACK±` | – | – | – | all |

---

## 11. Requirements traceability (`instructions.md` §1–§4)

| Req. | Requirement | Status | How / pointer |
|---|---|---|---|
| §1 | Stationary ESS application | Met | whole design |
| §1 | LFP primary, optional NMC / LCO | **Changed by owner decision** | LFP only (2026-11-17); 100 V FETs do not allow 16S NMC |
| §1.1 | AEC-Q100 / Q101 / Q200 throughout | **Not met** | No STM32G4 is AEC-Q (owner accepted). CA-IS transceivers, ESP32, CH340C, the clone 74LVC1G11 and many passives / connectors are not AEC-Q. AEC parts where kept: LM5164 / 5163 / 5013-Q1, TPS7B82-Q1, TPS22918-Q1, INA240-Q1, TLV1702-Q1 |
| §1.1 | −40 … +105 °C | **Not met** | STM32G473RCT6 is the 85 °C grade (D, DS473 p.221). ESP32-C3-MINI-1-N4 85 °C (−H4 105 °C exists, B Q-B15). Buzzer −20…70 °C, RJ45 −25…70 °C, FC-135 −40…85 °C (D). Realistic v1 rating: −40…85 °C ambient (D-14) |
| §1.2 | Low cost, JLC 4-layer, DFM | Partly | control board on JLC04161H; power board 2 oz with hand-soldered Cu bars and lugs (A §4.6); most power parts are Extended (A Q16) |
| §1.3 | ISO 26262 ASIL B/C principles, IEC 62619, UL 1973, UL 9540A | Partly | independent hardware trip, external watchdog, I2C CRC, CAN CRC, redundant thermal (AFE + MCU). No FMEDA, no certification |
| §2.1 | 16S LFP, 40.0–58.4 V | Met | – |
| §2.1 | Modular scaling to 400–800 V strings | **Not met** | Only parallel packs over RJ45 links. The 1.5 kVDC iso supply cannot sit in a high-voltage string |
| §2.1 | Cell accuracy ±1.5 mV | **Not met** | The BQ76952 is specified at ±15 mV max over −40…85 °C (research 02, TI [S28]). The protection comparators are ±25 mV (C). Typical values unverified; measure and publish |
| §2.1 | 4–8 NTC | Met | 4 pack NTCs (3 in the AFE, 1 on the MCU), up to 6 + mux spare; plus FET, shunt, balancer, ambient, die (C §5, D §5.9) |
| §2.1 | ±200 A continuous / 500 A peak, shunt | Met (design) | 100 µΩ shunt, INA linear −800…+725 A (A §5.3), OCD1 lets 500 A pass. The 500 A duration is still open (D-06) |
| §2.1 | **Isolated** shunt sensing | **Changed** | Not isolated. The high-side FET topology keeps AFE, shunt and MCU on `GND_PWR` (C §2.3) |
| §2.1 | High-resolution coulomb counting | Met | BQ76952 CC is the main gauge (C §8) |
| §2.2 | AFE with HW OV / UV, passive balancing 100–200 mA | Met | 118–129 mA per cell (C §4.3) |
| §2.2 | Isolated SPI / I2C AFE link, 2.5–5 kVrms | **Changed** | Shared ground; I2C + CRC (C D-C1) |
| §2.2 | Automotive MCU (S32K / SPC58 / TMS570) | **Changed by owner decision** | STM32G473RCT6 |
| §2.2 | Contactors + pre-charge | **Changed by owner decision** | FET banks + PDSG / PCHG; `EXT_OUT1/2` for external contactor / breaker |
| §2.2 | Hardware watchdog, fault logging FRAM / flash | Met | TPS3823 + IWDG + AFE HWD; FM25V02A + W25Q64 (D §5.2) |
| §2.2 | Dual CAN-FD, isolated RS-485 | Met | 2 × CA-IS3050CW, 2 × CA-IS3082WX (D §3) |
| §2.2 | Galvanic barrier 2.5–5 kVrms | **Partly** | transceivers 5 kVrms, 8 mm; the B0505S-2WR3 module is 1500 VDC (B §3.6, D-09) |
| §3 | IPC-2221B clearances | Met (planned) | A §10.4 rules |
| §3 | IPC-7351B, IPC-A-610 Class 3 | Not addressed | stock KiCad footprints; assembly class not specified |
| §3 | IEC 60664-1 ≥ 6.5 mm across the barrier | Met (comms) | 8 mm wide-body isolators; module creepage not checked |
| §3 | IEC 62619 secondary hardware OV | Partly | AFE COV + SOV PF act without the MCU; a separate 2LVL protector is not fitted (FUSE path DNP, D-16) |
| §3 | UL 9540A multi-point temperature, anti-propagation | Partly | 9–11 sensors; `DI_AUX1` fire input (D) |
| §4.1 | JLC04161H-7628 stackup | Met (control) / **Changed** (power) | power board 2 oz outer |
| §4.2–4.3 | DRC rules, net classes | Partly | existing rules kept; power-board classes not defined yet |
| §4.4 | Fiducials, tooling holes, LCSC numbers | Partly | §13 lists the wrong LCSC fields to fix |

---

## 12. Parts list (key ICs and power parts)

Stock and B/E as reported by the sections on 2026-11-17 (not re-checked). n/r = not reported.

| Ref-to-be | Part | LCSC | Stock | B/E | From |
|---|---|---|---|---|---|
| Q_CHG1–8, Q_DSG1–8 | Infineon IPT015N10N5 (TOLL, 100 V, 1.5 mΩ) | C108964 | 38 948 | E | A |
| (alt.) | HUAYI HYG015N10NS1TA | C2979263 | 11 353 | E | A |
| Q_CHG_OFF / Q_DSG_OFF, Q_HTR_HS | MMBT5401 | C8326 | 616 368 | B | A |
| D_GZ, D_KZ | BZT52C16S | C19077449 | 56 108 | E | A |
| D_BE / D_KB / D_LD / D_PK | BAS21 | C7502725 | 154 583 | E | A |
| Q_PDSG1, Q_PCHG1 | IRF9540NSTRLPBF | C33903 | 37 014 | E | A |
| R_PRE1 | HoRX-100W-50R-5 % (Al-housed) | C2985693 | **9** | E | A |
| R_PCHG1 | RX24/50W-100 Ω | C49375386 | **13** | E | A |
| D_TVS_B1–4 | 5.0SMDJ60CA | C2990413 | 2 389 | E | A |
| D_TVS_P1–2, D_TVS1 | SMCJ60A | C2996503 (A) / C4154628 (B) | 2 629 / 2 953 | E | A, B (one number to pick) |
| C_B / C_P | CL32B225KCJSNNE 2.2 µF 100 V | C55151 | n/r | E | A |
| R_SH1, R_SH2 | Vishay WSLP5931L2000FEA | C413492 | 937 | E | A |
| U_ISENSE1 | INA240A1QPWRQ1 | C553123 | 1 913 | E | A |
| U_OCP1 | TLV1702AQDGKRQ1 | C130036 | 1 795 | E | A |
| U_LATCH1 | SN74AUP1G74DCUR | C140267 | 17 455 | E | A |
| U_KILL1, U_KILL2 | 74LVC1G11GV (JSM clone) | C53114319 | 14 614 | E | A |
| U_KILL3 | SN74LVC1G04DCKR | C2983744 | 19 202 | E | A |
| Q_KLS_C/D, Q_HTR_LS | BSS123 | C7420338 | 822 704 | E | A |
| Q_KILL_C/D | AO3407A | C347478 | 117 696 | E | A |
| Q_EXT1/2 | SQ2318AES-T1_BE3 | C3280170 | 8 981 | E | A |
| Q_HTR1 | CSD19534Q5A | C114200 | 585 | E | A |
| D_FLY_EXT, D_HTR | SS34 / SS310 | C2837271 / C47018526 | 479 217 / 19 932 | E | A |
| J_BP/BM/PP/PM | XFCN T68160200-1400 (M6, 200 A) | C45384693 | 4 674 | E | A |
| J_B2B (power) | 2 × 15 female 2.54 mm | C5337168 | 1 187 | E | A (male unverified) |
| F_SUP, F_AUX | Littelfuse 0451002.MRL | C99547 | 10 322 | E | B |
| R_DAMP1/2 | HoLRT2512-2W-1R | C5127856 | 28 945 | E | B |
| D2 / D3 | SS320 / ES2D | C18199172 / C2848676 | 304 705 / 28 690 | E | B |
| C_IN1–4 | CL31Y225KCHVPNE 2.2 µF 100 V | C2803390 | 15 894 | E | B |
| U1 (rec.) | TI LM5013QDDARQ1 | C5219285 | 2 572 | E | B alt., **I** |
| U1 (alt.) | TI LM5164QDDARQ1 | C2072225 | 994 | E | B |
| L1 | SWRB1207S-470MT | C169376 | 1 075 | E | B (re-check for LM5013) |
| U5 / L5 | LM5163QDDARQ1 / SWRH1005C-101MT | C2877984 / C72572 | 1 666 / 623 | E | B |
| U3 | TPS7B8233QDGNRQ1 | C5220182 | 209 (LCSC 2 598) | E | B |
| U6 | TLV62569DBVR | C141836 | 639 669 | E | B |
| U7 | TPS22918TDBVRQ1 | C2653760 | 2 943 | E | B |
| U4 | EVISUN B0505S-2WR3 | C7465195 | 5 411 | E | B, D |
| Q_BTN, Q_ALRT | AO3401A | C15127 | 1 517 931 | B | B |
| D_OR, D_BAT1, D_REG0, D_BB | 1N4148WS | C2128 | 3 944 705 (J) | B | B, C |
| D_WAKE1 | BAV170 | C68970 | 11 520 | E | B, C |
| D_VBAT | BAT54C | C466637 | 2 567 | E | B |
| U_AFE1 | TI BQ76952PFBR | C2862742 | 11 814 | E | C |
| Q_BL1–16 | SS8050 | C2150 | 1 862 700 | B | C |
| R_BL1–16 | 33 Ω 1 W 2512 | C53728 | 29 460 | E | C |
| C_DF1–16 | CL10B224KB8NNNC 220 nF | C64705 | 341 140 | E | C |
| Q_REG0 | FCX495TA | C150457 | 1 567 | E | C |
| C_CP1 | CL31B225KBHNNNE 2.2 µF 50 V 1206 | C50254 | 10 / 273 424 (J) | B | C (A proposed C125847; **I**: C50254) |
| C_BAT1 | CL31B105KCHNNNE 1 µF 100 V | C13832 | 195 290 | E | C |
| J_CELL1 | Molex Micro-Fit 430451800 | C293541 | 367 | E | C |
| RT_FET1 + board NTCs | NCP18XH103F03RB | C13564 | 259 330 | E | C |
| D_ESD1–4 | PESD5V0S1BA | C19224 | 79 275 | E | C |
| R_LD1, R_PACK1 | 10 kΩ 1206 (200 V) | C17902 | 509 100 | B | C (A had 0805 C17414; **I**: 1206) |
| Q_FU1 (DNP) | IRLML0100TRPBF | C53658 | 7 260 | E | C |
| U301 | STM32G473RCT6 | C529361 | 2 870 | E | D |
| U302 | TPS3823-33DBVR | C7719 | 59 700 | E | D, B |
| Y301 / Y302 | YXC X50328MSB2GI (5032) / Epson Q13FC13500004 | C115962 / C32346 | 295 250 / 245 265 | n/r / B | D |
| U1001 / U1002 | FM25V02A-GTR / W25Q64JVSSIQ | C66029 / C179171 | 7 358 / 1 048 | E | D |
| U1003 | CD4051BQPWRQ1 | C555142 | 2 306 | n/r | D |
| U801, U802 | TCA9535PWR | C130204 | 14 125 | E | D |
| U601, U602 | Chipanalog CA-IS3050CW | C41784143 | 2 092 | E | D |
| U603, U604 | Chipanalog CA-IS3082WX | C970942 | 10 286 | E | D |
| D601/2, D603/4 | PESD1CAN / PSM712 | C343993 / C2687124 | 49 640 / 137 240 | E | D |
| J601–J604 | KH-RJ45-58-8P8C | C2683360 | 3 695 | E | D |
| U605 / U606 / U607 / J605 | CH340C / ISO7721DR / USBLC6-2SC6 / TYPE-C-31-M-12 | C84681 / C366164 / C7519 / C165948 | 86 800 / 12 955 / 38 690 / 497 290 | E | D |
| U901 | ESP32-C3-MINI-1-N4 | C2838502 | 9 258 | E | D, B |
| U501, U502 | GAQY212GS | C7435107 | 104 360 | E | D |
| SW801, SW601/2 | DSHP04TSGER | C3293144 | 56 144 | E | D |
| SW802 | TS-1187A-B-A-B | C318884 | 526 560 | B | D (replaces B's open BTN1) |
| Q501 | AO3400A | C20917 | 989 942 | B | D |

---

## 13. LCSC field corrections for the existing schematic

Old number → what LCSC returns → correct number (as found by the sections; nothing was edited).

| Ref today | Field LCSC | What it actually is | Correct number | Found by |
|---|---|---|---|---|
| U1 | C444643 | DIO6913TST6 (3 A buck) | C2072225 (LM5164QDDARQ1) | B |
| U2 | C86381 | no record | part removed | B |
| U3 | C352467 | 18 Ω 0402 resistor | C51118 (AP2112K) or C5220182 (TPS7B8233-Q1, recommended) | B, D |
| U4 | C265225 | no record | C7465178 (1 W) / C7465195 (2 W, needed) | D |
| C1 | C134763 | 220 µF / 10 V electrolytic | C2803390 (2.2 µF 100 V) | B |
| J2 | C224345 | NVE IL3285E isolated RS-485 transceiver | J_AUX (owner choice) | B |
| F1, L1, L2 | C2891395, C408332, C344383 | no record | C99547, C169376, (L2 removed) | B |
| U_AFE1 | C2687103 | Fuzetec PTC fuse | C2862742 | C |
| R_BL1–16 | C17936 | 1206 4.7 kΩ | C53728 | C |
| Q_BL1–16 | C85073 | does not exist | C2150 | C |
| C_DF1–16, C_CP1 | C14666 | does not exist | C64705 / C50254 | C |
| R_VC0–16 | C22775 (correct) | MPN field says 1 kΩ | fix MPN → 0603WAF1000T5E | C |
| C_NTC1–4, C_TS_PCB | C1588 | 1 nF, not 10 nF | keep, fix the value | C |
| RT_BOARD | C19702 | 10 µF capacitor | C13564 | C |
| D_ESD_NTC1–4 | C84296 | does not exist | C19224 | C |
| D_BAT1 | C8677 | XH-2Y connector housing | C2128 | C |
| C_BAT1 | C28323 | 1 µF **50 V** on a 58.4 V node | C13832 | C |
| R_SCL1, R_SDA1 | C22822 | 17.8 Ω | C23162 | C |
| J_CELL1 | C224359 | NVE IL610A-2E isolator | C293541 | C |
| J_NTC1–4, J_KELVIN1 | C224345 | NVE IL3285E | C157972 (J_NTC1) | C, PROJECT.md §3 |
| C_R1, C_R18 | C23630 | 2.2 µF 16 V (field says 10 V) | keep | C |
| R_PRE1 | C463124 | NCP1236AD100R2G flyback controller | C2985693 | A |
| Q_POS1 / Q_NEG1 / Q_PRE1 | C148416 | WSP4805 dual P-FET | C3280170 | A |
| U_MCU1 | C529329 | STM32G030 | C529361 (G473RCT6) | research summary §4, D |
| U_WDOG1 | C80145 | no record | C7719 | B, D |
| U_MEM1 | C5426 | no record | replaced by C66029 | D |
| U_485_1 | C395353 | FPC connector | C2671361 (part removed) | D |
| U_ISO_* | C129202 | zener, 0 stock | C366164 / C2867808 | D |
| U_CAN1 | C385473 | 220 kΩ THT resistor | C58988 (part removed) | D |
| SW_CFG1 | C318884 | tactile switch | C3293144 (rec.) or C3312443 | D |
| D_TVS_CAN1 / D_TVS_485_1 | C12948 / C19002 | no record | C343993 / C2687124 | D |
| Y1 | C115962 | YXC X50328MSB2GI 5032, not the 3225 MPN | keep the number, fix the footprint | D |

---

## 14. Consolidated open decisions for the owner

Each row gives the recommendation and its consequence. Source tags: A Qn, B Q-Bn, C Qn, D Qn, I = integrator.

### Blocking (needed before schematic work)

| # | Decision | Recommendation | Consequence |
|---|---|---|---|
| D-01 | `FET_EN` default and live output in Sleep (B Q-B4, D Q1, I-5) | **Pull-down; Sleep = output off, AFE monitoring.** Live output stays available in Standby (≈ 5.9 mA) | MCU-independent kill stays armed whenever the board is on. Loses Seplos-style live output at µA. The alternative (PU to `AFE_REG1`, logic on REG1) also needs `MCU_NRST` and `OC_TRIP_N` defaulted "OK", so the latch and watchdog kill are off in Sleep |
| D-02 | Kill on every MCU reset (`MCU_NRST` in the AND) (D Q1) | Keep | Each watchdog or software reset drops the output (≈ 200 ms TPS3823 delay + boot, est.); the FETs never run without a live host |
| D-03 | Two-board stack vs one 220 × 100 mm board (A Q4) | Stack | Kelvin pair and gate drive cross the B2B; same control board for 100–200 A |
| D-04 | 100 V FET margin; reversed parallel pack (A Q6, Q12) | Keep 100 V plus controlled t_f and the bench short test; footprint for the AN09 reverse clamp; 120–150 V TOLL fallback | 0 % margin in the SCD-only double fault and a negative margin with a reversed pack (§6) |
| D-05 | Inverter DC-link capacitance and pre-DC-link standby current (A Q1) | Owner to supply. 50 Ω if ≤ 0.05 A, else 25 Ω | Sets R_PRE1 and the predischarge settings |
| D-06 | 500 A peak duration / repetition; charge current rating (A Q2, C Q2) | Owner to supply | OCD1 delay, OCC and the shunt pulse check |
| D-07 | `+12V`: keep as a switched leaf; EXT coil supply and current (B Q-B1, Q-B2, A Q10) | Keep (heater gate + fan need it); LM5163-Q1 without EXT coils, LM5164-Q1 with them; pull-in ≤ 0.40 A | Drives U5 choice and EXT usefulness |
| D-08 | `+5V` trunk converter (B Q-B9, I-8) | **LM5013-Q1** (3.5 A, 27 % peak) | The LM5164 would sit at 96 % of 1 A; LM5013 pin-out and inductor to verify |
| D-09 | Isolated supply and barrier rating (B Q-B5) | 1 × 2 W for v1; owner to accept 1.5 kVDC or fund a transformer-driver design | The ≥ 2.5 kVrms requirement stays "Partly" |
| D-10 | Isolated transceivers and creepage (D Q3, Q4) | CA-IS3050CW + CA-IS3082WX, keep 6.5 mm (8 mm parts) | Wide-body footprints; cheapest option |
| D-11 | `AFE_DFETOFF` driven by A's AND gate; pin moves `AFE_ALERT` → PB9, `PG_5V` → PC5 (D Q2, I-1, I-2) | Accept | C's Q_DOFF1 / R_DOFF1 / D_DOFF1 removed; 100 kΩ PD at the BQ pin |
| D-12 | Hard-fault policy: every AFE fault kills both banks (A Q7) | Accept, with firmware limits inside the BQ limits (§5.1) | COV / OCC also block discharge while asserted |
| D-13 | Delete `+3V3_SENSE` / `EN_SENSE` (A Q13, I-6) | Delete; INA on `+3V3_A` | +2.3 mA in Standby and Fault; no blind-trip state |
| D-14 | Product temperature rating (D Q13, B Q-B15) | Declare −40…85 °C ambient for v1; ESP −H4 only if 105 °C is kept as a goal | §1 requirement stays "Not met" |
| D-15 | `BAT_SNS` from the cell connector (C) rather than the lug Kelvin (A) (I-10.b) | Cell connector pin 18 | The AFE does not see the lug transient; frees a B2B HV pin |
| D-16 | FUSE pin topology and secondary protector (C Q5, A §9.1, I-10.s) | C's pack-powered J_FUSE1 path (DNP); drop A's diode-OR into EXT_OUT1 | A +12V-powered trip coil fails whenever `+12V` is switched off, so it is not MCU-independent |

### Before layout

| # | Decision | Recommendation | Consequence |
|---|---|---|---|
| D-17 | Lugs M6 vs M8, cable size (A Q5) | M6 XFCN plus a footprint for a second lug | 200 A basis unverified |
| D-18 | Heatsink supplier and maximum ambient (A Q14) | ≤ 0.75 K/W plate at 40 °C | sets the power-board outline |
| D-19 | Hand-soldered Cu bars and lugs after PCBA (A Q15) | Accept | manual assembly step |
| D-20 | Extended-part cost (A Q16) | Accept for v1 | JLC set-up fees |
| D-21 | OC window +599 / −305 A; firmware COMP tier (A Q3) | Accept; COMP tier via TIM8 break | final divider values |
| D-22 | Shunt TCR 125 ppm (A Q11, C Q11) | Accept, with `NTC_SHUNT` compensation | ≈ 0.4–0.5 % residual before compensation |
| D-23 | PCHG path populate (A Q8) | Populate | recovery charge after a hardware CUV |
| D-24 | Heater: pad voltage, power, harness fuse, hardware thermostat (A Q9, B Q-B3) | Pack-voltage FET, ≤ 5 A, bimetal in the pad | heater harness at pack potential |
| D-25 | DDSG / DCHG pull-down value (B §5.3, C, I-4) | **470 kΩ** | Fault-as-Hi-Z holds with ±1 µA input leakage (0.47 V, calc); 1 MΩ gives 1 V, which is not guaranteed low; +7.4 µA in Sleep |
| D-26 | `PWR_HOLD` policy (D Q16) | B's 1 MΩ PD + 0.76 s RC hold | a hung MCU is reset by the TPS3823, not held on |
| D-27 | Dry contacts: photoMOS ≤ 60 V vs relays (B Q-B12, D Q7) | photoMOS | no 230 VAC switching |
| D-28 | RJ45 INV-CAN pins 1 / 2 / 7 / 8 (D Q5) | NC with DNP 0 Ω options | – |
| D-29 | Manual DIP termination vs auto (D Q6) | Manual DIP | – |
| D-30 | SOC LEDs 4 vs 6 (D Q8) | 4 + 2 DNP | – |
| D-31 | Buzzer: keep, drop, or a −40 °C part; limit its 95 mA (D Q9) | Drop for v1, or a series resistor | it is the largest +3V3 load (78 % peak) |
| D-32 | ESP antenna in a metal enclosure (D Q10) | Plastic window or an external-antenna module | – |
| D-33 | USB-C isolated service port (D Q12) | Fit | ≈ $1.2 |
| D-34 | MCU NTC count / mux (D Q14) | 8:1 mux + `NTC_SHUNT` direct | – |
| D-35 | Front-panel J801 (D Q17), Remote-ON opto (B Q-B10), AUX range / connector (B Q-B8), RTC in Ship / supercap (B Q-B7), main-lug keying (B Q-B13), RS-485 bias DNP (B Q-B6) | J801 footprint; opto DNP; 9–58 V AUX; supercap DNP; keyed lugs; bias DNP | small footprint items |
| D-36 | PF SOCC 300 A vs OCC 220–300 A and latch 293 A (I, §5.1) | C to re-check the ordering | risk of a PF before the faster layers act |
| D-37 | Harness: inline tap fuses, B− first, 103AT probes (C Q6); active-balancer module and enable interface (C Q8) | Fuses yes; B− first; 103AT | – |

### Firmware / production

| # | Decision | Recommendation | Consequence |
|---|---|---|---|
| D-38 | AFE variant (C Q1) | BQ76952PFBR | CRC and REG1 from OTP; the fixture must handle a blank part |
| D-39 | HWD timeout 10 s, output drop during firmware update (C Q3) | 10 s; the bootloader keeps talking to the AFE | – |
| D-40 | SUV PF at 2.0 V with PF_OTP (C Q4) | Keep | an over-discharged pack is permanently disabled |
| D-41 | Security keys, LOCK_CFG / PERM_SEAL (C Q7) | Per-unit keys; no PERM_SEAL | – |
| D-42 | Ship auto-shutdown at 2.3 V / cell (C Q9) | Accept | the pack goes dark until button or charger |
| D-43 | Autonomous balancing fallback (C Q10) | Keep 0x0F | – |
| D-44 | Comms wake only in Standby; `EN_ISO` policy (B Q-B11, D Q15) | Accept | no bus wake from Sleep / Ship |
| D-45 | OTP fixture with `FORCE_ON` and pull-ups on `AFE_REG1` (B Q-B14) | As B §8.2; the fixture supplies pull-ups if REG1 is down | – |
| D-46 | ESP32 may reflash the STM32 through ROM USART3 (D Q11) | DNP straps | the radio does not control the safety MCU by default |
| D-47 | CAN FD vs classic rates per port (D §3.2) | 500 k classic on the inverter port; FD on the link | – |

Counts: **16 blocking, 21 before layout, 10 firmware / production** (47 in total).

---

## 15. Unverified items (merged, deduplicated)

* **Bench tests (mandatory):**
  * short-circuit test at 58 V with a 1–2 µH loop; tune R_OFF, R_G and the snubber; run with the latch on and off;
  * DDSG / DCHG and DFETOFF / BOTHOFF response times;
  * the 15–20 µs t_f;
  * all loss, thermal, inductance and timing figures (A §6, §7, §4.5).
* **Data sheets not read (listing ratings only):**
  * TLV1702, SN74AUP1G74, 74LVC1G11 (clone; Ioff and VIL used in §5.2 / D-25), SN74LVC1G04, AO3407A (VGS max), BSS123, MMBT5401, BAS21, BZT52C16S;
  * IRF9540NS (SOA), CSD19534Q5A, SQ2318AES (RDS(on) at 3.3 V, pin-out);
  * 5.0SMDJ60CA / SMCJ60A (surge curves, IFSM), WSLP5931 pulse curve, XFCN lug 200 A basis, HoRX / RX24 energy;
  * CH340C, KH-RJ45, PESD1CAN / PSM712, GAQY212GS IF(on), CD4051 Ron.
* **BQ76952:**
  * DFETOFF pin abs max against the 3.3 V AND drive. C's own design also pulled it to REG1 (3.3 V).
  * LD / PACK pin abs max against the 96.8 V pack-side clamp.
  * Whether DDSG / DCHG assert on BOTHOFF.
  * AFE SLEEP current with the drivers off.
  * FUSE drive level and application topology.
  * CC Gain range (AN32 vs TRM).
  * COV delay encoding.
  * Predischarge exit logic.
  * REG0 / REG1 increment in SLEEP.
* **STM32G473 (RM0440 not opened):**
  * DAC → COMP INM mapping; TIM break from COMP;
  * UCPD dead-battery Rd on PB4 / PB6;
  * RTC_OUT behaviour on VBAT and an RTC_OUT pin other than PC13;
  * AN2606 Rev 71 (Rev 62 was read);
  * DS12712 AF-table anomalies: confirm in CubeMX;
  * whether a higher temperature code than 6 (DS473 p.221) is stocked.
* **Power tree:**
  * converter efficiencies;
  * LM5013-Q1 pin-out and inductor;
  * LM5163 ↔ LM5164 footprint;
  * TPS7B82 dropout at 233 mA and junction temperature at 85 °C ambient;
  * FB1 ferrite current rating with ≈ 11 mA on `+3V3_A`;
  * B0505S-2WR3 output below its 40 mA minimum load, isolation and creepage;
  * F_SUP opening time; R_DAMP pulse energy.
* **Leakage:**
  * BAV170 at 85 °C;
  * opto dark current on the TS2 node;
  * TCA9535 port behaviour with VCC = 0 while DDSG / DCHG are driven from REG1. A series resistor may be needed.
* **Overvoltage:**
  * the share of the lug overshoot that reaches the cell taps;
  * IPC-2221B B3 and IEC 60664-1 values quoted from memory;
  * JLC 2 oz minimum track / gap.
* **Loads:** fan, EXT coils, buzzer at 3.3 V, dry-contact LEDs, FRAM / flash / TCA9535, MCU peripheral adder, VDDA, CA-IS logic-side and loaded RS-485 currents, J801.
* **Parts and stock:**
  * no LCSC part yet for: the mating male B2B header, the power freewheel diode, the 22 nF INA filter cap, the 1 MΩ P-FET G–S resistors, the 0.1 % divider resistors, the EXT gate buffer, J501, J_AUX, the harness mating parts;
  * low stock: R_PRE1 (9), R_PCHG1 (13), TPS7B8233 (209 at JLC);
  * stock changes daily; re-check in the JLC BOM tool.
* **Other:**
  * SS8050 VCE(sat) at 100 mA, hFE at −40 °C, survival of > 25 V during a partial plug;
  * B3380 NTC error with the 103AT polynomial;
  * active-balancer enable interfaces;
  * ESP antenna keep-out;
  * Victron / Pylontech cable pin-outs.

---

## 16. Links

* Detailed sections (unchanged apart from a header line):
  * [A — power stage](docs_architecture/A_power_stage.md)
  * [B — power tree](docs_architecture/B_power_tree.md)
  * [C — AFE](docs_architecture/C_afe.md)
  * [D — MCU, comms, I/O](docs_architecture/D_mcu_comms_io.md)
* Research: `docs/research/00_SUMMARY.md` and `01`–`05`.
* Plans (background only): `docs/plans/`.
* Project facts and decisions log: `PROJECT.md`. Original requirements: `instructions.md`.
* References to `bms_work/review/...` inside sections B and C point to the off-repository working folder (`%TEMP%\bms_work`). The review notes there are not part of this repository.
