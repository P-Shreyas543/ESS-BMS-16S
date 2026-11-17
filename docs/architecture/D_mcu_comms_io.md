> Detailed section; where it conflicts with ../ARCHITECTURE.md, ARCHITECTURE.md wins.

# D: MCU, communications, I/O, connectors and sheet plan (architecture)

Part D of the architecture for the 16S LFP ESS BMS (200 A, on-board high-side FETs, STM32G473RCT6). Written 2026-11-17. **Architecture only: no project or KiCad file was changed.**

Inputs read: `PROJECT.md` (decisions log), `instruction.md` §6 / §8, `docs/research/01`, `02`, `05`, the sheet lists of `03_MCU_Control` and `06_Communications` in `PROJECT.md` §1.1 / §3, and the sibling architecture parts `A_power_stage.md` (A) and `C_afe.md` (C) in the same folder. Where A or C already own a signal, this part follows their definition and lists any conflict in §9.

## 0. Sources and evidence labels

| Tag | Document | Where it came from (this session) |
|---|---|---|
| **DS473** | ST **DS12712 Rev 2** (Oct 2019), STM32G473xB/xC/xE data sheet, 223 pages | LCSC copy for C529361. **Note: the G473 data sheet is DS12712. DS12288 is the G474 one** |
| **DS474** | ST DS12288 Rev 4 (Jun 2020), STM32G474 | LCSC copy for C521608; used only to cross-check AF rows |
| **AN2606** | ST AN2606 **Rev 62** (Mar 2024), section 47 "STM32G47xxx/48xxx devices" | University mirror (st.com timed out). Rev 71 (Nov 2026) exists and was **not** read |
| **IS3050C** | Chipanalog CA-IS305xC data sheet V1.00 (2024, Chinese) | LCSC copy for C41784143 |
| **IS3050** | Chipanalog CA-IS305x data sheet V1.10 | LCSC copy for C528763 |
| **IS3082** | Chipanalog CA-IS308x data sheet V1.10 | LCSC copy for C970942 |
| **ISO1500** | TI ISO1500, ZHCSIV2C (Chinese edition of SLLSF21C) | LCSC copy for C2671333 |
| **ISO7721** | TI ISO7721-Q1 data sheet | local copy from the earlier review |
| **TJA** | NXP TJA1051 product data sheet (2015) | local copy from the earlier review |
| **THVD** | TI THVD1450 data sheet | local copy from the earlier review |
| **TPS** | TI TPS3823 data sheet | local copy from the earlier review |
| **ESP** | Espressif ESP32-C3-MINI-1 data sheet (Chinese) | LCSC copy for C2838502 |
| **TCA** | TI TCA9535 data sheet | LCSC copy for C130204 |
| **FM25** | Cypress FM25V02A, doc 001-90865 Rev *E | LCSC copy for C66029 |
| **W25** | Winbond W25Q64JV | LCSC copy for C179171 |
| **FC135** | Epson FC-135 32.768 kHz spec | LCSC copy for C32346 |
| **GAQY** | SUPSiC GAQY212GS photoMOS | LCSC copy for C7435107 |
| **MLT** | Huaneng MLT-8530 buzzer spec | LCSC copy for C94599 |
| **S1 / S5 / S14 / KS / DALY** | Seplos 16S 200A manual V16, JBD UP16S010, PACE P16S100A, KS48100, Daly R16A | text extracts from the competitor research |
| **LCSC** | `wmsc.lcsc.com/ftps/wm/product/detail?productCode=…` (stock, price, MPN) | live 2026-11-17 |
| **JLCS** | `jlcsearch.tscircuit.com/api/search` (Basic / Extended flag, stock) | live 2026-11-17 |

"calc" = my arithmetic. "unverified" = not checked in a document this session. Page numbers are the printed page numbers of each data sheet. For AN2606 they are the printed pages of Rev 62.

---

## 1. Key choices (summary)

1. **MCU pin map.** All 52 I/O of the LQFP-64 are used (§2). Slow signals go to **two TCA9535 expanders** on a second I2C bus. The AFE keeps its own bus (I2C1, PA15 / PB7).
2. **ROM-bootloader-aware pin map.** AN2606 Table 101 makes the G47x ROM bootloader touch USART1/2/3, I2C2/3/4, SPI1/2 and USB pins (AN2606 p.234–236). No actuator, FET_EN or WDI sits on a pin the ROM drives or pulls up. The actuator timer group is on **TIM1 PC0–PC3**, not on PC6–PC9 (those are the ROM's I2C3 / I2C4 pins, open-drain with pull-up).
3. **Flashing ports:**
   * SWD is the primary port.
   * The **USB-C service port** goes to USART1 PA9 / PA10, which is a ROM-bootloader port.
   * The ESP32 can reach the ROM over USART3 on PC10 / PC11 (DNP strap option).
   * **The G47x ROM has no FDCAN bootloader** (AN2606 Rev 62 Table 101 lists none), so CAN / RS-485 / BLE updates need the custom bootloader.
4. **Isolated CAN: Chipanalog CA-IS3050CW** (integrated isolator + transceiver; CAN FD 5 Mbps; 5 kVrms; 8 mm creepage; logic side 3.0–5.5 V, so there is no VIO problem). It replaces ISO7721 + TJA1051T/3.
5. **Isolated RS-485: Chipanalog CA-IS3082WX** (500 kbps; 1/8 UL; true fail-safe receiver; 5 kVrms; 8 mm creepage). It replaces 2 × ISO7721 + THVD1450.
6. **Isolated power:** one `GND_ISO` domain for all four ports, fed by **B0505S-2WR3 (2 W)**. The power agent places it. The worst-case load is ≈ 290 mA (§3.4).
7. **RJ45 × 4 on the Seplos / PACE / JBD / Daly convention:** CAN on pins 4 / 5, RS-485 B / A on 1 / 2 and 8 / 7, GND on 3 / 6. LINK-IN and LINK-OUT carry RS-485 link + CAN link, wired 1:1.
8. **USB-C service = CH340C + ISO7721DR** (isolated UART bridge), not native USB. Native USB FS sits on PA11 / PA12, which FDCAN1 needs, and needs an expensive FS isolator.
9. **New sheets:**
   * 08_IO_Front_Panel (8xx)
   * 09_Wireless (9xx)
   * 10_Memory_Sensors (10xx)
   * 07_Power_Stage (7xx), owned by A
   * 05 becomes 05_Aux_Outputs (5xx)

---

## 2. STM32G473RCT6 pin map (LQFP-64)

### 2.1 Facts used (DS473)
* Package columns in Table 12 are WLCSP81 / UFQFPN48 / LQFP48 / **LQFP64** / LQFP80 / TFBGA100 / LQFP100 / LQFP128 (DS473 p.54).
* **FT = 5 V tolerant, TT = 3.6 V tolerant**. Suffixes:
  * `_a` analog switch (VDDA)
  * `_c` USB Type-C PD
  * `_d` dead battery
  * `_f` Fm+
  * `_u` USB

  "All I/Os are set as floating inputs during and after reset" unless a note says otherwise (DS473 p.53 Table 11).
* Absolute maximum VIN:
  * FT_xxx (except FT_c): min(VDD, VDDA) + 4.0 V
  * FT_c: 5.5 V
  * TT_xx: 4.0 V

  (DS473 p.78 Table 14). Operating VIN on TT_xx ≤ VDD + 0.3 V (DS473 p.80 Table 17).
* Note 2: PC13 / PC14 / PC15 sit behind the backup power switch. They sink ≤ 3 mA, run at ≤ 2 MHz, and **must not source current (no LED)** (DS473 p.68).
* Note 4: after reset PA13, PA14, PA15, PB3, PB4 are JTAG / SWD, with **pull-up on PA15, PA13, PB4 and pull-down on PA14** (DS473 p.68).
* Note 5: set PB8 to a non-analog mode after start-up (DS473 p.68).
* Internal pull-up / pull-down resistors are 25 / 40 / 55 kΩ (min / typ / max) (DS473 p.131).
* The comparator input range is 0…VDDA (DS473 p.163 Table 77). "All comparators can wake up from Stop mode, generate interrupts and breaks for the timers" (DS473 p.33).
* The temperature code **6 = −40…85 °C (105 °C junction)** (DS473 p.221). RCT6 is therefore the 85 °C grade.
* **AF numbers:** the DS473 Table 13 text extract (p.69–77) is partly misaligned:
  * the PA8 row drops I2C3_SCL;
  * PA9 / PA10 show a "CAN1_RXFD / TXFD" that the pin table (p.62) does not have;
  * PA13 loses I2C1_SCL.

  Every AF number used below was therefore **cross-checked against DS474 Table 13** (G474, same pin-out minus HRTIM), and they agree. Confirm once more in CubeMX before capture.

### 2.2 Full pin table

Direction is seen from the MCU. "Reset" = the state from reset until firmware configures the pin (floating input unless noted). "Ext. default" = the external resistor that defines the net while the pin floats. "ROM" = what the ROM bootloader does to the pin when BOOT0 = 1 (AN2606 p.234–236).

| Pin | Port | Net | AF / function | Dir | Reset / ext. default | Type | Notes |
|---|---|---|---|---|---|---|---|
| 1 | VBAT | `VBAT_MCU` | RTC / backup supply | S | – | – | From `+3V3` through BAT54-class Schottky, 100 nF (DS473 p.77 Fig.15). Supercap option DNP (§5.1) |
| 2 | PC13 | `WAKE_BTN_N` | GPIO / **WKUP2** / EXTI13 | in | floating; 100 kΩ pull-up to `+3V3` | FT | Button via D_WAKE1 (C §4). Input only (p.68 note 2). Standby pull-up via PWR_PUCRC (FW) |
| 3 | PC14 | `OSC32_IN` | LSE | – | – | FT | 32.768 kHz crystal (§5.1) |
| 4 | PC15 | `OSC32_OUT` | LSE | – | – | FT | |
| 5 | PF0 | `OSC_IN` | HSE | – | – | FT_fa | 8 MHz crystal (FDCAN bit timing) |
| 6 | PF1 | `OSC_OUT` | HSE | – | – | FT_a | |
| 7 | PG10-NRST | `MCU_NRST` | NRST | bi | internal pull-up | FT | TPS3823 RESET, SWD pin 10, 100 nF. Also an input to A's gate-kill AND |
| 8 | PC0 | `HEATER_EN` | **TIM1_CH1, AF2** | out | 100 kΩ pull-down → off | FT_a | Actuator group, TIM1 break → idle 0. ROM: untouched |
| 9 | PC1 | `EXT_OUT1` | **TIM1_CH2, AF2** | out | 100 kΩ pull-down → off | TT_a | Economiser PWM possible. Break idle per use (FW) |
| 10 | PC2 | `EXT_OUT2` | **TIM1_CH3, AF2** | out | 100 kΩ pull-down → off | FT_a | |
| 11 | PC3 | `FAN_PWM` | **TIM1_CH4, AF2** | out | 100 kΩ pull-down → fan off | TT_a | 25 kHz |
| 12 | PA0 | `ISENSE_OUT` | ADC12_IN1 + **COMP3_INP** | in (analog) | – | TT_a | Charge-side threshold vs internal DAC. **Must stay ≤ VDDA**: A powers the INA240 from `+3V3_A` (A §5) |
| 13 | PA1 | `RS485_INV_DE` | **USART2_RTS_DE, AF7** | out | CA-IS3082 internal DE pull-down (IS3082 p.4) → receive | TT_a | Hardware DE. ROM: untouched |
| 14 | PA2 | `RS485_INV_TX` | **USART2_TX, AF7** | out | floating (driver off while DE low) | FT_a | ROM USART2 TX (pull-up): no effect, DE stays low |
| 15 | VSS | `GND_PWR` | – | S | – | – | |
| 16 | VDD | `+3V3` | – | S | – | – | 100 nF |
| 17 | PA3 | `RS485_INV_RX` | **USART2_RX, AF7** | in | transceiver RO drives | TT_a | ROM USART2 RX: the ROM can receive, but it cannot answer (DE is not driven), so this is **not a flash port** |
| 18 | PA4 | `FRAM_CS_N` | GPIO | out | **10 kΩ pull-up** → deselected | TT_a | ROM SPI1_NSS input with pull-down (40 kΩ typ): 10 kΩ still wins, 2.6 V (calc) |
| 19 | PA5 | `SPI1_SCK` | **SPI1_SCK, AF5** | out | – | TT_a | FRAM + flash, mode 0 |
| 20 | PA6 | `SPI1_MISO` | **SPI1_MISO, AF5** | in | – | TT_a | ROM drives it as MISO. No contention: both CS lines are held high |
| 21 | PA7 | `SPI1_MOSI` | **SPI1_MOSI, AF5** | out | – | TT_a | |
| 22 | PC4 | `EXP_SCL` | **I2C2_SCL, AF4** | od | 4.7 kΩ pull-up | FT_fa | Expanders + front-panel connector. ROM I2C2 slave (0x53) |
| 23 | PC5 | `AFE_ALERT` | GPIO / **WKUP5** / EXTI5 | in | 10 kΩ pull-up (C) | TT_a | Wakes from Stop / Standby / Shutdown |
| 24 | PB0 | `ISENSE_OUT` (2nd pad) | ADC1_IN15 / ADC3_IN12 + **COMP4_INP** + OPAMP3_VINP | in (analog) | – | TT_a | Discharge-side threshold. Optional PGA for idle current |
| 25 | PB1 | `RS485_LINK_DE` | **LPUART1_RTS_DE, AF12** | out | CA-IS3082 DE pull-down → receive | TT_a | LPUART1 can wake from Stop on link traffic |
| 26 | PB2 | `NTC_SHUNT` | ADC2_IN12 | in (analog) | – | TT_a | Shunt NTC (A §7, C §5). Bias from `+3V3_A` |
| 27 | VSSA | `GND_PWR` (analog star) | – | S | – | – | |
| 28 | VREF+ | `+3V3_A` | – | S | – | – | 100 nF + 1 µF (DS473 p.77) |
| 29 | VDDA | `+3V3_A` | – | S | – | – | 10 nF + 1 µF (DS473 p.77) |
| 30 | PB10 | `RS485_LINK_RX` | **LPUART1_RX, AF8** | in | RO drives | TT_a | ROM: untouched |
| 31 | VSS | `GND_PWR` | – | S | – | – | |
| 32 | VDD | `+3V3` | – | S | – | – | 100 nF |
| 33 | PB11 | `RS485_LINK_TX` | **LPUART1_TX, AF8** | out | – | TT_a | |
| 34 | PB12 | `CAN_LINK_RX` | **FDCAN2_RX, AF9** | in | transceiver RXD drives | TT_a | ROM SPI2_NSS pull-down: harmless |
| 35 | PB13 | `CAN_LINK_TX` | **FDCAN2_TX, AF9** | out | **4.7 kΩ pull-up → recessive** | TT_a | ROM SPI2_SCK pull-down (40 kΩ) is beaten by 4.7 kΩ: 2.95 V (calc). Also keeps the bus recessive during reset |
| 36 | PB14 | `NTC_MUX` | ADC1_IN5 / ADC4_IN4 | in (analog) | – | TT_a | Output of the CD4051 8:1 NTC mux (§5.9). ROM drives PB14 as SPI2 MISO: harmless into a 10 kΩ divider |
| 37 | PB15 | `BUZZER` | **TIM15_CH2, AF1** | out | 100 kΩ pull-down → silent | TT_a | 2.7 kHz |
| 38 | PC6 | `PWR_HOLD` | GPIO | out | **pull-up at the power latch** (power agent) | FT_f | ROM I2C4_SCL (open-drain + pull-up): harmless with a pull-up design (§3.6) |
| 39 | PC7 | `FLASH_CS_N` | GPIO | out | **10 kΩ pull-up** | FT_f | ROM I2C4_SDA pull-up: deselected |
| 40 | PC8 | `OC_TRIP_N` | GPIO / EXTI8 | in | latch output (A) | FT_f | Read-back + IRQ. ROM I2C3_SCL pull-up: harmless |
| 41 | PC9 | `FAN_TACH` | **TIM3_CH4, AF2** (input capture) | in | 10 kΩ pull-up to `+3V3`, 1 kΩ series | FT_f | 5 V tolerant |
| 42 | PA8 | `EXP_SDA` | **I2C2_SDA, AF4** (DS474 Table 13) | od | 4.7 kΩ pull-up | FT_a | |
| 43 | PA9 | `SVC_TX` | **USART1_TX, AF7** | out | – | FT_fda | **ROM flash port** (USB-C bridge) |
| 44 | PA10 | `SVC_RX` | **USART1_RX, AF7** | in | ISO7721 output drives | FT_fda | |
| 45 | PA11 | `CAN_INV_RX` | **FDCAN1_RX, AF9** | in | transceiver RXD drives | FT_u | ROM enables USB DFU here (input, no pull): harmless |
| 46 | PA12 | `CAN_INV_TX` | **FDCAN1_TX, AF9** | out | **4.7 kΩ pull-up → recessive** | FT_u | |
| 47 | VSS | `GND_PWR` | – | S | – | – | |
| 48 | VDD | `+3V3` | – | S | – | – | 100 nF |
| 49 | PA13 | `SWDIO` | SWD (AF0) | bi | internal pull-up | FT_f | J301 |
| 50 | PA14 | `SWCLK` | SWD (AF0) | in | internal pull-down | FT_f | |
| 51 | PA15 | `AFE_SCL` | **I2C1_SCL, AF4** | od | 4.7 kΩ + 100 Ω series (C) | FT_f | Internal JTDI pull-up at reset: harmless |
| 52 | PC10 | `ESP_RXD` (MCU TX → ESP RXD0) | **UART4_TX, AF5** (ROM: USART3_TX, AF7) | out | 1 kΩ series | FT | Series R limits back-powering while `+3V3_ESP` is off |
| 53 | PC11 | `ESP_TXD` (ESP TXD0 → MCU RX) | **UART4_RX, AF5** (ROM: USART3_RX) | in | 1 kΩ series | FT_f | **ROM port for ESP32 recovery flashing** (option) |
| 54 | PC12 | `WDI` | GPIO | out | **floating** = TPS3823 watchdog disabled (TPS p.4) | FT | ROM: untouched, so ROM flashing is not reset by the external WDT |
| 55 | PD2 | `OC_CLR` | GPIO | out | 100 kΩ pull-down (A) → no clear | FT | Rising edge clears the latch only while no OC is present (A §8) |
| 56 | PB3 | `SWO` | TRACESWO (AF0) | out | – | FT | J301 pin 6 |
| 57 | PB4 | `KILL_N` | GPIO / EXTI4 | in | driven by A's U_KILL2 | FT_c | JTRST pull-up at reset and a possible UCPD dead-battery Rd: harmless on a driven input (FW: disable the dead-battery Rd, §2.5) |
| 58 | PB5 | `AFE_RST_SHUT` | GPIO | out | 10 kΩ pull-down R_RST1 (C) → normal | FT_f | |
| 59 | PB6 | `FET_EN` | **TIM8_CH1, AF5** | out | 100 kΩ pull-down (A) → **kill** | FT_c | TIM8 break (COMP3 / COMP4 / SW) forces 0 in hardware. A dead-battery Rd at reset would only pull further down: safe |
| 60 | PB7 | `AFE_SDA` | **I2C1_SDA, AF4** | od | 4.7 kΩ + 100 Ω (C) | FT_f | |
| 61 | PB8-BOOT0 | `MCU_BOOT0` | BOOT0 | in | 10 kΩ pull-down; BOOT jumper / test pad to `+3V3` | FT_f | Keep nSWBOOT0 = 1 (pin-controlled) |
| 62 | PB9 | `AFE_DFETOFF` | **TIM8_CH3, AF10** | out | 100 kΩ pull-down (C) → not asserted | FT_f | **High = all FETs off** (C §2 pin 30). TIM8 break idle = 1 (assert) |
| 63 | VSS | `GND_PWR` | – | S | – | – | |
| 64 | VDD | `+3V3` | – | S | – | – | 100 nF + 4.7 µF bulk (DS473 p.77 Fig.15) |

**Spare MCU pins: none.** The expanders give 13 spare bits (§2.4). Pins that can be freed if a feature is dropped:
* `BUZZER` (PB15, ADC2_IN15)
* `FAN_TACH` (PC9)
* `NTC_SHUNT` (PB2): move it into the mux

### 2.3 Timer and analog groups
* **TIM1 (actuators):** PC0–PC3 = HEATER_EN / EXT_OUT1 / EXT_OUT2 / FAN_PWM.
* **TIM8 (safety):** PB6 = FET_EN, PB9 = AFE_DFETOFF.
* **Break sources:** both timers take their break from COMP3 / COMP4 (internal, DS473 p.33) and from software (BG bit). With MOE cleared the outputs go to their programmed idle state in hardware:
  * FET_EN 0
  * AFE_DFETOFF 1
  * HEATER_EN 0
  * FAN per FW
  * EXT_OUTx per use, e.g. a shunt-trip output can idle at 1

  **The break latches until firmware re-arms MOE.** This is an *MCU-dependent* second tier only. The MCU-independent trip is A's TLV1702 + latch + gate-kill.
* **COMP3 / COMP4:** `ISENSE_OUT` on PA0 (COMP3_INP) and PB0 (COMP4_INP) (DS473 p.56–58). The INM inputs come from internal DAC channels. Which DAC channel can feed which COMPx_INM is in RM0440 (unverified).
* **Wake-up pins:** WKUP2 = PC13 (button) and WKUP5 = PC5 (AFE_ALERT) (DS473 p.54–57). LPUART1 (link RS-485) can also wake from Stop (no extra pin).
* **EXTI lines in use:** 4 (KILL_N), 5 (AFE_ALERT), 8 (OC_TRIP_N), 13 (WAKE_BTN_N). There are no EXTI line conflicts.

### 2.4 I/O expanders (I2C2, 400 kHz)

TCA9535 has **no internal pull-ups** (TCA p.14), and its ports **power up as inputs**. With external 100 kΩ pull-downs, every enable and contact is therefore off at power-up.

| U801 TCA9535 @0x20 | Signal | Dir | Default |
|---|---|---|---|
| P00–P03 | `DIP_ADDR0..3` (pack address, SW801) | in | 10 kΩ pull-ups, DIP to GND |
| P04 | `AFE_FLT_DSG_N` (read-back; the fast path is KILL_N on EXTI4) | in | 100 kΩ PD (C) |
| P05 | `AFE_FLT_CHG_N` | in | 100 kΩ PD (C) |
| P06 | `DI_AUX1` (e.g. aerosol / fire-suppressant input, Seplos-style, S1 §2.17) | in | 10 kΩ PU |
| P07 | spare in | in | |
| P10 | `EN_ISO` | out | 100 kΩ PD → isolated comms off |
| P11 | `EN_ESP` | out | 100 kΩ PD → ESP rail off |
| P12 | `ESP_EN` (open-drain use: drive 0 = hold ESP in reset; input = release) | out | ESP EN RC 10 kΩ / 1 µF to `+3V3_ESP` |
| P13 | `ESP_BOOT` (GPIO9 strap: 0 = download) | out | input → ESP internal pull-up → SPI boot (ESP p.12) |
| P14 | `EN_SENSE` | out | 100 kΩ PD (see the §9 caveat) |
| P15 | `BAL_EXT_EN` | out | 100 kΩ PD → module off (C §4.4) |
| P16 | `DRY1` (photoMOS LED) | out | contact open |
| P17 | `DRY2` | out | contact open |

| U802 TCA9535 @0x21 | Signal |
|---|---|
| P00–P03 | `LED_SOC1..4` (sink, anode to `+3V3` via 1 kΩ) |
| P04 / P05 | `LED_RUN` (green) / `LED_ALM` (red) |
| P06 / P07 | `LED_SOC5 / 6` (DNP: 6-LED bar option, JBD / PACE style) |
| P10–P12 | `MUX_S0..S2` (CD4051 select) |
| P13 | `MUX_INH` (100 kΩ PU = mux off) |
| P14–P17 | spare (e.g. auto-termination photoMOS option, LCD reset) |

TCA9535 INT is not wired to the MCU (no pin). Firmware polls every 50 ms. The fast fault path is `KILL_N` / `OC_TRIP_N` / `AFE_ALERT`. TCA9535 has no reset pin, so after an MCU reset firmware re-writes both expanders first. The only TCA9539 (the version with a reset pin) on LCSC is the QFN RTWR with 3 in stock (LCSC C134039), so it was rejected.

### 2.5 Bootloader (AN2606) against the wiring
* **Activation:** Pattern 14 (AN2606 p.234). ROM entry happens on BOOT0 pin = 1 with nSWBOOT0 = 1, or on nBOOT0 = 0 with nSWBOOT0 = 0; the dual-bank empty checks are also listed (AN2606 p.30 Table 2).
* **Hardware:** BOOT0 jumper / test pads next to J301. Firmware can also jump to system memory (0x1FFF0000, AN2606 p.234) on an "enter bootloader" command.
* **ROM I/O (AN2606 p.234–236 Table 101):**
  * USART1 PA9 / PA10
  * USART2 PA2 / PA3
  * USART3 PC10 / PC11
  * I2C2 PC4 / PA8, I2C3 PC8 / PC9, I2C4 PC6 / PC7 (slave 0b1010011x)
  * SPI1 PA4–PA7, SPI2 PB12–PB15
  * USB DFU PA11 / PA12

  **No FDCAN** in this revision.

| ROM interface | Our wiring | Usable for flashing? |
|---|---|---|
| USART1 PA9 / PA10 | USB-C service bridge (CH340C + ISO7721) | **Yes: recovery / factory port** |
| USART2 PA2 / PA3 | inverter RS-485; DE on PA1 is not driven by the ROM | **No** (the ROM can receive but cannot reply) |
| USART3 PC10 / PC11 | ESP32-C3 UART0 | **Yes, if** the ESP32 also controls BOOT0 and NRST (DNP straps R905 / Q901, owner Q11) |
| I2C2 PC4 / PA8 | expander bus + front-panel connector | possible from the front-panel connector; not planned |
| I2C3 / I2C4, SPI1 / SPI2 | PWR_HOLD, FLASH_CS_N, OC_TRIP_N, FAN_TACH, SPI memories, CAN link, NTC mux, buzzer | No. Pins were chosen so the ROM pull-ups / pull-downs are harmless (column "ROM" above) |
| USB DFU PA11 / PA12 | FDCAN1 | No |
| FDCAN | – | not offered by the G47x ROM. **CAN / RS-485 / BLE updates = custom bootloader** in user flash, image staged in the W25Q64 |

**Firmware rules (hardware depends on them):**
1. Early in start-up, disable the UCPD dead-battery pull-downs (PWR_CR3.UCPD_DBDIS). This affects PB4 / PB6 (FT_c, "UCPD1_CC2 / CC1", DS473 p.66). The exact reset behaviour is in RM0440 (unverified).
2. Use SWD only. Release PA15 / PB4 from JTAG (they keep their AF0 pull-ups until reconfigured, DS473 p.68).
3. Toggle WDI within 0.9 s (TPS3823 minimum timeout, A §8 / TPS p.7). Enable the IWDG by option byte as a backstop: WDI floats until firmware drives it, and floating WDI disables the TPS3823 (TPS p.4).
4. TIM1 / TIM8: set OSSI = 1 and the OISx idle levels as listed in §2.3. Never run TIM8 outputs with MOE set before the self-test has passed.
5. Set the UART4 pins to analog (Hi-Z) while `EN_ESP` = 0 (back-powering).
6. Set LSEDRV = 11 (high) for the chosen 12.5 pF crystal (§5.1).
7. I2C1 (AFE): 400 kHz, clock stretching on, CRC per C.
8. Set PB8 to a non-analog mode after start-up (DS473 p.68 note 5).

### 2.6 Fail-safe states (MCU in reset / unpowered / cable unplugged)

| Output | MCU in reset | +3V3 lost | Comment |
|---|---|---|---|
| FET_EN | 0 (PD) → kill | 0 | A §8. Availability question Q1 |
| AFE_DFETOFF | 0 (PD) → AFE autonomous | logic lost → AFE pin's own pull-down (C) | |
| HEATER_EN, EXT_OUT1 / 2, FAN_PWM | 0 → off | 0 | EXT_OUT1 also tripped by BQ FUSE (A §9.1) |
| PWR_HOLD | held by the latch pull-up | – | power agent |
| CAN TX | pull-up → recessive | transceiver unpowered → passive bus (IS3050C p.1 "ideal passive when unpowered") | |
| RS-485 DE | transceiver pull-down → receive | – | |
| Expander outputs | keep their last state during a short reset; inputs after POR | inputs → PD → off | FW re-writes them at boot |
| Dry contacts | as the expander | open | |
| ESP32 | as the expander | off | |

---

## 3. Communications

### 3.1 Block diagram

```
                         control board (GND_PWR side)                    | barrier |      isolated side (GND_ISO)            connectors
                                                                          |  8 mm   |
 STM32G473RCT6                                                            |         |
  FDCAN1 PA12 TX ──4k7↑──┐                                                |         |
         PA11 RX ────────┴── U601 CA-IS3050CW  VCC1=+3V3 ─────────────────┼─────────┼── VCC2=+5V_ISO ─ L601(DNP CMC) ─ D601 PESD1CAN ─ SW601a/b split term ─ J601 RJ45 "INV-CAN"
  FDCAN2 PB13 TX ──4k7↑──┐                                                |         |                                                                           4 CANH 5 CANL 3/6 GND
         PB12 RX ────────┴── U602 CA-IS3050CW ────────────────────────────┼─────────┼── +5V_ISO ─ L602(DNP) ─ D602 PESD1CAN ─ SW602a/b ─┬─ J603 RJ45 "LINK-IN"
                                                                          |         |                                                   └─ J604 RJ45 "LINK-OUT" (1:1)
  USART2 PA2 TX / PA3 RX / PA1 DE ── U603 CA-IS3082WX  VDDA=+3V3 ─────────┼─────────┼── VDDB=+5V_ISO ─ D603 PSM712 ─ SW601c 120R ─ J602 RJ45 "INV-485"  1/8 B 2/7 A 3/6 GND
  LPUART1 PB11 TX / PB10 RX / PB1 DE ── U604 CA-IS3082WX ─────────────────┼─────────┼── +5V_ISO ─ D604 PSM712 ─ SW602c 120R ─ J603 / J604 pins 1/2/7/8
                                                                          |         |
  +5V ─ EN_ISO ─(power agent load switch)─ U_ISO B0505S-2WR3 (2 W) ───────┼─────────┼── +5V_ISO / GND_ISO   (one domain for all 4 ports; RJ45 shields → CHASSIS via 1 nF 2 kV ∥ 1 MΩ)
                                                                          |         |
  USART1 PA9 / PA10 ── U606 ISO7721DR (VCC2=+3V3 | VCC1=+5V_USB) ─────────┼─────────┼── U605 CH340C ─ U607 USBLC6 ─ J605 USB-C   (domain GND_USB = laptop ground)
                                                                          |         |
  UART4 PC10 / PC11 ─1k─ U901 ESP32-C3-MINI-1-N4 (+3V3_ESP, EN ← ESP_EN, GPIO9 ← ESP_BOOT)   non-isolated, antenna at the board edge
  I2C2 PC4 / PA8 ── U801 / U802 TCA9535 ── LEDs, DIP, enables, dry-contact photoMOS ── J801 front-panel (optional remote LCD / LED board)
  I2C1 PA15 / PB7 ── AFE BQ76952 (C)          SPI1 ── U1001 FM25V02A + U1002 W25Q64JV
```

### 3.2 Isolated CAN (×2)

**Problems with the current parts (sheet 06):**
* The TJA1051**T/3** has a VIO pin 5: "supply voltage for I/O level adapter; TJA1051T/3 only". VIO must be 2.8–5.5 V (TJA p.2, p.4). The fix with the discrete parts is to tie VIO to the isolator's side-2 supply (`+5V_ISO`).
* The TJA1051 is rated for CAN FD "at data rates up to 2 Mbit/s" (TJA p.1).
* Each ISO7721 needs **0.1 µF on VCC1 and 0.1 µF on VCC2** (ISO7721 p.26). Three isolators need six capacitors. Sheet 06 has three (C_ISO_C1, C_ISO_C2, C_ISO_485). The ISO7721 D package has only **4 mm creepage** (ISO7721 p.9), which is below the 6.5 mm target in `plan_pcb_manufacturing.md` §2.

**Chosen: Chipanalog CA-IS3050CW** (SOIC16-WB), one per port.
* CAN FD up to 5 Mbps, classic up to 1 Mbps; 5 kVrms; ±52 V bus fault; ±30 V CMR (IS3050C p.1)
* Logic side **3.0–5.5 V**, so `+3V3` connects directly and no VIO pin exists; bus side 4.5–5.5 V (IS3050C p.6)
* ICC2 dominant 44 mA typ / 73 mA max (IS3050C p.10); dominant time-out 2 / 5 / 8 ms (IS3050C p.11)
* Creepage / clearance 8 mm (IS3050C p.8)
* Pins (W):
  * 1 VCC1; 2, 7, 8 GND1; 3 RXD; 6 TXD
  * 9, 10, 15 GND2; 12 CANL; 13 CANH; 16 VCC2

  (IS3050C p.4)
* Decoupling: 0.1 µF on each side, close to the pins (IS3050C p.4)
* **The rate is set by firmware:** 500 kbps classic for Pylontech-style inverter CAN (S1 §9.1: 500 kbit/s). CAN FD (e.g. 500 k / 2 M) is possible on the link bus between our own packs.
* **Termination, switchable:** split 2 × 60.4 Ω + 4.7 nF to GND_ISO. Each leg has its own DIP pole (SW601a / b, SW602a / b), so "off" leaves no asymmetric load.
  * Inverter port: ON by default (the BMS is a bus end).
  * Link port: ON only on the first and last pack of a chain.
  * Current through a pole ≈ 2.0 V / 120 Ω ≈ 17 mA (calc), against the 25 mA DIP rating (listing). See unverified item U9.
* **TVS:** PESD1CAN (C343993; 24 V class, 280 W 8/20 µs per listing) per port, between the transceiver and the RJ45. CMC ACT45B-510 (C76584) is a footprint, DNP with 0 Ω bypass (EMC test decides).
* **Classic-only fallbacks:**
  * CA-IS3050G (SOIC8-WB, 1 Mbps only, IS3050 p.1; C528763, 4,205 pcs)
  * CA-IS3050U (DUB8, 3.75 kVrms)
* **TI fallback:** ISO1042DWVR (C2671714) has only 75 pcs at $4.86 (LCSC), so it is not viable as the main part.

### 3.3 Isolated RS-485 (×2)

**Problems with the current parts:**
* Two ISO7721 + THVD1450 per port are needed for TX + DE + RX (three channels), and the decoupling is short, as for CAN.
* THVD1450 itself is good: its receiver stays fail-safe-high on an idle or shorted bus "without the need for external failsafe biasing" (THVD p.19). But the chain is big.

**Chosen: CA-IS3082WX** (SOIC16-WB).
* 500 kbps, 1/8 unit load (256 nodes), logic side 2.375–5.5 V, bus side 3.0–5.5 V (IS3082 p.1–2)
* **RO high when VA − VB > −20 mV**, i.e. true fail-safe with no bias resistors needed. **DE has an internal weak pull-down** (IS3082 p.4)
* Bus ESD ±20 kV HBM (IS3082 p.7); creepage 8 mm (IS3082 p.8); ICCB 6.8 mA unloaded (IS3082 p.12)
* RE is tied to GND1 (always receive: echo check of our own frames)
* **Termination:** 120 Ω through one DIP pole per port (SW601c / SW602c). Current ≈ 2.5 V / 120 Ω ≈ 21 mA (calc), close to the 25 mA DIP rating (U9)
* **Bias:** 560 Ω footprints DNP (only for a legacy master without fail-safe). This replaces today's always-fitted R_FS_A1 / B1
* **TVS:** PSM712 (C2687124; −7 / +12 V class, listing)
* **Smaller alternative:** TI **ISO1500DBQR** (SSOP-16, 1 Mbps, 3 kVrms, 1/8 UL, fail-safe; VCC1 1.71–5.5 V, ISO1500 p.1). It is roughly 1/3 of the area, but its **creepage is only 3.7 mm** (ISO1500 p.6), it needs RE tied low (open = disabled, ISO1500 p.3), and its loaded ICC2 is 52 / 70 mA (ISO1500 p.9). Use it only if the 6.5 mm creepage target is dropped (Q4).

### 3.4 Discrete vs integrated: comparison (per board, 2 CAN + 2 RS-485; prices LCSC @100 USD, 2026-11-17)

| Option | Parts | Cost (calc) | Package area (est., body + leads) | LCSC stock (lowest item) | Creepage | FD |
|---|---|---|---|---|---|---|
| A. Today's discrete TI / NXP, fixed | 2 × (ISO7721DR + TJA1051T/3) + 2 × (2 × ISO7721DR + THVD1450DR) | 6 × 0.43 + 2 × 0.60 + 2 × 0.97 = **$5.72** | 10 × SOIC-8 ≈ 10 × 30 = 300 mm² + 20 caps | THVD1450 4,816 | **4 mm** (ISO7721 D, p.9) | 2 Mbps (TJA p.1) |
| A-Q. Same with ISO7721QDRQ1 | – | ≈ $6.4 | same | **62 pcs** (C2867808) | 4 mm | 2 Mbps |
| **B. Chipanalog integrated (chosen)** | 2 × CA-IS3050CW + 2 × CA-IS3082WX | 2 × 0.72 + 2 × 0.77 = **$2.98** | 4 × SOIC16-WB ≈ 4 × 106 = 424 mm² (ISO + transceiver in one part, 8 caps) | 2,092 (CW) | **8 mm** | 5 Mbps |
| B-small. CA-IS3050G + ISO1500 | 2 × CA-IS3050G + 2 × ISO1500DBQR | 2 × 0.70 + 2 × 0.89 = $3.18 | 2 × ≈ 60 + 2 × ≈ 30 = 180 mm² | 4,205 | 6.8 / **3.7 mm** | **no** (1 Mbps) |
| C. Integrated with isolated power | 2 × CA-IS3062W + 2 × CA-IS2092W | 2 × 2.51 + 2 × 1.67 = $8.36, but **no B0505S** (−$0.82) | 4 × SOIC16-WB | 6,008 | 8 mm | 1 Mbps (listing) |

**Recommendation: B.**
* It is the cheapest option.
* It needs 4 ICs instead of 10, with less decoupling and no VIO / DIR-isolator pitfalls.
* It keeps the plan's 6.5 mm creepage, keeps FD, and the stock is adequate.
* Option C is the most compact power-wise, but it is 2.4 × the cost.

None of these parts is AEC-Q (consistent with the non-AEC MCU, `PROJECT.md` 2026-11-17).

**`+5V_ISO` load** (worst case, calc):
* CAN: 2 × 73 mA (IS3050C p.10)
* RS-485: 2 × ≈ 70 mA driving 54 Ω (ISO1500 p.9 figure used as the class estimate; the CA-IS3082 loaded figure was not extracted, U7)
* quiescent: 2 × 6.8 mA (IS3082 p.12)

Total ≈ **300 mA** → **B0505S-2WR3** (400 mA, listing) is required. A 1 W / 200 mA module is not enough. `+5V_ISO` is **not** exported on any RJ45.

### 3.5 RJ45 connectors and pinout

**Convention:** the same on four competitor documents:
* Seplos CAN port: 1 / 8 RS485-B, 2 / 7 RS485-A, 4 CAN-H, 5 CAN-L, 3 / 6 GND; RS-485 port: 4 / 5 "internal communication (NC)" (S1 p.31)
* PACE / JBD: 1, 8 = B; 2, 7 = A; 3, 6 = GND; 4, 5 = NC on the RS-485 port; the CAN port puts CAN on pins 4 / 5 (S14 p.16; S5 p.23)
* Daly: 1 = 485-B, 2 = 485-A, 3 = GND, 4 = CAN_H, 5 = CAN_L (DALY)
* KS48100: CAN_H 4, CAN_L 5, GND 6 (KS §8)

**Twisted pairs (T568B):**
* 1-2 = B / A, twisted ✓
* 7-8 = A / B, twisted ✓
* 4-5 = CANH / CANL, twisted ✓
* 3-6 = GND pair ✓

Part: 4 × KH-RJ45-58-8P8C (right angle, shielded). Shield → `CHASSIS` (1 nF 2 kV ∥ 1 MΩ to `GND_ISO`, values unverified, EMC).

| Pin | J601 INV-CAN | J602 INV-485 | J603 LINK-IN / J604 LINK-OUT (1:1 in parallel) |
|---|---|---|---|
| 1 | NC (option: `RS485_INV_B` via 0 Ω DNP, Seplos "CAN port" style) | `RS485_INV_B` | `RS485_LINK_B` |
| 2 | NC (option: `RS485_INV_A`, DNP) | `RS485_INV_A` | `RS485_LINK_A` |
| 3 | `GND_ISO` | `GND_ISO` | `GND_ISO` |
| 4 | `CANH_INV` | NC | `CANH_LINK` |
| 5 | `CANL_INV` | NC | `CANL_LINK` |
| 6 | `GND_ISO` | `GND_ISO` | `GND_ISO` |
| 7 | NC (option `RS485_INV_A`) | `RS485_INV_A` | `RS485_LINK_A` (option: `ADDR_OUT` for auto-addressing via 0 Ω DNP) |
| 8 | NC (option `RS485_INV_B`) | `RS485_INV_B` | `RS485_LINK_B` (option: `ADDR_IN`) |

Notes:
* **Inverter cable:** most inverters expect CANH on pin 4 and CANL on pin 5 at the battery end (S1, DALY, KS). Victron needs its "Type B" cable (general knowledge, unverified).
* **Link ports:** RS-485 on 1 / 2 / 7 / 8 matches the Seplos / PACE / JBD parallel ports. We add **CAN link on 4 / 5**; competitors have NC or "internal" there (S1 p.31), so **mixing brands on one link bus is not supported**.
* A straight-through Cat5 cable joins LINK-OUT of pack n to LINK-IN of pack n+1. The pack address comes from the DIP (§5.10).

### 3.6 Other connectors and the antenna
* **ESP32-C3-MINI-1-N4:**
  * Placed at a board edge, antenna end outwards. Follow the keep-out zone of the module footprint figure (ESP p.10): no copper on any layer and no parts under or beside the antenna.
  * The ≥ 15 mm clearance commonly quoted by Espressif's hardware design guide was not opened (unverified, U12).
  * The RJ45 shields and the FET bank / Cu bars must stay away from the antenna end.
  * **The pack enclosure is normally steel**, which blocks the PCB antenna. This is owner question Q10: the -1U variant (u.FL) was not found on LCSC.
* **J301 SWD:** keep the 2 × 5 1.27 mm Cortex debug header (J_SWD1): SWDIO, SWCLK, SWO (pin 6), NRST, `+3V3`, GND.
* **J605 USB-C (service):**
  * TYPE-C-31-M-12 with 5.1 kΩ Rd on CC1 / CC2 (sink)
  * USBLC6-2SC6 on D+ / D−
  * a PTC on VBUS (part unverified)
  * CH340C on VBUS 5 V; ISO7721DR with VCC1 = 5 V (USB side) and VCC2 = `+3V3` (both sides 2.25–5.5 V, ISO7721 p.1)
  * **domain `GND_USB` ≠ `GND_PWR`**

  Optional DNP: a second ISO7721 so that CH340 DTR / RTS can drive NRST / BOOT0 for one-click flashing.
* **J801 front panel** (optional remote LED / LCD board; part unverified, e.g. JST GH 8-pin): `+5V`, `+3V3`, `GND_PWR`, `EXP_SCL`, `EXP_SDA`, `WAKE_BTN_RAW`, `LED_ALM_HW` (option), spare. ESD array on SCL / SDA / button. The on-board LEDs and button stay on the main board edge with light pipes.

---

## 4. Signal-integrity and layout notes for the comms
* Keep each isolator straddling a **≥ 8 mm gap / milled slot** in all copper layers (IS3050C p.8, IS3082 p.8). All four sit in one row along the connector edge. GND_ISO is poured only on the connector side.
* Place the TVS within 5 mm of the RJ45 pins, with the return to `GND_ISO` by the shortest path. Put the termination resistors near the transceiver, the split capacitor at the mid-point.
* CAN TXD pull-ups (4.7 kΩ) and the RS-485 DE path go on the MCU side of the barrier. The `+5V_ISO` bulk (10 µF) and 0.1 µF per transceiver go on the bus side.
* 33 Ω series resistors in TX lines at the MCU (driver side, playbook §8). The 1 kΩ series resistors on the ESP UART protect against back-powering.

---

## 5. I/O blocks

### 5.1 RTC crystal and backup
* **Crystal:** Epson **Q13FC13500004** (FC-135): 32.768 kHz, **CL 12.5 pF, R1 ≤ 70 kΩ**, C0 1 pF, ±20 ppm, −40…85 °C (FC135 p.1). JLC **Basic**.
* **Load capacitors:** C = 2 × (CL − Cstray) = 2 × (12.5 − 3) ≈ 19 pF → **18 pF C0G** (calc; Cstray 3 pF assumed).
* **Oscillator margin:**
  * gm_crit = 4 · ESR · (2πf)² · (C0 + CL)² = 4 × 70 kΩ × (2π × 32 768)² × (13.5 pF)² = **2.16 µA/V** (calc).
  * The G473 LSE Gmcritmax is 0.5 / 0.75 / 1.7 / **2.7 µA/V** for LSEDRV = 00 / 01 / 10 / 11 (DS473 p.122 Table 45). **LSEDRV must be 11 (high)**; the margin is thin (×1.25).
  * Alternative: a 7 pF crystal, e.g. NDK NX3215SA-32.768K-EXS00A-MU00746 (C5136773, 3,171 pcs, E). It gives 0.76 µA/V (calc) and works at LSEDRV = 10. Its ESR was not checked (U14).
* **HSE:** keep 8 MHz. Sheet 03 field Y1 = "X32258MOB4SI" (3225), but its LCSC C115962 is a **YXC X50328MSB2GI (SMD5032)** (LCSC). The footprint and the number disagree. Use the 5032 part (295,250 pcs) and fix the footprint, or choose a verified 3225 (U13).
* **VBAT:** from `+3V3` through a Schottky, 100 nF. A 0.1–0.22 F supercap footprint (DNP) keeps the RTC through ship mode (05 §1.7). No coin cell.

### 5.2 FRAM FM25V02A and flash W25Q64
* **FM25V02A-GTR:** 32 KB, 40 MHz, SPI mode 0 / 3, 2.0–3.6 V, 10¹⁴ cycles, NoDelay writes, 8 µA sleep (FM25 p.1). SOIC-8, same footprint as the 25LC256. Use it for SOC / SOH, the last-fault record, and counters written on PVD brown-out.
* **W25Q64JVSSIQ:** 64 Mbit, 133 MHz, 2.7–3.6 V, < 1 µA power-down (W25 p.5). SOIC-8 **208 mil** (a different footprint). Use it for the black-box log, waveform captures and the staged firmware image.
* Both are on SPI1 (mode 0, ≤ 20 MHz on the shared bus). Each has a 10 kΩ CS pull-up. WP / HOLD go to `+3V3` (FRAM WP may go to a test pad for factory lock). 100 nF each.
* Second source for the flash: MX25L6433FM2I-08G (C706695, 1,941 pcs, E).

### 5.3 I/O expanders
Two TCA9535PWR (VCC 1.65–5.5 V; ports sink up to 25 mA; no pull-ups) (TCA p.1, p.4, p.14). Addresses 0x20 / 0x21 via A0–A2. 100 nF each. See the map in §2.4.

### 5.4 SOC LED bar + RUN / ALM
* 4 × green SOC + 1 green RUN + 1 red ALM, sinking into U802, each through 1 kΩ from `+3V3` (≈ 1.2 mA green, calc).
* Two extra SOC positions DNP (6-LED option).
* Option `LED_ALM_HW`: a diode-OR from `KILL_N` lights ALM even with the MCU dead (part count: 1 diode + 1 transistor).
* LED parts: KT-0603G (C12624, E) / KT-0603R (C2286, **Basic**).

### 5.5 Buzzer
* **MLT-8530:** 3.6 Vo-p rated, 2.5–4.5 V operating, ≤ 95 mA at 2.7 kHz, 16 Ω, **−20…+70 °C** (MLT p.2).
* Drive: SS8050 low-side from `+3V3` (rated 3.6 Vo-p), 1N4148-class flyback, base 1 kΩ + 100 kΩ PD, PWM from PB15.
* The −20 °C limit is below the −40 °C requirement (Q9).

### 5.6 Dry contacts (×2)
* **GAQY212GS** (SUPSiC):
  * 60 V AC-peak / DC, 0.8 A, 1.5 A for 100 ms
  * I/O isolation 2,500 Vrms
  * LED IF max 50 mA
  * −40…85 °C

  (GAQY p.1–2). Panasonic AQY212GS (C719745) is the alternative; its rating comes from the listing only (60 V, 1 A).
* LED drive: ≈ 5 mA from `+3V3` via 330 Ω (calc; check IF(on) on GAQY p.2, U10), sunk by U801 P16 / P17.
* Output: a 4-pin 3.5 mm pluggable terminal (part unverified), with an SMAJ-class TVS across each contact (≤ 60 V).
* **Rating limit:** these switch ≤ 60 V signals (inverter gen-start inputs, alarm loops). **They do not switch 230 VAC** (Q7). Competitor documents give no rating (S1 §2.16, S14).

### 5.7 Fan driver
* AO3400A (C20917, **Basic**; 30 V, 5.7 A) low-side from `FAN_PWM`. Gate 100 Ω + 100 kΩ PD. Flyback diode to `+12V`.
* 3-pin JST-PH header S3B-PH-K (C545716): `+12V`, switched GND, `FAN_TACH`.
* Tach: 10 kΩ pull-up to `+3V3`, 1 kΩ series, 1 nF (PC9 is FT_f).

### 5.8 Heater / EXT outputs
Owned by A (§9). Signals only:
* `HEATER_EN` (PC0, TIM1_CH1) → Q_HTR1 gate driver from `+12V` (A §9.2)
* `EXT_OUT1` (PC1) OR BQ FUSE → Q_EXT1 (A §9.1)
* `EXT_OUT2` (PC2) → Q_EXT2

They are 3.3 V push-pull with 100 kΩ PD at the driver. If A uses a 12 V relay for the heater, the coil runs from `+12V` with its own flyback, on A's sheet.

### 5.9 NTC inputs for the MCU
* C assigns NTC_PACK4 (and PACK5 / 6), NTC_SHUNT, NTC_BAL and NTC_AMB to the MCU ADC (C §5, §11). NTC_FET goes to the AFE CFETOFF pin (C pin 29).
* With no free pins, use **`NTC_SHUNT` direct on PB2** (for the CC temperature compensation) plus an **8:1 mux CD4051BQPWRQ1** (C555142; 3–20 V, AEC-Q100 per listing) on PB14, selected from U802 P10–P13.
* Each channel: 10 kΩ from `+3V3_A`, 10 kΩ B3380 NTC to `GND_PWR`, 100 nF at the mux output. Settling time ≥ 5 τ ≈ 5 ms per channel (calc, mux Ron ignored, U15).

### 5.10 DIP switch
* `SW801` 4-pole **pack address 0–15** (Seplos / JBD / PACE / JK all use 4 address bits: S1 §9.4, S5, S14, 02_competitors T3).
* The cell count and chemistry move to FRAM settings (LFP only by owner decision).
* Part: DSHP04TSGER (C3293144, 56,144 pcs, E, 1.27 mm SMD).
* The termination DIPs SW601 / SW602 are separate parts on the **isolated** side. A DIP body must not straddle the barrier.

---

## 6. Parts table

LCSC numbers checked live on 2026-11-17:
* MPN and stock from the LCSC product API (**L**);
* Basic / Extended from jlcsearch (**J**).

When the two stock numbers differ (different cache times), the LCSC figure is shown.

| Ref-to-be | Function | Part | LCSC | Stock | B/E | Key rating | Source |
|---|---|---|---|---|---|---|---|
| U301 | MCU | STM32G473RCT6 | C529361 | 2,870 | E | 170 MHz, 256 KB / 128 KB, 3 × FDCAN, −40…85 °C (DS473 p.221) | L + J |
| U302 | supervisor + WDT | TPS3823-33DBVR | C7719 | 59,700 | E | 2.93 V; WDI float = disabled (TPS p.4) | L + J |
| Y301 | HSE 8 MHz | YXC X50328MSB2GI (5032) | C115962 | 295,250 | n/r | CL not checked (U13) | L |
| Y302 | LSE | Epson Q13FC13500004 | C32346 | 245,265 | **B** | 12.5 pF, ≤ 70 kΩ (FC135 p.1) | L + J |
| C3xx | LSE load caps | 18 pF C0G 0402 GRM1555C1H180FA01D | C161534 | 79,935 (J) | E | ±1 %, 50 V | J (a Basic 18 pF should be picked in the audit) |
| J301 | SWD 2 × 5 1.27 mm | keep J_SWD1 part | C2932845 (field) | unverified | unverified | – | not checked |
| U1001 | FRAM | FM25V02A-GTR | C66029 | 7,358 | E | 32 KB, 40 MHz, 2.0–3.6 V (FM25 p.1) | L + J |
| U1002 | log / OTA flash | W25Q64JVSSIQ | C179171 | 1,048 | E | 64 Mbit, 133 MHz (W25 p.5) | L + J |
| U1002-alt | flash 2nd source | MX25L6433FM2I-08G | C706695 | 1,941 (J) | E | 64 Mbit, 133 MHz (listing) | J |
| U1003 | NTC mux | CD4051BQPWRQ1 | C555142 | 2,306 | n/r | 8:1, 3–20 V (listing) | L |
| U801, U802 | I/O expanders | TCA9535PWR | C130204 | 14,125 | E | 16 I/O, no pull-ups (TCA p.14) | L + J |
| SW801 | address DIP 4-pole | DSHP04TSGER | C3293144 | 56,144 | E | 24 V / 25 mA (listing) | L + J |
| SW802 | wake / reset button | TS-1187A-B-A-B | C318884 | 526,560 | **B** | 12 V / 50 mA (listing) | L + J |
| D801–D805 | SOC / RUN LEDs | KT-0603G | C12624 | 224,478 (J) | E | green 0603 | J |
| D806 | ALM LED | KT-0603R | C2286 | 5,724,023 (J) | **B** | red 0603 | J |
| BZ801 | buzzer | MLT-8530 | C94599 | 115,620 | E | 3.6 Vo-p, 95 mA, −20…70 °C (MLT p.2) | L + J |
| Q801 | buzzer driver | SS8050 (200–350) | C2150 | 3.1 M (J) | **B** | 25 V, 1.5 A (listing) | J |
| U501, U502 | dry contacts | GAQY212GS (SUPSiC) | C7435107 | 104,360 | E | 60 V, 0.8 A, 2.5 kVrms (GAQY p.2) | L + J |
| U501-alt | dry contacts | Panasonic AQY212GS | C719745 | 5,160 | E | 60 V, 1 A (listing only) | L + J |
| Q501 | fan driver | AO3400A | C20917 | 989,942 (J) | **B** | 30 V, 5.7 A | J |
| J502 | fan header | S3B-PH-K(LF)(SN) | C545716 | 13,011 (J) | E | 2 A / pin (listing) | J |
| J501 | dry-contact terminal 4P | – | unverified | – | – | – | not found |
| U601, U602 | isolated CAN FD | **CA-IS3050CW** | C41784143 | 2,092 | E | 5 kVrms, 5 Mbps FD, 8 mm (IS3050C p.1, p.8) | L + J |
| U601-alt | isolated CAN (classic) | CA-IS3050G | C528763 | 4,205 | E | 1 Mbps, 5 kVrms (IS3050 p.1) | L + J |
| U603, U604 | isolated RS-485 | **CA-IS3082WX** | C970942 | 10,286 | E | 500 kbps, fail-safe, 5 kVrms (IS3082 p.1–4) | L + J |
| U603-alt | small isolated RS-485 | ISO1500DBQR | C2671333 | 7,384 | E | 1 Mbps, 3 kVrms, 3.7 mm (ISO1500 p.1, p.6) | L + J |
| D601, D602 | CAN TVS | PESD1CAN (BORN) | C343993 | 49,640 | E | 24 V class (listing) | L + J |
| D603, D604 | RS-485 TVS | PSM712-LF-T7 (UMW) | C2687124 | 137,240 | E | −7 / +12 V, 150 W (listing) | L + J |
| L601, L602 | CAN CMC (DNP) | ACT45B-510-2P-TL003 | C76584 | 3,640 | E | 51 µH, 200 mA (listing) | L + J |
| SW601, SW602 | termination DIP (iso side) | DSHP04TSGER | C3293144 | 56,144 | E | 25 mA (listing) | L + J |
| R6xx / C6xx | 60.4 Ω, 120 Ω, 4.7 nF, 560 Ω (DNP) | – | unverified | – | – | – | not looked up |
| J601–J604 | RJ45 × 4 | KH-RJ45-58-8P8C | C2683360 | 3,695 | E | right angle, shielded, −25…70 °C (listing) | L + J |
| U605 | USB-UART | CH340C | C84681 | 86,800 | E | internal oscillator (data sheet encrypted, not read) | L + J |
| U606 | USB isolator | ISO7721DR | C366164 | 12,955 | E | 2.25–5.5 V both sides (ISO7721 p.1) | L + J |
| U607 | USB ESD | USBLC6-2SC6 | C7519 | 38,690 | E | – | L + J |
| J605 | USB-C | TYPE-C-31-M-12 | C165948 | 497,290 | E | 16-pin | L + J |
| U901 | BLE / WiFi | ESP32-C3-MINI-1-N4 | C2838502 | 9,258 | E | 3.0–3.6 V; TX 350 mA peak (ESP p.20–21) | L + J |
| U_ISO (power agent) | isolated DC-DC | B0505S-2WR3 (EVISUN) | C7465195 | 5,337 | E | 2 W / 400 mA, 1.5 kV (listing) | L + J |
| U902 (power agent) | ESP rail switch | TPS22918DBVR | C131941 | 66,825 (J) | E | 2 A, 53 mΩ (listing) | J |

**Corrections to the current fields (all looked up on LCSC 2026-11-17):**

| Ref (today) | Field LCSC | LCSC returns | Correct number |
|---|---|---|---|
| U_485_1 (THVD1450DR) | C395353 | JUSHUO AFC12-S12CCC-00 FPC connector | **C2671361** THVD1450DR, 4,816 pcs, E (part removed by this architecture) |
| U_ISO_* (ISO7721) | C129202 | Tak Cheong ZM4733AR13 zener, 0 stock | **C366164** ISO7721DR (12,955) or C2867808 ISO7721QDRQ1 (62) |
| U_CAN1 (TJA1051T/3) | C385473 | TyoHM RN1/2WS 220 kΩ THT resistor | **C58988** TJA1051T/3,118, 2,578 pcs (removed by this architecture) |
| SW_CFG1 (CHS-04B) | C318884 | XKB TS-1187A-B-A-B **tactile switch** | CHS-04B1 = **C3312443** (Nidec, 244 pcs). Recommended instead: DSHP04TSGER **C3293144**. C318884 is reused for the wake button SW802 |
| U3 (AP2112K-3.3) | C352467 | RESI 0402 18 Ω resistor | **C51118** AP2112K-3.3TRG1 (Diodes, 29,988 pcs, E) |
| U_MEM1 (25LC256-I/SN) | C5426 | no record | not found on jlcsearch: **unverified**. The part is replaced by the FM25V02A (C66029) |
| U4 (B0505S-1WR3) | C265225 | no record | 1 W: C7465178 (EVISUN, 102,762 pcs) / C2992394 (YLPTEC). No Mornsun-branded number was found (unverified). This architecture needs the 2 W C7465195 |
| U_WDOG1 (TPS3823-33) | C80145 (extra find) | no record | **C7719** |
| Y1 | C115962 | YXC X50328MSB2GI (5032), not the 3225 MPN in the field | see §5.1 |

---

## 7. Sheet plan for the new hierarchy

References become **numeric per sheet** (playbook house style). Today's name-based references are mapped when a sheet is redrawn. Power symbols follow the existing `#PWRnxx` scheme.

| # | File | Range | Owner | Content |
|---|---|---|---|---|
| 0 | `Automotive_ESS_BMS.kicad_sch` | – | – | root, sheet symbols with sheet pins |
| 01 | `01_Power_Supply` | 1xx | power agent | input protection, LM5164, +5V, +3V3 / +3V3_A, power latch (`PWR_HOLD`, `WAKE_BTN_RAW`), load switches (`EN_ISO`, `EN_ESP`, `EN_SENSE`), B0505S-2WR3 → `+5V_ISO`, `+3V3_ESP` |
| 02 | `02_AFE_Cell_Monitor` | 2xx | C | BQ76952, cell inputs, balancing, AFE NTCs, J_ABAL1 |
| 03 | `03_MCU_Control` | 3xx | **D** | U301 G473, decoupling, Y301 / Y302, VBAT, U302 TPS3823 + NRST, BOOT0, J301 SWD. Nothing else (playbook §6 "MCU sheet holds only …") |
| 04 | `04_Current_Sensing` | 4xx | A | shunt, INA240, OC window + latch |
| 05 | `05_Aux_Outputs` (rename of Power_Actuators) | 5xx | A + **D** | A: heater FET, EXT_OUT1 / 2 drivers. D: fan driver Q501 + J502, dry contacts U501 / U502 + J501 |
| 06 | `06_Communications` | 6xx | **D** | U601–U604, TVS, CMC, termination + SW601 / SW602, J601–J604, USB service U605–U607 + J605 |
| 07 | `07_Power_Stage` (new) | 7xx | A | FET banks, pre-charge, gate-kill logic, B2B (if two boards) |
| 08 | `08_IO_Front_Panel` (new) | 8xx | **D** | U801 / U802, LEDs D801–D806, SW801 DIP, SW802 button, BZ801 + Q801, J801 |
| 09 | `09_Wireless` (new) | 9xx | **D** | U901 ESP32-C3, EN RC, strap / test pads, DNP ROM-flash straps (R905 / Q901) |
| 10 | `10_Memory_Sensors` (new) | 1001–1099 | **D** | U1001 FRAM, U1002 flash, U1003 NTC mux + MCU NTC inputs / connectors |

If A's two-board split is adopted, sheets 04 / 07 and the power half of 05 become a separate "power board" project. The B2B is defined by A.

**Existing parts, sheets 03 and 06:**

| Today | Disposition |
|---|---|
| U_MCU1 STM32G431CBT6 | **replace** → U301 STM32G473RCT6 |
| U_WDOG1 TPS3823-33 | **keep** → U302; fix the LCSC to C7719; WDI moves from PB0 to PC12 |
| U_MEM1 25LC256 | **remove** → U1001 FM25V02A on sheet 10 (same SOIC-8 footprint) |
| Y1, C_X1-2 | **keep** 8 MHz → Y301 / C30x; fix the footprint / number mismatch (§5.1) |
| C_VDD1-3, C_A1-2 | **keep and extend** to 4 × VDD 100 nF + 4.7 µF, VDDA 10 nF + 1 µF, VREF+ 100 nF + 1 µF, VBAT 100 nF (DS473 p.77) |
| C_MEM1 | **move** to sheet 10 |
| C_RST2, R_RST2, R_BOOT0 | **keep** → 3xx |
| FB1 | **keep** (`+3V3` → `+3V3_A`); fix the footprint (bead on a resistor footprint) |
| SW_CFG1 + R_SW1-4 | **move** to sheet 08 as SW801 + pull-ups; the function changes to pack address; new part number |
| R_CS1 | **move** to sheet 10 (CS pull-up) |
| R_HB1 / D_HB1 heartbeat on PC13 | **remove** (PC13 must not source an LED, DS473 p.68; RUN LED is on U802) |
| J_SWD1 | **keep** → J301 |
| U_ISO_CAN1 ISO7721 + U_CAN1 TJA1051T/3 | **remove** → U601 CA-IS3050CW |
| U_ISO_485A / B ISO7721 + U_485_1 THVD1450 | **remove** → U603 CA-IS3082WX |
| J_CAN1, J_485_1 (1 × 4 headers with `+5V_ISO`) | **remove** → J601 / J602 RJ45 (no `+5V_ISO` on the connectors) |
| D_TVS_CAN1 NUP2105L (no LCSC record for C12948) | **replace** → D601 PESD1CAN |
| D_TVS_485_1 SM712 (no record for C19002) | **replace** → D603 PSM712 |
| R_TRM1-2 + C_TRM1 (split termination) | **keep** the function → R601 / R602 / C601, now switched by SW601a / b |
| R_TRM_485 | **keep** → R6xx, switched by SW601c |
| R_FS_A1 / R_FS_B1 (560 Ω bias) | **keep as DNP** footprints |
| C_CAN1-2, C_485_1, C_ISO_C1-2, C_ISO_485 | **remove**; new decoupling per IS3050C p.4 / IS3082 p.4 |

---

## 8. Interface signals (new names introduced by part D)

The contract names (`AFE_*`, `ISENSE_OUT`, `OC_TRIP_N`, `OC_CLR`, `FET_EN`, `KILL_N`, `PWR_HOLD`, `WAKE_BTN_N`, `EN_*`, outputs, rails, pack) are used unchanged. These names are added here:

| Name | From → to | Level / type | Notes |
|---|---|---|---|
| `MCU_NRST` | U302 / SWD ↔ MCU → A's gate-kill | open-drain-ish, low = reset | name already used by A |
| `MCU_BOOT0` | jumper → PB8 | 10 kΩ PD | |
| `SWDIO`, `SWCLK`, `SWO` | J301 ↔ MCU | 3.3 V | |
| `VBAT_MCU` | `+3V3` via Schottky → pin 1 | 1.55–3.6 V (DS473 p.80) | |
| `WDI` | MCU → U302 | 3.3 V | |
| `CAN_INV_TX`, `CAN_INV_RX`, `CAN_LINK_TX`, `CAN_LINK_RX` | MCU ↔ U601 / U602 | 3.3 V; TX 4.7 kΩ PU | |
| `CANH_INV`, `CANL_INV`, `CANH_LINK`, `CANL_LINK` | U60x ↔ RJ45 | CAN, `GND_ISO` | class `CAN_Bus` |
| `RS485_INV_TX/RX/DE`, `RS485_LINK_TX/RX/DE` | MCU ↔ U603 / U604 | 3.3 V | |
| `RS485_INV_A/B`, `RS485_LINK_A/B` | U60x ↔ RJ45 | RS-485, `GND_ISO` | |
| `CHASSIS` | RJ45 shields | via 1 nF ∥ 1 MΩ to `GND_ISO` | new domain |
| `SVC_TX`, `SVC_RX` | MCU ↔ U606 | 3.3 V | |
| `+5V_USB`, `GND_USB`, `USB_DP`, `USB_DM` | J605 side | USB domain | **new isolated domain; never merge with `GND_PWR`** |
| `ESP_RXD`, `ESP_TXD` | MCU TX → ESP RXD0 / ESP TXD0 → MCU RX | 3.3 V, 1 kΩ series | ESP pins 30 / 31 (ESP p.11) |
| `ESP_EN`, `ESP_BOOT` | U801 → ESP EN (pin 8) / GPIO9 (pin 23) | open-drain use | ESP p.11–12 |
| `SPI1_SCK`, `SPI1_MISO`, `SPI1_MOSI`, `FRAM_CS_N`, `FLASH_CS_N` | MCU ↔ sheet 10 | 3.3 V, CS 10 kΩ PU | |
| `EXP_SCL`, `EXP_SDA` | MCU ↔ U801 / U802 / J801 | I2C2, 4.7 kΩ PU | |
| `DIP_ADDR0..3` | SW801 → U801 | 10 kΩ PU | |
| `DI_AUX1` | external input → U801 | 10 kΩ PU, ESD | optional |
| `LED_SOC1..6`, `LED_RUN`, `LED_ALM`, `LED_ALM_HW` | U802 → LEDs | sink | |
| `BUZZER` | MCU → Q801 | PWM 2.7 kHz | |
| `DRY1_A`, `DRY1_B`, `DRY2_A`, `DRY2_B` | photoMOS outputs → J501 | ≤ 60 V | |
| `NTC_MUX`, `MUX_S0..2`, `MUX_INH` | U1003 → PB14 / U802 → U1003 | analog / 3.3 V | |
| `NTC_SHUNT`, `NTC_PACK4..6`, `NTC_BAL`, `NTC_AMB` | NTCs → PB2 / mux | analog, `+3V3_A` bias | names as used by C |
| `WAKE_BTN_RAW` | button node (C) | – | name from C |
| `ADDR_IN`, `ADDR_OUT` | RJ45 7 / 8 option | – | auto-address option, DNP |

---

## 9. Conflicts with A / C and caveats (for the coordinator)
1. **`AFE_DFETOFF` has two definitions.**
   * **C** (§2 pin 30, §11): MCU → AFE, **high = all FETs off**, through Q_DOFF1; `OC_TRIP_N` joins via a diode at the AFE pin.
   * **A** (§8): `AFE_DFETOFF` is the **output** of U_KILL1 AND(FET_EN, OC_TRIP_N, MCU_NRST), active-low.

   This part follows the contract (MCU ↔ AFE) and C: PB9 drives `AFE_DFETOFF`. A's AND output must then get its own name (e.g. `KILL_DFETOFF_N`) or be dropped. To be resolved between A and C (Q2).
2. **`AFE_FLT_DSG_N` / `AFE_FLT_CHG_N` on an MCU EXTI (C §5):** there are no pins left. The fast path is `KILL_N` (EXTI4), which A builds from both fault lines. The individual flags are read on U801 (≤ 50 ms poll).
3. **A's optional `OC_SET_MCU_N`** (a COMPx_OUT pin into the latch): not provided, for lack of a pin. Instead, COMP3 / COMP4 → TIM8 break drives `FET_EN` = 0 and `AFE_DFETOFF` = 1 in hardware, so the effect on the FETs is the same. The OC latch itself is not set.
4. **`EN_SENSE`:** if it gates the INA240 / `+3V3_A`, it also blinds A's hardware OC trip and the MCU ADC. Rule: `EN_SENSE` may only cut power while both FET banks are off, or it must not feed the OC-trip path at all (power agent).
5. **`PWR_HOLD`** must not drop the rails while the MCU is in reset (PC6 floats; ROM pulls it up). Design it as a self-holding latch with a pull-up and an active-low release, or with an RC hold longer than one reset cycle (power agent, Q16).

---

## 10. Open questions for the owner
1. **FET_EN during an MCU reset:** today it is pulled down (FETs off during every watchdog reset, A §8). Is the load dropout acceptable, or should the FETs ride through a reset (RC hold) and rely on the AFE?
2. **`AFE_DFETOFF` driver:** MCU direct (C, contract) or the AND-gate output (A)? (§9.1)
3. **CAN FD:** keep FD capability (CA-IS3050CW, SOIC16-WB) or accept classic 1 Mbps (CA-IS3050G, SOIC8-WB, smaller, more stock)?
4. **Creepage target 6.5 mm** (`plan_pcb_manufacturing.md`): keep it (wide-body isolators, this proposal)? Dropping it allows ISO1500 / ISO7721 narrow packages (3.7–4 mm).
5. **RJ45 pin-out:** confirm the Seplos / PACE / JBD convention (§3.5). On the inverter-CAN port, should pins 1 / 2 / 7 / 8 also carry RS485_INV (Seplos "CAN port" style) or stay NC?
6. **Termination:** manual DIP (proposed) or firmware-controlled auto-termination of the link chain (photoMOS option on U802 P14–P17)?
7. **Dry contacts:** ≤ 60 V photoMOS (proposed). Is a 230 VAC generator-start contact needed (a relay instead)?
8. **SOC LEDs:** 4 (Seplos) or 6 (JBD / PACE / JK)?
9. **Buzzer:** the MLT-8530 is rated −20…70 °C only (MLT p.2). Keep it, drop it, or find a −40 °C part?
10. **ESP32 antenna:** the enclosure is metal? If yes, use an external-antenna module (-1U, LCSC not found) or a plastic window.
11. **ESP32 may reset / re-flash the STM32** through the ROM USART3 (DNP straps)? It is a convenient OTA recovery, but it gives the radio module control of the safety MCU.
12. **USB-C service port:** fit it (≈ $1.2) or DNP it and use RS-485 / BLE only?
13. **MCU temperature grade:** RCT6 = 85 °C ambient (DS473 p.221) against the −40…105 °C requirement (R19). Accept it?
14. **MCU NTC count:** an 8:1 mux gives up to 8 + NTC_SHUNT. How many pack NTCs are wanted on the MCU?
15. **Wake on bus in standby:** keeping `EN_ISO` on (≈ 15–20 mA at 5 V, calc from IS3050C p.10 recessive + IS3082 p.12) allows wake on CAN / RS-485. Or should the isolated side be off for the lowest standby current?
16. **PWR_HOLD policy** (§9.5): a hung MCU then keeps the board awake (fail-on). OK?
17. **Front-panel connector J801** for a remote LCD / LED board: include it?

---

## 11. Unverified list
* U1. **AN2606 Rev 71** (Nov 2026) was not read. The "no FDCAN ROM bootloader on G47x" conclusion is from **Rev 62** Table 101.
* U2. **RM0440 not opened:**
  * DAC channel → COMPx_INM mapping
  * TIM1 / TIM8 break-from-COMP configuration (BKCMPxE)
  * UCPD dead-battery Rd behaviour on PB4 / PB6 at reset, and the UCPD_DBDIS bit
  * dual-bank / RWW on the 256 KB RC part (DS473 p.18 states dual-bank support generally)
  * FDCAN2 use without FDCAN1
  * UID address
* U3. **DS12712 Rev 2 AF-table anomalies** (PA8 / PA9 / PA10 / PA13 rows). The AFs used here were cross-checked with DS474 Table 13; confirm in STM32CubeMX for STM32G473RCTx. A newer DS12712 revision exists and was not read.
* U4. **CH340C** data sheet (LCSC copy is encrypted): pin-out, the internal-oscillator claim and the 5 V VCC were not read.
* U5. CA-IS3050CW ↔ ISO1050 / ISO1042-DW pin compatibility (second source) was not checked.
* U6. CA-IS3050C RXD state when VCC2 is off.
* U7. CA-IS3082WX loaded supply current. The ISO1500 figure (ISO1500 p.9) was used as an estimate.
* U8. KH-RJ45-58-8P8C: data sheet not opened; the temperature range (−25…70 °C) and shield tabs are from the listing.
* U9. DSHP04TSGER current rating (25 mA, listing) against 17–21 mA of termination current.
* U10. GAQY212GS LED IF(on) and RON at 5 mA drive (p.2 not fully extracted). The Panasonic AQY212GS data sheet was not opened.
* U11. PESD1CAN / PSM712 clamp curves (listing only).
* U12. ESP32-C3 antenna keep-out dimensions (only the footprint figure, ESP p.10, was seen). The Espressif hardware design guide was not opened.
* U13. Y301 HSE crystal load capacitance (C115962 data sheet not opened).
* U14. NX3215SA 7 pF crystal ESR.
* U15. CD4051B Ron at 3.3 V (data sheet not opened).
* U16. B0505S-2WR3 (EVISUN) isolation and no-load current (listing). No Mornsun-branded 2 W part was found.
* U17. Passives, terminal blocks, J801, PTC, BAT54 VBAT diode, 1 nF 2 kV shield capacitor: no LCSC numbers chosen (part audit).
* U18. J_SWD1 field C2932845 was not re-checked.
* U19. Victron "Type B" cable and Pylontech native RJ45 pin-out (general knowledge; competitor documents only).
* U20. MLT-8530 current when driven from 3.3 V (spec gives 95 mA at 5 Vo-p).
* U21. jlcsearch has no record of THVD1450DR, TJA1051T/3, ESP32-C3-MINI-1-N4 or CH340C under their MPN; their B/E flag was read by LCSC number (all E).
