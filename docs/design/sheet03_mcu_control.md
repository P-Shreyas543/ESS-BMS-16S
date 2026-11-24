# Sheet 03 — MCU Control (control board, refs 3xx) — design note

Schematic v1, 2026-11-24. Drawn sheet: [`docs/schematic/control_board_v1.pdf`](../schematic/control_board_v1.pdf). Parts: [`docs/bom/bom_schematic_v1.csv`](../bom/bom_schematic_v1.csv) (rows with Sheet = 03). Overview, B2B pin map, bring-up gates and firmware rules: [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md). Reviews: [spec review R1–R3](../reviews/spec_review.md), [final schematic review P5](../reviews/schematic_review_p5.md).

**Count:** 37 refs = 37 fitted (of which 9 copper-only, not in the BOM: test pads, net ties, mounting holes, solder jumpers) + 0 DNP; 15 unique LCSC numbers.

Tags: **DS** = datasheet page, **calc** = own arithmetic, **est.** = engineering estimate. A / B / C / D § = sections of `docs/architecture/` (A power stage, B power tree, C AFE, D MCU / comms / IO); ARCH = `docs/ARCHITECTURE.md`; P-xx / D-xx = owner decisions (`PROJECT.md` §5, ARCH §14); R1-xx / R2-xx / R3-xx = spec-review findings, P5-xx / P5C-xx = final-review findings. "Interface contract" = the net-naming and B2B rules in `docs/SCHEMATIC_V1.md`. "AGENT DECISION (owner may overrule)" marks a choice taken during the spec work under delegation from the owner; it stands until the owner overrules it.

Board: control. Symbol for U301: stock `MCU_ST_STM32G4:STM32G473RCTx` (64 pins, pin number = LQFP-64 pad = DS12712 Table 12 LQFP64 column, checked pin by pin). Parts: **37** (all fitted; 7 THT probe pads and 2 solder jumpers are `in_bom no`). Revised after review R3 (see §13).

Sheet rule (instruction §6): this sheet holds only the MCU, its decoupling, clocks, reset, boot and debug. Every pull resistor, series resistor or filter on an MCU signal lives on the peripheral's sheet (list at the end).

## 1. Blocks (left → right)

| Box | Parts | Key number for the on-sheet note |
|---|---|---|
| **MCU core + decoupling** | U301, C301–C305 (VDD), C306/C307 (VDDA), C308/C309 (VREF+), C310 (VBAT), R304/R305/R306 1 MΩ PDs on OC_TRIP_N / KILL_N / ISENSE_OUT, TP301 (GND hook), TP304 (VBAT_MCU), C318 1 nF on ISENSE_OUT (P5-08), TP306 / TP307 / TP308 THT pads on PWR_HOLD / FET_EN / KILL_N (P5C-06) | VDD 4 × 100 nF + 4.7 µF, VDDA 10 nF + 1 µF, VREF+ 100 nF + 1 µF (DS12712 p.77 Fig.15). VDDA = VREF+ = `+3V3_A` (ferrite from `+3V3`, sheet 01) |
| **Clocks HSE / LSE** | Y301 + C312/C313, Y302 + C314/C315 | HSE: CL = 33 pF/2 + 3…5 pF = 19.5…21.5 pF vs 20 pF; gm_crit = 4·80 Ω·(2π·8 MHz)²·(5+20 pF)² = 0.51 mA/V vs Gm 1.5 mA/V (DS12712 p.120) → ×2.9 (calc). LSE: gm_crit = 4·70 kΩ·(2π·32.768 kHz)²·(1+9 pF)² = 1.19 µA/V vs Gmcritmax 2.7 µA/V at LSEDRV = 11 (DS12712 p.122 Table 45) → ×2.3 (calc) |
| **Reset + watchdog** | U302 TPS3828-33 (open drain), R302 10 k PU, C317 100 nF, C316, JP302 WDI jumper (normally closed), TP302 (MCU_NRST), TP305 (03_WDI_SUP, U302 side) | Reset 2.93 V, td 120–300 ms, WDT 0.9–2.5 s (SLVS165G p.2, p.6). NRST high level with the power-board fail-safe PD: R302 ∥ RPU(min 25 k) = 7.1 k; PD ≥ 100 k → ≥ 3.08 V > VIH 0.7·VDD = 2.31 V (DS12712 p.136 Table 61; calc). Release τ = 7.1 k × 100 nF ≈ 0.7 ms. MCU_NRST also drives the RESET pins of U801/U802 (TCA9539, ±1 µA each, SCPS202C p.6): level unchanged |
| **Boot + SWD debug** | R303 10 k PD, JP301 BOOT0 → +3V3, TP303, J301 2 × 5 1.27 mm | BOOT0 = 0 → user flash; short JP301 → ROM bootloader (AN2606 pattern 14). J301: 1 VTref `+3V3`, 2 SWDIO, 3/5/9 GND, 4 SWCLK, 6 SWO, 7/8 NC, 10 nRESET |

## 2. U301 pin map (= ARCHITECTURE §8, no deviation)

All 64 pins are in the netlist; MCU nets are named exactly as in ARCHITECTURE §8 (this includes the sheet-local `OSC_*`, `OSC32_*`, `SWDIO`, `SWCLK`, `SWO`, `MCU_BOOT0`, `WDI`).

**AF verification** against DS12712 Rev 2 (downloaded from LCSC, C529361, 2026-11-23): function names from Table 12 (pin definitions, p.53–68), AF numbers from Table 13 (p.69–77).

| Pin | Port | Net | Function used | Table 12 (function present, I/O type) | Table 13 AF no. |
|---|---|---|---|---|---|
| 2 | PC13 | WAKE_BTN_N | EXTI13 / WKUP2 | ✓ WKUP2, FT; note 2: no current source (p.68) | GPIO |
| 7 | PG10-NRST | MCU_NRST | NRST | ✓ FT | – |
| 8–11 | PC0–PC3 | HEATER_EN, EXT_OUT1, EXT_OUT2, FAN_PWM | TIM1_CH1..CH4 | ✓ FT_a / TT_a / FT_a / TT_a | AF2 ✓ |
| 12 | PA0 | ISENSE_OUT | ADC12_IN1 + COMP3_INP | ✓ TT_a | analog |
| 13 / 14 / 17 | PA1 / PA2 / PA3 | RS485_INV_DE / TX / RX | USART2_RTS_DE / TX / RX | ✓ TT_a / FT_a / TT_a | AF7 ✓ |
| 18–21 | PA4–PA7 | FRAM_CS_N, SPI1_SCK/MISO/MOSI | GPIO, SPI1 | ✓ TT_a | AF5 ✓ |
| 22 | PC4 | EXP_SCL | I2C2_SCL | ✓ FT_fa | AF4 ✓ |
| 23 | PC5 | PG_5V | GPIO / EXTI5 (WKUP5) | ✓ TT_a | GPIO |
| 24 | PB0 | ISENSE_OUT | ADC1_IN15 + COMP4_INP | ✓ TT_a | analog |
| 25 | PB1 | RS485_LINK_DE | LPUART1_RTS_DE | ✓ TT_a | AF12 ✓ |
| 26 | PB2 | NTC_SHUNT | ADC2_IN12 | ✓ TT_a | analog |
| 30 / 33 | PB10 / PB11 | RS485_LINK_RX / TX | LPUART1_RX / TX | ✓ TT_a | AF8 ✓ |
| 34 / 35 | PB12 / PB13 | CAN_LINK_RX / TX | FDCAN2_RX / TX | ✓ TT_a | AF9 ✓ |
| 36 | PB14 | NTC_MUX | ADC1_IN5 | ✓ TT_a | analog |
| 37 | PB15 | BUZZER | TIM15_CH2 | ✓ TT_a | AF1 ✓ |
| 38 / 39 / 40 | PC6 / PC7 / PC8 | PWR_HOLD / FLASH_CS_N / OC_TRIP_N | GPIO (EXTI8) | ✓ FT_f | GPIO |
| 41 | PC9 | FAN_TACH | TIM3_CH4 | ✓ FT_f | AF2 ✓ |
| 42 | PA8 | EXP_SDA | I2C2_SDA | ✓ FT_a (Table 12 lists I2C2_SDA) | AF4 — Table 13 row PA8 is shifted in Rev 2 (shows I2C2_SMBA); the function is confirmed by Table 12 and AF4 by DS474 (D §2.1). Closed (review R3-18) |
| 43 / 44 | PA9 / PA10 | SVC_TX / RX | USART1_TX / RX | ✓ FT_fda | AF7 ✓ |
| 45 / 46 | PA11 / PA12 | CAN_INV_RX / TX | FDCAN1_RX / TX | ✓ FT_u | AF9 ✓ |
| 49 / 50 | PA13 / PA14 | SWDIO / SWCLK | SWD | ✓ FT_f, note 4 PU / PD (p.68) | AF0 |
| 51 / 60 | PA15 / PB7 | AFE_SCL / AFE_SDA | I2C1_SCL / SDA | ✓ FT_f | AF4 ✓ |
| 52 / 53 | PC10 / PC11 | ESP_RXD / ESP_TXD | UART4_TX / RX | ✓ FT / FT_f | AF5 ✓ (ROM: USART3 AF7) |
| 54 / 55 | PC12 / PD2 | WDI / OC_CLR | GPIO | ✓ FT | GPIO |
| 56 | PB3 | SWO | TRACESWO | ✓ FT | AF0 |
| 57 | PB4 | KILL_N | EXTI4 | ✓ FT_c (UCPD1_CC2) | GPIO |
| 58 | PB5 | AFE_RST_SHUT | GPIO | ✓ FT_f | GPIO |
| 59 | PB6 | FET_EN | TIM8_CH1 | ✓ FT_c (UCPD1_CC1) | AF5 ✓ |
| 61 | PB8-BOOT0 | MCU_BOOT0 | BOOT0 | ✓ FT_f, note 5 (p.68) | – |
| 62 | PB9 | AFE_ALERT | GPIO / EXTI9 | ✓ FT_f | GPIO |

Supply pins: 1 `VBAT_MCU`, 15/31/47/63 `GND_PWR`, 16/32/48/64 `+3V3`, 27 VSSA `GND_PWR`, 28 VREF+ / 29 VDDA `+3V3_A`. EXTI lines 4, 5, 8, 9, 13: no conflict. `ISENSE_OUT` on pins 12 and 24 is by design.

**Pin-map deviations from §8: none.** Value-only note: §8 lists 4.7 kΩ for the `EXP_SCL/SDA` pull-ups; the P3 BOM (bom_G3 F10) uses 2.2 kΩ (sheet 08, R801/R802).

## 3. External defaults of U301 nets drawn on other sheets (not here)
`WAKE_BTN_N` 1 MΩ to AFE_REG1 → sheet 08 R824. `EXP_SCL/SDA` 2.2 k → sheet 08. `FRAM_CS_N`/`FLASH_CS_N` 10 k PU, SPI 33 Ω series → sheet 10. `NTC_SHUNT` bias + 100 nF, `NTC_MUX` 10 nF → sheet 10. `BUZZER` 100 k PD → sheet 08. `VBAT_MCU` BAT54C OR → sheet 01 (D109). `PG_5V` PU, `PWR_HOLD` 1 MΩ PD → sheet 01. `AFE_SCL/SDA` 4.7 k + 100 Ω, `AFE_ALERT` 10 k, `AFE_RST_SHUT` 10 k PD → sheet 02. `FET_EN` 100 k PD → sheet 07. `HEATER_EN`, `EXT_OUT1/2`, `FAN_PWM` PDs, `FAN_TACH` PU + series → sheet 05 / 07. CAN TX 4.7 k PU → sheet 06. `ESP_RXD/TXD` 1 k series → sheet 09 (PCB: next to U301).

## 4. Test points
TP301 GND_PWR hook; THT pads TP302 MCU_NRST, TP303 MCU_BOOT0, TP304 VBAT_MCU, TP305 03_WDI_SUP (U302 side of JP302), TP306 PWR_HOLD, TP307 FET_EN, TP308 KILL_N (P5C-06). One pad per net; none on crystal nodes (probe capacitance).

## 5. DNP list
None. (C311 supercap and R301 removed, see decision 6.)

## 6. AGENT DECISIONS (owner may overrule)

| # | Question (bom_G3 §8) | Choice | Why | Source |
|---|---|---|---|---|
| 1 | U302 TPS3828 or TPS3823 + 1 k | **TPS3828-33DBVR C20032 + R302 10 k** | open-drain does not fight SWD / internal resets; keeps D-02 (kill on every reset) | P-09 (owner 2026-11-23); SLVS165G p.1 |
| 2 | LSE 9 pF FC-135 or 12.5 pF Basic | **Q13FC13500003 C99010, 10 pF caps** | gm margin ×2.3 vs ×1.25 | DS12712 p.122; calc §1 |
| 3 | X5R allowed? | **yes: C305 = CL21A475KAQNNNE C1779 (Basic, X5R 25 V)** | owner allowed X5R bulk; removes one Extended line | owner 2026-11-23 |
| 6 | Supercap C311 | **no supercap footprint in v1** (C311, R301 removed) | no LCSC supercap could be verified (jlcsearch + JLC API searched 2026-11-23); RTC keeps running in Sleep (VBAT_MCU = OR(+3V3, AFE_REG1), sheet 01) and is lost only in Ship (REG1 off); firmware re-syncs time over CAN / BLE and keeps the last timestamp in FRAM | D-35 asked "supercap DNP" — this is a downgrade, owner may restore it once a part is verified |
| 9 | SWD header XunPu or Samtec | **XunPu PH1.27-02-05PWS C41360877** | −40…105 °C (listing), 1,795 at JLC (≥ 500), $ ≪ Samtec C448647 | P-13; live check 2026-11-23 |
| – | D301 BAT54C ownership | **dropped here; sheet 01 D109 (C37704) is the VBAT_MCU OR** | one physical part (contract) | bom_G1 D109 |
| – | TPS3828 MR pin | **NC** (internal 52 k PU) | no manual-reset source needed; wake button is separate | SLVS165G p.3, p.6 |
| – | MCU pin net names | §8 names verbatim, incl. sheet-local ones | lets the netlist be diffed against §8 directly | ARCHITECTURE §8 |

## 7. New interface signals
None. (Sheet-local net `03_WDI_SUP` = U302 side of JP302.) Every cross-sheet net on this sheet is in ARCHITECTURE §10 or the contract rail list.

## 8. B2B change requests
None. **Request to the sheet 07 owner (power board):** the fail-safe pull-down on `MCU_NRST` (bom_G2 F-13) must be **≥ 100 kΩ**, otherwise NRST high can fall below VIH (calc §1). 100 kΩ gives 3.08 V.

## 9. Firmware rules forced by this sheet
1. LSEDRV = 11 (≥ 10 minimum) for Y302.
2. Toggle WDI (PC12) within 0.9 s after start (debug: cut JP302, or keep PC12 analog); WDI floats in reset and disables the WDT (SLVS165G p.2). Enable IWDG as backstop.
3. Release PA15 / PB4 from JTAG (keep SWD); disable UCPD dead-battery Rd on PB4 / PB6 (UCPD_DBDIS) early.
4. PB8 to non-analog mode after start (DS12712 p.68 note 5); keep nSWBOOT0 = 1.
5. PC13 (`WAKE_BTN_N`) input only (p.68 note 2).

## 10. Unverified items
* Y301 load capacitance is the listing value (20 pF); YXC PDF is image-only. Check the HSE frequency on the first board (ST rule of thumb of 10 pF stray would give 20 pF caps).
* XunPu J301 drawing pad check carried from bom_G3 (pads 0.74 × 2.5 vs KiCad 0.74 × 2.4).

## 11. Owner questions remaining
* Restore a supercap footprint (needs a verified 3.3 V+ supercap LCSC number) or accept RTC loss in Ship mode?

## 12. LCSC verification
All LCSC numbers on this sheet were checked live on **2026-11-23**: MPN + manufacturer + LCSC stock from the LCSC product API (`wmsc.lcsc.com/ftps/wm/product/detail`), JLC stock + Basic/Extended from the JLCPCB parts API (`selectSmtComponentList`).
| LCSC | MPN | Manufacturer | LCSC stock | JLC stock | JLC type | Refs |
|---|---|---|---|---|---|---|
| C1634 | CL10C100JB8NNNC | Samsung Electro-Mechanics | 420,200 | 1,749,904 | Basic | C314, C315 |
| C1663 | CL10C330JB8NNNC | Samsung Electro-Mechanics | 298,000 | 1,310,926 | Basic | C312, C313 |
| C1779 | CL21A475KAQNNNE | Samsung Electro-Mechanics | 243,560 | 1,869,010 | Basic | C305 |
| C14663 | CC0603KRX7R9BB104 | YAGEO | 227,800 | 52,261,571 | Basic | C301, C302, C303, C304, C308, C310, C316, C317 |
| C20032 | TPS3828-33DBVR | TI | 37,850 | 37,850 | Extended | U302 |
| C22935 | 0603WAF1004T5E | UNI-ROYAL | 2,378,500 | 5,576,566 | Basic | R304, R305, R306 |
| C25804 | 0603WAF1002T5E | UNI-ROYAL | 0 | 42,081,465 | Basic | R302, R303 |
| C28323 | CL21B105KBFNNNE | Samsung Electro-Mechanics | 140 | 3,838,926 | Basic | C307, C309 |
| C57112 | 0603B103K500NT | FH | 0 | 4,483,923 | Basic | C306 |
| C99010 | Q13FC13500003 | EPSON | 24,700 | 24,702 | Extended | Y302 |
| C115962 | X50328MSB2GI | YXC Crystal Oscillators | 289,440 | 521,898 | Basic | Y301 |
| C529361 | STM32G473RCT6 | ST | 2,944 | 3,055 | Extended | U301 |
| C5199801 | RH-5001 | ronghe | 97,335 | 99,458 | Extended | TP301 |
| C41360877 | PH1.27-02-05PWS | XUNPU | 1,795 | 1,795 | Extended | J301 |

## 13. Review disposition (R3_mcu_io_comms.md)

| Finding | Disposition | Changed refs |
|---|---|---|
| R3-08 no way to disable the external WDT | **Applied**: JP302 normally-closed solder jumper (`Jumper:SolderJumper_2_Bridged`, in_bom no) between PC12 `WDI` and U302 WDI (`03_WDI_SUP`); TP305 moved to the U302 side | JP302 (new), U302 pin 4, TP305 |
| R3-12 power-board inputs float with the B2B unplugged | **Applied**: 1 MΩ (C22935) to GND_PWR on `OC_TRIP_N`, `KILL_N`, `ISENSE_OUT` (3.3 µA load each, calc). `NTC_SHUNT` is already defined by R1013 (sheet 10) | R304, R305, R306 (new) |
| R3-18 PA8 AF note | **Closed** against DS12712 Rev 2 Table 12 | – |
| R3-01 (expander RESET on MCU_NRST) | applied on sheet 08; NRST level check above | – |
| P5-08 ISENSE_OUT ADC sampling reservoir | **Fixed**: C318 1 nF C0G 0603 ISENSE_OUT → GND_PWR at U301 (series R = R419 100 R on the power board); LCSC C163508 reused from sheet 02 C227–C230 (live-verified there, 2026-11-23) | C318 (new) |
| P5C-06 probe access on PWR_HOLD / FET_EN / KILL_N | **Fixed**: THT pads (in_bom no) | TP306, TP307, TP308 (new) |
