# Stage 5 Engineering Plan: Power Actuators, Contactors & Pre-Charge
## Automotive-Grade, Low-Side Smart Drivers with Coil PWM Economizing

---

## 1. Subsystem Overview & Core Requirements

* **Primary Function:** High-reliability switching and control of high-voltage battery contactors, automated pre-charge sequencing to protect inverter DC-link capacitors, and coil power economizing.
* **Actuator Channels:**
  1. **Main Positive Contactor (`CONT_POS`):** Connects the positive battery terminal to the DC bus.
  2. **Main Negative Contactor (`CONT_NEG`):** Connects the negative battery terminal to ground.
  3. **Pre-charge Relay (`PRE_CHARGE`):** Routes initial current through a current-limiting pre-charge resistor to charge inverter DC capacitors smoothly.
* **Drive Voltage:** **Regulated $+12.0\,\text{V}$** from Stage 1 Power Supply.

---

## 2. Pre-Charge Sequence & Inverter Voltage Sensing

```
+-----------------------------------------------------------------------------------------+
|                               PRE-CHARGE TIMING SEQUENCE                                |
|                                                                                         |
| 1. IDLE / STANDBY:                                                                      |
|    • CONT_POS = OPEN, CONT_NEG = OPEN, PRE_CHARGE = OPEN. System de-energized.          |
|                                                                                         |
| 2. STEP 1 (Ground Reference):                                                           |
|    • Close CONT_NEG. Low-side of battery stack is now locked to chassis/inverter return.|
|                                                                                         |
| 3. STEP 2 (Controlled Inrush Charge):                                                   |
|    • Close PRE_CHARGE relay. Current flows through 50 Ohm pre-charge resistor.          |
|    • Inrush current limited: I_peak = V_pack / R_precharge = 58V / 50 Ohm = 1.16 A.     |
|                                                                                         |
| 4. STEP 3 (Verification via HV Sense Divider):                                          |
|    • MCU ADC continuously reads V_INVERTER via precision 100:1 voltage divider.        |
|    • When V_INVERTER >= 95% of V_BATT (typically 200ms - 800ms), pre-charge is complete!|
|                                                                                         |
| 5. STEP 4 (Main Bus Closure):                                                           |
|    • Close CONT_POS. Main DC link is now direct-connected with ZERO contact arcing.     |
|    • Open PRE_CHARGE relay 50ms later. System is fully operational!                     |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Contactor Drivers & Coil Power Economizer (PWM)

### 3.1 Smart Driver Selection
* **Driver IC:** **Infineon BTS3050TF** / **Texas Instruments TLE92xx** or discrete automotive N-Channel MOSFETs (**Vishay SQ2318EY-T1_GE3**, AEC-Q101, $40\,\text{V}$, $8\,\text{A}$, $R_{\text{DS(on)}} < 25\,\text{m}\Omega$).
* **Protections:** Integrated active zener flyback clamping (clamps coil inductive kickback at $+42\,\text{V}$ to protect driver), thermal shutdown, and gate pull-down resistors.

### 3.2 High-Efficiency PWM Economizing
* **Problem:** Automotive contactors require $1.0\,\text{A} - 1.5\,\text{A}$ at $12\,\text{V}$ to pull in their heavy armature ($18\,\text{W}$ instantaneous), but once closed, they only need $250\,\text{mA}$ to remain held in place. Running $100\%$ duty cycle continuously boils the coil and wastes energy.
* **Solution:**
  * **Pull-In Phase (First $100\,\text{ms}$):** $100\%$ duty cycle ($12\,\text{V}$ full voltage) guarantees fast, snap closure.
  * **Holding Phase (After $100\,\text{ms}$):** Duty cycle drops to $25\% - 30\%$ PWM at $20\,\text{kHz}$ (filtered by coil inductance).
  * **Power Reduction:** Drops coil holding power from $18\,\text{W} \to \mathbf{1.5\,\text{W}}$ ($>90\%$ reduction in heat dissipation!).

---

## 4. JLCPCB SMT Bill of Materials (BOM)

| Function | RefDes | Value / MPN | Footprint | LCSC Part # | JLCPCB Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Contactor Drivers**| `Q_POS, Q_NEG, Q_PRE`| **SQ2318EY** 40V 8A N-Ch (3x)| `Package_TO_SOT_SMD:SOT-23` | `C2837410` | Standard |
| **Freewheel Diodes** | `D_FLY1, D_FLY2, D_FLY3`| **ES1J** 600V 1A Fast Diode | `Diode_SMD:D_SMA` | `C22452` | **Basic Part** |
| **Pre-charge Resistor**| `R_PRE` | $50\,\Omega\;25\,\text{W}$ Wirewound / TO-220| `Package_TO_SOT_SMD:TO-263-2` | `C2837415` | Standard |
| **HV Divider Top** | `R_HV1, R_HV2` | $1.00\,\text{M}\Omega\;1\%\;1206$ ($200\text{V}$) | `Resistor_SMD:R_1206_3216Metric` | `C14457` | **Basic Part** |
| **HV Divider Bottom**| `R_HV_BOT` | $20.0\,\text{k}\Omega\;0.1\%\;0603$ | `Resistor_SMD:R_0603_1608Metric` | `C25804` | **Basic Part** |
| **Contactor Terminal**| `J_CONT` | 6-Pin $5.08\,\text{mm}$ Screw Terminal | `TerminalBlock_Phoenix:MKDS-1,5-6-5.08` | `C2837420` | Standard |
