# Stage 3 Engineering Plan: Safety Microcontroller & Logic Core
## Automotive-Grade, Functional Safety (ASIL-B Ready), Scalable Architecture

---

## 1. Subsystem Overview & Core Requirements

* **Primary Function:** Overall pack management, real-time SoC/SoH estimation, contactor state-machine sequencing, thermal management, fault handling, and CAN-FD/RS-485 communications.
* **Core Silicon:** **NXP S32K144 / ST STM32G4 Automotive**
  * **Architecture:** ARM Cortex-M4F with Hardware Floating Point Unit (FPU) and Memory Protection Unit (MPU).
  * **Automotive Qualification:** AEC-Q100 Grade 1 ($-40^\circ\text{C}$ to $+125^\circ\text{C}$).
  * **Functional Safety:** ISO 26262 ASIL-B compliant hardware metrics (ECC on Flash and SRAM, clock monitor, core self-test libraries).
  * **Memory:** $512\,\text{KB}$ Flash with ECC + $64\,\text{KB}$ SRAM with ECC.
  * **Peripherals:** Dual FlexCAN / CAN-FD modules, high-speed SPI, isolated UART/RS-485, hardware CRC engine.
  * **Package:** `LQFP-64` ($10 \times 10\,\text{mm}, 0.5\,\text{mm}$ pitch), standard JLCPCB SMT inventory.

---

## 2. Hardware Safety & Supervisory Architecture

### 2.1 External Windowed Hardware Watchdog
* **Why an external watchdog?**
  * Under ISO 26262 and IEC 62619, software cannot be solely relied upon to detect its own crashes or infinite loops.
* **IC Selection:** **Texas Instruments TPS3851-Q1** (AEC-Q100).
  * Window watchdog with programmable timeout via capacitor.
  * Requires a periodic "kick" heartbeat pulse from the MCU within an exact time window (e.g., between $50\,\text{ms}$ and $100\,\text{ms}$).
  * If the MCU locks up or runs too fast (clock failure), the watchdog forces an immediate hard reset and trips the hardware safety latch to open the main contactors!

### 2.2 Non-Volatile Lifetime & Fault Logging
* **IC Selection:** **Microchip 25LC256-I/SN** (AEC-Q100, $256\,\text{Kb}$ SPI EEPROM) or **Infineon CY15B104Q** (Automotive SPI FRAM).
* **Storage Allocation:**
  1. **Lifetime Operating Metrics:** Cumulative pack throughput (Ah / kWh), total cycle count, maximum/minimum temperature records, peak discharge current.
  2. **Fault Blackbox Logger:** Circular buffer recording the last 50 fault events with full system snapshot (all 16 cell voltages, pack current, temperatures, and timestamp).

### 2.3 Hardware Configuration DIP Switch (7S–16S & Chemistry)
An on-board 4-position SPST DIP switch (`SW_CONFIG`) connected to MCU GPIOs with internal pull-ups:
* **Switch 1 (Chemistry):**
  * `OFF (1)`: **LiFePO4 (LFP)** profile ($3.2\,\text{V}$ nominal, $3.65\,\text{V}$ max).
  * `ON  (0)`: **NMC / Li-Ion** profile ($3.7\,\text{V}$ nominal, $4.20\,\text{V}$ max).
* **Switch 2–4 (Series Cell Count):**
  * `000`: 7S
  * `001`: 8S
  * `010`: 10S
  * `011`: 12S
  * `100`: 13S
  * `101`: 14S
  * `110`: 15S
  * `111`: 16S (Default)
* *Software Lock:* The hardware DIP switch can be read at boot or overridden via authenticated CAN-FD service commands for remote commissioning.

---

## 3. Circuit Schematics & Peripheral Interfaces

```
                          +------------------------------------+
                          |       SAFETY MCU (S32K144)         |
                          |                                    |
   [3.3V Logic Rail] ────►| VDD / VDDA (Filtered with LC bead) |
   [GND Logic Rail]  ────►| VSS / VSSA                         |
                          |                                    |
   [8MHz Crystal]    ────►| XTAL_IN / XTAL_OUT (AEC-Q200)      |
                          |                                    |
   [TPS3851-Q1]      ◄───►| WDI (Heartbeat Kick) / RESET_N     |
   [SPI EEPROM]      ◄───►| SPI_SCK / MISO / MOSI / CS_MEM     |
   [4-Pos DIP SW]    ────►| GPIO_CFG[0..3] (Internal Pull-up)  |
   [10-Pin SWD]      ◄───►| SWD_CLK / SWD_DIO / RESET          |
                          |                                    |
   [AFE Interface]   ◄───►| SPI_AFE (via ISO7741 Isolator)     |
   [Current Amp]     ────►| ADC_I_SENSE (12-bit / 16-bit)      |
   [Contactors]      ────►| CONT_POS / CONT_NEG / PRECHARGE    |
   [CAN-FD Trx]      ◄───►| CAN_TX / CAN_RX                    |
   [RS-485 Trx]      ◄───►| UART_TX / UART_RX / RS485_DIR      |
                          +------------------------------------+
```

---

## 4. JLCPCB SMT Bill of Materials (BOM)

| Function | RefDes | Value / MPN | Footprint | LCSC Part # | JLCPCB Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Safety MCU** | `U_MCU` | **S32K144UATOVLFT** (LQFP-64) | `Package_QFP:LQFP-64_10x10mm_P0.5mm` | `C361254` | Standard |
| **Crystal Oscillator**| `Y1` | $8.000\,\text{MHz}\;12\,\text{pF}$ (AEC-Q200) | `Crystal:Crystal_SMD_3225-4Pin` | `C115962` | **Basic Part** |
| **Crystal Caps** | `C_X1, C_X2`| $18\,\text{pF}\;50\,\text{V}\;\text{NP0}\;0603$ | `Capacitor_SMD:C_0603_1608Metric` | `C1644` | **Basic Part** |
| **Watchdog IC** | `U_WDOG` | **TPS3851G33EDDRBRQ1** | `Package_SON:VSON-8_3x3mm_P0.65mm` | `C2837385` | Standard |
| **SPI EEPROM** | `U_MEM` | **25LC256-I/SN** ($256\,\text{Kb}$) | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`| `C7588` | Standard |
| **DIP Switch** | `SW_CFG` | 4-Position SPST SMD DIP | `Button_Switch_SMD:SW_DIP_SPSTx04_Slide_Copal_CHS-04B_W5.4mm_P1.27mm` | `C318884` | Standard |
| **Debug Header** | `J_SWD` | $2 \times 5$ Pin $1.27\,\text{mm}$ Cortex | `Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD` | `C2932845` | Standard |
| **Decoupling Caps**| `C_VDD1..8`| $100\,\text{nF}\;16\,\text{V}\;\text{X7R}\;0603$ | `Capacitor_SMD:C_0603_1608Metric` | `C14663` | **Basic Part** |
| **Bulk Decoupling**| `C_BLK` | $10\,\mu\text{F}\;10\,\text{V}\;\text{X7R}\;0805$ | `Capacitor_SMD:C_0805_2012Metric` | `C15850` | **Basic Part** |
