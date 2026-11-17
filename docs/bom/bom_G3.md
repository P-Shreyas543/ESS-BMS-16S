# G3 BOM: sheets 03 MCU, 08 IO / Front Panel, 10 Memory / Sensors

P3 part selection for the 16S LFP ESS BMS (STM32G473RCT6 + BQ76952). Written 2026-11-17. **Read-only on the project; nothing in the repository was changed.** Machine-readable copy: `bom_G3.csv` (same rows, playbook column order; quantity = number of references).

**Verification source (every LCSC number below, live this session, 2026-11-17):**

* MPN + manufacturer: LCSC product API `wmsc.lcsc.com/ftps/wm/product/detail?productCode=Cxxxx`.
* JLC stock, Basic / Extended / Preferred flag and the @100 price: JLCPCB parts API `jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList` (keyword = LCSC number, exact code match).
* Candidate search: `jlcsearch.tscircuit.com/api/search` and the JLCPCB API. jlcsearch returns no stock figures today, so its stock is not used.
* Datasheets: the LCSC PDF of the exact LCSC number, text extracted with pypdf; image-only PDFs (YXC crystal, KINGTEK DIP, XunPu header, XKB switch, Huaneng buzzer, SUPSiC package page) were read as images. Page numbers are PDF pages.

Stock = JLC assembly stock. DNP rows carry full purchase data and the condition to fit them.

## 1. BOM table

| Ref | Qty | Value | Footprint | MPN | Manufacturer | LCSC | Spec | Stock | B/E | Description | DS check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U301 | 1 | STM32G473RCT6 | `Package_QFP:LQFP-64_10x10mm_P0.5mm` | STM32G473RCT6 | ST | [C529361](https://jlcpcb.com/partdetail/C529361) | Cortex-M4 170MHz 256K/128K 3xFDCAN | 2,940 | Extended | STM32G473RCT6 MCU LQFP-64, main controller (VDD 1.71-3.6 V, temp code 6 = -40...85 C, DS12712 p.221) | DS12712 Rev 2: LQFP64 pin table p.54-68 (VBAT 1, VDD 16/32/48/64, VSSA 27, VREF+ 28, VDDA 29); temp code 6 -40...85 C (105 C Tj) p.221; supply scheme p.77 Fig.15; VBAT 1.55-3.6 V p.80 |
| C301, C302, C303, C304, C308, C310, C316, C317 | 8 | 100nF 50V | `Capacitor_SMD:C_0603_1608Metric` | CC0603KRX7R9BB104 | YAGEO | [C14663](https://jlcpcb.com/partdetail/C14663) | X7R 0603 | 31,857,596 | Basic | 100 nF X7R 50 V 0603, U301 VDD x4 / VREF+ / VBAT, U302 VDD, MCU_NRST filter (n x 100 nF per VDD, DS12712 p.77 Fig.15; 0.1 uF on NRST p.137 Fig.26) | MLCC: 50 V on 3.3 V = 15x derating |
| C305 | 1 | 4.7uF 25V | `Capacitor_SMD:C_0805_2012Metric` | CC0805KKX7R8BB475 | YAGEO | [C354262](https://jlcpcb.com/partdetail/C354262) | X7R 0805 | 661,021 | Extended | 4.7 uF X7R 25 V 0805, U301 VDD bulk (1 x 4.7 uF, DS12712 p.77 Fig.15) | 25 V on 3.3 V = 7.6x; X7R per playbook. Basic X5R alternative C1779 if owner allows X5R |
| C306 | 1 | 10nF 50V | `Capacitor_SMD:C_0603_1608Metric` | 0603B103K500NT | FH | [C57112](https://jlcpcb.com/partdetail/C57112) | X7R 0603 | 4,940,862 | Basic | 10 nF X7R 50 V 0603, VDDA pin 29 HF decoupling (10 nF + 1 uF, DS12712 p.77 Fig.15) |  |
| C307, C309 | 2 | 1uF 50V | `Capacitor_SMD:C_0805_2012Metric` | CL21B105KBFNNNE | Samsung Electro-Mechanics | [C28323](https://jlcpcb.com/partdetail/C28323) | X7R 0805 | 4,177,802 | Basic | 1 uF X7R 50 V 0805, VDDA pin 29 / VREF+ pin 28 (1 uF each, DS12712 p.77 Fig.15); no Basic X7R 1 uF in 0603, so one size up |  |
| C311 | 1 | 0.22F 3.3V | `UNVERIFIED (supercap footprint TBD)` | UNVERIFIED | UNVERIFIED | UNVERIFIED | Supercap, DNP | - | UNVERIFIED | 0.1-0.22 F supercap 3.3 V+, VBAT_MCU RTC hold-up in Ship (fit only if D-35 / B Q-B7 = keep RTC in Ship; VBAT 1.55-3.6 V, DS12712 p.80) | UNVERIFIED: no supercap found via jlcsearch / JLCPCB search this session. Candidate to check: KEMET FC0V224ZFTBR24 (0.22 F 3.5 V) or Seiko CPH3225A (11 mF 3.3 V) |
| R301 | 1 | 1k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1001T5E | UNI-ROYAL | [C21190](https://jlcpcb.com/partdetail/C21190) | 0603 100mW, DNP | 26,033,633 | Basic | 1 kOhm 1% 0603, C311 supercap charge limit from VBAT_MCU (inrush <= 3.3 mA on AFE_REG1 5 mA budget, ARCHITECTURE 4.2) - fit with C311 only | P = 3.3 V^2/1 k = 11 mW transient (11 % of 100 mW) |
| D301 | 1 | BAT54C | `Package_TO_SOT_SMD:SOT-23` | BAT54C,215 | Nexperia | [C37704](https://jlcpcb.com/partdetail/C37704) | 30V 200mA SOT-23 | 325,904 | Extended(Preferred) | BAT54C dual Schottky 30 V SOT-23, VBAT_MCU OR of +3V3 and AFE_REG1 (common cathode, IR <= 2 uA @ 25 V, BAT54C DS p.1). OWNERSHIP: also listed as D_VBAT (C466637) on sheet 01 - keep one | Nexperia BAT54C DS p.1-2: pin 3 common cathode, pins 1/2 anodes; VR 30 V vs 3.3 V |
| Y301 | 1 | 8MHz | `Crystal:Crystal_SMD_5032-2Pin_5.0x3.2mm` | X50328MSB2GI | YXC Crystal Oscillators | [C115962](https://jlcpcb.com/partdetail/C115962) | 8MHz 20pF 5032 | 505,830 | Basic | 8 MHz 20 pF +-10 ppm 5032 crystal, HSE for FDCAN bit timing (ESR <= 80 Ohm, C0 <= 5 pF, -40...85 C, YXC YSX530GA DS p.1) | YSX530GA DS p.1: 5.0x3.2 2-pad, land 1.7x2.4 @ 3.7 mm pitch vs KiCad 2.0x2.4 @ 3.7 mm (ok). gm_crit = 4*80*(2*pi*8 MHz)^2*(5+20 pF)^2 = 0.51 mA/V < Gm 1.5 mA/V (DS12712 p.120 Table 44). Field Y1 had a 3225 footprint with this 5032 number |
| C312, C313 | 2 | 33pF 50V | `Capacitor_SMD:C_0603_1608Metric` | CL10C330JB8NNNC | Samsung Electro-Mechanics | [C1663](https://jlcpcb.com/partdetail/C1663) | C0G 0603 | 1,420,768 | Basic | 33 pF C0G 50 V 0603, Y301 load caps (CL = C/2 + Cstray = 16.5 + 3...5 = 19.5-21.5 pF vs 20 pF, YSX530GA p.1) | ST suggests 5-20 pF typ. with 10 pF stray (DS12712 p.120); with 10 pF stray C = 20 pF -> confirm on first board by measuring f |
| Y302 | 1 | 32.768kHz | `Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm` | Q13FC13500003 | EPSON | [C99010](https://jlcpcb.com/partdetail/C99010) | 32.768k 9pF 3215 | 30,665 | Extended | 32.768 kHz 9 pF +-20 ppm 3215 crystal, LSE / RTC (R1 <= 70 kOhm, C0 1 pF typ, -40...85 C, Epson FC-135 DS p.1) | FC-135 DS p.1: CL 9 pF, R1 70 k max. gm_crit = 4*70k*(2*pi*32768)^2*(1+9 pF)^2 = 1.19 uA/V vs Gmcritmax 2.7 uA/V at LSEDRV=11 (2.3x) / 1.7 at 10 (1.4x), DS12712 p.122 Table 45. Basic 12.5 pF C32346 gives 2.16 uA/V (1.25x only) |
| C314, C315 | 2 | 10pF 50V | `Capacitor_SMD:C_0603_1608Metric` | CL10C100JB8NNNC | Samsung Electro-Mechanics | [C1634](https://jlcpcb.com/partdetail/C1634) | C0G 0603 | 1,934,352 | Basic | 10 pF C0G 50 V 0603, Y302 load caps (CL = C/2 + Cstray = 5 + 3...5 = 8-10 pF vs 9 pF, FC-135 p.1) | No series resistor on LSE (forbidden, DS12712 p.122) |
| U302 | 1 | TPS3828-33DBVR | `Package_TO_SOT_SMD:SOT-23-5` | TPS3828-33DBVR | TI | [C20032](https://jlcpcb.com/partdetail/C20032) | 2.93V WDT open-drain | 38,434 | Extended | TPS3828-33 supervisor + watchdog, OPEN-DRAIN RESET on MCU_NRST (2.93 V; td 120-300 ms; WDT 0.9-2.5 s; SLVS165J p.1, p.6). Replaces push-pull TPS3823 (C7719) that fights NRST / SWD | SLVS165J p.1: DBV pin-out 1 RESET, 2 GND, 3 MR, 4 WDI, 5 VDD (same as TPS3823); "Open-Drain (TPS3828)" p.1; WDI unconnected = WDT off p.2; MR 52 k internal pull-up p.6; -40...85 C p.1 |
| R302, R303 | 2 | 10k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1002T5E | UNI-ROYAL | [C25804](https://jlcpcb.com/partdetail/C25804) | 0603 100mW | 41,260,558 | Basic | 10 kOhm 1% 0603, R302 MCU_NRST pull-up (open-drain U302, edge for U_KILL1), R303 MCU_BOOT0 pull-down (BOOT0 = 0 -> flash) | P <= 3.3^2/10k = 1.1 mW (1 %) |
| J301 | 1 | SWD 2x5 1.27mm | `Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD` | PH1.27-02-05PWS | XUNPU | [C41360877](https://jlcpcb.com/partdetail/C41360877) | SMD vertical, unshrouded | 1,810 | Extended | 2x5 1.27 mm SMD pin header, Cortex-M 10-pin SWD + SWO + NRST (1 A, -40...105 C, XunPu PH1.27-02-NPWS drawing). Replaces field C2932845 (= 250 mOhm resistor) | XunPu drawing p.1: pads 0.74 x 2.5 at 1.27 pitch, 6.5 mm outer span; KiCad 0.74 x 2.4 at +-1.95 mm (6.3 mm) - match. Pin 1 VTref +3V3, 2 SWDIO, 3/5/9 GND, 4 SWCLK, 6 SWO, 7 key/NC, 8 NC, 10 nRESET |
| TP301 | 1 | GND_PWR | `TestPoint:TestPoint_Keystone_5000-5004_Miniature` | RH-5001 | ronghe | [C5199801](https://jlcpcb.com/partdetail/C5199801) | Black hook | 108,127 | Extended | Black test hook, GND_PWR reference at the MCU area (playbook 5.5) | ronghe RH-500x drawing p.1: hook pins match Keystone 5000 pattern (2 pins) |
| TP302, TP303, TP304, TP305 | 4 | MCU_NRST / MCU_BOOT0 / VBAT_MCU / WDI | `TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm` | - | - | - | THT pad | - | n/a | THT probe pads (in_bom no): reset line, boot strap, RTC supply, watchdog kick | Not purchased (in_bom no) |
| JP301 | 1 | BOOT0 | `Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` | - | - | - | Solder jumper | - | n/a | Solder jumper MCU_BOOT0 -> +3V3 (ROM bootloader entry, AN2606 pattern 14), PCB only (in_bom no) | Not purchased |
| U801, U802 | 2 | TCA9535PWR | `Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm` | TCA9535PWR | TI | [C130204](https://jlcpcb.com/partdetail/C130204) | 16-bit I2C GPIO 400kHz | 14,096 | Extended | TCA9535 16-bit I2C expander TSSOP-24, U801 @0x20 (DIP, AFE flags, enables, dry contacts) / U802 @0x21 (LEDs, mux select, EN_12V) (5-V tolerant I/O, VI <= 6 V, SCPS201D p.1, p.4) | SCPS201D: PW pin-out p.3 (INT 1, A1 2, A2 3, P00-07 4-11, GND 12, P10-17 13-20, A0 21, SCL 22, SDA 23, VCC 24); address 0100 A2 A1 A0 p.18; VOL 0.5 V @ 8 mA, IIH/IIL +-1 uA p.5; no internal pull-ups p.1; ports are inputs at POR |
| C801, C802 | 2 | 100nF 50V | `Capacitor_SMD:C_0603_1608Metric` | CC0603KRX7R9BB104 | YAGEO | [C14663](https://jlcpcb.com/partdetail/C14663) | X7R 0603 | 31,857,596 | Basic | 100 nF X7R 50 V 0603, U801 / U802 VCC decoupling (SCPS201D typ. application) |  |
| R801, R802 | 2 | 2.2k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF2201T5E | UNI-ROYAL | [C4190](https://jlcpcb.com/partdetail/C4190) | 0603 100mW | 4,451,876 | Basic | 2.2 kOhm 1% 0603, I2C2 EXP_SCL / EXP_SDA pull-ups to +3V3 (Fm 400 kHz: tr = 0.85*R*Cb <= 300 ns -> Cb <= 160 pF incl. J801 cable; 1.5 mA <= SDA IOL 3 mA, SCPS201D p.5) | P = 3.3^2/2.2k = 5 mW (5 %). Changed from 4.7 k (Cb <= 75 pF only) |
| R803, R804, R805, R806, R807, R809, R810, R811 | 8 | 10k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1002T5E | UNI-ROYAL | [C25804](https://jlcpcb.com/partdetail/C25804) | 0603 100mW | 41,260,558 | Basic | 10 kOhm 1% 0603: R803-R806 DIP_ADDR0..3 pull-ups, R807 DI_AUX1 pull-up at J802, R809-R811 series into U801 P04/P05/P07 (AFE_FLT_DSG_N, AFE_FLT_CHG_N, DFETOFF_RB: limits injection when TCA VCC = 0) | P <= 1.1 mW |
| SW801 | 1 | DSHP04TSGET | `Button_Switch_SMD:SW_DIP_SPSTx04_Slide_KingTek_DSHP04TS_W7.62mm_P1.27mm` | DSHP04TSGET | YE | [C40736](https://jlcpcb.com/partdetail/C40736) | 4P SPST 1.27mm -40C | 23,976 | Extended | 4-pole SMD DIP 1.27 mm, pack address 0-15 to GND (25 mA 24 VDC, -40...85 C, KINGTEK DSHP drawing p.1). Replaces DSHP04TSGER C3293144 (-30 C) and field C318884 (tactile switch) | KINGTEK drawing p.1: operating -40...+85 C; land 1.27 x 0.76 at 1.27 pitch, rows 6.35/8.89 mm = KiCad KingTek_DSHP04TS footprint exactly |
| R808 | 1 | 1k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1001T5E | UNI-ROYAL | [C21190](https://jlcpcb.com/partdetail/C21190) | 0603 100mW | 26,033,633 | Basic | 1 kOhm 1% 0603, DI_AUX1 series from J802 to U801 P06 (ESD current limit; node reads 0 V when contact closes) |  |
| C803 | 1 | 10nF 50V | `Capacitor_SMD:C_0603_1608Metric` | 0603B103K500NT | FH | [C57112](https://jlcpcb.com/partdetail/C57112) | X7R 0603 | 4,940,862 | Basic | 10 nF X7R 50 V 0603, DI_AUX1 filter at U801 P06 (tau 10 us) |  |
| D801, D802, D803, D804, D807 | 5 | KT-0805G | `LED_SMD:LED_0805_2012Metric` | KT-0805G | Hubei KENTO Elec | [C2297](https://jlcpcb.com/partdetail/C2297) | Green 525nm 0805 | 3,160,579 | Basic | Green LED 0805, SOC1-4 + RUN, anode +5V via 1 k, cathode sunk by U802 (VF 2.6-3.1 V @ 5 mA, -40...85 C, KT-0805G DS p.3) | KENTO DS: VF 2.6-3.1 V @ 5 mA, Topr -40...+85 C. VF too high for a 3.3 V anode (0.2 V left at worst case), so anode = +5V; port HIGH (3.3 V) leaves 1.7 V across -> off |
| D805, D806 | 2 | KT-0805G | `LED_SMD:LED_0805_2012Metric` | KT-0805G | Hubei KENTO Elec | [C2297](https://jlcpcb.com/partdetail/C2297) | Green 525nm 0805, DNP | 3,160,579 | Basic | Green LED 0805, SOC5 / SOC6 (fit only for the 6-LED bar option, D-30) | as D801 |
| D808 | 1 | KT-0603R | `LED_SMD:LED_0603_1608Metric` | KT-0603R | Hubei KENTO Elec | [C2286](https://jlcpcb.com/partdetail/C2286) | Red 0603 | 5,530,278 | Basic | Red LED 0603, ALM, anode +3V3 via 680 R, cathode sunk by U802 P05 (VF 1.8-2.4 V @ 20 mA, -40...85 C, KT-0603R DS p.3) | KENTO DS: VF 1.8-2.4 V @ 20 mA, Topr -40...+85 C. Red on +3V3 so port HIGH = 0 V across (no glow) |
| R812, R813, R814, R815, R818 | 5 | 1k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1001T5E | UNI-ROYAL | [C21190](https://jlcpcb.com/partdetail/C21190) | 0603 100mW | 26,033,633 | Basic | 1 kOhm 1% 0603, green LED series from +5V (I = (5 - 2.6...3.1 - 0.05)/1k = 1.9-2.4 mA) | P = 5.8 mW max (6 %) |
| R816, R817 | 2 | 1k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1001T5E | UNI-ROYAL | [C21190](https://jlcpcb.com/partdetail/C21190) | 0603 100mW, DNP | 26,033,633 | Basic | 1 kOhm 1% 0603, SOC5 / SOC6 series (6-LED option) |  |
| R819 | 1 | 680R 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF6800T5E | UNI-ROYAL | [C23228](https://jlcpcb.com/partdetail/C23228) | 0603 100mW | 1,375,434 | Basic | 680 Ohm 1% 0603, ALM LED series from +3V3 (I = (3.3 - 1.8...2.0)/680 = 1.9-2.2 mA) | P = 3.3 mW |
| D809 | 1 | 1N4148WS | `Diode_SMD:D_SOD-323` | 1N4148WS | JSCJ | [C2128](https://jlcpcb.com/partdetail/C2128) | 100V 150mA SOD-323, DNP | 3,888,795 | Basic | 1N4148WS 100 V SOD-323, LED_ALM_HW option: ALM cathode -> KILL_N, lights ALM with the MCU dead (100 V, 150 mA, 1N4148WS DS p.1) | KILL_N low: (3.3 - 1.9 - 0.7)/680 = 1 mA; KILL_N high: 0 V across -> off |
| BZ801 | 1 | QMB-09B-05 | `Automotive_ESS_BMS:Buzzer_D9.0mm_P4.00mm` | QMB-09B-05 | Huaneng | [C161819](https://jlcpcb.com/partdetail/C161819) | 5V 2.7kHz THT, DNP | 23,244 | Extended | Passive magnetic buzzer 9 mm THT, 5 V rated, 42 Ohm, 2.7 kHz, <= 60 mA, -40...85 C (Huaneng QMB-09B-05 spec p.2); on +5V. Fit only if D-31 = keep | Spec p.2: rated 5 V, 3-7 V, coil 42 +-5 Ohm, <= 60 mA, -40...+85 C, D 9 x 5.5 mm, pins 0.6 mm at 4.0 mm. No stock KiCad footprint -> project footprint (easyeda2kicad + pad check). Replaces MLT-8530 C94599 (-20...70 C, 3.6 V) |
| Q801 | 1 | SS8050 | `Package_TO_SOT_SMD:SOT-23` | SS8050(RANGE:200-350) | JSCJ | [C2150](https://jlcpcb.com/partdetail/C2150) | 25V 1.5A SOT-23, DNP | 3,014,994 | Basic | SS8050 NPN 25 V 1.5 A SOT-23, buzzer low-side switch (VCEO 25 V, hFE 120-400 @ 100 mA, SS8050 DS p.1) | Ic peak 5 V/42 Ohm = 119 mA, Ib 2.6 mA (forced beta 46 < hFE min 120). P = 0.1 V*119 mA*50 % = 6 mW |
| R820 | 1 | 1k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1001T5E | UNI-ROYAL | [C21190](https://jlcpcb.com/partdetail/C21190) | 0603 100mW, DNP | 26,033,633 | Basic | 1 kOhm 1% 0603, Q801 base series from BUZZER (PB15) | P = 6.8 mW |
| R821 | 1 | 100k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1003T5E | UNI-ROYAL | [C25803](https://jlcpcb.com/partdetail/C25803) | 0603 100mW, DNP | 14,257,504 | Basic | 100 kOhm 1% 0603, BUZZER (PB15) pull-down -> silent while MCU floats |  |
| D810 | 1 | 1N4148WS | `Diode_SMD:D_SOD-323` | 1N4148WS | JSCJ | [C2128](https://jlcpcb.com/partdetail/C2128) | 100V 150mA SOD-323, DNP | 3,888,795 | Basic | 1N4148WS 100 V SOD-323, BZ801 coil flyback (IF 150 mA vs 119 mA peak, IFSM 2 A, 1N4148WS DS p.1) |  |
| U803, U804 | 2 | GAQY212GS | `Package_SO:SOP-4_3.8x4.1mm_P2.54mm` | GAQY212GS | SUPSiC | [C7435107](https://jlcpcb.com/partdetail/C7435107) | 60V 0.8A 2.5kV SOP-4 | 130,418 | Extended | PhotoMOS 1 Form A 60 V 0.8 A SOP-4, dry contacts DRY1 / DRY2 (2.5 kVrms I/O, IF 5-30 mA rec., -40...85 C, GAQY212GS DS p.1-2). Architecture places these as U501/U502 on sheet 05 | GAQY DS p.1 pin-out 1 LED A, 2 LED K, 3/4 MOSFET; p.2 VL 60 V, IL 0.8 A, VF 1.32-1.5 V @ 10 mA, IF(on) max 2 mA, rec. IF 5-30 mA, -40...85 C; p.4 land 0.8 x 1.2 mm, rows 6.0 mm, 2.54 pitch -> KiCad SOP-4_3.8x4.1 pads are 0.55 x 1.45 at 5.5 mm: usable but narrow; prefer a project footprint per p.4 |
| R822, R823 | 2 | 220R 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF2200T5E | UNI-ROYAL | [C22962](https://jlcpcb.com/partdetail/C22962) | 0603 100mW | 1,835,226 | Basic | 220 Ohm 1% 0603, photoMOS LED series from +3V3, sunk by U801 P16/P17 (IF = (3.2 - 1.5 - 0.5)/220 = 5.5 mA min, 8.3 mA typ; rec. 5-30 mA, GAQY p.2) | P = 15 mW (15 %). +3V3 anode chosen so port HIGH = 0 V on the LED (with a 5 V anode, 1.7 V could exceed IF(on) 2 mA max) |
| D811, D812 | 2 | SMAJ36CA | `Diode_SMD:D_SMA` | SMAJ36CA/TR13 | Brightking | [C87270](https://jlcpcb.com/partdetail/C87270) | 36V 400W SMA bidir | 216,027 | Extended | SMAJ36CA bidirectional TVS 400 W SMA, across DRY1 / DRY2 contacts (VRWM 36 V, VBR 40-44.2 V, VC 58.1 V @ 6.9 A < photoMOS VL 60 V, Brightking DS p.3) | DS p.3 row SMAJ36CA: VRWM 36 V, VBR 40.0-44.2 V, VC 58.1 V @ 6.9 A, IR 1 uA. Limits field signal to <= 30 V working |
| D813 | 1 | PESD5V0S1BA | `Diode_SMD:D_SOD-323` | PESD5V0S1BA,115 | Nexperia | [C19224](https://jlcpcb.com/partdetail/C19224) | 5V ESD SOD-323 | 65,484 | Extended | PESD5V0S1BA bidirectional ESD SOD-323, DI_AUX1 at J802 (VRWM 5 V, IRM 5 nA typ / 100 nA max, Nexperia DS p.4) | Same part as C D_ESD1-4 (no new line) |
| D814, D815, D816 | 3 | PESD5V0S1BA | `Diode_SMD:D_SOD-323` | PESD5V0S1BA,115 | Nexperia | [C19224](https://jlcpcb.com/partdetail/C19224) | 5V ESD SOD-323, DNP | 65,484 | Extended | PESD5V0S1BA ESD SOD-323, J801 EXP_SCL / EXP_SDA / WAKE_BTN_RAW (fit with J801; on WAKE_BTN_RAW check leakage vs TS2 0.2 uA budget, IRM 100 nA max @25 C, DS p.4) |  |
| J802 | 1 | DRY/DI 6P 3.81 | `Connector_Phoenix_MC:PhoenixContact_MC_1,5_6-G-3.81_1x06_P3.81mm_Horizontal` | WJ15EDGRC-3.81-06P-14-00A | KANGNEX | [C7246](https://jlcpcb.com/partdetail/C7246) | 6P 3.81mm THT R/A | 12,803 | Extended | Pluggable terminal header 6P 3.81 mm right-angle THT: 1-2 DRY1, 3-4 DRY2, 5 DI_AUX1, 6 GND_PWR (300 V / 8 A, -40...105 C, Kangnex WJ15EDGRC drawing p.1). Mating plug C7247 ordered loose | Kangnex drawing p.1: 300 V UL / 8 A, -40...+105 C, pitch 3.81 = Phoenix MC 1,5/6-G-3.81 pattern; hole diameter not legible in the text extract (check drawing before layout) |
| J801 | 1 | FRONT PANEL 8P | `Connector_Molex:Molex_PicoBlade_53261-0871_1x08-1MP_P1.25mm_Horizontal` | 532610871 | MOLEX | [C293349](https://jlcpcb.com/partdetail/C293349) | 8P 1.25mm SMD R/A, DNP | 45,317 | Extended | Molex PicoBlade 8P 1.25 mm SMD right-angle, optional front-panel board: +5V, +3V3, GND, EXP_SCL, EXP_SDA, WAKE_BTN_RAW, LED_ALM_HW, spare (1 A, 125 V, -40...105 C listing). Footprint only per D-35 | DS download timed out twice; rating from LCSC/JLC listing only (-40...+105 C, 1 A). JST GH (C265111 / C42376901) rejected: -25 C |
| SW802 | 1 | PTS810SJG250 | `Button_Switch_SMD:SW_SPST_PTS810` | PTS810SJG250SMTRLFS | C&K | [C221895](https://jlcpcb.com/partdetail/C221895) | 16V 50mA 400gf | 14,722 | Extended | Tactile switch 4.2 x 3.2 mm 400 gf SMD, wake button WAKE_BTN_RAW -> GND_PWR (16 VDC 50 mA, -40...85 C, C&K PTS810 DS p.1). Replaces TS-1187A C318884 (-30 C) | C&K PTS810 DS p.1: SJG = 400 gf, J-bend SMT, 2.5 mm high, -40...85 C, bounce <= 10 ms; KiCad SW_SPST_PTS810 footprint = same series. Front-panel plunger / light pipe TBD |
| R824 | 1 | 1M 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1004T5E | UNI-ROYAL | [C22935](https://jlcpcb.com/partdetail/C22935) | 0603 100mW | 4,305,666 | Basic | 1 MOhm 1% 0603, WAKE_BTN_N pull-up to AFE_REG1 (3.3 uA pressed; ARCHITECTURE 8 pin 2, B 4). OWNERSHIP: B draws it in the sheet-01 latch - keep one |  |
| R825, R826, R827, R828 | 4 | 100k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1003T5E | UNI-ROYAL | [C25803](https://jlcpcb.com/partdetail/C25803) | 0603 100mW | 14,257,504 | Basic | 100 kOhm 1% 0603, pull-downs on U801/U802 enable outputs EN_ISO / EN_ESP / BAL_EXT_EN / EN_12V (TCA ports are inputs at POR -> loads off). OWNERSHIP: drop any duplicate at the load switch (sheet 01) |  |
| TP801, TP802 | 2 | EXP_SCL / EXP_SDA | `TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm` | - | - | - | THT pad | - | n/a | THT probe pads (in_bom no), I2C2 bus | Not purchased |
| TP803 | 1 | GND_PWR | `TestPoint:TestPoint_Keystone_5000-5004_Miniature` | RH-5001 | ronghe | [C5199801](https://jlcpcb.com/partdetail/C5199801) | Black hook | 108,127 | Extended | Black test hook, GND_PWR in the front-panel area |  |
| U1001 | 1 | FM25V02A-GTR | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | FM25V02A-GTR | Infineon/CYPRESS | [C66029](https://jlcpcb.com/partdetail/C66029) | 32KB FRAM 40MHz | 7,255 | Extended | FM25V02A 256 Kbit SPI F-RAM SOIC-8, SOC/SOH, fault record, brown-out counters (2.0-3.6 V, 40 MHz, -40...85 C, 001-90865 Rev *E p.1). Replaces 25LC256 U_MEM1 (field C5426 has no record) | 001-90865 p.1: VDD 2.0-3.6 V, -40...+85 C, 10^14 cycles; p.3 SOIC-8 pin-out 1 CS, 2 SO, 3 WP, 4 VSS, 5 SI, 6 SCK, 7 HOLD, 8 VDD; WP must be tied to VDD if unused p.3 |
| U1002 | 1 | GD25Q64ESIG | `Package_SO:SOIC-8_5.3x5.3mm_P1.27mm` | GD25Q64ESIG | GigaDevice Semicon Beijing | [C2685734](https://jlcpcb.com/partdetail/C2685734) | 64Mbit SPI NOR 208mil | 19,975 | Extended | GD25Q64E 64 Mbit SPI NOR SOP-8 208 mil, black-box log + staged firmware image (2.7-3.6 V, 133 MHz, -40...85 C I-grade, GD25Q64E DS p.37, p.49) | GD25Q64E DS p.6 pin-out (CS#, SO, WP#, VSS, SI, SCLK, HOLD#, VCC) = W25Q64JV; p.37 TA -40...85 (I); p.39 VCC 2.7-3.6 V; p.49 S = SOP8 208 mil. W25Q64JVSSIQ C179171 kept as alternate (LCSC 227 / JLC 4,060 pcs) |
| C1001, C1002, C1003, C1004, C1005, C1006, C1007, C1008, C1010 | 9 | 100nF 50V | `Capacitor_SMD:C_0603_1608Metric` | CC0603KRX7R9BB104 | YAGEO | [C14663](https://jlcpcb.com/partdetail/C14663) | X7R 0603 | 31,857,596 | Basic | 100 nF X7R 50 V 0603: U1001 / U1002 / U1003 decoupling, NTC channel filters S0-S4 (tau = 5 k x 100 nF = 0.5 ms), NTC_SHUNT filter at PB2 | TMUX1308 asks 0.1-10 uF on VDD (DS p.4). X7R ok for DC NTC filters |
| R1001, R1002, R1006, R1007, R1008, R1009, R1010, R1011, R1012, R1013 | 10 | 10k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1002T5E | UNI-ROYAL | [C25804](https://jlcpcb.com/partdetail/C25804) | 0603 100mW | 41,260,558 | Basic | 10 kOhm 1% 100 ppm 0603: R1001 FRAM_CS_N / R1002 FLASH_CS_N pull-ups (deselected while MCU floats); R1006-R1010 NTC bias from +3V3_A (NTC_PACK4/5/6, NTC_BAL, NTC_AMB); R1011/R1012 50 % reference divider on mux S7; R1013 NTC_SHUNT bias (OWNERSHIP: A sheet 04) | P <= 1.1 mW. 1 % / 100 ppm adds ~0.25 C at 25 C on top of the 1 % NTC |
| R1003, R1004 | 2 | 33R 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF330JT5E | UNI-ROYAL | [C23140](https://jlcpcb.com/partdetail/C23140) | 0603 100mW | 3,016,616 | Basic | 33 Ohm 1% 0603, SPI1_SCK / SPI1_MOSI series at U301 (edge damping, <= 20 MHz shared bus) |  |
| U1003 | 1 | TMUX1308PWR | `Package_SO:TSSOP-16_4.4x5mm_P0.65mm` | TMUX1308PWR | TI | [C970231](https://jlcpcb.com/partdetail/C970231) | 8:1 mux 1.62-5.5V | 5,024 | Extended | TMUX1308 8:1 analog mux TSSOP-16, MCU NTC inputs -> NTC_MUX (PB14) (1.62-5.5 V, RON <= 350 Ohm @ 3.3 V -40...85 C, IS(OFF) <= 25 nA, SCDS426 / ZHCSKY9E p.9). Replaces CD4051BQPWRQ1 C555142 (specified >= 3 V, RON at 5/10/15 V only) | TMUX1308 DS p.4: 4051 pin-out, pin 6 EN active-low (high = all off, same sense as CD4051 INH), pin 7 N.C. (CD4051 VEE), pin 8 GND, 16 VDD; p.7 VDD 1.62-5.5 V; p.9 RON 330/350 Ohm max at 3.3 V (25 C / -40...85 C), IS(OFF) +-25 nA, ID(OFF) +-45 nA |
| R1005 | 1 | 100k 1% | `Resistor_SMD:R_0603_1608Metric` | 0603WAF1003T5E | UNI-ROYAL | [C25803](https://jlcpcb.com/partdetail/C25803) | 0603 100mW | 14,257,504 | Basic | 100 kOhm 1% 0603, MUX_INH -> U1003 EN pull-up to +3V3 (mux off until U802 drives it) |  |
| C1009 | 1 | 10nF 50V | `Capacitor_SMD:C_0603_1608Metric` | 0603B103K500NT | FH | [C57112](https://jlcpcb.com/partdetail/C57112) | X7R 0603 | 4,940,862 | Basic | 10 nF X7R 50 V 0603, NTC_MUX output at PB14 (ADC kick-back 5 pF/10 nF = 0.05 %; charge share with 100 nF channel cap 9 % -> settle >= 5 ms per channel, firmware) |  |
| RT1001, RT1002 | 2 | NCP18XH103F03RB | `Resistor_SMD:R_0603_1608Metric` | NCP18XH103F03RB | muRata | [C13564](https://jlcpcb.com/partdetail/C13564) | 10k B3380 1% NTC | 270,796 | Extended | 10 kOhm B3380 1% NTC 0603, RT1001 NTC_AMB (board edge) / RT1002 NTC_BAL (among R_BL, B.Cu) (-40...125 C, Murata NTC catalog p.12). OWNERSHIP: C lists the board NTCs with RT_FET1 | Murata catalog p.12 row NCP18XH103F03RB: 10 k +-1 %, B25/50 3380 +-1 %; 0603 = R_0603 land |
| TP1001, TP1002, TP1003, TP1004, TP1005, TP1006 | 6 | SPI1_SCK / SPI1_MOSI / SPI1_MISO / FRAM_CS_N / FLASH_CS_N / NTC_MUX | `TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm` | - | - | - | THT pad | - | n/a | THT probe pads (in_bom no), SPI bus and mux output | Not purchased |
| TP1007 | 1 | GND_PWR | `TestPoint:TestPoint_Keystone_5000-5004_Miniature` | RH-5001 | ronghe | [C5199801](https://jlcpcb.com/partdetail/C5199801) | Black hook | 108,127 | Extended | Black test hook, GND_PWR in the memory / sensor area |  |

Loose item (not placed by JLC, order with the PCBA): **J802 mating plug** WJ15EDGK-3.81-06P-14-00A (KANGNEX), [C7247](https://jlcpcb.com/partdetail/C7247), 6P 3.81 mm screw plug, −40…105 °C, JLC stock 17,162, Extended, $0.308 @100.

## 2. Summary

| Item | Value |
|---|---|
| BOM lines | 60 (sheet 03: 18, sheet 08: 31, sheet 10: 11) |
| Placed, purchased parts (fitted) | **98** |
| DNP parts with purchase data | 16 (incl. C311 UNVERIFIED) |
| Probe pads / solder jumper (in_bom no) | 12 THT pads + 1 solder jumper |
| Unique LCSC numbers | **38** (+ C7247 loose plug) |
| Basic | **18** unique |
| Extended | **20** unique (1 of them Preferred: C37704). 17 fitted non-Preferred lines carry the JLC set-up fee |
| UNVERIFIED | **1** (C311 supercap, DNP) |
| Est. parts cost per board at qty 100 (fitted only, JLC @100 price) | **≈ $12.46 est.** (sheet 03 $5.57, sheet 08 $3.76, sheet 10 $3.14) |
| + Extended set-up fees | ≈ 17 × $3 / 100 boards = **≈ $0.51 / board est.** |
| + loose J802 plug | $0.31 |
| DNP options if all fitted | + $0.61 (buzzer chain $0.15) |
| Not included | JLC THT hand-solder fee for J802 and the three hooks; PCB; stock/price drift |
| Largest items | U301 STM32G473RCT6 $4.54, U1001 FM25V02A $2.12, 2 × TCA9535 $1.90, U1002 GD25Q64E $0.60, 2 × GAQY212GS $0.81 |

**Extended parts (fitted unless marked):** C529361 STM32G473RCT6, C354262 4.7 µF X7R 0805, C99010 FC-135 9 pF, C20032 TPS3828-33DBVR, C41360877 SWD header, C5199801 RH-5001 hook, C130204 TCA9535PWR, C40736 DSHP04TSGET, C7435107 GAQY212GS, C87270 SMAJ36CA, C19224 PESD5V0S1BA, C7246 terminal header, C221895 PTS810, C66029 FM25V02A, C2685734 GD25Q64ESIG, C970231 TMUX1308PWR, C13564 NCP18XH103F03RB, C37704 BAT54C (Preferred, no fee), C161819 QMB-09B-05 (DNP), C293349 PicoBlade (DNP). Loose: C7247.

Extended lines that can become Basic if the owner accepts the trade-off: C354262 → C1779 (4.7 µF **X5R** 25 V 0805, Basic) if X5R is allowed; C99010 → C32346 (FC-135 **12.5 pF**, Basic, with 18 pF caps) if a 1.25× LSE gm margin is accepted.

**THT parts:** J802 terminal header (6 joints), TP301 / TP803 / TP1007 RH-5001 hooks, BZ801 buzzer (DNP, 2 joints). THT probe pads TP302–305, TP801–802, TP1001–1006 are bare pads (in_bom no).

**Low stock (< 2,000 at JLC):** C41360877 SWD header (1,810; ≥ 500 rule met). Watch-list: C529361 STM32G473RCT6 (2,940), C970231 TMUX1308PWR (5,024), C66029 FM25V02A (7,255). The architecture's W25Q64JVSSIQ C179171 is down to 227 at LCSC (4,060 at JLC), so it was moved to alternate.

## 3. UNVERIFIED items

| Ref | Need | Status | Candidate to check |
|---|---|---|---|
| C311 (DNP) | 0.1–0.22 F supercap ≥ 3.3 V for VBAT_MCU RTC hold-up in Ship (B Q-B7, D-35) | No supercap could be matched through jlcsearch or the JLCPCB API this session; **no LCSC number given** | KEMET FC0V224ZFTBR24 (0.22 F 3.5 V coin type) or Seiko CPH3225A (11 mF 3.3 V, SMD). Confirm number, footprint and leakage before fitting |

Datasheet gaps (LCSC number verified, DS check partial):
* J801 Molex 53261-0871 (C293349): PDF download timed out twice; rating from the listing only (−40…105 °C, 1 A). DNP.
* J802 Kangnex header (C7246): hole diameter not legible in the extracted drawing text; pitch 3.81 mm and ratings read. Check before layout.
* U803/U804 GAQY212GS: KiCad footprint pads are narrower than the DS land (see table); make a project footprint.
* BZ801: no stock KiCad footprint; `Automotive_ESS_BMS:Buzzer_D9.0mm_P4.00mm` must be created (easyeda2kicad + pad check against spec p.2).

## 4. Calculations used

* **HSE (Y301, 8 MHz, CL 20 pF):** CL = C/2 + Cstray. With Cstray = 3…5 pF, C = 2 × (20 − 3…5) = 30…34 pF → **33 pF C0G** → CL = 19.5…21.5 pF. gm_crit = 4·ESR·(2πf)²·(C0+CL)² = 4·80 Ω·(2π·8 MHz)²·(25 pF)² = **0.51 mA/V** < Gm 1.5 mA/V (DS12712 p.120). ST's "10 pF combined stray" rule of thumb (p.120) would give 20 pF; check the frequency on the first board.
* **LSE (Y302, 32.768 kHz, CL 9 pF, R1 ≤ 70 kΩ, C0 1 pF):** C = 2 × (9 − 4) = 10 pF C0G → CL = 8…10 pF. gm_crit = 4·70 kΩ·(2π·32 768)²·(10 pF)² = **1.19 µA/V**; Gmcritmax = 2.7 µA/V at LSEDRV = 11 (2.3×), 1.7 at LSEDRV = 10 (1.4×) (DS12712 p.122). The 12.5 pF Basic part gives 2.16 µA/V = 1.25× only.
* **LEDs:** green KT-0805G VF 2.6–3.1 V @ 5 mA (DS p.3): from 3.3 V the worst case leaves 0.2 V for the resistor, so the green LEDs go to **+5V via 1 kΩ** (1.9–2.4 mA). Red KT-0603R stays on +3V3 via 680 Ω (1.9–2.2 mA) so a HIGH expander port leaves 0 V across it.
* **PhotoMOS LED:** (3.2 V − 1.5 V − 0.5 V VOL@8 mA) / 220 Ω = 5.5 mA min, 8.3 mA typ, inside 5–30 mA (GAQY p.2).
* **I2C2:** Fm tr ≤ 300 ns; tr ≈ 0.85·R·Cb → 2.2 kΩ allows 160 pF (4.7 kΩ only 75 pF).
* **NTC mux settling:** charge share 10 nF (output) with 100 nF (channel) = 9 % step; τ = (5 kΩ + 0.35 kΩ) × 110 nF = 0.59 ms; to ½ LSB at 12 bit: ln(0.09 × 8192) × τ ≈ 3.9 ms → firmware waits **≥ 5 ms** after each MUX_S change. Mux leakage (7 × 25 + 45 nA) × 5 kΩ ≈ 1.1 mV.
* **Buzzer (DNP):** 5 V / 42 Ω = 119 mA peak, ≤ 60 mA at 50 % duty on **+5V** (not +3V3). Ib = (3.3 − 0.75) / 1 kΩ = 2.6 mA, forced β 46 < hFE min 120.
* **Derating:** every MLCC ≥ 25 V on 3.3 / 5 V rails (≥ 5×). Highest resistor dissipation 15 mW (R822/R823) = 15 % of 100 mW. SMAJ36CA VC 58.1 V < photoMOS 60 V.

## 5. Wrong LCSC numbers re-resolved (sheet 03 fields and architecture tables)

| Ref today → new | Field / arch number | What LCSC returns (live) | New number |
|---|---|---|---|
| U_MCU1 → U301 | C529329 | STM32G030C8T6 (LQFP-48) | **C529361** STM32G473RCT6 |
| U_WDOG1 → U302 | C80145 (field) / C7719 (arch) | C80145: no record. C7719 = TPS3823-33DBVR, **push-pull** | **C20032** TPS3828-33DBVR (open-drain, same pin-out). See finding F1 |
| U_MEM1 → U1001 | C5426 | no record | **C66029** FM25V02A-GTR |
| Y1 → Y301 | C115962 + 3225 footprint + MPN X32258MOB4SI | YXC X50328MSB2GI, **5032** 2-pad, 20 pF, Basic | keep **C115962**, footprint → `Crystal_SMD_5032-2Pin_5.0x3.2mm`, caps → 33 pF |
| C_X1 / C_X2 → C312/C313 | C1644, value "18pF", MPN CL10C180JB8NNNC | C1644 = CL10C**150**JB8NNNC, **15 pF** | **C1663** 33 pF C0G |
| J_SWD1 → J301 | C2932845 | **HoYH1206 250 mΩ 1 W current-sense resistor** | **C41360877** XunPu PH1.27-02-05PWS |
| SW_CFG1 → SW801 | C318884 (arch: C3293144) | C318884 = TS-1187A tactile switch; C3293144 = DSHP04TSGER rated **−30 °C** | **C40736** DSHP04TSGET (KINGTEK, −40…85 °C) |
| SW802 (arch) | C318884 TS-1187A | operating −30…85 °C (XKB drawing) | **C221895** C&K PTS810SJG250SMTRLFS (−40…85 °C) |
| D_HB1 (removed) | C72044, value "Blue Heartbeat", MPN 19-217/BHC-AP1Q2/3T | Everlight 19-217/**R6C**-AL1M2VY/3T, a **red** LED, 0 stock | removed (PC13 must not source an LED, DS12712 p.68); RUN = D807 |
| C_A1 (sheet 03) | C15849, MPN CC0603KRX7R7BB105 (X7R) | CL10A105KB8NNNC = **X5R** | C307/C309 **C28323** X7R 0805 |
| U1002 (arch) | C179171 W25Q64JVSSIQ | correct part, but LCSC stock 227 (JLC 4,060) | **C2685734** GD25Q64ESIG (19,975), W25Q64 as alternate |
| U1003 (arch) | C555142 CD4051BQPWRQ1 | correct part; 3–20 V, no RON at 3.3 V | **C970231** TMUX1308PWR (pin-compatible) |
| BZ801 (arch) | C94599 MLT-8530 | −20…70 °C, 3.6 V rated | **C161819** QMB-09B-05 (−40…85 °C, 5 V), DNP |
| D801–D805 (arch) | C12624 KT-0603G (Extended) | correct, VF 3.1 V | **C2297** KT-0805G (Basic, same VF class) |
| D_VBAT (B, sheet 01) | C466637 BAT54C (High Diode, 2,567) | – | **C37704** Nexperia BAT54C,215 (Preferred, 325,904) |

## 6. Design-impacting findings

* **F1. TPS3823 RESET is push-pull and fights NRST.** SLVS165J p.1: active-low push-pull on TPS3820/3/4/5; open-drain only on TPS3828. STM32 NRST is bidirectional: internal resets (IWDG, software, BOR) pull the pin low, and DS12712 p.137 Fig.26 note 2 requires that the level "can go below VIL(NRST)". A push-pull high fights the SWD probe and the MCU's own reset pulse. It also hides those resets from U_KILL1, which breaks D-02 ("kill on every MCU reset"). **Fix:** U302 = TPS3828-33DBVR (C20032, same SOT-23-5 pin-out, 38k stock) plus R302 10 kΩ pull-up. The fallback, if TPS3823 is kept, is 1 kΩ in series between RESET and the NRST node, with U_KILL1 and SWD pin 10 on the MCU side of the resistor.
* **F2. Wrong J_SWD1 number.** C2932845 is a 250 mΩ shunt resistor. The PCBA would have placed a resistor on the debug footprint.
* **F3. LED supply.** The green VF of 2.6–3.1 V (KT-0805G DS) is too high for a 3.3 V anode at worst case and at −40 °C. The fix is green LEDs on +5V, sunk by the TCA9535 (5-V-tolerant ports, VI ≤ 6 V, SCPS201D p.1, p.4). Red ALM and the photoMOS LEDs stay on +3V3 so that a HIGH port means 0 V across them: a 5 V anode would put about 1.7 V on the photoMOS LED, and IF(on) can be as low as 2 mA max (GAQY p.2). This **changes the integrator proposal** "LEDs on +3V3" (ARCHITECTURE §4.1): about 12 mA moves from +3V3 to +5V.
* **F4. −40 °C (D-14) violations in the architecture's picks:**
  * DSHP04TSGER (−30 °C), also used for **SW601 / SW602 on sheet 06**: move those to C40736 too.
  * TS-1187A (−30 °C).
  * MLT-8530 (−20 °C).
  * JST GH SM08B (−25 °C).

  All of these were replaced with −40 °C parts.
* **F5. Buzzer on +5V.** QMB-09B-05 is rated 5 V and draws ≤ 60 mA. Running it from +5V removes the 95 mA buzzer peak from the TPS7B82 +3V3 LDO (the D-31 concern, ARCHITECTURE §4.2 notes U3 dissipation). It is THT. Left DNP until D-31 is decided.
* **F6. Mux.** CD4051B is specified from 3 V with RON given only at 5/10/15 V. TMUX1308PWR is pin-compatible (pin 6 EN active-low = INH sense, pin 7 NC where the CD4051 has VEE), specified at 3.3 V (RON ≤ 350 Ω, leakage ±25 nA, SCDS426 p.9) and costs $0.18 vs $0.62.
* **F7. HSE footprint and caps.** The Basic C115962 is 5032 2-pad with CL = 20 pF. The footprint must change from 3225-4pin to 5032-2pin, and the load caps from "18 pF" (actually 15 pF) to 33 pF.
* **F8. AFE_FLT_* read-back leakage.** Adding U801 P04 / P05 to the DDSG / DCHG nets adds up to ±1 µA (TCA9535 IIH/IIL, SCPS201D p.5). With D-25's 470 kΩ pull-down that is another 0.47 V on the Hi-Z = fault node. Together with the 74LVC ±1 µA, the worst case is about 0.94 V, which is above the LVC VIL. The 10 kΩ series resistors (R809 / R810) do not cure leakage. For C / A to decide:
  * lower the pull-down to 220 kΩ;
  * read the flags after U_KILL2;
  * or accept the typical (nA) leakage.
* **F9. Supercap inrush.** A supercap on VBAT_MCU fed through the BAT54C from AFE_REG1 would draw an unlimited charge current from REG1 (5 mA budget). R301 = 1 kΩ (3.3 mA) is mandatory if C311 is fitted.
* **F10. I2C2 pull-ups 2.2 kΩ, not 4.7 kΩ.** J801 extends the bus off-board; 4.7 kΩ meets Fm rise time only up to 75 pF.
* **F11. Flash second source promoted.** W25Q64JVSSIQ is at 227 pcs on LCSC. GD25Q64ESIG has the same pin-out and 208-mil footprint (GD25Q64E p.6, p.49). Firmware must handle both JEDEC IDs.
* **F12. Dry contacts.** SMAJ36CA clamps below the photoMOS 60 V (VC 58.1 V), so the contacts are specified for **≤ 30 V working** (12/24 V gen-start / alarm loops).
* **F13. Ownership.** ARCHITECTURE §3 puts the dry contacts on sheet 05 (U501/U502/J501). This BOM numbers them U803/U804/J802 on sheet 08 as the brief asked; the coordinator picks one. DI_AUX1 shares J802 pin 5; pin 6 is GND_PWR.

## 7. Cross-sheet duplicates to resolve (listed here, may also be in another group's BOM)

| Here | Other owner | Part |
|---|---|---|
| D301 BAT54C (VBAT_MCU OR) | B / sheet 01 `D_VBAT` | keep one (recommend C37704) |
| R824 1 MΩ WAKE_BTN_N → AFE_REG1 | B / sheet 01 latch | keep one |
| R825–R828 100 kΩ PDs on EN_ISO / EN_ESP / BAL_EXT_EN / EN_12V | B / sheet 01 load switches, C (BAL_EXT_EN) | keep one per net |
| R1013 + C1010 NTC_SHUNT bias / filter at PB2 | A / sheet 04 | bias belongs on the control board (B2B), keep here |
| RT1001 / RT1002 board NTCs | C parts table (RT_FET1 + board NTCs) | keep here; RT_FET1 stays with A/C |
| U803 / U804 / J802 / D811 / D812 / R822 / R823 dry contacts | ARCHITECTURE sheet 05 (U501/U502/J501) | coordinator |
| SW601 / SW602 (sheet 06) | G-comms | swap C3293144 → C40736 (−40 °C), F4 |
| FET_EN 100 kΩ PD, PWR_HOLD 1 MΩ PD | A sheet 07 / B sheet 01 | **not** duplicated here (must sit on the power board / latch for the fail-safe states) |

## 8. Questions for the owner

1. **U302:** use TPS3828-33 (open-drain, recommended), or keep TPS3823 with a 1 kΩ series resistor on NRST?
2. **LSE:** keep the 9 pF Epson FC-135 (Extended, 2.3× gm margin), or use the 12.5 pF Basic C32346 with 18 pF caps (1.25× margin)?
3. **X5R allowed?** If yes, the 4.7 µF bulk becomes Basic C1779 and one Extended line goes away.
4. **D-31 buzzer:** fit QMB-09B-05 on +5V (THT, −40 °C), or leave the chain DNP? It is DNP here.
5. **LED supply:** accept green on +5V and red / photoMOS on +3V3 (F3)? This reverses the integrator's "LEDs on +3V3".
6. **Supercap C311:** fit or not? If yes, a verified part and footprint are still needed. It is DNP and UNVERIFIED.
7. **Dry contacts:** is ≤ 30 V working (SMAJ36CA) acceptable? Is DI_AUX1 a dry contact to GND only (no 12/24 V signal)?
8. **J801:** Molex PicoBlade (−40 °C, friction lock) as the DNP front-panel connector, instead of JST GH (−25 °C)?
9. **SWD header:** cheap unshrouded XunPu (Extended, 1,810 pcs), or Samtec FTSH-105-01-L-DV-K (C448647, $1.45, −55…125 °C)?
10. **AFE_FLT_* read-back on U801 (F8):** keep, with C/A choosing the pull-down value, or drop the read-back?

## 9. Firmware notes forced by these parts

* Set LSEDRV ≥ 10 (11 recommended) for Y302.
* TCA9535 power-up state: all ports are inputs, so LEDs are off, photoMOS contacts open and enables are held off by R825–R828. Re-write both expanders after every MCU reset; there is no reset pin.
* Mux: drive EN (MUX_INH) low only while sampling, and wait ≥ 5 ms after a channel change. S5 / S6 are tied to GND_PWR (expect 0). S7 is the 50 % ratiometric check of the bias / ADC path.
* WDI floats while the MCU is in reset, which disables the watchdog (SLVS165J p.2). Toggle it within 0.9 s once started.
