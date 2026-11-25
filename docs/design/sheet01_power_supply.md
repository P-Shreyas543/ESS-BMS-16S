# Sheet 01 — Power Supply (control board, refs 1xx) — design note (v1.1)

Schematic v1.1, 2026-11-25 (sheet revision v1.1, A2). Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 01). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md), [v1.1 power-tree review](../reviews/v11_power_tree_review.md).

**v1.1 (owner decisions 2026-11-24 / 2026-11-25, `PROJECT.md` §5):** the +5V trunk is an LM5146-Q1 synchronous buck controller (200 kHz forced PWM, external FETs, shunt current limit) instead of the LM5013-Q1, and `+5V_ISO` comes from an SN6505B push-pull driver + LT31-113 transformer + TLV76750 LDO instead of the B0505S-2WR3 module and its dummy load. Details in §12, review disposition in §13.

**Count:** 114 refs = 112 fitted (of which 6 copper-only, not in the BOM: test pads) + 2 DNP; 65 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings, V11-xx / N-xx = v1.1 review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

Breakdown: 106 BOM parts fitted + 2 DNP (C123, C124) + 6 THT probe pads (TP109, TP110, TP111, TP113, TP114, TP115; not in the BOM, no LCSC).

## 1. Blocks (dashed boxes), placement left → right

| # | Box title | Refs | Placement / flow |
|---|---|---|---|
| 1 | Supply input (VSUP_TAP / AUX) | R101 R102 D101 D103 C101-C103 J101 F101 D102 R103 R127 R136 TP101 TP107 TP109 TP110 | far left. Top row: `VSUP_TAP` (hier. input from J206 pin 1, sheet 02) → R101 → R102 → `VSUP_F` → D101 → `VSUP`. Bottom row: J101 → F101 → `AUX_IN` → D102 → `VSUP`. D103 + C101-C103 on the `VSUP` node right of the OR; R103 / R127 / R136 bleeders on `AUX_IN` |
| 2 | +5V trunk (U101 LM5146-Q1) | U101 Q103 Q104 Q105 L101 R104-R106 R108 R129-R135 R137-R139 C107-C110 C130-C138 TP102 TP111 | centre top; `VSUP` in left (R137/C136 to VIN, C137 at the Q103 drain), power stage Q103 / Q104 // Q105 / R138 shunt / L101 top, snubber R135/C138 across Q104/Q105, compensation R129/R130/C130-C132 and RT/SS/ILIM parts below U101, `+5V` power symbol out right |
| 3 | +12V switched leaf (U102 LM5163-Q1) | C104 U102 R113-R116 C112-C116 L102 TP104 | centre bottom, fed from `VSUP`; `EN_12V` hier. input |
| 4 | +3V3 / +3V3_A (U103) | U103 C117-C120 FB101 TP103 | right of box 2, from `+5V` |
| 5 | +3V3_ESP (U104) | U104 C121-C124 L103 R118 R119 TP105 | right, from `+5V`; `EN_ESP` hier. input |
| 6 | +5V_ISO (U105 TPS22918 + U106 SN6505B + U107 TLV76750) | U105 C125 C126 U106 C127 C139 T101 D110 D111 C128 C140 U107 C129 TP106 TP108 TP115 | far right: `+5V` → U105 → `01_ISO_VIN` → U106 → T101; barrier drawn as a vertical dashed line through T101 (primary pins 1-2-3 left, secondary 6-5-4 right); D110/D111 → `01_ISO_RECT` → U107 → `+5V_ISO`, `GND_ISO` side right |
| 7 | Power latch (PWR_EN) | Q101 Q102 D105-D108 R109-R112 R123-R126 C111 TP113 TP114 | below box 1/2, `PWR_EN` wire into U101 pin 1 (EN/UVLO) |
| 8 | VBAT_MCU OR | D109 | bottom right; `VBAT_MCU` hier. output |

Hierarchical labels: inputs `VSUP_TAP`, `PWR_HOLD`, `WAKE_BTN_N`, `AFE_ALERT`, `EN_12V`, `EN_ESP`, `EN_ISO`; outputs `PG_5V`, `VBAT_MCU`. Power symbols: `+12V +5V +3V3 +3V3_A +3V3_ESP +5V_ISO GND_PWR GND_ISO AFE_REG1`. PWR_FLAG (review V11-10, ERC): **`VSUP`** (driven by diodes only), **`+3V3_A`** (fed through a bead), **`GND_ISO`** (no source pin), **`01_U101_VIN`** (U101 VIN power_in behind R137), **`01_ISO_RECT`** (U107 IN power_in behind D110 / D111); **none on `+5V_ISO`** (driven by the U107 OUT power_out pin); `AFE_REG1` / `GND_PWR` only if the sheet-02 owner does not flag them. `VSUP`, `VSUP_F`, `AUX_IN`, `FORCE_ON`, `PWR_EN` are names from ARCHITECTURE §10 and stay sheet-local labels here. The interface (global) net set is unchanged by v1.1 (self-check).

## 2. Key number per block (on-sheet note)

| Box | Note | Calc / source |
|---|---|---|
| 1 | "R_DAMP 4.4 Ω: hot-plug 13 A pk, I²t 0.0034 A²s vs F701 0.53 A²s; TVS ≈ 79 V @25 °C < 100 V" | 58.4/4.4 Ω; V²C/2R with 8.8 µF; (96.8−70)/(4.4+1.49) ≈ 3.8 A → ≈ 79 V (review R2-15 calc, est.); 100 V = LM5146-Q1 VIN/SW abs max (DS p.6) and Q103/Q104 VDS |
| 2 | "+5V: 200 kHz FPWM, 5.08 V, ΔIL 0.34 A, shunt ILIM valley 1.29-1.76 A, fc 20 kHz / PM 60°; peak 0.96-1.00 A, η ≈ 81 %" | 1e4/49.9 k (DS p.20 Eq.3); 0.8×(1+10.7/2.00) (p.8); IRS × RILIM / RS (p.9, p.23); §12.2 / §13 |
| 3 | "+12V: 305 kHz, 12.2 V, 0.15 A of ≈0.47 A" | 12.2×2500/100k; 1.2×(1+220/24); ARCH §4.2 |
| 4 | "U103 0.40 W @ 233 mA → Tj 111 °C @ 85 °C" | (5−3.3)×0.233 × 63.9 °C/W (TPS7B82 DS p.6) |
| 5 | "COUT 22 µF + 10 µF at the module (C123 DNP); VOUT 3.33 V" | TLV62569 DS p.9 Table 4; 0.6×(1+100/22) |
| 6 | "SN6505B 424 kHz → T101 1:1.3 → 2 × MBR0520L → TLV76750 5.0 V; 2.5 kV barrier; +5V_ISO 4.94-5.05 V; 300 mA = 0.40 A from +5V" | v1.1 iso study calc rescaled to +5V 4.95-5.22 V (§12.3); CT 330 pF → 1.06 ms (TPS22918 DS p.14) |
| 7 | "PWR_EN hold 0.68 s; release: 11 µA × 56 k = 0.62 V < 1.164 V; off < 0.37 V (typ); ≤ 11.5 V; AUX on ≈ 7.1 V / off ≈ 4.4 V; ALERT latched or ≥ 30 ms" | 56 k × 10 µF × ln((2.7−0.56)/(1.2−0.56)); LM5146-Q1 DS p.8/p.25; §12.4, review N-08 |
| 8 | "VBAT_MCU = max(+3V3, AFE_REG1) − 0.3 V" | BAT54C |

## 3. Test points

| TP | Net | Type | Proves |
|---|---|---|---|
| TP101 | VSUP | red hook | input OR + TVS node |
| TP107 | GND_PWR | black hook | probe ground, control-board power area (at U101 / Q104 source) |
| TP109 | VSUP_F | THT pad | F701 + R_DAMP path (compare with TP101 → D101 drop) |
| TP110 | AUX_IN | THT pad | F101 + AUX presence |
| TP102 | +5V | red hook | U101 output |
| TP111 | PG_5V | THT pad | U101 PGOOD |
| TP104 | +12V | red hook | U102 output |
| TP103 | +3V3 | red hook | U103 output |
| TP105 | +3V3_ESP | red hook | U104 output |
| TP106 / TP108 | +5V_ISO / GND_ISO | red / black hook | U107 output (isolated side) |
| TP115 | 01_ISO_RECT | THT pad (v1.1) | rectifier output = U107 headroom (≥ 5.4 V at 300 mA) |
| TP113 / TP114 | FORCE_ON / PWR_EN | THT pads | EOL pogo short |

The SW node (`01_U101_SW`) gets no probe point (high-voltage switching node); probe it at the Q104 drain with a spring-tip ground at TP107 during bring-up.

Removed vs bom_G1: TP112 (+3V3_A pad) — no pad after a bead (instruction §5.5); `+3V3_A` is measured at TP402 (sheet 04). Unused refs (traceability to bom_G1): R117, R120, R121, TP112. **Retired in v1.1 (not re-used, traceability to v1.0):** D104, C105, C106, R107, R122, R128.

## 4. DNP list

| Ref | Why | Fit only if |
|---|---|---|
| C124 6.8 pF | U104 feed-forward | load-step response of +3V3_ESP needs it |
| C123 22 µF | 2nd +3V3_ESP output cap | a load-step test needs it (review R2-16) |
| ~~R135 / C138 snubber~~ | fitted since the v1.1 review (V11-03) | — |

## 5. AGENT DECISIONS (owner may overrule)

bom_G1 §6 questions 1-11 (owner delegated, 2026-11-23), along the file's recommendations:

| Q | Question | Choice | Why / source |
|---|---|---|---|
| 1 | F_SUP location | F701 at the B+ lug on the power board, `VSUP_TAP` on B2B pin 1 (sheet 07) | P-02 (owner-accepted); contract pin map |
| 2 | 250 V MLCCs | 2.2 µF 250 V 2220 (C153032) on every 58 V node: C101-C104 here; v1.1 adds 100 nF 250 V 1206 (C136, C137), 4.7 pF 250 V (C134) and 100 pF 250 V (C138 DNP) on VSUP / SW-swinging nodes | P-01 (owner-accepted), 2× rule |
| 3 | PDSG/PCHG blocking diodes | fitted (sheet 07 D711/D712) | P-03 |
| 4 | R_PRE / R_PCHG sourcing | sheet 07 | — |
| 5 | Shunt | owner chose C558625; sheet 04 | — |
| 6 | M6 torque | sheet 07 | — |
| 7 | Non-AEC TPS22918DBVR / TLV62569DBVR | **accept** both (the -Q1 TPS22918 has ~114 pcs; no AEC buck at the price). v1.1 adds non-AEC SN6505BDBVR and TLV76750DRVR (SN6505B-Q1 +$2.18 left as owner option) | bom_G1 §5 item 9; recommendation; v1.1 iso study |
| 8 | R_LD / R_PACK | on the power board (sheet 07 R751/R752) | contract |
| 9 | Numbering | heater 7xx on sheet 07; shunt + NTC_SHUNT → sheet 04; male J_B2B = J206 on sheet 02 | owner 2026-11-23 two-project decision + contract |
| 10 | TPS22918 ramp | **C126 = 330 pF C0G (C1664, Basic)** → 1.06 ms | kept in v1.1: limits the inrush into C127 + C139 to 23 mA (calc) before the SN6505B soft-start |
| 11 | Stack height 11 mm | sheet 07 | — |

Further decisions taken in this spec:

| # | Question | Choice | Why |
|---|---|---|---|
| A1 | J_AUX connector not -40 °C (KF301 C474881 is -30..+120 °C, LCSC API) — P-13 | **Kangnex WJ500V-5.08-2P (C8465)**, -40..+105 °C, UL 300 V / 10 A, 5.08 mm, stock 263 k; footprint stock Phoenix MKDS-1,5-2-5.08 | P-13; WJ500V drawing p.1; same part for J710 on sheet 07 |
| A2 | R_AUXB value | **3 × 33 kΩ 1206 in parallel (R103 + R127 + R136, C18004)** = 11 kΩ (v1.0: 2 × 33 k after review R2-05; v1.1 adds R136) | ES2D IR 100 µA max at 100 °C (DS p.1) → AUX_IN ≤ 1.1 V → PWR_EN ≤ 0.21 V through R110/R109, below the LM5146-Q1 0.37 V shutdown-falling typ (DS p.25, no min/max); 103 mW each at 58.4 V = 41 % |
| A3 | EN_ISO / EN_ESP / EN_12V pull-downs | **not placed here** (bom_G1 R117/R120/R121 dropped) | bom_G3 R825-R828 place one per net at the expander U801/U802 ("keep one per net", instruction §8). Confirmed at integration 2026-11-23: sheet 08 adds them; none on sheet 01 |
| A4 | WAKE_BTN_N 1 MΩ pull-up to AFE_REG1 | not here; sheet 08 R824 owns it | bom_G3 ownership table |
| A5 | AFE_ALERT 10 k pull-up to AFE_REG1 | not here; sheet 02 R261 owns it | bom_G2 |
| A6 | VBAT_MCU OR | **D109 on sheet 01** (sheet scope) | Coordination: bom_G3 lists the same BAT54C as D301 on sheet 03 — sheet 03 must drop D301 (and R301/C311 stay there, fed from `VBAT_MCU`) |
| A7 | U102 PGOOD | NC (open drain unused) | no MCU pin for +12V status in ARCH §8 |
| A8 | U103 EN | tied to IN (+5V) | VEN ≤ VIN allowed (TPS7B82 DS p.4); B §7 item 2 |
| A9 | U105 QOD | tied to VOUT (internal RPD discharge) | TPS22918 DS p.3; bom_G1 |
| A10 | Symbols | project symbols **LM5146-Q1_RGY** (v1.1), **Transformer_CT_1P_1S_LT31-113** (v1.1), LM5163-Q1_DDA (pin-identical copy of stock `LM5164DDA`), TPS7B8233-Q1_DGN, TPS22918_DBV; stock TLV62569DBV, AO3401A, 1N4148WS, BAT54C, 1.5SMCxxA (SMCJ60A: pin 1 = bar = cathode, pin 2 = anode, from the symbol graphics), v1.1 stock **Q_NMOS_GSD** (Q103), **DMN10H220L** (Q104), **SN6505BDBV** (U106), **TLV76750DRVx** (U107), D_Schottky (D110/D111). v1.0 project symbols LM5013-Q1_DDA and B0505S-2WR3 deleted from the project symbol library (no ref uses them) | names must match the part; pins checked vs DS and footprint pads by script |
| A11 (v1.1) | U101 footprint | **project footprint `TI_RGY0020B_VQFN-20-1EP_3.5x4.5mm_P0.5mm_EP1.7x2.7mm`**: KiCad stock `Texas_RGY_R-PVQFN-N20_EP2.05x3.05mm` is RGY0020A (EP 2.05 × 3.05); easyeda2kicad C1850329 gives the same 3.05 × 2.05 EP. LM5146-Q1 RGY0020B/E land is EP 1.7 × 2.7 (DS p.55-60) → copied stock, EP and pad width changed | 0.5 mm pad-to-EP gap as TI's land (stock gives 0.33 mm next to 100 V pins) |
| A12 (v1.1) | VIN pin filter | **R137 2.2 Ω + C136 100 nF 250 V** fitted | DS p.17 recommends an RC at VIN; the VSUP clamp (79 V at 25 °C, review R2-15 calc; ≈ 84-87 V hot; ≈ 91 V at the 96.8 V VC corner of SMCJ60A, est.) is close to the 100 V abs max. Review N-10 suggests 4.7-10 Ω; kept 2.2 Ω (bring-up option, footprint unchanged) |
| A13 (v1.1) | SYNCIN strap | **R132 10 k to VCC** (not a direct tie) | DS p.26 allows either; 5.0 V > 2 V VIH with the 20 k input (p.9); leaves a pad to inject an MCU clock later (owner question in the study) |
| A14 (v1.1) | Gate resistors | **R133 4.7 Ω** (HS, review V11-03), **R134 / R139 0 Ω** (LS, one per paralleled FET; never increase, V11-08) | HS edge slowed ≈ 40 % (12 Ω turn-on path vs 7.3 Ω); larger values risk overlap with the adaptive dead time, which senses the driver pins |
| A15 (v1.1) | Soft start | **C133 47 nF (Basic)** → 3.8 ms instead of the study's 39 nF (Extended) | DS p.21 Eq.4; inrush ≈ 0.1 A into ≈ 80 µF on `+5V` |
| A16 (v1.1) | ILIM | **RSENSE mode (review V11-01): R138 100 mΩ 1 % 1 W 1206 shunt (Milliohm HoLRTX, C5123673) in the Q104 / Q105 source path, R131 1.50 k from ILIM to the shunt top, PGND pin 12 to the shunt ground side** | RDS(on) sensing failed in the hot corner (DMN Fig 6 × 1.8 at 125 °C vs ILIM source × 1.29: worst valley 0.71-0.81 A < 0.83 A operating valley, review calc). Shunt mode: IRS 90-110 µA, 0 ppm/°C (DS p.9) → valley 1.29-1.76 A, no temperature term |
| A17 (v1.1) | Iso parts refs | C130/C131 of the iso study → **C139 / C140** (C130-C138 taken by the buck) | house rule: next free numbers |

## 6. New interface signals

None. Every cross-sheet name used here is in ARCHITECTURE §10 or the interface contract (`VSUP_TAP`). v1.1 adds only sheet-local nets (`01_U101_*`, `01_Q103_G`, `01_Q104_G`, `01_ISO_D1/D2/S1/S2/RECT`). Self-check confirms the global net set is identical to v1.0.

## 7. B2B change requests

None. (VSUP_TAP on pin 1 is consumed here unchanged.)

## 8. Verification record (live, 2026-11-23; v1.1 numbers 2026-11-24)

Every LCSC number on this sheet was re-read live on 2026-11-23 from the **LCSC product API** (`wmsc.lcsc.com/ftps/wm/product/detail?productCode=…`: MPN, brand, package, stock, operating temperature) **and** the **JLCPCB parts API** (`selectSmtComponentList`: JLC stock, Basic/Extended). All MPN + manufacturer match. New numbers this session: C8465 (WJ500V), C1664 (330 pF C0G, Basic, JLC 773 k), C17713 reused for R103. Datasheets downloaded 2026-11-23 (TI parts from ti.com; others from the LCSC datasheet link); drawing-only pages were read as rendered images (AO3401A). **v1.1:** all 28 new LCSC numbers and the 9 re-used ones on new / changed rows were re-read live on 2026-11-24 from both APIs (table §12.7); datasheets from the v1.1 studies.

Pin sources: LM5146-Q1 DS p.4-5 (20 pins + EP; pin 15 "EP" internally tied to the exposed pad, electrically isolated → GND); LM5163-Q1 DS p.3; TPS7B82-Q1 DS p.3 (DGN: 1 IN, 2 EN, 3/7 NC, 4-6 GND, 8 OUT, PAD); TLV62569 DS p.3 (= stock symbol); TPS22918 DS p.3; SN6505B DS p.3 (1 D1, 2 VCC, 3 D2, 4 GND, 5 EN, 6 CLK = stock `SN6505BDBV`); TLV767 DS p.3-4 (DRV fixed: 1 OUT, 2 SNS, 3/5 GND, 4 EN, 6 IN, PAD = stock `TLV76750DRVx`); LT31-113 spec p.3 / WE 760390014 DS p.1 (primary 1-2-3, CT 2; secondary 6-5-4, CT 5); SQ2398ES DS p.1 and DMN10H220LQ DS p.1 (SOT-23: 1 G, 2 S, 3 D); MBR0520L DS p.1 (cathode band = pad 1 of `D_SOD-123`); AO3401A DS p.1 image (1 G, 2 S, 3 D); BAT54C DS p.1 (1 A1, 2 A2, 3 K). Footprint pad sets = symbol pins for every ref (self-check).

Low stock (stock < 10 × need for 100 boards): **T101 LT31-113 C7471252: JLC 771, not on the LCSC API (JLC-only); alternate Würth 760390014 C2802211: JLC 0** — order / reserve now; **C153032 2.2 µF 250 V: JLC 6 379 / LCSC 2 644 vs 1 000 needed (10 per board over both boards)** (2026-11-23); **D103 SMCJ60A C2996503 2 624** (second source TWGMC C4154628, 2 713, live 2026-11-23). R137 C22939: LCSC 0, JLC 206 599 (Basic) — JLC assembly only. The v1.0 LM5013-Q1 stock problem (250 pcs) is gone with U101 → LM5146-Q1 (LCSC 8 862 / JLC 9 149).

## 9. Unverified / open technical items

1. R101/R102 sub-ms pulse rating (0.53 J per part at F701 opening) — no single-pulse curve in the HoLRT DS; bench check (carried from bom_G1).
2. DC-bias derating of C153032 (250 V 2220), C2918511 (25 V 1210 at 5 V / 12.2 V) and C106241 — curves not read; v1.1 loop and ripple use −15 % on COUT and −30 % on CIN (est.).
3. ~~B0505S-2WR3 below 40 mA minimum load~~ — removed in v1.1 (U106 B0505S replaced, no minimum load; R122/R128 gone).
4. ES2D reverse leakage at 58 V / 85 °C is not specified (only 25 °C / 100 °C at rated 200 V); R103 / R127 / R136 sized on the 100 °C max.
5. FB101 + C120 (1 µF) resonance not computed (bead inductance not in the listing); the LDO output has no switching content, so low risk.
6. WJ500V drawing asks for Ø1.5 mm holes; stock Phoenix footprint has Ø1.3 mm (pin 0.9 × 0.8 mm, diagonal 1.20 mm, calc). OK for assembly, tight; layout may enlarge to 1.5 mm.
7. (v1.1) ~~DMN10H220LQ RDS(on) at 7.5 V / TC for ILIM~~ — no longer used for current sensing (V11-01). Still est. for the loss model: 180 mΩ typ / 235 mΩ max at 7.5 V, × 1.8 at 125 °C (Fig 6 reading, review).
8. (v1.1) MOSFET switching times at 7.5 V drive (tr 8 ns, tf 6 ns), Qoss 1.5 nC and the 30 mW core loss are estimates in the loss model; Qg uses the 10 V values (conservative).
9. (v1.1) The EN/UVLO shutdown threshold 0.37 V falling is typical only (DS p.25, no min/max) — bring-up gate B1.
10. (v1.1) LT31-113 land pattern has no pin numbers (pin-1 dot top-left, spec p.2); pinout taken from the winding table p.3 and the identical Würth part. First-article check (B8).
11. (v1.1) TLV767 COUT ESR 2-500 mΩ confirmed on the rendered page (review N-11): 4.7 µF 1206 + sheet-06 10 µF through trace resistance is inside; do not add a large low-ESR bank directly at U107. Closed.

## 10. Owner questions that remain

1. ~~LM5013-Q1 stock (250 pcs)~~ — closed by v1.1 (LM5146-Q1).
2. ~~Confirm sheet 03 drops D301~~ — done: the VBAT_MCU OR is D109 here; sheet 03 has no D301. (EN_* pull-downs: confirmed on sheet 08.)
3. (v1.1, from the studies, still open) ~~T101 body 6.55 mm vs the 6.5 mm rule~~ — not applicable (review N-05: 6.55 mm is the body length along the pin rows; across the barrier the 8.02 mm pad gap counts, now protected by the footprint rule area); open: LT31-113 (JLC-only, 771) vs Würth 760390014 (AEC-Q200, 0 stock); SN6505B-Q1 (+$2.18); MCU spread-spectrum clock on SYNCIN (R132 pad) vs the fixed 200 kHz strap.

4. (v1.1 review) Standby cost of the review fixes: ≈ +6 mA pack current vs LM5013 at 70 mA (owner accepted ≈ +3 mA) and ≈ 81 % peak efficiency (accepted ≈ 84 %). Options: accept; fit the snubber only if gate B4 fails (−1.0 mA); single larger low-side FET instead of Q104 // Q105 (needs a new live-verified part, review V11-02 alternative); DCM (R132 to GND) — rejected by the owner's FPWM choice.
5. (v1.1 review V11-12) T101 LT31-113 has no operating-temperature range or AEC statement in its spec (P-13 needs −40 °C): get it in writing from Linekey / the JLC attribute page before release, or reserve the Würth 760390014 (AEC-Q200 grade 1, −40…+125 °C, 0 stock). Record in D-09 that the barrier is functional isolation (WE: "functional insulation for a working voltage of 400 Vrms"), not reinforced.

## 11. Review disposition (2026-11-23, accepted items)

| ID | Disposition | Refs changed / evidence |
|---|---|---|
| R2-01 BLOCKER | fixed in v1.0; **superseded by v1.1** (U106 B0505S-2WR3 removed, the pin-1/2 sample gate is void) | U106 pin 1 = Vin (`01_ISO_VIN`), pin 2 = GND (`GND_PWR`); the project symbol library corrected. Re-read: EVISUN B0505S DS p.5 pin table and Fig 3 |
| R2-05 | fixed; v1.1 re-checked against the LM5146-Q1 0.37 V shutdown-falling threshold (R136 added) | New R123 / R124 100 k drain pull-downs and R125 / R126 1 k drain series resistors; the D106 / D107 anodes are on `01_QBTN_R` / `01_QALRT_R`. R103 → 33 k 1206, plus R127 (and v1.1 R136) 33 k 1206 in parallel (C18004) |
| R2-14 | noted (doc) | The Sleep budget text lives in ARCH §4.3 (updated for schematic v1). With the output off (D-01) the AFE_FLT lines are low, so they draw 0 µA |
| R2-15 | fixed | R101 / R102 1 Ω HoLRT → 2.2 Ω 2 W 2512 Yageo RC2512FK-7W2R2L (C876260); the HoLRT family has no 2.2 Ω at LCSC. TVS current ≈ 3.8 A → clamp ≈ 79 V at 25 °C (calc); 2 V drop at 0.46 A; F701 still melts at 13 A (6.5× its rating) |
| R2-16 | fixed | C123 → DNP: 22 µF + 10 µF module cap is inside the TLV62569 matrix (DS p.9 Table 4) |
| R2-20, R2-21, R2-23, R2-24, R2-25 | noted, no change | — |
| R2-22 | bring-up note | In AUX-only bench mode, SS320 leakage (≤ 10 mA at 100 °C, SS320 DS p.2) back-energises VSUP_TAP / BAT+ on the power board. Treat BAT+ as live |
| R2-32 | noted | D-09 still open in v1.0; v1.1 (SN6505B + 2.5 kV transformer) is the owner's answer |
| R3-02 | fixed in v1.0; **superseded by v1.1** (R122 / R128 dummy load removed: the TLV76750 output needs no minimum load; +5V_ISO 4.94-5.05 V at all corners, calc) | — |
| R2-02 … R2-13, R2-17, R2-18 | n/a | Sheet 02 / 08 items. R2-17 is already a layout gate (sheet 07 design note §8) |

**New LCSC numbers on this sheet (v1.0 review round).** All live-verified 2026-11-23 on the LCSC product API and the JLCPCB parts API.

| LCSC | Part | Stock (LCSC / JLC) | Class |
|---|---|---|---|
| C876260 | RC2512FK-7W2R2L | 5 285 / 6 251 | Extended |
| C18004 | 1206W4F3302T5E | 125 400 / 167 078 | Extended |
| C17887 | 1206W4F3000T5E (removed in v1.1) | – | Basic |
| C21190 | 0603WAF1001T5E | – | Basic |

Unverified: the thick-film 2512 single-pulse rating for the 1.2 J fault pulse (no curve published).

## 12. v1.1 changes (owner decision 2026-11-24, PROJECT.md §5 "v1.1 power tree")

Decision 1 supersedes D-08 (+5V trunk LM5013-Q1); decision 2 supersedes D-09 (one 2 W isolated module). Studies: v1.1 buck study (300 kHz / 47 µH baseline) and v1.1 iso study (summarised in `docs/reviews/v11_power_tree_review.md`); every 200 kHz value below was recomputed from the LM5146-Q1 DS (SNVSB32B) by script (own arithmetic; "calc" = arithmetic on DS numbers, "est." = assumed value).

### 12.1 Ref changes (v1.0 90 refs → v1.1 111 refs → 114 refs after the review, §13)

| Kind | Refs |
|---|---|
| **Removed** | D104 (SS520 freewheel diode), C105 / C106 / R107 (LM5013 type-3 ripple injection), R122 / R128 (+5V_ISO dummy load) |
| **Changed** (same ref, new part / value) | U101 LM5013QDDARQ1 → **LM5146QRGYRQ1** (C1850329); L101 22 µH → **68 µH SMDRI127-680MT** (C9907, same footprint); R104 39 k RON → **49.9 k RT**; R105 150 k → **10.5 k**; R106 47 k → **2.00 k**; C107 2.2 nF → **100 nF** BST; R109 1 M → **56 k**; C111 1 µF 0805 → **10 µF 25 V 1206**; R110 / R111 2 M 0603 → **240 k 0805**; U106 B0505S-2WR3 → **SN6505BDBVR** (C74518); C127 / C128 / C129 (4.7 µF, same part) re-roled to U106 VCC / rectifier / U107 output |
| **Added** | Q103 SQ2398ES (HS), Q104 DMN10H220LQ (LS), R129 / R130 / C130 / C131 / C132 (type-III), C133 SS, R131 / C134 ILIM, C135 VCC, R132 SYNCIN, R133 / R134 gate 0 Ω, R137 / C136 VIN filter, C137 HF CIN, R135 / C138 snubber (DNP), R136 AUX bleeder; T101 LT31-113, D110 / D111 MBR0520LT1G, U107 TLV76750DRVR, C139 / C140 100 nF, TP115 |
| **Review round (2026-11-25, §13)** | added **Q105** (2nd DMN10H220LQ-7), **R138** (100 mΩ shunt), **R139** (Q105 gate 0 Ω); changed **R105** 10.5 k → 10.7 k, **R133** 0 Ω → 4.7 Ω, **R123 / R124** 100 k → 10 k, **C135** 2.2 µF 0805 → 4.7 µF 50 V 1206, **C127** 4.7 µF → 10 µF 25 V 1206; **R135 / C138** DNP → fitted; R131 re-roled to the shunt (new net `01_U101_RS`) |
| Description-only updates | C101, D103, D105, R103, R108, R123, R125, R126, R127, C126, U105, TP102, TP106, TP107, TP108, TP111; block names of box 2 and box 6 |

New sheet-local nets: `01_U101_RT/SS/COMP/RC1/RC2/SYNC/ILIM/LO/HO/VCC/VIN/SNB`, `01_Q103_G`, `01_Q104_G`, `01_ISO_D1/D2/S1/S2/RECT`; removed `01_U101_RC`, `01_U101_RON`. `01_U101_SW/BST/FB`, `01_ISO_VIN` kept. U101 pinout: 1 EN/UVLO `PWR_EN`, 2 RT, 3 SS/TRK, 4 COMP, 5 FB, 6 AGND `GND_PWR`, 7 SYNCOUT NC, 8 SYNCIN, 9 NC, 10 PGOOD `PG_5V`, 11 ILIM, 12 PGND `GND_PWR`, 13 LO, 14 VCC, 15 EP `GND_PWR`, 16 NC, 17 BST, 18 HO, 19 SW, 20 VIN, 21 (pad) `GND_PWR`.

### 12.2 +5V trunk calculations (VIN 40-58.4 V, 9 V AUX min, 96.8 V TVS max; IOUT 0.962 A peak per ARCH §4.2)

| Item | Value | Calc / source |
|---|---|---|
| FSW | **200.4 kHz** (R104 49.9 k) | R[kΩ] = 10⁴ / F[kHz], DS p.20 Eq.3, Table 8-1; RT needed also when synchronised (p.4) |
| Mode | forced PWM: SYNCIN = VCC × 20 k / (10 k + 20 k) = 5.0 V > 2 V | DS p.5, p.26, p.9 (RSYNC-IN 20 kΩ, VIH 2 V) |
| VOUT | **5.08 V** nominal, 4.95-5.22 V worst (VREF 792-808 mV, 1 % R; R105 10.7 k since review V11-11; v1.1 draft 10.5 k gave 5.000 / 4.87-5.14 V) | 0.8 × (1 + 10.7/2.00), DS p.8; PG window tracks VREF: low < 4.67 V, OV > 5.49 V; every +5V load is ≤ 5.5 V (TLV62569, TPS22918, SN6505B VCC rec. max 5.5 V) |
| PG_5V | high above 94 % (4.70 V), low below 92 % (4.60 V) or above 108 % (5.40 V), 25 µs deglitch | DS p.8, p.19; R108 100 k to +3V3 (10-100 k, ≤ 13 V) |
| tON / tOFF | tON 258 ns @96.8 V (> 60 ns max tON(min)); tOFF 1.8 µs @8.1 V VSUP (> 200 ns) | DS p.9 |
| Inductor ripple | **0.335 A pp @58.4 V** (35 % of 0.962 A; 0.419 A with L −20 %), 0.321 A @40 V | Eq.7 p.27: VOUT(1−VOUT/VIN)/(L·FSW) |
| IL peak / Isat | 1.13 A @0.962 A (1.17 A with L −20 %); worst ILIM peak 2.71 A < **Isat 4.0 A**, Irms 0.97 A < 2.1 A | SMDRI127 DS p.9 |
| CIN | C101-C103 3 × 2.2 µF 250 V (≈ 4.6 µF eff, est.) + C137 100 nF 250 V: Irms 0.32 A @40 V, ripple 114 mV pp | DS p.29 Eq.11/12 |
| COUT | C108 / C109 2 × 22 µF 25 V (37.4 µF eff, est.) + C110: ripple **5.6 mV pp**; load-off 0.5 A step ≤ 45 mV, full 0.962 A dump ≤ 166 mV (no loop help, worst) | DS p.28 Eq.9/10 |
| VCC / BST | C135 2.2 µF (1-5 µF, p.17); C107 100 nF (≥ 0.1 µF, p.23); VCC load 2.1 mA gate + 1.8 mA IQ | Qg 2.3 + 8.3 nC × 200 kHz |
| Soft start | C133 47 nF → **3.8 ms** (3.1-4.4 ms) | DS p.21 Eq.4, ISS 8.5-12 µA p.8 |
| ILIM (review V11-01) | **RSENSE mode**: R138 100 mΩ ±1 % in the Q104 / Q105 source path, R131 1.50 k from ILIM to the shunt top, PGND pin 12 at the shunt ground side. Valley = (IRS × RILIM − VILIM-TH) / RS = **1.29 A min / 1.52 A typ / 1.76 A max** (IRS 90-110 µA, 0 ppm/°C; VILIM-TH −8…+3.5 mV; 1 % R and shunt) vs operating valley 0.83 A at 1.00 A (0.79 A with L −20 %) → ≥ +55 % margin, no temperature term. Output limit 1.45-1.97 A, worst peak 1.76 + 0.435 = **2.20 A < Isat 4.0 A** (45 % margin). Shunt 92 mW at 1.00 A, 0.31 W at the max valley (1 W part). Hiccup after 128 cycles, 8192 off | DS p.9, p.23 Fig 8-9 + Eq.6, p.24, p.10 |
| CILIM | C134 4.7 pF 250 V: τ = 7.0 ns (≈ 6 ns) | DS p.24 |
| Compensation (type III) | fo = 1/(2π√(68 µH × 37.4 µF)) = **3.16 kHz**; target fc 20 kHz (FSW/10): Kmid = fc/(fo·kFF) = 0.42 → **RC1 4.42 k**; **CC1 22 nF** (fz1 1.64 kHz = fo/2); **CC3 4.7 nF** (fz2 3.2 kHz = fo); **RC2 340 Ω** (fp2 100 kHz = FSW/2); **CC2 330 pF** (fp1 109 kHz; ceramic ESR zero > 1 MHz) | DS p.31-33 Table 9-2/9-4, Eq.16, kFF 15 (p.22) |
| Loop (exact transfer functions, RDAMP = D·RHS + (1−D)·RLS + DCR) | nominal **fc 20.0 kHz, PM 60°, GM 21 dB**; light load 20 mA: PM 58°; COUT +0 % / L +20 %: fc 14.6 kHz PM 62°; COUT −30 % / L −20 %: fc 28.8 kHz PM 53-55°, GM 17 dB; with +10 µF downstream: fc 16 kHz PM 60°. Target 50-70° (DS p.34) met in all corners | calc (script) |
| Losses @200 kHz, FPWM, after the review (Table 9-1 p.30; RHS 0.50 Ω hot, 2 × DMN in parallel at 180/235 mΩ × Fig 6, shunt 0.1 Ω, Qg 2.3 + 2 × 8.3 nC @10 V, Qrr 2 × 9.8 nC, Qoss 2 × 1.5 nC, edges +50 % for R133, snubber 100 pF) | **1.11 W @51.2 V / 1.21 W @58.4 V at 0.962 A → η 81.3 % / 79.9 %** (1.00 A: 81.4 % / 80.1 %); 0.41 W at no load, 0.43 W at 0.164 A. v1.1 draft (single LS FET, no snubber, RDS(on) sense): 0.92 / 0.97 W, 84.0 / 83.2 % | calc (script, est. items as listed) |
| Standby / sleep cost | pack current at 70 mA, 51.2 V: **8.1 mA** (v1.1 draft 5.1 mA, LM5013 2.1 mA, calc): **+6.0 mA vs LM5013** (+3.0 mA draft, +1.7 mA Q105 gate charge, +1.0 mA snubber, + Qoss) + 0.25 mA SYNCIN pull-up — **exceeds the owner-accepted ≈ +3 mA (owner question §10.4)**; U101 shutdown 13.5 µA typ / 30 µA max → Sleep +10-20 µA (unchanged) | DS p.8; calc |
| Thermal @85 °C amb, 58.4 V, 1.00 A (review V11-02) | Q104 / Q105 each 0.11-0.13 W → **Tj 104-108 °C on the minimum pad (177 °C/W)**, 95-97 °C with note-7 copper (94 °C/W) — SW copper can stay small; Q103 0.35 W (incl. 2/3 of the doubled Qrr 0.15 W) → **Tj 131 °C** (130 °C/W, Tj max 175 °C); U101 0.24 W → 94 °C (VCC 3.8 mA gate + 1.8 mA IQ); L101 0.19 W; R138 92 mW; R135 68 mW | SQ2398ES p.1-2, DMN p.2-3, DS p.7; calc with thermal feedback |
| +5V peak with the v1.1 ISO stage | ≈ 1.00 A (962 − 357 B0505S input + 396 SN6505 path at 300 mA, calc), inside the 1.45 A minimum output current limit | ARCH §4.2 updated for v1.1 |
| Snubber (fitted, V11-03) | R135 10 Ω + C138 100 pF across Q104 / Q105: 68 mW @58.4 V, 188 mW @96.8 V (C·V²·f) < 250 mW 1206 | calc |
| PWR_EN max | 11.5 V (AUX / FORCE_ON at 58.4 V) < 100 V EN abs max; C111 46 % of 25 V | §12.4 |

### 12.3 +5V_ISO (SN6505B + LT31-113 + 2 × MBR0520L + TLV76750)

Topology: `+5V` → U105 TPS22918 (`EN_ISO`, CT 330 pF, 1.06 ms) → `01_ISO_VIN` (C127 4.7 µF + C139 100 nF) → U106 VCC and EN (EN tied to VCC, CLK to GND: internal 424 kHz spread-spectrum clock, DS p.3/p.5) → D1 / D2 drive T101 pins 1 / 3, centre tap pin 2 on `01_ISO_VIN` → secondary 6 / 4 → D110 / D111 → `01_ISO_RECT` (C128 4.7 µF + C140 100 nF, TP115) → U107 IN and EN → OUT / SNS `+5V_ISO` (C129 4.7 µF + sheet 06 C615 10 µF); T101 pin 5 = `GND_ISO`. Why TPS22918 stays: `EN_ISO` is 3.3 V and the SN6505 EN needs 0.7 × VCC (DS p.5); the switch also gives a 0 µA off state (QOD discharge).

| Item | Value | Source |
|---|---|---|
| +5V_ISO (review V11-11) | **4.94-5.05 V** at 0-300 mA with +5V = 4.95-5.22 V (R105 10.7 k); in the cold / low corner the LDO is in dropout at ≥ 280 mA (≈ 4.99 V at 300 mA, scaled from the study's 4.937 V at +5V 4.90 V). With the draft 10.5 k (+5V 4.87 V) it would have been ≈ 4.90 V. **No minimum load** (R122 / R128 removed). Hot / high corner: 01_ISO_RECT ≤ 6.92 V no load, U107 0.36 W → Tj 113 °C, T101 7.2 V·µs | v1.1 iso study rescaled (calc); TLV767 DS p.5-6 (VDO 1.4 V max @1 A) |
| Rectifier / LDO headroom | 01_ISO_RECT 5.36 V (cold, 300 mA) … 6.66 V (no load, 5.1 V in); TLV767 VIN ≤ 16 V | calc; DS p.5 |
| Transformer | applied 7.02 V·µs (5.1 V / 2 / 363 kHz) < 11 V·µs; n = 1.3 ≥ 1.28 required (TI Eq.10) | WE DS p.1; SN6505 DS |
| Diodes | PRV 2 × 6.76 = 13.5 V < 20 V; 95 mW total at 300 mA | MBR0520L DS p.2 |
| Efficiency / +5V draw | 300 mA: η ≈ 76 %, 0.40 A from +5V; idle 20 mA bus: 32 mA from +5V vs ≈ 109 mA for B0505S + dummy (est.) | calc |
| Thermal @85 °C | U107 0.33 W → Tj 111 °C (77.7 °C/W); U106 → 92 °C | calc |
| Ripple | 79 mV pp on 01_ISO_RECT at 300 mA (4.5 µF eff, 848 kHz) | calc |
| Barrier | T101 2.5 kVAC / 60 s (WE 760390014 2500 VAC; LT31-113 2.5 kV); pad gap across the barrier 8.02 mm (> 6.5 mm rule; v1.0 B0505S footprint was 3.58 mm pad 2 to pad 4); D-09 Partly → Met | WE DS p.1, LT31 spec p.2 |

### 12.4 PWR_EN latch re-scale (LM5146-Q1 EN/UVLO, DS p.4, p.8, p.18-19, p.25)

The LM5146-Q1 EN/UVLO sources **9-11 µA into the external network while EN > 1.2 V** (hysteresis current, p.8). With the v1.0 R109 = 1 MΩ the source alone would hold EN at 10 V and the latch could never release. Thresholds: shutdown→standby 0.42 V rising, 50 mV hysteresis → **0.37 V falling (typ only, no min/max, p.25)**; standby → run 1.164-1.236 V. Between 0.37 V and 1.2 V the IC is in standby with the VCC LDO on (IQ-STBY 1.75 mA typ / 2 mA max, p.8).

| Check | Value (calc) | Result |
|---|---|---|
| Release condition | IHYS max × R109 = 11 µA × 56 k = **0.62 V < 1.164 V** (R109 must be < 106 k) | OK, 0.55 V margin |
| Hold after a full pulse (button, PWR_HOLD, ≥ 50 ms ALERT) | from 2.70 V (AFE_REG1 − D106), τ = 56 k × 10 µF = 0.56 s, decays toward 0.56 V while the source is on: t = 0.56 × ln((2.70 − 0.56)/(1.2 − 0.56)) = **0.68 s** (v1.0 0.66 s) | OK |
| Wake pulse charge (review V11-04) | through R125 / R126 1 k: Thevenin 2.65 V, τ = 9.8 ms → 6.2 ms to reach 1.236 V; 10 ms → 1.69 V → hold 0.32 s; **30 ms → 2.53 V → hold 0.63 s nominal / 0.49 s with C111 −25 %**. Required hold ≥ TPS3828-33 reset delay 300 ms max (sheet 03 U302, td 120-300 ms) + ≈ 30 ms rail-up / boot = **0.33 s** → a 10 ms pulse fails in the slow-supervisor corner | **AFE_ALERT latched until the MCU clears it (preferred), or low ≥ 30 ms** |
| Release time | after PWR_HOLD goes low: 0.68 s to 1.2 V (rail up), then 0.66 s in standby (1.2 → 0.37 V, source off, 1.75 mA) → shutdown ≈ 1.3 s | OK |
| AUX / FORCE_ON on | 9 V AUX: (9 − 0.6) × 56/296 = 1.59 V > 1.236 V; 40 V: 7.45 V | OK |
| AUX / FORCE_ON max | 58.4 V: 10.9 V + 0.45 V (10 µA × 240 k ∥ 56 k) = **11.4 V** (FORCE_ON at 58.4 V: 11.05 + 0.45 = 11.5 V): C111 46 % of 25 V, D105 reverse 11.5 V, R110 / R111 47.5 V across (0805 150 V), 9.4 mW | OK |
| Sleep leakage, AUX side | 100 µA ES2D leakage × (33 k / 3 = 11 k) = 1.10 V on AUX_IN → PWR_EN ≤ 1.10 × 56/296 = **0.21 V** (diode drop ignored) vs 0.37 V typ; with only 2 bleeders 0.31 V (too close) → **R136 added** | OK, margin 0.16 V to a typ-only threshold → gate B1 |
| Sleep leakage, Q101 / Q102 (review V11-05) | R123 / R124 **10 k**: IDSS 5 µA × 10 k = 0.05 V at the drain, the OR diode never conducts below ≈ 15 µA → no FET term; floor = AUX term only (0.17-0.21 V). DS Fig 7-17 (p.13): standby thresholds flat over −40…150 °C (falling ≈ 0.36-0.37 V typ) | OK; 0.33 mA from AFE_REG1 only while the button / ALERT is active |
| AUX bleeder dissipation | 3 × 103 mW at 58.4 V (41 % each), 5.3 mA from AUX (bench only) | OK |

### 12.5 Firmware rules (new / changed in v1.1)

1. **AFE_ALERT wake: latched until the MCU clears it (preferred), or low ≥ 30 ms** (review V11-04). Hold budget: PWR_EN must stay above 1.2 V for ≥ 300 ms (TPS3828-33 reset delay max) + 30 ms (rail-up and firmware start); a 30 ms pulse gives 0.49-0.63 s, a 10 ms pulse only 0.32 s. Gate B2.
2. **Assert `PWR_HOLD` as the first GPIO action after reset** (before clock tree / peripheral init); there is no fixed ms budget the firmware can control, the reset supervisor alone uses up to 300 ms.
3. **Shutdown takes ≈ 1.3 s** after `PWR_HOLD` is released (0.68 s rail still up, then ≈ 0.66 s standby at 1.75 mA); do not treat the still-alive rail as a failed shutdown and do not re-assert `PWR_HOLD` in that window.
4. **+5V_ISO ready ≥ 25 ms after `EN_ISO`** goes high (TPS22918 1.06 ms + SN6505 soft-start delay ≤ 18 ms, DS p.6 + LDO start); ignore `CAN_*_RX` / `RS485_*_RX` until then (extends the existing sheet-06 rule).
5. `PG_5V` semantics unchanged (low < 92 % / > 108 %); no MCU clock on SYNCIN in v1.1 (R132 strap).
6. **Never back-feed `+5V` while U101 is enabled** (review V11-13): in FPWM (SYNCIN high) the stage conducts negative inductor current (DS p.5 pin 8, p.26) and boosts a back-fed `+5V` into VSUP, which D101 / D102 cannot return to the pack → D103 dissipates continuously. For back-powered bench tests hold PWR_EN low (no FORCE_ON) or move R132 to GND (diode emulation).

### 12.6 New bring-up gates (v1.1)

| # | Gate | Pass criterion |
|---|---|---|
| B1 | **PWR_EN shutdown band:** measure PWR_EN and VSUP current in Sleep / Ship at 25 °C and 85 °C, AUX absent and AUX connected but unpowered | PWR_EN ≤ 0.15 V; U101 VIN current ≤ 30 µA (shutdown, DS p.8), not 1.75 mA (standby) |
| B2 | Wake by AFE_ALERT with the **minimum configured ALERT pulse at −40 °C** (C111 low, slowest supervisor); scope PWR_EN, MCU NRST and PWR_HOLD (review V11-04) | PWR_EN > 1.3 V; PWR_HOLD high before PWR_EN falls below 1.2 V, with ≥ 50 ms spare after NRST release |
| B3 | Latch release after PWR_HOLD low | PWR_EN < 1.16 V, then shutdown (< 0.37 V) within ≈ 2 s |
| B4 | SW node and LS gate (review V11-03 / V11-08): probe at the Q104 / Q105 drain with a spring ground at TP107; VSUP 58.4 V, 1 A; then repeat with an 80 V bench supply on VSUP | at 58.4 V: (V_SW,pk − VSUP) ≤ 8 V and undershoot ≥ −5 V (DS p.6: SW −5 V for 20 ns); at 80 V: V_SW,pk < 95 V; `01_Q104_G` bump at the SW rising edge < 0.8 V. Tune R135 / C138 (fitted) or R133 (4.7-10 Ω); never increase R134 / R139 |
| B5 | Load step 0.1 ↔ 0.9 A at 40 V and 58.4 V (Bode if available) | overshoot < 150 mV, ≤ 2 rings (PM ≥ 45°) |
| B6 | Overload: ramp the +5V load (review V11-01: shunt limit) | hiccup between 1.45 A and 2.0 A output; L101 not saturating (peak ≤ 2.2 A) |
| B7 | Thermal at 0.96-1.0 A (scaled to 85 °C ambient), after review V11-02 | Q104 / Q105 Tj < 120 °C, Q103 < 140 °C, R138 < 100 °C; no large copper needed on the SW node |
| B8 | +5V_ISO: 0 → 300 mA at −40 °C and +85 °C; TP115 headroom; T101 pin-1 orientation on the first article | 4.90-5.10 V; TP115 ≥ 5.4 V at 300 mA cold; pin-1 dot matches pad 1 |
| B9 | Barrier hipot (board level) after assembly | per D-09 test level, ≤ the 2.5 kVAC / 60 s T101 rating |
| B10 | Q103 R_DS(on) at 6.4-6.9 V gate (review V11-06): V_DS(on) of Q103 at 1 A, −40 °C, AUX 9 V only (VSUP ≈ 8.1 V, VCC at the edge of regulation) | V_DS(on) ≤ 0.6 V (≈ 0.55 Ω × 1.1 A, SQ2398ES DS p.2 max hot at 10 V); else swap Q103 to DMN10H220LQ-7 (R_DS(on) specified at 4.5 V) |
| B11 | Back-feed check (V11-13) | with +5V driven by a 5.3 V bench supply and U101 enabled, VSUP must not rise: document as a forbidden test configuration instead |

Removed gates: v1.0 R2-01 (B0505S pin 1/2 on a sample) and R3-02 (+5V_ISO ≤ 5.5 V at idle / −40 °C with the dummy load).

**Layout rules added by the review:** (a) V11-03: C137 plus one 2220 input cap (C101-C103) inside a < 1 cm² loop with the Q103 drain and the R138 / Q104 / Q105 source return; (b) V11-01: R131 and C134 Kelvin to the R138 top pad, U101 PGND (pin 12) Kelvin to the R138 ground pad, power return separate; (c) V11-02: Q104 / Q105 symmetric (same gate trace length from LO via R134 / R139, same source path to R138), SW copper kept minimal; (d) V11-14: T101 rule area (no tracks / vias / pours, all copper layers, x ±4.0 / y ±3.4 mm) is now in the footprint.

### 12.7 New LCSC numbers (live 2026-11-24; review round 2026-11-25 below the table)

| LCSC | MPN | Refs | Stock LCSC / JLC | JLC class |
|---|---|---|---|---|
| C1850329 | LM5146QRGYRQ1 (TI) | U101 | 8 862 / 9 149 | Extended |
| C727466 | SQ2398ES-T1_GE3 (Vishay) | Q103 | 10 266 / 10 266 | Extended |
| C5260572 | DMN10H220LQ-7 (Diodes) | Q104 | 3 645 / 3 646 | Extended |
| C9907 | SMDRI127-680MT (SXN) | L101 | 59 180 / 61 093 | Extended |
| C23184 | 0603WAF4992T5E 49.9 k | R104 | 1 009 800 / 1 283 026 | Basic |
| C22855 | 0603WAF1052T5E 10.5 k (dropped by review V11-11, now C22857) | (R105) | 76 200 / 92 124 | Extended |
| C22975 | 0603WAF2001T5E 2.00 k | R106 | 2 980 800 / 9 032 092 | Basic |
| C23043 | 0603WAF4421T5E 4.42 k | R129 | 15 200 / 15 200 | Extended |
| C23144 | 0603WAF3400T5E 340 Ω | R130 | 19 400 / 19 600 | Extended |
| C22843 | 0603WAF1501T5E 1.5 k | R131 | 983 200 / 2 499 896 | Basic |
| C25804 | 0603WAF1002T5E 10 k | R132 | 1 500 / 41 684 468 | Basic |
| C21189 | 0603WAF0000T5E 0 Ω | R133, R134 | 5 713 800 / 15 153 853 | Basic |
| C22939 | 0603WAF220KT5E 2.2 Ω | R137 | 0 / 206 599 | Basic |
| C17903 | 1206W4F100JT5E 10 Ω | R135 (DNP) | 272 000 / 1 138 355 | Basic |
| C23206 | 0603WAF5602T5E 56 k | R109 | 209 700 / 564 321 | Basic |
| C25824 | 0805W8F2403T5E 240 k 150 V | R110, R111 | 61 500 / 98 731 | Extended |
| C21122 | CL10B223KB8NNNC 22 nF | C130 | 329 200 / 1 091 509 | Basic |
| C53987 | 0603B472K500NT 4.7 nF | C132 | 86 500 / 797 821 | Basic |
| C1622 | CL10B473KB8NNNC 47 nF | C133 | 426 900 / 1 650 505 | Basic |
| C2294341 | GQM1875C2E4R7BB12D 4.7 pF 250 V | C134 | 6 300 / 6 301 | Extended |
| C19110 | CL21B225KAFNNNE 2.2 µF 25 V (dropped by review V11-07, now C29823) | (C135) | 761 770 / 840 700 | Extended |
| C106241 | CC1206KKX7RYBB104 100 nF 250 V | C136, C137 | 111 920 / 123 318 | Extended |
| C66331 | 0805CG101J251NT 100 pF 250 V | C138 (DNP) | 14 100 / 13 957 | Extended |
| C70462 | CC1206KKX7R8BB106 10 µF 25 V | C111 | 162 890 / 187 154 | Extended |
| C74518 | SN6505BDBVR (TI) | U106 | 1 482 / 1 728 | Extended |
| C7471252 | LT31-113 (Linekey) | T101 | – (not on LCSC API) / 771 | Extended |
| C2802211 | 760390014 (Würth), alternate for T101 | (md only) | – / 0 | Extended |
| C23848 | MBR0520LT1G (onsemi) | D110, D111 | 288 830 / 288 839 | Extended |
| C2872569 | TLV76750DRVR (TI) | U107 | 4 664 / 4 664 | Extended |

Review round, live 2026-11-25 (LCSC product API + JLC parts API):

| LCSC | MPN | Refs | Stock LCSC / JLC | JLC class |
|---|---|---|---|---|
| C5123673 | HoLRTX1206-1W-100mR-1% (Milliohm), 1 W, ±50 ppm/°C, −55…+155 °C | R138 | 20 220 / 20 224 | Extended |
| C22857 | 0603WAF1072T5E 10.7 k | R105 | 25 800 / 25 814 | Extended |
| C23164 | 0603WAF470KT5E 4.7 Ω | R133 | 332 300 / 766 555 | Basic |
| C5260572 | DMN10H220LQ-7 (re-read for Q105) | Q104, Q105 | 3 645 / 3 646 | Extended |
| C29823 / C70462 / C25804 / C21189 / C17903 / C66331 | re-read for C135 / C127 / R123-R124 / R139 / R135 / C138 | — | 272 390 / 893 096; 151 945 / 176 912; 53 100 / 40 854 406; – ; 228 200 / 1 122 944; 14 100 / – (JLC API timeout, 13 957 on 11-24) | — |

Numbers dropped by the review: C22855 (10.5 k, was R105), C19110 (2.2 µF 0805, was C135).

Re-used numbers re-read on 2026-11-24 for their new rows: C14663 (C107, C139, C140), C1664 (C131), C29823 (C127-C129), C18004 (R136), C25803 (R108). Numbers no longer used on this sheet: C5219285 (LM5013), C2891410 (SS520), C9905 (22 µH), C23153, C22807, C25819, C17470, C22976, C17887, C7465195 (B0505S).

### 12.8 Symbols and footprints (v1.1)

* the project symbol library: **+ `Automotive_ESS_BMS:LM5146-Q1_RGY`** (21 pins: 1-20 + 21 = EP; pin 15 "EP" passive → GND; DS p.4-5) and **+ `Automotive_ESS_BMS:Transformer_CT_1P_1S_LT31-113`** (pins 1 P1, 2 PCT, 3 P2 left; 6 S1, 5 SCT, 4 S2 right; LT31-113 spec p.3 = WE DS p.1); − LM5013-Q1_DDA, − B0505S-2WR3 (no longer used).
* the project footprint library (`footprints.pretty/`): **+ `TI_RGY0020B_VQFN-20-1EP_3.5x4.5mm_P0.5mm_EP1.7x2.7mm`** (A11) and **+ `Transformer_WE-PPTI_760390014`** (6 pads 1.12 × 0.96 mm at x = ±4.57, y = −2.54 / 0 / +2.54; pin 1 top-left, 1-2-3 down the left column, 6-5-4 down the right column; body 7.14 × 6.73 on F.Fab; courtyard ±5.38 × ±3.62). Both load in KiCad 10 (`kicad-cli fp upgrade` round trip, 25 / 6 pads).
* Stock symbols / footprints used for new refs: `Transistor_FET:Q_NMOS_GSD` + `Package_TO_SOT_SMD:SOT-23` (Q103), `Transistor_FET:DMN10H220L` + SOT-23 (Q104), `Power_Management:SN6505BDBV` + `SOT-23-6` (U106), `Regulator_Linear:TLV76750DRVx` + `Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm_ThermalVias` (U107), `Device:D_Schottky` + `Diode_SMD:D_SOD-123` (D110 / D111), `Inductor_SMD:L_SXN_SMDRI127` (L101 unchanged).

### 12.9 Owner-accepted trade-offs (PROJECT.md 2026-11-24)

* +5V trunk: owner accepted ≈ 84 % peak efficiency and ≈ +3 mA standby; **after the review fixes (Q105, fitted snubber, shunt, R133) the calc is ≈ 81 % / 80 % at peak and ≈ +6 mA standby vs LM5013 — outside the accepted figure, owner question §10.4.** Sleep +10-20 µA (U101 shutdown current), latch re-scale (R109 / C111 / R110 / R111 / R136, R123 / R124 10 k), AFE_ALERT latched or ≥ 30 ms. Gained: synchronous FPWM at a fixed 200 kHz (predictable EMI spectrum, CISPR 25 class 5 optimised controller, DS p.1), LM5013 stock risk closed, temperature-independent current limit.
* +5V_ISO: fixes the 3.58 mm B0505S creepage defect (8.02 mm pad gap), barrier 1.5 kVDC → 2.5 kVAC / 60 s (D-09 Partly → Met), no dummy load, idle draw from +5V ≈ 109 → 32 mA (offsets most of the buck standby increase while `EN_ISO` is on); cost +$0.62 and 3 more Extended types (study).
* Follow-ups outside this sheet (done in the v1.1 documentation pass): ARCHITECTURE §3 / §4.1 / §4.2 text (LM5013 → LM5146, U4 B0505S → SN6505B chain, +5V peak ≈ 1.00 A, `+5V_ISO` min load row), D-08 / D-09 notes; sheet 06 text updated in this round.

## 13. v1.1 review disposition (v1.1 review 2026-11-24, accepted and applied 2026-11-25)

| ID | Sev | Disposition | Change / evidence |
|---|---|---|---|
| V11-01 | MAJOR | **fixed** | RSENSE current limit (DS p.23 Fig 8-9): **R138** 100 mΩ 1 % 1 W 1206 HoLRTX (C5123673) in the Q104 / Q105 source path (`01_U101_RS`), **R131** 1.50 k from ILIM to the shunt top, PGND pin 12 to the shunt ground side (`GND_PWR`, Kelvin rule §12.6). Valley 1.29 / 1.52 / 1.76 A (min / typ / max over IRS 90-110 µA, 0 ppm/°C, VILIM-TH, 1 % R and shunt; DS p.9) vs 0.83 A operating valley at 1.00 A; worst peak 2.20 A vs Isat 4.0 A. 1.40 k was also checked (1.20-1.65 A); 1.50 k kept for margin and to reuse C22843. C134 4.7 pF kept (τ 7 ns) |
| V11-02 | MAJOR | **fixed** | **Q105** = second DMN10H220LQ-7 (C5260572) in parallel with Q104, own gate resistor **R139** 0 Ω (C21189). LO drive: 2 × 8.3 nC = 16.6 nC from a 2.3 A / 3.5 A driver, Miller (2 × 2 nC) in ≈ 1.7 / 1.1 ns — fine; VCC load +1.7 mA. Thermals (calc, thermal feedback, Fig 6): Q104 / Q105 0.11-0.13 W each → 104-108 °C on the minimum pad, 95-97 °C with copper; Q103 incl. 2/3 of the doubled Qrr → 0.35 W, Tj 131 °C (175 °C max). Cost: standby +1.7 mA (owner question §10.4) |
| V11-03 | MAJOR | **fixed** | **R135 / C138 fitted** (10 Ω 1206 + 100 pF 250 V C0G, 68 mW); **R133 = 4.7 Ω** (C23164): HS turn-on path 12 Ω vs 7.3 Ω, Miller 3.0 → 4.9 ns (calc); 10 Ω rejected because the adaptive dead time senses the driver pin (overlap risk) and turn-off loss rises; R134 stays 0 Ω. Gate B4 rewritten ((V_SW,pk − VSUP) ≤ 8 V, undershoot ≥ −5 V at 58.4 V; < 95 V at an 80 V bench VSUP); layout rule (a) added |
| V11-04 | MAJOR | **fixed (firmware + text)** | Rule 1: AFE_ALERT latched until the MCU clears it (preferred) or low ≥ 30 ms (2.53 V → 0.49-0.63 s hold); explicit budget ≥ 300 ms reset (TPS3828-33 td max) + 30 ms; rule 2: assert PWR_HOLD as the first GPIO action after reset; gate B2 now at −40 °C with the minimum configured pulse. No hardware change |
| V11-05 | MINOR | **fixed** | R123 / R124 100 k → **10 k** (C25804, already in the BOM): FET leakage term removed, floor 0.17-0.21 V (AUX term only); DS Fig 7-17 added as evidence (§12.4); gate B1 kept |
| V11-06 | MINOR | note + gate | Accepted with bring-up gate **B10** (Q103 V_DS(on) at 1 A, −40 °C, AUX 9 V); fallback DMN10H220LQ-7 for Q103 (same footprint / pinout) |
| V11-07 | MINOR | **fixed** | C135 → **4.7 µF 50 V 1206** (C29823, already in the BOM), ≈ 4 µF at 7.5 V (est.), inside the 1-5 µF window (DS p.17) |
| V11-08 | MINOR | note + gate | R134 / R139 stay 0 Ω ("never increase" in the descriptions), HS edge slowed by R133; B4 now scopes `01_Q104_G` (bump < 0.8 V) |
| V11-09 | MINOR | **fixed** | C127 → **10 µF 25 V 1206** (C70462, already in the BOM); TPS22918 inrush 48 mA (calc) |
| V11-10 | MINOR | **fixed (text)** | PWR_FLAG on `VSUP`, `+3V3_A`, `GND_ISO`, `01_U101_VIN`, `01_ISO_RECT`; none on `+5V_ISO` (§1) |
| V11-11 | MINOR | **fixed** | +5V_ISO range corrected (§12.3). **R105 10.5 k → 10.7 k applied** (C22857): VOUT 5.08 V, 4.95-5.22 V worst; PGOOD window is a fraction of VREF and moves with VOUT (low < 4.67 V, OV > 5.49 V) — fits; every +5V load is rated ≥ 5.5 V; loop re-run with RFB1 10.7 k: fc 20 kHz, PM 60° (52.7° worst), unchanged because above fz2 the CC3 / RC2 branch sets the gain; SN6505 V·µs 7.2 < 11, 01_ISO_RECT ≤ 6.92 V, U107 Tj 113 °C. Result: +5V_ISO ≈ 4.99 V in the cold 300 mA corner instead of 4.90 V |
| V11-12 | MINOR | note | Owner question §10.5 (LT31-113 temperature / AEC in writing or reserve Würth; functional isolation in D-09); gate B8 stays at −40 °C |
| V11-13 | MINOR | note | Firmware / bench rule 6 (never back-feed `+5V` with U101 enabled; R132 → GND or PWR_EN low for back-powered tests), gate B11 |
| V11-14 | MINOR | **fixed** | `Transformer_WE-PPTI_760390014.kicad_mod`: rule area "T101_barrier_keepout", all copper layers (`*.Cu`), x ±4.0 / y ±3.4 mm, tracks / vias / pours not allowed, pads allowed; round trip through `kicad-cli fp upgrade` keeps the zone and the 6 pads |
| N-01…N-07 | NOTE | noted | confirmations (pins, loop, LCSC, footprints); N-05 closes the T101 body owner question as not applicable (§10.3) |
| N-08 | NOTE | **text** | AUX-only UVLO ≈ 7.1 V on / ≈ 4.4 V off added to the box-7 note (bench-only dropout behaviour) |
| N-09 | NOTE | not applied | gate-source 100 k on Q103 / Q104 / Q105 left out (driver body diodes hold the gates ≈ 0.7 V in Sleep, below DMN Vth min 1.0 V); bring-up option |
| N-10 | NOTE | not applied | R137 stays 2.2 Ω (A12); 4.7-10 Ω is a value-only bring-up option |
| N-11 | NOTE | **text** | TLV767 COUT ESR 2-500 mΩ confirmed; §9 item 11 closed, C129 description |
| N-12 | NOTE | partly | TVS clamp corners stated in A12 (79 V at 25 °C, 84-87 V hot, ≈ 91 V at VC 96.8 V); §12 ILIM / thermal rows updated; R824 value (A4) is sheet 08's; no THT pad on `01_U101_VCC` added (owner may add TP116) |

Self-check after the review (script): 114 refs, 273 net rows, 40 local nets, interface net set identical to v1.0, every new / changed LCSC row matches the live record, **ERRORS: 0**.
