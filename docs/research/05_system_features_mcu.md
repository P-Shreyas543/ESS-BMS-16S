# 05 — System features around the MCU (research, report only)

Date 2026-11-17. Read-only on the project. Scope: MCU choice and the hardware that lets firmware offer best-in-class ESS features. Competitor matrix, AFE features, balancing and shunt / power path are covered by other agents and are referenced only where they touch the MCU.

**Evidence labels.**
* **[DS]** = read in a datasheet downloaded this session: DS12589 Rev 2 (STM32G431, Oct 2019, LCSC copy) and DS12288 Rev 4 (STM32G474, Jun 2020, LCSC copy). Both are older revisions; re-check against the current ST revisions.
* **[SYM]** = KiCad 10 stock symbol `MCU_ST_STM32G4.kicad_sym` (pin alternate functions, generated from ST data).
* **[LCSC]** = LCSC product API (`wmsc.lcsc.com/ftps/wm/product/detail?productCode=…`), read live on 2026-11-17. Stock and price are that day's snapshot, in USD.
* **(search)** = web-search snippet only.
* **(unverified)** = general knowledge, not checked.

Not opened: RM0440 (G4 reference manual), AN2606 (ROM bootloader pins), ES0431 errata, the G473 datasheet (DS13092?), the ESP32-C3 datasheet, the S32K144 datasheet. Every attempt to reach st.com / st.com.cn timed out. The LCSC datasheet mirrors worked.

---

## 0. Summary

1. **MCU recommendation: STM32G473RCT6 (LQFP-64 10×10, 256 KB flash, 128 KB SRAM, 3× FDCAN), LCSC C529361: 2,870 in stock, $6.28 @1 and $4.58 @100 [LCSC].** It belongs to the same G4 family, so the firmware, CubeMX and the analog blocks carry over. It costs only $0.45 more than the G431RBT6 in the same package (C431633, $5.83 @1) and about $0.70 more than today's G431CBT6 at 100 pcs. It supplies the dual CAN that `instructions.md` §2.2 asks for, and enough pins for every feature below.
2. **The project's LCSC fields are worse than "unverified": several point to unrelated parts** (§1.6). For example, U_MCU1 C529329 is an **STM32G030C8T6**.
3. **Power is the limiting resource, not pins.** With the added features, the 1 W isolated module and the +5 V buck run out first, and the +12 V rail is already short (P4 in the requirements review). See §4.
4. **The internal comparators + DAC + TIM1 break of the G4 can replace the TLV3501.** This also fixes review items C1 (comparator disabled), C2 (no latch) and C3 (one polarity only), and gives a hardware-latched bidirectional trip on the contactor PWM outputs in about 17–31 ns + filter [DS]. It is not independent of the MCU silicon, so the AFE-based path (A9) is still needed for IEC 62619 independence.

---

## 1. MCU today: STM32G431CBT6 LQFP-48

### 1.1 Facts from DS12589 Rev 2 [DS]
* Cortex-M4F at 170 MHz, 128 KB flash with ECC, 32 KB SRAM (22 KB + 10 KB CCM), 1 KB OTP. 38 GPIOs on LQFP48, 17 ADC channels, **1 FDCAN**, 3 SPI, 3 I2C, 2 USART + 1 UART + 1 LPUART (the UART is not on LQFP48), USB FS device, UCPD, 4 comparators, 3 op-amps, 4 DAC channels (2 external + 2 internal).
* Temperature code: **6 = −40…85 °C ambient (105 °C junction), 3 = −40…125 °C (130 °C junction)**. The part on the schematic, **CBT6, is the 85 °C grade**, so it does not meet the −40…105 °C requirement (R19).
* **AEC-Q100: none.** DS12589 and DS12288 have no AEC statement (text search "AEC": 0 hits). ST sells no AEC-Q100 STM32G4. ST's new automotive STM32A line (A4 / A5 / A9) is sampling, with broader availability from H1 2027 (search). It is not usable for this design.
* 96-bit unique ID [DS p.1]. Its address is 0x1FFF7590 according to RM0440 (unverified; RM not opened). Uses: serial number, BLE pairing PIN, Modbus / CAN address arbitration for auto-addressing.
* Comparator (Table 75): tD 16.7 ns typ / 31 ns max at VDDA ≥ 2.7 V. Offset −9…+3 mV. Programmable hysteresis 0–63 mV typ. Inputs 0…VDDA. "All comparators can wake up from Stop mode, generate interrupts and breaks for the timers" [DS §3.21]. Blanking from a timer is supported.
* Low power (typ, 25 °C / 85 °C, 3.0 V): Stop 1 **59 µA / 555 µA**. Standby 0.12 µA / 1.2 µA (RTC off) and about 0.4 µA with IWDG. Shutdown 35 nA / 805 nA. The strong temperature dependence matters for a warm pack. VBAT powers the RTC and the backup registers. Wake-up from Standby / Shutdown comes from WKUP pins, RTC or NRST.
* Run current at 170 MHz (G474 DS Table 21, same core): **29.5 mA typ, 42 mA max at 125 °C with peripherals off**. Budget 60 mA with ADC, COMP, FDCAN, timers and DMA active.
* Pin types: **PA0 and PA1 are `TT_a` (3.6 V tolerant, not 5 V)**. This confirms review item M7: the INA240 on +5 V can drive PA0 to ≈ 4.8 V, which is above VDDA and the comparator input range. PA8, PB5, PB7, PB8 and PB9 are `FT_f` (5 V-tolerant, Fm+ I2C). PA11 / PA12 are `FT_u` (USB). PB4 is `FT_c`.

### 1.2 Free pins and peripherals on the LQFP-48 today
Unconnected: PA15, PB3, PB4, PB5, PC14, PC15. PB9 is a duplicate of `AFE_SDA` and becomes free once it is removed (M2). Unused peripherals: USART2 / USART3 (only USART1 is used), LPUART1, SPI2 / SPI3, I2C2 / I2C3, USB, UCPD, all 4 comparators, 3 op-amps, DAC, RTC / LSE, TIM1 / TIM8 / TIM15–17 (the contactor pins are plain GPIO), CORDIC / FMAC, RNG.

What fits in those 7 pins: an I2C fix + LSE (4) + 3 spare. That is far short of the feature list in §2 (≈ 25 more signals).

### 1.3 Fix for the AFE bus (PB6 is not I2C) [DS AF table + SYM]
* The DS12589 AF table confirms that PB6 has no I2C (TIM16_CH1N, TIM4_CH1, TIM8_CH1, USART1_TX, COMP4_OUT …). I2C1_SCL is on **PA13 (SWDIO), PA15 and PB8 (BOOT0)**. I2C1_SDA is on PA14 (SWCLK), PB7 and PB9.
* **Minimum fix on the LQFP-48: SCL → PA15, SDA → PB7, drop PB9.** PB8 should not be used: it is BOOT0 with R_BOOT0 pulled down, and an I2C pull-up would boot the system ROM unless the option bit nSWBOOT0 is cleared.
* **SPI option** (owner: "AFE may move to SPI"): SPI3 / SPI1 sit on **PB3 SCK, PB4 MISO, PB5 MOSI, PA15 NSS**, which are exactly the free pins. Whether the AFE is ordered as an SPI variant is for the AFE agent.

### 1.4 One FDCAN against the dual-CAN requirement (R10)
* The G431 has 1 FDCAN in every package [DS Table 2]. The fixes are an external SPI CAN-FD controller (an extra part, extra SPI traffic and extra firmware) or a G4 with more FDCANs.
* FDCAN count by part [SYM]: **G473 / G474: 3 (FDCAN1–3), G491: 2, G431 / G441: 1**.
* **STM32G473CBT6 / G474CET6 in LQFP-48 are pin-name-identical to the G431CBT6** (KiCad pin-by-pin diff: no pin moved) and add FDCAN2 on PB5 / PB6 or PB12 / PB13 and FDCAN3 on PA8 / PA15 or PB3 / PB4. This would be a drop-in fix, but **the G473CBT6 costs $19.16 @1, 228 in stock (C730111) [LCSC]**, three times the price of the LQFP-64 G473RCT6. The pin shortage would also remain.

### 1.5 Analog: can COMP / OPAMP / DAC replace the TLV3501?
**Yes, for the fast trip, if the owner accepts an MCU-internal trip** (C1 / C2 / C3 in the review):
* Put `ADC_I_SENSE` on two COMP+ pins (proposed: **PA0 = COMP3_INP + ADC1_IN1** and **PB0 = COMP4_INP + ADC1_IN15**; same net, two pads).
* Set the charge threshold with COMP3 against internal DAC3_CH1 and the discharge threshold with COMP4 against internal DAC3_CH2, with output polarity inverted. Thresholds and hysteresis stay software-adjustable per chemistry or pack size. Which DAC channel can feed which comparator INM must be checked in RM0440 (unverified).
* Route both comparator outputs internally to **TIM1 BRK**. TIM1 drives the contactor gates (§3). A break forces the outputs to their idle (low) state in hardware without the CPU and **stays latched** until firmware re-arms MOE. This is the "latch" the plan asked for, at no part cost.
* Benefits: it removes U_OCP1 TLV3501, R_TH1 / R_TH2 / C_TH1 and the SHDN problem, about 3 mA of comparator supply (TLV3501 IQ, unverified) and roughly $1. A COMPx_OUT pin can still drive the OCP LED or an external gate-kill if the AFE agent's hardware path wants the signal.
* Limits:
  1. A common-cause failure with the MCU is possible (silicon, clock, a supply fault). In reset the GPIOs go high-Z and the 47 k gate pull-downs open the contactors, so a reset fails safe. An MCU-independent path from the AFE is still needed for R15 / R16 (AFE agent).
  2. The input must stay ≤ VDDA: fix M7 first, with the INA240 on +3V3 or a divider. This is the shunt agent's topic.
* OPAMP extra: one internal op-amp in PGA mode (e.g. OPAMP3, VINP on PB0) gives ×8–×16 gain on `ADC_I_SENSE` to the ADC without a pin. That gives ~20 mA/LSB resolution on small currents (idle / self-discharge / standby current display), on top of the BQ76952 coulomb counter (unverified gain options; RM0440 not opened).

### 1.6 Contactor economiser PWM (no HRTIM needed)
* The G431 / G473 have no HRTIM; that is the G474. HRTIM is not needed: a 20–25 kHz economiser PWM needs only a general or advanced timer.
* Today PA2 / PA3 / PA4 can use only TIM2 / TIM15 / TIM3 and plain GPIO. On the LQFP-64 the proposed map puts **CONT_POS / CONT_NEG / PRECHARGE / HEATER on PC0–PC3 = TIM1_CH1–CH4** [SYM]. This gives one timer for all coil outputs, a common break (OCP comparators + an optional BKIN pin from the AFE fault), and dead-time-free PWM. Pull-in at 100 % for ~100 ms, then hold at ~30–50 % duty (coil data needed). This is required anyway because of the +12 V budget (§4).
* With PWM hold the freewheel diode carries current. On turn-off the diode-only clamp (D_FLY1-3) gives slow contactor drop-out and contact arcing. A diode + zener clamp is preferable (unverified; actuator / power-path topic).

### 1.7 RTC with LSE (PC14 / PC15)
Fit a 32.768 kHz crystal: **Epson Q13FC13500004, C32346, 12.5 pF, SMD3215, 245,850 in stock, $0.12 @100 [LCSC]**, with 2 load capacitors (≈ 18 pF each, estimated as CL = C/2 + ~3 pF stray; confirm with ST AN2867, not opened). The result is a calendar RTC, timestamped fault logs, scheduled tasks (calibration, SOH test cycles, time-of-use) and RTC wake-up from Standby.
* **VBAT:** in normal standby VDD stays on, so VBAT = VDD is enough. To keep time through ship mode (bucks off), add a 0.1–0.22 F supercap on VBAT through a Schottky + resistor; that holds for days (RTC on VBAT ≈ 0.3–0.5 µA, unverified). Firmware also resyncs the clock from the inverter, the BLE app or Modbus. A CR1220 holder is not recommended inside an ESS pack (transport and UL questions).

### 1.8 LCSC field audit: what the project's MCU-area numbers actually are [LCSC, 2026-11-17]
| Ref | Field MPN | LCSC in field | What LCSC returns | Correct number found |
|---|---|---|---|---|
| U_MCU1 | STM32G431CBT6 | C529329 | **STM32G030C8T6** | **C529355** STM32G431CBT6, 7,286 stock, $4.82 @1 |
| U_485_1 | THVD1450DR | C395353 | JUSHUO AFC12 FPC connector | **C2671361**, 4,816 stock, $1.31 @1 |
| U_ISO_* | ISO7721QDRQ1 | C129202 | ZM4733A zener | **C2867808**, **62 stock**, $0.90 @1; non-Q ISO7721DR **C366164** 12,955 stock $0.67 |
| U_CAN1 | TJA1051T/3,118 | C385473 | 220 k THT resistor | **C58988**, 2,578 stock, $0.76 @1 |
| SW_CFG1 | CHS-04B DIP | C318884 | TS-1187A tactile switch | not searched |
| U3 | AP2112K-3.3 | C352467 | 0402 18 R resistor | not searched |
| U_MEM1 / U4 | 25LC256 / B0505S | C5426 / C265225 | API returned no record | not searched |

The full audit belongs to the planned part audit. It is listed here because the MCU sheet and the comms sheet depend on it.

---

## 2. MCU options compared

| | A: stay G431CBT6 LQFP-48 | B: G431RBT6 LQFP-64 | **C: G473RCT6 LQFP-64 (rec)** | D: G474RET6 / RCT6 LQFP-64 | E: NXP S32K144 (FS32K144HFT0VLHT) LQFP-64 |
|---|---|---|---|---|---|
| LCSC | C529355 | C431633 | **C529361** | C521608 / C529414 | C508512 |
| Stock / price @1 / @100 [LCSC] | 7,286 / $4.82 / ≈ $3.88 | 1,452 / $5.83 / $4.36 | **2,870 / $6.28 / $4.58** | 39 / $12.68 / $9.50 ; 0 / $12.02 | 843 / $4.81 / ≈ $3.20 |
| FDCAN | 1 | 1 | **3** | 3 | 3 FlexCAN, FD on 1 only (search) |
| Flash / RAM | 128 K / 32 K | 128 K / 32 K | **256 K / 128 K** | 512 / 256 K, 128 K | 512 K / 64 K (unverified) |
| GPIO | 38 | 52 | **52** | 52 | ≈ 58 (unverified) |
| Temp | 85 °C | 85 °C | 85 °C (T3 = 125 °C exists; no LCSC listing found) | 85 °C | −40…105 °C "V" grade (search) |
| AEC-Q100 | no | no | no | no | **yes** (unverified datasheet; NXP automotive family) |
| Firmware reuse | 100 % | ~100 % | ~95 % (same HAL, more peripherals) | ~95 % | 0 %: new toolchain / SDK, no CubeMX |
| Fits the features in §2 | **no** (≈ 25 signals short) | partly (no 2nd CAN) | **yes** (with a 16-bit I2C expander) | yes | yes, but a different analog set (1 CMP + DAC) |

**Recommendation: C, STM32G473RCT6.**
* Pros: same family, three CANs, twice the flash for a bootloader plus a staged image, 128 KB RAM for logs and BLE buffers, 7 comparators and 6 op-amps.
* Package: the layout is being restarted anyway (owner decision 2026-11-16), so the 10×10 mm package is not a cost.
* If the owner later sets an "all AEC-Q100" policy (review S3), option E is the realistic automotive part on LCSC. That decision means a firmware rewrite and is not justified by features alone.
* G474: rejected (HRTIM not needed, 2× the price, no stock).
* G473CBT6 LQFP-48 drop-in: rejected ($19, still pin-starved).
* Re-check JLCPCB assembly availability for C529361 (Extended part, not checked).

---

## 3. Proposed MCU pin map: STM32G473RCT6 LQFP-64

Alternate functions are from the KiCad symbol STM32G473RCTx [SYM]. Confirm them against the G473 datasheet before schematic capture. "EXP" means a TCA9535 I2C expander port (§5). Pins marked † change role if the AFE stays on I2C (see the notes after the table).

| Pin | Port | Net (proposed) | Function | Note |
|---|---|---|---|---|
| 1 | VBAT | VBAT | RTC supply | VDD via Schottky + optional supercap |
| 2 | PC13 | BTN_WAKE_N | GPIO / **WKUP2** | front-panel button (also wakes the AFE via TS2, §5.13) |
| 3 / 4 | PC14 / PC15 | LSE | OSC32 | 32.768 kHz crystal (new) |
| 5 / 6 | PF0 / PF1 | HSE | OSC | 8 MHz Y1 (keep; FDCAN needs an accurate clock) |
| 7 | PG10 | MCU_RESET_N | NRST | TPS3823 / SWD / C_RST2 as today (M5 open) |
| 8 | PC0 | CTRL_CONT_POS | **TIM1_CH1** | economiser PWM, break-protected |
| 9 | PC1 | CTRL_CONT_NEG | **TIM1_CH2** | economiser PWM |
| 10 | PC2 | CTRL_PRECHARGE | **TIM1_CH3** | on / off (PWM possible) |
| 11 | PC3 | CTRL_HEATER | **TIM1_CH4** | new 4th low-side driver; also cut by the break |
| 12 | PA0 | ADC_I_SENSE | ADC1_IN1 + **COMP3_INP** | charge OCP vs DAC3; TT_a, keep ≤ 3.3 V |
| 13 | PA1 | RS485_INV_DE | **USART2_DE** | hardware DE (Modbus timing) |
| 14 | PA2 | RS485_INV_TX | USART2_TX | inverter RS-485 (Modbus / Pylontech) |
| 17 | PA3 | RS485_INV_RX | USART2_RX | |
| 18 | PA4 | SPI1_CS_FRAM | SPI1_NSS | FRAM |
| 19–21 | PA5 / PA6 / PA7 | SPI1_SCK / MISO / MOSI | SPI1 | FRAM + external flash |
| 22 | PC4 | V_HV_SENSE | ADC2_IN5 | moved from PA1 |
| 23 | PC5 | AFE_ALERT | EXTI / **WKUP5** | AFE wakes the MCU from Stop / Standby / Shutdown |
| 24 | PB0 | ADC_I_SENSE (2nd pad) | **COMP4_INP** (+ OPAMP3_VINP) | discharge OCP (inverted), optional PGA |
| 25 | PB1 | SPI1_CS_FLASH | GPIO | W25Q64 |
| 26 | PB2 | AFE_RST_SHUT | GPIO | as today (PB11) |
| 30 | PB10 | RS485_LINK_TX | USART3_TX | parallel-pack RS-485 |
| 33 | PB11 | RS485_LINK_RX | USART3_RX | |
| 34 | PB12 | CAN_LINK_RX | **FDCAN2_RX** | second CAN (parallel packs / EMS) |
| 35 | PB13 | CAN_LINK_TX | **FDCAN2_TX** | |
| 36 | PB14 | RS485_LINK_DE | **USART3_DE** | |
| 37 | PB15 | FAN_PWM | TIM15_CH2 | 25 kHz |
| 38 | PC6 | I2C4_SCL | I2C4 | expander + front-panel / LCD header |
| 39 | PC7 | I2C4_SDA | I2C4 | |
| 40 | PC8 | MCU_WDOG_WDI | GPIO | was PB0 |
| 41 | PC9 | PWR_HOLD | GPIO | keeps the LM5164 enabled (§5.17) |
| 42 | PA8 | LED_ALM | GPIO | direct, so it works without the expander |
| 43 / 44 | PA9 / PA10 | SERVICE_TX / RX | USART1 | USB-C service bridge; likely the ROM bootloader USART (AN2606 not read) |
| 45 / 46 | PA11 / PA12 | CAN_INV_RX / TX | **FDCAN1** | inverter CAN 500 kbps |
| 49 / 50 | PA13 / PA14 | SWDIO / SWCLK | SWD | |
| 51 | PA15 | AFE_CS † | SPI3_NSS (alt I2C1_SCL) | |
| 52 / 53 | PC10 / PC11 | BLE_TX / BLE_RX | **UART4** | ESP32-C3 module / BLE header |
| 54 | PC12 | FAN_TACH | TIM5_CH2 (input capture) | |
| 55 | PD2 | EXP_INT_N | EXTI | TCA9535 interrupt (DIP / ADDR_IN change) |
| 56–58 | PB3 / PB4 / PB5 | AFE_SCK / MISO / MOSI † | SPI3 | |
| 59 | PB6 | ISO_PWR_EN | GPIO | load switch for the isolated DC-DC |
| 60 | PB7 | LED_RUN † | GPIO (alt I2C1_SDA) | heartbeat / run LED |
| 61 | PB8-BOOT0 | MCU_BOOT0 | BOOT0 | 10 k pull-down, as today |
| 62 | PB9 | BUZZER | TIM17_CH1 | 2.7 kHz drive |

**Expander TCA9535 (16 bits, I2C4):**

| Port | Signal |
|---|---|
| P00–P03 | ADDR DIP 4 bits (SW_CFG1 repurposed) |
| P04 | ADDR_IN |
| P05 | ADDR_OUT |
| P06 | DRY1 |
| P07 | DRY2 |
| P10–P13 | LED_SOC1..4 |
| P14 | ESP_PWR_EN |
| P15 | ESP_BOOT (GPIO9 strap) |
| P16 | SENSE_PWR_EN (INA240 / analog gating) |
| P17 | spare (protocol jumper) |

The expander outputs power up as inputs, so the relays and LEDs are off by default.

**Notes on the map:**
* † If the AFE stays on I2C: AFE_SCL → PA15 (I2C1_SCL), AFE_SDA → PB7 (I2C1_SDA), LED_RUN → PB5. PB3 / PB4 then become free and can carry **FDCAN3** (PB3 RX, PB4 TX) for a third CAN (DNP).
* Not on the map: the 4 DIP pins (now on the expander, 4 MCU pins saved), PB12–PB15 CFG and PC13 heartbeat (re-used).
* Free MCU pins: none in the SPI-AFE variant; 2 in the I2C variant. A +12 V rail monitor could use a spare AFE ADC input (AFE agent) or replace CS_FLASH if no flash is fitted.

---

## 4. Power budget

Rated limits: U1 LM5164 +12 V 1 A [DS lm5164 p.1]; U2 LMR16006Y **600 mA** [DS lmr16006 p.1]; U3 AP2112 600 mA, **θJA 184 °C/W SOT-25**, IQ 55 µA [DS ap2112 p.3, p.5]; U4 B0505S-1WR3 **200 mA out**, 78–82 % efficiency, ~8 mA no-load (series value, search). Loads are estimates; the sources are noted.

### 4.1 +3V3 (AP2112, from +5 V, P = 1.7 V × I)
| Load | mA (typ / peak) | Source |
|---|---|---|
| G473 at 170 MHz + peripherals | 45 / 60 | DS12288 Table 21 + estimate |
| ISO7721 VCC1 × 5 (CAN ×2, RS-485 ×2 + DIR) | 8 / 15 | ISO7721 DS ICC1 0.8–2.9 mA |
| FRAM + flash (program burst) | 1 / 15 | unverified |
| TCA9535, I2C pull-ups, TPS3823 | 2 | estimate |
| LEDs: RUN, ALM, 4× SOC at 2–3 mA | 12 / 18 | estimate |
| CH340 side of the service port: on VBUS, not on +3V3 | 0 | – |
| **Sum without ESP32** | **≈ 70 / 110** | → 0.19 W, ΔT ≈ 34 °C: **OK** |
| ESP32-C3 BLE (avg) / WiFi TX peak | 30 / ≈ 335 | Espressif, unverified |
| **Sum with ESP32 on U3** | ≈ 100 / ≈ 445 | 0.76 W peak → ΔT ≈ 140 °C: **FAILS thermally** |

→ **The ESP32 gets its own rail**: AMS1117-3.3 (C6186, 890k stock, $0.16) or a second LMR16006 from +12 V (better efficiency; same part as U2), behind a TPS22918 load switch (C131941, $0.25) for standby gating. Note that the AMS1117 is not an AEC part.

### 4.2 +5V (LMR16006Y, 600 mA)
| Load | mA |
|---|---|
| U3 input (= +3V3 load) | 110 |
| INA240 | 2.4 (DS) |
| Isolated DC-DC input, 1 W today at full load | 247 (search: Mornsun table) |
| Buzzer MLT-8530 | ≈ 30 (unverified) |
| Dry contacts (photoMOS LED 5 mA × 2, from +3V3) | – |
| **Total today + features, ESP32 not on +5V** | **≈ 390 mA: OK** |
| With a 2 W isolated module (needed, §4.4): +250 | ≈ 640 mA: **FAILS** (> 600 mA) |
| With the ESP32 AMS1117 also on +5 V: +100 avg / +335 peak | ≈ 740 / 975 mA: **FAILS** |

→ Either upgrade U2 to a 1.5–2 A buck (power-path agent), or move the ESP32 rail to +12 V (second LMR16006) and split the isolation into two 1 W modules (inverter-port domain and link domain). The split is better anyway: a harness fault on the parallel link then cannot take down the inverter comms.

### 4.3 +12V (LM5164, 1 A)
* Already short for two non-economised contactor coils (review P4).
* Added: fan 80–150 mA (typ. 80–120 mm 12 V fan, unverified), heater relay / contactor coil 30–300 mA, plus the +5 V buck input (≈ 0.3 A at 12 V for 600 mA at 5 V).
* Worst case with economised coils: 2 × 0.25 A hold + 0.15 + 0.1 + 0.3 = **≈ 1.05 A: at or over the limit; pull-in transients exceed it.**

→ The economiser PWM is **mandatory** and the firmware must never pull in two coils at once. Better options (power-path agent): a 2 A 100 V buck, or contactors / heater relay with **pack-voltage (48 V) coils driven from V_BATT+** through 100 V FETs, which removes the coil current from the 12 V rail.

### 4.4 +5V_ISO (B0505S-1WR3, 200 mA)
| Load | today | with CAN2 + RS485-2 |
|---|---|---|
| TJA1051, dominant 50 typ / 70 max (DS) | 70 | 140 |
| THVD1450 driving 54 Ω (≈ 5 V / 2 / 54 Ω ≈ 46 mA, estimate) + 2.4 mA quiescent (DS) | 50 | 100 |
| ISO7721 VCC2 (≈ 1.6–4 mA each) | 8 | 15 |
| RS-485 failsafe bias 560 / 120 / 560 Ω | 4 | 8 |
| `+5V_ISO` exported on connectors | ? | ? |
| **Worst case** | **≈ 130 mA (OK)** | **≈ 265 mA: FAILS (> 200 mA)** |

Realistic average (CAN ~50 % dominant, one RS-485 driver active at a time): ≈ 190 mA, right at the limit. The unregulated output also rises at light load (unverified).

→ Use **2 W (400 mA)**: B0505S-2WR3 (DEXU brand, C3019590, 432 stock, $0.99 @1 / $0.59 @100 [LCSC]; no Mornsun-branded 2 W was found live). Or use two 1 W modules, one per domain. Remove `+5V_ISO` from the connectors, or fuse it with a PTC (review K8).

### 4.5 Standby (pack current at 51.2 V)
| Mode | What is on | Estimate |
|---|---|---|
| Run, comms on | everything | ≈ 1.5–2 W → **≈ 30–40 mA** |
| **Standby** (inverter off, pack idle) | AFE SLEEP 24–41 µA (DS); bucks in light load (LM5164 10.5 µA, LMR16006 28 µA at 12 V); AP2112 55 µA; MCU **Stop 1 59 µA at 25 °C / 555 µA at 85 °C** or Standby + RTC < 1 µA; FRAM / flash in sleep; **iso DC-DC, INA240, ESP32, LEDs switched off** | ≈ 0.1–0.2 mA at 25 °C. Without gating, add INA240 2.4 mA at 5 V, the iso module 8 mA no-load at 5 V and the rail LEDs D4 / D6 / D7 / D8 (~2 mA each) → about **1.5 mA from the pack** |
| **Ship / deep** | AFE SHUTDOWN 1 µA (DS); LM5164 off 3 µA (DS); divider leakage | **≈ 5–10 µA** (~7 mAh / month) |

Rail-indicator LEDs D4 / D6 / D7 / D8 should be DNP in production or use ≥ 10 k resistors. Today they alone cost more than the whole standby target.

---

## 5. ESS feature hardware checklist

Priority: **M = Must** (expected in a 2026 ESS BMS, or a requirement), **S = Should** (beats Daly / JBD / JK / Seplos / Pace; competitor claims are the matrix agent's), **N = Nice**. Costs are LCSC @100 where verified, otherwise "est.".

| # | Feature | Prio | Needed in 2026 ESS? | Hardware | MCU pins | Parts (LCSC, live 2026-11-17) | Cost add |
|---|---|---|---|---|---|---|---|
| 1 | **Inverter CAN 500 kbps, Pylontech-style** (IDs 0x351 / 355 / 356 / 359 / 35C / 35E, unverified) | M | yes; the main inverter link (Victron, SMA, Growatt, Deye …) | existing FDCAN1 + ISO7721 + TJA1051 + split termination. Fix K1 (TJA1051T/3 VIO pin 5). Add a termination DIP / jumper and an **RJ45** with an inverter-standard pinout. Classic CAN is enough; FD stays available | PA11 / PA12 | TJA1051T/3 C58988 $0.60; ISO7721DR C366164 $0.43 (Q1: C2867808, low stock); RJ45 HC-RJ45-5224-1-6 C3010562 $0.22 | +$0.3 (RJ45 + DIP) |
| 2 | **RS-485 Modbus** (inverter / EMS, also Pylontech RS-485) | M | yes | existing chain on USART2 with hardware DE. Fix K3: DIR isolator ISO7721**F** (C2872355, $1.27, **14 stock**) + pull-down. Termination / bias DIP. RJ45 | PA1 / PA2 / PA3 | THVD1450DR C2671361 $0.97 | +$0.3 |
| 3 | **Second RS-485, parallel packs** (link in / out, RJ45 ×2 as Seplos / Pace) | M | yes; ≥ 2 packs in parallel is the norm for 5–30 kWh ESS | THVD1450 + 2 × ISO7721 (one F type for DIR) + SM712 + bias / term DIP + **2 × RJ45 wired straight through** (in / out) | PB10 / PB11 / PB14 (USART3) | THVD1450DR C2671361; ISO7721DR C366164; RJ45 ×2 C3010562 | ≈ $2.6 |
| 4 | **Second CAN** (EMS or pack-to-pack; requirement R10) | M | yes (the requirement) | TJA1051T/3 + ISO7721 + NUP2105L + split termination. Carried on the same link RJ45 pair (in / out) | PB12 / PB13 (FDCAN2) | C58988, C366164 | ≈ $1.2 |
| 5 | **Pack addressing** | M (DIP) / S (auto) | DIP 0–15 is universal (unverified, matrix agent) | DIP: re-purpose SW_CFG1 as a 4-bit address; chemistry / cell count move to FRAM settings via app / PC tool. **Auto-address**: ADDR_OUT → opto → ADDR_IN of the next pack, on spare RJ45 link pins. The master assigns addresses in sequence and the UID breaks ties | expander P00–P05 | SW_CFG1 (field C318884 is wrong, §1.8); 2 × opto (e.g. EL357N / PC817, not verified) | DIP $0; auto ≈ $0.3 |
| 6 | **Bluetooth / WiFi** | S (market: M) | yes; phone apps are standard on JK / JBD / Daly | **ESP32-C3-MINI-1-N4** C2838502, 9,260 stock, $3.07 @1 / $2.14 @100 (BLE 5 + WiFi, OTA, can bridge to cloud). ESP32-C6-MINI-1-N4 C5736265: 110 stock, $3.02 @100 (adds Thread / Zigbee, WiFi 6). Own 3V3 rail + load switch (§4.1). Fit on board with antenna keep-out at the board edge, or a 2×5 header for a plug-in module. A UART-only BLE module is cheaper but loses WiFi / OTA | PC10 / PC11 (UART4) + EXP P14 / P15 | C2838502; AMS1117-3.3 C6186 $0.16; TPS22918 C131941 $0.25 | ≈ $2.7 (module) or $0.15 (header only) |
| 7 | **LED SOC bar + RUN / ALM + LCD header** | M | yes; front panel on every rack pack | 4 green SOC + green RUN + red ALM, on a front-panel connector (2×5) carrying 3V3, GND, I2C4, BTN, LED lines. Supports an I2C OLED / LCD board later | PA8, PB7, EXP P10–P13, PC6 / PC7 | TCA9535PWR C130204, 14,125 stock, $0.96; LEDs (not verified) | ≈ $1.3 |
| 8 | **Wake / reset button** | M | yes | tactile switch on the front panel. One press drives (a) PC13 WKUP2, (b) TS2 low through a diode = **BQ76952 wake from SHUTDOWN** (TS2 "functions as wakeup from SHUTDOWN", BQ76952 p.5 pin 22), (c) the LM5164 EN latch (#17). Long press = ship mode (firmware). An NRST button is optional (DNP) | PC13 | TS-1187A-B-A-B **C318884**, 526k stock, $0.02 | ≈ $0.1 |
| 9 | **Dry contacts** (alarm, generator start) | S | common on ESS (inverter gen-start) | 2 × photoMOS from expander outputs (no coil current, isolated by nature). **AQY212GS** C719745, 5,154 stock, $0.91 (60 V / 0.5 A per Panasonic, unverified), or TLP241A C2152214, $1.00 (40 V / 2 A, unverified). Mechanical alternative: SRD-05VDC-SL-C C35449 $0.26, but ~70 mA coil and large (unverified) | EXP P06 / P07 | C719745 | ≈ $2 + terminal |
| 10 | **Heating-pad driver** (LFP no charge < 0 °C) | S | yes for outdoor / cold-climate ESS | **4th low-side channel identical to Q_POS1** (logic-level FET, gate R / pull-down, flyback) driving an external heater relay / contactor. The heater power (48 V, 100–300 W) stays off-board. On TIM1_CH4, so the break also kills it. Heater NTC on an AFE channel | PC3 | reuse the contactor-driver parts | ≈ $0.25 + 2-pin terminal |
| 11 | **Fan driver** | S | useful: balancing dissipates up to 6.4 W (review A13) | low-side FET + flyback, 25 kHz PWM, tach input with 10 k pull-up + series R | PB15, PC12 | reuse FET / diode | ≈ $0.2 + 3-pin header |
| 12 | **Buzzer** | N | some packs have one | MLT-8530 passive buzzer + NPN / FET + diode. Rated −20…70 °C (search) | PB9 | **C94599**, 115k stock, $0.15 | ≈ $0.2 |
| 13 | **RTC + backup** | M | yes (timestamped logs) | LSE crystal + 2 caps (§1.7); VBAT from VDD, optional supercap (N) | PC14 / PC15, VBAT | Epson Q13FC13500004 **C32346** $0.12 | ≈ $0.13 (+$0.3 supercap) |
| 14 | **FRAM vs EEPROM** for fault log, SOC / SOH history | S | strongly recommended | **FM25V02A-GTR** C66029, 32 KB, 7,358 stock, $3.45 @1 / **$2.14 @100**. Same SPI SOIC-8 pin-out as the 25LC256 (drop-in, unverified pin check). Instant writes with no 5 ms page cycle and 10^14 endurance (unverified), so the SOC and the last fault can be written on brown-out (PVD interrupt). Larger: FM25W256-GTR C23520 $2.71 @100 (32 KB, 2.7–5.5 V). MB85RS256B C8742: no LCSC record returned. Keeping the 25LC256 works with a ring buffer + CRC (review M10) but loses brown-out safety | PA4 + SPI1 | C66029 | +≈ $1.6 vs EEPROM |
| 15 | **External flash for logs** ("black box") | S | differentiator | **W25Q64JVSSIQ** C179171, 8 MB, 1,053 stock, $1.37 @100. Holds years of daily per-cell min / max / SOH records, a pre / post-trigger fault waveform capture, and **a staged firmware image** for safe updates. W25Q128JVSIQ C97521 is only 17 in stock | PB1 + SPI1 | C179171 | ≈ $1.4 |
| 16 | **USB-C service port** | S | PC tool / factory set-up; competitors mostly use RS-485 / BT | USB-C → CH340C (VBUS-powered) → ISO7721 → USART1. **Isolated, because GND_PWR is pack negative and differs from laptop / PE ground when the NEG contactor is open.** A non-isolated native USB (PA11 / PA12) would also clash with FDCAN1 | PA9 / PA10 | TYPE-C-31-M-12 C165948 $0.15; USBLC6-2SC6 C7519 $0.12; CH340C C84681 $0.34; ISO7721DR C366164 $0.43 | ≈ $1.1 |
| 17 | **Ultra-low standby + wake chain** | M | yes (long storage, ship mode) | (a) **LM5164 EN latch**: a 300 V-class PNP / NPN pair or a 100 V FET pair (EN today is tied to VIN). It is held on by OR(PWR_HOLD from the MCU, BTN, wake-on-bus-voltage divider from V_INVERTER_BUS for a charger on the bus); the AFE "awake" output is for the AFE agent. (b) Load switches for the iso DC-DC (ISO_PWR_EN), the ESP32 rail and INA240 / analog. (c) MCU Stop 2 / Standby + RTC with WKUP from AFE_ALERT (PC5) and BTN (PC13). (d) AFE SLEEP / DEEPSLEEP / SHUTDOWN 24–41 / 9–10 / 1 µA (BQ76952 p.1) | PC9, PB6, PC5, PC13, EXP P14 / P16 | TPS22918 C131941 $0.25 ×2–3; SI2301 C10487 $0.07 (20 V only, low-voltage side); high-voltage transistors not verified | ≈ $1.0 |
| 18 | **Firmware update** over CAN / RS-485 / BLE / USB | M (firmware) | yes; field updates are expected | No extra silicon beyond #15. Custom bootloader in flash (16–32 KB). Image comes over CAN (inverter or link port; the master can push updates to slave packs), Modbus, BLE (ESP32 → UART4) or USB-C. It is staged in W25Q64 or the second half of the 256 KB flash, CRC / signature checked, then swapped, with a rollback copy. ROM bootloader as recovery (USART1 / FDCAN1 pins per AN2606, not read). Whether the 256 KB G473 supports dual-bank RWW is not verified (DS12288 states it for the 512 KB part) | – | – | $0 (+ #15) |
| 19 | **Isolated vs non-isolated comms** (48 V pack) | M decision | – | **Keep all external ports isolated** (inverter CAN + RS-485, link CAN + RS-485, USB service). Reasons: the low-side NEG contactor makes BMS ground ≠ system ground; several packs in parallel; surge on long cables. Cheap Chinese BMS often have non-isolated ports (unverified, matrix agent). Internal-only items (ESP32, LEDs, expander) stay non-isolated. Prefer two isolation domains (inverter ports / link ports, 1 W each) over one 2 W module. AFE-to-MCU isolation stays the separate decision of review S1 | – | 2nd B0505S-1W or a 2 W module (§4.4) | ≈ $1 |
| 20 | **Internal-COMP bidirectional OCP latch** (replaces TLV3501) | S | fixes review C1–C3 | second pad of ADC_I_SENSE on PB0; DAC3 thresholds; TIM1 break; INA240 output range fix (M7) | PA0, PB0 | remove U_OCP1, R_TH1 / 2, C_TH1 | −$1 |

### 5.1 Prioritised feature list

* **Must:**
  * #0 MCU → G473RCT6
  * #1 inverter CAN (with the VIO fix + RJ45 + termination switch)
  * #2 RS-485 Modbus (DIR default fix)
  * #3 second RS-485 for parallel packs with RJ45 in / out
  * #4 second CAN
  * #5 DIP pack address
  * #7 LED SOC bar + front panel
  * #8 wake button
  * #13 RTC + LSE
  * #17 power latch + load switches (standby)
  * #18 bootloader
  * #19 isolated external ports with an adequate isolated supply
* **Should:**
  * #5b auto-addressing
  * #6 ESP32-C3 BLE / WiFi
  * #9 dry contacts
  * #10 heater driver
  * #11 fan driver
  * #14 FRAM
  * #15 W25Q64 black box
  * #16 isolated USB-C service port
  * #20 internal-COMP OCP latch
* **Nice:**
  * #12 buzzer
  * VBAT supercap
  * LCD module (header in Must #7)
  * FDCAN3 footprint (I2C-AFE variant)
  * OPAMP PGA low-current channel

**Indicative BOM add for Must + Should:** ≈ $18–20 @100 (est.). The biggest items are the ESP32 module ($2.1), FRAM (+$1.6), external flash ($1.4), the second RS-485 chain ($2.6), photoMOS ($1.8), front panel ($1.3), USB service ($1.1), isolated-supply upgrade (~$1) and the MCU (+$0.7). It is partly offset by removing the TLV3501 network (≈ −$1).

---

## 6. Open points / not verified

* **Datasheets not opened:** RM0440 (UID address, COMP INMSEL / DAC mapping, break latch details, dual-bank on 256 KB, NRST mode); AN2606 (ROM bootloader pins for G47x); the G473-specific datasheet (pin table taken from the KiCad symbol); ES0431 / G47x errata (FDCAN, COMP).
* No LCSC listing was found for the **125 °C grades** (G473RCT3 / G474RET3 / G431CBT3); availability for −40…105 °C (R19) is unknown.
* JLCPCB assembly class (Basic / Extended) and JLC stock were not checked for any part.
* Unverified ratings: AQY212GS / TLP241A contact ratings; MLT-8530 drive voltage; ESP32-C3 TX current; B0505S-1WR3 exact no-load current; fan and coil currents (coil data missing, review P4); TCA9535 is not AEC.
* LCSC API returned **no record** for C8742 (MB85RS256B), C5426 (25LC256 field), C265225 (B0505S field), C41613 (B0505S-2WR2): these were not checked further.
* ISO7721**Q**DRQ1 (62 in stock) and ISO7721**F**QDRQ1 (14 in stock) are thin at LCSC. With 5–6 isolators per board, plan on the non-Q ISO7721DR (12,955 stock) or a second source, which conflicts with the AEC goal.
* The LM5164 EN latch topology and the AFE "awake" output depend on the AFE agent (REG1 / REGIN, multifunction-pin config).
* The Pylontech CAN IDs and RJ45 pin-outs are general knowledge; get the protocol documents before firmware work.

## Sources
* STM32G431 datasheet DS12589 Rev 2 (LCSC copy): https://datasheet.lcsc.com/datasheet/pdf/3f23d741047d660d2a0e8aabbc953854.pdf?productCode=C529355
* STM32G474 datasheet DS12288 Rev 4 (LCSC copy): https://datasheet.lcsc.com/datasheet/pdf/a99955f86e1b6873dffbae2a2058f698.pdf?productCode=C521608
* KiCad 10 symbol library `MCU_ST_STM32G4.kicad_sym` (local install)
* LCSC product API, e.g. https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C529361 (all C-numbers in this file were queried the same way on 2026-11-17)
* Local datasheet texts in `bms_work\review\ds\` (BQ76952, LM5164-Q1, LMR16006Y-Q1, AP2112, ISO7721-Q1, TJA1051, THVD1450, TLV3501, TPS3823)
* ST STM32A announcement (search): https://www.automotiveworld.com/news/st-launches-stm32a-family-for-edge-ai-car-compute/
* Mornsun B_S-1WR3 series data (search): https://www.mornsun-power.com/public/uploads/pdf/B_S-1WR3.pdf
* S32K144 LCSC listing: https://www.lcsc.com/product-detail/C508512.html ; FlexCAN FD on FlexCAN0 only (search): https://community.nxp.com/t5/S32K/S32K144-FlexCAN0-FD-Mode/m-p/2137448
