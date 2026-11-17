# Power Stage Architecture & Implementation Plan
## Automotive-Grade, Low-Cost BMS for 7S–16S LFP & NMC Energy Storage Systems

---

## 1. Executive Summary & Power Rails Definition

To answer the architecture question directly: **Why do we need $12\text{V}$, $5\text{V}$, and $3.3\text{V}$, and how is each rail generated?**

In an automotive-grade, commercial Energy Storage System (ESS), three distinct power rails are required to ensure safety, industrial compatibility, and low noise:

```
+-------------------------------------------------------------------------------------------------+
|                                 BMS SYSTEM POWER DISTRIBUTION                                   |
|                                                                                                 |
|   Pack Input: 16V - 72V (7S LFP to 16S NMC)                                                     |
|       │                                                                                         |
|       ├──► [STAGE 0: Input Protection] (Fuse + 75V TVS + Reverse Polarity Schottky)             |
|       │         │                                                                               |
|       │         ▼                                                                               |
|       ├──► [STAGE 1: Main High-Voltage Buck (LM5164-Q1)] ─────────────────► +12V Contactor Rail |
|       │         │                                                           (12V @ 1.0A - 1.5A) |
|       │         ▼                                                           • Main Contactors   |
|       ├──► [STAGE 2: Intermediate Step-Down (LMR36506-Q1 / Buck)] ────────► +5V System Rail     |
|       │         │                                                           (5V @ 0.6A)         |
|       │         ▼                                                           • CAN-FD / RS-485   |
|       ├──► [STAGE 3: Low-Noise Precision LDO (AP2112K / TPS7A25)] ────────► +3V3 MCU Logic Rail |
|       │         │                                                           (3.3V @ 0.3A)       |
|       │         ▼                                                           • MCU (S32K144)     |
|       └──► [STAGE 4: Galvanic Isolation DC-DC (B0505S / SN6505B)] ────────► +5V_ISO Comms Rail  |
|                                                                             (5V @ 0.2A Isolated)|
|                                                                             • Inverter Modbus   |
+-------------------------------------------------------------------------------------------------+
```

---

## 2. Power Rail Budget & Consumer Mapping

| Power Rail | Nominal Voltage | Peak Current | Continuous Current | Primary Consumers | Why This Voltage? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`+12V`** | $12.0\,\text{V} \pm 3\%$ | $1.5\,\text{A}$ (Pull-in) | $250\,\text{mA}$ (Hold w/ PWM) | • Main (+) & (-) Contactors<br>• Pre-charge Relay<br>• Optional 12V Cooling Fan | Industrial & automotive contactor coils (Gigavac, TE EV200, Song Chuan) are standard $12\,\text{V}$. |
| **`+5V`** | $5.0\,\text{V} \pm 2\%$ | $600\,\text{mA}$ | $200\,\text{mA}$ | • CAN-FD Transceiver (TCAN1042-Q1)<br>• Digital Isolators (ISO7741-Q1)<br>• Current Shunt Amplifier (INA240)<br>• Input to +3.3V LDO | Automotive CAN transceivers and isolated differential amplifiers require a rigid $5.0\,\text{V}$ rail. |
| **`+3V3`** | $3.30\,\text{V} \pm 1\%$ | $300\,\text{mA}$ | $85\,\text{mA}$ | • Safety MCU (NXP S32K144 / ST)<br>• External Flash / EEPROM<br>• Temperature Sensor NTC Bias<br>• Status LEDs & Hardware DIP Switch | Microcontroller core, high-resolution ADC, clock oscillators, and digital logic operate at $3.3\,\text{V}$. |
| **`+5V_ISO`**| $5.0\,\text{V} \pm 4\%$ | $200\,\text{mA}$ | $60\,\text{mA}$ | • Isolated RS-485 Modbus Transceiver<br>• External EMS CAN Interface | Galvanically isolated from battery ground ($\ge 2.5\,\text{kV}_{\text{rms}}$) to prevent ground loops with solar inverters. |

---

## 3. Detailed Stage-by-Stage Implementation Plan

### Stage 0: Input Transient Protection & Dual-Source MUX
* **Purpose:** Protect electronics against inductive kickback, lightning surges, and accidental reverse battery connection.
* **Input Envelope:**
  * Minimum: $16.0\,\text{V}$ (7S LFP discharged to $2.28\,\text{V}/\text{cell}$).
  * Maximum: $68.0\,\text{V}$ (16S NMC charged to $4.25\,\text{V}/\text{cell}$).
  * Surge limit: $100.0\,\text{V}$ withstand ($<100\,\text{ms}$).
* **Circuit Components:**
  1. **Fuse `F1`:** $2.5\,\text{A}$, $125\,\text{V}$ Fast-acting SMD 1206 (Littelfuse 0466).
  2. **TVS Diode `D1`:** `SMCJ75A` Uni-directional ($75\,\text{V}$ standoff, $120\,\text{V}$ max clamping at $12.5\,\text{A}$ surge).
  3. **Reverse Polarity Protection `D2`:** `SS310` ($100\,\text{V}$, $3\,\text{A}$ Schottky in SMB, or P-MOSFET gate-clamp).
  4. **Auxiliary Cold-Start Input `J_AUX`:** 2-pin header allowing bench power via an external $12\,\text{V}$ wall adapter without needing a live battery stack.

---

### Stage 1: Primary High-Voltage Buck ($V_{\text{BATT}} \to +12.0\,\text{V}$)
* **Topology:** Non-isolated Synchronous Step-Down (Buck) Converter.
* **IC Selection:** **Texas Instruments LM5164-Q1** (AEC-Q100 Grade 1).
  * Input range: $6\,\text{V}$ to $100\,\text{V}$ continuous.
  * Internal power switches: High-side and low-side synchronous MOSFETs.
  * Quiescent current: Ultra-low $10\,\mu\text{A}$ standby.
  * Package: SOIC-8 PowerPAD (`HSOP-8-1EP`).
* **Sizing Calculation for $+12.0\,\text{V}$ Output:**
  $$V_{\text{OUT}} = V_{\text{FB}} \times \left(1 + \frac{R_{\text{FB1}}}{R_{\text{FB2}}}\right) = 1.20\,\text{V} \times \left(1 + \frac{90.9\,\text{k}\Omega}{10.0\,\text{k}\Omega}\right) = 1.20 \times 10.09 = \mathbf{12.1\,\text{V}}$$
* **Inductor Sizing:** $L_1 = 47\,\mu\text{H}$ to $68\,\mu\text{H}$, $I_{\text{sat}} \ge 1.8\,\text{A}$ (e.g., Sunlord SWPA8040 series).
* **Duty Cycle across 7S–16S:**
  * At 16S NMC ($68\,\text{V}$): $D = 12 / 68 = 17.6\%$ (well within minimum on-time).
  * At 7S LFP ($16\,\text{V}$): $D = 12 / 16 = 75.0\%$ (well below LM5164 maximum duty cycle of $>95\%$).

---

### Stage 2: Intermediate Buck ($+12.0\,\text{V} \to +5.0\,\text{V}$)
* **Why a second Buck instead of an LDO?**
  * Stepping down $12\,\text{V} \to 5\,\text{V}$ with an LDO at $300\,\text{mA}$ would dissipate:
    $$P_{\text{loss}} = (12\,\text{V} - 5\,\text{V}) \times 0.3\,\text{A} = \mathbf{2.1\,\text{W}}$$
    This creates an unacceptable local hot spot on an automotive PCB!
  * Using a high-efficiency miniature synchronous buck (efficiency $>92\%$):
    $$P_{\text{loss}} \approx 0.12\,\text{W}\quad (\text{virtually zero heat!})$$
* **IC Selection:** **TI LMR36506-Q1** or **Monolithic Power MP2315** / **TI TPS62933** (65V/36V synchronous buck, SOT-23-6 or TSOT-23-8).
* **Output:** Clean $5.0\,\text{V}$ @ $600\,\text{mA}$.

---

### Stage 3: Low-Noise Precision LDO ($+5.0\,\text{V} \to +3.3\,\text{V}$)
* **Topology:** Low-Dropout Linear Regulator (LDO).
* **Dissipation:**
  $$P_{\text{loss}} = (5.0\,\text{V} - 3.3\,\text{V}) \times 0.1\,\text{A} = \mathbf{0.17\,\text{W}}\quad (\text{well within SOT-23-5 thermal envelope})$$
* **IC Selection:** **Diodes Inc AP2112K-3.3** (or TI TPS7A2533-Q1).
  * Output current: $600\,\text{mA}$.
  * Dropout voltage: Ultra-low $250\,\text{mV}$ at $600\,\text{mA}$.
  * Noise: Ultra-low output ripple for high-accuracy 12-bit/16-bit ADC sampling.
  * Package: `SOT-23-5` (JLCPCB Basic Part: `C138760`).

---

### Stage 4: Galvanic Isolation DC-DC ($+5.0\,\text{V} \to +5.0\,\text{V}_{\text{ISO}}$)
* **Purpose:** Provide an isolated supply for the RS-485 Modbus and external CAN-FD bus connected to solar inverters and grid controllers.
* **Isolation Rating:** $3000\,\text{V}_{\text{DC}}$ / $2500\,\text{V}_{\text{rms}}$ reinforced isolation.
* **Component Selection:**
  * **Option A (Modular):** **Mornsun B0505S-1WR3** (SIP-4 compact module, JLCPCB standard stock).
  * **Option B (Discrete AEC-Q):** **TI SN6505B-Q1** push-pull driver with Coilcraft or Wurth planar isolation transformer.

---

## 4. JLCPCB SMT BOM & Sourcing Matrix

| Stage | RefDes | Value / MPN | Footprint | LCSC Part # | JLCPCB Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Protection** | `F1` | 2.5A 125V Fuse | `Fuse_1206_3216Metric` | `C2891395` | Standard |
| **Protection** | `D1` | SMCJ75A TVS Diode | `Diode_SMD:D_SMC` | `C80614` | Standard |
| **Protection** | `D2` | SS310 Schottky (100V 3A) | `Diode_SMD:D_SMB` | `C8678` | **Basic Part** |
| **Stage 1 (12V)**| `U1` | **LM5164-Q1** (100V Buck) | `HSOP-8-1EP_3.9x4.9mm` | `C497166` | Standard |
| **Stage 1 (12V)**| `L1` | $47\,\mu\text{H}\;2\,\text{A}$ Inductor | `L_7.3x7.3_H4.5` | `C408332` | Standard |
| **Stage 1 (12V)**| `R_FB1` | $90.9\,\text{k}\Omega\;1\%\;0603$ | `R_0603_1608Metric` | `C23224` | **Basic Part** |
| **Stage 1 (12V)**| `R_FB2` | $10.0\,\text{k}\Omega\;1\%\;0603$ | `R_0603_1608Metric` | `C25804` | **Basic Part** |
| **Stage 2 (5V)** | `U2` | **TPS62933 / LMR36506** | `SOT-23-6 / SOT-563` | `C2924147` | Standard |
| **Stage 2 (5V)** | `L2` | $4.7\,\mu\text{H}\;1.5\,\text{A}$ Inductor | `L_0806 / L_4x4` | `C265287` | Standard |
| **Stage 3 (3.3V)**| `U3` | **AP2112K-3.3** (LDO) | `Package_TO_SOT_SMD:SOT-23-5` | `C138760` | **Basic Part** |
| **Stage 4 (ISO)** | `U4` | **B0505S-1WR3** (1W Isolated) | `Converter_DCDC:Mornsun_B0505S-1WR3` | `C70155` | Standard |
| **Decoupling** | `C_IN` | $10\,\mu\text{F}\;100\,\text{V}\;\text{X7R}$ | `C_1210_3225Metric` | `C134763` | Standard |
| **Decoupling** | Caps | $100\,\text{nF}\;50\,\text{V}\;0603$ | `C_0603_1608Metric` | `C14663` | **Basic Part** |
| **Indicators** | `D_12V`| Blue LED 0603 (12V OK) | `LED_SMD:LED_0603_1608Metric` | `C72044` | **Basic Part** |
| **Indicators** | `D_5V` | Yellow LED 0603 (5V OK) | `LED_SMD:LED_0603_1608Metric` | `C72043` | **Basic Part** |
| **Indicators** | `D_3V3`| Green LED 0603 (3.3V OK) | `LED_SMD:LED_0603_1608Metric` | `C72041` | **Basic Part** |

---

## 5. Implementation Roadmap for Schematic `01_Power_Supply.kicad_sch`

1. **Update Schematic Hierarchy:**
   - Redraw `01_Power_Supply.kicad_sch` with explicit graphical sub-circuits:
     * `[SECTION A: Input Protection & Auxiliary OR-ing]`
     * `[SECTION B: +12V Contactor Supply (LM5164-Q1)]`
     * `[SECTION C: +5V Intermediate Logic Supply]`
     * `[SECTION D: +3.3V Clean MCU & Reference Supply]`
     * `[SECTION E: +5V_ISO Galvanic Isolation Power Module]`
2. **Visual Cleanliness:**
   - Draw formal wire lines and junction dots between components rather than purely disconnected pin labels.
   - Separate power ground (`GND_PWR`), analog logic ground (`GND`), and isolated ground (`GND_ISO`).
3. **Automated Validation:**
   - Re-run `kicad-cli sch erc` to guarantee 0 errors.
