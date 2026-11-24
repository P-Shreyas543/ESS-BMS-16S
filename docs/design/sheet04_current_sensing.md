# Sheet 04 — Current Sensing (power board, refs 4xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/power_board_v1.pdf`](../schematic/power_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 04). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 43 refs = 42 fitted (of which 8 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 1 DNP; 20 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

**Net naming (interface contract rev. R1-09 / R1-06).** The shunt battery-side current pads are `BAT-` (200 A power copper, global label, power board only) and join `GND_PWR` (all signal grounds, B2B ground pins) only through **NT401** at the battery-side Kelvin edge of the shunt. `PACK-` is a global label. The latch output is `OC_TRIP_N_PB` (power board only; the 10 k to the B2B `OC_TRIP_N` sits on sheet 07). Sheet-local nodes: `04_SH1_KB`, `04_SH1_KP`, `04_SH2_KB`, `04_SH2_KP` (Kelvin taps, B = battery side, P = PACK− side), `04_ISENSE_AMP`, `04_ISENSE_F`, `04_REF_HI`, `04_REF_LO`, `04_CLR_N`. §10 names used: `SHUNT_K_BAT`, `SHUNT_K_PACK` (to J701 pins 11/12 on sheet 07; taken at the sense pads), `INA_K_P`, `INA_K_N` (local), `ISENSE_OUT`, `OC_CLR`, `NTC_SHUNT`.

## Shunt decision (owner pick HolRS3920 — parallel count, footprint, thermal)

| Check | 1 × 0.2 mΩ | **2 × 0.2 mΩ ∥ = 100 µΩ (chosen)** | Source |
|---|---|---|---|
| 200 A continuous | 8.0 W = **160 %** of 5 W; rated current 158 A → fails | 100 A each → **2.0 W = 40 %** of 5 W | Milliohm DS p.3 (5 W, 158.11 A) |
| 85 °C ambient | – | derating 100 % to 70 °C, linear to 0 at 170 °C → 4.25 W; 2.0 W = **47 %**; with ±10 % sharing (110 A) 2.4 W = 57 % | DS p.4 curve; calc |
| 500 A / ≤ 10 ms (D-06) | – | 250 A each → 12.5 W = 2.5 × P_rated for 10 ms; DS short-time overload 5 × P_rated for 5 s, ΔR ≤ 0.5 % → covered (inferred, no pulse curve) | DS p.5 |
| Short circuit ≈ 1.2 kA, 25 µs | – | 600 A each → 72 W × 25 µs = 1.8 mJ (negligible) | calc |
| Signal levels | 40 mV at 200 A; INA saturates at +362 A → window +599 A impossible | **20 mV / 200 A, 50 mV / 500 A** (BQ CC ±200 mV); INA linear −800…+725 A; no change to A's thresholds | A §5.1, §5.3 |
| TCR error at +35 K | – | ±50 ppm × 35 K = **±0.18 %** (was ±0.8 % with WSLP5931) — NTC_SHUNT compensation becomes optional refinement | DS p.3 |

**Footprint.** Bare manganin 3920 (10.0 × 5.2 mm, 2-terminal, DS p.3). Recommended land DS p.6: L 11, A 6.2, B 5.6 mm → current pads 2.7 × 6.2 mm at ±4.15 mm; Kelvin "sensing trace" leaves the inner pad edge at mid-width (DS p.6 figure) → sense pads 2/3 (0.6 × 0.6 mm) overlapping the inner edges, `net_tie_pad_groups "1, 2" "3, 4"`. Pad numbers follow `Device:R_Shunt` (1, 4 current; 2 next to 1, 3 next to 4) like the stock WSK2512 Kelvin footprint. easyeda2kicad (C558625) gives 2 pads 3.5 × 5.2 mm at ±3.81 mm (inner gap 4.12 mm ≠ DS 5.6 mm) — kept as reference only. Layout: mirror-symmetric copper from both shunts to the lugs (current sharing), 2 oz outer, thermal vias to the Al plate, RT401 on GND_PWR copper at the battery-side pads.

## Blocks (left → right)

| # | Box title | Parts | Key number (calc) |
|---|---|---|---|
| 1 | Shunt + Kelvin taps | R401, R402, NT401, TP401 | 100 µΩ; 2.0 W each at 200 A = 40 % |
| 2 | Kelvin filters | R403–R410, C401 | BQ pair: 2 × 20 Ω per leg (10 Ω) + 100 Ω at the BQ (sheet 02) → τ 22 µs; INA pair: 2 × 10 Ω (5 Ω) + 22 nF → τ = 10 Ω × 22 nF = **0.22 µs** |
| 3 | Current amplifier U401 | U401, C402, R419, TP402, TP403 | ISENSE_OUT = **1.65 V + 2.0 mV/A** (REF1 = VS, REF2 = GND; gain error 0.20 %, INA240 DS p.5) |
| 4 | OC window comparator U402 | U402, R411–R414, C403, C404, C407, C408, TP407, TP408 | V_HI = 3.3 × 86.5 / 100.2 = 2.849 V → **+599 A**; V_LO = 3.3 × 31.6 / 100.2 = 1.041 V → **−305 A**; ±2 % ≈ ±12 A |
| 5 | OC latch U403 + supervisor | U403, U404, R415, R416, R420, C405 (DNP), C406, C410, C411, TP404–TP406 | power-up / brown-out: TLV803S holds CLR_N ≤ 0.2 V from VDD 1.1 V until 200 ms after +3V3 > 2.93 V (DS p.5, p.8) → latch powers up tripped; trip path load = 10 k + pin capacitance only |
| 6 | NTC_SHUNT | RT401, TP409 | bias 10 k from +3V3_A on sheet 10 (R1013 + C1010); 1.65 V at 25 °C over the B2B |

## Pin map (full list in the netlist)

* **R401 / R402** (Device:R_Shunt): 1 `BAT-`, 2 `04_SHn_KB`, 3 `04_SHn_KP`, 4 `PACK-`.
* **R403/R404**: `04_SH1_KB` / `04_SH2_KB` → `SHUNT_K_BAT`; **R405/R406**: `04_SH1_KP` / `04_SH2_KP` → `SHUNT_K_PACK` (SRP = battery side → charge reads positive, BQ DS p.5).
* **R407/R408**: `04_SHn_KP` → `INA_K_P`; **R409/R410**: `04_SHn_KB` → `INA_K_N` (IN+ = PACK− side → discharge reads positive, A §5.1).
* **U401 INA240A1PWR** (INA240 DS ZHCSFM1A p.3 = `Amplifier_Current:INA240A1PW`): 1 NC → GND_PWR (DS: connect to ground), 2 IN+ `INA_K_P`, 3 IN− `INA_K_N`, 4 GND, 5 VS `+3V3_A`, 6 REF2 GND_PWR, 7 REF1 `+3V3_A`, 8 OUT `04_ISENSE_AMP` → R411 (comparator RC) and R419 100 Ω → `ISENSE_OUT` (B2B / MCU; INA240 C_load ≤ 1 nF, DS p.5).
* **NT401** (NetTie-2 2.0 mm): 1 `BAT-`, 2 `GND_PWR`, placed at the battery-side Kelvin edge of R401 / R402.
* **U402 TLV1702AIDGKR** (DGK pinout SBOS589 p.5 = `Comparator:LM2903` numbering): ch 1 trips high side — 3 1IN+ `04_REF_HI`, 2 1IN− `04_ISENSE_F`, 1 1OUT; ch 2 trips charge side — 5 2IN+ `04_ISENSE_F`, 6 2IN− `04_REF_LO`, 7 2OUT; outputs wired-OR = `04_CLR_N`; 8 V+ `+3V3_A`, 4 V− GND_PWR. Inputs rail-to-rail (VCM V− to V+, p.7), needed because V_HI = 2.85 V on a 3.3 V supply (an LM2903 would not work).
* **U403 SN74AUP1G74DCUR** (SCES644D p.3 = `74xGxx:74AUP1G74`): 1 CLK `04_OC_CLK` (P5-02: `OC_CLR` from J701.20 → R416 10 k PD + TP405 on the connector side → R420 1 k series → `04_OC_CLK`, C411 100 pF C0G to GND_PWR at the pin), 2 D +3V3, 3 /Q NC, 4 GND, 5 Q `OC_TRIP_N_PB`, 6 /CLR `04_CLR_N`, 7 /PRE +3V3, 8 VCC +3V3.
* **U404 TLV803SDBZR** (project symbol, DBZ pinout ZHCS187C p.3): 1 GND, 2 /RESET (open drain) = `04_CLR_N`, 3 VDD = +3V3; C410 100 nF. R415 10 k pull-up now from `+3V3_A` (R1-10).
* Supply split per ARCH §5.4: INA240, TLV1702 and the divider on `+3V3_A`; latch and supervisor on `+3V3`; CLR_N pull-up on `+3V3_A` so a lost analog rail trips the latch.

## Test points

| TP | Net | Type | Proves |
|---|---|---|---|
| TP401 | GND_PWR | black hook | probe ground at the shunt star |
| TP402 | +3V3_A | red hook | analog rail arriving over the B2B |
| TP403 | 04_ISENSE_AMP | THT pad | INA output: 1.65 V at 0 A, CC / INA gain calibration |
| TP404 | OC_TRIP_N_PB | THT pad | latch state (low after power-up) |
| TP405 | OC_CLR | THT pad | clear edge from the MCU |
| TP406 | 04_CLR_N | THT pad | comparator / supervisor state |
| TP407 / TP408 | 04_REF_HI / 04_REF_LO | THT pad | window thresholds 2.849 / 1.041 V |
| TP409 | NTC_SHUNT | THT pad | shunt temperature divider |

No pad on `04_ISENSE_F` (RC-internal) or the Kelvin nodes.

## DNP list

| Ref | Why | Fit only if |
|---|---|---|
| C405 100 pF | CLR_N noise option (never 100 nF, P-06) | false trips from coupled noise are seen at bring-up |

## AGENT DECISIONS (owner may overrule)

| # | Question | Choice | Why | Source |
|---|---|---|---|---|
| AD-04-1 | Shunt parallel count (owner part HolRS3920) | **2 in parallel = 100 µΩ** | single part is 160 % of rating at 200 A and breaks the INA / window scaling | table above |
| AD-04-2 | Shunt footprint | hand-made 4-pad Kelvin per DS p.6 land | easyeda land does not match the DS | the project footprint library (`footprints.pretty/`) |
| AD-04-3 | Q3 Kelvin averaging R | **R403–R406 = 20 Ω** (C22950) | TI-preferred split, 100 Ω at the BQ on sheet 02 | bom_G2 F-3 |
| AD-04-4 | Comparator part | **TLV1702AIDGKR (C2870937)** replaces TLV1702AQDGKRQ1 (C130036) | C130036 has **0 stock** at LCSC and JLC today; same DGK pinout, −40…125 °C; v1 is not AEC-Q (same reasoning as the owner's INA240 non-Q pick) | live 2026-11-23; SBOS589 p.5, p.7 |
| AD-04-5 | Q7 / P-06 POR | **superseded by review R1-05:** TLV803S supervisor (U404) wired-OR on CLR_N; C405 → 100 pF DNP | the RC + diode held CLR_N low for only ≈ 0.12 ms (R415 charged C409 through D401) | review R1-05 |
| AD-04-6 | Reference node filtering | **C407 / C408 100 nF** on OC_REF_HI / OC_REF_LO | ~12–22 kΩ nodes next to a 200 A path; τ 1.2 / 2.2 ms settles inside the latch's power-up hold | calc |
| AD-04-7 | Q4 NTC_SHUNT bias | **superseded by integration fix 2026-11-23:** bias stays on sheet 10 (R1013 + C1010) with the other NTC biases; R417 removed, RT401 stays | one bias per net | integration |
| AD-04-8 | NT401 | **restored** (interface contract rev. R1-09): BAT− ↔ GND_PWR at the Kelvin edge | the net tie enforces the single star in the PCB tool | review R1-09 |
| AD-04-9 | TP409 NTC_SHUNT | added | ADC-feeding node, THT pad per house rule | instruction §5.5 |

Owner picks applied: INA240A1PWR non-Q (C93965), HolRS3920 C558625; P-06 intent (separate power-up hold, no 100 nF on CLR_N) kept, now by a supervisor.

## New interface signals

No new name invented here; one contract name that is not in ARCHITECTURE §10 is listed for the netlist self-check.

| Signal | From → to | Note |
|---|---|---|
| `OC_TRIP_N_PB` | U403 Q (sheet 04) → U701 AND input + 10 k to B2B `OC_TRIP_N` (sheet 07) | interface contract 2026-11-23 rev. R1-06; global label, power board only |

## B2B change requests

None. Sheet 04 has no connector of its own; `SHUNT_K_BAT`, `SHUNT_K_PACK`, `ISENSE_OUT`, `NTC_SHUNT`, `OC_CLR`, `+3V3`, `+3V3_A`, GND_PWR reach J701 (and `OC_TRIP_N_PB` reaches U701 / the 10 k) on sheet 07 by name.

## Integration notes (P3 duplicates — keep one)

* NTC_SHUNT sensor: RT401 here vs RT702 (P3 BOM, sheet 07) → keep RT401, drop RT702.
* NTC_SHUNT bias: R1013 + C1010 on sheet 10 (integration fix); R417 removed from this sheet.
* `OC_TRIP_N_PB` has no pull-down here (no switched sense rail, ARCH §5.4); the sheet 07 kill logic owns its own fail-safe pull-downs (bom_G2 F-13).

## Review disposition (R1 power board — items on sheet 04)

| ID | Disposition | Change |
|---|---|---|
| R1-05 MAJOR | **fixed** | R418 / C409 / D401 / D402 deleted; **U404 TLV803SDBZR (C132016)** open-drain /RESET on `04_CLR_N`, C410 100 nF. Low-VCC check: output valid for VDD ≥ 1.1 V (VOL < 0.2 V at 50 µA, DS p.5 "power-up reset voltage"); below 1.1 V it is Hi-Z (DS p.8) but CLR_N then sits at ≤ VDD where the AUP latch is not yet operating; from 1.1 V until 200 ms after +3V3 ≥ 2.93 V (2.87–2.99 V) CLR_N is held low → Q = 0 = tripped. Brown-out below 2.87 V re-asserts it. VOL 0.2 V at 0.5 mA (DS p.5) vs AUP VIL 0.9 V |
| R1-06 MAJOR (sheet 04 part) | **fixed** | U403.Q → `OC_TRIP_N_PB`; TP404 on it; the 10 k to B2B `OC_TRIP_N` is on sheet 07 |
| R1-09 MAJOR | **fixed** | R401 / R402 pin 1 → `BAT-`; NT401 `BAT-` ↔ `GND_PWR` at the shunt Kelvin edge; SHUNT_K_BAT / INA_K_N taken at the sense pads 2 |
| R1-10 MINOR | **fixed** | R415 pull-up from `+3V3_A` (loss of the analog rail trips the latch; AUP inputs ≤ 3.6 V, DS p.4) |
| R1-11 MINOR | **deferred to bench (proposed fix option b)** | No DS evidence either way at 3.3 V / 0.33 mA (only the 36 V rows, SBOS589 p.7). Bring-up item: measure CLR_N low level with ISENSE forced past each threshold at −40 / 25 / 85 °C, pass ≤ 0.6 V. Fallback if it fails: open-drain rail-to-rail comparator with VOL specified at 3.3 V in the DGK pinout (to be selected then) |
| R1-15 MINOR | **fixed** | R419 100 Ω 0603 (C22775) between the INA output (`04_ISENSE_AMP`, R411 tap) and `ISENSE_OUT`; sheet 03 adds the ADC kick-back RC |
| R1-23 / R1-24 NOTE | noted | window maths and pin maps confirmed by the reviewer |
| R1-02 / R1-26 | n/a here | sheet 02 / sheet 07 items |
| P5-02 (2026-11-24) | **fixed** | R416 → 10 k 0603 pull-down on `OC_CLR` (connector side, C25804 reused from R415), TP405 stays on `OC_CLR`; new **R420** 1 k 0603 series (C21190 reused from R411) → new local net `04_OC_CLK` → U403 pin 1 CLK; new **C411** 100 pF C0G 0603 (C14858 reused from C405) `04_OC_CLK` → GND_PWR at U403. 1 k + 100 pF ≈ 67 ns/V edge (τ 100 ns over 1.5 V swing region; AUP1G74 Δt/ΔV ≤ 200 ns/V, SCES644D recommended operating conditions). No new LCSC numbers |
| P5-06 | **fixed** | visible local label on every `04_*` net (`04_SHn_KB/KP`, `04_ISENSE_AMP`, `04_ISENSE_F`, `04_REF_HI`, `04_REF_LO`, `04_CLR_N`, `04_OC_CLK`) |
| P5-04 | **no change (already present)** | BAT- already has THT pad TP716 at the B- lug on sheet 07; a second pad next to NT401 would duplicate the net (house rule: one probe point per net) |

## Unverified items

1. HolRS3920 500 A / 10 ms: no pulse curve; inferred from the 5 × P / 5 s overload test (DS p.5).
2. Current sharing between R401 / R402 depends on layout symmetry (assumed ±10 %).
3. TLV1702 V_OL at 0.33 mA: DS gives only 600 mV at 0 mA / 900 mV at 4 mA (at VS = 36 V, p.7) vs AUP VIL 0.9 V → bench test item (R1-11).
4. RT0603BRD0731K6L (C705766) shows LCSC stock 0, JLC 1 043 — enough for ≈ 1 000 boards only via JLC.
5. RT0603BRD0713K7L (C861119) JLC 1 236 — watch.
6. INA240 non-Q DS used = TI Chinese edition ZHCSFM1A (Oct 2016) from the LCSC record; page numbers refer to it.

## Owner questions that remain

1. Window thresholds +599 / −305 A (A Q3) still as proposed.
2. Accept the non-Q TLV1702AIDGKR (−Q1 out of stock) or wait for C130036 stock.

## Live verification of LCSC numbers (2026-11-23)

LCSC product API (`wmsc.lcsc.com/ftps/wm/product/detail`) + JLCPCB parts API (`selectSmtComponentList`, exact componentCode), both queried 2026-11-23; same MPN in both records.

| LCSC | MPN | Mfr | JLC type | Stock LCSC / JLC | Refs |
|---|---|---|---|---|---|
| C558625 | HolRS3920-5W-0.2mR-1% | Milliohm | Extended | 14414 / 14414 | R401, R402 |
| C22950 | 0603WAF200JT5E | UNI-ROYAL | Basic | 320500 / 1081137 | R403, R404, R405, R406 |
| C22859 | 0603WAF100JT5E | UNI-ROYAL | Basic | 1491760 / 6147238 | R407, R408, R409, R410 |
| C77069 | GRM21B5C1H223JA01L | muRata | Extended | 35050 / 54881 | C401 |
| C93965 | INA240A1PWR | TI | Extended | 1720 / 2396 | U401 |
| C22775 | 0603WAF1000T5E | UNI-ROYAL | Basic | 3671300 / 12717986 | R419 |
| C14663 | CC0603KRX7R9BB104 | YAGEO | Basic | 227500 / 52250351 | C402..C410 (6) |
| C21190 | 0603WAF1001T5E | UNI-ROYAL | Basic | 13282000 / 39615039 | R411, R420 (P5) |
| C27694 | CL10C471JB8NNNC | Samsung Electro-Mechanics | Extended | 11700 / 18823 | C403 |
| C2870937 | TLV1702AIDGKR | TI | Extended | 1944 / 1944 | U402 |
| C861119 | RT0603BRD0713K7L | YAGEO | Extended | 1220 / 1236 | R412 |
| C728593 | RT0603BRD0754K9L | YAGEO | Extended | 10680 / 10736 | R413 |
| C705766 | RT0603BRD0731K6L | YAGEO | Extended | 0 / 1043 | R414 |
| C25804 | 0603WAF1002T5E | UNI-ROYAL | Basic | 0 / 42079659 | R415, R416 (P5) |
| C14858 | CL10C101JB8NNNC | Samsung Electro-Mechanics | Basic | 57500 / 2950463 | C405, C411 (P5) |
| C140267 | SN74AUP1G74DCUR | TI | Extended | 17291 / 17291 | U403 |
| C25803 | 0603WAF1003T5E | UNI-ROYAL | Basic | 3380900 / 12793234 | (none after P5; R416 is now 10 k C25804) |
| C132016 | TLV803SDBZR | TI | Extended | 31210 / 31497 | U404 |
| C13564 | NCP18XH103F03RB | muRata | Extended | 218390 / 228475 | RT401 |
| C5199801 | RH-5001 | ronghe | Extended | 97335 / 99458 | TP401 |
| C5277086 | RH-5000 | ronghe | Extended | 194800 / 194802 | TP402 |

Unique LCSC numbers: 8 Basic, 13 Extended.
