# Sheet 09 — Wireless (control board, refs 9xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 09). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 17 refs = 13 fitted (of which 0 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 4 DNP; 9 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

ESP32-C3-MINI-1-**H4X** (C41349510, owner pick 2026-11-23, replaces the NRND -N4) on `+3V3_ESP`, UART0 to the MCU UART4 (PC10 / PC11), reset / boot controlled from expander U801 (sheet 08).
17 parts = 13 fitted + 4 DNP (R905, Q901, R906, J901). Fitted cost ≈ $2.34 / board @ 100 (module $2.26). Updated after review R3.

## Blocks
| # | Box title | Contents | Key number for the on-sheet note |
|---|---|---|---|
| 1 | **ESP32-C3 module** | U901, C901 10 µF X5R, C902 100 nF | `+3V3_ESP` 3.0–3.6 V (ESP DS v2.2 p.21), 350 mA TX peak (budget ARCHITECTURE §4.2, 18 % of U6) |
| 2 | **EN reset RC** | R901 10 k, C903 1 µF, R902 1 k from `ESP_EN` | τ = 10 k × 1 µF = 10 ms (DS p.34 recommends 10 k / 1 µF); `ESP_EN` low → EN = 3.3 × 1 k / 11 k = 0.30 V < VIL 0.83 V (calc, DS p.21) |
| 3 | **Boot straps** | R903 10 k GPIO9 PU + R910 1 k from `ESP_BOOT`, R904 10 k GPIO8 PU, R907 10 k GPIO2 PU | GPIO9 = 1 → SPI boot, 0 → joint download (GPIO8 must be 1) (DS p.13 table 4-3) |
| 4 | **UART to MCU** | R908 1 k (`ESP_RXD` → RXD0 pin 30), R909 1 k (TXD0 pin 31 → `ESP_TXD`), R911 100 k `ESP_TXD` pull-up to `+3V3` (PC11 idles high with the ESP off; 33 µA back-feed, calc) | back-power current with ESP off ≤ (3.3 − 0.3) / 1 k = 3 mA (calc) |
| 5 | **ROM-flash options (DNP)** | R905 1 k GPIO4 → `MCU_BOOT0`; Q901 AO3400A GPIO5 → `MCU_NRST` + R906 100 k; J901 1×6 header (GND, TXD0, RXD0, EN, GPIO9, +3V3_ESP sense) | D-46: the radio does not control the safety MCU by default |

Placement: U901 at a board edge, antenna end (beyond pads 36–48) outward and flush / overhanging; no copper on any layer and no parts in the keep-out zone (ESP DS p.10). Keep RJ45 shields, Cu bars and the FET banks away from the antenna end.

Pin use (ESP DS v2.2 p.11 table 3-1): 1, 2, 11, 14, 36–53 GND (49 = centre pad array) → `GND_PWR`; 3 3V3; 8 EN; 5 IO2 strap; 22 IO8 strap; 23 IO9 strap; 18 IO4 / 19 IO5 for the DNP options; 30 RXD0, 31 TXD0; all other IO (0, 1, 3, 6, 7, 10, 18, 19) and the NC pins → `NC`.

## Test points
No separate pads: J901 is DNP, its bare THT holes are the probe points for EN, GPIO9, TXD0, RXD0, `+3V3_ESP` and GND. The `+3V3_ESP` hook is on sheet 01 (TP105 in bom_G1). P3's TP901–TP904 are dropped (duplicate probe points on the same nodes).

## DNP list
| Ref | Fit when |
|---|---|
| R905 1 k | owner accepts D-46 (ESP may put the STM32 into ROM bootloader via BOOT0) |
| Q901 AO3400A, R906 100 k | owner accepts D-46 (ESP may reset the STM32 via `MCU_NRST`) |
| J901 1×6 header | bench flashing of the ESP over UART0 without the MCU; pin 6 is a sense pin, do not supply the board through it |

## AGENT DECISIONS (owner may overrule)
| Question | Choice | Why | Source |
|---|---|---|---|
| bom_G4 Q2: module | ESP32-C3-MINI-1-**H4X** C41349510 (owner decision 2026-11-23, recorded) — 2,954 LCSC / 4,260 JLC, $2.26 | -N4 / -H4 are NRND; H4X = chip v1.1, −40…105 °C | ESP DS v2.2 p.3 |
| bom_G4 Q3: X5R bulk | C901 10 µF → X5R 0805 Basic C15850 | owner 2026-11-23 | PROJECT.md §5 |
| `ESP_BOOT` series resistor | add **R910 1 k** (C21190, Basic) | limits back-power from U801 P13 into GPIO9 when `+3V3_ESP` is off; low level stays 0.30 V | calc |
| ESP flash access | **J901 DNP 1×6 header** (C492405) instead of four THT test pads | one footprint gives UART0 + strap + EN access for flashing and doubles as probe points | D §7 "DNP ROM-flash straps / header" |
| D-46 straps | keep R905 / Q901 / R906 DNP (ARCHITECTURE D-46 recommendation) | – | ARCHITECTURE §14 |

## New interface signals
| Name | From → to | Type | Note |
|---|---|---|---|
| `MCU_BOOT0` | R905 (DNP) → MCU PB8-BOOT0 (sheet 03, 10 k PD there) | 3.3 V logic | name from ARCHITECTURE §8 pin 61 and D §8; not in the §10 table, hence listed |
Other cross-sheet nets (ARCHITECTURE §10): `ESP_EN`, `ESP_BOOT` (U801 P12 / P13, sheet 08), `ESP_RXD`, `ESP_TXD` (MCU PC10 / PC11, sheet 03), `MCU_NRST` (DNP Q901), rails `+3V3_ESP`, `GND_PWR`.

## B2B change requests
None.

## −40 °C check
U901 −40…105 °C (DS p.3); AO3400A −55…150; header −40…105; chip R/C −55…125/155. No exception.

## Unverified items
* Antenna keep-out dimensions: only the module figure (DS p.10) was used; the ESP32-C3 Hardware Design Guidelines (≈ 15 mm clearance) were not opened. The keep-out rule area must be drawn at layout (the generated footprint has none).
* Module footprint generated by easyeda2kicad from C41349510; after review R3-03 checked against DS v2.2 fig 11-1 p.38: 48 × 0.4 × 0.8 mm pads at 0.8 mm pitch, rows 11.8 / 9.8 mm apart, 4 × 0.7 mm corner pads (11.9 / 9.9), 9 × 1.45 mm EPAD squares over 5.4 mm — all match. The DS pin-1 EPAD square is chamfered; ours is a plain square (harmless). Thermal vias between the squares (DS fig 11-1) are a layout item.
* Metal enclosure vs PCB antenna (D-32 still open): the -1U external-antenna variant ESP32-C3-MINI-1U-H4X exists (DS p.4) but was not looked up on LCSC.

## Owner questions that remain
1. D-32: enclosure material / antenna window (plastic window or the -1U variant)?
2. D-46: allow the ESP to re-flash / reset the STM32 (fit R905, Q901, R906)?

## Firmware notes
* Keep U801 P12 (`ESP_EN`) low and P13 (`ESP_BOOT`) as input (Hi-Z) whenever `EN_ESP` is off, and keep MCU PC10 (UART4 TX) low or Hi-Z, so nothing back-powers the module.
* Download mode: P13 low, pulse P12 low ≥ 1 ms, release P12, hold P13 low ≥ 3 ms (tH, DS p.13), then release.
* PC10 / PC11 are also the STM32 ROM USART3 pins (AN2606): this is what the DNP D-46 option uses.

## Review disposition (review R3, 2026-11-23)
| Finding | Disposition | Change |
|---|---|---|
| R3-03 9th GND EPAD square missing in the U901 footprint | **fixed** | `footprints.pretty/ESP32-C3-MINI-1.kicad_mod`: pad 49 now 9 × 1.45 mm rects incl. (−1.98, −1.98); re-checked vs DS fig 11-1 p.38 (see Unverified items) |
| R3-13 PC11 (UART4 RX) floats / sees break while the ESP is off | **fixed** | R911 100 k 0603 (C25803, existing line) `ESP_TXD` → `+3V3` |
