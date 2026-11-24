# Sheet 01 — Power Supply (control board, refs 1xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 01). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 90 refs = 88 fitted (of which 5 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 2 DNP; 46 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

Breakdown: 83 BOM parts fitted + 2 DNP (C123, C124) + 5 THT probe pads (TP109, TP110, TP111, TP113, TP114; not in the BOM, no LCSC).

## 1. Blocks (dashed boxes), placement left → right

| # | Box title | Refs | Placement / flow |
|---|---|---|---|
| 1 | Supply input (VSUP_TAP / AUX) | R101 R102 D101 D103 C101-C103 J101 F101 D102 R103 R127 TP101 TP107 TP109 TP110 | far left. Top row: `VSUP_TAP` (hier. input from J206 pin 1, sheet 02) → R101 → R102 → `VSUP_F` → D101 → `VSUP`. Bottom row: J101 → F101 → `AUX_IN` → D102 → `VSUP`. D103 + C101-C103 on the `VSUP` node right of the OR |
| 2 | +5V trunk (U101 LM5013-Q1) | U101 R104-R108 C105-C110 D104 L101 TP102 TP111 | centre top; `VSUP` in left, `+5V` power symbol out right |
| 3 | +12V switched leaf (U102 LM5163-Q1) | C104 U102 R113-R116 C112-C116 L102 TP104 | centre bottom, fed from `VSUP`; `EN_12V` hier. input |
| 4 | +3V3 / +3V3_A (U103) | U103 C117-C120 FB101 TP103 | right of box 2, from `+5V` |
| 5 | +3V3_ESP (U104) | U104 C121-C124 L103 R118 R119 TP105 | right, from `+5V`; `EN_ESP` hier. input |
| 6 | +5V_ISO (U105 + U106) | U105 C125-C129 U106 R122 R128 TP106 TP108 | far right; barrier drawn as a vertical dashed line through U106, `GND_ISO` side right |
| 7 | Power latch (PWR_EN) | Q101 Q102 D105-D108 R109-R112 R123-R126 C111 TP113 TP114 | below box 1/2, `PWR_EN` wire into U101 pin 3 |
| 8 | VBAT_MCU OR | D109 | bottom right; `VBAT_MCU` hier. output |

Hierarchical labels: inputs `VSUP_TAP`, `PWR_HOLD`, `WAKE_BTN_N`, `AFE_ALERT`, `EN_12V`, `EN_ESP`, `EN_ISO`; outputs `PG_5V`, `VBAT_MCU`. Power symbols: `+12V +5V +3V3 +3V3_A +3V3_ESP +5V_ISO GND_PWR GND_ISO AFE_REG1`. PWR_FLAG: `VSUP` (driven by diodes only), `+3V3_A` (fed through a bead), `+5V_ISO`/`GND_ISO` (module output), and `AFE_REG1`/`GND_PWR` only if the sheet-02 owner does not flag them. `VSUP`, `VSUP_F`, `AUX_IN`, `FORCE_ON`, `PWR_EN` are names from ARCHITECTURE §10 and stay sheet-local labels here.

## 2. Key number per block (on-sheet note)

| Box | Note | Calc / source |
|---|---|---|
| 1 | "R_DAMP 4.4 Ω: hot-plug 13 A pk, I²t 0.0034 A²s vs F701 0.53 A²s; TVS ≈ 79 V @25 °C < 100 V" | 58.4/4.4 Ω; V²C/2R with 8.8 µF; (96.8−70)/(4.4+1.49) ≈ 3.8 A → ≈ 79 V (review R2-15 calc, est.) |
| 2 | "+5V: 321 kHz, 5.03 V, peak load 0.96 A = 27 % of 3.5 A" | 5×2500/39k (DS p.12); 1.2×(1+150/47) (DS p.5); ARCH §4.2 |
| 3 | "+12V: 305 kHz, 12.2 V, 0.15 A of ≈0.47 A" | 12.2×2500/100k; 1.2×(1+220/24); ARCH §4.2 |
| 4 | "U103 0.40 W @ 233 mA → Tj 111 °C @ 85 °C" | (5−3.3)×0.233 × 63.9 °C/W (TPS7B82 DS p.6) |
| 5 | "COUT 22 µF + 10 µF at the module (C123 DNP); VOUT 3.33 V" | TLV62569 DS p.9 Table 4; 0.6×(1+100/22) |
| 6 | "CT 330 pF → 1.06 ms ramp; 150 Ω dummy load 33 mA fitted (module min 40 mA)" | SR = 0.55×330+30 µs/V (TPS22918 DS p.14) |
| 7 | "PWR_EN hold 0.66 s; off < 0.45 V (shutdown falling); ≤ 19.5 V via FORCE_ON / AUX" | 1 MΩ×1 µF×ln(2.7/1.4); LM5013-Q1 DS p.5; 58.4×1M/3M |
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
| TP106 / TP108 | +5V_ISO / GND_ISO | red / black hook | isolated module output (min-load check) |
| TP113 / TP114 | FORCE_ON / PWR_EN | THT pads | EOL pogo short |

Removed vs bom_G1: TP112 (+3V3_A pad) — no pad after a bead (instruction §5.5); `+3V3_A` is measured at TP402 (sheet 04). Unused refs (traceability to bom_G1): R117, R120, R121, TP112.

## 4. DNP list

| Ref | Why | Fit only if |
|---|---|---|
| C124 6.8 pF | U104 feed-forward | load-step response of +3V3_ESP needs it |
| C123 22 µF | 2nd +3V3_ESP output cap | a load-step test needs it (review R2-16) |

## 5. AGENT DECISIONS (owner may overrule)

bom_G1 §6 questions 1-11 (owner delegated, 2026-11-23), along the file's recommendations:

| Q | Question | Choice | Why / source |
|---|---|---|---|
| 1 | F_SUP location | F701 at the B+ lug on the power board, `VSUP_TAP` on B2B pin 1 (sheet 07) | P-02 (owner-accepted); contract pin map |
| 2 | 250 V MLCCs | 2.2 µF 250 V 2220 (C153032) on every 58 V node: C101-C104 here | P-01 (owner-accepted), 2× rule |
| 3 | PDSG/PCHG blocking diodes | fitted (sheet 07 D711/D712) | P-03 |
| 4 | R_PRE / R_PCHG sourcing | sheet 07 | — |
| 5 | Shunt | owner chose C558625; sheet 04 | — |
| 6 | M6 torque | sheet 07 | — |
| 7 | Non-AEC TPS22918DBVR / TLV62569DBVR | **accept** both (the -Q1 TPS22918 has ~114 pcs; no AEC buck at the price) | bom_G1 §5 item 9; recommendation |
| 8 | R_LD / R_PACK | on the power board (sheet 07 R751/R752) | contract |
| 9 | Numbering | heater 7xx on sheet 07; shunt + NTC_SHUNT → sheet 04; male J_B2B = J206 on sheet 02 | owner 2026-11-23 two-project decision + contract |
| 10 | TPS22918 ramp | **C126 = 330 pF C0G (C1664, Basic)** → 1.06 ms | B §5.1 asks ≈ 1 ms because the module is "hot plug: not supported"; 100 pF gave 0.43 ms |
| 11 | Stack height 11 mm | sheet 07 | — |

Further decisions taken in this spec:

| # | Question | Choice | Why |
|---|---|---|---|
| A1 | J_AUX connector not -40 °C (KF301 C474881 is -30..+120 °C, LCSC API) — P-13 | **Kangnex WJ500V-5.08-2P (C8465)**, -40..+105 °C, UL 300 V / 10 A, 5.08 mm, stock 263 k; footprint stock Phoenix MKDS-1,5-2-5.08 | P-13; WJ500V drawing p.1; same part for J710 on sheet 07 |
| A2 | R_AUXB value | **2 × 33 kΩ 1206 in parallel (R103 + R127, C18004)** = 16.5 kΩ (superseded 47 k after review R2-05) | ES2D IR 100 µA max at 100 °C (DS p.1); board off needs PWR_EN < 0.45 V (shutdown **falling**, LM5013-Q1 DS p.5) → AUX_IN < 1.65 V → 100 µA tolerated; 102 mW each at 58 V = 41 % |
| A3 | EN_ISO / EN_ESP / EN_12V pull-downs | **not placed here** (bom_G1 R117/R120/R121 dropped) | bom_G3 R825-R828 place one per net at the expander U801/U802 ("keep one per net", instruction §8). Confirmed at integration 2026-11-23: sheet 08 adds them; none on sheet 01 |
| A4 | WAKE_BTN_N 1 MΩ pull-up to AFE_REG1 | not here; sheet 08 R824 owns it | bom_G3 ownership table |
| A5 | AFE_ALERT 10 k pull-up to AFE_REG1 | not here; sheet 02 R261 owns it | bom_G2 |
| A6 | VBAT_MCU OR | **D109 on sheet 01** (sheet scope) | Coordination: bom_G3 lists the same BAT54C as D301 on sheet 03 — sheet 03 must drop D301 (and R301/C311 stay there, fed from `VBAT_MCU`) |
| A7 | U102 PGOOD | NC (open drain unused) | no MCU pin for +12V status in ARCH §8 |
| A8 | U103 EN | tied to IN (+5V) | VEN ≤ VIN allowed (TPS7B82 DS p.4); B §7 item 2 |
| A9 | U105 QOD | tied to VOUT (internal RPD discharge) | TPS22918 DS p.3; bom_G1 |
| A10 | Symbols | project symbols LM5013-Q1_DDA, LM5163-Q1_DDA (pin-identical copies of stock `LM5164DDA`), TPS7B8233-Q1_DGN, TPS22918_DBV, B0505S-2WR3; stock TLV62569DBV, AO3401A, 1N4148WS, BAT54C, 1.5SMCxxA (SMCJ60A: pin 1 = bar = cathode, pin 2 = anode, from the symbol graphics) | names must match the part; pins checked vs DS and footprint pads by script |

## 6. New interface signals

None. Every cross-sheet name used here is in ARCHITECTURE §10 or the interface contract (`VSUP_TAP`); confirmed by the netlist self-check.

## 7. B2B change requests

None. (VSUP_TAP on pin 1 is consumed here unchanged.)

## 8. Verification record (live, 2026-11-23)

Every LCSC number on this sheet was re-read live on 2026-11-23 from the **LCSC product API** (`wmsc.lcsc.com/ftps/wm/product/detail?productCode=…`: MPN, brand, package, stock, operating temperature) **and** the **JLCPCB parts API** (`selectSmtComponentList`: JLC stock, Basic/Extended). All MPN + manufacturer match. New numbers this session: C8465 (WJ500V), C1664 (330 pF C0G, Basic, JLC 773 k), C17713 reused for R103. Datasheets downloaded 2026-11-23 (TI parts from ti.com; others from the LCSC datasheet link); drawing-only pages were read as rendered images (AO3401A).

Pin sources: LM5013-Q1 DS p.3 (EP no internal connection → GND); LM5163-Q1 DS p.3; TPS7B82-Q1 DS p.3 (DGN: 1 IN, 2 EN, 3/7 NC, 4-6 GND, 8 OUT, PAD); TLV62569 DS p.3 (= stock symbol); TPS22918 DS p.3; B0505S-2WR3 DS p.5 (1 Vin, 2 GND, 4 0V, 6 +Vo — corrected by review R2-01; KiCad Murata NMA footprint pads 1,2,4,5,6 at the same 2.54 grid, pad 5 → NC); AO3401A DS p.1 image (1 G, 2 S, 3 D); BAT54C DS p.1 (1 A1, 2 A2, 3 K). Footprint pad sets = symbol pins for every ref (netlist self-check).

Low stock (stock < 10 × need for 100 boards): **U101 LM5013QDDARQ1 C5219285: JLC 250 / LCSC 250** (was 2 460 on 11-17) — order / reserve now; **C153032 2.2 µF 250 V: JLC 6 379 / LCSC 2 644 vs 1 000 needed (10 per board over both boards)**; **D103 SMCJ60A C2996503 2 624** (second source TWGMC C4154628, 2 713, live).

## 9. Unverified / open technical items

1. R101/R102 sub-ms pulse rating (0.53 J per part at F701 opening) — no single-pulse curve in the HoLRT DS; bench check (carried from bom_G1).
2. DC-bias derating of C153032 (250 V 2220) and C2918511 (25 V 1210 at 12.2 V) — curves not read (est.).
3. B0505S-2WR3 below 40 mA minimum load → +5V_ISO may exceed 5.5 V; R122 DNP until measured.
4. ES2D reverse leakage at 58 V / 85 °C is not specified (only 25 °C / 100 °C at rated 200 V); R103 sized on the 100 °C max.
5. FB101 + C120 (1 µF) resonance not computed (bead inductance not in the listing); the LDO output has no 300 kHz content, so low risk.
6. WJ500V drawing asks for Ø1.5 mm holes; stock Phoenix footprint has Ø1.3 mm (pin 0.9 × 0.8 mm, diagonal 1.20 mm, calc). OK for assembly, tight; layout may enlarge to 1.5 mm.

## 10. Owner questions that remain

1. LM5013-Q1 stock (250 pcs): reserve now, or accept the LM5164-Q1 fallback (1 A, 96 % at peak — not recommended)?
2. ~~Confirm sheet 03 drops D301~~ — done: the VBAT_MCU OR is D109 here; sheet 03 has no D301. (EN_* pull-downs: confirmed on sheet 08.)

## 11. Review disposition (2026-11-23, accepted items)

| ID | Disposition | Refs changed / evidence |
|---|---|---|
| R2-01 BLOCKER | fixed | U106 pin 1 = Vin (`01_ISO_VIN`), pin 2 = GND (`GND_PWR`); the project symbol library (`symbols/Automotive_ESS_BMS.kicad_sym`) corrected. Re-read: EVISUN B0505S DS p.5 pin table (1 Vin, 2 GND, 4 0V, 5 no pin, 6 +Vo) and Fig 3 (read from the rendered image). **Bring-up gate: confirm pins 1 and 2 on a physical sample (diode check, or a 50 mA current-limited supply) before the board order** |
| R2-05 | fixed | New R123 / R124 100 k drain pull-downs and R125 / R126 1 k drain series resistors; the D106 / D107 anodes are now on `01_QBTN_R` / `01_QALRT_R`. R103 → 33 k 1206, plus new R127 33 k 1206 in parallel (C18004). The notes now say the board shuts down below **0.45 V falling** (LM5013-Q1 DS p.5) |
| R2-14 | noted (doc) | The Sleep budget text lives in ARCH §4.3 (updated for schematic v1). With the output off (D-01) the AFE_FLT lines are low, so they draw 0 µA |
| R2-15 | fixed | R101 / R102 1 Ω HoLRT → 2.2 Ω 2 W 2512 Yageo RC2512FK-7W2R2L (C876260); the HoLRT family has no 2.2 Ω at LCSC. TVS current ≈ 3.8 A → clamp ≈ 79 V at 25 °C (calc); 2 V drop at 0.46 A; F701 still melts at 13 A (6.5× its rating) |
| R2-16 | fixed | C123 → DNP: 22 µF + 10 µF module cap is inside the TLV62569 matrix (DS p.9 Table 4) |
| R2-20, R2-21, R2-23, R2-24, R2-25 | noted, no change | — |
| R2-22 | bring-up note | In AUX-only bench mode, SS320 leakage (≤ 10 mA at 100 °C, SS320 DS p.2) back-energises VSUP_TAP / BAT+ on the power board. Treat BAT+ as live |
| R2-32 | noted | D-09 still open |
| R3-02 | fixed | R122 330 Ω DNP → 300 Ω 1206 fitted, plus new R128 300 Ω 1206 (C17887, Basic) = 150 Ω / 33 mA. **Bring-up gate:** record +5V_ISO at idle and at −40 °C; it must be ≤ 5.5 V (CA-IS305x / 308x VCC2 max) |
| R2-02 … R2-13, R2-17, R2-18 | n/a | Sheet 02 / 08 items. R2-17 is already a layout gate (sheet 07 design note §8) |

**New LCSC numbers on this sheet.** All live-verified 2026-11-23 on the LCSC product API and the JLCPCB parts API.

| LCSC | Part | Stock (LCSC / JLC) | Class |
|---|---|---|---|
| C876260 | RC2512FK-7W2R2L | 5 285 / 6 251 | Extended |
| C18004 | 1206W4F3302T5E | 125 400 / 167 078 | Extended |
| C17887 | 1206W4F3000T5E | – | Basic |
| C21190 | 0603WAF1001T5E | – | Basic |

Unverified: the thick-film 2512 single-pulse rating for the 1.2 J fault pulse (no curve published).
