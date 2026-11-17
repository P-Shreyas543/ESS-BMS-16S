# BOM G4: sheets 05 Aux Outputs, 06 Communications, 09 Wireless

P3 part selection for the 16S LFP ESS BMS (BQ76952, STM32G473RCT6). Written 2026-11-17. Read-only on the project; nothing in the repository was changed.

**Inputs:** `docs/ARCHITECTURE.md` (D-01..D-16 decided, D-17+ open), `docs/architecture/D_mcu_comms_io.md`, `docs/architecture/A_power_stage.md` §9, `instruction.md` §3.3 / §5, `PROJECT.md` §3 / §5, and the current `05_Power_Actuators` / `06_Communications` sheets for field checks.

**How the parts were verified:**
* Every LCSC number was checked live this session against two sources:
  * the LCSC product API (`wmsc.lcsc.com/ftps/wm/product/detail`) for MPN, manufacturer, package and LCSC stock;
  * the JLCPCB parts API (`jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`) for Basic/Extended, JLC stock and the price at quantity 100.
* The MPN matched exactly between the two sources for every line (the script asserts this).
* Data sheets were downloaded from the LCSC links and read with pypdfium2. Drawings that are only images (RJ45, terminal, DIP) were rendered and read visually. Page numbers are the printed pages; for TI's ISO7721 they are PDF page numbers, marked "pdf p.".
* KiCad footprint names were checked against the KiCad `kicad-footprints` master on GitLab.

**Full per-reference data** (all 13 playbook columns, one row per reference, 139 rows) is in `bom_G4.csv`. The table below groups identical parts.

**Reference ranges:**
* Sheet 05 uses 501–549. **The heater group should start at 550** to avoid collisions.
* Sheet 06 uses 601–629.
* Sheet 09 uses 901–909.

## 1. Table (grouped)

| Refs | Qty | Value | Footprint | LCSC | MPN | Manufacturer | Spec | B/E | Stock (JLC / LCSC) | Unit $ @100 | DS check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q501, Q502, Q503 | 3 | AO3400A | `Package_TO_SOT_SMD:SOT-23` | C20917 | AO3400A | AOS | 30V 5.7A N-FET logic-level | Basic | JLC 1190745 / LCSC 603450 | 0.0621 | SOT-23 pin 1 G, 2 S, 3 D (AO3400A DS p.1); VDS 30 V, VGS +-12 V; RDS(on) < 48 mOhm @ VGS 2.5 V (p.1); VGS(th) 0.65-1.45 V (p.2) |
| R501, R504, R507, R508, R902, R908, R909 | 7 | 1k 1% | `Resistor_SMD:R_0603_1608Metric` | C21190 | 0603WAF1001T5E | UNI-ROYAL | 0603 100mW | Basic | JLC 26039662 / LCSC 0 | 0.0017 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 1kΩ 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount R" |
| R502, R509, R510 | 3 | 100k 1% | `Resistor_SMD:R_0603_1608Metric` | C25803 | 0603WAF1003T5E | UNI-ROYAL | 0603 100mW | Basic | JLC 14257115 / LCSC 4974900 | 0.0029 | Passive: rating from JLC attributes "-55℃~+155℃ 100kΩ 100mW 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount" |
| D501, D506, D507 | 3 | SS34 | `Diode_SMD:D_SMA` | C8678 | SS34 | MDD(Microdiode Semiconductor) | 40V 3A Schottky SMA | Basic | JLC 2618110 / LCSC 1743320 | 0.0351 | SMA(DO-214AC), 40 V / 3 A (listing + JLC attributes); MDD datasheet not opened |
| R503, R901, R903, R904, R907 | 5 | 10k 1% | `Resistor_SMD:R_0603_1608Metric` | C25804 | 0603WAF1002T5E | UNI-ROYAL | 0603 100mW | Basic | JLC 41239091 / LCSC 0 | 0.002 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 10kΩ 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount " |
| C501 | 1 | 1nF 50V | `Capacitor_SMD:C_0603_1608Metric` | C1588 | CL10B102KB8NNNC | Samsung Electro-Mechanics | X7R 0603 | Basic | JLC 5445548 / LCSC 599550 | 0.0063 | Passive: rating from JLC attributes "-55℃~+125℃ 1nF 50V X7R ±10% 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS" |
| J502 | 1 | S3B-PH-K(LF)(SN) | `Connector_JST:JST_PH_S3B-PH-K_1x03_P2.00mm_Horizontal` | C545716 | S3B-PH-K(LF)(SN) | JST | JST PH 3P RA THT | Extended THT | JLC 13011 / LCSC 13010 | 0.0513 | 2.0 mm pitch, 2 A/pin, -25..+85 C (listing); KiCad stock fp named for this MPN |
| U501, U502 | 2 | GAQY212GS | `Package_SO:SOP-4_4.4x2.6mm_P1.27mm` | C7435107 | GAQY212GS | SUPSiC | 60V 0.8A photoMOS 2.5kVrms | Extended | JLC 130418 / LCSC 104287 | 0.4047 | SOP-4, pin 1 LED A, 2 LED K (DS p.1); 60 V / 0.8 A, 1.5 A 100 ms, 2500 Vrms (p.2); IF recommended 5-30 mA, IF(on) max 2 mA (p.2) |
| R505, R506 | 2 | 330R 1% | `Resistor_SMD:R_0603_1608Metric` | C23138 | 0603WAF3300T5E | UNI-ROYAL | 0603 100mW | Basic | JLC 2193205 / LCSC 0 | 0.002 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 330Ω 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount " |
| D502, D503 | 2 | SMAJ33CA | `Diode_SMD:D_SMA` | C115251 | SMAJ33CA | MDD(Microdiode Semiconductor) | 33V 400W bidir SMA | Extended | JLC 186463 / LCSC 186460 | 0.044 | SMA; VRWM 33 V, VBR 36.7-40.6 V, VC 53.3 V @ 7.5 A (MDD DS p.2) < 60 V photoMOS rating |
| J501, J503 | 2 | DB128V-5.08-4P-GN-S | `Automotive_ESS_BMS:TerminalBlock_Dorabo_DB128V-5.08-4P_1x04_P5.08mm` | C2915641 | DB128V-5.08-4P-GN-S | DORABO | 4P 5.08mm screw terminal THT | Extended THT | JLC 89940 / LCSC 89940 | 0.3393 | Drawing: pitch 5.08, PCB hole 1.6 mm, pin 0.8x1.0 mm, 300 V / 16 A UL, -40..+105 C. KiCad Phoenix MKDS-1,5-4-5.08 has the same pitch but 1.3 mm drill (< 1.6 recommended) -> project copy with 1.6 mm drill |
| D504, D505 | 2 | BZT52C5V6 | `Diode_SMD:D_SOD-123` | C173406 | BZT52C5V6 | MDD(Microdiode Semiconductor) | 5.6V 500mW zener SOD-123 | Extended | JLC 371728 / LCSC 371700 | 0.0149 | SOD-123, VZ 5.32-5.88 V, 500 mW (listing / JLC attributes); MDD DS not opened |
| D508, D509 | 2 | KT-0805G | `LED_SMD:LED_0805_2012Metric` | C2297 | KT-0805G | Hubei KENTO Elec | green 0805 LED | Basic | JLC 3160704 / LCSC 2227000 | 0.0164 | 0805, VF 2.6-3.1 V, 5 mA test (listing); KENTO DS not opened |
| R511, R512, R611, R612 | 4 | 4.7k 1% | `Resistor_SMD:R_0603_1608Metric` | C23162 | 0603WAF4701T5E | UNI-ROYAL | 0603 100mW | Basic | JLC 14387752 / LCSC 2083500 | 0.0028 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 4.7kΩ 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount" |
| U601, U602 | 2 | CA-IS3050CW | `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` | C41784143 | CA-IS3050CW | Chipanalog | Iso CAN FD 5Mbps 5kVrms | Extended | JLC 2095 / LCSC 2092 | 0.6144 | SOIC16-WB 10.30x7.50 (IS3050C p.1) = KiCad SOIC-16W_7.5x10.3mm_P1.27mm; pins 1 VCC1, 2/7/8 GND1, 3 RXD, 6 TXD, 9/10/15 GND2, 12 CANL, 13 CANH, 16 VCC2 (p.4); VCC1 3.0-5.5 V, VCC2 4.5-5.5 V (p.6); creepage 8 mm (p.8); ICC2 dom 73 mA max (p.10) |
| U603, U604 | 2 | CA-IS3082WX | `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` | C970942 | CA-IS3082WX | Chipanalog | Iso RS-485 500kbps 5kVrms | Extended | JLC 9576 / LCSC 9567 | 0.6619 | SOIC16-WB 10.30x7.50 (p.1) = KiCad SOIC-16W_7.5x10.3mm_P1.27mm; pins 1 VDDA, 3 RO, 4 RE, 5 DE (weak PD), 6 DI, 12 A, 13 B, 16 VDDB; 0.1 uF + 1 uF each side (p.5); creepage/clearance 8 mm (p.8); VDDA 2.375-5.5 V, VDDB 3-5.5 V (p.7) |
| C601, C602, C603, C604, C607, C608, C609, C610, C620, C621, C622, C623, C902 | 13 | 100nF 50V | `Capacitor_SMD:C_0603_1608Metric` | C14663 | CC0603KRX7R9BB104 | YAGEO | X7R 0603 | Basic | JLC 31861348 / LCSC 1500 | 0.0058 | Passive: rating from JLC attributes "100nF 50V X7R ±10% 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS" |
| C605, C606, C611, C612, C613, C614, C619, C903 | 8 | 1uF 50V | `Capacitor_SMD:C_0805_2012Metric` | C28323 | CL21B105KBFNNNE | Samsung Electro-Mechanics | X7R 0805 | Basic | JLC 4179156 / LCSC 161250 | 0.0213 | Passive: rating from JLC attributes "1uF 50V X7R ±10% 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS" |
| C615, C901 | 2 | 10uF 25V | `Capacitor_SMD:C_1206_3216Metric` | C14860 | CL31B106KAHNNNE | Samsung Electro-Mechanics | X7R 1206 | Extended | JLC 1680184 / LCSC 1603540 | 0.1431 | Passive: rating from JLC attributes "10uF 25V X7R ±10% 1206 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS" |
| R601, R602, R603, R604 | 4 | 60.4R 1% | `Resistor_SMD:R_0603_1608Metric` | C23090 | 0603WAF604JT5E | UNI-ROYAL | 0603 100mW | Extended | JLC 37486 / LCSC 13800 | 0.0074 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 60.4Ω 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount" |
| C616, C617 | 2 | 4.7nF 50V | `Capacitor_SMD:C_0603_1608Metric` | C53987 | 0603B472K500NT | FH | X7R 0603 | Basic | JLC 808855 / LCSC 98300 | 0.0045 | Passive: rating from JLC attributes "4.7nF 50V X7R ±10% 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS" |
| R605, R606 | 2 | 120R 1% | `Resistor_SMD:R_1206_3216Metric` | C17909 | 1206W4F1200T5E | UNI-ROYAL | 1206 250mW | Basic | JLC 530118 / LCSC 136700 | 0.0046 | Passive: rating from JLC attributes "-55℃~+155℃ 120Ω 200V 250mW Thick Film Resistor ±1% ±100ppm/℃ 1206 Chip Resistor - Surface Mount" |
| R607, R608, R609, R610 | 4 | 560R 1% | `Resistor_SMD:R_0603_1608Metric` | C23204 | 0603WAF5600T5E | UNI-ROYAL | 0603 100mW DNP | Basic | JLC 2340129 / LCSC 1695500 | 0.0033 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 560Ω 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount " |
| R613, R614, R615, R616, R617 | 5 | 33R 1% | `Resistor_SMD:R_0603_1608Metric` | C23140 | 0603WAF330JT5E | UNI-ROYAL | 0603 100mW | Basic | JLC 3016933 / LCSC 677700 | 0.0024 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 33Ω 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount R" |
| L601, L602 | 2 | ACT45B-510-2P-TL003 | `Automotive_ESS_BMS:L_CommonModeChoke_TDK_ACT45B-510-2P` | C76584 | ACT45B-510-2P-TL003 | TDK | 51uH 200mA CAN CMC DNP | Extended | JLC 12985 / LCSC 3554 | 0.3555 | 4.5x3.2 mm SMD, 51 uH, 200 mA (listing; DS downloaded, not studied). No KiCad stock footprint -> project footprint |
| R618, R619, R620, R621 | 4 | 0R | `Resistor_SMD:R_0603_1608Metric` | C21189 | 0603WAF0000T5E | UNI-ROYAL | 0603 jumper | Basic | JLC 16637665 / LCSC 7346000 | 0.0021 | Passive: rating from JLC attributes "-55℃~+155℃ 0Ω 100mW 75V Thick Film Resistor ±1% 0603 Chip Resistor - Surface Mount ROHS" |
| R622, R623, R624, R625 | 4 | 0R | `Resistor_SMD:R_0603_1608Metric` | C21189 | 0603WAF0000T5E | UNI-ROYAL | 0603 jumper DNP | Basic | JLC 16637665 / LCSC 7346000 | 0.0021 | Passive: rating from JLC attributes "-55℃~+155℃ 0Ω 100mW 75V Thick Film Resistor ±1% 0603 Chip Resistor - Surface Mount ROHS" |
| SW601, SW602 | 2 | DSHP04TSGER | `Button_Switch_SMD:SW_DIP_SPSTx04_Slide_KingTek_DSHP04TS_W7.62mm_P1.27mm` | C3293144 | DSHP04TSGER | kangshen | 4-pole DIP 1.27mm SMD | Extended | JLC 63136 / LCSC 55472 | 0.4325 | Drawing: pad rows 6.35/8.89 -> 7.62 centres, 1.27 pitch = KiCad KingTek DSHP04TS fp; switching 25 mA @ 24 VDC, non-switching 100 mA @ 50 V; op. temp -30..+85 C (drawing notes 1.2, 3.1, 3.2) |
| D601, D602, D603 | 3 | SZNUP2105LT1G | `Package_TO_SOT_SMD:SOT-23` | C233494 | SZNUP2105LT1G | onsemi | 24V 350W CAN TVS AEC-Q101 | Extended | JLC 180724 / LCSC 180370 | 0.0517 | SOT-23, pins 1/2 = lines, 3 = GND (DS p.1); VRWM 24 V (p.2); 350 W 8/20 us (p.1); SZ = AEC-Q101 (p.2); KiCad symbol Power_Protection:NUP2105L |
| D604, D605, D606 | 3 | PSM712-LF-T7 | `Package_TO_SOT_SMD:SOT-23` | C32677 | PSM712-LF-T7 | PROTEK | -7/+12V 600W RS-485 TVS | Basic | JLC 124236 / LCSC 59940 | 0.2677 | SOT-23, pins 1/2 = lines, 3 = common (DS p.1, p.5); VWM 7 V / 12 V asymmetric, 600 W 8/20 us (p.2); KiCad symbol Diode:SM712_SOT23 |
| J601, J602, J603, J604 | 4 | KH-RJ45-58-8P8C | `Automotive_ESS_BMS:RJ45_Kinghelm_KH-RJ45-58-8P8C_Horizontal` | C2683360 | KH-RJ45-58-8P8C | kinghelm | RJ45 shielded RA no-LED THT | Extended THT | JLC 3932 / LCSC 3725 | 0.2721 | Drawing (image, rendered): 8 pins 1.27/2.54 grid, 0.9 mm holes, 2x 3.2 mm pegs 11.43 apart, 2 shield tabs 15.13 apart; op. temp -25..+70 C; 125 VAC / 1.5 A. Pin/peg grid = KiCad Connector_RJ:RJ45_Amphenol_54602-x08_Horizontal, but that footprint has NO shield pads -> project footprint required |
| C618, C624 | 2 | 1nF 2kV | `Capacitor_SMD:C_1206_3216Metric` | C9196 | 1206B102K202NT | FH | X7R 1206 | Basic | JLC 1959364 / LCSC 465630 | 0.0228 | Passive: rating from JLC attributes "1nF 2kV X7R ±10% 1206 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS" |
| R626, R629 | 2 | 1M 1% | `Resistor_SMD:R_1206_3216Metric` | C17927 | 1206W4F1004T5E | UNI-ROYAL | 1206 250mW 200V | Basic | JLC 2774218 / LCSC 1558100 | 0.0042 | Passive: rating from JLC attributes "-55℃~+155℃ 1MΩ 200V 250mW Thick Film Resistor ±1% ±100ppm/℃ 1206 Chip Resistor - Surface Mount " |
| U605 | 1 | CH340C | `Package_SO:SOIC-16_3.9x9.9mm_P1.27mm` | C84681 | CH340C | WCH | USB-UART, internal clock | Extended | JLC 88534 / LCSC 86567 | 0.3342 | SOP-16 3.9 mm 1.27 pitch (CH340 DS p.2) = KiCad SOIC-16_3.9x9.9mm; VCC pin 16, V3 pin 4 (0.1 uF to GND at 5 V supply), UD+ 5, UD- 6 (p.3, p.5); no crystal (p.1); English DS V3C read via pdfium |
| U606 | 1 | ISO7721DR | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | C366164 | ISO7721DR | TI | 2ch digital iso 1F/1R | Extended | JLC 9092 / LCSC 9142 | 0.4227 | SOIC-8 D = KiCad SOIC-8_3.9x4.9mm; VCC1/VCC2 2.25-5.5 V (pdf p.1); 0.1 uF bypass each side (pdf p.26); D-package creepage 4 mm (pdf p.7) - USB service domain only |
| U607 | 1 | USBLC6-2SC6 | `Package_TO_SOT_SMD:SOT-23-6` | C7519 | USBLC6-2SC6 | ST | USB ESD 2-line + VBUS | Extended | JLC 40479 / LCSC 40420 | 0.1201 | SOT23-6L (DS p.1) = KiCad SOT-23-6; protects D+/D- and VBUS (p.1) |
| J605 | 1 | TYPE-C-31-M-12 | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 | TYPE-C-31-M-12 | Korean Hroparts Elec | USB-C 16P SMD receptacle | Extended | JLC 515037 / LCSC 496205 | 0.1478 | KiCad stock footprint named for this exact HRO MPN; LCSC drawing is image-only (not re-measured) |
| R627, R628 | 2 | 5.1k 1% | `Resistor_SMD:R_0603_1608Metric` | C23186 | 0603WAF5101T5E | UNI-ROYAL | 0603 100mW | Basic | JLC 18947823 / LCSC 13577000 | 0.0015 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 5.1kΩ 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount" |
| F601 | 1 | 200mA 24V | `Fuse:Fuse_1206_3216Metric` | C20984 | SMD1206P020TF | RUILON | 1206 PTC Ihold 0.2A | Extended | JLC 100343 / LCSC 98175 | 0.072 | RUILON SMD1206P020TF: Ihold 0.20 A, Itrip 0.46 A, Vmax 24 V, 1206 (DS p.2) |
| TP601 | 1 | RH-5000 | `TestPoint:TestPoint_Keystone_5000-5004_Miniature` | C5277086 | RH-5000 | ronghe | Red hook | Extended THT | JLC 209912 / LCSC 209910 | 0.0649 | Test hook, house default (instruction.md 5.5) |
| TP602 | 1 | RH-5001 | `TestPoint:TestPoint_Keystone_5000-5004_Miniature` | C5199801 | RH-5001 | ronghe | Black hook | Extended THT | JLC 108127 / LCSC 108125 | 0.0687 | Test hook, house default (instruction.md 5.5) |
| U901 | 1 | ESP32-C3-MINI-1-N4 | `Automotive_ESS_BMS:ESP32-C3-MINI-1` | C2838502 | ESP32-C3-MINI-1-N4 | ESPRESSIF | WiFi/BLE module 4MB 85C | Extended | JLC 26401 / LCSC 9228 | 2.1345 | 53-pad 13.2x16.6 mm module (ESP EN DS v2.2 p.35); 3.0-3.6 V (p.3); EN pin 8 must not float, RC 10k/1uF (p.11, p.34); strap GPIO2/8 float, GPIO9 weak PU (p.12-13); antenna keep-out (p.10); N4 = -40..85 C and marked NRND (p.3). No KiCad stock footprint (RF_Module has only C3-WROOM-02 / DevKitM-1) |
| R905 | 1 | 1k 1% | `Resistor_SMD:R_0603_1608Metric` | C21190 | 0603WAF1001T5E | UNI-ROYAL | 0603 100mW DNP | Basic | JLC 26039662 / LCSC 0 | 0.0017 | Passive: rating from JLC attributes "-55℃~+155℃ 100mW 1kΩ 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount R" |
| Q901 | 1 | AO3400A | `Package_TO_SOT_SMD:SOT-23` | C20917 | AO3400A | AOS | 30V 5.7A N-FET logic-level DNP | Basic | JLC 1190745 / LCSC 603450 | 0.0621 | SOT-23 pin 1 G, 2 S, 3 D (AO3400A DS p.1); VDS 30 V, VGS +-12 V; RDS(on) < 48 mOhm @ VGS 2.5 V (p.1); VGS(th) 0.65-1.45 V (p.2) |
| R906 | 1 | 100k 1% | `Resistor_SMD:R_0603_1608Metric` | C25803 | 0603WAF1003T5E | UNI-ROYAL | 0603 100mW DNP | Basic | JLC 14257115 / LCSC 4974900 | 0.0029 | Passive: rating from JLC attributes "-55℃~+155℃ 100kΩ 100mW 75V Thick Film Resistor ±1% ±100ppm/℃ 0603 Chip Resistor - Surface Mount" |

THT test pads (`TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm`, in_bom no, no LCSC): TP501 EXT1_DRAIN, TP502 EXT2_DRAIN, TP503 FAN_SW, TP603 CANH_INV, TP604 CANL_INV, TP605 CANH_LINK, TP606 CANL_LINK, TP607 RS485_INV_A, TP608 RS485_INV_B, TP609 RS485_LINK_A, TP610 RS485_LINK_B, TP611 +5V_USB, TP612 GND_USB, TP901 ESP_EN, TP902 ESP_BOOT, TP903 ESP_TXD, TP904 ESP_RXD

### Circuit notes (what the BOM assumes)
* **EXT_OUT1/2 (each channel):**
  * `+12V` → J503 coil → drain of Q502/Q503, source to `GND_PWR`.
  * SS34 flyback across the coil terminals, at the connector.
  * Gate path: `EXT_OUT1/2` (PC1/PC2, 3.3 V) → 1k → gate, with 100k gate–source and a BZT52C5V6 gate clamp.
  * ON LED: `+12V` → 4.7k → green LED → drain.
  * Per D-16 there is no diode-OR from the BQ FUSE pin.
* **Fan:**
  * Q501 is low-side, with 1k gate series, 100k pull-down and an SS34 flyback to `+12V`.
  * J502 pins: `+12V`, switched GND, `FAN_TACH`.
  * Tach: 10k pull-up to `+3V3`, 1k series, 1 nF.
* **Dry contacts:**
  * GAQY212GS LEDs run from `+3V3` through 330R and are sunk by the U801 expander.
  * SMAJ33CA across each contact.
  * J501 pinout: DRY1_A, DRY1_B, DRY2_A, DRY2_B.
* **CAN:**
  * Split termination: CANH → SWx-1 → 60.4R → midpoint ← 60.4R ← SWx-2 ← CANL, with 4.7 nF from the midpoint to `GND_ISO`.
  * A TVS sits at every RJ45 that carries CAN: J601, J603 and J604.
  * The CMC is DNP, with a 0R bypass on each line.
* **RS-485:**
  * 120R termination through SWx-3.
  * 560R bias is DNP.
  * A PSM712 sits at every RJ45 that carries RS-485: J602, J603 and J604.
* **SWx-4** is a spare pole.
* **USB service port:**
  * J605 → F601 PTC → `+5V_USB`.
  * USBLC6 on D+ / D− / VBUS; CC1/CC2 5.1k Rd.
  * CH340C TXD/RXD ↔ ISO7721DR ↔ `SVC_RX`/`SVC_TX` (PA10/PA9).
  * The shell goes to `GND_USB` through 1 nF 2 kV ∥ 1M.
  * D-33 says fit it, so it is **fitted**, not DNP.
* **ESP32-C3:**
  * Supply: 10 µF + 100 nF.
  * EN: 10k / 1 µF, with ESP_EN through 1k.
  * Straps: 10k pull-ups on GPIO9, GPIO8 and GPIO2.
  * UART: 1k in each line.
  * The D-46 ROM-flash option (R905, Q901, R906) is DNP.
* **ESP antenna keep-out:**
  * Place U901 at a board edge with the antenna end overhanging or flush.
  * No copper on any layer, and no parts, in the dotted keep-out zone (ESP DS p.10).
  * Keep the RJ45 shields, the Cu bars and the FET bank away from the antenna end.
  * Espressif's hardware design guide (≈15 mm clearance) was **not** opened.

## 2. Summary

| Item | Value |
|---|---|
| BOM lines (references) | 139 = 109 fitted + 13 DNP + 17 THT test pads (in_bom no) |
| By sheet (fitted) | 05: 30, 06: 68, 09: 11 |
| Fitted placements | 73 Basic + 36 Extended |
| Unique LCSC numbers | 41 (20 Basic, 21 Extended; 20 Extended fitted, ACT45B CMC is DNP only) |
| UNVERIFIED LCSC numbers | **0** |
| Parts cost per board, qty 100 (est.) | **$11.52** (JLC price @100: sheet 05 $2.01, 06 $7.19, 09 $2.32) |
| Extended setup fee (est.) | 20 × $3 per order ÷ 100 boards ≈ **$0.60 / board** |
| THT hand-solder (est.) | ≈ 60 joints (4 × RJ45 12 pins, 2 × 4P terminal, JST 3P, 2 hooks) ≈ $0.3–0.5 / board |
| **Total, qty 100 (est.)** | **≈ $12.5 per board** for G4 sheets |

**Extended parts (fitted):**
* Comms ICs:
  * CA-IS3050CW C41784143
  * CA-IS3082WX C970942
  * CH340C C84681
  * ISO7721DR C366164
* Protection:
  * USBLC6-2SC6 C7519
  * SZNUP2105LT1G C233494
  * SMAJ33CA C115251
  * BZT52C5V6 C173406
  * SMD1206P020TF C20984
* Connectors and switches:
  * KH-RJ45-58-8P8C C2683360
  * TYPE-C-31-M-12 C165948
  * DSHP04TSGER C3293144
  * S3B-PH-K C545716
  * DB128V-5.08-4P C2915641
* Passives:
  * 60.4R 0603 C23090 (no Basic 60–62 Ω exists)
  * 10 µF X7R 1206 C14860 (no Basic 10 µF X7R; the Basic X5R option is C15850, owner question Q3)
* Other:
  * ESP32-C3-MINI-1-N4 C2838502
  * GAQY212GS C7435107
  * RH-5000 C5277086
  * RH-5001 C5199801

**THT parts:**
* J601–J604 KH-RJ45 (4×)
* J501 and J503 DB128V 4P terminals
* J502 JST PH
* TP601 and TP602 hooks
* 17 THT test pads (bare pads, not assembled)

**Low-stock watch:** no part is below 500. The tightest are:
* CA-IS3050CW: JLC 2,095 (2 per board, ≈ 10 builds of 100)
* KH-RJ45-58-8P8C: JLC 3,932 (4 per board, ≈ 9 builds)

C21190, C25804 and C23138 show LCSC stock 0 but millions at JLC. This does not matter for JLC assembly.

**Basic-vs-cost note:** the Basic PSM712 (ProTek C32677, $0.27) was used per the playbook. The UMW PSM712 C2687124 (Extended, $0.037) would save ≈ $0.66 per board minus one setup fee.

## 3. UNVERIFIED items

No LCSC number is unverified. These *data* items are not verified:
* Data sheets not opened or not readable:
  * SS34 (MDD), BZT52C5V6 (MDD), KT-0805G and ACT45B: ratings come from listings.
  * TYPE-C-31-M-12: image only. KiCad has a footprint named for this MPN, but it was not re-measured.
* KH-RJ45-58-8P8C:
  * The drawing was read (image).
  * The shield-tab pad size and drill for a new footprint must be taken from the drawing (tabs 0.7 × 1.7 mm, 15.13 mm apart). Check them before layout.
* CH340C:
  * The English data sheet V3C was read.
  * The "TNOW → DTR# via 4.7k" behaviour depends on the lot. It only matters for the optional one-click flashing.
* Shield RC values (1 nF 2 kV ∥ 1M), the CAN CMC need, and the 4.7 nF split capacitor: these await the EMC test (D §3.5).
* The ESP antenna clearance figure (Espressif hardware design guide) was not opened.
* The fault-case dissipation of the 0603 60.4R split resistors with CANH/CANL shorted to 24 V is not covered (F7).

## 4. Questions for the owner / coordinator

* **Q1. EXT FET.** Accept AO3400A (Basic, logic-level) in place of A's SQ2318AES for EXT_OUT1/2 (F1)? The other option is to keep SQ2318AES (AEC-Q101) and add a +5 V / +12 V gate buffer.
* **Q2. ESP module.** Keep ESP32-C3-MINI-1-N4 (NRND, 26k stock), or move to Espressif's current revision?
  * ESP32-C3-MINI-1-**H4X** (C41349510, 105 °C, 1,641 stock, +$0.12)
  * **-N4X**: 0 stock at JLC
* **Q3. Bulk caps.** X5R allowed? Basic CL21A106KAYNNNE C15850 (10 µF 25 V X5R 0805) would replace Extended C14860 at 3 places.
* **Q4. EXT output protection.** Add a PTC or e-fuse per EXT channel? An external harness short loads the `+12V` buck (shared with the fan and heater gate). None is fitted now.
* **Q5. INV-CAN pins 1/2/7/8.** D-28 is still open. 0R DNP options R622–R625 are provided.
* **Q6. Auto-address on the link RJ45 pins 7/8** (D §3.5). Not provided, because it conflicts with RS485_LINK_A/B on the same pins. Confirm it is dropped.
* **Q7. DIP spare pole.** Use SWx-4 to switch the 560R bias (fitted, so a field-selectable bias), or leave it spare?

## 5. Design-impacting findings

* **F1. SQ2318AES cannot be driven from a 3.3 V MCU pin.**
  * Vishay specifies RDS(on) only at 4.5 V and 10 V. VGS(th) is up to 2.5 V (SQ2318AES DS p.1–2), and it rises further at −40 °C.
  * The listed part number itself is right: C3280170 = SQ2318AES-T1_BE3, Vishay, AEC-Q101, pins 1 G / 2 S / 3 D.
  * **Selected instead: AO3400A C20917 (Basic).** It has RDS(on) < 48 mΩ at VGS 2.5 V and VGS(th) ≤ 1.45 V (AO3400A DS p.1–2), the same SOT-23 G/S/D pin-out, and it is already the fan FET.
  * Limits: VDS 30 V (the coil clamp is ≈ 12.6 V) and VGS ±12 V, hence the 5.6 V gate zener rather than the old 18 V BZX84.
* **F2. ESP32-C3-MINI-1-N4 and -H4 are NRND** (ESP DS v2.2 p.3). Espressif recommends the -N4X / -H4X (chip v1.1). Only -H4X is stocked (Q2).
  * The external-antenna module that D Q10 / D-32 said was "not found" **exists**: ESP32-C3-MINI-1U-H4, C3013922, 2,399 at JLC, 105 °C, NRND. This matters if the enclosure is steel.
* **F3. KiCad stock footprints missing.** Four project footprints are needed in `Automotive_ESS_BMS`, each checked against its drawing:
  * **RJ45 (KH-RJ45-58):** the pin and peg grid matches `Connector_RJ:RJ45_Amphenol_54602-x08_Horizontal` (1.27 / 2.54 pitch, 3.2 mm pegs 11.43 mm apart), but that footprint has **no shield pads**. Make a project copy with the 2 shield tabs.
  * **ESP32-C3-MINI-1:** no KiCad stock footprint. Use the Espressif KiCad library or easyeda2kicad C2838502.
  * **ACT45B CMC:** no KiCad stock footprint.
  * **DB128V terminal:** KiCad's Phoenix MKDS-1,5-4-5.08 has a 1.3 mm drill, against the vendor's 1.6 mm recommendation for 0.8 × 1.0 mm pins.

  These names are used in the CSV as `Automotive_ESS_BMS:…` and are marked as to be created.
* **F4. CA-IS footprints are fine.** CA-IS3050CW and CA-IS3082WX are SOIC16-WB 10.30 × 7.50 mm (IS3050C p.1, IS3082 p.1). This matches stock `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm`. Creepage and clearance are 8 mm (p.8), which meets the 6.5 mm D-10 target if the board slot / keep-out is kept.
  * CA-IS3082WX needs **0.1 µF + 1 µF on each side** (IS3082 p.5). D listed 0.1 µF only.
* **F5. Temperature limits below −40 °C** (D-14 rates the board at −40…85 °C):
  * KH-RJ45 −25…+70 °C (drawing note 9.2)
  * DSHP04TSGER −30…+85 °C (drawing note 1.2)
  * JST PH −25…+85 °C (listing)

  These need an owner waiver or −40 °C alternatives.
* **F6. Termination DIP current.** DSHP04TSGER is rated 25 mA switching and 100 mA non-switching (drawing 3.1–3.2). The 17–21 mA termination current fits; this closes D's U9.
* **F7. The 120R RS-485 terminators must be 1206.** At 3 V differential they dissipate 75 mW, which is 75 % of a 0603 rating; 1206 brings it to 30 %. The 60.4R CAN legs at 17 mW are fine in 0603. In a CANH/CANL short to 24 V, any split terminator and the DIP pole are overstressed; this is accepted, as in common practice.
* **F8. The PSM712 is a different TVS from the SM712 asked for.** PSM712 (ProTek, Basic C32677) is the SM712-equivalent −7 / +12 V asymmetric part (PSM712 DS p.2). The genuine SM712-02HTG is C172881 (Littelfuse, Extended, $0.29).
  * For CAN, NUP2105L is verified as **C14486** (NUP2105LT1G) and **C233494** (SZNUP2105LT1G, AEC-Q101, used). D's PESD1CAN C343993 is also valid.
* **F9. Wrong LCSC numbers in today's sheets 05 / 06** (live lookups):

| Ref (today) | Field LCSC | LCSC returns | Re-resolved |
|---|---|---|---|
| U_485_1 THVD1450DR | C395353 | JUSHUO AFC12-S12CCC-00 FPC connector | C2671361 THVD1450DR (4,682); part removed, now U603/U604 CA-IS3082WX C970942 |
| U_ISO_* ISO7721-Q1 | C129202 | Tak Cheong ZM4733AR13 zener, 0 stock | C366164 ISO7721DR (U606 only) |
| U_CAN1 TJA1051T/3 | C385473 | TyoHM 220 kΩ THT resistor | C58988 TJA1051T/3,118 (2,548); removed, now U601/U602 C41784143 |
| J_CAN1, J_485_1 (2.54 1x4) | C224347 | NVE IL3422-3E isolated transceiver | removed, now J601–J604 C2683360 |
| D_TVS_CAN1 NUP2105LT1G | C12948 | no record | C233494 SZNUP2105LT1G / C14486 NUP2105LT1G |
| D_TVS_485_1 SM712 | C19002 | no record | C32677 PSM712 (Basic) / C172881 SM712-02HTG |
| Q_POS1, Q_NEG1 (Q_PRE1) SQ2318EY | C148416 | Winsok WSP4805 dual P-FET SOP-8 | C3280170 SQ2318AES-T1_BE3 exists; AO3400A C20917 chosen (F1) |
| D_Z_POS1/NEG1/PRE1 BZX84-C18 | C2194 | no LCSC record (JLC: YXC HC-49U crystal) | BZX84C18LT1G C82474 if 18 V kept; 5.6 V C173406 used (F1) |
| D_FLY1-3 SS34 | C8679 | no record | C8678 SS34 MDD, Basic |
| D_LED_P1 / N1 "Green" | C72041 | Everlight blue LED, 0 stock | C2297 KT-0805G green, Basic |
| D_LED_R1 "Amber" | C72042 | Everlight yellow-green, 0 stock at JLC | precharge LED, other group |
| R_TRM1/2 60.4R | C23145 | 357 kΩ 0603 | C23090 60.4 Ω |
| R_GS1-3 47k 0603 | C25792 | 47 kΩ 0402 | G4 uses 100k C25803 |
| R_FS_A1/B1 560R | C23179 | 470 Ω | C23204 560 Ω |
| J_PRE1 / J_CONT1 MKDS 5.08 | C462689 / C462691 | ADI LT3494 boost IC / LTC4054 charger IC | C2915641 DB128V 4P (J501/J503); J_PRE1 belongs to another group |
| R_HV1/2 1M 1206 | C17938 | no record | other group; C17927 = 1M 1206 Basic |
| R_HV_BOT1 20.0k 0603 | C25768 | 22 kΩ 0402 | other group |
| C_TRM1 4.7nF | C1586 | 47 nF 0402 | C53987 4.7 nF 0603 Basic |
| C_CAN2 4.7uF 0805 | C19668 | no record | removed (C615 10 µF) |
| U4 B0505S-1WR3 | C265225 | no record | other group (2 W module, D-09) |

* **F10. EXT terminal current path.** Two coils share J503's `+12V` pins at ≤ 0.4 A each. The terminal is 16 A, so this is fine. The `+12V` budget (D-07) must include 2 coils plus the fan.
