# Research summary — beat Daly / JBD / JK with a compact 16S ESS BMS (2026-11-17)

Sources: `01_bq76952_features.md`, `02_competitors.md`, `03_balancing.md`, `04_shunt_powerpath.md`, `05_system_features_mcu.md` (same folder). Every number below is from those reports (datasheet pages cited there) or marked est. Nothing in the project was changed.

## 1. Where we stand vs competitors
**Table stakes we lack:** sleep / wake (biggest gap: our rails are always on; they sleep at 50–500 µA), SOC LEDs + RUN/ALM, Bluetooth app, 2 dry contacts, heater output, parallel packs (RJ45 x2, 2nd RS-485, pack address), RTC-stamped logs, field firmware update, inverter protocol library (firmware).
**Differentiators nobody documents:** MCU-independent hardware trip; welded-switch / pre-charge fault detection; per-cell + busbar resistance diagnostics (real SOH); better SOC (~±3 % est. vs their ±5 %); open published protocols + deep timestamped log + signed OTA; true isolation; 2 CAN.

## 2. Decisions that set the architecture
| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | Power switching | (a) on-board back-to-back high-side N-FETs driven by BQ76952 CHG/DSG + PCHG/PDSG pre-charge; (b) external contactors (today); (c) both as variants | (a) — what competitors and TI intend; compact; uses the AFE fully. Keep the contactor driver channels as optional outputs (breaker shunt-trip / external contactor) |
| D2 | Rating, size, chemistry | 100 A on 160x100 (4+4 FETs); 200 A on ~220x100 or control + power boards (8+8 FETs, ~25–35 W loss, Al plate, Cu bars, M8 lugs, 2 oz outer); LFP only vs + NMC (needs 120–150 V FETs) | 200 A, LFP only (100 V FETs), size per D1 |
| D3 | MCU | keep STM32G431CBT6 (1 CAN, pins exhausted) / STM32G473RCT6 LQFP-64 (3 FDCAN, 256 KB, +$0.70) / NXP S32K144 (AEC-Q, firmware rewrite) | G473RCT6 (no STM32G4 is AEC-Q; S32K only if AEC-Q is mandatory) |
| D4 | AFE link | I2C + CRC vs SPI | I2C + CRC (SPI not faster here, costs 2 pins); fix SCL to a real I2C pin, drop PB9 |
| D5 | Balancing | internal only / improved passive (NPN SS8050 per TI SLUAA81A, ~105 mA guaranteed) + active-balancer header / LTC3300 active (~$80–120) | improved passive + header + charge-based balancing firmware |

## 3. Changes per sheet (after D1–D5)
* **01 Power:** fix D1 TVS (reversed, too low), U1 RON to GND; sleep/wake latch on LM5164 EN; load switches on iso / ESP32 / sense rails; +5V buck upgrade; isolated supply 2 W (or 2 x 1 W); +12V sizing per D1; rail LEDs DNP.
* **02 AFE:** REG0 NPN pre-regulator, BREG fixed, CP1 to BAT; PACK via 10k to bus; NTCs on TS1/TS3/HDQ/CFETOFF, TS2 = wake, NTC caps ≤3.3 nF; DCHG/DDSG as fault outputs; R_VC16 20 R; balance channels per D5 (gate resistor / clamp); DNP FUSE footprint; LFP OTP image at end of line (10–12 V, no cells).
* **03 MCU:** MCU per D3; I2C pin fix + ALERT pull-up; RTC crystal; FRAM FM25V02A + 8 MB flash; DIP = pack address; I/O expander for LEDs / button / dry contacts; internal comparators + DAC as fast bidirectional latched OC trip; one timer for all coil/heater outputs.
* **04 Current:** on-board shunt 100 µΩ (2 x WSLP5931 0.2 mΩ, C413492); separate Kelvin filters for AFE (100 R / 100 nF) and amp; INA240A1 on +3V3 (±500 A → 0.65–2.65 V); latched independent trip; AFE coulomb counter = main gauge.
* **05 Power:** per D1 — FET banks + PNP fast turn-off + TVS clamp (SM8S class) + pre-discharge P-FET with R_PRE1; hardware AND gate-kill (AFE fault, OC latch, MCU); heater + fan drivers; dry contacts.
* **06 Comms:** 2nd isolated CAN + 2nd isolated RS-485 (parallel link), RJ45 x4; TJA1051 VIO tied; ISO7721 decoupling; ESP32-C3-MINI-1 module (BLE / WiFi / OTA); isolated USB-C service port (optional).

## 4. Part data is wrong in many places (must audit before anything is ordered)
LCSC numbers that point to other parts: U_MCU1 (C529329 = STM32G030), U_485_1 (an FPC connector), ISO7721 (a zener), U_CAN1 (a resistor), SW_CFG1, U3 (a resistor), R_BL (4.7 k 1206), Q_BL (does not exist), C_DF; U_MEM1 / U4 not found. A full live part audit of every sheet is needed (open question 10 in `PROJECT.md`).

## 5. Not verified (summary)
Live JLC stock/price for most power parts; FET SOA curves; shunt pulse rating; SS8050 datasheet; REG0 default on BQ7695202; DDSG/DCHG response time (bench test); OTP PF write at 16S; G473 reference manual details; Pylontech protocol documents; competitor specs partly from listings (marked in `02_competitors.md`).
