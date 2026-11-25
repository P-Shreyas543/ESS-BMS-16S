# Schematic v1 — 16S LFP ESS BMS (v1 2026-11-24, revision v1.1 2026-11-25)

Schematic v1 is the first complete, verified circuit of the v1 architecture ([`ARCHITECTURE.md`](ARCHITECTURE.md)): a two-board stack for a 16S LFP pack (40.0–58.4 V, 200 A continuous) with on-board back-to-back high-side N-FET banks driven by a TI BQ76952, an STM32G473 host, an MCU-independent hardware kill chain, isolated CAN / RS-485, an isolated USB-C service port and an ESP32-C3 radio.

**Status: schematic done, not yet laid out, not built, not tested.** All numbers below are datasheet values, own arithmetic (`calc`) or estimates (`est.`); nothing has been measured. The bring-up gates further down must pass before anyone trusts this design with a pack. PCB layout is the next step.

| Deliverable | File |
|---|---|
| Control board schematic (root + 8 sheets) | [`schematic/control_board_v1.pdf`](schematic/control_board_v1.pdf) — KiCad project `Automotive_ESS_BMS.kicad_pro` |
| Power board schematic (root + 2 sheets) | [`schematic/power_board_v1.pdf`](schematic/power_board_v1.pdf) — KiCad project `power_board/power_board.kicad_pro` |
| Part list, one row per reference | [`bom/bom_schematic_v1.csv`](bom/bom_schematic_v1.csv) (summary in [`BOM_v1.md`](BOM_v1.md#schematic-v1-bom-2026-11-24)) |
| Design note per sheet (blocks, calculations, decisions, review disposition, LCSC verification) | [`design/`](design/) |
| Spec review R1–R3 (before drawing) | [`reviews/spec_review.md`](reviews/spec_review.md) |
| Final schematic review P5 (after drawing) | [`reviews/schematic_review_p5.md`](reviews/schematic_review_p5.md) |
| v1.1 power-tree review (sheet 01) | [`reviews/v11_power_tree_review.md`](reviews/v11_power_tree_review.md) |
| What changed in v1.1 | [§9 Revision v1.1](#9-revision-v11-2026-11-25) |

---

## 1. Board split

| Board | KiCad project | Sheets | Size (plan) | Role |
|---|---|---|---|---|
| **Control** | `Automotive_ESS_BMS.kicad_pro` (repo root) | 01, 02, 03, 05, 06, 08, 09, 10 | ≈ 160 × 100 mm, 4 layers, 1 oz | supply tree, AFE + balancing, MCU, aux outputs, comms, IO, radio, memory / NTC mux |
| **Power** | `power_board/power_board.kicad_pro` | 04, 07 | ≈ 150 × 100 mm, 4 layers, 2 oz outer, on an Al plate | shunt + independent OC trip, FET banks, pre-charge, clamps, gate-kill logic ("safety island"), heater switch, M6 lugs |

The boards stack on a 2 × 15, 2.54 mm board-to-board connector: **J206** (male, sheet 02) on the **bottom** of the control board into **J701** (female HC-PM254-8.5H, sheet 07) on the **top** of the power board, pin n ↔ pin n, 3 A per pin, 11.0 mm stack (8.5 mm socket + 2.5 mm header body), M3 × 11 standoffs. KiCad's `PinSocket_2x15` has pad 2 mirrored against `PinHeader_2x15`, so pin 1 ↔ pin 1 only holds in that orientation — a row swap would put `VSUP_TAP` on `AFE_PACK` (layout gate, reviews R2-17 / P5-16).

### 1.1 B2B pin map v1 (J206 = J701)

Pins 1–8 (columns 1–4) are the HV group, all near pack potential; pins 9 / 10 are an empty creepage gap; pins 11–30 are low voltage.

| Pin | Net | Pin | Net |
|---|---|---|---|
| 1 | `VSUP_TAP` (fused by F701 at the B+ lug, P-02) | 2 | `AFE_PACK` (10 k R752 on the power board) |
| 3 | `AFE_CHG` | 4 | `AFE_DSG` |
| 5 | `AFE_PCHG` | 6 | `AFE_PDSG` |
| 7 | `AFE_LD` (10 k R751 on the power board) | 8 | `AFE_DSG` (2nd contact, review R1-12) |
| 9 | NC (gap) | 10 | NC (gap) |
| 11 | `SHUNT_K_BAT` | 12 | `SHUNT_K_PACK` |
| 13 | `GND_PWR` | 14 | `ISENSE_OUT` |
| 15 | `NTC_FET` | 16 | `NTC_SHUNT` |
| 17 | `GND_PWR` | 18 | `+3V3_A` |
| 19 | `OC_TRIP_N` | 20 | `OC_CLR` |
| 21 | `FET_EN` | 22 | `MCU_NRST` |
| 23 | `AFE_FLT_DSG_N` | 24 | `AFE_FLT_CHG_N` |
| 25 | `AFE_DFETOFF` | 26 | `KILL_N` |
| 27 | `HEATER_EN` | 28 | `+3V3` |
| 29 | `+12V` | 30 | `GND_PWR` |

### 1.2 Interface contract (net naming)

* Cross-sheet and cross-board signals use exactly the names of [`ARCHITECTURE.md`](ARCHITECTURE.md) §10; rails are power symbols: `+12V +5V +3V3 +3V3_A +3V3_ESP +5V_ISO AFE_REG1 VBAT_MCU GND_PWR GND_ISO GND_USB CHASSIS`.
* **`BAT-`** is the 200 A power copper only (B− lugs J703 / J707, shunt battery-side pads, BAT clamp TVS D713–D716 and MLCC C707–C710 returns), a global label on the power board. It joins **`GND_PWR`** (all signal grounds, AFE VSS, B2B ground pins) at exactly one net tie, **NT401** on sheet 04 at the shunt Kelvin edge (review R1-09). `BAT+`, `BAT-`, `PACK+`, `PACK-`, `FET_MID` are global labels, not power symbols.
* The MCU-side B2B nets keep their names `OC_TRIP_N` (pin 19) and `KILL_N` (pin 26). On the power board the chain nodes are **`OC_TRIP_N_PB`** (latch Q on sheet 04 → AND gate on sheet 07) and `07_KILL_N_INT`, each joined to its B2B net by a 10 k series resistor (R756 / R757) next to J701, so a GPIO driven the wrong way cannot override the chain (review R1-06).
* Sheet-local nets are `<sheet>_<name>` (for example `07_GATE_CHG`); every one has a visible label (review P5-06) so layout net classes can address the HV nodes by name.
* Reference ranges: sheet NN uses NNxx (sheet 10: 1001–1099); test points TPNxx in the sheet range. Each physical part exists once.

---

## 2. Sheets

| Sheet | Title | Board | Page | Refs: fitted (BOM + copper-only) / DNP | Main ICs | Design note |
|---|---|---|---|---|---|---|
| root | Control board root + block diagram | control | A3 | – | – | – |
| 01 | Power Supply (rev v1.1) | control | A2 | 112 (106 + 6) / 2 | LM5146-Q1 + SQ2398ES / 2 × DMN10H220LQ (+5V), LM5163-Q1 (+12V), TPS7B8233-Q1 (+3V3), TLV62569 (+3V3_ESP), TPS22918 + SN6505B + LT31-113 + TLV76750 (+5V_ISO) | [sheet01](design/sheet01_power_supply.md) |
| 02 | AFE / Cell Monitor | control | A2 | 164 (152 + 12) / 12 | BQ76952PFBR | [sheet02](design/sheet02_afe_cell_monitor.md) |
| 03 | MCU Control | control | A3 | 37 (28 + 9) / 0 | STM32G473RCT6, TPS3828-33 | [sheet03](design/sheet03_mcu_control.md) |
| 05 | Aux Outputs | control | A3 | 36 (33 + 3) / 0 | – (AO3400A drivers) | [sheet05](design/sheet05_aux_outputs.md) |
| 06 | Communications | control | A3 | 87 (73 + 14) / 10 | 2 × CA-IS3050CW, 2 × CA-IS3082WX, CH340X, ISO7721DR, USBLC6-2SC6 | [sheet06](design/sheet06_communications.md) |
| 08 | IO / Front Panel | control | A3 | 57 (52 + 5) / 15 | 2 × TCA9539PWR, 2 × GAQY212GS | [sheet08](design/sheet08_io_front_panel.md) |
| 09 | Wireless | control | A3 | 13 (13 + 0) / 4 | ESP32-C3-MINI-1-H4X | [sheet09](design/sheet09_wireless.md) |
| 10 | Memory / Sensors | control | A3 | 37 (31 + 6) / 0 | FM25V02A, GD25Q64E, TMUX1308 | [sheet10](design/sheet10_memory_sensors.md) |
| root | Power board root + note block | power | A3 | – | – | – |
| 04 | Current Sensing | power | A3 | 42 (34 + 8) / 1 | INA240A1, TLV1702, SN74AUP1G74, TLV803S | [sheet04](design/sheet04_current_sensing.md) |
| 07 | Power Stage | power | A2 | 163 (145 + 18) / 11 | 16 × IPT015N10N5, 2 × IRF9640S, 2 × SN74LVC1G11, SN74LVC1G04 | [sheet07](design/sheet07_power_stage.md) |

Totals (v1.1): control 586 refs (543 fitted, 43 DNP, 146 unique LCSC fitted); power 217 refs (205 fitted, 12 DNP, 60 unique LCSC fitted). Copper-only parts (test pads, net ties, mounting holes, solder jumpers) are `Fit` but not in the BOM.

---

## 3. How v1 was produced and verified

1. **Pin-level spec per sheet** (2026-11-23), built from the architecture, the owner decisions (`PROJECT.md` §5) and the P3 part selection: every part with value, footprint, MPN, manufacturer, live-verified LCSC number and fit / DNP, and **every pin of every part** with its net. Pin numbers were checked against the datasheet pin table, the KiCad symbol and the footprint pads by script. Each sheet note records its calculations, test points, DNP list and the decisions taken.
2. **Independent adversarial review** of the specs by reviewers who did not write them: R1 power board (sheets 04, 07), R2 power tree + AFE (01, 02), R3 MCU / IO / comms (03, 05, 06, 08, 09, 10). Result: **2 BLOCKER, 14 MAJOR, 35 MINOR, 33 NOTE** — every finding has a disposition ([`reviews/spec_review.md`](reviews/spec_review.md)).
3. **Fixes** applied to the specs (both blockers fixed: pre-charge P-FET sources on `FET_MID`, B0505S input pins), then the spec was frozen.
4. **Scripted drawing**: each sheet was generated from the frozen spec in the house style (dashed block boxes left → right, a key number per block, 1.0 mm text).
5. **Netlist-vs-spec check**: the netlist exported by `kicad-cli` was compared with the spec partition for every sheet — **SPEC MATCH on all 10 sheets** (every pin, net partition, value, footprint, MPN, LCSC and DNP flag), and the **B2B J206 ↔ J701 pin map matches** pin by pin across the two projects.
6. **ERC** (`kicad-cli sch erc`): **0 errors on both boards**. Control board: 2 warnings, both `pin_to_pin` on U1002 (GD25Q64E) pins 3 WP and 7 HOLD, which are bidirectional quad-SPI IO pins tied to `+3V3` on purpose (WP / HOLD inactive); documented and accepted. Power board: 0 warnings.
7. **Final independent schematic review P5** of both drawn boards, on the exported netlists joined at the B2B: **0 BLOCKER** (power board 2 MAJOR, 7 MINOR, 8 NOTE; control board 0 MAJOR, 9 MINOR, 14 NOTE). The fix round of 2026-11-24 was applied to spec and drawing and re-verified (SPEC MATCH, ERC as above) ([`reviews/schematic_review_p5.md`](reviews/schematic_review_p5.md)).
8. **Revision v1.1** (sheet 01 power tree): specified, independently reviewed (0 BLOCKER, 4 MAJOR — all fixed before drawing, [`reviews/v11_power_tree_review.md`](reviews/v11_power_tree_review.md)), drawn; ERC re-run on 2026-11-25: 0 errors on both boards, control board with the same 2 documented U1002 warnings, power board 0 warnings. See §9.

---

## 4. Key design numbers

| Area | Number | Source |
|---|---|---|
| Pack | 16S LFP, 40.0–58.4 V, 200 A continuous, 500 A ≤ 10 ms | D-06 |
| FET banks | 8 × IPT015N10N5 (100 V, 1.5 mΩ) per direction; worst FET 1.8 W at 200 A; VGS clamp 16 V | sheet 07 |
| Shunt | 2 × HolRS3920 0.2 mΩ in parallel = 100 µΩ; 2.0 W each at 200 A = 40 % of 5 W; ±50 ppm × 35 K = ±0.18 % | sheet 04 |
| Current amplifier | `ISENSE_OUT` = 1.65 V + 2.0 mV/A (INA240A1, gain error 0.20 %) | sheet 04 |
| Hardware OC window | +599 A / −305 A (±2 % ≈ ±12 A), latched; power-up held tripped by TLV803S until 200 ms after `+3V3` > 2.93 V | sheet 04 |
| BAT clamp | 4 × 5.0SMDJ60CA, VC 96.8 V at 51.7 A each; supply-tap fuse F701 2 A / 10 kA at 75 VDC | sheet 07 |
| PACK clamp | 4 × 5.0SMDJ60A + MBRB20200CT freewheel | sheet 07 |
| Pre-discharge / pre-charge | P-FET sources on `FET_MID`; R_PRE 50 Ω: 1.17 A / 68 W peak, 174 J; R_PCHG 100 Ω: 0.26 A / 7 W | sheet 07 |
| DSG turn-on | 10.2 kΩ × 135 nF ≈ 1.4 ms (AN09 network) | sheet 07 |
| Kill driver | 42 V / 47 k = 0.9 mA active, 37 mW | sheet 07 |
| Heater | ≤ 3.5 A continuous (F702 5 A, 10 kA at 75 VDC); VGS ≈ 11.7 V, 16 V clamp | sheet 07 |
| Supply input | R_DAMP 2 × 2.2 Ω = 4.4 Ω: hot-plug 13 A peak, TVS ≈ 79 V at 25 °C (< 100 V) | sheet 01 |
| +5V trunk (v1.1) | LM5146-Q1 synchronous, 200 kHz forced PWM, 5.08 V (4.95–5.22 V), ΔIL 0.34 A; shunt current limit valley 1.29–1.76 A; fc 20 kHz / PM 60°; peak 0.96–1.00 A at η ≈ 81 % | sheet 01 |
| +12V leaf | LM5163-Q1, 305 kHz, 12.2 V; budget fan 150 mA + 2 × 70 mA EXT + 1.2 mA heater gate ≈ 291 mA of ≈ 470 mA (62 %) | sheets 01, 05 |
| +3V3 | TPS7B8233-Q1, 0.40 W at 233 mA → Tj 111 °C at 85 °C ambient | sheet 01 |
| +5V_ISO (v1.1) | SN6505B 424 kHz → T101 1:1.3 → 2 × MBR0520L → TLV76750 5.0 V: 4.94–5.05 V at 0–300 mA, no minimum load; 300 mA = 0.40 A from +5V; barrier 2.5 kVAC / 60 s, 8.02 mm pad gap | sheet 01 |
| Power latch (v1.1) | `PWR_EN` hold 0.68 s; release 11 µA × 56 k = 0.62 V < 1.164 V; shutdown below 0.37 V falling (typ); ≤ 11.5 V; AUX on ≈ 7.1 V / off ≈ 4.4 V; shutdown ≈ 1.3 s after `PWR_HOLD` low | sheet 01 |
| Cell filter | τ = 2 × 100 Ω × 220 nF = 44 µs (cell 1: 22 µs, C201 to VSS) | sheet 02 |
| Balancing | TI NPN stage, 118 mA at 3.4 V / 129 mA at 3.65 V per cell; ≤ 8 cells, ≤ 3.0 W bank | sheet 02 |
| AFE_REG1 load | ≤ 1.80 mA = 36 % of the 5 mA budget | sheet 02 |
| MCU reset | TPS3828-33 open drain, 2.93 V, td 120–300 ms, WDT 0.9–2.5 s; NRST high ≥ 3.08 V with the 100 k power-board pull-down | sheet 03 |
| EXT outputs | ≤ 70 mA continuous per channel at 85 °C (≤ 120 mA at 25 °C) | sheet 05 |
| CAN termination | split 2 × 60.4 Ω + 4.7 nF, fc 1.1 MHz | sheet 06 |
| NTC mux | settle ≥ 5 ms after each channel change | sheet 10 |

---

## 5. Bring-up gates (consolidated)

Nothing in this list has been done yet. Items marked **before order** must pass before boards are ordered; **layout** items before the layout is released.

| # | Gate | When | From |
|---|---|---|---|
| 1 | J206 ↔ J701 pin 1 ↔ pin 1 checked in the 3D stack and on a 1:1 print (B2B script with the real placement) | **layout** | R2-17, P5-16 |
| 2 | RJ45 pin 1 checked on a physical XKB jack or a 1:1 print (a mirror swaps CANH / CANL on J601, J603, J604) | **layout** | sheet 06, R3-23 |
| 3 | ESP32-C3 antenna keep-out drawn as a rule area; thermal vias between the EPAD squares | **layout** | sheet 09 |
| 4 | XFCN lug holes converted to slots; WJ500V holes Ø1.5 mm if needed; mirror-symmetric shunt copper (current sharing); HV clearance on TP212 / TP213 (58–71 V pads) | **layout** | sheets 01, 02, 04, 07 |
| 5 | AUX-only bench mode: SS320 leakage back-energises `VSUP_TAP` / `BAT+` — treat BAT+ as live | first power-up | sheet 01, R2-22 |
| 6 | Fit FORCE_ON (TP113–TP114) or supply AUX before first flashing and for debugging on battery (`PWR_HOLD` is not driven by a blank MCU / the ROM bootloader) | first flash | R3-20, P5C-12 |
| 7 | Blank BQ76952 programming sequence (fixture supply on J201 pins 17 / 18, MCU held in reset, fixture I2C pull-ups, REG0 / REG1 enable first, CRC last, ≤ 100 kHz) | first AFE power-up | sheet 02, R2-04, R2-06 |
| 8 | OTP image items: DDSG / DCHG drive from REG1 = 3.3 V (0xAA), ALERT pin active-low with INITCOMP unmasked | AFE configuration | P5-15, P5C-16 |
| 9 | TS2 < 0.6 V with the wake button pressed in SHUTDOWN at −40 °C; else fit D232 (BAT54WS across the D225 TS2 leg) | cold test | sheet 02, P5C-02 |
| 10 | `WAKE_BTN_RAW` leakage at 85 °C (D817 PESD5V0S1BA not proven ≤ 10 nA) | hot test | sheet 08, R3-10 |
| 11 | HSE frequency of Y301 on the first board; LSE start-up at −40 °C with LSEDRV 10 and 11 | first board | sheet 03, R3-22 |
| 12 | CLR_N low level with ISENSE forced past each threshold at −40 / 25 / 85 °C: pass ≤ 0.6 V (TLV1702 VOL at 3.3 V not specified) | bench | sheet 04, R1-11 |
| 13 | `ISENSE_OUT` zero calibrated with the boards stacked (a few mV between the grounds shifts the reading ≈ 0.5 A per mV) | calibration | P5-11 |
| 14 | **D-04 short-circuit bench test** at 58 V with a 1–2 µH loop: set R_OFF / zener / C_GS values (SPICE + bench), kill-only turn-off with `AFE_DSG` held high into a resistive load and into the short, latch on and off; read the IPT015N10N5 SOA (Diagram 3) first; scope `TP404` for re-arm glitches on every interruption; watch `AFE_CHG`; current with a Rogowski coil or coaxial shunt | power bench | sheet 07, R1-03, R1-04, R1-19, P5-02, P5-04, P5-14 |
| 15 | Gate test pads TP706 / TP707: probe only with ×100 / ≥ 100 MΩ; no-clean flux removed around the gate bus | power bench | R1-17 |
| 16 | CP1 − BAT measured at 85 °C (charge-pump load with hot zener leakage) | hot test | R1-20 |
| 17 | NTC_FET offset against the junctions characterised; OTF threshold lowered to match | thermal test | R1-27 |
| 18 | CAN RXD level with `EN_ISO` off (RS-485 RO idles high per datasheet) | bench | sheet 06, R3-24, P5C-14 |
| 19 | Single-pulse checks with no published curve: R101 / R102 at F701 opening, HoRX R_PRE at 68 W × 2.55 s hot, HolRS3920 at 500 A / 10 ms | bench | sheets 01, 04, 07 |
| 20 | Fan plug fit / polarisation on the DLL 2510-4A header with the chosen fan | assembly | sheet 05 |
| 21 | Optional load-step tests: +3V3_ESP (C123 / C124 DNP), DC-bias of the 250 V 2220 MLCCs at 58 V | bench | sheet 01, R2-16, R2-23 |
| 22 | PWR_EN shutdown band (B1): PWR_EN and VSUP current in Sleep / Ship at 25 °C and 85 °C, AUX absent and AUX connected but unpowered: PWR_EN ≤ 0.15 V, U101 VIN current ≤ 30 µA (not the 1.75 mA standby band) | first power-up | sheet 01 v1.1 |
| 23 | AFE_ALERT wake with the minimum configured ALERT pulse at −40 °C (B2): PWR_EN > 1.3 V, `PWR_HOLD` high before PWR_EN falls below 1.2 V with ≥ 50 ms spare after NRST release; latch release after `PWR_HOLD` low (B3): shutdown within ≈ 2 s | cold test | sheet 01 v1.1 |
| 24 | +5V buck SW node and low-side gate (B4) at 58.4 V / 1 A and at an 80 V bench VSUP: (V_SW,pk − VSUP) ≤ 8 V, undershoot ≥ −5 V; V_SW,pk < 95 V at 80 V; `01_Q104_G` bump < 0.8 V. Tune the fitted R135 / C138 or R133 (4.7–10 Ω); never increase R134 / R139 | power bench | sheet 01 v1.1 |
| 25 | +5V load step 0.1 ↔ 0.9 A at 40 / 58.4 V (B5): overshoot < 150 mV, ≤ 2 rings; overload ramp (B6): hiccup between 1.45 and 2.0 A, L101 peak ≤ 2.2 A; thermal at 0.96–1.0 A scaled to 85 °C (B7): Q104 / Q105 < 120 °C, Q103 < 140 °C, R138 < 100 °C | power bench | sheet 01 v1.1 |
| 26 | +5V_ISO 0 → 300 mA at −40 °C and +85 °C (B8): 4.90–5.10 V, TP115 ≥ 5.4 V at 300 mA cold; T101 pin-1 orientation on the first article; **LT31-113 −40 °C qualification** (no temperature range in its spec; alternate Würth 760390014) | cold / hot test | sheet 01 v1.1 |
| 27 | Barrier hipot after assembly (B9), ≤ the 2.5 kVAC / 60 s T101 rating; Q103 V_DS(on) ≤ 0.6 V at 1 A, −40 °C, AUX 9 V only (B10), else swap Q103 to DMN10H220LQ-7 | production / cold test | sheet 01 v1.1 |
| 28 | Back-feed (B11): never drive `+5V` from a bench supply with U101 enabled (forced PWM boosts it into VSUP) — forbidden test configuration | bench rule | sheet 01 v1.1 |

---

## 6. Firmware rules (consolidated)

**Start-up and reset (sheet 03)**
1. Drive `PWR_HOLD` (PC6) high as the **first GPIO action after reset** (before clock-tree / peripheral init); the reset supervisor alone uses up to 300 ms of the 0.49–0.68 s latch hold (P5C-12, V11-04). After `PWR_HOLD` is released, shutdown takes ≈ 1.3 s: do not treat the live rail as a failed shutdown and do not re-assert `PWR_HOLD` in that window. **AFE_ALERT wake pulse: latched until the MCU clears it (preferred), or low ≥ 30 ms** (AFE configuration, V11-04). **Never back-feed `+5V` while U101 is enabled** (forced PWM conducts negative inductor current and boosts into VSUP, V11-13); for back-powered tests hold PWR_EN low or move R132 to GND.
2. Toggle `WDI` (PC12) within 0.9 s after start and before any long start-up task; WDI floats in reset and disables the external watchdog. Enable IWDG as backstop. Before Stop mode set PC12 to analog and rely on IWDG (P5C-11). Debug: cut JP302 or keep PC12 analog.
3. Release PA15 / PB4 from JTAG (SWD only); set `UCPD1_DBDIS` early — before the first read of `KILL_N`, before enabling EXTI4 and before driving `FET_EN` high (R3-16, P5C-10).
4. PB8 to non-analog mode after start; keep nSWBOOT0 = 1. PC13 (`WAKE_BTN_N`) input only. LSEDRV = 11 for Y302.

**Protection and AFE (sheets 02, 04, 07)**
5. `OC_CLR` (PD2) push-pull, idle low; re-arm the OC latch only after the fault is classified (P5-02).
6. Compensate the cell-1 reading from the coulomb-counter current: cell 1 includes I × R of the B− cable, lug and B2B ground (≈ ±40 mV at 200 A for 0.2 mΩ, est.; R2-02).
7. Watch (stack − `PACK+`) and drop `FET_EN` on a mismatch (open DSG contact, R1-12).
8. `AFE_ALERT` and `WAKE_BTN_N` read low while the AFE is off (blank part, AUX bench) — not an alert or a button press (R2-30).
9. Balance only at cell temperature ≤ 50 °C; throttle on `NTC_BAL` (local ≤ 95 °C) and Max Internal Temp (AD-02-6).

**IO, outputs, comms (sheets 05, 06, 08, 09, 10)**
10. Expanders (TCA9539 at 0x74 / 0x75) are reset with `MCU_NRST`: write the output registers before switching ports to output. LEDs off = port HIGH or input; DRY1/2 on = LOW; `FAN_EN` on = HIGH; DIP address = NOT DIP_ADDR3..0. Inputs are polled every 50 ms (INT not connected).
11. Never PWM `FAN_EN` / Q501; speed control only on `FAN_PWM` (25 kHz, 4-wire fans). `FAN_TACH` is valid only while Q501 is on. PC0–PC3 share TIM1 (one PWM frequency). EXT outputs are static; a coil economiser needs PWM ≥ 20 kHz.
12. CAN: 500 kbit/s classic on the inverter port, FD only on the pack link. RS-485 RE is tied low: discard the echo of own frames. Ignore `RS485_*_RX` / `CAN_*_RX` while `EN_ISO` is off and for **≥ 25 ms after `EN_ISO` goes high** (v1.1 supply start-up: TPS22918 1.06 ms + SN6505B soft-start ≤ 18 ms + LDO). Termination DIP poles 1 and 2 are always switched together (user manual).
13. ESP32: keep `ESP_EN` (U801 P12) low, `ESP_BOOT` (P13) as input and PC10 low / Hi-Z whenever `EN_ESP` is off (back-power through 1 kΩ ≤ 2.7 mA). Download mode: P13 low, pulse P12 low ≥ 1 ms, release P12, hold P13 low ≥ 3 ms.
14. NTC mux: `MUX_INH` low only while sampling; wait ≥ 5 ms after each `MUX_S` change; self-test S5 / S6 ≈ 0, S7 ≈ 50 %.
15. SPI1 ≤ 20 MHz, mode 0; both CS high before any transfer; accept both flash JEDEC IDs (GD25Q64E, MX25L6433F). Write SOC / counters to FRAM on PVD brown-out. The RTC is lost in Ship mode: re-sync time over CAN / BLE and keep the last timestamp in FRAM.

---

## 7. Open owner decisions

| # | Decision | State in v1 | Where |
|---|---|---|---|
| P5-01 | **Charge-fault kill policy.** DCHG asserts on every charge-direction fault, including UTC (0 °C) and OTC (45 °C), and kills **both** banks — so as built there is no discharge below 0 °C or above 45 °C and the heater (fed from `PACK+`) cannot self-heat the pack. Options: keep (document offline windows), clear UTC / OTC in CHG FET Protections B, or take DCHG out of the hardware kill | Hardware hook fitted: **R759 0R (fitted) = DCHG kills both banks (D-12, as built)**; remove R759 and fit **R760 10 k (DNP)** to `+3V3` = charge faults do not kill discharge. ARCH §5.1 / §5.2 / D-12 follow the decision | sheet 07, [P5 review](reviews/schematic_review_p5.md) |
| – | Heater limited to **3.5 A** continuous by the 5 A F702 (the 6.3–8 A rows of the 451 series list only 50 A at 125 VDC); a hardware thermostat in the pad is required (harness item) | AGENT DECISION (owner may overrule) | sheet 07, R1-08 |
| – | RTC / supercap in Ship mode: no supercap footprint (no verified LCSC part); RTC runs in Sleep and is lost in Ship | AGENT DECISION (owner may overrule); restore once a part is verified | sheet 03 |
| D-31 | Buzzer BZ801 (QMB-09B-05 on +5V): fit or DNP | DNP | sheet 08 |
| – | CELL_0 harness and B− cable: J201 pin 1 optional (via R274 10 Ω), B− lug first on / last off; **B− cable + lug ≤ 0.1 mΩ** (≤ 20 mV at 200 A) | requirement for the harness spec; ≤ 0.5 A fuse per cell tap (R2-29) | sheet 02, R2-02 |
| – | EXT_OUT1/2 sized for interposing relays: **≤ 70 mA** at 85 °C (≤ 120 mA at 25 °C). Direct contactor coils would need LM5164 on +12V, bigger PTCs (D-07) | as sized | sheet 05 |
| – | CH340X temperature rating: −40…85 °C only in the newer datasheet V3C; the older datasheet and the LCSC listing say −20…70 °C | CH340X fitted | sheet 06 |
| – | USB-C: GCT USB4105-GF-A (LCSC 0 / JLC 4 375) vs Kinghelm KH-TYPE-C-16P | GCT fitted | sheet 06 |
| – | **J201** Micro-Fit 430451800 stock (LCSC 12 / JLC 437): reserve, or the gold-flash 430451801 (C19793486) | open | sheet 02 |
| – | **R_PRE / R_PCHG** HoRX 100 W stock (12 / 19 pcs): back-order or a consigned ≥ 100 W Al-housed equivalent | open | sheet 07 |
| – | **T101 LT31-113**: JLC-only (771 pcs), no temperature range / AEC statement in its spec | owner 2026-11-25: keep LT31-113 with a −40 °C qualification gate; Würth 760390014 (AEC-Q200, 0 stock) as drop-in alternate | sheet 01, V11-12 |
| – | SN6505B-Q1 (+$2.18) instead of SN6505BDBVR; MCU spread-spectrum clock on SYNCIN (R132 pad) instead of the fixed 200 kHz strap | open options | sheet 01 |
| D-04 | **100 V FET margin**: 15 % in the design case, 0 % in the SCD-only double fault; the short-circuit bench test decides R_OFF / zener / C_GS values (bring-up gate 14); 120–150 V TOLL fallback | open | ARCH §6, sheet 07 |
| – | Non-Q TLV1702AIDGKR (the -Q1 had 0 stock) and OC window +599 / −305 A | accepted as AGENT DECISION / proposal | sheet 04 |
| D-16 | FUSE / breaker part for the BQ FUSE path | J205 path DNP | sheet 02 |
| D-17 | M6 lug torque 2.5 N.m for the chosen cable lugs; 200 A basis of the XFCN terminal | bench / owner check; DNP second-lug footprints J706–J709 | sheet 07 |
| D-32 | ESP antenna in a metal enclosure (plastic window or -1U variant) | open | sheet 09 |
| D-46 | Allow the ESP to reset / re-flash the STM32 (fit R905, Q901, R906) | DNP | sheet 09 |
| – | Fan type: 12 V 4-wire PWM PC fan (3-wire supported on / off) | to confirm | sheet 05 |

---

## 8. Known limitations of v1

* **Not built and not tested.** Every timing, energy and margin figure is calc / est. until the bench tests in §5.
* **B2B unplugged** (P5-03): with the connector out the power board has no `+3V3`, so the kill FETs are not driven and the BQ drivers are disconnected; the banks are held off only by 10 MΩ + zeners (off-state sound, no active turn-off; gate decay ≈ 1.0–1.4 s under load, calc). Never separate the boards with the output on. The sheet 07 on-sheet note states this since v1.1.
* **100 V FETs**: 0 % margin in the SCD-only double fault and a negative margin with a reversed parallel pack (ARCH §6, D-04).
* **Charge-fault policy** as built (P5-01): no discharge outside 0…45 °C cell temperature until the owner decides.
* **Isolation (v1.1)**: the comms supply barrier is T101, 2.5 kVAC / 60 s with an 8.02 mm pad gap (≥ 2.5 kVrms requirement met), but it is **functional isolation, not reinforced**; the transceivers are 5 kVrms / 8 mm. The USB service barrier (ISO7721DR, 4 mm) is functional only. (v1.0 had a 1500 VDC module with only 3.58 mm creepage on its footprint.)
* **+5V trunk (v1.1)**: ≈ 81 % peak efficiency and ≈ +6 mA standby versus the v1.0 LM5013 (owner-accepted); the EN/UVLO shutdown threshold is typical-only (gate B1).
* **Temperature rating** −40…85 °C ambient (D-14); several parts are not AEC-Q (STM32G473, CA-IS transceivers, ESP32, CH340X, INA240A1PWR, TLV1702AIDGKR, TPS22918DBVR, TLV62569DBVR, SN6505BDBVR, TLV76750DRVR).
* **AFE accuracy**: BQ76952 ±15 mV max cell accuracy, not the ±1.5 mV of the original requirement.
* **Ship mode** is delayed while LD is held above 0.8–2.25 V (charger or parallel pack on `PACK+`, R2-13); the RTC is lost in Ship.
* **Open B− cable under load** is destructive in every variant: tap fuses at the cells are required (R2-29).
* No field firmware update through the STM32 ROM bootloader without opening the unit (JP301 + reset, R3-20).
* **Cosmetic items left open** from the final review (no electrical effect): ground symbols do not show the `GND_PWR` name (P5-17); title-block comment "Sheet n/9" numbering and line order (P5C-19); the U103 note points to TP402 "sheet 04" without naming the power board (P5C-20); pin-name overlaps on U103 / U901 and hidden J801 pin numbers (P5C-21); the cell-filter ↔ balancer join on sheet 02 is by labels only (P5C-22); two hooks on `GND_ISO` (TP108, TP601; P5C-18). The BQ76952 symbol still names pin 25 `HDQ_IO/ALERT`; an on-sheet note clarifies pin 25 = ALERT, pin 28 = HDQ (P5C-08).

---

## 9. Revision v1.1 (2026-11-25)

v1.1 changes only the control-board **sheet 01 power tree**. The interface net set, the B2B pin map and the other nine sheets are electrically unchanged; the sheet 07 box-5 note was corrected as text. Sheet 01 is now A2 with 114 references (v1.0: A3, 90). Design note: [`design/sheet01_power_supply.md`](design/sheet01_power_supply.md) §12–§13; review: [`reviews/v11_power_tree_review.md`](reviews/v11_power_tree_review.md).

### 9.1 What changed and why

| Block | v1.0 | v1.1 | Why |
|---|---|---|---|
| +5V trunk | LM5013-Q1 non-synchronous COT buck, SS520 freewheel diode | **LM5146-Q1** synchronous controller, 200 kHz **forced PWM** (SYNCIN strap R132), high-side Q103 SQ2398ES, low-side **Q104 + Q105** DMN10H220LQ-7 in parallel, 68 µH, **R138 100 mΩ shunt current limit** (valley 1.29–1.76 A), fitted snubber R135 / C138, R133 4.7 Ω gate resistor, type-III compensation (fc 20 kHz, PM 60°) | fixed-frequency switching for a predictable EMI spectrum; LM5013 stock risk (250 pcs) closed; temperature-independent current limit (review V11-01) |
| PWR_EN latch | R109 1 MΩ, C111 1 µF, R110 / R111 2 MΩ, 2 AUX bleeders | **R109 56 k, C111 10 µF, R110 / R111 240 k, R123 / R124 10 k, third AUX bleeder R136** | the LM5146 EN/UVLO pin sources 9–11 µA above 1.2 V: with 1 MΩ the latch could never release; release now 0.62 V < 1.164 V, hold 0.68 s |
| +5V_ISO | B0505S-2WR3 2 W module + 150 Ω dummy load (R122 / R128) | TPS22918 kept → **SN6505B** (424 kHz, spread spectrum) → **T101 LT31-113** 1:1.3 → **2 × MBR0520L** → **TLV76750** 5.0 V LDO; +5V_ISO 4.94–5.05 V, no minimum load | fixes the **v1.0 creepage defect** (only 3.58 mm between the module's `GND_PWR` and `GND_ISO` pads, < 6.5 mm rule; now 8.02 mm across T101, rule area in the footprint); barrier 1.5 kVDC → **2.5 kVAC / 60 s**; no dummy load; idle draw from +5V ≈ 109 → 32 mA |
| Sheet 07 note | "B2B unplugged → BOTHOFF only" | "B2B unplugged: no +3V3 = no kill, BQ off the gates; FETs held off only by R719 / R720 10 MΩ …; never unplug the B2B with the pack connected / under load" | review P5-03 |

### 9.2 Owner decisions and accepted trade-offs (`PROJECT.md` §5, 2026-11-24 / 2026-11-25)

* **+5V trunk = LM5146-Q1**, 200 kHz / 68 µH, forced PWM (supersedes D-08). After the review fixes (shunt, Q105, snubber, R133) the owner accepted **≈ +6 mA standby versus the LM5013** (first accepted: ≈ +3 mA) and **≈ 81 % peak efficiency** (first accepted: ≈ 84 %). The iso change saves **≈ 9 mA**, so board standby stays **≈ 3 mA below v1.0**. Sleep +10–20 µA (U101 shutdown current).
* **+5V_ISO = SN6505B + transformer + TLV76750** (supersedes D-09). Transformer **Linekey LT31-113** with a **−40 °C qualification bring-up gate** (its spec gives no temperature range), **Würth 760390014** (AEC-Q200) as the drop-in alternate. The barrier is recorded as **functional isolation, not reinforced**.
* AFE_ALERT wake: **latched, or low ≥ 30 ms** (the reset supervisor delay of up to 300 ms needs the longer latch hold).

### 9.3 Closed by v1.1

* B0505S pin 1 / 2 physical check (review R2-01 bring-up gate) — part removed.
* `+5V_ISO` ≤ 5.5 V overvoltage gate and the dummy-load question (review R3-02) — the LDO output needs no minimum load.
* B0505S footprint creepage defect (3.58 mm) — replaced by the 8.02 mm transformer barrier.
* LM5013-Q1 stock risk.

### 9.4 Verification of v1.1 (2026-11-25)

* Netlist-vs-spec check: SPEC MATCH on all 10 sheets (both projects), against the updated sheet-01 spec.
* B2B pin map: J206 = J701 on all 30 pins, matching the contract table.
* ERC: control board 0 errors (2 documented U1002 WP/HOLD pin_to_pin warnings), power board 0 errors / 0 warnings.
* Independent review of the v1.1 change: 0 blockers; all 4 majors fixed ([`reviews/v11_power_tree_review.md`](reviews/v11_power_tree_review.md)).

