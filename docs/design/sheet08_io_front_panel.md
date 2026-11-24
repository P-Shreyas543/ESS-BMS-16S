# Sheet 08 — IO / Front Panel (control board, refs 8xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 08). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 72 refs = 57 fitted (of which 5 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 15 DNP; 28 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

Board: control. Parts: **72** (57 fitted, 15 DNP; TP801/TP802 and TP804–TP806 are `in_bom no`). Project symbol `Automotive_ESS_BMS:TCA9539PWR` (KiCad 10 `Interface_Expansion` has no TCA9539). The photoMOS dry contacts U803/U804 and J802 are on **this sheet** (Block "Dry contacts + DI_AUX1 (J802)"); sheet 05 keeps only the EXT_OUT and fan parts.

## 1. Blocks (left → right)

| Box | Parts | Key number for the on-sheet note |
|---|---|---|
| **I2C2 expanders U801 / U802** | U801 TCA9539 @0x74 (A1 = A0 = GND), U802 TCA9539 @0x75 (A0 = +3V3), RESET of both = `MCU_NRST`; C801/C802; R801/R802 2.2 k; R809–R811 470 k read-back series; R825–R827 100 k enable PDs; R831–R833 spare ties; TP801/TP802, TP803, TP804–TP806 on EN_12V / EN_ISO / EN_ESP | Every MCU reset (U302, IWDG, SWD, NRST) holds both expanders in reset: all 32 ports return to inputs and the pull resistors define the safe state (SCPS202C p.18 §8.3.2; tW ≥ 6 ns, tRESET ≤ 400 ns, p.8). I2C Fm: Cb ≤ 160 pF with 2.2 kΩ (calc); sink 1.3 mA < 3 mA (p.6). Ports 5 V tolerant, VIH ≤ 5.5 V at any VCC, VI abs max 6 V (p.1, p.5) |
| **Pack address DIP** | SW801, R803–R806 10 k PU | closed = 0; address = inverted 4-bit word |
| **SOC / RUN / ALM LEDs** | D801–D804, D807 (green, +5V via 1 k), D805/D806 + R816/R817 (DNP, D-30), R834/R835 100 k PU, D808 (red, +3V3 via 680 Ω) | green 1.4…2.4 mA; HIGH port (3.3 V) leaves 1.7 V < VF min 2.6 V → off (P-10). U802 sink ≤ 14 mA total vs IOL 18 mA/pin at Tj 85 °C (SCPS202C p.5) |
| **Wake button** | SW802 → R837 100 Ω → `WAKE_BTN_RAW`; D817 ESD at SW802 (fitted); R824 220 kΩ `WAKE_BTN_N` → AFE_REG1 | 15 µA from AFE_REG1 while pressed (calc). 0.5 µA leakage at the Q101 gate drops 0.11 V < VGS(th) min 0.5 V (R2-18) |
| **Buzzer (DNP)** | BZ801 on +5V, Q801, R820, R821, D810 | 119 mA peak, ≤ 60 mA at 50 % |
| **Dry contacts + DI_AUX1 (J802)** | U803/U804 GAQY212GS, R822/R823 220 Ω, D811/D812 SMAJ36CA, J802, R807 10 k PU, R838 2.2 k 1206 in series with J802 pin 5, R808 1 k, C803, D813, R836 100 Ω 1206 in the pin-6 return | IF 5.5 mA min vs IF(on) ≤ 2 mA (GAQY p.2). R836: closed contact reads 27 mV, DI node 0.62 V via R838 2.2 k; a field wire on PACK− carries ≤ 1.6 mA at 800 A (calc) |
| **Front-panel connector J801 (DNP)** | J801, F801/F802 PTC 100 mA in +5V / +3V3 (DNP), D814–D816 ESD (DNP) | J801: 1 +5V via F801, 2 +3V3 via F802, 3 GND, 4 EXP_SCL, 5 EXP_SDA, 6 WAKE_BTN_RAW, 7 LED_ALM, 8 GND, MP NC |

## 2. TCA9539 pin-out (verified) and port map

**Source:** TI TCA9539 datasheet SCPS202C (May 2016), downloaded from ti.com 2026-11-23. PW TSSOP-24 pin functions p.3–4: 1 INT, 2 A1, **3 RESET** (active low), 4–11 P00–P07, 12 GND, 13–20 P10–P17, 21 A0, 22 SCL, 23 SDA, 24 VCC. This is identical to the TCA9535 except pin 3 (A2 → RESET).
- Address 1110 1 A1 A0 = 0x74–0x77 (p.21 Table 2).
- 5 V tolerant I/O (p.1); VIH for P-ports and RESET 0.7 VCC … 5.5 V (p.5 ROC); VI / VO abs max −0.5…6 V (p.5).
- IIH/IIL ±1 µA, RESET input ±1 µA (p.6); TA −40…85 °C (p.5).
- RESET low holds the registers and the I2C state machine in default, so ports = inputs (p.18).
- LCSC **C131972** TCA9539PWR, TI, TSSOP-24: LCSC 9,821 / JLC 9,840, Extended (live 2026-11-23).

| U801 @0x74 | Pin | Net | Notes |
|---|---|---|---|
| P00–P03 | 4–7 | DIP_ADDR0..3 | 10 k PU, SW801 to GND |
| P04 / P05 | 8 / 9 | 08_FLT_DSG_RB / 08_FLT_CHG_RB ← R809 / R810 470 k ← AFE_FLT_DSG_N / AFE_FLT_CHG_N | read-back only; fast path KILL_N on PB4 |
| P06 | 10 | DI_AUX1 | J802 pin 5 via R808 1 k |
| P07 | 11 | DFETOFF_RB ← R811 470 k ← AFE_DFETOFF | gate-kill self-test read-back |
| P10 / P11 | 13 / 14 | EN_ISO / EN_ESP | R825 / R826 100 k PD here (only PD on each net) |
| P12 / P13 | 15 / 16 | ESP_EN / ESP_BOOT | sheet 09 |
| P14 | 17 | **FAN_EN** | new interface signal to sheet 05; default off via sheet 05 R501 1 k + R502 100 k gate PD |
| P15 | 18 | BAL_EXT_EN | PD R270 on sheet 02 |
| P16 / P17 | 19 / 20 | DRY1 / DRY2 | photoMOS LED cathodes |
| RESET / INT | 3 / 1 | MCU_NRST / NC | |

| U802 @0x75 | Pin | Net | Notes |
|---|---|---|---|
| P00–P03 | 4–7 | LED_SOC1..4 | |
| P04 / P05 | 8 / 9 | LED_RUN / LED_ALM | |
| P06 / P07 | 10 / 11 | LED_SOC5 / 6 | DNP LEDs, R834/R835 100 k PU |
| P10–P13 | 13–16 | MUX_S0..2, MUX_INH | sheet 10 (PDs / PU there) |
| P14 | 17 | EN_12V | R827 100 k PD here (only PD on the net) |
| P15–P17 | 18–20 | 08_U802_P15..17 | spare, R831–R833 10 k to GND |
| RESET / INT | 3 / 1 | MCU_NRST / NC | |

Green LEDs on +5V with VCC = 3.3 V are allowed by p.1 / p.5 (VIH ≤ 5.5 V, VI ≤ 6 V). While a port is an input (power-up or reset), its node floats at ≈ 5 V − VF(leakage), below 5.5 V. The datasheet notes "for voltages applied above VCC, an increase in ICC will result" (p.5); that applies only during reset.

MCU_NRST load: + 2 × 1 µA RESET leakage (p.6), so the NRST high level is unchanged (sheet 03 calc).

## 3. Test points
TP801 EXP_SCL, TP802 EXP_SDA (THT pads), TP803 GND_PWR hook, TP804 EN_12V, TP805 EN_ISO, TP806 EN_ESP (THT pads, P5C-06).

## 4. DNP list
- D805, D806, R816, R817: 6-LED bar (D-30).
- BZ801, Q801, R820, R821, D810: buzzer (D-31).
- J801, F801, F802, D814, D815, D816: front panel (D-35).

## 5. AGENT DECISIONS (owner may overrule)

| # | Question | Choice | Why | Source |
|---|---|---|---|---|
| 4 (bom_G3 §8) | Buzzer | QMB-09B-05 C161819 on +5V, DNP | −40…85 °C; off the +3V3 LDO | QMB spec p.2 |
| 5 | LED supply | green on +5V, red ALM + photoMOS on +3V3 | P-10 | SCPS202C p.1, p.5 |
| 7 | Dry contacts / DI_AUX1 | ≤ 30 V working; DI_AUX1 = potential-free contact between J802 pins 5 and 6 | SMAJ36CA VC < 60 V | GAQY p.2 |
| 8 | J801 | PicoBlade C293349, DNP | −40…105 °C | P-13 |
| 10 | AFE_FLT_* / DFETOFF read-back | keep, **470 k series** (R809–R811); the node pull-downs are the 100 k parts on sheets 02 / 07 | a stuck output-high port can only lift a Hi-Z = fault node to 0.58 V (calc) | review R3-04 |
| P-13 | DIP, button | C40736, C221895 | −40 °C | P-13 |
| – | Expander part | **TCA9539PWR C131972** with RESET = MCU_NRST | outputs return to the safe state on every MCU reset | review R3-01 (accepted) |
| – | Enable PDs | R825 EN_ISO, R826 EN_ESP, R827 EN_12V (100 k) here; BAL_EXT_EN keeps R270 (sheet 02) | sheet 01 does not fit them | integration fix 2026-11-23 |
| – | FAN_EN port | **U801 P14** (spare per §8), **no PD on this sheet**: TCA9539 RESET → input, and sheet 05 R501 1 k + R502 100 k to GND defines the net | one PD per net | integration 2026-11-23; sheet 05 netlist |
| – | Unused ports | 10 k to GND (R831–R833), 100 k PU on DNP LED ports | defined input level | – |
| – | J801 pins 7 / 8 / MP | LED_ALM / GND_PWR / NC | – | – |
| – | R824 | **220 kΩ**, kept here; sheet 01 has no other pull on WAKE_BTN_N (sheet 01 netlist: only the Q101 gate) | Q101 / PC13 leakage margin | review R2-18 |
| – | I2C2 pull-ups | 2.2 kΩ (P3 value) | J801 extends the bus | bom_G3 F10 |

## 6. New interface signals

| Name | From → to | Port | Level / default | Requested by |
|---|---|---|---|---|
| `FAN_EN` | U801 → sheet 05 Q501 gate (R501 1 k) | U801 P14 (pin 17) | 3.3 V push-pull, high = fan on; off in reset (port Hi-Z + sheet 05 R502 100 k PD) | sheet 05 / integration 2026-11-23 |

## 7. B2B change requests
None.

## 8. Firmware rules
1. After every MCU reset the expanders are already in their default state (RESET = MCU_NRST). Write the output registers before switching ports to output.
2. LEDs off = port HIGH or input; SOC5/6 and spares stay inputs or LOW.
3. (removed P5C-01: no hardware ALM option any more.)
4. DIP address = NOT DIP_ADDR3..0. DRY1/2 on = port LOW. FAN_EN on = HIGH.
5. Expander addresses are now 0x74 / 0x75.

## 9. Review disposition (R3_mcu_io_comms.md, R2_power_tree_afe.md)

| Finding | Disposition | Changed refs |
|---|---|---|
| R3-01 MAJOR: expander outputs latch through MCU reset | **Applied**: TCA9539PWR C131972, RESET (pin 3) = MCU_NRST; pin-out verified SCPS202C p.3–4; addresses 0x74 / 0x75; port map unchanged except P14 = FAN_EN | U801, U802 (part, symbol, pin 3 net) |
| R3-04: 10 k read-back can override Hi-Z = fault | **Applied**: 470 k (C23178) | R809, R810, R811 |
| R3-10: wake button without ESD | **Applied, part only partly verified**: D817 PESD5V0S1BA at SW802, always fitted, + R837 100 Ω. ≤ 10 nA at 85 °C could not be proven (Nexperia gives 100 nA max at 25 °C and only a relative curve, Fig.6); measure WAKE_BTN_RAW leakage at 85 °C at bring-up | D817 (new), R837 (new), SW802 pin 1 net |
| R3-11: GND_PWR on a field terminal | **Applied**: R836 100 Ω 1206 (C17901) in series with J802 pin 6 | R836 (new), J802 pin 6 net |
| R3-15: J801 rails without a limit | **Applied**: F801 / F802 PTC 100 mA (C20975), DNP with J801 | F801, F802 (new), J801 pins 1/2 nets |
| R2-18: 1 MΩ wake pull-up too weak | **Applied**: 220 kΩ (C22961) | R824 |
| Stale text (R827 / 470 k) | **Fixed**: decision 10 now states 470 k series and 100 k node PDs on sheets 02 / 07 | – |
| P5C-01: hardware ALM LED option not wanted | **fixed**: D809, R829 and net 08_ALMHW_K deleted (KILL_N no longer on this sheet) | D809, R829 |
| P5C-04: field input DI_AUX1 needs series protection | **fixed**: R838 2.2 k 1206 (C17948, new, live-verified 2026-11-24) between J802 pin 5 (new net 08_DI_IN) and the R807 / D813 / R808 node; closed contact node 0.62 V < VIL 0.99 V, wetting 0.27 mA (calc) | R838 (new), J802 pin 5 net |
| P5C-06: probe access on power-sequencing enables | **fixed**: TP804 EN_12V, TP805 EN_ISO, TP806 EN_ESP THT pads (in_bom no) next to R827 / R825 / R826 | TP804–TP806 (new) |
| R3-02, -03, -05, -06, -07, -13, -14 | not on this group's sheets (01 / 05 / 06 / 09) | – |

## 10. Unverified items
* D817 leakage at 85 °C (see R3-10).
* GAQY212GS land p.4 and the buzzer pin drawing are images (data from bom_G3, matches the easyeda2kicad output).
* QMB-09B-05 reliability tests only go to −30 °C (spec p.4).
* J801 Molex drawing not opened; J802 hole diameter not legible.

## 11. Owner questions remaining
* D-31 buzzer: fit or DNP? (LED_ALM_HW option removed, P5C-01.)

## 12. LCSC verification (live 2026-11-23: LCSC product API + JLCPCB parts API)

| LCSC | MPN | Manufacturer | LCSC stock | JLC stock | JLC type | Refs |
|---|---|---|---|---|---|---|
| C2128 | 1N4148WS | JSCJ | 1,040,600 | 3,222,044 | Basic | D810 |
| C2150 | SS8050(RANGE:200-350) | JSCJ | 2,005,350 | 3,219,314 | Basic | Q801 |
| C2286 | KT-0603R | Hubei KENTO Elec | 5,655,200 | 8,307,892 | Basic | D808 |
| C2297 | KT-0805G | Hubei KENTO Elec | 2,052,500 | 2,990,992 | Basic | D801, D802, D803, D804, D805, D806, D807 |
| C4190 | 0603WAF2201T5E | UNI-ROYAL | 1,294,000 | 4,065,728 | Basic | R801, R802 |
| C7246 | WJ15EDGRC-3.81-06P-14-00A | KANGNEX | 13,460 | 15,548 | Extended | J802 |
| C14663 | CC0603KRX7R9BB104 | YAGEO | 227,800 | 52,261,571 | Basic | C801, C802 |
| C17948 | 1206W4F2201T5E | UNI-ROYAL | 114,900 | 191,611 | Extended | R838 (new P5C-04, live 2026-11-24: LCSC product API + JLC parts API; 2.2 kΩ 1 % 250 mW 200 V, −55…155 °C) |
| C17901 | 1206W4F1000T5E | UNI-ROYAL | 791,600 | 1,738,059 | Basic | R836 |
| C19224 | PESD5V0S1BA,115 | Nexperia | 132,915 | 139,480 | Extended | D813, D814, D815, D816, D817 |
| C20975 | SMD0805P010TF | RUILON | 75,060 | 76,478 | Extended | F801, F802 |
| C21190 | 0603WAF1001T5E | UNI-ROYAL | 13,287,100 | 39,696,104 | Basic | R808, R812, R813, R814, R815, R816, R817, R818, R820 |
| C22775 | 0603WAF1000T5E | UNI-ROYAL | 3,671,300 | 12,718,209 | Basic | R837 |
| C22961 | 0603WAF2203T5E | UNI-ROYAL | 513,800 | 871,759 | Basic | R824 |
| C22962 | 0603WAF2200T5E | UNI-ROYAL | 480,800 | 2,264,143 | Basic | R822, R823 |
| C23178 | 0603WAF4703T5E | UNI-ROYAL | 325,400 | 948,176 | Basic | R809, R810, R811 |
| C23228 | 0603WAF6800T5E | UNI-ROYAL | 416,500 | 1,286,490 | Basic | R819 |
| C25803 | 0603WAF1003T5E | UNI-ROYAL | 3,381,000 | 12,793,913 | Basic | R821, R825, R826, R827, R834, R835 |
| C25804 | 0603WAF1002T5E | UNI-ROYAL | 0 | 42,081,465 | Basic | R803, R804, R805, R806, R807, R831, R832, R833 |
| C40736 | DSHP04TSGET | YE | 19,876 | 23,034 | Extended | SW801 |
| C57112 | 0603B103K500NT | FH | 0 | 4,483,923 | Basic | C803 |
| C87270 | SMAJ36CA/TR13 | Brightking | 312,880 | 330,224 | Extended | D811, D812 |
| C131972 | TCA9539PWR | TI | 9,821 | 9,840 | Extended | U801, U802 |
| C161819 | QMB-09B-05 | Huaneng | 23,025 | 23,027 | Extended | BZ801 |
| C221895 | PTS810SJG250SMTRLFS | C&K | 12,470 | 12,460 | Extended | SW802 |
| C293349 | 532610871 | MOLEX | 44,625 | 44,628 | Extended | J801 |
| C5199801 | RH-5001 | ronghe | 97,335 | 99,458 | Extended | TP803 |
| C7435107 | GAQY212GS | SUPSiC | 102,042 | 120,392 | Extended | U803, U804 |

Loose item: J802 mating plug WJ15EDGK-3.81-06P-14-00A (KANGNEX) **C7247**, JLC 14,481 / LCSC 14,169, Extended (live 2026-11-23); order with the PCBA.
