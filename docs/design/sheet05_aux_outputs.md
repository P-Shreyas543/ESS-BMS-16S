# Sheet 05 — Aux Outputs (control board, refs 5xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 05). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 36 refs = 36 fitted (of which 3 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 0 DNP; 16 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

Scope of this sheet (contract 2026-11-23): EXT_OUT1/2 low-side coil drivers + terminal J501, fan driver + tach + header J502.
Not here: heater FET (power board, sheet 07), dry-contact photoMOS (sheet 08).
36 parts = 33 assembled + 3 THT test pads, 0 DNP. Fitted cost ≈ $1.08 / board @ 100 (JLC price, 2026-11-23). Updated after review R3 (see Review disposition).

## Blocks (left → right signal flow)

| # | Box title | Contents | Key number for the on-sheet note |
|---|---|---|---|
| 1 | **+12V aux entry** | C502 10 µF X5R, C503 100 nF at J501 / J502 | `+12V` budget, LM5163-Q1 (sheet 01): fan 150 mA + 2 × 70 mA EXT + 1.2 mA heater gate ≈ 291 mA of ≈ 470 mA DC (62 %, calc; B est. for 470 mA) |
| 2 | **Fan driver** | Q501 AO3400A ON/OFF from `FAN_EN` (R501 1 k, R502 100 k), D501 SS34 flyback, Q504 AO3400A open-drain PWM from `FAN_PWM` (R511 1 k, R512 100 k), J502 4-pin, tach R503 10 k PU / R504 1 k / C501 1 nF / D502 BAT54C clamp, TP501 | Q501 at 150 mA: 0.15² × 48 mΩ = 1.1 mW (calc, RDS(on) @ 2.5 V AO3400A DS p.2); PWM 25 kHz on pin 4 only; tach filter τ = 1 k × 1 nF = 1 µs. Note on sheet: "Q501 = fan ON/OFF only, never PWM the supply" |
| 3 | **EXT_OUT1 driver** | R505 1 k, R507 100 k, D503 5.6 V clamp, Q502, F501 PTC, D505 SS34, D509 SMAJ15A, R509 + D507 ON LED, TP502 | ≤ 70 mA continuous per channel at 85 °C (≤ 120 mA at 25 °C; SMD1206P012TF hold 0.07 / 0.12 A, RUILON DS p.4); short → trip ≈ 0.44 A at −40 °C (est. 0.29 A × 0.18 / 0.12) < LM5163 IPEAK 0.63 A min; 0.5 A trips in ≤ 1 s (DS p.2) |
| 4 | **EXT_OUT2 driver** | R506, R508, D504, Q503, F502, D506, D510, R510 + D508, TP503 | as block 3 |
| 5 | **EXT terminal** | J501 DB128V-5.08-4P: 1 EXT1+ (`05_EXT1_P`), 2 EXT1− (drain), 3 EXT2+, 4 EXT2− | 16 A / 300 V UL per pin (DORABO drawing) |

Channel topology (each EXT): `+12V` → PTC → `05_EXTn_P` = J501 "+" pin → external coil → J501 "−" pin = drain → AO3400A → `GND_PWR`.
SS34 across the coil terminals (cathode on the PTC side), SMAJ15A from `05_EXTn_P` to `GND_PWR` (drain is clamped through the SS34 to the same node: worst drain ≈ 24.4 V + 0.5 V < 30 V VDS).
Gate: `EXT_OUTn` → 1 k → gate, 100 k gate–source (this is the §10 100 kΩ PD), BZT52C5V6 gate clamp (P-12).
ON LED from `05_EXTn_P` → 4.7 k → green LED → drain: (12.2 − 2.9) / 4.7 k = 2.0 mA (calc).

Fan header J502 is the 4-wire PC-fan order (KK-254 style 2.54 mm): 1 = ground switched by Q501 (`05_FAN_SW`), 2 = `+12V`, 3 = tach, 4 = PWM (open drain, Q504; the fan supplies the pull-up). A 4-wire fan is speed-controlled on pin 4 with Q501 on; a 3-wire fan plugs onto pins 1–3 and is switched on/off by Q501 only.
With low-side PWM the fan ground floats while Q501 is off, so the tach line can be pulled toward +12 V through the fan electronics; R504 + D502 (BAT54C, both anodes on `FAN_TACH`, cathode on `+3V3`) keep PC9 below VDD + 0.3 V.

## Test points
| TP | Net | Proves |
|---|---|---|
| TP501 | `05_FAN_SW` | fan PWM and Q501 switching |
| TP502 | `05_EXT1_D` | EXT1 drain: switch state, flyback clamp |
| TP503 | `05_EXT2_D` | EXT2 drain |
`+12V` and `GND_PWR` hooks are on sheet 01 (TP104 +12V in bom_G1); none duplicated here.

## DNP list
None.

## AGENT DECISIONS (owner may overrule)
| Question | Choice | Why | Source |
|---|---|---|---|
| bom_G4 Q4: PTC / e-fuse per EXT channel | **PTC per channel** F501 / F502 = RUILON **SMD1206P012TF (C20982)** after review R3-05 (was SMD1206P020TF: at −40 °C its trip ≈ 0.69 A exceeded the buck limit) **plus** SMAJ15A TVS per channel (D509 / D510, C113958) | A harness short now trips the 0.46 A PTC instead of holding the shared `+12V` buck (fan, heater gate) in current limit; trip < LM5163 IPEAK min 0.63 A over −40…85 °C (est. from the derating row). The TVS clamps harness surges below the AO3400A 30 V VDS. An e-fuse would cost ≈ 10× | RUILON DS p.2 (SMD1206P012TF: Ihold 0.12 A, Itrip 0.29 A, 60 V, 0.5 A / 1 s), p.4 derating 0.18 / 0.12 / 0.07 A; MDD SMAJ15A DS p.2; LM5163 IPEAK from bom_G1 U102 |
| bom_G4 Q1 / P-12: EXT FET | AO3400A + 5.6 V gate clamp (owner accepted P-12 on 2026-11-23; recorded, not an AGENT DECISION) | SQ2318AES not specified at 3.3 V drive | AO3400A DS p.2 |
| bom_G4 Q3: X5R bulk | C502 10 µF 25 V **X5R 0805 Basic C15850** | owner 2026-11-23 allows X5R for bulk | PROJECT.md §5 2026-11-23 |
| P-13: fan header −25 °C (JST PH S3B-PH-K C545716) | **DLL 2510-4A C22451125** (4-pin after review R3-06; 2,150 LCSC / 2,155 JLC), 2.54 mm KK-254-compatible vertical header, −40…+105 °C, footprint `Connector_Molex:Molex_KK-254_AE-6410-04A_1x04_P2.54mm_Vertical` (drill 1.19 ≥ DS 0.9) | −40 °C rated, standard 3-pin PC-fan plug fits, $0.04. Genuine Molex 22-27-2031 (C471416, 9,000 pcs) has no temperature on LCSC and the Molex drawing could not be downloaded | DLL DS p.1 (3 A, 250 V, −40…+105 °C), p.2 drawing (0.64 mm pin, Ø0.9 hole) |
| Terminal ref | EXT terminal = **J501** (was J503 in P3; the dry-contact terminal moved to sheet 08) | contract scope | sheet scope |
| Fan tach clamp | add D502 BAT54C (C37704, already used for D109 on sheet 01) | protects PC9 from the floating-ground tach line; no new BOM line | Nexperia BAT54 DS p.1–2 |

## New interface signals
| Name | From → to | Type | Note |
|---|---|---|---|
| `FAN_EN` | U801 P14 (sheet 08, the spare left by `EN_SENSE`, ARCHITECTURE §8) → R501 → Q501 gate | 3.3 V push-pull, 100 kΩ PD here (R502) | fan supply ON/OFF (review R3-06). **Needs sheet 08 to wire U801 P14 = `FAN_EN`** (done: sheet 08 wires U801 P14 = `FAN_EN`) |

Other cross-sheet nets: `EXT_OUT1`, `EXT_OUT2`, `FAN_PWM`, `FAN_TACH` (ARCHITECTURE §10), rails `+12V`, `+3V3`, `GND_PWR`.

## B2B change requests
None.

## −40 °C check (D-14 / P-13)
All parts −40 °C or better (listing / DS): AO3400A −55…150, SS34 / BZT52 / SMAJ15A MDD −55/−65…150, KT-0805G −40…85, PTC −40…85 (DS p.1), DB128V −40…105, 2510-4A −40…105, BAT54C −55…150, chip R/C −55…125/155.

## Unverified items
* EXT coil current limit: ≤ 70 mA continuous per channel at 85 °C is a PTC-derating figure; the −40 °C trip current is scaled from the hold-current row (est., the DS gives Itrip at 25 °C only); the actual external coil (interposing relay / breaker shunt trip) is not known.
* LM5163-Q1 `+12V` DC capability ≈ 0.47 A is B's estimate (ARCHITECTURE §4.2), not re-derived here.
* SS34 and BZT52C5V6 (MDD) ratings from listing (datasheets not opened, as in P3).
* KK-254 compatibility of 3- and 4-pin PC fan plugs with the DLL 2510-4A header (general knowledge; same 2.54 mm wafer family; standard PC 4-pin headers use a pin-1-3 ramp that the plain 2510 wafer does not have — check plug fit / polarisation with the chosen fan).
* Fan tach pull-up to the floating fan ground: worst-case tach-line voltage with Q501 off depends on the fan; clamp current < 9 mA is a calc with 12 V on the raw node.

## Owner questions that remain
1. EXT outputs are now sized for interposing relays (≤ 70 mA at 85 °C, ≤ 120 mA at 25 °C). Is that enough, or should EXT drive contactor coils directly (then LM5164 on sheet 01, bigger PTC, D-07)?
2. Fan type: 12 V 4-wire PWM PC fan (3-wire also supported on/off) — confirm.

## Firmware notes
* **Never PWM `FAN_EN` / Q501 at 25 kHz** (chops the fan supply into its input capacitor): Q501 is ON/OFF (≤ 100 Hz at most). Speed control = 25 kHz on `FAN_PWM` (PC3 TIM1_CH4) → J502 pin 4, 4-wire fans only.
* `FAN_TACH` is valid only while Q501 is on.
* `FAN_PWM` shares TIM1 with `HEATER_EN` / `EXT_OUT1/2` (one frequency, review R3-21).
* `EXT_OUTn` are static on/off (no PWM needed); if a coil economiser is used, PWM ≥ 20 kHz keeps the SS34 freewheel current continuous.

## Review disposition (review R3, 2026-11-23)
| Finding | Disposition | Change |
|---|---|---|
| R3-05 PTC trips above the LM5163 limit at −40 °C | **fixed** | F501 / F502 → SMD1206P012TF **C20982** (live-verified 2026-11-23: RUILON, 40,770 LCSC / 41,685 JLC, Extended, −40…+85 °C); EXT rating now ≤ 70 mA @ 85 °C / ≤ 120 mA @ 25 °C; `+12V` budget 291 mA (62 %) |
| R3-06 fan supply chopped at 25 kHz | **fixed** | J502 → 4-pin DLL 2510-4A **C22451125** (GND / +12V / TACH / PWM); new Q504 AO3400A + R511 1 k + R512 100 k drive pin 4 open-drain from `FAN_PWM`; Q501 (R501, R502) now ON/OFF from new signal `FAN_EN` (U801 P14, sheet 08 to wire); firmware rule added |
| R3-21 TIM1 shared by PC0–PC3 | noted | firmware note |
