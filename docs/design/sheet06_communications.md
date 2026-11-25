# Sheet 06 — Communications (control board, refs 6xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 06). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 97 refs = 87 fitted (of which 14 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 10 DNP; 28 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

2 × isolated CAN FD (CA-IS3050CW), 2 × isolated RS-485 (CA-IS3082WX) on one `+5V_ISO` / `GND_ISO` domain (D-09, D-10), 4 × RJ45, termination DIPs, isolated USB-C service port (CH340X + ISO7721DR) on its own `GND_USB` domain.
97 parts = 73 assembled + 10 THT test pads + 10 DNP + 4 mounting holes (not in BOM). Fitted cost ≈ $7.96 + 2 × 10k ≈ $7.97 / board @ 100 (JLC price 2026-11-23). Updated after review R3 and the P5 fix round (see Review disposition).

## Domains (checked by script on the netlist)
| Domain | Ground | Supply | Parts |
|---|---|---|---|
| MCU side | `GND_PWR` | `+3V3` | U601–U604 pins 1–8, U606 pins 5–8, C601/C603/C607/C609/C611/C613/C623, R611–R617, R634/R635 (DE pull-downs) |
| Isolated bus side | `GND_ISO` | `+5V_ISO` (from sheet 01: U105 TPS22918 → U106 SN6505B push-pull driver → T101 1:1.3 transformer (LT31-113, 2.5 kV) → D110/D111 → U107 TLV76750 5.0 V LDO, v1.1; never on an RJ45) | U601–U604 pins 9–16, CMCs, 0R bypasses, termination, TVS, bias, RJ45 3/6, C602/C604–C606/C608/C610/C612/C614–C617, TP601–TP609 |
| Chassis | `CHASSIS` | – | RJ45 shields, MH601–MH604; C618 1 nF 2 kV ∥ R626 1 MΩ to `GND_ISO` |
| USB service | `GND_USB` | `+5V_USB` (VBUS via F601) | J605, U605, U607, U606 pins 1–4, R627–R629, C619–C622, C624, TP610/TP611 |
`GND_ISO`, `GND_PWR` and `GND_USB` meet only through the isolators (union-find check: no merge). The USB barrier is ISO7721DR D-package, CPG 4 mm (ISO7721 DS p.7): a functional barrier against laptop ground loops, not the 6.5 mm comms barrier.

**v1.1 supply change (owner 2026-11-24, PROJECT.md §5 "v1.1 power tree", text only on this sheet):** the isolated bus side is fed by the sheet-01 SN6505B + T101 + TLV76750 chain instead of the v1.0 2 W isolated DC/DC module (D-09 superseded). The comms barrier on the supply path is now T101 (2.5 kVAC / 60 s; 8.02 mm pad gap across the barrier, sheet 01 §12.3), in line with the 6.5 mm rule; the v1.0 module footprint had only 3.58 mm between its input and output ground pads. No dummy load on `+5V_ISO` any more. No sheet-06 part or net changes; layout: keep the barrier keep-out (and the optional isolation slot) continuous under T101 on sheet 01.

## Blocks (left = MCU side, barrier in the middle, connectors on the right board edge)
| # | Box title | Contents | Key number for the on-sheet note |
|---|---|---|---|
| 1 | **Isolated CAN INV** | U601, C601, C602, C605, R611 4.7 k TXD PU, R613 33 R, L601 (DNP) / R618, R619 | 5 kVrms, CPG / CLR 8 mm (CA-IS305xC DS p.8); ICC2 73 mA max dominant (p.10) |
| 2 | **Isolated CAN LINK** | U602, C603, C604, C606, R612, R614, L602 (DNP) / R620, R621 | as block 1 |
| 3 | **Isolated RS-485 INV** | U603, C607/C611, C608/C612, R615 33 R, R634 10 k DE pull-down, R630/R631 10 R anti-surge in A/B, R607/R608 560 R bias (DNP) | RE tied low (echo of own frames), fail-safe RO high for VA−VB > −20 mV (CA-IS308x DS p.5) |
| 4 | **Isolated RS-485 LINK** | U604, C609/C613, C610/C614, R616, R635 10 k DE pull-down, R632/R633 10 R, R609/R610 (DNP) | as block 3 |
| 5 | **Termination INV** | SW601 + R601/R602 60.4 R + C616 4.7 nF, R605 120 R 1206. On-sheet note **and PCB silk next to SW601/SW602: "1+2 = CAN TERM, switch together"** | split fc = 1 / (2π × 30.2 Ω × 4.7 nF) = 1.1 MHz; CAN pole ≈ 2.0 V / 120 Ω = 17 mA, RS-485 pole 2.5 V / 120 Ω = 21 mA < 25 mA DIP rating (calc; DSHP04TSGET drawing note 1.4) |
| 6 | **Termination LINK** | SW602 + R603/R604 + C617, R606 | default OFF; ON only on the first and last pack of a chain |
| 7 | **Inverter ports** | J601 INV-CAN + R622–R625 (DNP), J602 INV-485, D601 SZNUP2105L, D604 PSM712, TP602/603/606/607 | TVS ≤ 5 mm from the RJ45 pins (D §4) |
| 8 | **Pack-link ports** | J603 LINK-IN, J604 LINK-OUT (1:1), D602/D603 NUP2105L, D605/D606 PSM712, TP604/605/608/609 | straight Cat5 from LINK-OUT n to LINK-IN n+1 |
| 9 | **Isolated domain** | C615 10 µF `+5V_ISO` bulk (in parallel with sheet 01 C129 4.7 µF at the U107 output; TLV767 COUT 1-220 µF), C618 / R626 chassis RC, TP601 GND_ISO hook | `+5V_ISO` load ≈ 300 mA worst case (ARCHITECTURE §4.2); supply 4.94-5.05 V at 0-300 mA with no minimum load (sheet 01 §12.3, v1.1) |
| 10 | **USB-C service port** | J605 USB4105-GF-A, R627/R628 5.1 k Rd, U607 USBLC6, F601 PTC, C619, U605 CH340X + C620/C621, U606 ISO7721DR + C622/C623, R617 33 R, C624/R629 shell RC, TP610/TP611 | `+5V_USB` load ≈ 22 mA (CH340X 20 mA max, CH340 DS V3C p.8) vs PTC hold 0.2 A |
| 11 | **Mounting holes** | MH601–MH604 M3 plated (MountingHole_Pad, same as MH701) on `CHASSIS` | "MH on CHASSIS, standoffs to the power board / Al plate; MH601 next to the RJ45 row" |

Signal paths:
* CAN: MCU TX → 33 R → transceiver TXD (4.7 k PU to `+3V3` on that node); RXD direct to MCU. Bus side: CANH/CANL → CMC footprint (DNP, 0 R bypass fitted) → `06_CANH_x` / `06_CANL_x` → split termination via DIP poles 1/2, TVS, RJ45 4/5.
* RS-485: MCU TX → 33 R → DI; DE from the USART RTS_DE pin (internal weak PD, DS p.5, plus R634 / R635 10 k to `GND_PWR`, P5C-03); RO → MCU RX. Transceiver A/B (`06_U60x_A/B`) → 10 R anti-surge (R630–R633) → bus node (`06_RS485_x_A/B`) with TVS, termination, bias → RJ45 2/7 (A), 1/8 (B); 120 R via DIP pole 3; DIP pole 4 spare (NC). Bus VOD with 2 × 10 R ≥ 1.5 V × 54 / 74 = 1.1 V (calc, stiff-driver estimate) ≫ 0.2 V receiver threshold.
* Service: CH340X TXD → ISO7721 INB (pin 3) → OUTB (pin 6) = `SVC_RX` (PA10); `SVC_TX` (PA9) → 33 R → INA (pin 7) → OUTA (pin 2) → CH340X RXD. ISO7721 outputs default high when the input side is unpowered (DS p.1), so `SVC_RX` idles high with no USB cable.

## RJ45 pinout (ARCHITECTURE §9, Seplos / PACE / JBD convention)
| Pin | J601 INV-CAN | J602 INV-485 | J603 / J604 LINK |
|---|---|---|---|
| 1 | `06_J601_P1` → R622 (DNP) → `06_RS485_INV_B` | `06_RS485_INV_B` | `06_RS485_LINK_B` |
| 2 | `06_J601_P2` → R623 (DNP) → `06_RS485_INV_A` | `06_RS485_INV_A` | `06_RS485_LINK_A` |
| 3, 6 | `GND_ISO` | `GND_ISO` | `GND_ISO` |
| 4 | `06_CANH_INV` | NC | `06_CANH_LINK` |
| 5 | `06_CANL_INV` | NC | `06_CANL_LINK` |
| 7 | `06_J601_P7` → R624 (DNP) → `06_RS485_INV_A` | `06_RS485_INV_A` | `06_RS485_LINK_A` |
| 8 | `06_J601_P8` → R625 (DNP) → `06_RS485_INV_B` | `06_RS485_INV_B` | `06_RS485_LINK_B` |
| SH | `CHASSIS` | `CHASSIS` | `CHASSIS` |
Bus nets keep the D §8 names with the sheet prefix (`06_CANH_INV` = D's `CANH_INV`, etc.) because they never leave this sheet; assign them to net class `CAN_Bus`.

## Test points
| TP | Net | Proves |
|---|---|---|
| TP601 (black hook RH-5001) | `GND_ISO` | probe ground for all isolated-side measurements |
| TP602 / TP603 | `06_CANH_INV` / `06_CANL_INV` | inverter CAN levels, termination (60 Ω with DIP on) |
| TP604 / TP605 | `06_CANH_LINK` / `06_CANL_LINK` | link CAN |
| TP606 / TP607 | `06_RS485_INV_A` / `_B` | inverter RS-485, fail-safe idle |
| TP608 / TP609 | `06_RS485_LINK_A` / `_B` | link RS-485 |
| TP610 / TP611 | `+5V_USB` / `GND_USB` | service-port supply after the PTC |
The P3 red hook on `+5V_ISO` (TP601 red) is **dropped**: bom_G1 already has a `+5V_ISO` hook on sheet 01 (TP106), and the house rules (instruction.md §5.5) forbid two probe points per net.

## DNP list
| Ref | Why DNP / fit when |
|---|---|
| L601, L602 ACT45B CMC | fit only if the EMC test needs it, then remove R618/R619 (R620/R621) |
| R607–R610 560 R | RS-485 bias; fit only for a legacy master without fail-safe receivers (D-35) |
| R622–R625 0 R | J601 pins 1/2/7/8 carry RS485_INV only if a Seplos-style inverter cable needs it (D-28) |

## AGENT DECISIONS (owner may overrule)
| Question | Choice | Why | Source |
|---|---|---|---|
| bom_G4 Q5 (D-28): INV-CAN pins 1/2/7/8 | **NC, with DNP 0 R options R622–R625** | D-28 recommendation; keeps the CAN cable free of a second bus unless the inverter needs it | ARCHITECTURE §14 D-28 |
| bom_G4 Q6: auto-address on link pins 7/8 | **dropped** (no `ADDR_IN` / `ADDR_OUT`) | pins 7/8 carry `RS485_LINK_A/B` (Seplos parallel-port convention); the pack address comes from the DIP on sheet 08 | D §3.5 |
| bom_G4 Q7: DIP pole 4 | **spare, both pins NC; bias stays DNP** | one pole cannot switch a symmetric two-resistor bias; CA-IS3082 receivers are true fail-safe; D-35 says bias DNP | CA-IS308x DS p.5; D-35 |
| bom_G4 Q3: X5R bulk | C615 `+5V_ISO` 10 µF → **X5R 0805 Basic C15850** (was Extended X7R 1206 C14860) | owner 2026-11-23 allows X5R | PROJECT.md §5 |
| P-13 RJ45 (KH-RJ45-58-8P8C −25…+70 °C) | **XKB X12ADGWA3DY1027, C2916453**, shielded RA THT no-LED, −40…+85 °C, 125 VAC / 1.5 A; 25,629 LCSC / 27,236 JLC; $0.40 | −40 °C rated, 8× the stock of the P3 part; footprint generated (the project footprint library (`footprints.pretty/`)) | XKB drawing rev A1 (2025-04-30) |
| P-13 DIP (DSHP04TSGER −30…+85 °C) | **DSHP04TSGET, C40736** (Kingtek / "YE"), −40…+85 °C, 25 mA 24 VDC, same 1.27 mm / 7.62 mm footprint as stock `SW_DIP_SPSTx04_Slide_KingTek_DSHP04TS`; $0.30 (cheaper) | same series, −40 °C | DSHP04TSGET drawing notes 1.2, 1.4 + PCB layout |
| P-13 USB-C (HRO TYPE-C-31-M-12 −30…+80 °C) | **GCT USB4105-GF-A, C3020560**, −40…+85 °C, stock KiCad footprint `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` (pads = symbol pins, checked) | −40 °C, footprint in the stock library; +$0.49 | GCT DS p.1 |
| P-13 USB-UART (CH340C: −20…+70 °C unless lot "4…") | **CH340X, C3035748** (MSOP-10, stock symbol `Interface_USB:CH340X`, stock footprint `MSOP-10_3x3mm_P0.5mm`), −40…+85 °C per CH340 DS V3C p.8; 5 V-tolerant IO | the CH340C rating depends on a lot code JLC cannot guarantee; CH340X rating does not | CH340 DS V3C p.8 (EN), pin-out CN DS p.10 figure 7.9 |
| CAN TVS | keep P3's SZNUP2105LT1G (AEC-Q101) at every CAN RJ45 (D601–D603) | already verified in P3; one per jack | NUP2105L DS p.2 |
| TP601 `+5V_ISO` red hook | dropped (duplicate of sheet-01 hook) | instruction.md 5.5 "no duplicates on one net" | – |

## New interface signals
| Name | From → to | Type | Note |
|---|---|---|---|
| `+5V_USB` | J605 VBUS → F601 → U605 / U606 VCC1 | power rail of the `GND_USB` domain, sheet 06 only | D §8 name; needs a project power symbol (pin `power_in`) and a PWR_FLAG (enters only through a connector). Not in the contract rail list, hence listed here |
Cross-sheet nets used (all in ARCHITECTURE §10 or the contract rails): `CAN_INV_TX/RX`, `CAN_LINK_TX/RX`, `RS485_INV_TX/RX/DE`, `RS485_LINK_TX/RX/DE`, `SVC_TX/RX`, `+3V3`, `+5V_ISO`, `GND_PWR`, `GND_ISO`, `GND_USB`, `CHASSIS`. `CHASSIS` and `GND_USB` need PWR_FLAG / power symbols as for any rail entering only through connectors.

## B2B change requests
None.

## −40 °C check (D-14 / P-13)
After the swaps every fitted part is rated −40 °C or better: CA-IS3050CW / CA-IS3082WX −40…125 (DS p.6 / p.7), ISO7721 −55…125 (DS p.5), USBLC6 Tj −40…125, NUP2105L / PSM712 −55…150, ACT45B −40…150, PTC −40…85, XKB RJ45 −40…85, DSHP04TSGET −40…85, USB4105 −40…85, CH340X −40…85 (DS V3C), chip R/C −55…125/155. RH-5001 hook: no rating (metal). **No exception needed**, but see the CH340X item below.

## Unverified items
* **CH340X temperature**: CH340 DS V3C (English, LCSC copy of C84681) p.8 lists "CH340X / lot-4 CH340C/N −40…85 °C"; the older Chinese DS (LCSC copy of C3035748) p.5 and the LCSC listing say −20…70 °C. Taken from the newer V3C.
* CH340X MSOP-10 pin numbers come from the CN DS application figure (p.10); the pin table only gives the ESSOP-10 (CH340K) column. They match the KiCad `CH340X` symbol. Unused RTS#/CTS#/TNOW pins left open ("unused I/O pins can be dangled", DS V3C p.4).
* XKB RJ45 footprint generated by easyeda2kicad (EasyEDA names it X12ADHWA3DY1027); pin / shield / peg grid checked against the drawing, not against a physical part. Panel cut-out position not checked.
* **LAYOUT GATE (review R3-23): verify RJ45 pin 1 on a physical XKB jack or a 1:1 print before ordering** — a mirrored footprint is harmless for RS-485 / GND (1/8, 2/7, 3/6 symmetric) but swaps CANH / CANL (4 ↔ 5) on J601, J603, J604.
* USB4105-GF-A: LCSC stock 0, JLC stock 4,375 (2026-11-23); footprint is KiCad's, named for the part, not re-measured.
* CA-IS3082WX supply current while driving 54 Ω and CA-IS3050CW RXD state with VCC2 off (D U6/U7) — not in the extracted pages.
* PSM712 clamp levels vs the CA-IS3082 bus abs max −8 / +13 V (DS p.7): PSM712 clamps at 11 V / 17 V @ 34 A (−7 V direction) and 19 V / 30 V @ 30 A (+12 V direction) (PSM712 DS p.2). The 10 R anti-surge resistors R630–R633 now limit the residual current into the pins (review R3-07); the ESR10 single-pulse limit for this case was not computed — verify at the EMC test.
* Shield RC (1 nF 2 kV ∥ 1 MΩ), CMC need and 4.7 nF split value: EMC test (D §3.5).
* Fault dissipation of the 0603 60.4 R legs with CANH/CANL shorted to 24 V (P3 F7) not covered.

## Owner questions that remain
1. CH340X instead of CH340C (−40 °C by the newer datasheet only) — OK?
2. USB-C GCT USB4105 (+$0.49) vs the cheaper Kinghelm KH-TYPE-C-16P (C709357, −40…85 °C listing, 111 k stock, $0.06) which needs a generated footprint — keep GCT?

## Firmware notes
* FDCAN TX pins are pulled up (recessive) during reset; RS-485 DE has the transceiver's internal PD, so all four buses are silent while the MCU is in reset.
* RE is tied low: the MCU receives its own RS-485 frames (echo check; discard them in the driver).
* Inverter port runs 500 kbit/s classic CAN; FD only on the link (D-47).
* Ignore `RS485_*_RX` / `CAN_*_RX` while `EN_ISO` is off and for ≥ 25 ms after `EN_ISO` goes high (receiver state with `+5V_ISO` down not specified, R3-24; v1.1 supply start-up = TPS22918 1.06 ms + SN6505B soft-start delay ≤ 18 ms + LDO, sheet 01 §12.5).
* User manual: termination DIP poles 1 and 2 must always be set together (R3-14).

## Review disposition (review R3, 2026-11-23)
| Finding | Disposition | Change |
|---|---|---|
| R3-07 no current limit between RS-485 TVS and the −8/+13 V pins | **fixed** | R630, R631 (U603 A/B), R632, R633 (U604 A/B) = 10 R 5 % 0805 anti-surge ROHM ESR10EZPJ100 **C2073902** (live-verified 2026-11-23: 53,400 LCSC / 53,409 JLC, Extended, 0.4 W, −55…+155 °C; anti-surge series, ESR DS p.1); new nets `06_U603_A/B`, `06_U604_A/B` |
| R3-14 split-termination poles must switch together | **fixed (text)** | SW601 / SW602 descriptions, on-sheet note and PCB silk "1+2 = CAN TERM, switch together"; manual note. No part change |
| R3-23 RJ45 pin-1 orientation | **recorded as layout gate** | Unverified items: check pin 1 on a physical jack / 1:1 print before ordering |
| R3-24 receiver state with `EN_ISO` = 0 | kept as firmware rule | – |
| R3-16 UCPD dead-battery on PA9/PA10 | no sheet-06 change | firmware rule is on sheet 03 |
| P5C-03 RS485_*_DE float while the MCU is in reset / boot | **fixed** | R634 (RS485_INV_DE), R635 (RS485_LINK_DE) 10 k 1 % 0603 to `GND_PWR` at U603 / U604, LCSC **C25804** reused (already in the BOM: R745 / R747 / R756, sheet 07) |
| P5C-05 no mounting holes on the control board | **fixed** | MH601–MH604 M3 plated (`Mechanical:MountingHole_Pad`, `MountingHole_3.2mm_M3_Pad_Via`, same as MH701), pad on `CHASSIS`, not in BOM; block "Mounting holes" with the note "MH on CHASSIS, standoffs to the power board / Al plate; MH601 next to the RJ45 row" |
