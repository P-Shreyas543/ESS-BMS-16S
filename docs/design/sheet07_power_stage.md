# Sheet 07 — Power Stage (power board, refs 7xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/power_board_v1.pdf`](../schematic/power_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 07). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 174 refs = 163 fitted (of which 18 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 11 DNP; 52 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

Breakdown after the P5 fix round: 145 BOM parts fitted (incl. the chassis-mounted R735 / R737) + 11 DNP + 18 copper-only (TP705–TP716 THT pads, MH701–MH706; not in the BOM, no LCSC). Before P5 the sheet had 168 refs.

Not on this sheet (moved by the contract / owner): shunt R742/R743 and NTC_SHUNT RT702 of bom_G1 → sheet 04 (4xx); B2B male → J206 on sheet 02. `BAT-` side of the shunt and `PACK-` connect to sheet 04 by name (`BAT-`, `PACK-`; see R1-09).

## 1. Blocks (dashed boxes), placement left → right (power flow BAT+ → FET_MID → PACK+)

| # | Box title | Refs | Placement |
|---|---|---|---|
| 1 | Battery lugs, supply-tap fuse, BAT clamp | J702 J703 J706 J707 F701 D713-D716 C707-C710 TP701 TP712 | far left; `BAT+` global label; F701 from `BAT+` to `VSUP_TAP` → J701 pin 1 |
| 2 | CHG bank (Q701-Q708) | Q701-Q708 R701-R708 R717 R719 D701 D702 Q717 D705 R721 TP706 | centre-left; drains on `FET_MID` |
| 3 | DSG bank (Q709-Q716) | Q709-Q716 R709-R716 R718 R720 D703 D704 Q718 D706 R722 TP705 TP707 | centre-right, mirror of box 2 |
| 4 | Gate-kill drivers (Q719-Q722) | Q719-Q722 R723-R730 R749 C701 C702 D707-D710 | under boxes 2/3 (one column per bank) |
| 5 | Gate-kill logic (U701-U703) | U701-U703 C703-C706 R731-R733 R750 TP703 TP708-TP710 | bottom centre, left of J701 |
| 6 | Pre-discharge / pre-charge | Q723 Q724 R734-R737 D711 D712 | top, spanning BAT+ ↔ PACK+ |
| 7 | PACK clamp, snubbers, reverse clamp (DNP) | J704 J705 J708 J709 D717 D718 C711 C712 D719 R738 R739 C713 C714 Q725 R740 R741 D720-D722 TP702 TP704 | far right |
| 8 | Heater switch (Q726) | Q726-Q728 R744-R748 D724 J710 C715 TP711 | bottom right |
| 9 | B2B (J701), LD / PACK resistors, NTC_FET | J701 R751 R752 RT701 MH701-MH706 | bottom left; J701 drawn with passive pins, HV pins 1-8 grouped, 9/10 NC flags |

## 2. Gate network topology - SUPERSEDED by section 13.1 (kept for traceability)

`AFE_CHG` (J701-3) → R717 100 Ω → `07_GATE_CHG` bus → R701…R708 10 Ω → Q701…Q708 gates. Bus → R719 10 MΩ and D701/D702 16 V zeners (K = bus, A = `BAT+`) to the bank source. PNP turn-off: Q717 E = bus, B = `AFE_CHG`, C → R721 22 Ω → `BAT+`; D705 BAS21 A = `AFE_CHG`, K = bus (B-E clamp). Kill: Q719 AO3407A S = bus, D → R723 22 Ω → `BAT+`; G = `07_KG_CHG` with R727 100 k and D709 (K = bus) to the bus; R725 47 k ∥ C701 1 nF 2 kV → `07_KLS_CHG` → D707 BAS21 (A → K) → `07_KDR_CHG` = drain of Q721 BSS131 (S = `GND_PWR`, G via R729 100 Ω from `07_KILL`). DSG: same with `AFE_DSG`, `07_GATE_DSG`, `PACK+`, Q718/Q720/Q722, R718/R720/R722/R724/R726/R728/R730, D703/D704/D706/D708/D710, C702.

Logic: U701 AND3(`FET_EN`, `OC_TRIP_N`, `MCU_NRST`) → `AFE_DFETOFF` (J701-25 and U702 A); U702 AND3(`AFE_DFETOFF`, `AFE_FLT_DSG_N`, `AFE_FLT_CHG_N`) → `KILL_N` (J701-26, U703 A); U703 → `07_KILL` (sheet-local; ARCH §10 `KILL`) → R729/R730. All on `+3V3` from J701-28.

## 3. Key number per block (on-sheet note)

| Box | Note | Calc / source |
|---|---|---|
| 1 | "F701 2 A / 10 kA @75 VDC; clamp VC 96.8 V @ 51.7 A ×4" | 451 DS p.2; Liown DS p.2 |
| 2/3 | "8 × 1.5 mΩ per bank: worst FET 1.8 W @ 200 A; VGS clamp 16 V" | (27.5 A)² × 2.4 mΩ (A §4.4, est. hot factor) |
| 4 | "Kill: 42 V / 47 k = 0.9 mA active, 37 mW; AO3407A wins over CP 200 µA" | A §8.1 |
| 5 | v1.1 (P5-03): "Hi-Z inputs → BOTHOFF + kill (100 k pull-downs, 0.5 V < VIL 0.8 V); +3V3 lost → BOTHOFF only. B2B unplugged: no +3V3 = no kill, BQ off the gates; FETs held off only by R719 / R720 10 MΩ (τ 1.0–1.4 s if separated under load). Never unplug the B2B with the pack connected / under load." (v1.0 read "+3V3 lost / B2B unplugged → BOTHOFF only") | ARCH §5.3; reviews R1-16, P5-03 |
| 6 | "P-FET sources on FET_MID (BQ Fig 16-1); R_PRE 50 Ω: 1.17 A / 68 W pk, 174 J; R_PCHG 100 Ω: 0.26 A / 7 W" | BQ DS p.67; A §4.2 |
| 7 | "PACK clamp 4 × 5.0SMDJ60A + MBRB20200CT freewheel" | review R1-07 |
| 8 | "Heater ≤ 3.5 A (F702 5 A, 10 kA @75 VDC); VGS ≈ 11.7 V, 16 V clamp" | 451 DS p.2; R1-08 |
| 9 | "J701 pin map v1 (contract); 3 A / pin" | contract |

**Note (final review P5-03).** The box-5 text "B2B unplugged → BOTHOFF only" overstates what the hardware does. `+3V3` reaches the power board only through J701 pin 28, so with the connector out the kill FETs are never driven and the BQ drivers are no longer connected to the gates. The banks are then held off only by R719 / R720 (10 MΩ) and the zeners. Off-state: sound. Separation while conducting: the gates decay with τ ≈ 10 MΩ × 100–135 nF ≈ 1.0–1.4 s (calc) through the linear region under load. Rule: never separate the boards with the output on; screw the standoffs before the lugs are connected. **v1.1:** the on-sheet box-5 note now states this (table row above).

## 4. Test points

| TP | Net | Type | Proves |
|---|---|---|---|
| TP701 / TP702 | BAT+ / PACK+ | red hooks | pack and output potential |
| TP703 / TP704 | GND_PWR / PACK- | black hooks | probe grounds: kill-logic area / pack output (GND_PWR also has TP401 at the shunt star, different area) |
| TP712 | VSUP_TAP | THT pad | F701 intact |
| TP705 | FET_MID | THT pad | bank state (common drain) |
| TP706 / TP707 | 07_GATE_CHG / 07_GATE_DSG | THT pads | gate drive; use a ×10 probe (10 MΩ hold) |
| TP708 / TP709 | 07_KILL_N_INT / AFE_DFETOFF | THT pads | safety chain (chain side of R757) |
| TP710 / TP711 | +3V3 / +12V | THT pads | rails after the B2B |

## 5. DNP list

| Ref | Fit only if |
|---|---|
| J706-J709 (2nd M6 lug per node) | the XFCN 200 A basis is not confirmed (D-17) |
| C716 / C717 22 nF | bank gate-source capacitance option (R1-03) |
| R738/C713, R739/C714 | bank ringing on the bench (snubber values tuned there) |

## 6. AGENT DECISIONS (owner may overrule)

bom_G1 §6 questions (owner delegated 2026-11-23):

| Q | Choice | Why / source |
|---|---|---|
| 1 F_SUP | **F701 0451002.MRL at the B+ lug**, `VSUP_TAP` on J701 pin 1 | P-02, contract map |
| 2 250 V MLCCs | C707-C712 2.2 µF 250 V 2220; snubber C713/C714 100 nF 250 V; kill speed-up C701/C702 1 nF 2 kV | P-01 |
| 3 Blocking diodes | **D711 / D712 ES2D in series with Q723 / Q724 drains** (A = drain, K → R_PRE / R_PCHG) | P-03 |
| 4 R_PRE / R_PCHG | **keep Milliohm HoRX-100W (C2985693 50 Ω, 12 pcs; C2985696 100 Ω, 19 pcs, live)**, one 100 W part per path bolted to the plate with 2 × M4; back-order at LCSC or consign an equal ≥ 100 W Al-housed part | recommendation; stock is the only issue |
| 5 Shunt | owner decision C558625 → sheet 04, not here | — |
| 6 M6 torque 2.5 N.m | **keep XFCN M6 + DNP parallel footprints J706-J709**; torque stays a bench / owner check (LCSC has no M8 PCB terminal) | recommendation |
| 7 Non-AEC | n/a here (sheet 01) | — |
| 8 R_LD / R_PACK | **on the power board: R751 / R752 10 kΩ 1206 (C17902, Basic)** | contract; 1206 200 V vs 97 V clamp |
| 9 Numbering | heater stage 7xx on sheet 07 (Q726-Q728, R744-R748, D724, J710, C715); shunt + NTC_SHUNT to sheet 04 | owner 2026-11-23 |
| 10 TPS22918 ramp | sheet 01 | — |
| 11 Stack height | **accept 11.0 mm** (8.5 mm socket + 2.5 mm header body), M3 × 11 F-F standoffs | recommendation |

Further decisions in this spec:

| # | Question | Choice | Why |
|---|---|---|---|
| B1 | `BAT-` net | superseded by R1-09: `BAT-` power copper (J703, J707, D713-D716, C707-C710), joined to GND_PWR by NT401 on sheet 04 | contract 2026-11-23 rev. |
| B2 | J710 heater terminal not -40 °C (KF301 -30 °C) — P-13 | **WJ500V-5.08-2P C8465** (-40..+105 °C, 10 A UL, 5 A use = 50 %) | P-13, drawing p.1 |
| B3 | XFCN lug temperature — P-13 | **documented exception**: the drawing gives no temperature range; the part is all-metal (H62 brass, Sn plated, no polymer), so -40 °C is not material-limited (engineering judgment, not a datasheet value). No -40 °C-rated alternative M6 PCB terminal found at LCSC | XFCN drawing p.1 |
| B4 | Power-board fail-safe pull-downs | R731 FET_EN 100 k, **R750 MCU_NRST 100 k (new)**, R732/R733 AFE_FLT_*_N **100 k** (integration fix 2026-11-23: the only pair on these nets, sheet 02 drops R264/R265; II ±5 µA × 100 k = 0.5 V < VIL 0.8 V, SN74LVC1G11 DS p.4-5; C25803 re-verified live 2026-11-23, Basic), R748 HEATER_EN 100 k | contract (bom_G2 F-13). MCU_NRST: with the 10 k pull-up of sheet 03 (TPS3828 open drain) the high level is 3.0 V > VIH 2.0 V (SN74LVC1G11 DS p.4) |
| B5 | KILL line when U703 is unpowered | **R749 100 k pull-down on `07_KILL` (new)** | U703 output is Hi-Z with Ioff; BSS131 gates would float |
| B6 | D723 (AN09 D4, DNP) | **dropped**: same nodes as D706 (AFE_DSG → GATE_DSG) | duplicate footprint |
| B7 | KILL net name | sheet-local `07_KILL` (ARCH §10 `KILL` never leaves the sheet) | contract naming rule |
| B8 | Heater gate pull-down R745 | to `PACK-` (the FET source) | VGS defined at the source; PACK- ≈ GND_PWR within the shunt drop |
| B9 | Mounting holes MH701-MH706 | plated pads on **`CHASSIS`** (stack standoffs + Al plate, not via the B2B) — accepted 2026-11-23 for both boards | ≥ 4 mm to live copper |
| B10 | Chassis resistors R735 / R737 | symbol `Device:R`, footprint SolderWire 2-pad, Fit (purchased, hand-wired) | contract Fit/DNP only |
| B11 | Symbols | stock: IPT015N10N5, IRF9540N (on TO-263-2: pad 2 = tab = D, DS p.1 "Gate Drain Source"; superseded by IRF9640SPBF, same pinout, §13.2), BSC098N10NS5 (TDSON-8-1 pads 1-3 S, 4 G, 5 D), 2N7002, BAS21, 74LVC1G11/04, Q_PNP_BEC (MMBT5401 1 B 2 E 3 C, DS p.1), Q_PMOS_GSD (AO3407A 1 G 2 S 3 D, UMW DS p.2), Q_NMOS_GSD (BSS131 1 G 2 S 3 D, DS p.1), D_TVS (bidir), 1.5SMCxxA (unidir, pin 1 = K), D_Schottky_Dual_CommonCathode_AKA (MBRB20200CT: DS pins 1/3 A, 4 = tab K → KiCad TO-263-2 pad 2), Conn_02x15_Odd_Even. Project: XFCN_T68160200 (1 pin, 8 pads "1") | P-08 numbered pins = SOT-23 pads, checked by script |

## 7. New interface signals

None. Cross-sheet names used: rails + `BAT+ PACK+ PACK- FET_MID CHASSIS` + the 30 J701 nets of the contract map. Sheet-04 nets arriving only at J701 here (single pin on this sheet, continue on sheet 04): `SHUNT_K_BAT`, `SHUNT_K_PACK`, `ISENSE_OUT`, `NTC_SHUNT`, `+3V3_A`, `OC_CLR`. `OC_TRIP_N` comes from the sheet-04 latch to U701 and J701-19.

## 8. B2B change requests

None to the pin map. Layout note: KiCad `PinSocket_2x15` has pad 2 at x = −2.54 (mirror of `PinHeader_2x15`). Pin n ↔ pin n only holds if J206 (male, sheet 02) sits on the **bottom** of the control board facing J701 on the **top** of the power board; check by the B2B script with the real placement.

## 9. Verification record (live, 2026-11-23)

All 42 LCSC numbers re-read live 2026-11-23 on the LCSC product API and the JLCPCB parts API (MPN + manufacturer match, stock, Basic/Extended, LCSC temperature attribute). New this session: C8465 (WJ500V), C17902 (10 k 1206, Basic, JLC 1.6 M). Datasheets 2026-11-23: SN74LVC1G11 / 1G04 from ti.com; IPT015N10N5, BSC098N10NS5, IRF9540NS, AO3407A, BSS131, MMBT5401, 2N7002, BAS21, MBRB20200CT, MMSZ5246BS, ES2D, SS320, SMCJ60A, 5.0SMDJ60CA, 0451, XFCN, WJ500V, HC-PM254 from the LCSC datasheet links; drawing-only pages rendered and read as images (BSS131, MMBT5401, BAS21, MBRB20200CT, XFCN, WJ500V).

Low stock (< 10 × need for 100 boards): **R735 HoRX 50 Ω 12 pcs, R737 HoRX 100 Ω 19 pcs**; **D713-D716 5.0SMDJ60CA 2 389 vs 400**; **D717/D718 SMCJ60A 2 624** (shared with D103; 2nd source C4154628); **C153032 250 V 2220 2 644 LCSC / 6 379 JLC vs 1 000**.

Footprints: all stock except the lug (the project footprint library (`footprints.pretty/`)): easyeda2kicad C45384693 → `XFCN_T68160200-1400`; pitch 5.6/5.7/5.6 and 14.0 mm rows match the drawing; holes are round 4.2 mm instead of the drawn 3.6 × 2.5 mm slots — layout should convert to slots. TOLL footprint `Infineon_PG-HSOF-8-1_ThermalVias` pads 1 G / 2 S (merged leads 2-8) / 3 D = symbol. TO-263-2 pads 1, 3 leads + 2 tab.

## 10. Unverified items

1. RESOLVED (integration 2026-11-23): R732/R733 = 100 k, single pair → 0.5 V worst case at ±5 µA. Cost: 2 × 33 µA from AFE_REG1 while DDSG/DCHG are high (Sleep budget in ARCH §4.3 to be updated at integration).
2. IPT015N10N5 SOA at 80-100 V for 15-20 µs (graph not read); R_OFF 22 Ω is a start value — short-circuit bench test (D-04).
3. XFCN 200 A basis (no temperature rise stated), 2.5 N.m torque, temperature range (B3).
4. HoRX 5× / 5 s overload covers 174 J; no single-pulse data for 68 W × 2.55 s at hot plate temperature.
5. BSS131 RDS(on) at VGS 3.3 V is not specified (4.5 V: 14 Ω max); kill current 1 mA → OK by margin, not by DS figure.
6. RESOLVED by R1-02: the DSG turn-on path is now 10.2 kΩ + diode and the reverse clamp is fitted (≤ 5.7 mA from the pin at −58 V, calc).
7. NCP18 NTC_FET placement on GND_PWR copper thermally coupled to FET_MID: thermal coupling est. only.

## 11. Owner questions that remain

1. Closed at integration 2026-11-23 (R732/R733 100 k, sheet 02 drops R264/R265).
2. Closed (R1-02 / R1-04: reverse clamp fitted).
3. R_PRE / R_PCHG: approve back-order or a consigned equivalent (12 / 19 pcs at LCSC).
4. Closed: CHASSIS on the mounting holes of both boards accepted (integration 2026-11-23); plate earthing stays an installation item.
5. M6 lug torque 2.5 N.m for the chosen cable lugs (unchanged from bom_G1).

## 12. Mechanical BOM lines (no schematic symbol)

MECH701-706 M3 × 11 F-F brass standoffs (C551331), MECH707 Cu bars 10 × 3 mm (custom), MECH708 gap pad ≥ 3 W/m·K 1 mm (TBD), MECH709 M6 bolt kits, MECH710 M4 screws for R735/R737 — as bom_G1 §2; kept out of the schematic (no symbol / pins). C551331 re-read live 2026-11-23 (LCSC API: M3*11 Shuntian, 2 370 pcs, need 600 → low stock, 2nd source C64321 per bom_G1).

## 13. Revision after review R1 (2026-11-23, accepted)

### 13.1 Gate networks now (AN09 Fig 5-2 + two-stage turn-off)

* **CHG:** `AFE_CHG` (J701-3) → R717 1 k → `07_PNPB_CHG` (Q717 base) → D705 BAS21 (A = base node, K = bus) → `07_GATE_CHG` (turn-on path). Q717 E = bus, C = `07_OFF_CHG`; the kill FET Q719 drain is on the same `07_OFF_CHG` node. Turn-off node → fast stage R721 22 Ω + D731 5.6 V zener (K = node side, A = `BAT+`), and slow stage R723 470 Ω → `BAT+`. C716 22 nF G-S is DNP. R719 10 M and D701/D702 16 V are unchanged.
* **DSG:** `AFE_DSG` (J701-4) → R718 5.1 k → R753 5.1 k → D706 BAS21 → `07_GATE_DSG` (turn-on: 10.2 k × 135 nF ≈ 1.4 ms). Q718 base ← R754 1 k ← D732 BAS21 (A = base side, K = `AFE_DSG`). Q718 C, Q720 D and the static-floor PNP Q729 C all sit on `07_OFF_DSG` → R722 22 Ω + D733 5.6 V → `PACK+`, and R724 470 Ω → `PACK+`. C717 22 nF is DNP.
  * Q720: hold cap C718 10 nF G-S; speed-up C702 4.7 nF 2 kV; Q729 base via R755 100 k 1206 from `07_KLS_DSG`.
  * Reverse clamp Q725 / R740 / R741 / D720 / D721 is **fitted**.
* All R_OFF / zener / C_GS values are **set by SPICE + the D-04 short-circuit bench test**. With a single 22 Ω stage the interruption is TVS / avalanche-clamped and V_DS > 100 V is expected (R1-03).
* **Expected at the BQ pins on sheet 02 (coordination with sheet 02):**
  * BAS21 VSS → `AFE_DSG` at U201 pin 43 (A = VSS, K = pin).
  * BAS21 VSS → `AFE_LD` (pin 41) and BAS21 VSS → `AFE_PACK` (pin 42).
  * Nothing extra on `AFE_CHG` (J701-3).
  * D722 is removed from sheet 07.

### 13.2 Pre-charge / pre-discharge now (R1-01, R1-13)

* Q723 / Q724 = IRF9640SPBF (−200 V, C540971). **Sources are on `FET_MID`**; R734 / R736 1 M and the D725 / D726 16 V zeners run gate → `FET_MID`.
* PDSG path: `BAT+` → CHG bank → `FET_MID` → Q723 → D711 → R735 50 Ω → `PACK+`.
* PCHG path: `PACK+` → DSG bank → `FET_MID` → Q724 → D712 → R737 100 Ω → `BAT+`.
* 2× rule: 200 V / 97 V clamp = 2.06×; 200 V / 58.4 V = 3.4× (IRF9640S DS p.1-2).
* D711 / D712 are now redundant but kept.

### 13.3 Review disposition

| ID | Disposition | Refs changed / evidence |
|---|---|---|
| R1-01 BLOCKER | fixed | Q723, Q724 S → FET_MID; R734, R736 → FET_MID; new D725, D726 (MMSZ5246BS). BQ DS p.7 / p.12 / p.67 Fig 16-1 |
| R1-02 | fixed; sheet-02 clamps added on sheet 02 (13.1) | R717 100 Ω → 1 k; R718 100 Ω → 5.1 k 1206; new R753 5.1 k, R754 1 k, D732 BAS21; D705, D706, Q717, Q718 re-wired; D722 removed (moves to sheet 02) |
| R1-03 | fixed (footprints; values by SPICE + D-04 bench) | R721 / R722 fast 22 Ω + new D731 / D733 MMSZ5232BS 5.6 V; R723 / R724 → 470 Ω 0603 slow stage (the PNP and kill paths share the node); new C716 / C717 22 nF DNP |
| R1-04 | fixed, with one deviation | New C718 10 nF. C702 1 nF → 4.7 nF 2 kV (C41017). New Q729 MMBT5401 + R755. **R755 = 100 k 1206, not the proposed 4.7 k:** 4.7 k would dissipate (58 − 1.4)² / 4.7 k = 0.68 W with PACK+ held at 58 V (calc); 100 k still gives 0.57 mA base, enough for the ≤ 0.2 mA pump current. Reverse clamp Q725 / R740 / R741 / D720 / D721 now Fit. Bench plan: kill-only turn-off with `AFE_DSG` held high, into a resistive load and into a 1–2 µH short |
| R1-05 | n/a (sheet 04) | — |
| R1-06 | fixed | new R756 10 k (`OC_TRIP_N_PB` ↔ `OC_TRIP_N`) and R757 10 k (`07_KILL_N_INT` ↔ `KILL_N`); U701.B, U702.Y, U703.A and TP708 moved to the chain nodes |
| R1-07 | fixed | D717, D718 → 5.0SMDJ60A (C2990376); new D728, D729; D719 MBRB20200CT now Fit |
| R1-08 | fixed; 5 A F702 accepted as AGENT DECISION 2026-11-23 (heater ≤ 3.5 A, on the owner list) | New F702 **0451005.MRL 5 A** (C48467): PACK+ → `07_HTR_P` → J710-1 / D724 K. 7–8 A was asked, but in the 451 series only the 2–5 A rows list 10 kA @ 75 VDC; the 6.3–8 A rows list only 50 A @ 125 VDC (451 DS p.2), too low for a pack-fed fault. The heater is therefore limited to 3.5 A continuous (70 % of 5 A). A hardware thermostat (bimetal in the pad) is **required** (owner harness item) |
| R1-09 | fixed | J703, J707, D713–D716 pin 2 and C707–C710 pin 2 → `BAT-` (global label); NT401 is on sheet 04 |
| R1-10, R1-11, R1-15 | n/a (sheet 04) | — |
| R1-12 | fixed (contract pin map updated 2026-11-23) | J701 pin 8 = AFE_DSG, second contact parallel to pin 4; firmware watch on (stack − PACK+) |
| R1-13 | fixed | Q723 / Q724 → IRF9640SPBF −200 V (C540971) |
| R1-14 | fixed | new R758 1 k at J701-22 and C719 100 pF at U701.C; R750 moved to the U701 side (`07_NRST_PB`) |
| R1-16 | fixed | §3 box 5 note corrected |
| R1-17 | fixed (bring-up note) | TP706 / TP707: probe only with a ×100 / ≥ 100 MΩ probe; no-clean flux removed around the gate bus |
| R1-18 | fixed | new D730 MMSZ5246BS from `07_HTR_G` to PACK-. No separate +12V OVP is fitted (it depends on the sheet-01 buck); noted |
| R1-19, R1-20, R1-27 | deferred to the bring-up plan | read IPT015 SOA Diagram 3 before the bench test; measure CP1 − BAT at 85 °C; characterise the NTC_FET offset and lower OTF to match |
| R1-21 … R1-26 | noted, no change | R1-21 is covered by R1-02 (1 k base resistor) |

### 13.4 B2B change request (from R1-12)

Pin 8 (HV spare): double `AFE_DSG` (pin 4) so a single open contact cannot drop the DSG drive. Accepted at integration 2026-11-23: contract pin 8 = AFE_DSG; J701 pin 8 wired to AFE_DSG on sheet 07 (J206 pin 8 on sheet 02 must match).

### 13.5 New interface signals

| Name | Type | From → to | Note |
|---|---|---|---|
| `OC_TRIP_N_PB` | global label, power board only | sheet 04 latch Q → U701.B, R756 | contract 2026-11-23 (R1-06) |
| `BAT-` | global label, power board only | J703 / J707, BAT clamp, shunt battery side (sheet 04) | contract 2026-11-23 (R1-09) |

### 13.6 New LCSC numbers on this sheet

All live-verified 2026-11-23 on the LCSC product API + JLCPCB parts API (stock shown as LCSC / JLC):

| LCSC | Part | Stock / class |
|---|---|---|
| C540971 | IRF9640SPBF | 6 203 / 6 507 |
| C2990376 | 5.0SMDJ60A (Liown) | 7 775 / 7 778 |
| C22395563 | MMSZ5232BS | 2 660, JLC preferred |
| C41017 | 4.7 nF 2 kV 1206 | 65 180 |
| C26033 | 5.1 k 1206 | Extended |
| C23179 | 470 Ω 0603 | Basic |
| C21190 | 1 k 0603 | Basic |
| C21122 | 22 nF 0603 | Basic |
| C57112 | 10 nF 0603 | Basic, JLC 4.47 M; LCSC 0 |
| C17900 | 100 k 1206 | Basic |
| C48467 | 0451005.MRL | 21 820 |

Datasheets read:
* IRF9640S (Vishay): p.1 pinout G-D-S, VDS −200 V, VGS ±20 V.
* 5.0SMDJ60A row: Liown DS p.2.
* MMSZ5232BS row: DS p.2, 5.32–5.88 V.

## 14. P5 fix round (decisions 2026-11-24)

Now 174 refs / 395 pin rows. New LCSC numbers: none (R759 reuses C21189, the 0R 0603 of R618 on sheet 06; R760 reuses C25804, the 10 k 0603 of R745 / R747 on this sheet; the new THT pads have no LCSC, as TP705-TP712).

| ID | Disposition | Refs / nets changed |
|---|---|---|
| P5-01 | fixed | New R759 0R 0603 (Fit) strap AFE_FLT_CHG_N -> new local net `07_FLT_CHG_K` -> U702.6 (was AFE_FLT_CHG_N). New R760 10k 0603 **DNP**, 07_FLT_CHG_K -> +3V3. R733 pull-down stays on the AFE_FLT_CHG_N (B2B) side. Note in the logic box: "R759 0R fitted = DCHG kills both banks (D-12, as built); remove 0R + fit R760 10k = charge faults do not kill discharge (owner decision pending)" |
| P5-04 | fixed | New THT pads TP713 `07_KILL`, TP714 `07_OFF_CHG`, TP715 `07_OFF_DSG` (Block: Gate-kill drivers, next to the kill FET drains that drive the OFF nodes), TP716 `BAT-` (Battery lugs block, on the BAT- rail at the B- lug). The optional DNP V_DS probe pads were not added. Sheet 04 must not add a second BAT- pad |
| P5-05 | fixed | Block "PACK clamp, snubbers, reverse clamp (DNP)" renamed "PACK clamp, snubbers, reverse clamp" (22 rows) |
| P5-06 | fixed (drawing only) | Every 07_* net has at least one visible local label on the sheet |
| P5-07 | fixed (drawing only) | R756 drawn OC_TRIP_N (B2B side, left) -> OC_TRIP_N_PB (gate side, global label at the U701.B input route); "B2B side" / "gate side" text added |
| P5-03 | fixed (text, v1.1) | Box-5 on-sheet note corrected ("B2B unplugged: no +3V3 = no kill, BQ off the gates; FETs held off only by R719 / R720 10 MΩ …"); ARCH §5.3 corrected; no hardware change (review proposed none) |
