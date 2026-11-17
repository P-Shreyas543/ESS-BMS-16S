# System Architecture Master Plan
## Automotive-Grade, Low-Cost Battery Management System (BMS) for 7S–16S ESS

---

## 1. Complete System Architecture & Stage Map

This master document links the 7 subsystem engineering plans defining every stage of the BMS hardware, firmware interfaces, and manufacturing workflow:

```
====================================================================================================
                                      BMS SYSTEM ARCHITECTURE
====================================================================================================

               +-------------------------------------------------------------+
               |                    HIGH-VOLTAGE STACK                       |
               |             7S - 16S LFP (16V - 58V) / NMC (20V - 68V)      |
               +-------------------------------------------------------------+
                                      │                        │
         Pack Power (16V - 72V)       │                        │ Cell Sensing (VC0 - VC16)
         ─────────────────────────────┼────────┐               │ + 4x Pack NTC Thermistors
                                      │        │               │
                                      ▼        │               ▼
  +──────────────────────────────────────+     │    +──────────────────────────────────────+
  | STAGE 1: POWER SUPPLY SUBSYSTEM      |     │    | STAGE 2: AFE & CELL MONITORING       |
  | [plan_powerstage.md]                 |     │    | [plan_afe_cell_monitor.md]           |
  | • Stage 0: 75V TVS + Fuse + Polarity |     │    | • TI BQ76952-Q1 Automotive AFE       |
  | • Stage 1: HV Buck -> +12V Contactor |     │    | • 16-Ch Low-Pass RC Sense Filters    |
  | • Stage 2: Synchronous Buck -> +5V   |     │    | • 16x Active Passive Balance (100mA) |
  | • Stage 3: Clean LDO -> +3V3 MCU     |     │    | • Multi-point NTC Array (Pack + PCB) |
  | • Stage 4: Isolated DC-DC -> +5V_ISO |     │    +──────────────────────────────────────+
  +──────────────────────────────────────+     │                       │
           │              │             │      │                       │ Isolated SPI / I2C
           │ +12V         │ +5V         │ +3V3 │                       ▼ (ISO7741-Q1 Barrier)
           ▼              ▼             ▼      │    +──────────────────────────────────────+
  +────────────────+  +─────────+  +──────────────┼─►| STAGE 3: SAFETY MICROCONTROLLER      |
  | STAGE 5: POWER |  | STAGE 6:|  |              │  | [plan_mcu_safety.md]                |
  | ACTUATORS      |  | ISOLATED|  |              │  | • NXP S32K144 Automotive MCU (M4F)  |
  | [plan_power_   |  | COMMS   |  |              │  | • Hardware Window Watchdog          |
  |  actuators.md] |  | [plan_  |  |              │  | • Non-Volatile FRAM Fault Logger    |
  | • Main (+) Cont|  |  isolt_ |  |              │  | • 4-Pos Chem & Cell Count DIP SW    |
  | • Main (-) Cont|  |  comms. |  |              │  | • Real-time SoC/SoH Kalman Filter   |
  | • Pre-charge   |  |  md]    |  |              │  +──────────────────────────────────────+
  | • Coil PWM Eco |  | • CAN-FD|  |              │             │                │
  +────────────────+  | • RS-485|  |              │             │ Kelvin Sense   │
                      +─────────+  +──────────────┼─────────────┼────────────────┘
                                                  │             ▼
                                                  │  +──────────────────────────────────────+
                                                  │  | STAGE 4: HIGH-PRECISION CURRENT SENSE|
                                                  │  | [plan_current_sensing.md]            |
                                                  └─►| • 100uOhm / 50uOhm Manganin Shunt    |
                                                     | • TI INA240-Q1 Bi-directional Amp    |
                                                     | • <2us Hardware Short-Circuit Trip   |
                                                     +──────────────────────────────────────+

               +-------------------------------------------------------------+
               | STAGE 7: 4-LAYER PCB MANUFACTURING & JLCPCB PCBA AUTOMATION |
               | [plan_pcb_manufacturing.md]                                 |
               | • Standard JLC04161H-7628 Stackup (1.6mm, 1oz Cu)           |
               | • Strict IPC-2221B HV Clearance & 6.5mm Isolation Trench   |
               | • 100% JLCPCB Basic/Extended SMT Part Selection             |
               +-------------------------------------------------------------+
====================================================================================================
```

---

## 2. Directory Map of Engineering Plans

Every subsystem is documented in a dedicated engineering plan in the project directory:

| Document | Subsystem / Focus | Key Silicon / Standards |
| :--- | :--- | :--- |
| **[`plan_powerstage.md`](plan_powerstage.md)** | Stage 1: Power Supply Subsystem | LM5164-Q1 ($12\text{V}$), TPS62933 ($5\text{V}$), AP2112K ($3.3\text{V}$), B0505S ($5\text{V}_{\text{ISO}}$) |
| **[`plan_afe_cell_monitor.md`](plan_afe_cell_monitor.md)** | Stage 2: AFE & Cell Balancing | TI BQ76952-Q1, 16x SOT-23 balance switches, 16S/8S/7S masking |
| **[`plan_mcu_safety.md`](plan_mcu_safety.md)** | Stage 3: Safety MCU & Logic | NXP S32K144 / ST, External Window Watchdog, 32KB FRAM, DIP Switch |
| **[`plan_current_sensing.md`](plan_current_sensing.md)** | Stage 4: Current Shunt & OCP | $100\,\mu\Omega$ Manganin Shunt, INA240-Q1, Fast Hardware Trip Comparator |
| **[`plan_power_actuators.md`](plan_power_actuators.md)** | Stage 5: Contactors & Relays | Main (+)/(-) drivers, Pre-charge circuit, Contactor PWM economizer |
| **[`plan_isolated_comms.md`](plan_isolated_comms.md)** | Stage 6: Isolated Communications | Isolated CAN-FD (TCAN1042 + ISO7721), Isolated RS-485 Modbus RTU |
| **[`plan_pcb_manufacturing.md`](plan_pcb_manufacturing.md)** | Stage 7: PCB DFM/DFA & PCBA | JLC04161H 4-Layer stackup, IPC-2221B creepage, optical fiducials |

---

## 3. Standard Signals & Global Bus Interconnect

All sub-sheets interface cleanly through standardized global labels:

```
POWER BUS:
  V_BATT+       : Raw positive battery pack voltage (16V - 72V)
  GND_PWR       : Primary power ground (Battery stack negative return)
  +12V          : Regulated 12V supply for contactor coils, relays, fans (LM5164-Q1)
  +5V           : Regulated 5V intermediate supply for CAN transceivers & isolators
  +3V3          : Regulated 3.3V ultra-low-noise logic supply for MCU & ADC
  +5V_ISO       : Galvanically isolated 5V supply for external communication ports
  GND_ISO       : Isolated ground return for RS-485 / external inverter ports

AFE & SENSING BUS:
  VC0 .. VC16   : Cell voltage sensing taps 0 through 16
  BAL0 .. BAL15 : Passive balance control drive lines
  NTC1 .. NTC4  : Battery pack temperature thermistor channels
  NTC_PCB       : On-board thermistor for balancing resistor thermal monitor
  I_SENSE+ / -  : Kelvin 4-wire differential sense lines from current shunt
  OC_ALERT      : Hardware over-current fast-trip interrupt to MCU

CONTROL & ACTUATION BUS:
  CONT_POS_DRV  : Gate drive signal for Main Positive Contactor
  CONT_NEG_DRV  : Gate drive signal for Main Negative Contactor
  PRECHARGE_DRV : Gate drive signal for Pre-charge Relay
  HV_SENSE_INV  : Inverter DC-link voltage sense divider input to MCU ADC

COMMUNICATION BUS:
  CAN_H / CAN_L : High-speed CAN-FD differential bus to Energy Management System (EMS)
  RS485_A / B   : Modbus RTU differential pair to hybrid solar/storage inverters
  AFE_SCL / SDA : Isolated digital interface between Safety MCU and BQ76952-Q1
```

---

## 7. Automotive-Grade Transient, TVS & ESD Protection Architecture

In accordance with **ISO 7637-2 / ISO 16750-2** (Road vehicles — Electrical disturbances from conduction and coupling), **ISO 10605 / IEC 61000-4-2** (Road vehicles — Test methods for electrical disturbances from electrostatic discharge), and **AEC-Q101** semiconductor qualification standards, all external ports, inductive gates, and low-level sensing lines are protected by dedicated transient suppression silicon:

| Subsystem / Port | Component Reference | Part Number & Rating | Package | JLCPCB / LCSC | Protection Standard & Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CAN-FD Bus (`J_CAN1`)** | `D_TVS_CAN1` | **NUP2105LT1G** (24V $V_{RWM}$, 350W peak) | SOT-23 | `C12948` | **ISO 10605 / ISO 7637-3**: $\pm 30\text{kV}$ air / contact ESD clamp across `NET_CANH` and `NET_CANL` to `GND_ISO`. Clamps high-speed differential bus transience with $<30\text{pF}$ parasitic capacitance. |
| **RS-485 Modbus (`J_485_1`)** | `D_TVS_485_1` | **SM712** (Asymmetrical $-7\text{V} / +12\text{V}$, 600W) | SOT-23 | `C19002` | **IEC 61000-4-2 / IEC 61000-4-5**: Asymmetrical dual TVS array tailored for RS-485 transceiver common-mode range ($-7\text{V}$ to $+12\text{V}$), protecting `RS485_A` and `RS485_B` against ground bounce and lightning surge. |
| **Pos Contactor Gate (`Q_POS1`)** | `D_Z_POS1` | **BZX84-C18** (18V Zener clamp, 350mW) | SOD-323 | `C22809` | **AEC-Q101 Inductive Protection**: Clamps Gate-Source ($V_{GS}$) below $\pm 18\text{V}$ absolute maximum rating, preventing gate oxide puncture caused by high-voltage Miller capacitive kickback ($C_{gd}\frac{dv}{dt}$) during inductive contactor de-energization. |
| **Neg Contactor Gate (`Q_NEG1`)** | `D_Z_NEG1` | **BZX84-C18** (18V Zener clamp, 350mW) | SOD-323 | `C22809` | Clamps Gate-Source ($V_{GS}$) of main negative contactor driver MOSFET. |
| **Precharge Gate (`Q_PRE1`)** | `D_Z_PRE1` | **BZX84-C18** (18V Zener clamp, 350mW) | SOD-323 | `C22809` | Clamps Gate-Source ($V_{GS}$) of pre-charge relay driver MOSFET. |
| **Current Sense Input (`U_ISENSE1`)** | `D_TVS_SHUNT1` | **SMAJ5.0CA** (5.0V Bidirectional, 400W peak) | SMA | `C8063` | **Short-Circuit Inductive Clamp**: Directly shunts differential voltage across `AMP_IN+` and `AMP_IN-` to $<9.2\text{V}$ during extreme multi-kiloamp battery short circuits ($L\frac{di}{dt}$ transients), safeguarding the INA240 input stage. |
| **Ext NTC Channel 1 (`J_NTC1`)** | `D_ESD_NTC1` | **ESD5V0D3B** (5.0V Bidirectional ESD, 350W) | SOD-323 | `C84296` | **ISO 10605 ESD**: $\pm 30\text{kV}$ air / contact ESD suppression on battery module temperature sensor wire harness entering the pack enclosure. |
| **Ext NTC Channel 2 (`J_NTC2`)** | `D_ESD_NTC2` | **ESD5V0D3B** (5.0V Bidirectional ESD, 350W) | SOD-323 | `C84296` | $\pm 30\text{kV}$ ESD clamp on Module 2 NTC harness. |
| **Ext NTC Channel 3 (`J_NTC3`)** | `D_ESD_NTC3` | **ESD5V0D3B** (5.0V Bidirectional ESD, 350W) | SOD-323 | `C84296` | $\pm 30\text{kV}$ ESD clamp on Module 3 NTC harness. |
| **Ext NTC Channel 4 (`J_NTC4`)** | `D_ESD_NTC4` | **ESD5V0D3B** (5.0V Bidirectional ESD, 350W) | SOD-323 | `C84296` | $\pm 30\text{kV}$ ESD clamp on Module 4 NTC harness. |
| **Main Battery Input (`J1`)** | `D1` | **SMCJ75A** (75V Unidirectional TVS, 1500W) | SMC | `C14480` | **ISO 16750-2 Load Dump (Pulse 5b)**: Primary battery power input TVS clamp absorbing inductive surges and load dump transients up to $1500\text{W}$ peak pulse power. |
| **Reverse Polarity (`J1`)** | `D2` | **SS310** (100V 3A Schottky) | SMB | `C2494` | Protects low-voltage buck converters against accidental reverse battery pack polarity. |
| **Contactor Coils (`D_FLY1..3`)** | `D_FLY1..3` | **S3M** (1000V 3A Fast Recovery) | SMB | `C88806` | Absorbs flyback energy from high-inductance contactor coils ($0.5\text{H} - 5\text{H}$) during emergency shutdown. |

