> Detailed section; where it conflicts with ../ARCHITECTURE.md, ARCHITECTURE.md wins.

# B — Power tree, power budget, sleep / wake / ship, input protection

Part B of the architecture for the 16S LFP ESS BMS (200 A, on-board high-side FET banks driven by the BQ76952, STM32G473RCT6, ESP32-C3, 2 × CAN, 2 × RS-485). **Architecture only.** No project or KiCad file was changed.

Date: 2026-11-17.

**Inputs read:**
* `PROJECT.md`, including the decisions log.
* `instruction.md` §3.2 / §8 and `instructions.md`.
* `docs/research/00_SUMMARY.md`, `01_bq76952_features.md`, `02_competitors.md` and `05_system_features_mcu.md`.
* `DESIGN_NOTES.md` and `01_Power_Supply.kicad_sch`.
* The requirements review (`bms_work/review/requirements_review.md`).
* The sibling architecture parts `A_power_stage.md` (A) and `C_afe.md` (C), for interface alignment.

**Evidence labels:**
* **[DS-x p.n]**: a datasheet page opened this session. Sources are listed in §13.
* **calc**: my arithmetic.
* **est.**: an estimate.
* **unverified**: not checked in any document.
* **[LCSC]**: the LCSC product API (`wmsc.lcsc.com/ftps/wm/product/detail`), read live this session.
* **[JLC]**: `jlcsearch.tscircuit.com`, read live this session, for JLC stock and Basic / Extended.

---

## 0. Summary of the key choices

| # | Choice | Why (short) |
|---|---|---|
| B1 | **Supply tap on `BAT+`, the cell side of the high-side FETs**, through a fuse, a damping resistor and a series diode into a protected node `VSUP`. The AFE `BAT` / REG0 stay on their own cell-sense feed (part C §3) | The BMS keeps running with both FET banks off (fault, pre-charge, ship wake). The 200 A path carries no BMS-supply parts |
| B2 | **U1 LM5164-Q1 is kept but re-pointed to `+5V` direct (1 A)**, with RON fixed to GND (41.2 kΩ → 303 kHz). **`+12V` becomes a separate switched buck U5** (LM5163-Q1 0.5 A, or LM5164-Q1 1 A on the same footprint), enabled by the new `EN_12V` | One converter in the always-on path gives the lowest standby current. +12V loads (fan, heater relay, EXT coils) are now optional and off in standby, and a fault there cannot pull down the logic. The LMR16006Y cannot take pack voltage and is no longer needed |
| B3 | **`+3V3` = TPS7B8233-Q1 LDO from +5V** (AEC-Q100, 300 mA, IQ 1.9 µA). It replaces the AP2112K (55 µA, 85 °C, not AEC) | Clean analog rail for VDDA / VREF+ / INA240 REF. Pd 0.19 W in HVSSOP (calc) |
| B4 | **`+3V3_ESP` = TLV62569 2 A buck from +5V**, enabled by `EN_ESP` (no extra load switch) | WiFi TX peak 350 mA [DS-ESP p.21]. The buck's own EN gives 0.1 µA off |
| B5 | **`+5V_ISO` = one 2 W unregulated module (B0505S-2WR3, 400 mA) behind a TPS22918 load switch (`EN_ISO`)** | Worst case 2 × (CAN dominant + RS-485 driving) ≈ 270 mA = 68 % (calc). The present 1 W / 200 mA part would be at 135 %. Option: 2 × 1 W (Q-B5) |
| B6 | **`+3V3_SENSE` (new) = TPS22918 from +3V3, enabled by `EN_SENSE`**, for the INA240 and the external OC comparator / latch | INA240 IQ 1.8–2.4 mA [DS-INA p.6] is gated off in Sleep. The AFE's own SCD / OCD comparators keep protecting in SLEEP [DS-BQ p.52] |
| B7 | **Power latch:** `PWR_EN` (U1 EN/UVLO) = diode-OR of `PWR_HOLD` (MCU), `AFE_ALERT` (inverted, from the `AFE_REG1` island), the button (inverted, same island), `AUX_IN` and the `FORCE_ON` pads, plus an RC hold (1 µF / 1 MΩ, ≈ 0.76 s) | The board can turn fully off while the AFE keeps protecting and watching for charger or load. Every wake source works with the MCU unpowered |
| B8 | **States: Ship 8 µA, Sleep ≈ 47 µA (output live), Standby ≈ 5 mA (comms alive), Run ≈ 19 mA typ** (calc / est., §6) | Competitors list sleep at Seplos ≤ 50 µA, JBD 0.4 mA and Daly ~0.5 mA, and run at 40–45 mA (`02_competitors.md` table). Ship beats them 6–60×. Sleep beats JBD / Daly by about 10× and matches Seplos **with the pack output still live** |
| B9 | **AUX bench input fixed:** fuse + 200 V silicon diode into `VSUP`, 9–58 V range. **OTP:** 10–12 V on `BAT` / `VC16` through the cell connector, with the board powered from AUX or from B+ at 11.5 V | Today AUX has no fuse or TVS and back-feeds +12V. OTP needs BAT 10–12 V with no cells [DS-BQ p.9] |

**Errors found in the current sheet-01 fields** (LCSC API, this session; this belongs to the part audit, question 10 in `PROJECT.md`):

| Ref | Field LCSC | What that number really is |
|---|---|---|
| U1 | C444643 | **DIO6913TST6** (a 3 A buck). LM5164QDDARQ1 is **C2072225** |
| U3 | C352467 | an **18 Ω 0402 resistor** |
| C1 | C134763 | a **220 µF / 10 V electrolytic** on the 58 V input node. The field says 10 µF 100 V |
| J2 | C224345 | an **NVE IL3285E digital isolator** |
| U2 | C86381 | no record |
| F1 | C2891395 | no record |
| L1 | C408332 | no record |
| L2 | C344383 | no record |

---

## 1. Power tree

```
 Cells ── BAT+ busbar (cell side of the CHG/DSG FET banks, part A) ──[ Q_CHG | Q_DSG ]── PACK+
            │   (BAT+ clamp: 4 × 5.0SMDJ60CA + MLCC, part A §4.3)
            │
            │ supply tap (thin track / B2B pin, taken at the B+ lug, NOT through the FETs)
            ▼
   F_SUP 0451002 2 A very-fast 125 V ── R_DAMP 2 × 1 Ω 2 W ──●── VSUP_F
                                                            │
                                                            └─ D2 SS320 (200 V Schottky) ──┐
   J_AUX (9–58 V bench / OTP) ── F_AUX 0451002 ── D3 ES2D (200 V Si) ── AUX_IN ──┬─────────┤
                                                       R_AUXB 100 k to GND_PWR ┘          │
                                                                                          ▼
                     VSUP 6…58.4 V  ═ D_TVS1 SMCJ60A ═ C_IN 4 × 2.2 µF 100 V ═ (to GND_PWR)
                        │                                   │
        PWR_EN ──► U1 LM5164-Q1 (303 kHz, 47 µH)            U5 LM5163-Q1 / LM5164-Q1 (302 kHz, 100 µH) ◄── EN_12V
                        │                                   │
                       +5V  1.0 A                          +12V 0.5 A (or 1 A): FAN, HEATER relay, EXT_OUT1/2 coils (option)
                        │
          ┌─────────────┼───────────────────────┬──────────────────────────┬─────────────────────┐
          │             │                       │                          │                     │
   U3 TPS7B8233-Q1   U6 TLV62569 ◄ EN_ESP   U7 TPS22918 ◄ EN_ISO        SOC/RUN/ALM LEDs      DRY1/2 drive,
   LDO 300 mA        buck 2 A                │                          (5 V anode, OD pins)  buzzer
          │             │                    U4 B0505S-2WR3 2 W ═══╪═══ +5V_ISO / GND_ISO  (CAN ×2, RS-485 ×2)
        +3V3          +3V3_ESP (ESP32-C3)                   1.5 kVDC barrier
          │
          ├─ FB ── +3V3_A (VDDA, VREF+)
          └─ U8 TPS22918 ◄ EN_SENSE ── +3V3_SENSE (INA240, OC comparator / latch)

 AFE island (part C §3, not on VSUP):  BAT_SNS (CELL_16 contact) ─ D_REG0 ─ 3k3 ─ Q_REG0 ─ REGIN → REG1 = AFE_REG1 3.3 V (≤ 5 mA)
     AFE_REG1 feeds: DDSG/DCHG drive, BOTHOFF pull-up, gate-kill logic, AFE I2C pull-ups (proposed, §5.5),
                     WAKE_BTN_N / AFE_ALERT pull-ups + the two wake inverters, MCU_VBAT (with +3V3)

 Grounds: GND_PWR = BAT- star at the shunt cell-side Kelvin (part C pin 17). GND_ISO only behind U4 and the isolators.
```

**Wake / power-latch detail:**

```
            AFE_REG1 (3.3 V whenever the AFE is not in SHUTDOWN)
              │1M            │10k (moved from +3V3, see §5.5)
 WAKE_BTN_RAW─┤BAV170├─WAKE_BTN_N ──► MCU (FT pin, EXTI)        AFE_ALERT (open-drain, active-low) ──► MCU (FT pin, EXTI)
   │ (button  │ common │    │                                         │
   │  to GND) │ cathode│   G│ Q_BTN AO3401A (S = AFE_REG1)           G│ Q_ALRT AO3401A (S = AFE_REG1)
   │          │        │    D──|>|─┐ 1N4148WS                        D──|>|─┐ 1N4148WS
 AFE_TS2_WAKE ┘                    │                                        │
                 PWR_HOLD (MCU) ──|>|──●── PWR_EN ── U1 EN/UVLO     ◄────────┘
                 AUX_IN ──470k──|>|────┤      │
                 VSUP ──1M── FORCE_ON pads ───┤   C_EN 1 µF ║ R_EN 1 MΩ to GND_PWR (hold ≈ 0.76 s, calc)
                 (opt.) RTC_WAKE (PC13) ─|>|──┘   (DNP)
```

---

## 2. Input protection from the pack

### 2.1 Where the supply is taken

* **Tap point:** `BAT+` at the B+ lug, on the cell side of the back-to-back FET banks (part A §2).
  * This rail stays alive with CHG and DSG both off: fault, pre-charge, ship wake, and UV recovery with a charger.
  * No BMS supply current flows through the FETs.
  * If the tap were on `PACK+`, the BMS would black itself out on its first protection trip.
* **Return:** `GND_PWR` = `BAT-` at the cell-side shunt Kelvin (part C pin 17). The board's own consumption (≈ 19 mA typ, §6) is therefore not seen by the shunt. Firmware adds it as a self-discharge term in the SOC.
* **The AFE `BAT` and REG0 do not use `VSUP`.** They take their own fused-by-design `BAT_SNS` contact on the cell connector, each through its own diode (part C §3; [DS-BQ p.64, p.75]). This keeps `REGIN ≤ BAT` true in AUX-only bench mode ([DS-BQ p.46]).

### 2.2 Overvoltage: TVS clamp versus every downstream absolute maximum

Downstream absolute maximums:

| Part on VSUP / derived | Absolute max | Source |
|---|---|---|
| LM5164-Q1 / LM5163-Q1 VIN, EN/UVLO | 100 V (VIN), 100 V (EN recommended maximum) | [DS-LM5164 p.4], [DS-LM5163 p.4] |
| SS320 D2 / ES2D D3 reverse | 200 V | [DS-SS320 p.1], [LCSC] |
| C_IN, CL31Y225KCHVPNE | 100 V rated | [LCSC] |
| BQ76952 `BAT` (own feed, part C) | 85 V | [DS-BQ p.7] |

**TVS choice: D_TVS1 = SMCJ60A, unidirectional, after D2.**
* Ratings: VRWM 60 V, VBR 66.7–73.7 V, IR ≤ 1 µA at VRWM, VC 96.8 V at 15.5 A (10/1000 µs), 1500 W [DS-SMCJ p.2].
* 58.4 V (16 × 3.65 V) sits below VRWM, so leakage at full charge stays at the 1 µA class.
* It sits in the same 60 V family as the power-stage clamp 5.0SMDJ60CA (VBR 66.7 V, VC 96.8 V at 51.7 A; part A §4.3). The two therefore start conducting together.
* **Alternative:** SMCJ58A (Bourns, VC 93.6 V at 16.1 A [DS-SMCJ p.2]). Its clamp is 3 V lower, but VRWM 58 V is below 58.4 V, so leakage at full charge rises (unverified).

**Clamp check (calc).** The `BAT+` busbar is held by the part-A clamp to ≤ 96.8 V. R_DAMP (2 Ω) limits the current into D_TVS1:
* I = (96.8 − 73.7 V) / 2 Ω ≈ **11.6 A**.
* With the 10/1000 µs slope, VC ≈ 73.7 + (96.8 − 73.7) × 11.6 / 15.5 ≈ **91 V**.
* That is **< 100 V LM5164 VIN**, a margin of 9 %. With the 8/20 µs data point (VC 125.8 V at 77.5 A [DS-SMCJ p.2]) the linear estimate is lower still, ≈ 77 V. Both are linear interpolations, hence the "est." mark.
* Without R_DAMP, the TVS current would be set only by the trace and fuse resistance, and VC could exceed 100 V at 8/20 currents (121.7 V at 80.5 A for SMCJ58A [DS-SMCJ p.2]).
* **Cross-part condition:** this holds only if part A keeps `BAT+` ≤ ≈ 100 V at its design short-circuit turn-off (part A §6, t_f 15–20 µs).

**Why not a sustained overvoltage?** `BAT+` is the cell stack, and with back-to-back high-side FETs the CHG body diode blocks charging current when CHG is off. `BAT+` cannot sit above the stack voltage (≤ 58.4 V), so the TVS only ever sees µs-to-ms transients. This is inferred from the topology in part A.

### 2.3 Hot-plug inrush, LC overshoot and fuse I²t

Input capacitance: C_IN = 4 × 2.2 µF 100 V (two per buck, per the LM5164 typical application CIN 2.2 µF [DS-LM5164 p.1]), 8.8 µF nominal. The X7S DC-bias loss is ignored, which is the worst case for I²t.

| Item | With R_DAMP 2 Ω (rec) | Without R_DAMP (fuse + ~0.1 Ω wiring) |
|---|---|---|
| Peak inrush, 58.4 V hot-plug (calc) | 58.4 / 2.09 ≈ 28 A, τ ≈ 18 µs | ≈ 580 A (wiring-limited) |
| I²t ≈ V²C / 2R (calc, `instruction.md` §8 formula) | 58.4² × 8.8 µF / (2 × 2.09) = **0.0072 A²s** | 58.4² × 8.8 µF / 0.2 = **0.15 A²s** |
| vs fuse nominal melting I²t 0.53 A²s (0451002 [DS-LF451 p.2]) | **74×** margin | 3.5× (below the ≥ 5× rule in review P7) |
| LC damping, L ≈ 1 µH tap lead (est.): ζ = R / (2√(L/C)), √(L/C) = 0.34 Ω | ζ ≈ 3, overdamped, **no overshoot** (calc) | ζ ≈ 0.15. An ideal LC rings to ≈ 1.6–1.9 × 58.4 V = **95–110 V**, the classic hot-plug spike (calc) |
| Steady drop / loss at 0.37 A worst (§3) | 0.74 V / 0.27 W (2 × 2 W parts) | – |

**F_SUP = Littelfuse 0451002.MRL** (Nano2, very fast-acting, 2 A, 125 V):
* Interrupting rating **10 000 A at 75 VDC** in the 2 A row [DS-LF451 p.2]. A direct cell-stack short downstream of the fuse is therefore within rating (58.4 V < 75 V). The 1 A row of the same table does not print the 75 V rating, so 2 A is chosen.
* Run current is ≤ 0.46 A even at 2.0 V/cell (§3), 23 % of rating. Slow-blow is not needed because R_DAMP removes the inrush.
* Fault in the downstream short case: 58.4 V / 2 Ω = 29 A, about 15× rating, opening in ms (est.; the time-current curve was not read). R_DAMP then absorbs about 29² × 1 Ω × 2 ms ≈ 1.7 J per resistor (est.). The pulse rating of the 2512 part is **unverified** and is an owner / bring-up check.

### 2.4 Reverse polarity

| Case | Result |
|---|---|
| Supply tap or AUX connector reversed | **D2 / D3 block** (200 V rating ≥ 58.4 V plus residual VSUP). The TVS sits after D2 and is never forward-biased, so F_SUP survives. This is better than the old "crowbar and blow F1" arrangement |
| Cell connector reversed | The AFE `BAT` diode blocks the supply (part C). VC pins: harness keying only |
| **Main B+ / B− lugs swapped** | **Not survivable** for the AFE, the gate drive or the TVS array; competitors behave the same. Mitigation: different stud sizes or keyed, coloured lugs, and the pack main fuse. Owner question Q-B13 |

D2 uses a Schottky for its low drop at 0.3 A. D3 uses a **silicon** fast diode (ES2D, IR 5 µA at 200 V [LCSC]). The reason: in Sleep, D3 is reverse-biased by VSUP, and Schottky leakage (SS320: 10 mA at rated VR at 100 °C [DS-SS320 p.2]) would charge `AUX_IN` and turn on `PWR_EN` through the 470 kΩ. R_AUXB 100 kΩ bleeds the remaining µA (calc: 5 µA × 100 kΩ = 0.5 V on AUX_IN → ≤ 0.35 V on PWR_EN, below the 1.1 V shutdown threshold [DS-LM5164 p.5]).

---

## 3. Rails and budget

### 3.1 Rail budget

| Rail | Source → regulator | Load typ / peak (mA) | Limit | % used (peak) | Note |
|---|---|---|---|---|---|
| `VSUP` | BAT+ tap / AUX → F, R, D | 21 / 290 at 51.2 V (calc from rows below, η 0.85 est.); 460 at 32 V | F_SUP 2 A | 23 % | |
| `+5V` | U1 LM5164-Q1 | 162 / 759 | 1 A rated; valley limit 0.95 A min [DS-LM5164 p.6] | **76 %** (80 % of valley min) | Peak = WiFi TX + both buses fully dominant + buzzer, all at once |
| `+12V` (switched) | U5 LM5163-Q1 | 0 / 225 (fan + relay) | 0.5 A; IPEAK 0.63 A min [DS-LM5163 p.6] → about 0.47 A DC with 0.32 A ripple (calc) | 48 % | With EXT coils on +12V, fit LM5164-Q1: 725 mA / 1 A = 73 % |
| `+3V3` | U3 TPS7B8233-Q1 from +5V | 60 / 114 | 300 mA [DS-TPS7B82 p.6] | 38 % | Pd = 1.7 V × 0.114 A = 0.19 W × 63.9 °C/W = **+12 °C** (calc, [DS-TPS7B82 p.5]) |
| `+3V3_A` | +3V3 through a ferrite | 3 / 6 (est.) | – | – | VDDA, VREF+ only |
| `+3V3_SENSE` | U8 TPS22918 from +3V3 | 2.3 / 3.4 | 2 A (1.5 A at 85 °C) [DS-TPS22918 p.4] | < 1 % | |
| `+3V3_ESP` | U6 TLV62569 from +5V | 30 (BLE, est.) / 350 | 2 A [DS-TLV62569 p.4] | 18 % | 350 mA is 802.11b TX at 20.5 dBm [DS-ESP p.21] |
| `+5V_ISO` | U7 + U4 B0505S-2WR3 | 43 / 270 | 400 mA [DS-EV2W p.1] | **68 %** | Minimum load 40 mA (10 %) [DS-EV2W p.1]. See §3.6 |
| `AFE_REG1` (part C) | BQ76952 REG1 | 0.1 / 2 | 5 mA budget (part C §3.4); 45 mA IC limit | 40 % of budget | Load list in §5.5 |

### 3.2 `+5V` loads (every load)

| Load | typ mA | peak mA | Basis |
|---|---|---|---|
| U3 input (= +3V3 load, LDO) | 60 | 114 | §3.3 |
| U6 input: ESP 350 mA × 3.3 / (5 × 0.85) | 23 (BLE ≈ 30 mA est.) | 272 | [DS-ESP p.21]; η est. |
| U7/U4 input: out / η, η = 84 % at full load [DS-EV2W p.1]; no-load ≈ 8 mA [DS-EV2W p.1] | 62 | 321 | §3.6 |
| SOC × 4 + RUN + ALM LEDs, 2 mA each, 5 V anode | 12 | 12 | est. (`instruction.md` §3.3 LED rule) |
| Dry contacts DRY1/2 as photoMOS (2 × 5 mA LED) | 5 | 10 | est.; relays would need 2 × 30–40 mA (Q-B12) |
| Buzzer (optional) | 0 | 30 | unverified (`05_system_features_mcu.md` §4.2) |
| Rail-indicator LEDs | 0 | 0 | **DNP** (§5.7) |
| **Total** | **162** | **759** | calc |

### 3.3 `+3V3` loads

| Load | typ mA | peak mA | Basis |
|---|---|---|---|
| STM32G473 Run 170 MHz (29.5 / 34 mA at 85 °C with all peripherals disabled) plus peripherals (FDCAN × 2, USART × 4, SPI, I2C, ADC × 2, timers) | 45 | 60 | [DS-G473 p.86 Table 21]; the peripheral adder is est. |
| ISO7721 VCC1, 5 devices, 1 Mbps: 1.6 / 2.8 mA each | 8 | 14 | [DS-ISO7721 p.14]. Device count belongs to comms |
| FRAM + 8 MB flash (program burst) | 0.1 | 25 | unverified |
| TCA9535, TPS3823 (15 / 25 µA), RTC/LSE, straps | 0.2 | 0.5 | [DS-TPS3823 p.7]; the rest est. |
| I2C4 pull-ups 2 × 4.7 kΩ (AFE bus pull-ups go to AFE_REG1, §5.5) | 0.7 | 1.4 | calc |
| `+3V3_SENSE`: INA240 1.8 / 2.4 mA + OC comparator / latch | 2.3 | 3.4 | [DS-INA p.6]; comparator est. |
| VDDA (`+3V3_A`) | 3 | 6 | est. |
| USB-C service bridge | 0 | 0 | on VBUS (`05_system_features_mcu.md` §4.1) |
| **Total** | **≈ 60** | **≈ 114** | calc |

### 3.4 `+12V` loads (switched by `EN_12V`)

| Load | mA | Basis |
|---|---|---|
| Fan, `FAN_PWM` / `FAN_TACH`, 80–120 mm 12 V | 80–150 | unverified |
| Heater relay coil (`HEATER_EN`). The heater element itself is pack-powered (part A / Q-B3) | 30–75 | est. |
| `EXT_OUT1` / `EXT_OUT2` (breaker shunt-trip / external contactor coils), only if their coils are on +12V | 2 × 100–250 hold, 0.5–1 A pull-in | unverified; review P4 |
| **Without EXT on +12V** | **≤ 225** → LM5163-Q1, 48 % | calc |
| **With EXT on +12V** (economised, one pull-in at a time) | **≤ 725 hold** → LM5164-Q1, 73 %. A simultaneous pull-in exceeds 1 A | calc |

### 3.5 Which rails are still needed now that the contactors are gone

| Rail | Keep? | Reason |
|---|---|---|
| `+12V` | **Keep, but as an optional switched leaf** (U5 on its own footprint, DNP-able) | Today it is the trunk of the tree and limits everything (review P4). The only remaining users are the fan, the heater relay and the optional EXT coils. **It could be dropped** if the owner accepts a 5 V fan and 5 V relay and puts EXT coils on pack voltage or an external supply (Q-B2); that saves U5, L5, 3 µA in Ship and about $2.5 (calc from [JLC] prices). Recommended: keep the footprint and decide per variant |
| `+5V` | **Keep, it becomes the trunk** | Iso module input (5 V class), LEDs (5 V anode rule), ESP buck input, LDO input |
| `+3V3` | Keep | MCU and logic |
| `+3V3_A` | Keep | VDDA / VREF+ filtering |
| `+3V3_ESP` | **New** | WiFi peaks must not hit the MCU rail. The AP2112 would see ΔT ≈ 140 °C (`05_system_features_mcu.md` §4.1) |
| `+3V3_SENSE` | **New** (needs a name; see the interface table) | Gating the INA240 and the comparator |
| `+5V_ISO` | Keep, resized | §3.6 |

### 3.6 Upgrade options compared

**+5V trunk:**

| Option | Peak margin | Standby | Cost (JLC 1–9) | Verdict |
|---|---|---|---|---|
| **A (rec): U1 LM5164-Q1 → +5V direct**, 41.2 kΩ RON | 76 % of 1 A | one converter: IQ 10.5 µA [DS-LM5164 p.5] | $12.55 (C2072225; $8.08 at 100+) | Keeps the verified part. Only the topology and RON change |
| A′: LM5013-Q1 → +5V (100 V, 3.5 A) | 22 % | sleep 10 µA, shutdown 3.1 µA [DS-LM5013 p.5] | $6.47 (C5219285) | If the owner wants headroom (e.g. powered RJ45 accessories) or a lower price. Different pin-out (unverified) |
| B: keep LM5164 → +12V → upgraded 1.5–2 A 5 V buck | +12V at 1.1–1.2 A with EXT loads ✗ | two converters in series; 12 V cannot be switched off | – | Not recommended |

**Calc for option A:**
* FSW = 5 × 2500 / 41.2 = 303 kHz [DS-LM5164 p.10 Eq.1].
* tON at 58.4 V = 5 / (58.4 × 303 k) = 283 ns, above the 50 ns minimum. At 10 V it is 1.65 µs, below the 10 µs maximum [DS-LM5164 p.4].
* FB divider 316 k / 100 k → 1.2 × 4.16 = 4.99 V (VREF 1.2 V [DS-LM5164 p.5]).
* ΔI_L with 47 µH = (58.4 − 5) × 0.0856 / (47 µH × 303 kHz) = 0.32 A p-p.
* Peak 0.76 + 0.16 = 0.92 A, below IPEAK min 1.25 A [DS-LM5164 p.6].
* A COT ripple-injection network (Type 3) is still required (review P5, [DS-LM5164 p.10–11]).

**+12V (U5):** RON 100 kΩ → 302 kHz (review P3). With 100 µH, ΔI_L = (58.4 − 12.1) × 0.207 / (100 µH × 302 kHz) = 0.32 A p-p (calc). The 47 µH of today's L1 would give 0.68 A, too high.

**+3V3:**

| Option | IQ | Temp / AEC | Stock (JLC) | Verdict |
|---|---|---|---|---|
| **TPS7B8233QDGNRQ1 (rec)** | 1.9 / 5 µA [DS-TPS7B82 p.5] | AEC-Q100, 300 mA | 209 (LCSC 2 598); the WSON variant C2869742 has 623 | rec; order stock early |
| AP2112K-3.3TRG1 (today) | 55 / 80 µA [DS-AP2112 p.4] | 85 °C, not AEC (review P10) | 29 988 (C51118) | fallback only |

**+3V3_ESP:**

| Option | Verdict |
|---|---|
| **TLV62569DBVR (rec)**: 2.5–5.5 V in, 2 A, IQ 35 µA, ISD 0.1 / 2 µA [DS-TLV62569 p.1, p.4]; 639 669 in stock, $0.07 | rec. It is off in Sleep, so the 35 µA does not count |
| LMR16006YDDCR (same family as U2): 600 mA, 58 % at a 350 mA peak, $0.80 | alternative |
| LDO from +5V (AMS1117) | ✗: 0.6 W at peak and mA-class IQ |

**+5V_ISO.** The per-domain worst case is calc'd from datasheet maxima:

| Item | mA | Source |
|---|---|---|
| TJA1051 dominant | 70 max | [DS-TJA1051 p.2] |
| THVD1450 driving 54 Ω | ≈ 50 (est.) + 3 quiescent | [DS-THVD1450 p.10] |
| ISO7721 VCC2 | 3 × 2.8 | [DS-ISO7721 p.14] |
| Bias (if fitted) | 4 | calc: 5 V / 1240 Ω |
| **Per domain** | **≈ 135** | calc |

Two domains: 270 mA.

| Option | Load | Verdict |
|---|---|---|
| Today: B0505S-1WR3, 200 mA | 135 % ✗ | review / research finding confirmed |
| **1 × B0505S-2WR3 2 W (rec)**, EVISUN C7465195 (5 411 JLC) | 68 % | rec: one part, one `EN_ISO`, keeps the contract names |
| 2 × B0505S-1WR3 (one per domain: inverter port / parallel link) | 68 % each | Better fault and ground-loop separation, and the link domain can stay off in Standby (≈ −2 mA). Needs new names `+5V_ISO2`, `GND_ISO2`, `EN_ISO2` (Q-B5) |
| Transformer driver (SN6505B class) + transformer + iso LDO | regulated output, own EN | Not searched this session. Consider it if the light-load overvoltage below or the 1.5 kVDC rating is unacceptable |

Two module caveats:
* **Light load:** the module is unregulated, with load regulation 12 % over 10–100 % for 5 V outputs and a 40 mA minimum load [DS-EV2W p.1, p.3]. In Standby the bus side draws about 20–26 mA, below the minimum, so the output may rise above TJA1051 VCC max 5.5 V [DS-TJA1051 p.2] (unverified). Measure at bring-up; the mitigation is a ≈ 15 mA dummy load switched with the bus mode, or a regulated module.
* **Isolation:** the module is rated **1500 VDC / 1 min** [DS-EV2W p.3], against the "≥ 2.5 kVrms" in `instructions.md` §2.2 (Q-B5).

**Do not export `+5V_ISO` on the RJ45s** without a PTC (review K8). Fitting the RS-485 failsafe bias is optional because the THVD1450 has failsafe (review K7); DNP saves 4 mA per domain.

### 3.7 Parts on sheet 01 today: keep or change

| Ref (today) | Today | Decision | Justification |
|---|---|---|---|
| U1 | LM5164-Q1, RON to VIN (2.4 MΩ) | **Keep the part.** RON 41.2 kΩ to GND, FB 316 k / 100 k, output +5V, EN = `PWR_EN` | 100 V VIN gives margin over the 91 V clamp (§2.2); IQ 10.5 µA, shutdown 3 µA, AEC-Q100 [DS-LM5164 p.1, p.5]. RON must go to GND [DS-LM5164 p.3] (review P3) |
| U2 | LMR16006YQ5 → +5V from +12V | **Remove.** Optional reuse: the LMR16006YDDCR (adj) can serve as the `+3V3_ESP` alternative | VIN max 40 V [DS-LMR16006 p.4], so it cannot sit on VSUP. 600 mA is too small for the new +5V budget |
| U3 | AP2112K-3.3 | **Replace** with TPS7B8233-Q1 | 85 °C, not AEC, IQ 55 µA (review P10, R18/R19) |
| U4 | B0505S-1WR3 | **Replace** with B0505S-2WR3 + U7 load switch | 135 % load in the new comms set (§3.6) |
| D1 | SMCJ64A, on a bidirectional symbol, reversed | **Replace** with SMCJ60A, unidirectional, cathode to VSUP, after D2 | Review P1 / P2 |
| D2 | SS310 100 V | **Replace** with SS320 200 V | Survives reverse polarity plus a VSUP residual (§2.4) |
| D3 | SS34 into +12V | **Replace** with ES2D into VSUP, + F_AUX | Leakage in Sleep (§2.4); AUX gets a fuse |
| F1 | 0466002 (63 V class) | **Replace** with 0451002.MRL (125 V, 10 kA at 75 VDC) | Review P7; [DS-LF451 p.2] |
| C1 | field = 220 µF / 10 V e-cap | **Replace** with 4 × 2.2 µF 100 V X7S | Field error (§0) |
| L1 | 47 µH (unverified number) | **Keep the value** for U1 at 303 kHz: SWRB1207S-470MT | ΔI 0.32 A (calc) |
| D4 / D6 / D7 / D8 | rail LEDs | **DNP** (or ≥ 10 kΩ) | §5.7 |
| R_PG1 | PGOOD to +12V | **PGOOD → `PG_5V`, pulled up to +3V3** | Used for brown-out warning (§7) |
| J2 | 2-pin header, field = isolator | **J_AUX** 2-pin, polarised connector (owner picks) | §8 |

---

## 4. Sleep / wake / ship: the chain

### 4.1 Chain, from AFE to MCU

1. **BQ76952 power modes:**
   * NORMAL: 286 µA [DS-BQ p.10].
   * SLEEP: 24 µA with DSG in source-follower, 41 µA with DSG in 11 V overdrive [DS-BQ p.10–11]. Comparator protections stay on, and the part exits on current, charger, fault or RST_SHUT < 1 s [DS-BQ p.52].
   * DEEPSLEEP: 9.2–10.7 µA, no protection, FETs off [DS-BQ p.11, p.52–53].
   * SHUTDOWN: 1 / 3.1 µA, FETs off. It exits on TS2 pulled low (0.7–1.1 V) or on LD rising above 0.8–2.25 V [DS-BQ p.9, p.11, p.53].
   * **DEEPSLEEP is not used:** it costs 10× SHUTDOWN and gives no protection.
2. **TS2 = button wake from SHUTDOWN**, wired as in part C: TS2 ─ BAV170 ─ `WAKE_BTN_RAW` ─ BAV170 ─ `WAKE_BTN_N`.
   * In SHUTDOWN TS2 is a weak ≈ 5 V source (4.6 MΩ) [DS-BQ p.11]. BAV170 leakage is 5 nA (part C), giving 23 mV of droop (calc). No false wake.
   * **Change requested from part C:** the `WAKE_BTN_N` pull-up goes to **`AFE_REG1` (1 MΩ)**, not +3V3. Otherwise the button cannot wake a board whose +3V3 is off (Sleep).
   * The MCU reads `WAKE_BTN_N` on an FT pin. An FT pin tolerates the 3.3 V of the island with VDD = 0; positive injection is 0 mA on FT/TT pins [DS-G473 p.79], so no back-powering.
3. **Charger wake:**
   * From SHUTDOWN via LD, which part A / C wire through 10 kΩ to `PACK+` [DS-BQ p.53, p.75]. A charger on `PACK+` raises LD above 2.25 V.
   * From SLEEP via PACK > TOS + delta [DS-BQ p.52].
4. **AFE_ALERT as a wake output.**
   * Alarm mask includes WAKE ("wakened from SLEEP"), INITCOMP, SSA / SSBC and PF (TRM Table 6-8 and Alarm Status ≈ p.102; the part C mask 0xFA69 already contains these).
   * ALERT is open-drain active-low (part C). **Change requested:** pull-up R_ALRT1 to `AFE_REG1` instead of +3V3.
   * Q_ALRT inverts it into the `PWR_EN` OR.
5. **`PWR_EN`** = diode-OR of:
   * `PWR_HOLD`, the button inverter, the ALERT inverter;
   * `AUX_IN` (470 kΩ, bench = always on);
   * `FORCE_ON` (two pads: VSUP via 1 MΩ, for the first power-up of a blank AFE and for the EOL fixture);
   * optional `RTC_WAKE`.
   
   C_EN 1 µF ∥ R_EN 1 MΩ stretch a short button press: 3.0 V decays to the 1.4 V enable-falling threshold in τ·ln(3.0 / 1.4) = **0.76 s** (calc; [DS-LM5164 p.5]). That covers the 3 ms soft-start, the 200 ms TPS3823 reset delay ([LCSC] listing) and the MCU boot before `PWR_HOLD` takes over. EN accepts up to 100 V [DS-LM5164 p.4], so the FORCE_ON path (VSUP / 2 ≈ 29 V) is safe, and the 1N4148WS (100 V) block it from the 3.3 V sources.
6. **MCU `PWR_HOLD`.** The MCU latches U1 on, then raises `EN_SENSE`, `EN_ISO`, `EN_ESP` and `EN_12V` as needed. To go down, it drops `PWR_HOLD` after clearing ALERT.
7. **MCU low-power modes** [DS-G473]:
   * Stop 1 with RTC (LSE): 84.5 µA at 25 °C / 660 µA at 85 °C (p.105).
   * Standby + RTC: 0.66 µA / 2.1 µA (p.107).
   * VBAT + RTC: 0.525 µA / 0.91 µA (p.110).
   * **The G4's Stop current is too high for a µA Sleep.** Sleep therefore switches the whole board off and keeps only the RTC alive on `MCU_VBAT` = BAT54C-OR(+3V3, `AFE_REG1`). VBAT range is 1.55–3.6 V [DS-G473 p.80].
8. **RTC.** The RTC keeps time in Run, Standby and Sleep. In Ship, `AFE_REG1` is off and time is lost unless a coin-cell / supercap footprint (DNP) is fitted (Q-B7).
   * Optional self-wake: RTC alarm on PC13 RTC_OUT1 → diode → `PWR_EN`, footprint DNP.
   * PC13 is supplied through the backup power switch [DS-G473 p.68]. Whether RTC_OUT1 drives in VBAT mode is **unverified** (RM0440 not read).

### 4.2 States

| State | AFE | FETs / `PACK+` | U1 +5V / +3V3 | MCU | ISO / ESP / SENSE / +12V | Entry | Exit (wake) | I_pack at 51.2 V, 25 °C |
|---|---|---|---|---|---|---|---|---|
| **Run** | NORMAL | per protection | on | Run 170 MHz | per need | any wake | – | ≈ 19 mA typ (≈ 26 mA with WiFi) |
| **Standby** (comms alive) | NORMAL → SLEEP when I < Sleep Current | on | on | **Stop 1**, RAM kept | ISO on (RX idle), ESP off or BLE beacon, SENSE off, 12V off | no traffic / button press | CAN_RX / USART RX EXTI, `WAKE_BTN_N`, `AFE_ALERT`, RTC, `PG_5V` | ≈ 5 mA (est., §6.3) |
| **Sleep** (output live) | SLEEP, DSG source-follower (or off by policy) | live (or off) | **off** (`PWR_EN` low) | off; RTC on VBAT | all off | idle timer (no current, no comms) | AFE_ALERT: WAKE on current above the Wake Comparator, charger, fault; button | **≈ 47 µA** (§6.1) |
| **Ship / storage** | SHUTDOWN | off | off | off | off | MCU command (SHUTDOWN subcommand or RST_SHUT high ≥ 1 s [DS-BQ p.48, p.53]); **AFE auto-shutdown** at Shutdown Cell / Stack Voltage (part C: 2.3 V / 36 V) | TS2 button, LD charger; then AFE boots in 200–300 ms [DS-BQ p.53] → INITCOMP → ALERT → `PWR_EN` | **≈ 8 µA** (§6.2) |
| **Fault** | NORMAL, FET(s) off by AFE or `KILL_N` | off (one or both directions) | on | Run: log, ALM LED, DRY1/2 | SENSE on, ISO on | protection trip | recovery per AFE (time / charger / LD); after a timeout → Sleep with FETs off, or Ship if UV | as Run |

**Transitions:**

```
            button / charger(LD)                       wake: current / charger / fault / button / RTC*
   SHIP ────────────────────────────► RUN ◄──────────────────────────────────────── SLEEP
    ▲   AFE auto-shutdown (UV)   ▲     │ │  idle timer (no I, no comms) ──────────────►  ▲
    │   or MCU "ship" command    │     │ └── no traffic ──► STANDBY ── idle timer ──────┘
    └────────────────────────────┼─────┘        ▲   │ RX edge / button / ALERT
                                 │              └───┘ (back to RUN)
                                 └── FAULT (FETs off, board on) ── timeout ──► SLEEP (FETs off) or SHIP (UV)
   * RTC wake only with the optional RTC_WAKE diode fitted
```

Wake latency (calc / est.):
* From Sleep: ALERT → 3 ms soft-start → +3V3 → 200 ms TPS3823 delay → MCU boot ≈ **0.21 s**.
* From Ship: add the AFE boot of 0.2–0.3 s → ≈ **0.5 s** [DS-BQ p.53].

### 4.3 Wake sources: what is possible

| Source | Ship | Sleep | Standby | How |
|---|---|---|---|---|
| Button | ✓ (TS2) | ✓ (Q_BTN → `PWR_EN`) | ✓ (EXTI) | §4.1 items 2 and 5 |
| Charger | ✓ (LD) | ✓ (AFE exits SLEEP → WAKE alarm) | ✓ | [DS-BQ p.52–53] |
| Load current (inverter starts drawing) | ✗ (FETs off) | ✓ (Wake Comparator, 12 ms check [DS-BQ p.52]) | ✓ | AFE |
| AFE fault (SSA / SSBC / PF) | ✗ | ✓ | ✓ | ALERT |
| **CAN / RS-485 activity** | ✗ | **✗** | ✓ | **Only while the iso side is powered.** In Standby, RXD passes through the ISO7721 (≈ ns) to an EXTI / USART-wake pin; the first frame is lost and the inverter retries. In Sleep and Ship the iso side is unpowered and cannot see the bus. Keeping it alive costs the module no-load ≈ 8 mA at 5 V [DS-EV2W p.1] → ≥ 1 mA from the pack (calc), which defeats the µA target |
| **Remote-ON from the inverter** (option, DNP) | ✓ | ✓ | ✓ | An opto (LTV-817S, Basic) whose LED is driven by the inverter's 12–24 V dry contact; its transistor pulls `WAKE_BTN_RAW`. It draws zero standby current. Its dark current must stay ≪ 0.2 µA at 85 °C on the 4.6 MΩ TS2 node (unverified, Q-B10) |
| RTC periodic | ✗ | option (`RTC_WAKE`, unverified) | ✓ | §4.1 item 8 |

---

## 5. Supporting details

### 5.1 Load switches

| Switch | Part | Switched rail | Off-state | Note |
|---|---|---|---|---|
| `EN_ISO` | U7 TPS22918-Q1 (52 mΩ at 5 V, CT slew control, QOD) [DS-TPS22918 p.1, p.3] | +5V → U4 input | 0.5 µA [DS-TPS22918 p.5] | Set the CT ramp to about 1 ms: the module is "hot plug: not supported" [DS-EV2W p.2], so it must see a controlled ramp |
| `EN_SENSE` | U8 TPS22918-Q1 | +3V3 → `+3V3_SENSE` | 0.5 µA | INA240 REF1 must be on the same switched rail as its VS |
| `EN_ESP` | U6 TLV62569 EN pin | +5V → `+3V3_ESP` | 0.1 µA [DS-TLV62569 p.4] | Bulk ≥ 100 µF on +3V3_ESP for TX bursts (est.) |
| `EN_12V` | U5 EN/UVLO | VSUP → +12V | 3 µA [DS-LM5163 p.5] | Pull-down, so off by default (expander pins power up as inputs) |

### 5.2 Fail-safe defaults with the MCU off or in reset

* `PWR_HOLD`, `EN_*`: pulled down → off.
* `FET_EN`: **must not mean "kill" when the MCU is unpowered by design (Sleep).** Recommendation to the protection part: pull `FET_EN` up to `AFE_REG1` (default enable). The MCU-kill is then an additional path, and the AFE stays the independent protector (OTP-configured). Otherwise Sleep has to run with the output off (Q-B4).
* The OC latch output `OC_TRIP_N`, powered by `+3V3_SENSE`, must read "no trip" when unpowered. Its diode into BOTHOFF (part C D-C4) already gives that.

### 5.3 AFE-side current that hits the Sleep budget (request to part C)

* DDSG / DCHG are push-pull high when there is no fault, so each pull-down draws current continuously.
* Part C uses 100 kΩ: 2 × 33 µA = **66 µA**, more than the whole AFE SLEEP current.
* **Request: 1 MΩ** (2 × 3.3 µA). Hi-Z detection still works with CMOS inputs (typ. nA). The 74LVC worst-case II of ±1 µA would make the Hi-Z level marginal (1 V), so this is also a protection-part check.

### 5.4 Rail LEDs

* D4 / D6 / D7 / D8 are **DNP in production**. If fitted for bring-up, use ≥ 10 kΩ at 5 V (≈ 0.2 mA) and ≥ 47 kΩ at 12 V.
* Today they cost ~2 mA each (`05_system_features_mcu.md` §4.5), more than the whole Sleep budget.

### 5.5 `AFE_REG1` island load list (budget ≤ 5 mA, part C §3.4)

| Load | Run | Sleep |
|---|---|---|
| DDSG / DCHG pull-downs (1 MΩ, §5.3) | 6.6 µA | 6.6 µA |
| BOTHOFF pull-up 10 kΩ (part C) | 0.33 mA when asserted | 0 |
| AFE I2C pull-ups, **proposed to move from +3V3 to `AFE_REG1`** (10 kΩ) | ≈ 0.3 mA average | 0 (idle high) |
| ALERT pull-up 10 kΩ | 0.33 mA when asserted | 0 |
| `WAKE_BTN_N` pull-up 1 MΩ, Q_BTN / Q_ALRT gates | 3.3 µA while pressed | 0 |
| Gate-kill logic (74LVC class) | ≤ 2 mA budget (part C), typ µA | ≈ 1 µA (est.) |
| `MCU_VBAT` (only when +3V3 is off) | 0 | 0.525 µA [DS-G473 p.110] |
| **Total** | ≤ 1.2 mA + kill logic | **≈ 8 µA** |

Why move the I2C pull-ups: with them on +3V3, AUX-only bench mode (AFE unpowered) would inject about 0.7 mA through the pull-ups into the AFE pads. With them on `AFE_REG1`, the bus is dead when the AFE is dead, and the MCU sees "AFE absent". MCU SCL / SDA must be FT pins.

### 5.6 MCU pin-type requirements (to the MCU part)

* `AFE_ALERT`, `WAKE_BTN_N`, `AFE_FLT_*`, `FET_EN` and the AFE I2C pins see `AFE_REG1` levels while VDD = 0, so they must be **FT pins**.
* Positive injection on FT/TT is 0 mA [DS-G473 p.79]. FT tolerance with VDD = 0 is ≤ 4 V by the ST convention (unverified: the DS12712 absolute-maximum row was not read).
* The research map's PC5 for `AFE_ALERT` is **TT_a** [DS-G473 p.57], so move it.
* PC9 (`PWR_HOLD` in the research map) is FT_f [DS-G473 p.62], OK.

### 5.7 Other notes

* `+5V_ISO` / GND_ISO: unchanged barrier. Module rating is 1500 VDC (Q-B5).
* The board does **not** need the AFE's CP1-to-BAT current note (+200 µA with the pump on and CP1 tied to BAT [DS-BQ p.75]): in the FET build CP1 has 2.2 µF (part C §3.5).

---

## 6. Current budgets, item by item

All at 51.2 V and 25 °C unless stated; worst case = datasheet maximum or 85 °C.

### 6.1 Sleep (AFE SLEEP, output live, board off)

| Item | typ µA | worst µA | Source |
|---|---|---|---|
| BQ76952 SLEEP, DSG source-follower (REG1 off in the spec) | 24 | – (no maximum given) | [DS-BQ p.11] ISLEEP_2 |
| REG0 / REG1 running, no load (increment) | 5 | 10 | **unverified** (est. from DEEPSLEEP 10.7 µA with REG1 on vs SHUTDOWN 1 µA, [DS-BQ p.11]) |
| `AFE_REG1` island loads (§5.5) | 8 | 15 | calc / est. |
| U1 LM5164 shutdown (EN < 1.1 V) | 3 | 15 | [DS-LM5164 p.5] |
| U5 LM5163 shutdown | 3 | 15 | [DS-LM5163 p.5] |
| D_TVS1 SMCJ60A at 51.2 V (< VRWM 60 V) | < 1 | 1 | [DS-SMCJ p.2] |
| D3 ES2D reverse leakage into R_AUXB (51 V of 200 V) | 0.5 | 5 | [LCSC] (5 µA at 200 V) |
| PACK / LD 10 kΩ paths, PACK+ ≈ BAT | 1 | 2 | est. |
| Balancing NPN / gate network leakage (16 ×) | 1 | 2 | est. |
| U7 / U8 / U6 off (input unpowered with +5V off) | 0 | 0 | – |
| Rail LEDs | 0 | 0 | DNP |
| **Total** | **≈ 47** | **≈ 70** (calc; 85 °C AFE not specified) | |

* With DSG in charge-pump overdrive (41 µA [DS-BQ p.10]): ≈ 64 µA.
* With 100 kΩ DDSG / DCHG pull-downs (part C today): ≈ 106 µA.
* **Comparison:** Seplos ≤ 50 µA, JBD 0.4 mA, Daly ~0.5 mA (`02_competitors.md`; most do not say whether the output is live).

### 6.2 Ship (AFE SHUTDOWN, everything off)

| Item | typ µA | max µA | Source |
|---|---|---|---|
| BQ76952 SHUTDOWN | 1 | 3.1 | [DS-BQ p.11] |
| TS2 weak source into the WAKE_BTN_N chain (5 V / (4.6 + 1 + 10 MΩ)) | 0.3 | 0.3 | calc; REG1 has 10 MΩ to VSS in SHUTDOWN [DS-BQ p.47] |
| U1 + U5 shutdown | 6 | 30 | [DS-LM5164 p.5], [DS-LM5163 p.5] |
| D_TVS1 leakage | < 1 | 1 | [DS-SMCJ p.2] |
| D3 / R_AUXB | 0.5 | 5 | [LCSC] |
| LD 80 kΩ pull-down (FETs off, PACK+ ≈ 0 V) | 0 | 0 | [DS-BQ p.12] |
| REG0 NPN off-state leakage | < 0.1 | 0.1 | est. |
| **Total** | **≈ 8** | **≈ 40** | calc |

* Self-discharge: 8 µA × 8760 h = 70 mAh / year, i.e. 0.07 % / year of a 100 Ah pack (calc).
* Without U5 (+12V dropped): 5 µA.

### 6.3 Standby (comms alive) and Run

| Item | Standby mA | Run typ mA | Source |
|---|---|---|---|
| MCU | 0.085 (Stop 1; 0.66 at 85 °C) | 45 | [DS-G473 p.105, p.86] |
| ISO7721 VCC1 × 5 (DC: 1 mA each) | 5 | 8 | [DS-ISO7721 p.14] |
| Other +3V3 (TPS3823, memories, logic) | 0.05 | 4 | §3.3 |
| `+3V3_SENSE` | 0 (off) | 2.3 | [DS-INA p.6] |
| +3V3_ESP input | 0 | 23 | §3.2 |
| Iso module input: no-load 8 mA + bus side / η. Standby bus side: TJA1051 recessive 5 mA + THVD1450 RX 0.7 mA + VCC2 3 × 1 mA per domain ≈ 2 × 8.7 mA, at η ≈ 0.6 (est., light load) | 37 | 62 | [DS-EV2W p.1], [DS-TJA1051 p.2], [DS-THVD1450 p.10] |
| LEDs, dry contacts | 0.1 | 17 | est. |
| **+5V total** | **≈ 42** | **≈ 162** | calc |
| Converted to the pack (U1 η ≈ 0.80 / 0.85 est.) + AFE (0.04 SLEEP / 0.29 NORMAL + ~0.2 charge pump, est.) | **≈ 5.2 mA** | **≈ 19 mA** | calc |

Run with WiFi active (≈ 80 mA average, est.) is ≈ 26 mA. **Competitor run:** Daly ~45 mA, JBD 40 mA, Seplos < 40 mA (`02_competitors.md`).

---

## 7. Sequencing, power-good and brown-out

1. **`PWR_EN` rises** → U1 starts with its fixed 3 ms soft-start [DS-LM5164 p.1]. PGOOD (`PG_5V`) goes high at FB > 1.14 V [DS-LM5164 p.5]; it is an open-drain output pulled up to +3V3 (PGOOD absolute max 14 V [DS-LM5164 p.4]).
2. **+3V3** follows +5V. U3 EN can be tied to +5V (VEN ≤ VIN allowed [DS-TPS7B82 p.4]). Gating EN with `PG_5V` is not needed, because the LDO only regulates once VIN > VOUT + dropout.
   * **Analog before or with digital:** `+3V3_A` comes from the same LDO through a ferrite, so VDDA and VREF+ rise with VDD. No ordering problem.
3. **Reset:** TPS3823-33 holds NRST until +3V3 > 2.93 V, plus 200 ms ([LCSC]: TPS3823-33QDBVRQ1 C180100 listing; the -33 threshold also in [DS-TPS3823 p.7]).
4. **Firmware:** `PWR_HOLD` high within 50 ms of reset release (the RC hold gives 0.76 s). Then `EN_SENSE` → 10 ms → `EN_ISO` (1 ms ramp) → 10 ms → `EN_ESP` → `EN_12V` only on demand. This staggers the +5V load steps for the COT loop.
5. **Brown-out:**
   * The MCU's own BOR is set to level 4 (2.85–2.95 V rising [DS-G473 p.82]) as a backup to the TPS3823. PVD gives an early interrupt (PVD0 2.1–2.19 V [DS-G473 p.82]; higher PVD levels not read).
   * `PG_5V` falling (FB < 1.08 V, i.e. +5V −10 % [DS-LM5164 p.5]) is an EXTI: flush logs to FRAM.
   * The AFE keeps protecting regardless: it is powered from `BAT`.
6. **Power-down:** `EN_12V` → `EN_ESP` (set the UART TX pin low or Hi-Z first, so the unpowered ESP32 is not back-powered) → `EN_ISO` → `EN_SENSE` → clear the ALERT latch → `PWR_HOLD` low.
7. **No input UVLO divider** on U1, because EN carries the wake logic. Low-pack protection comes from AFE auto-shutdown (part C: 2.3 V / cell, 36 V stack) plus the MCU dropping `PWR_HOLD` at low SOC. This also keeps U1 working at 10–12 V for OTP and AUX. It closes review P8.

---

## 8. Bench / programming supply

### 8.1 AUX input (`J_AUX`)

* **Range 9–58 V.** U1 / U5 run from 6 V [DS-LM5164 p.4]; the TVS VRWM is 60 V.
* **Path:** F_AUX 0451002 → D3 ES2D (200 V) → `VSUP`. The VSUP TVS also protects the AUX side through D3, which is forward-biased for positive surges. A reversed AUX supply is blocked by D3.
* `AUX_IN` → 470 kΩ → `PWR_EN`: **the board is always on while AUX is present** (bench / firmware work).
* The AFE stays unpowered on AUX alone; by design, `REGIN ≤ BAT` stays true. The MCU sees "AFE absent" (I2C pull-ups on `AFE_REG1` are dead).
* The +12V output is in dropout at a 12 V AUX input (≈ 11 V out, est.), which is fine for bench work.
* **Today:** J2 → SS34 → +12V, with no fuse or TVS, and its LCSC field points to an isolator (§0).

### 8.2 OTP programming (EOL, no cells)

* **Requirement:** BAT 10–12 V and VC16 on the same supply, cells not connected, ≤ 45 °C (`01_bq76952_features.md` 9d: DS p.9, FAQ p.12, AN32 p.14).
* **Fixture:**
  * 11.5 V ± 0.3 V on the cell connector `BAT_SNS` / `CELL_16` contacts. The AFE BAT is then 11.5 − Vf(1N4148WS, ≈ 0.5 V at µA) ≈ 11.0 V, inside 10–12 V (calc; part C feed).
  * Board power from AUX at 12 V, or from B+ at the same 11.5 V.
  * Pogo pins short the `FORCE_ON` pads, because a blank AFE may not raise REG1 (REG0_EN default on the -02 / base part is unverified, part C).
  * The MCU firmware runs in factory mode and writes the OTP image over I2C. Note that the I2C pull-ups sit on `AFE_REG1`: if REG1 is not up on a blank part, the fixture must supply the pull-ups or the MCU must enable REG1 first. Part C to confirm (Q-B14).
  * Remove FORCE_ON after programming.
* At 11 V, U1 runs at D = 0.45 and tON = 1.5 µs (calc) → +5V OK. The TVS and fuse are irrelevant at 12 V.

---

## 9. Parts table

**Sources:**
* JLC stock and B/E = [JLC] `jlcsearch.tscircuit.com`.
* LCSC stock and brand = [LCSC] product API.
* Both read on 2026-11-17. "–" = the exact-number query returned no JLC stock figure.

| Ref-to-be | Function | Part | LCSC | Stock JLC / LCSC | B/E | Key rating | Source |
|---|---|---|---|---|---|---|---|
| F_SUP, F_AUX | Supply and AUX fuse | Littelfuse 0451002.MRL | C99547 | 10 322 / 10 325 | E | 2 A very fast, 125 V, 10 kA at 75 VDC, I²t 0.53 A²s | [DS-LF451 p.2] |
| R_DAMP1, R_DAMP2 | Inrush / damping / TVS current limit (2 in series) | Milliohm HoLRT2512-2W-1R-1% | C5127856 | 28 945 / 25 170 | E | 1 Ω, 2 W, 2512 | [LCSC] |
| D2 | Pack-tap OR / reverse block | SS320 (LCSC brand R+O; DS file Hongjiacheng) | C18199172 | 304 705 / 299 900 | E (preferred) | 200 V, 3 A, VF 0.95 V at 3 A, IR 50 µA | [DS-SS320 p.1–2] |
| D3 | AUX OR / reverse block, low leakage | GOODWORK ES2D-SMB | C2848676 | 28 690 / 28 450 | E | 200 V, 2 A, IR 5 µA at 200 V | [LCSC] |
| D_TVS1 | VSUP clamp | SMCJ60A (TWGMC) | C4154628 | 2 953 / 2 710 | E | VRWM 60, VBR 66.7–73.7, VC 96.8 V at 15.5 A, 1500 W | [DS-SMCJ p.2] (JEDEC values, Bourns), [LCSC] |
| (alt) | | Bourns SMCJ58A | C151899 | 3 376 / 3 160 | E | VC 93.6 V at 16.1 A | [DS-SMCJ p.2] |
| C_IN1–4 | Buck input | Samsung CL31Y225KCHVPNE | C2803390 | 15 894 / – | E | 2.2 µF, 100 V, X7S, 1206 | [LCSC] |
| U1 | +5V trunk buck | TI LM5164QDDARQ1 | C2072225 | 994 / 925 | E | 6–100 V, 1 A, IQ 10.5 µA, SD 3 µA, AEC-Q100; $12.55 (1–9) | [DS-LM5164 p.1, p.4–6] |
| (alt U1) | | TI LM5013QDDARQ1 | C5219285 | 2 572 / 2 448 | E | 100 V, 3.5 A, SD 3.1 µA; $6.47 | [DS-LM5013 p.1, p.5] |
| L1 | U1 inductor | Sunlord SWRB1207S-470MT | C169376 | 1 075 / – | E | 47 µH, 2.5 A, 100 mΩ | [LCSC] |
| U5 | +12V switched buck | TI LM5163QDDARQ1 (or LM5164-Q1 for EXT coils) | C2877984 | 1 666 / 1 590 | E | 100 V, 0.5 A, IPEAK 0.63 A min, SD 3 µA; $2.16 | [DS-LM5163 p.1, p.5–6] |
| L5 | U5 inductor | Sunlord SWRH1005C-101MT | C72572 | 623 / – | E | 100 µH, 1.35 A, 253 mΩ | [LCSC] |
| U3 | +3V3 LDO | TI TPS7B8233QDGNRQ1 | C5220182 | 209 / 2 598 | E | 300 mA, IQ 1.9 / 5 µA, 40 V, AEC-Q100, RθJA 63.9 °C/W | [DS-TPS7B82 p.4–6] |
| (alt U3) | | TI TPS7B8233QDRVRQ1 (WSON) | C2869742 | 623 / 573 | E | same, RθJA 72.8 °C/W | [DS-TPS7B82 p.5] |
| U6 | +3V3_ESP buck | TI TLV62569DBVR | C141836 | 639 669 / 627 725 | E | 2.5–5.5 V, 2 A, IQ 35 µA, ISD 0.1 µA | [DS-TLV62569 p.1, p.4] |
| L6 | U6 inductor | NR4018S2R2MT (brand not checked) | C28642347 | 17 210 / – | E | 2.2 µH | unverified specs |
| U7, U8 | `EN_ISO`, `EN_SENSE` switches | TI TPS22918TDBVRQ1 | C2653760 | 2 943 / 2 943 | E | 5.5 V, 2 A, 52 mΩ, QOD, CT | [DS-TPS22918 p.1, p.4–5] |
| (alt U7/U8) | | TI TPS22918DBVR | C131941 | 66 825 / 65 210 | E | same, non-Q | [LCSC] |
| U4 | Isolated 5 V | EVISUN B0505S-2WR3 | C7465195 | 5 411 / 5 282 | E | 5 → 5 V, 400 mA (min 40 mA), η 84 / 88 %, 1500 VDC, −40…105 °C | [DS-EV2W p.1–3] |
| (alt U4) | | YLPTEC B0505S-2WR3 | C5369473 | 4 476 / 4 455 | E | 2 W | [LCSC] (DS not read) |
| Q_BTN, Q_ALRT | Wake inverters (island) | AOS AO3401A | C15127 | 1 517 931 / 940 490 | **B** | −30 V PMOS, SOT-23 | [LCSC] |
| D_OR1–5 | `PWR_EN` OR | JSCJ 1N4148WS | C2128 | – / 1 861 350 | **B** | 100 V, 150 mA | [LCSC] |
| D_WAKE1 | TS2 / button (part C part, reused) | JSCJ BAV170 | C68970 | – / 11 520 | E | 75 V, common cathode, low leakage | [LCSC]; part C |
| D_VBAT | `MCU_VBAT` OR | BAT54C (High Diode) | C466637 | 2 567 / 2 550 | E | 30 V dual Schottky, common cathode | [LCSC] |
| U_OPT (DNP) | Remote-ON wake opto | Lite-On LTV-817S-TA1-C | C109227 | 362 461 / – | **B** | 5 kV, CTR 50–600 % | [JLC] listing |
| (MCU sheet) | Supervisor, kept | TI TPS3823-33DBVR | C7719 | 59 825 / – | E | 2.93 V, 200 ms, 15 µA; WDI floating → no reset | [DS-TPS3823 p.4, p.7]; field C80145 = no record |
| ESP module (comms part, listed for the budget) | BLE / WiFi | Espressif ESP32-C3-MINI-1-N4 | C2838502 | – / 9 258 | unverified | TX 350 mA peak, deep sleep 5 µA | [DS-ESP p.20–21] |
| C_EN, R_EN, R_AUXB, R pull-ups, RON 41.2 k, FB 316 k / 100 k | passives | generic 0603 1 % / X7R | not looked up | – | B (expected) | – | **unverified** |
| BTN1 | Wake button (on-board + header) | owner choice | – | – | – | – | **unverified** |
| J_AUX | AUX connector | owner choice (2-pin, polarised) | – | – | – | – | **unverified** |

---

## 10. Interface signals

Contract names are used as given. **NEW** marks names this part adds. Part C names are marked (C).

| Signal | Level / type | From → to | Default / fail-safe | Note |
|---|---|---|---|---|
| `PWR_HOLD` | 3.3 V push-pull, active-high | MCU → `PWR_EN` OR (1N4148WS) | 1 MΩ pull-down → off | Assert ≤ 50 ms after reset |
| `WAKE_BTN_N` | active-low, 1 MΩ pull-up **to `AFE_REG1`** | button (via BAV170) → MCU FT/EXTI pin, Q_BTN gate | high (released) | Change from part C (pull-up was +3V3) |
| `EN_ISO` | 3.3 V, active-high | MCU → U7 ON | pull-down → off | |
| `EN_ESP` | 3.3 V, active-high | MCU / expander → U6 EN | pull-down → off | UART TX low before off |
| `EN_SENSE` | 3.3 V, active-high | MCU / expander → U8 ON | pull-down → off | |
| `AFE_ALERT` | open-drain, active-low, 10 kΩ pull-up **to `AFE_REG1`** | AFE → MCU FT/EXTI pin, Q_ALRT gate | high | Change from part C (pull-up was +3V3); not on the TT_a pin PC5 |
| `AFE_RST_SHUT` | 3.3 V push-pull, 10 kΩ to VSS | MCU → AFE | low | High ≥ 1 s = SHUTDOWN (ship) [DS-BQ p.48] |
| `AFE_FLT_DSG_N`, `AFE_FLT_CHG_N` | REG1 push-pull | AFE → kill logic, MCU FT pins | Hi-Z → pull-down → "fault" | **Pull-downs 1 MΩ requested** (§5.3) |
| `FET_EN` | 3.3 V | MCU → kill logic | **pull-up to `AFE_REG1` recommended** (§5.2) | Protection-part decision |
| `+12V`, `+5V`, `+3V3`, `+3V3_A`, `+3V3_ESP`, `+5V_ISO`, `GND_PWR`, `GND_ISO`, `BAT+`, `BAT-`, `PACK+`, `PACK-` | rails | §1 | – | +12V now switched |
| `VSUP` **NEW** | 6–58.4 V | tap / AUX → U1, U5 | – | TVS-clamped node |
| `VSUP_F` **NEW** | 58.4 V | after F_SUP + R_DAMP, before D2 | – | Test point |
| `AUX_IN` **NEW** | 9–58 V | J_AUX → D3 → VSUP; 470 kΩ → `PWR_EN` | 100 kΩ bleeder | Bench = always on |
| `PWR_EN` **NEW** | 0–3.3 V (≤ 29 V via FORCE) | OR node → U1 EN/UVLO | 1 MΩ ∥ 1 µF to GND → off | Hold ≈ 0.76 s |
| `FORCE_ON` **NEW** | pads | VSUP → 1 MΩ → `PWR_EN` | open | EOL / first power-up |
| `EN_12V` **NEW** | 3.3 V, active-high | MCU / expander → U5 EN | pull-down → off | |
| `PG_5V` **NEW** | open-drain, pull-up to +3V3 | U1 PGOOD → MCU EXTI | – | Brown-out warning |
| `+3V3_SENSE` **NEW** | 3.3 V switched | U8 → INA240 VS / REF, OC comparator / latch | off | Replaces "+3V3" at the INA240 |
| `MCU_VBAT` **NEW** | 1.55–3.6 V | BAT54C(+3V3, `AFE_REG1`) → MCU VBAT | – | Optional coin cell / supercap (DNP) |
| `RTC_WAKE` **NEW** (DNP) | 3.3 V | MCU PC13 RTC_OUT1 → `PWR_EN` OR | – | Unverified in VBAT mode |
| `REMOTE_ON` **NEW** (DNP) | 12–24 V external | inverter dry contact → opto LED; transistor → `WAKE_BTN_RAW` | – | Zero standby current |
| `AFE_REG1` (C) | 3.3 V, ≤ 5 mA | AFE REG1 → island | off only in SHUTDOWN | §5.5 |
| `WAKE_BTN_RAW`, `AFE_TS2_WAKE` (C) | button node / TS2 | – | – | Part C wiring |
| `+5V_ISO2`, `GND_ISO2`, `EN_ISO2` **NEW** (only if 2 × 1 W is chosen) | | | | Q-B5 |

---

## 11. Firmware rules (power)

1. Assert `PWR_HOLD` first. Read the wake cause from the AFE Alarm Status, `WAKE_BTN_N`, `PG_5V` and the RTC flags. Clear the ALERT latch only after `PWR_HOLD` is high.
2. Sleep entry, in this order:
   * Set the Alarm Enable mask (WAKE, INITCOMP, SSA, SSBC, PF).
   * SLEEP_ENABLE; REG1 stays on (HWD Regulator Options = 0x00, part C).
   * Apply the FET policy.
   * Switch off `EN_*`.
   * Save to FRAM.
   * Clear ALERT.
   * Drop `PWR_HOLD`.
3. Ship entry: send the SHUTDOWN subcommand, or hold `AFE_RST_SHUT` high ≥ 1 s, then drop `PWR_HOLD`. Shutdown is delayed while LD > VWAKEONLD (charger present) [DS-BQ p.53]. Enable the Auto-Shutdown-Time re-entry in OTP (TRM §7.5, ≈ p.67).
4. Standby (Stop 1):
   * Set the TPS3823 WDI pin to Hi-Z. The device then pulses internally and does not reset [DS-TPS3823 p.4].
   * Keep the IWDG alive with RTC wakeups.
   * Wake on EXTI: CAN_RX, USART RX, `WAKE_BTN_N`, `AFE_ALERT`, `PG_5V`.
5. Never pull in two EXT coils at once (if on +12V). Turn on the fan at ≤ 50 % PWM first.
6. Drive the ESP32 UART and isolator inputs low or Hi-Z before cutting their supply.
7. BOR level 4; on PVD or `PG_5V` falling, flush logs.
8. Add the board self-consumption (≈ 19 mA run, ≈ 5 mA standby, ≈ 47 µA sleep, est.) to the SOC: `GND_PWR` returns on the cell side of the shunt, so the shunt does not see it.

---

## 12. Open questions for the owner

| # | Question | Recommendation |
|---|---|---|
| Q-B1 | Tree: **+5V trunk from U1 and +12V as a separate switched leaf (A)**, or keep +12V as the trunk (B)? | A |
| Q-B2 | +12V: keep it (fan / heater relay), and how much load? Are the `EXT_OUT1/2` coils on +12V, on pack voltage or on an external supply? Drop +12V entirely (5 V fan / relay)? | Keep the footprint; LM5163-Q1 without EXT coils, LM5164-Q1 with them |
| Q-B3 | Heater element: pack-voltage film switched by a FET (part A), or a 12 V relay? | Pack-voltage FET, relay optional |
| Q-B4 | Sleep policy: is the pack output live in Sleep (DSG source-follower, 24 µA)? This needs `FET_EN` to default to "enable" with the MCU off (pull-up to `AFE_REG1`). Idle timer, and the Wake Comparator current (part C uses 1 A)? | Live, pull-up, 1 A |
| Q-B5 | Isolation: one 2 W module (1.5 kVDC) or 2 × 1 W (per domain, + 3 names)? Is 1.5 kVDC acceptable against the "≥ 2.5 kVrms" in `instructions.md` §2.2, or move to a transformer-driver design? | 1 × 2 W for v1; owner to confirm the rating |
| Q-B6 | RS-485 failsafe bias resistors: DNP by default? | DNP (THVD1450 failsafe) |
| Q-B7 | RTC in Ship mode: accept losing the time (re-sync from app or inverter), or fit a coin cell / supercap? | Accept, footprint DNP |
| Q-B8 | AUX input: 9–58 V wide range OK? Connector type? AUX = always-on OK? | Yes |
| Q-B9 | Cost: LM5164-Q1 costs $8–12.5 at JLC. Accept it, or LM5013-Q1 ($6.5, 3.5 A) / non-Q parts? | Accept for v1, or LM5013-Q1 |
| Q-B10 | Fit the Remote-ON opto wake input (inverter dry contact)? | Footprint, DNP |
| Q-B11 | Accept "comms wake only in Standby" (none in Sleep / Ship)? | Yes |
| Q-B12 | Dry contacts: photoMOS (≈ 5 mA) or relays (≈ 35 mA each)? | PhotoMOS |
| Q-B13 | Reversed main lugs are not survivable. Accept mechanical keying plus the pack fuse? | Yes |
| Q-B14 | OTP fixture: 11.5 V on BAT_SNS / CELL_16 plus FORCE_ON pogo pins; I2C pull-ups on `AFE_REG1` with a blank part (part C)? | As in §8.2 |
| Q-B15 | Temperature grade: ESP32-C3-MINI-1-N4 is 85 °C; the -H4 (C2934569, 105 °C) is in stock at LCSC. Which? | -H4 if the 105 °C target (R19) holds |

---

## 13. Sources (opened this session unless noted)

| Tag | Document |
|---|---|
| DS-LM5164 | TI LM5164-Q1 SNVSB51C (local text extract, `bms_work/review/ds`) |
| DS-LM5163 | TI LM5163-Q1 (ti.com symlink PDF) |
| DS-LM5013 | TI LM5013-Q1 (ti.com symlink PDF) |
| DS-LMR16006 | TI LMR16006Y-Q1 SNVSAC1 (local) |
| DS-AP2112 | Diodes AP2112 (local) |
| DS-BQ | TI BQ76952 SLUSE13B Nov 2021 (local) |
| TRM | TI SLUUBY2B May 2022 (local; page numbers counted from page footers, marked ≈) |
| DS-G473 | ST STM32G473xB/C/E DS12712 Rev 2 (LCSC copy, C529361) |
| DS-TPS7B82 | TI TPS7B82-Q1 (LCSC copy, Chinese edition) |
| DS-TLV62569 | TI TLV62569 / TLV62569P (LCSC copy) |
| DS-TPS22918 | TI TPS22918-Q1 (LCSC copy, Chinese edition) |
| DS-EV2W | EVISUN A/B_S-2WR3 series V1.0 (LCSC copy, Chinese) |
| DS-LF451 | Littelfuse 451/453 Nano2, rev 02/26/16 (LCSC copy) |
| DS-SMCJ | Bourns SMCJ series (bourns.com) |
| DS-SS320 | Hongjiacheng SS32–SS320 Rev 2.0 (LCSC copy for C18199172) |
| DS-ESP | Espressif ESP32-C3-MINI-1 (LCSC copy, Chinese edition) |
| DS-ISO7721 | TI ISO7720-Q1 / ISO7721-Q1 SLLSEU1C Dec 2024 (local) |
| DS-TJA1051 | NXP TJA1051 (local) |
| DS-THVD1450 | TI THVD1450 (local) |
| DS-INA | TI INA240-Q1 (local) |
| DS-TPS3823 | TI TPS3823 (local) |
| Project | `PROJECT.md`, `instruction.md`, `instructions.md`, `docs/research/*.md`, `bms_work/review/requirements_review.md`, `bms_work/arch/A_power_stage.md`, `bms_work/arch/C_afe.md` |
| [LCSC] / [JLC] | `wmsc.lcsc.com/ftps/wm/product/detail?productCode=…` / `jlcsearch.tscircuit.com/components/list.json?search=…`, 2026-11-17 |

---

## 14. Unverified list

* **Converter efficiencies:**
  * LM5164 at 5 V / 51 V and LM5163 at 12 V: est. 0.80–0.85; the datasheet efficiency curves were not read.
  * Iso-module light-load efficiency: est. 0.6.
* **REG0 / REG1 incremental current in SLEEP** (est. 5 µA). REG0_EN default on the ordered AFE variant.
* **G4 FT pins with VDD = 0:** tolerance up to ≈ 4 V (absolute-maximum row not read). Whether RTC_OUT1 on PC13 works in VBAT mode (RM0440 not read). Higher PVD levels.
* **B0505S-2WR3 below its 40 mA minimum load:** output voltage against the 5.5 V transceiver limit. No-load 8 mA is the series "as low as" figure. The YLPTEC alternative's datasheet was not read.
* **Pass devices:**
  * TPS7B82 IQ at VIN = 5 V (specified at 6–40 V).
  * TPS7B82 dropout of the 3.3 V version at 114 mA (only the 5 V version's table was read).
* **ESP32-C3:** BLE average current (est. 30 mA). JLC stock / Basic status of C2838502.
* **Fault energy:**
  * F_SUP opening time at 29 A (time-current curve not read).
  * R_DAMP 2512 single-pulse energy rating.
  * Whether the 1 A 451 row carries the 75 VDC interrupting rating (hence 2 A is chosen).
* **SMCJ60A:**
  * TWGMC / SETsafe datasheets not read; Bourns JEDEC values used.
  * Clamp at 11.6 A by linear interpolation.
  * Leakage at 58.4 V and 85 °C.
* **Part-A coordination:** the `BAT+` peak at the clamp ≤ ≈ 100 V (part A, not re-checked).
* **Load currents:**
  * Fan, heater relay and EXT coil currents.
  * Buzzer.
  * Dry-contact LEDs.
  * FRAM / flash / TCA9535.
  * MCU peripheral adder.
  * VDDA.
  * THVD1450 current when driving 54 Ω.
  * ISO7721 device count (comms part).
* **Leakage on high-impedance wake nodes:** BAV170 leakage at 85 °C (5 nA is the 25 °C figure, part C); opto dark current on the TS2 node.
* **Board-specific values:**
  * Tap-lead inductance (1 µH est.).
  * CL31Y225KCHVPNE DC-bias derating.
  * NR4018S2R2MT inductor specs and brand.
  * Generic passives (RON 41.2 k, FB 316 k / 100 k, R_EN, C_EN, pull-ups) were not looked up individually.
* **Packaging and sources:**
  * LM5163 ↔ LM5164 footprint / pin compatibility.
  * LM5013 pin-out.
  * SS320 LCSC brand (R+O) vs the datasheet file (Hongjiacheng).
* **Not chosen:** the button part and the J_AUX connector.
* **Competitor figures** are as given in `02_competitors.md` (partly listing-based).
