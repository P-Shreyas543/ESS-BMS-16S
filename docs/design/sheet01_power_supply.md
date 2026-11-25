# Sheet 01 — Power Supply (control board, refs 1xx) — design note (v1.2)

Schematic v1.2, 2026-11-25 (sheet revision v1.2, A3, HYBRID). Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 01). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md), [v1.1 power-tree review](../reviews/v11_power_tree_review.md), [v1 vs v1.1 comparison](../reviews/v1_vs_v11_comparison.md).

**Revision v1.2 (2026-11-25, owner decision `PROJECT.md` §5 row "v1.2", HYBRID):** `+5V` trunk and power latch = v1.0 design (`LM5013`, commercial `LM5013DDAR` C5383001), `+5V_ISO` = v1.1 chain with AEC-Q100 `SN6505B-Q1` (C1849490) + `T101` + `TLV76750`, see §14. The v1.1 `LM5146-Q1` design is archived on git commit `ca3a7a3` as fallback.

**Count:** 95 refs = 93 fitted (of which 6 copper-only, not in the BOM: test pads TP109, TP110, TP111, TP113, TP114, TP115) + 2 DNP; 49 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, V11-xx / N-xx = v1.1 review findings, F-xx = v1-vs-v1.1 comparison findings.

## 1. Blocks (dashed boxes), placement left → right

| # | Box title | Refs | Placement / flow |
|---|---|---|---|
| 1 | Supply input (VSUP_TAP / AUX) | R101 R102 D101 D103 C101-C103 J101 F101 D102 R103 R127 TP101 TP107 TP109 TP110 | far left. Top row: `VSUP_TAP` (hier. input from J206 pin 1, sheet 02) → R101 → R102 → `VSUP_F` → D101 → `VSUP`. Bottom row: J101 → F101 → `AUX_IN` → D102 → `VSUP`. D103 + C101-C103 on the `VSUP` node right of the OR |
| 2 | +5V trunk (U101 LM5013-Q1) | U101 R104-R108 C105-C110 D104 L101 TP102 TP111 | centre top; `VSUP` in left, `+5V` power symbol out right |
| 3 | +12V switched leaf (U102 LM5163-Q1) | C104 U102 R113-R116 C112-C116 L102 TP104 | centre bottom, fed from `VSUP`; `EN_12V` hier. input |
| 4 | +3V3 / +3V3_A (U103) | U103 C117-C120 FB101 TP103 | right of box 2, from `+5V` |
| 5 | +3V3_ESP (U104) | U104 C121-C124 L103 R118 R119 TP105 | right, from `+5V`; `EN_ESP` hier. input |
| 6 | +5V_ISO (U105 TPS22918 + U106 SN6505B-Q1 + U107 TLV76750) | U105 C125 C126 U106 C127 C139 T101 D110 D111 C128 C140 U107 C129 TP106 TP108 TP115 | far right: `+5V` → U105 → `01_ISO_VIN` → U106 → T101; barrier drawn as a vertical dashed line through T101 (primary pins 1-2-3 left, secondary 6-5-4 right); D110/D111 → `01_ISO_RECT` → U107 → `+5V_ISO`, `GND_ISO` side right |
| 7 | Power latch (PWR_EN) | Q101 Q102 D105-D108 R109-R112 R123-R126 C111 TP113 TP114 | below box 1/2, `PWR_EN` wire into U101 pin 3 |
| 8 | VBAT_MCU OR | D109 | bottom right; `VBAT_MCU` hier. output |

Hierarchical labels: inputs `VSUP_TAP`, `PWR_HOLD`, `WAKE_BTN_N`, `AFE_ALERT`, `EN_12V`, `EN_ESP`, `EN_ISO`; outputs `PG_5V`, `VBAT_MCU`. Power symbols: `+12V +5V +3V3 +3V3_A +3V3_ESP +5V_ISO GND_PWR GND_ISO AFE_REG1`. PWR_FLAG (v1.2 mix, ERC): **`VSUP`** (driven by diodes only), **`+3V3_A`** (fed through a bead), **`GND_ISO`** (no source pin), **`01_ISO_RECT`** (U107 IN power_in behind D110 / D111); **none on `+5V_ISO`** (driven by the U107 OUT power_out pin, review V11-10); `AFE_REG1` / `GND_PWR` only if the sheet-02 owner does not flag them. (`01_U101_VIN` of v1.1 no longer exists: U101 VIN is on `VSUP` directly.) `VSUP`, `VSUP_F`, `AUX_IN`, `FORCE_ON`, `PWR_EN` are names from ARCHITECTURE §10 and stay sheet-local labels here.

## 2. Key number per block (on-sheet note)

| Box | Note | Calc / source |
|---|---|---|
| 1 | "R_DAMP 4.4 Ω: hot-plug 13 A pk, I²t 0.0034 A²s vs F701 0.53 A²s; TVS ≈ 79 V @25 °C < 100 V" | 58.4/4.4 Ω; V²C/2R with 8.8 µF; (96.8−70)/(4.4+1.49) ≈ 3.8 A → ≈ 79 V (review R2-15 calc, est.) |
| 2 | "+5V: 321 kHz, 5.03 V, peak load 0.96 A = 27 % of 3.5 A" | 5×2500/39k (DS p.12); 1.2×(1+150/47) (DS p.5); ARCH §4.2 |
| 3 | "+12V: 305 kHz, 12.2 V, 0.15 A of ≈0.47 A" | 12.2×2500/100k; 1.2×(1+220/24); ARCH §4.2 |
| 4 | "U103 0.40 W @ 233 mA → Tj 111 °C @ 85 °C" | (5−3.3)×0.233 × 63.9 °C/W (TPS7B82 DS p.6) |
| 5 | "COUT 22 µF + 10 µF at the module (C123 DNP); VOUT 3.33 V" | TLV62569 DS p.9 Table 4; 0.6×(1+100/22) |
| 6 | "SN6505B-Q1 424 kHz → T101 1:1.3 → 2 × MBR0520L → TLV76750 5.0 V; 2.5 kV barrier; +5V_ISO 4.90-5.05 V; 300 mA = 0.40 A from +5V" | iso study calc (§12); CT 330 pF → 1.06 ms (TPS22918 DS p.14) |
| 7 | "PWR_EN hold 0.66 s; off < 0.45 V (shutdown falling); ≤ 19.5 V via FORCE_ON / AUX; wake pulse: charge τ ≈ 1 ms, ALERT latched or low ≥ 2 ms" | 1 MΩ×1 µF×ln(2.7/1.4); LM5013 DS SNVSCB3 p.6 (= LM5013-Q1 DS p.5); 58.4×1M/3M; §14.3 |
| 8 | "VBAT_MCU = max(+3V3, AFE_REG1) − 0.3 V" | BAT54C |

## 3. Test points

| TP | Net | Type | Proves |
|---|---|---|---|
| TP101 | VSUP | red hook | input OR + TVS node |
| TP107 | GND_PWR | black hook | probe ground, control-board power area |
| TP109 | VSUP_F | THT pad | F701 + R_DAMP path (compare with TP101 → D101 drop) |
| TP110 | AUX_IN | THT pad | F101 + AUX presence |
| TP102 | +5V | red hook | U101 output |
| TP111 | PG_5V | THT pad | U101 PGOOD |
| TP104 | +12V | red hook | U102 output |
| TP103 | +3V3 | red hook | U103 output |
| TP105 | +3V3_ESP | red hook | U104 output |
| TP106 / TP108 | +5V_ISO / GND_ISO | red / black hook | U107 output (isolated side) |
| TP115 | 01_ISO_RECT | THT pad (v1.1, kept) | rectifier output = U107 headroom (≥ 5.4 V at 300 mA) |
| TP113 / TP114 | FORCE_ON / PWR_EN | THT pads | EOL pogo short |

Removed vs P3 `bom_G1`: TP112 (+3V3_A pad) — no pad after a bead (instruction §5.5); `+3V3_A` is measured at TP402 (sheet 04). Unused refs (traceability to `docs/bom/bom_G1.md`): R117, R120, R121, TP112. Retired in v1.1 and not re-used: R122, R128 (v1.0 dummy load). The v1.1-only refs Q103-Q105, R129-R139, C130-C138 do not exist in v1.2 (archived on commit `ca3a7a3`); free for later use only with a traceability note.

## 4. DNP list

| Ref | Why | Fit only if |
|---|---|---|
| C124 6.8 pF | U104 feed-forward | load-step response of +3V3_ESP needs it |
| C123 22 µF | 2nd +3V3_ESP output cap | a load-step test needs it (review R2-16) |

## 5. AGENT DECISIONS (owner may overrule)

`docs/bom/bom_G1.md` §6 questions 1-11 (owner delegated, 2026-11-23), along the file's recommendations:

| Q | Question | Choice | Why / source |
|---|---|---|---|
| 1 | F_SUP location | F701 at the B+ lug on the power board, `VSUP_TAP` on B2B pin 1 (sheet 07) | P-02 (owner-accepted); B2B pin map |
| 2 | 250 V MLCCs | 2.2 µF 250 V 2220 (C153032) on every 58 V node: C101-C104 here | P-01 (owner-accepted), 2× rule |
| 3 | PDSG/PCHG blocking diodes | fitted (sheet 07 D711/D712) | P-03 |
| 4 | R_PRE / R_PCHG sourcing | sheet 07 | — |
| 5 | Shunt | owner chose C558625; sheet 04 | — |
| 6 | M6 torque | sheet 07 | — |
| 7 | Non-AEC TPS22918DBVR / TLV62569DBVR (v1.2: plus TLV76750DRVR and the commercial LM5013DDAR, owner choice) | **accept** both (the -Q1 TPS22918 has ~114 pcs; no AEC buck at the price) | `docs/bom/bom_G1.md` §5 item 9; recommendation |
| 8 | R_LD / R_PACK | on the power board (sheet 07 R751/R752) | contract |
| 9 | Numbering | heater 7xx on sheet 07; shunt + NTC_SHUNT → sheet 04; male J_B2B = J206 on sheet 02 | owner 2026-11-23 two-project decision + contract |
| 10 | TPS22918 ramp | **C126 = 330 pF C0G (C1664, Basic)** → 1.06 ms | kept in v1.1 / v1.2: limits the inrush into C127 10 µF + C139 to 48 mA (calc) ahead of the SN6505B-Q1 soft start |
| 11 | Stack height 11 mm | sheet 07 | — |

Further decisions taken in this spec:

| # | Question | Choice | Why |
|---|---|---|---|
| A1 | J_AUX connector not -40 °C (KF301 C474881 is -30..+120 °C, LCSC API) — P-13 | **Kangnex WJ500V-5.08-2P (C8465)**, -40..+105 °C, UL 300 V / 10 A, 5.08 mm, stock 263 k; footprint stock Phoenix MKDS-1,5-2-5.08 | P-13; WJ500V drawing p.1; same part for J710 on sheet 07 |
| A2 | R_AUXB value | **2 × 33 kΩ 1206 in parallel (R103 + R127, C18004)** = 16.5 kΩ (superseded 47 k after review R2-05) | ES2D IR 100 µA max at 100 °C (DS p.1); board off needs PWR_EN < 0.45 V (shutdown **falling**, LM5013-Q1 DS p.5) → AUX_IN < 1.65 V → 100 µA tolerated; 102 mW each at 58 V = 41 % |
| A3 | EN_ISO / EN_ESP / EN_12V pull-downs | **not placed here** (`docs/bom/bom_G1.md` R117/R120/R121 dropped) | `docs/bom/bom_G3.md` R825-R828 place one per net at the expander U801/U802 ("keep one per net", instruction §8). Confirmed by the integrator 2026-11-23: sheet 08 adds them; none on sheet 01 |
| A4 | WAKE_BTN_N 1 MΩ pull-up to AFE_REG1 | not here; sheet 08 R824 owns it | `docs/bom/bom_G3.md` ownership table |
| A5 | AFE_ALERT 10 k pull-up to AFE_REG1 | not here; sheet 02 R261 owns it | `docs/bom/bom_G2.md` |
| A6 | VBAT_MCU OR | **D109 on sheet 01** (interface contract) | Coordination: `docs/bom/bom_G3.md` lists the same BAT54C as D301 on sheet 03 — sheet 03 must drop D301 (and R301/C311 stay there, fed from `VBAT_MCU`) |
| A7 | U102 PGOOD | NC (open drain unused) | no MCU pin for +12V status in ARCH §8 |
| A8 | U103 EN | tied to IN (+5V) | VEN ≤ VIN allowed (TPS7B82 DS p.4); B §7 item 2 |
| A9 | U105 QOD | tied to VOUT (internal RPD discharge) | TPS22918 DS p.3; `docs/bom/bom_G1.md` |
| A10 | Symbols | project symbols LM5013-Q1_DDA, LM5163-Q1_DDA (pin-identical copies of stock `LM5164DDA`), TPS7B8233-Q1_DGN, TPS22918_DBV, **Transformer_CT_1P_1S_LT31-113** (v1.1); stock TLV62569DBV, AO3401A, 1N4148WS, BAT54C, 1.5SMCxxA (SMCJ60A: pin 1 = bar = cathode, pin 2 = anode, from the symbol graphics), **SN6505BDBV** (U106, pin-identical for the -Q1, SLLSF95D p.3), **TLV76750DRVx** (U107), D_Schottky (D110 / D111). B0505S-2WR3 removed from project symbols; `LM5013-Q1_DDA` kept for the commercial LM5013DDAR (same DDA pinout, SNVSCB3 p.4) | names must match the part; pins checked vs DS and footprint pads by script |

## 6. New interface signals

None. Every cross-sheet name used here is in ARCHITECTURE §10 or the contract (`VSUP_TAP`).

## 7. B2B change requests

None. (VSUP_TAP on pin 1 is consumed here unchanged.)

## 8. Verification record (live, 2026-11-23)

Every LCSC number on this sheet was re-read live on 2026-11-23 from the **LCSC product API** (`wmsc.lcsc.com/ftps/wm/product/detail?productCode=…`: MPN, brand, package, stock, operating temperature) **and** the **JLCPCB parts API** (`selectSmtComponentList`: JLC stock, Basic/Extended). All MPN + manufacturer match. New numbers this session: C8465 (WJ500V), C1664 (330 pF C0G, Basic, JLC 773 k), C17713 reused for R103. Datasheets downloaded 2026-11-23 (TI parts from ti.com; others from the LCSC datasheet link) and pin tables read with pypdf / pypdfium2 (images rendered where the PDF was drawing-only: AO3401A).

Pin sources: LM5013-Q1 DS p.3 = commercial LM5013 DS SNVSCB3 p.4 (EP no internal connection → GND); LM5163-Q1 DS p.3; TPS7B82-Q1 DS p.3 (DGN: 1 IN, 2 EN, 3/7 NC, 4-6 GND, 8 OUT, PAD); TLV62569 DS p.3 (= stock symbol); TPS22918 DS p.3; SN6505x-Q1 DS SLLSF95D p.3 (1 D1, 2 VCC, 3 D2, 4 GND, 5 EN, 6 CLK); TLV767 DS p.3-4 (DRV fixed: 1 OUT, 2 SNS, 3/5 GND, 4 EN, 6 IN, PAD); LT31-113 spec p.3 / WE 760390014 DS p.1 (primary 1-2-3, CT 2; secondary 6-5-4, CT 5); MBR0520L DS p.1 (cathode band = pad 1); AO3401A DS p.1 image (1 G, 2 S, 3 D); BAT54C DS p.1 (1 A1, 2 A2, 3 K). Footprint pad sets = symbol pins for every ref (netlist check).

Low stock (stock < 10 × need for 100 boards): ~~U101 LM5013QDDARQ1 C5219285: 250 (213 at the v1.2 comparison)~~ → **v1.2 U101 = LM5013DDAR C5383001: LCSC 6 940 / JLC 6 940 (live 2026-11-25)**; **T101 LT31-113 C7471252: JLC 771, JLC-only** (Würth 760390014 C2802211 alternate: 0) — reserve; **C153032 2.2 µF 250 V: JLC 6 379 / LCSC 2 644 vs 1 000 needed (10 per board over both boards)**; **D103 SMCJ60A C2996503 2 624** (second source TWGMC C4154628, 2 713, live).

## 9. Unverified / open technical items

1. R101/R102 sub-ms pulse rating (0.53 J per part at F701 opening) — no single-pulse curve in the HoLRT DS; bench check (carried from `docs/bom/bom_G1.md`).
2. DC-bias derating of C153032 (250 V 2220) and C2918511 (25 V 1210 at 12.2 V) — curves not read (est.).
3. ~~B0505S-2WR3 below 40 mA minimum load~~ — gone since v1.1 (TLV76750 needs no minimum load).
4. ES2D reverse leakage at 58 V / 85 °C is not specified (only 25 °C / 100 °C at rated 200 V); R103 sized on the 100 °C max.
5. FB101 + C120 (1 µF) resonance not computed (bead inductance not in the listing); the LDO output has no 300 kHz content, so low risk.
6. WJ500V drawing asks for Ø1.5 mm holes; stock Phoenix footprint has Ø1.3 mm (pin 0.9 × 0.8 mm, diagonal 1.20 mm, calc). OK for assembly, tight; layout may enlarge to 1.5 mm.

## 10. Owner questions that remain

1. ~~LM5013-Q1 stock (250 pcs)~~ — closed by v1.2: commercial LM5013DDAR (6 940 pcs), owner decision 2026-11-25.
2. Confirm sheet 03 drops D301 (VBAT_MCU OR lives here as D109). (EN_* pull-downs: confirmed on sheet 08.)

## 11. Review disposition (2026-11-23, integrator-accepted items)

| ID | Disposition | Refs changed / evidence |
|---|---|---|
| R2-01 BLOCKER | fixed in v1.0; **void since v1.1** (B0505S removed) | U106 pin 1 = Vin (`01_ISO_VIN`), pin 2 = GND (`GND_PWR`); project symbol corrected. Re-read: EVISUN B0505S DS p.5 pin table (1 Vin, 2 GND, 4 0V, 5 no pin, 6 +Vo) and Fig 3 (read from the rendered image). **Bring-up gate: confirm pins 1 and 2 on a physical sample (diode check, or a 50 mA current-limited supply) before the board order** |
| R2-05 | fixed | New R123 / R124 100 k drain pull-downs and R125 / R126 1 k drain series resistors; the D106 / D107 anodes are now on `01_QBTN_R` / `01_QALRT_R`. R103 → 33 k 1206, plus new R127 33 k 1206 in parallel (C18004). The notes now say the board shuts down below **0.45 V falling** (LM5013-Q1 DS p.5) |
| R2-14 | noted (doc) | The Sleep budget text belongs to the integrator (ARCH §4.3). With the output off (D-01) the AFE_FLT lines are low, so they draw 0 µA |
| R2-15 | fixed | R101 / R102 1 Ω HoLRT → 2.2 Ω 2 W 2512 Yageo RC2512FK-7W2R2L (C876260); the HoLRT family has no 2.2 Ω at LCSC. TVS current ≈ 3.8 A → clamp ≈ 79 V at 25 °C (calc); 2 V drop at 0.46 A; F701 still melts at 13 A (6.5× its rating) |
| R2-16 | fixed | C123 → DNP: 22 µF + 10 µF module cap is inside the TLV62569 matrix (DS p.9 Table 4) |
| R2-20, R2-21, R2-23, R2-24, R2-25 | noted, no change | — |
| R2-22 | bring-up note | In AUX-only bench mode, SS320 leakage (≤ 10 mA at 100 °C, SS320 DS p.2) back-energises VSUP_TAP / BAT+ on the power board. Treat BAT+ as live |
| R2-32 | noted | D-09 still open |
| R3-02 | fixed in v1.0; **void since v1.1** (R122 / R128 dummy load removed with the B0505S) | — |
| R2-02 … R2-13, R2-17, R2-18 | n/a | Sheet 02 / 08 items. R2-17 is already a layout gate (sheet07.md §8 note) |

**New LCSC numbers on this sheet.** All live-verified 2026-11-23 on the LCSC product API and the JLCPCB parts API.

| LCSC | Part | Stock (LCSC / JLC) | Class |
|---|---|---|---|
| C876260 | RC2512FK-7W2R2L | 5 285 / 6 251 | Extended |
| C18004 | 1206W4F3302T5E | 125 400 / 167 078 | Extended |
| C17887 | 1206W4F3000T5E (removed since v1.1) | – | Basic |
| C21190 | 0603WAF1001T5E | – | Basic |

Unverified: the thick-film 2512 single-pulse rating for the 1.2 J fault pulse (no curve published).

## 12. +5V_ISO — v1.1 isolated supply, kept in v1.2 (U106 → SN6505B-Q1)

### 12.1 Topology and values (v1.1, unchanged in v1.2 except U106 → SN6505BQDBVRQ1)

Topology: `+5V` → U105 TPS22918 (`EN_ISO`, CT 330 pF, 1.06 ms) → `01_ISO_VIN` (C127 4.7 µF + C139 100 nF) → U106 SN6505B-Q1 VCC and EN (EN tied to VCC, CLK to GND: internal 424 kHz spread-spectrum clock, DS p.3/p.5) → D1 / D2 drive T101 pins 1 / 3, centre tap pin 2 on `01_ISO_VIN` → secondary 6 / 4 → D110 / D111 → `01_ISO_RECT` (C128 4.7 µF + C140 100 nF, TP115) → U107 IN and EN → OUT / SNS `+5V_ISO` (C129 4.7 µF + sheet 06 C615 10 µF); T101 pin 5 = `GND_ISO`. Why TPS22918 stays: `EN_ISO` is 3.3 V and the SN6505 EN needs 0.7 × VCC (DS p.5); the switch also gives a 0 µA off state (QOD discharge).

| Item | Value | Source |
|---|---|---|
| +5V_ISO (review V11-11, v1.2) | **4.90-5.05 V** at 0-300 mA with the v1.0 +5V = 1.2 × (1 + 150/47) = 5.03 V nominal, 4.87-5.18 V worst (LM5013 VREF 1.181-1.218 V, DS SNVSCB3 p.6); in the cold / low corner the LDO is in dropout at ≥ 280 mA (≈ 4.90 V at 300 mA, calc, ≥ 4.5 V transceiver minimum). **No minimum load.** Hot / high corner: 01_ISO_RECT ≤ 6.87 V no load, U107 ≈ 0.35 W → Tj ≈ 112 °C, T101 7.1 V·µs | iso study calc rescaled (calc); TLV767 DS p.5-6 (VDO 1.4 V max @1 A, COUT ESR 2-500 mΩ) |
| Rectifier / LDO headroom | 01_ISO_RECT 5.36 V (cold, 300 mA) … 6.66 V (no load, 5.1 V in); TLV767 VIN ≤ 16 V | calc; DS p.5 |
| Transformer | applied 7.02 V·µs (5.1 V / 2 / 363 kHz) < 11 V·µs; n = 1.3 ≥ 1.28 required (TI Eq.10) | WE DS p.1; SN6505 DS |
| Diodes | PRV 2 × 6.76 = 13.5 V < 20 V; 95 mW total at 300 mA | MBR0520L DS p.2 |
| Efficiency / +5V draw | 300 mA: η ≈ 76 %, 0.40 A from +5V; idle 20 mA bus: 32 mA from +5V vs ≈ 109 mA for B0505S + dummy (est.) | calc |
| Thermal @85 °C | U107 0.33 W → Tj 111 °C (77.7 °C/W); U106 → 92 °C | calc |
| Ripple | 79 mV pp on 01_ISO_RECT at 300 mA (4.5 µF eff, 848 kHz) | calc |
| Barrier | T101 2.5 kVAC / 60 s (WE 760390014 2500 VAC; LT31-113 2.5 kV); pad gap across the barrier 8.02 mm (> 6.5 mm rule; v1.0 B0505S footprint was 3.58 mm pad 2 to pad 4); D-09 Partly → Met | WE DS p.1, LT31 spec p.2 |

### 12.2 LCSC numbers of the iso chain (live)

| LCSC | MPN | Refs | Stock LCSC / JLC | Date |
|---|---|---|---|---|
| **C1849490** | **SN6505BQDBVRQ1** (TI, AEC-Q100 grade 1, −40…+125 °C TA, SLLSF95D p.1/p.4) | U106 | 3 000 / 3 000 | 2026-11-25 |
| C7471252 | LT31-113 (Linekey) | T101 | – (JLC-only) / 771 | 2026-11-24 |
| C2802211 | 760390014 (Würth), alternate for T101 (md only) | – | – / 0 | 2026-11-24 |
| C23848 | MBR0520LT1G (onsemi) | D110, D111 | 288 830 / 288 839 | 2026-11-24 |
| C2872569 | TLV76750DRVR (TI) | U107 | 4 664 / 4 664 | 2026-11-24 |
| C70462 | CC1206KKX7R8BB106 10 µF 25 V | C127 | 151 945 / 176 912 | 2026-11-25 |
| C29823 / C14663 | 4.7 µF 50 V 1206 / 100 nF 0603 | C128, C129 / C139, C140 | basic, see v1.0 | 2026-11-24 |

SN6505B-Q1 vs SN6505B: same DBV SOT-23-6 pinout (SLLSF95D p.3, Figure 5-1 and Table 5-1: 1 D1, 2 VCC, 3 D2, 4 GND, 5 EN, 6 CLK), same 363-517 kHz, RON 0.25 Ω max, soft-start delay 3.5-18 ms (p.6) → stock symbol `Power_Management:SN6505BDBV` and footprint `SOT-23-6` unchanged; no other circuit change.

### 12.3 Symbols / footprints of the iso chain

* Project symbols: `Automotive_ESS_BMS:Transformer_CT_1P_1S_LT31-113` (pins 1 P1, 2 PCT, 3 P2 left; 6 S1, 5 SCT, 4 S2 right; LT31-113 spec p.3 = WE DS p.1).
* `footprints.pretty/Transformer_WE-PPTI_760390014.kicad_mod`: 6 pads 1.12 × 0.96 mm at x = ±4.57, y = −2.54 / 0 / +2.54 (WE DS p.1, LT31 spec p.2) **with the rule area `T101_barrier_keepout`** (all copper layers, x ±4.0 / y ±3.4 mm, no tracks / vias / pours; review V11-14, **F-06 confirmed present 2026-11-25**).
* Layout: keep the barrier keep-out continuous with the sheet-06 comms barrier; isolation slot optional.

### 12.4 Firmware rules and bring-up gates of the iso chain (kept from v1.1)

* **+5V_ISO ready ≥ 25 ms after `EN_ISO`** goes high (TPS22918 1.06 ms + SN6505B-Q1 soft-start delay ≤ 18 ms, SLLSF95D p.6, + LDO start); ignore `CAN_*_RX` / `RS485_*_RX` until then (sheet 06 rule).
* Gate B8: +5V_ISO 0 → 300 mA at −40 °C and +85 °C: 4.85-5.10 V; TP115 ≥ 5.3 V at 300 mA cold; T101 pin-1 dot = pad 1 on the first article.
* Gate B9: board-level barrier hipot after assembly at the D-09 level, ≤ the 2.5 kVAC / 60 s T101 rating (functional isolation; WE: 400 Vrms working).
* Owner question (V11-12): LT31-113 spec has no temperature range / AEC statement — get −40 °C in writing or reserve the Würth 760390014.

## 13. v1.1 buck, latch re-scale and v1.1 review items — SUPERSEDED by v1.2

The v1.1 +5V trunk (LM5146-Q1 sync controller, 200 kHz / 68 µH, Q103-Q105, R129-R139, C130-C138, R138 shunt, fitted snubber), the re-scaled PWR_EN latch (R109 56 k, C111 10 µF, R110 / R111 240 k, R136, R123 / R124 10 k) and their calculations, firmware rules (AFE_ALERT latched / ≥ 30 ms, ≈ 1.3 s shutdown) and bring-up gates B1-B7, B10, B11 are **superseded** and not part of v1.2. Full text, csv files and the RGY0020B footprint are archived in git commit `ca3a7a3`; the LM5146 design stays the owner's fallback.

Disposition of the v1.1 review (`docs/reviews/v11_power_tree_review.md`) items in v1.2:

| ID | v1.2 status |
|---|---|
| V11-01, -02, -03, -06, -07, -08, -13 | n/a (LM5146 power stage removed). V11-13 (back-feed) does not apply to the non-sync LM5013 (no reverse current) |
| V11-04 | replaced by the v1.0-latch wake rule in §14.3 (F-09) |
| V11-05 | n/a: v1.0 latch restored exactly (R123 / R124 100 k, R2-05 analysis against the LM5013 0.45 V shutdown-falling threshold, §5 A2 / §11) |
| V11-09 | **kept**: C127 = 10 µF 25 V 1206 (C70462) |
| V11-10 | **kept** for the new mix (§1 PWR_FLAG list) |
| V11-11 | range text kept, R105 10.7 k **not** applied (v1.0 buck restored exactly): +5V_ISO 4.90-5.05 V (§12.1) |
| V11-12 | kept as owner question (§12.4) |
| V11-14 | **kept**: rule area in the T101 footprint (F-06 confirmed) |
| N-05, N-11 | kept (T101 body question not applicable; TLV767 COUT ESR 2-500 mΩ) |

## 14. v1.2 changes (owner decision 2026-11-25, PROJECT.md §5 row "v1.2")

### 14.1 Why

An independent v1.0-vs-v1.1 comparison found: LM5013-Q1 stock only 213 pcs (the original v1.0 risk), but the LM5146-Q1 solution costs ≈ +$5.6 / board and +17 parts, raises standby by ≈ +3 mA (≈ +6 mA after the review fixes) and needs the re-scaled latch with its typ-only 0.37 V shutdown band and a long wake pulse. The owner chose the **hybrid**: v1.0 +5V trunk and latch with the **commercial LM5013DDAR** (stock 6 940), and the v1.1 isolated supply (which fixed the B0505S creepage defect and the dummy load) with the AEC-Q100 **SN6505B-Q1**.

### 14.2 Ref changes vs v1.1 (111 refs as issued, 114 after the review → v1.2 95 refs)

| Kind | Refs |
|---|---|
| **Removed** (v1.1 LM5146-only) | Q103, Q104, Q105, R129, R130, R131, R132, R133, R134, R135, R136, R137, R138, R139, C130, C131, C132, C133, C134, C135, C136, C137, C138 (23 refs) |
| **Restored from v1.0** (exact v1.0 rows / nets) | D104 SS520, C105, C106, R107 (type-3 ripple), and the v1.0 values of U101 block and latch: L101 22 µH, R104 39 k, R105 150 k, R106 47 k, C107 2.2 nF, R109 1 M, C111 1 µF, R110 / R111 2 M, R123 / R124 100 k, R103 / R127 description (2 × 33 k), D103 / D105 / R108 / R125 / R126 / C101 / TP102 / TP107 / TP111 v1.0 texts |
| **Changed** | U101 LM5013QDDARQ1 → **LM5013DDAR** (C5383001, commercial; same DDA pinout, footprint `TI_SO-PowerPAD-8_ThermalVias`, project symbol `LM5013-Q1_DDA`); U106 SN6505BDBVR → **SN6505BQDBVRQ1** (C1849490) |
| **Kept from v1.1** (iso chain) | U105, C125, C126, U106, C127 (10 µF), C128, C129, C139, C140, T101, D110, D111, U107, TP106, TP108, TP115 |
| Net changes vs v1.1 | the `01_U101_*` nets return to v1.0 (`01_U101_SW / BST / FB / RON / RC`); `01_U101_RT / SS / COMP / RC1 / RC2 / SYNC / ILIM / LO / HO / VCC / VIN / SNB / RS`, `01_Q103_G`, `01_Q104_G`, `01_Q105_G` removed; iso nets `01_ISO_VIN / D1 / D2 / S1 / S2 / RECT` unchanged. Global interface nets = v1.0 (netlist check) |
| Symbols / footprints | `LM5013-Q1_DDA` back (Source updated to cite SNVSCB3 p.4); `LM5146-Q1_RGY` removed; `TI_RGY0020B_…` footprint file (archived on commit `ca3a7a3`) |

### 14.3 Commercial LM5013DDAR check and the restored latch (F-09)

* **LM5013DDAR (DS SNVSCB3, Oct 2022):** same 8-pin SO PowerPAD DDA, pins 1 GND, 2 VIN, 3 EN/UVLO, 4 RON, 5 FB, 6 PGOOD, 7 BST, 8 SW, EP no internal connection (p.4) = LM5013-Q1; VIN / SW / EN abs max 100 V (p.5); operating TJ −40…+150 °C (p.5-6; the p.1 feature list says −40…+125 °C TJ — use 125 °C as the design limit; at 1.00 A ≈ 0.82 W (buck loss calc, est.) × 34.8 °C/W (p.6) → Tj ≈ 114 °C at 85 °C ambient, inside); IQ shutdown 3.1 / 9.9 µA, standby 25 / 40 µA; EN rising 1.43-1.6 V, falling 1.35-1.47 V, shutdown falling 0.45 V; VREF 1.181-1.218 V; CBST 1.5-2.5 nF (p.5-6) — identical to the values the v1.0 sheet was designed with, so every v1.0 value stays. Differences: not AEC-Q100 (owner-accepted), HBM ±1 kV / CDM ±750 V (p.5, handle as ESD-sensitive). Live 2026-11-25: LCSC 6 940 / JLC 6 940, Extended, $0.975 @100 (JLC API).
* **Wake pulse with the v1.0 latch (F-09; the v1.1 "≥ 10 ms / ≥ 30 ms" rules are void):** C111 1 µF charges from AFE_REG1 through R125 / R126 1 k: **τ ≈ 1.0 ms** (1 k ∥ 1 M × 1 µF), 2.7 V final. EN reaches 1.6 V (max rising) after **0.9 ms**. Hold after release = 1 s × ln(V0 / VEN-falling): from 2.7 V **0.66 s typ**, 0.46 s worst (1.47 V, C111 −25 %). Needed: ≥ 300 ms TPS3828-33 reset delay max + ≈ 30 ms rail-up / boot = 0.33 s → V0 ≥ 2.28 V worst → **pulse ≥ 1.4 ms worst (1.3 ms nominal)**. Firmware rule: **AFE_ALERT latched until the MCU clears it (preferred), or low ≥ 2 ms** (2 ms → 2.33 V nom / 2.51 V with C −25 % → hold 0.51 s nom / 0.40 s worst); assert `PWR_HOLD` as the first GPIO action after reset. Gate B2 (v1.2): wake with the minimum configured ALERT pulse at −40 °C; PWR_HOLD high before PWR_EN falls below 1.47 V.
* +5V peak with the iso chain ≈ 1.00 A (calc: 962 − 357 + 396 mA) = 29 % of the LM5013's 3.5 A.

### 14.4 New bring-up gate

| # | Gate | Pass criterion |
|---|---|---|
| B12 | **EMC pre-scan of the +5V LM5013 buck** (COT, variable frequency ≈ 321 kHz at load, DCM / lower frequency at light load): conducted emissions on VSUP_TAP / AUX with a LISN, and near-field H-probe over L101 / D104 / SW node, at 0.07 A, 0.16 A and 1 A, VSUP 51.2 V and 58.4 V | pre-scan against the project's CISPR 25 target (class and margin to be set by the owner; none is fixed in ARCHITECTURE yet), result recorded; if it fails: input π-filter on VSUP, RC snubber across D104, slower layout loop — record before the board order |
| B2 | Wake pulse (v1.2 latch) | see §14.3 |
| B8 / B9 | iso chain | see §12.4 |

### 14.5 Owner-accepted trade-offs (v1.2)

Commercial-grade U101 (no AEC-Q100, ESD HBM ±1 kV) in exchange for stock and cost; the v1.0 variable-frequency COT buck EMC is unproven (gate B12); the LM5146-Q1 design stays archived as the fallback (git commit `ca3a7a3`).
