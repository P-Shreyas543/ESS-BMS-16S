# Sheet 10 — Memory / Sensors (control board, refs 1001-1099) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 10). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 37 refs = 37 fitted (of which 6 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 0 DNP; 11 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

Board: control. Parts: **37** (all fitted; TP1001–TP1006 are `in_bom no`). Project symbol: `Automotive_ESS_BMS:TMUX1308PW`. Stock symbols: U1001 `Memory_EEPROM:25LCxxx` (same SOIC-8 SPI pin-out as FM25V02A: 1 CS, 2 SO, 3 WP, 4 VSS, 5 SI, 6 SCK, 7 HOLD, 8 VDD), U1002 `Memory_Flash:W25Q32JVSS` (= GD25Q64E SOP8 pin-out, GD25Q64E DS p.6 Table 1).

## 1. Blocks (left → right)

| Box | Parts | Key number for the on-sheet note |
|---|---|---|
| **SPI1 memories FRAM + flash** | U1001 FM25V02A (32 KB F-RAM), U1002 GD25Q64ESIG (8 MB NOR), C1001/C1002, R1001/R1002 4.7 k CS PUs, R1003/R1004 33 Ω SCK / MOSI series (PCB: at U301), TP1001–TP1005, TP1007 GND hook | shared bus ≤ 20 MHz, mode 0 (FRAM 40 MHz max, 001-90865 p.1; flash 133 MHz, GD25Q64E). CS PU 4.7 k vs ROM SPI1_NSS pull-down (RPD min 25 k, DS12712 p.131): 3.3 × 25/29.7 = 2.78 V > VIH 2.31 V → deselected (calc; review R3-09). WP / HOLD tied to +3V3 (FRAM WP "must be tied to VDD if not used", 001-90865 p.3) |
| **NTC mux + MCU NTC inputs** | U1003 TMUX1308 on +3V3_A, C1003; channel bias R1006–R1010 10 k from +3V3_A + C1004–C1008 100 nF; RT1001 NTC_AMB; S5/S6 to GND; S7 = 50 % reference R1011/R1012; R1005 100 k MUX_INH PU; R1014–R1016 100 k MUX_S PDs; C1009 10 nF at PB14; NTC_SHUNT bias R1013 + C1010 at PB2; TP1006 | settle after a channel change: charge share 10 nF / 110 nF = 9 %, τ = (5 k + 0.35 k) × 110 nF = 0.59 ms, to ½ LSB at 12 bit ln(0.09 × 8192) × τ ≈ 3.9 ms → firmware waits **≥ 5 ms** (calc). Mux leakage (7 × 25 + 45 nA) × 5 kΩ ≈ 1.1 mV ≈ 0.04 K at 25 °C (calc, SCDS426E p.9). +3V3_A load at 25 °C: 7 × 3.3 V / 20 kΩ = 1.2 mA (calc; ARCH §4.2 budget 1.5 mA) |

## 2. Pin maps

| U1003 TMUX1308 | Pin | Net | Source / note |
|---|---|---|---|
| S0 | 13 | NTC_PACK4 | pack NTC 4, J202 pins 7/8 (sheet 02, ESD there) |
| S1 | 14 | NTC_PACK5 | J203 (DNP) on sheet 02; reads ≈ 3.3 V = "absent" when not fitted |
| S2 | 15 | NTC_PACK6 | J203 (DNP) |
| S3 | 12 | NTC_BAL | RT201 among the balance resistors (sheet 02) |
| S4 | 1 | NTC_AMB | RT1001 on this sheet (board edge) |
| S5 / S6 | 5 / 2 | GND_PWR | unused inputs to GND (SCDS426E p.26); firmware expects 0 |
| S7 | 4 | 10_MUX_REF | 50 % ratiometric check of bias / mux / ADC |
| D | 3 | NTC_MUX | → U301 PB14 (ADC1_IN5), C1009 10 nF |
| A0 / A1 / A2 | 11 / 10 / 9 | MUX_S0 / S1 / S2 | from U802 P10–P12 (sheet 08, TCA9539: inputs after POR and every MCU reset); 100 k PD here |
| ~EN | 6 | MUX_INH | from U802 P13; 100 k PU → all off (SCDS426E p.26 Table 9-1) |
| N.C. | 7 | NC | not internally connected (SCDS426E p.4) — symbol pin typed no_connect, no flag needed |
| VDD / GND | 16 / 8 | +3V3_A / GND_PWR | VDD = the NTC bias rail, so signals never exceed VDD (SCDS426E p.7) |

Memories: `FRAM_CS_N` (U301 PA4) → U1001.1, `FLASH_CS_N` (PC7) → U1002.1, `SPI1_MISO` (PA6) → both pin 2, `SPI1_SCK` (PA5) → R1003 → `10_SPI_SCK` → pin 6, `SPI1_MOSI` (PA7) → R1004 → `10_SPI_MOSI` → pin 5; pins 3, 7, 8 = +3V3, pin 4 = GND_PWR.

## 3. Test points
THT pads TP1001 10_SPI_SCK, TP1002 10_SPI_MOSI, TP1003 SPI1_MISO, TP1004 FRAM_CS_N, TP1005 FLASH_CS_N, TP1006 NTC_MUX (ADC input); TP1007 GND_PWR hook. No pads on the channel filter nodes (high-impedance NTC dividers).

## 4. DNP list
None. (J203 / NTC 5–6 are DNP on sheet 02; their bias and filter parts here stay fitted so an absent sensor reads open.)

## 5. AGENT DECISIONS (owner may overrule)

| Question | Choice | Why | Source |
|---|---|---|---|
| Mux part | **TMUX1308PWR C970231** (P-11) | specified at 3.3 V (RON ≤ 350 Ω, −40…85 °C), pin-compatible with CD4051 (pin 7 N.C. instead of VEE) | P-11; SCDS426E p.4, p.9 |
| Flash part | **GD25Q64ESIG C2685734 primary** (P-11); **alternate MX25L6433FM2I-08G C706695** (JLC 1,169) | W25Q64JVSSIQ C179171 is down to 51 at JLC / 3 at LCSC (2026-11-23); firmware must accept both JEDEC IDs | live check |
| Mux supply | **+3V3_A** | NTC channels are biased from +3V3_A; keeps VS ≤ VDD | SCDS426E p.7 |
| NTC_BAL sensor | **RT201 on sheet 02** (bom_G3's RT1002 dropped); bias R1009 + filter here | one physical part; bias belongs to the MCU ADC side (bom_G2 Q-4) | bom_G2 RT201 |
| NTC_SHUNT bias | **R1013 10 k + C1010 100 nF on the control board, here**; sheet 04 drops R417 (confirmed at integration 2026-11-23) | ratiometric to VREF+, and an unplugged B2B reads open (fault) instead of a valid temperature | bom_G3 §7 |
| Mux logic pins at POR | **R1014–R1016 100 k PDs on MUX_S0..2** (new vs bom_G3) | U802 ports are inputs after POR; floating CMOS select pins draw current (SCDS426E p.26) and would be undefined inputs (TCA9539 SCPS202C p.3: inputs at power-on and after RESET) | datasheets |
| C311 supercap | see sheet 03 decision 6 | – | – |

## 6. New interface signals
None (`NTC_PACK4..6`, `NTC_BAL`, `NTC_SHUNT`, `NTC_MUX`, `MUX_S0..2`, `MUX_INH`, `SPI1_*`, `FRAM_CS_N`, `FLASH_CS_N` are ARCHITECTURE §10 names; `NTC_AMB` is §10 and stays on this sheet).

## 7. B2B change requests
None (`NTC_SHUNT` on pin 16, `+3V3_A` on pin 18 as in the contract map).

## 8. Firmware rules
1. Mux: drive MUX_INH low only while sampling; wait ≥ 5 ms after each MUX_S change; S5/S6 must read ≈ 0, S7 ≈ 50 % (self-test).
2. SPI1 ≤ 20 MHz, mode 0; both CS high before any transfer; flash JEDEC ID check (GD25Q64E or MX25L6433F).
3. FRAM: write SOC / counters on PVD brown-out (NoDelay writes, 001-90865 p.1).

## 9. Unverified / watch items
* **Stock watch (live 2026-11-23):** TMUX1308PWR **644** at JLC (bom_G3 saw 5,024); FM25V02A-GTR **1,063** (was 7,255). Both meet the ≥ 500 rule today. Fallbacks seen in the JLC API: TMUX1308AQPWRQ1 C39041466 (527, same TSSOP-16 pin-out, DS not opened), CD4051BQPWRQ1 C555142 (2,232, no RON at 3.3 V); FRAM MB85RS256BPNF-G-JNERE1 C8742 (JLC 17,366; LCSC product API returned no record; DS not opened, pin compatibility assumed from the standard SOIC-8 SPI F-RAM pin-out — verify before use).
* MX25L6433FM2I-08G is listed as "SOP-8-200mil": check its land against `SOIC-8_5.3x5.3mm_P1.27mm` before using it as the alternate.
* FM25V02A SOIC-8 pin-out figure (001-90865 p.3) is an image; pin order taken from bom_G3's reading and the "direct hardware replacement for serial flash and EEPROM" statement (p.1).

## 10. Owner questions remaining
None for this sheet.

## 11. LCSC verification (live 2026-11-23: LCSC product API for MPN / manufacturer / stock, JLCPCB parts API for JLC stock and Basic/Extended)

| LCSC | MPN | Manufacturer | LCSC stock | JLC stock | JLC type | Refs |
|---|---|---|---|---|---|---|
| C13564 | NCP18XH103F03RB | muRata | 218,390 | 228,475 | Extended | RT1001 |
| C14663 | CC0603KRX7R9BB104 | YAGEO | 227,800 | 52,261,571 | Basic | C1001, C1002, C1003, C1004, C1005, C1006, C1007, C1008, C1010 |
| C23140 | 0603WAF330JT5E | UNI-ROYAL | 1,107,200 | 3,596,660 | Basic | R1003, R1004 |
| C23162 | 0603WAF4701T5E | UNI-ROYAL | 5,756,500 | 18,939,296 | Basic | R1001, R1002 |
| C25803 | 0603WAF1003T5E | UNI-ROYAL | 3,381,000 | 12,793,913 | Basic | R1005, R1014, R1015, R1016 |
| C25804 | 0603WAF1002T5E | UNI-ROYAL | 0 | 42,081,465 | Basic | R1006, R1007, R1008, R1009, R1010, R1011, R1012, R1013 |
| C57112 | 0603B103K500NT | FH | 0 | 4,483,923 | Basic | C1009 |
| C66029 | FM25V02A-GTR | Infineon/CYPRESS | 1,063 | 1,063 | Extended | U1001 |
| C970231 | TMUX1308PWR | TI | 500 | 644 | Extended | U1003 |
| C2685734 | GD25Q64ESIG | GigaDevice Semicon Beijing | 19,739 | 19,739 | Extended | U1002 |
| C5199801 | RH-5001 | ronghe | 97,335 | 99,458 | Extended | TP1007 |

## 12. Review disposition (R3_mcu_io_comms.md)

| Finding | Disposition | Changed refs |
|---|---|---|
| R3-09 FRAM CS margin in ROM mode | **Applied**: 4.7 kΩ (C23162) on both CS lines | R1001, R1002 |
| R3-01 (TCA9539 RESET) | applied on sheet 08; MUX_S PDs / MUX_INH PU here now also define the mux after every MCU reset | – |
| NTC_SHUNT bias ownership | stays here (R1013 + C1010); sheet 04 drops R417 (integration) | – |
