# Sheet 02 — AFE / Cell Monitor (control board, refs 2xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 02). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 176 refs = 164 fitted (of which 12 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 12 DNP; 43 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

**Net naming.** Cross-sheet / cross-board nets use ARCHITECTURE §10 / contract names. Sheet-local nodes are `02_*` (`02_CELLn`, `02_VCn`, `02_QBn_B`, `02_QBn_C`, `02_SRP`, `02_SRN`, `02_TS1`, `02_HDQ`, `02_TS3`, `02_CFETOFF`, `02_NTCn`, `02_REG18`, `02_REGIN`, `02_REG2`, `02_BREG`, `02_REG0_D`, `02_CELL0_HARN`, `02_I2C_PU`, `02_TS2_D`, `02_ABAL_GND`, `02_REG0_C`, `02_BAT_D`, `02_BAT`, `02_CP1`, `02_SCL_PIN`, `02_SDA_PIN`, `02_ABAL_EN_OD`, `02_ABAL_5V`, `02_FUSE_*`). Four §10 names are used for nodes that now live only on this sheet: `BAT_SNS`, `AFE_TS2_WAKE`, `AFE_FUSE` (and `AFE_REG1` as rail). BQ pins 19 / 44 are `NC` (stock symbol types them no_connect, DS Table 6-1 p.5 "not connected to silicon"); no flag needed, copper may still be poured to VSS in layout.

## Blocks (dashed boxes, left → right signal flow)

| # | Box title | Parts | Placement | Key number for the on-sheet note (calc) |
|---|---|---|---|---|
| 1 | Cell connector + input filter | J201, NT201, R274, R201–R217, C201–C216 | far left, J201 at board edge | τ = 2 × 100 Ω × 220 nF = **44 µs** (cell 1: C201 to VSS, 100 Ω × 220 nF = 22 µs) ≪ 3 ms conversion (BQ DS p.9; AN81 p.8) |
| 2 | Balancing (TI NPN) | Q201–Q216, R218–R233, R234–R249, D201–D216, RT201 | left-centre, R_BL bank on B.Cu | I_cell 118 mA @3.4 V / 129 mA @3.65 V; R_BL 0.38 W = 38 % of 1 W; ≤ 8 cells (odd / even) ≤ **3.0 W** bank (C §4.3) |
| 3 | AFE U201 | U201, TP201 | centre | – |
| 4 | AFE supply (REG0 / BAT / CP1) | D217, D218, D228, R250, R251, R252, Q217, C217–C222, TP202–TP204, TP212, TP213 | above U201 | REG0 worst case P_Q ≤ 57.8² / (4 × 3.3 k) = **0.25 W** = 25 % of 1 W; BAT hold-up 1 µF / 0.5 mA = 0.5 V/ms (C §3) |
| 5 | Current-sense filter SRP/SRN | R253, R254, C223–C226 | right of U201, next to J206 pins 11/12 | leg 10 Ω (2 × 20 Ω on sheet 04) + 100 Ω = 110 Ω; τ_diff = 2 × 110 Ω × 100 nF = **22 µs** |
| 6 | Temperature inputs | J202, J203, R266–R269, C227–C230, D219–D224 | below U201, J202/J203 at board edge | τ = 18 kΩ × 1 nF = **18 µs** (< 5 % of 3 ms, BQ DS p.66) |
| 7 | Host I/F + fault pins | R257–R263, R276, D225, D227, TP205–TP211 | right of U201 | AFE_REG1 load ≤ 1.80 mA (I2C 2 × 0.7 mA while low, ALERT 0.33 mA, DDSG/DCHG 2 × 33 µA into the 100 k PDs on sheet 07) = **36 %** of the 5 mA REG1 budget |
| 8 | Active-balancer header | Q218, R270, R275, F201, J204 | bottom right, J204 at edge | module enable ≤ **50 mA**: BSS138BK ≤ 4.5 Ω at 2.5 V → ≤ 0.23 V, + 0.5 V across R275 (calc) |
| 9 | FUSE driver (DNP) | R271–R273, Q219, D226, J205 | bottom right | FUSE pin ≤ 2 mA, V_OH 6–9 V at 5 k (BQ DS p.7, p.12) |
| 10 | B2B J206 | J206, D229–D231 | right edge (stacks on J701) | HV group pins 1–8 (pin 8 = second `AFE_DSG` contact, interface contract rev. R1-12), gap 9–10; AFE_CHG up to BAT + 13 V ≈ 71 V (A §12) |

## Pin map highlights (full list in the netlist)

* **U201** pins 1–16 = VC15…VC0 → `02_VC15`…`02_VC0`; 48 VC16; 17 VSS = GND_PWR; 18 SRP / 20 SRN via R253 / R254 from `SHUNT_K_BAT` / `SHUNT_K_PACK` (SRP = battery side, charge positive, DS p.5); 21 TS1, 28 HDQ, 23 TS3 = pack NTC 1/2/3; 29 CFETOFF = `NTC_FET` (OTF); 22 TS2 → BAV170 wake; 25 ALERT; 26/27 I2C via 100 Ω; 30 DFETOFF = `AFE_DFETOFF` (100 k PD); 31/32 DCHG/DDSG = `AFE_FLT_CHG_N` / `AFE_FLT_DSG_N` (no PD on this sheet: the single 100 k PD pair sits on sheet 07 at the 74LVC1G11 inputs, integration fix 2026-11-23); 33 RST_SHUT (10 k PD); 34 REG2 (cap DNP); 35 REG1 = `AFE_REG1`; 36 REGIN; 37 BREG; 38 FUSE = `AFE_FUSE` (100 k PD fitted); 39/40/43/45 PDSG/PCHG/DSG/CHG and 41/42 LD/PACK straight to J206 (10 k R_LD / R_PACK sit on the power board per contract — the P3 R255/R256 are removed from this sheet); 46 CP1; 47 BAT.
* **Balancing stage n (1…16):** Q20n C → R(217+n) 33 Ω → `02_CELLn`; E → `02_CELL(n−1)`; B → `02_QBn_B` → R(233+n) 220 Ω → `02_VC(n−1)`; D20n K = base, A = emitter (AN81 Fig 2-5, C §4.3).
* **J201** (Micro-Fit 2×9, row-wise numbering per Molex SD-43045-001 p.1 and the KiCad footprint): pin 1 = `02_CELL0_HARN` → R274 10 Ω pulse-proof → GND_PWR; pin k+1 = `02_CELLk` (k = 1…16); pin 18 = `BAT_SNS` (D-15), with D228 backup from `02_CELL16`. On-board `02_CELL0` (R201, Q201.E, D201.A) ↔ GND_PWR by NT201 at the AFE VSS point (DS p.71; review R2-02).
* **J202** (Micro-Fit 2×4): 1 NTC1 (TS1), 3 NTC2 (HDQ), 5 NTC3 (TS3), 7 NTC4 → `NTC_PACK4` (MCU mux, sheet 10); 2/4/6/8 GND_PWR returns. **J203** (DNP, 2×2): 1 `NTC_PACK5`, 3 `NTC_PACK6`, 2/4 GND_PWR.
* **J204** (2×2): 1 `02_ABAL_EN_OD` (Q218 drain), 2 `02_ABAL_GND` → R275 10 Ω → GND_PWR, 3 +5V via F201, 4 NC.
* **J205** (DNP, 2×2): 1 coil− = Q219 drain, 2 coil+ (pack-powered through the coil harness, fused externally), 3 2nd-level protector input (R272), 4 GND_PWR. D226 across 1–2.
* **I2C pull-ups:** R257 / R258 to `02_I2C_PU`, fed from `AFE_REG1` through D227 BAT54WS (V_F 0.32 V at 1 mA → bus high ≥ 2.98 V, Diodes DS30098 p.2). C201 (cell 1) is VC1 → VSS (FAQ p.18 §7.5).
* **D229 / D230 / D231 BAS21** (A GND_PWR, K pin) clamp `AFE_DSG`, `AFE_LD`, `AFE_PACK` at the BQ pins (R1-02; sheet 07 drops D722).
* **D225 BAV170:** 1 A = `02_TS2_D` (TS2 via R276 1 kΩ), 2 A = `WAKE_BTN_N`, 3 K = `WAKE_BTN_RAW` (C §6.1; pinout JCET DS p.1). The 1 MΩ `WAKE_BTN_N` pull-up to AFE_REG1 is **not** on this sheet (R824 on sheet 08; latch on sheet 01).
* **J206:** exactly the contract map v1 (netlist self-check compares pin by pin).

## Test points

| TP | Net | Type | Proves at bring-up |
|---|---|---|---|
| TP201 | GND_PWR | black hook | probe ground at the AFE star |
| TP202 | AFE_REG1 | red hook | REG1 = 3.3 V after OTP (REG0 chain alive) |
| TP203 | 02_REG18 | THT pad | internal 1.8 V LDO up |
| TP204 | 02_REGIN | THT pad | ≈ 5.5 V REG0 output (C §9.1) |
| TP205 / TP206 | AFE_SCL / AFE_SDA | THT pad | fixture I2C for OTP / calibration |
| TP207 | AFE_ALERT | THT pad | INITCOMP / alarm |
| TP208 | AFE_RST_SHUT | THT pad | reset / ship control |
| TP209 | AFE_DFETOFF | THT pad | BOTHOFF state from the kill AND |
| TP210 / TP211 | AFE_FLT_DSG_N / AFE_FLT_CHG_N | THT pad | fault outputs (0xAA config) |
| TP212 | BAT_SNS | THT pad | 11.5 V OTP supply path (C §9.1) |
| TP213 | 02_CP1 | THT pad | charge pump ≈ BAT + 11 V (new, AGENT DECISION) |

No pads on filter-internal nodes (VCn, SRP/SRN, TSn, BAT after R251). TP203–TP213 are `in_bom no`; NT201 is a net tie, not in BOM.

## DNP list

| Ref | Why | Fit only if |
|---|---|---|
| C221 | REG2 disabled in the OTP image | REG2 is enabled |
| C225, C226 | optional SRP/SRN-to-VSS caps (DS p.66) | CC noise at bring-up needs them |
| D223, D224, J203 | pack NTC 5–6 option | 6 pack NTCs wanted |
| R271, R272, Q219, D226, J205 | FUSE / breaker shunt-trip path (D-16) | the owner picks a fuse / breaker (R272 only with a secondary protector, D226 only for an inductive coil) |
| D232 | Schottky across the D225 TS2 leg (P5C-02) | TS2 > 0.6 V with the button pressed at −40 °C (bring-up gate) |

## AGENT DECISIONS (owner may overrule)

| # | Question (bom_G2 / task) | Choice | Why | Source |
|---|---|---|---|---|
| AD-02-1 | Q1 C_BAT1 voltage | **C217 = 1 µF 250 V X7R 1812 (C381468)** (P-07) | 58.4 V on 250 V = 23 %; 100 V part fails 2× rule | P-07; BQ DS p.65 |
| AD-02-2 | Q3 SRP/SRN filter placement | **TI arrangement:** R253/R254 = 100 Ω at the BQ (C22775), 2 × 20 Ω averaging on sheet 04 | filter at the device as TI asks; τ 22 µs vs 20 µs | bom_G2 F-3; BQ DS p.66, p.77 |
| AD-02-3 | Q4 NTC_BAL placement | **RT201 stays on sheet 02** (physically in the R_BL bank), bias 10 k from +3V3_A on sheet 10 | sensor with the bank it measures; one bias per net | ARCH §10; bom_G3 R1006–R1010 |
| AD-02-4 | Q5 / P-13 connectors | **Micro-Fit 3.0 R/A, −40…+105 °C:** J202 430450800 (C122422), J203/J204/J205 430450400 (C122413) | JST XH is −25 °C (D-14); LCSC has stock (10 047 / 47 172) | live LCSC + JLC 2026-11-23; SD-43045-001 |
| AD-02-5 | Q6 C_DF dielectric | **X7R 220 nF 0603 (C64705) accepted** | 3.65 V on 50 V, RC needs only 44 µs ≪ 3 ms; C0G 220 nF is 1206 only (+16 large parts) | bom_G2 F-11 |
| AD-02-6 | Q8 balance bank at 85 °C ambient | **keep 33 Ω 1 W (C53728) + firmware throttle** on NTC_BAL (local ≤ 95 °C) and Max Internal Temp | balancing is only allowed at cell temp ≤ 50 °C (image Max Cell Temp 50 °C), so ambient while balancing ≤ ≈ 50 °C: 50 + 40 K = 90 °C local → 0.76 W rating, 0.38 W = 50 % (calc, UNI-ROYAL DS p.5 linear 70→155 °C). The 2 W C2793905 has stock for ≈ 190 boards only | bom_G2 F-6; C §8.2 |
| AD-02-7 | Q9 balancer enable FET | **BSS138BK (60 V, specified at 2.5 V gate; review R2-09) and module enable ≤ 50 mA** | module voltages unknown → keep 60 V; 50 mA = 43 % of 115 mA | bom_G2 F-12 |
| AD-02-8 | Q10 CELL_0–VSS tie | **NT201 net tie on the control board** between `02_CELL0` and GND_PWR at the AFE VSS point; J201 pin 1 split off via R274 (review R2-02) | TI requires VC0 → R → VSS on the PCB before any cell attaches (DS p.71). Ground-loop risk → owner question 1 | BQ DS p.71 |
| AD-02-9 | P-13 for J205 / FUSE path | J205 becomes Micro-Fit 2×2 carrying coil−, coil+, 2LVL input, GND | control board has no BAT+/PACK+ net; coil supply comes with the coil harness (D-16 "pack-powered"); 2LVL input gives R272 a source | C §7; D-16 |
| AD-02-10 | AFE_FUSE pull-down position | R273 100 k directly on the FUSE pin (not the gate) | keeps the pin defined while R271/Q219 are DNP | ARCH §10 AFE_FUSE 100 k PD |
| AD-02-11 | Q217 FCX495 symbol | `Transistor_BJT:BCX56` (1 B, 2 C, 3 E) + `SOT-89-3` (pad 2 = tab) | FCX495 DS p.1 top view: tab = C, leads E-C-B → with leads down, left→right B-C-E = standard SOT-89 numbering | FCX495 DS DS33057 Rev 8-2 p.1 |
| AD-02-12 | Q219 symbol | `Transistor_FET:IRLML0030` (G1 S2 D3) with Value IRLML0100TRPBF | no stock IRLML0100 symbol; IR DS p.1 drawing shows G=1, S=2, D=3 | IRLML0100 DS p.1 |
| AD-02-13 | TP213 on 02_CP1 | added THT pad | pump check at bring-up; DC node with 2.2 µF, probe-safe | instruction §5.5 |
| AD-02-14 | BQ pins 19 / 44 | left `NC` (C proposed tie to VSS) | symbol types them no_connect (ERC); DS: not connected to silicon | BQ DS p.5 |

Owner-confirmed picks applied (owner decisions, not AGENT DECISIONs): P-06 (sheet 04), P-07, P-08 (SS8050 / 2N7002 / BAV170 / IRLML symbols with numbered pins), P-13, X5R allowed (no bulk cap on this sheet needed it; C219/C220 stay X7R in the warm balancing area).

## New interface signals

None. Every off-sheet net used here is in ARCHITECTURE §10 or the contract (`NTC_PACK5`, `NTC_PACK6` = the §10 `NTC_PACK4..6` row; `VSUP_TAP` = contract pin 1).

| Signal | From → to | Note |
|---|---|---|

## B2B change requests

None. J206 = contract map v1 exactly. Observation for sheet 03 (not a B2B change): with J206 unplugged `OC_TRIP_N`, `KILL_N`, `ISENSE_OUT`, `NTC_SHUNT` float at the MCU; the MCU side should not read them as "OK" (e.g. weak PD on `OC_TRIP_N` at PC8).

## Integration fixes applied 2026-11-23

* **R264 / R265 removed** (AFE_FLT_DSG_N / AFE_FLT_CHG_N 470 k PDs). One pair stays on the power board (sheet 07), changed to 100 k because the 74LVC1G11 input leakage is up to ±5 µA (470 k → 2.35 V). With J206 unplugged the BQ pins then have no PD on the control board; they are push-pull when REG1 is up and the kill logic sees its own PDs, so this is acceptable.
* **DDSG / DCHG drive into 100 k: OK.** BQ DS p.11: DCHG / DDSG driving from REG1 give VOH ≥ 0.9 × VREG1 at IOH = −5 mA and VOL ≤ 0.77 V at IOL = 5 mA (row stated for the 5 V REG1 setting; no separate 3.3 V row → 3.3 V behaviour est. similar). 3.3 V / 100 k = 33 µA is ≈ 150× below the 5 mA test current, so VOH ≈ VREG1 (≥ 2.97 V ≫ LVC VIH 2.0 V at 3.3 V). REG1 load 2 × 33 µA = 66 µA (1.3 % of the 5 mA budget). In SHUTDOWN the pins are Hi-Z (TRM p.61) → 100 k PD reads "fault", as required.

## Integration notes (duplicates in the P3 BOM — keep one)

* NTC_BAL: RT201 (here) vs RT1002 (P3 BOM group G3, sheet 10) → keep RT201, drop RT1002.
* BAL_EXT_EN pull-down: R270 here at the Q218 gate vs R827 (sheet 08) → keep R270 (at the FET), drop R827.
* WAKE_BTN_N 1 MΩ pull-up: not on sheet 02 (R824 on sheet 08 / latch on sheet 01).
* `DFETOFF_RB`: not drawn here; sheet 08 taps `AFE_DFETOFF` (R811 series resistor into U801 P07; 470 k after review R3-04).
* R_LD1 / R_PACK1 (P3 R255 / R256) moved to the power board (contract, bom_G1 Q8): refs R255/R256 are unused on this sheet.

## Unverified items

1. **J201 stock:** C293541 has JLC 437 / LCSC 12 today (2026-11-23) — less than one production lot. Gold-flash variant 430451801 (C19793486, 674, −40…+105 °C, ≈ $4.4, same footprint; jlcsearch only, not checked on the LCSC API) is the fallback. The HCTL clones are −25 °C.
2. ~~FCX495 pin numbers~~ — closed by review R2-26 (independent read of DS p.1 gives the same B-C-E).
3. **Molex 43045 footprints:** pin numbering checked against SD-43045-001 p.1 (circuit 1/2 in the row next to the pegs); land dimensions taken from the KiCad stock footprints, not re-measured.
4. **Samsung CL10C102JB8NNNC (C163508)**: series DS not read; listing values used.
5. **2512 derating above 70 °C** read from the UNI-ROYAL DS p.5 curve via bom_G2 (not re-opened).
6. **Active-balancer module enable** current / voltage (unknown module).
7. **J206 / J701 stack height** (6 mm male into the C5337168 female) — mechanical fit not checked.
8. Test hooks RH-5000/5001 temperature rating not checked (not in the P-13 list).

## Owner questions that remain

1. ~~CELL_0 ground loop~~ — resolved by review R2-02 (see "Review disposition"). Original text: With NT201 and a populated CELL_0 harness wire, the CELL_0 wire runs in parallel with the main B− cable: at 200 A a 0.2 mΩ B− cable drops ≈ 40 mV, driving ≈ 0.6 A through a 1 m AWG22 CELL_0 wire + contacts (≈ 63 mΩ, calc est.); if the B− cable opens, load current flows in the sense wire. Options: (a) keep NT201 and leave J201 pin 1 unpopulated in the harness (cell 1 then includes the B− cable drop → BQ Cell 1 Interconnect compensation), (b) replace NT201 with a 10 Ω 0603 (C22859-class, ≈ 4 mA loop, acts as a fuse on a B− open), (c) keep as drawn + inline fuse in the CELL_0 wire. Recommendation: (b).
2. FUSE / breaker part (D-16) still open — the J205 path stays DNP.
3. J201 lot stock (unverified item 1): reserve parts or accept the gold variant.

## Blank-part programming sequence (review R2-04, R2-06)

A blank BQ76952PFBR talks I2C **without CRC** at 0x10 and has **REG1 disabled** (BQ DS p.4), so `AFE_REG1` and the board I2C pull-ups are dead until the first configuration write.

1. Fixture, no cells: 11.5 V on J201 pin 17 (`02_CELL16` → VC16) and **12.3 V on pin 18** (`BAT_SNS` → BAT ≈ 11.7 V after D218, inside the 10–12 V OTP window; REG0 then has ≈ 2.2 mA headroom at the 4.1 V REGIN minimum, DS p.13 — R2-06). Return through TP201 (GND_PWR hook) or the B2B ground, not J201 pin 1 (R274 = 10 Ω). D228 is reverse-biased by 0.8 V in this step.
2. Hold the MCU in reset through SWD NRST (PA15 / PB7 Hi-Z). Board +3V3 may stay off.
3. Fixture pull-ups 2.2–4.7 kΩ to its own 3.3 V on TP205 / TP206. D227 is reverse-biased (I_R ≤ 2 µA at 25 V, Diodes DS30098 p.2), so nothing back-feeds `AFE_REG1` / the REG1 pin (abs max VREGIN + 0.3 V, DS p.7). Bus ≤ 100 kHz.
4. Unseal (default keys), CONFIG_UPDATE, write REG0 Config = 0x01 and REG12 Config = 0x0D first → REG1 = 3.3 V; check TP202 / TP204. The board pull-ups on `02_I2C_PU` then work in parallel with the fixture ones.
5. Load the rest of the image (C §8.2) with Comm Type 0x12 (I2C + CRC) last; exit CONFIG_UPDATE and continue with CRC.
6. Calibration and OTP per C §9.2 (REG1 load during OTP ≤ 1.8 mA).

## Review disposition (R2 power tree / AFE, R1 power board — items on sheet 02)

| ID | Disposition | Change |
|---|---|---|
| R2-02 MAJOR | **fixed** | NT201 kept for the on-board VC0 node (`02_CELL0`: R201, Q201.E, D201.A). J201 pin 1 on its own net `02_CELL0_HARN` → **R274 10 Ω CRCW1206-HP (C511457)** → GND_PWR. Consequence: cell 1 reads V_cell1 + I × R(B− cable + lug + B2B ground) ≈ ±40 mV at 200 A for 0.2 mΩ (est.). BQ Cell 1 Interconnect is integer mΩ (TRM p.170), so **the MCU compensates its cell-1 reading from the CC current**, and the **B− cable + lug must be ≤ 0.1 mΩ** (≤ 20 mV at 200 A, inside the 43 mV gap between firmware 3.60 V and COV 3.643 V). Harness: pin 1 optional; B− lug first on, last off |
| R2-03 MAJOR | **fixed** | C201 pin 2 → GND_PWR (VC1 to VSS, FAQ p.18 §7.5) |
| R2-04 MAJOR | **fixed** | D227 BAT54WS-7-F (C124205): A `AFE_REG1`, K `02_I2C_PU`; R257 / R258 moved to `02_I2C_PU`; programming sequence above |
| R2-06 MINOR | **fixed (procedure)** | OTP fixture: pin 18 at 12.3 V, pin 17 at 11.5 V, I2C ≤ 100 kHz (steps 1, 3) |
| R2-07 MINOR | **fixed** | R251 → 100 Ω 1206 CRCW-HP pulse-proof (C844642) |
| R2-08 MINOR | **fixed** | R216 (R_VC15) → 100 Ω 1206 0.25 W (C17901, Basic): 62 mW = 25 % |
| R2-09 MINOR | **fixed** | Q218 → BSS138BK (ElecSuper, C5224267): RDS(on) ≤ 4.5 Ω at VGS 2.5 V / 0.1 A, VGS(th) 0.8–1.5 V (DS p.3), 60 V |
| R2-10 MINOR | **fixed** | J204 pin 2 → `02_ABAL_GND` → R275 10 Ω CRCW1206-HP → GND_PWR (≈ 4 mA parallel-path limit); may become 0 Ω or an opto once the module is known |
| R2-11 MINOR | **fixed** | R276 1 kΩ between U201.22 and D225.1; leakage budget on `WAKE_BTN_RAW` (≪ 0.5 µA over temperature) handed to sheet 08 |
| R2-12 MINOR | **fixed** | D228 1N4148WS A `02_CELL16`, K `BAT_SNS` (owner may overrule D-15) |
| R2-13 MINOR | **fixed (note)** | SHUTDOWN / Ship is delayed while LD > 0.8–2.25 V (DS p.53): with a charger or parallel pack holding PACK+, the pack cannot reach the 8 µA Ship state. System note for the sheet 07 owner; no LD pull-down option added here |
| R2-14 MINOR | **fixed (text)** | Sleep budget: with output off (D-01) DDSG / DCHG are low → 0 µA in the sheet-07 100 k PDs; the "output live" Sleep option adds 2 × 33 µA = 66 µA (calc). ARCHITECTURE §4.3 text to be corrected at integration |
| R2-17 MINOR | **fixed (layout gate)** | J206 ↔ J701 pin 1 ↔ pin 1 check in the 3D stack and on a 1:1 print before release (a row swap puts VSUP_TAP on AFE_PACK) |
| R2-26 NOTE | closed | FCX495 unverified item closed |
| R2-27 / R2-28 / R2-30 NOTE | noted | firmware rule: AFE_ALERT / WAKE_BTN_N read low while the AFE is off — not an alert / button press |
| R2-29 NOTE | noted | harness spec: ≤ 0.5 A fuse per tap at the cells |
| R2-31 NOTE | noted | TP212 / TP213 are 58–71 V pads: HV clearance in layout |
| R1-12 MINOR (B2B) | **fixed** | J206 pin 8 = `AFE_DSG` (second contact, interface contract rev.) |
| R1-02 MAJOR (sheet 02 part) | **fixed** | D229 BAS21 VSS → `AFE_DSG` clamp (replaces sheet 07 D722, which was deleted there), D230 VSS → `AFE_LD`, D231 VSS → `AFE_PACK` (BAS21 C7502725, 250 V; A GND_PWR, K pin). The AN09 Fig 5-2 gate-network rebuild is on sheet 07 |
| P5C-02 | **fixed** | D232 BAT54WS-7-F (C124205, reused from D227 — no new LCSC number), **DNP**, in parallel with the D225 TS2 leg: A `02_TS2_D`, K `WAKE_BTN_RAW`. Fit if TS2 > 0.6 V with the button pressed at −40 °C (bring-up gate). Block: Host I/F + fault pins |
| P5C-08 | **fixed** | On-sheet note at U201: pin 25 = ALERT, pin 28 = HDQ (stock symbol pin names `HDQ_IO/ALERT` / `HDQ_IO/SPI_MOSI`); no net change |

## Live verification of LCSC numbers (2026-11-23)

Every number below was queried on 2026-11-23 through the LCSC product API (`wmsc.lcsc.com/ftps/wm/product/detail`) and the JLCPCB parts API (`selectSmtComponentList`, exact componentCode). MPN and manufacturer are copied from the record; both APIs returned the same MPN.

| LCSC | MPN | Mfr | JLC type | Stock LCSC / JLC | Refs |
|---|---|---|---|---|---|
| C2862742 | BQ76952PFBR | TI | Extended | 11478 / 11479 | U201 |
| C293541 | 430451800 | MOLEX | Extended | 12 / 437 | J201 |
| C22775 | 0603WAF1000T5E | UNI-ROYAL | Basic | 3671300 / 12717986 | R201..R260 (23) |
| C17901 | 1206W4F1000T5E | UNI-ROYAL | Basic | 791600 / 1738059 | R216 |
| C22950 | 0603WAF200JT5E | UNI-ROYAL | Basic | 320500 / 1081137 | R217 |
| C64705 | CL10B224KB8NNNC | Samsung Electro-Mechanics | Extended | 289360 / 355732 | C201..C216 (16) |
| C511457 | CRCW120610R0FKEAHP | VISHAY | Extended | 61010 / 65985 | R274, R275 |
| C2128 | 1N4148WS | JSCJ | Basic | 1040600 / 3222022 | D228..D218 (19) |
| C7502725 | BAS21 | R+O | Extended | 149650 / 152448 | D229, D230, D231 |
| C2150 | SS8050(RANGE:200-350) | JSCJ | Basic | 2005300 / 3219229 | Q201..Q216 (16) |
| C53728 | 25121WF330JT4E | UNI-ROYAL | Extended | 4800 / 32687 | R218..R233 (16) |
| C22962 | 0603WAF2200T5E | UNI-ROYAL | Basic | 480700 / 2264065 | R234..R249 (16) |
| C13564 | NCP18XH103F03RB | muRata | Extended | 218390 / 228475 | RT201 |
| C620876 | 25121WF3301T4E | UNI-ROYAL | Extended | 5600 / 23740 | R250 |
| C150457 | FCX495TA | DIODES | Extended | 720 / 1434 | Q217 |
| C7250 | 0603WAF1005T5E | UNI-ROYAL | Basic | 380000 / 869179 | R252 |
| C21122 | CL10B223KB8NNNC | Samsung Electro-Mechanics | Basic | 337000 / 1107853 | C218 |
| C844642 | CRCW1206100RFKEAHP | VISHAY | Extended | 75300 / 75304 | R251 |
| C381468 | FS43X105K251EGG | PSA | Extended | 66925 / 87985 | C217 |
| C50254 | CL31B225KBHNNNE | Samsung Electro-Mechanics | Basic | 4870 / 284540 | C222 |
| C19110 | CL21B225KAFNNNE | Samsung Electro-Mechanics | Extended | 771540 / 849416 | C219, C221 |
| C3039701 | CL21B475KOFNFNE | Samsung Electro-Mechanics | Extended | 4560 / 4571 | C220 |
| C363929 | GRM3195C1H104JA05D | muRata | Extended | 0 / 8817 | C223 |
| C14858 | CL10C101JB8NNNC | Samsung Electro-Mechanics | Basic | 57500 / 2950463 | C224 |
| C14663 | CC0603KRX7R9BB104 | YAGEO | Basic | 227500 / 52250351 | C225, C226 |
| C163508 | CL10C102JB8NNNC | Samsung Electro-Mechanics | Extended | 154350 / 188162 | C227, C228, C229, C230 |
| C19224 | PESD5V0S1BA,115 | Nexperia | Extended | 132915 / 139480 | D219..D224 (6) |
| C122422 | 430450800 | MOLEX | Extended | 10047 / 10295 | J202 |
| C122413 | 430450400 | MOLEX | Extended | 47172 / 47174 | J203, J204, J205 |
| C23162 | 0603WAF4701T5E | UNI-ROYAL | Basic | 5759100 / 18995280 | R257, R258 |
| C25804 | 0603WAF1002T5E | UNI-ROYAL | Basic | 0 / 42079659 | R261, R262 |
| C25803 | 0603WAF1003T5E | UNI-ROYAL | Basic | 3380900 / 12793234 | R263, R270, R273 |
| C68970 | BAV170 | JSCJ | Extended | 11460 / 11906 | D225 |
| C21190 | 0603WAF1001T5E | UNI-ROYAL | Basic | 13282000 / 39615039 | R276 |
| C124205 | BAT54WS-7-F | DIODES | Extended | 79355 / 79265 | D227 |
| C5224267 | BSS138BK | ElecSuper | Extended | 38470 / 38471 | Q218 |
| C20975 | SMD0805P010TF | RUILON | Extended | 75060 / 76478 | F201 |
| C23186 | 0603WAF5101T5E | UNI-ROYAL | Basic | 12780900 / 18155776 | R271, R272 |
| C53658 | IRLML0100TRPBF | Infineon | Extended | 21700 / 21904 | Q219 |
| C82648 | ES1D-E3/61T | VISHAY | Extended | 93461 / 93461 | D226 |
| C56496 | 2.54-2*15P | BOOMELE(Boom Precision Elec) | Extended | 6215 / 6216 | J206 |
| C5199801 | RH-5001 | ronghe | Extended | 97335 / 99458 | TP201 |
| C5277086 | RH-5000 | ronghe | Extended | 194800 / 194802 | TP202 |

Unique LCSC numbers: 16 Basic, 27 Extended.
