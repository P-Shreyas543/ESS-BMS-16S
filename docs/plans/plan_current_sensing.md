# Stage 4 Engineering Plan: High-Precision Current Sensing & Hardware OCP
## Automotive-Grade, Bidirectional, Kelvin 4-Wire Architecture

---

## 1. Subsystem Overview & Core Requirements

* **Primary Function:** High-resolution bidirectional battery current measurement (for accurate State-of-Charge Coulomb counting) and ultra-fast hardware over-current/short-circuit detection.
* **Current Specifications:**
  * **Continuous Rating:** $\pm 200\,\text{A}_{\text{DC}}$ continuous.
  * **Peak Pulse Rating:** $\pm 500\,\text{A}$ peak ($10\,\text{seconds}$).
  * **Measurement Resolution:** $\le 50\,\text{mA}$ across full range.
  * **Hardware Short-Circuit Trip Response:** $<2.0\,\mu\text{s}$ (hardware comparator directly trips the contactor driver latch without waiting for MCU firmware loops).

---

## 2. Shunt Resistor Selection & Thermal Sizing

### 2.1 Shunt Value & Sizing Calculation
* **Target Resistance:** $R_{\text{SHUNT}} = 100\,\mu\Omega$ ($0.000100\,\Omega$).
* **Voltage Drop:**
  * At $200\,\text{A}$ continuous:
    $$V_{\text{SHUNT}} = 200\,\text{A} \times 0.000100\,\Omega = \mathbf{\pm 20.0\,\text{mV}}$$
  * At $500\,\text{A}$ peak:
    $$V_{\text{SHUNT}} = 500\,\text{A} \times 0.000100\,\Omega = \mathbf{\pm 50.0\,\text{mV}}$$
* **Continuous Power Dissipation:**
  $$P_{\text{DISS}} = I^2 R = (200\,\text{A})^2 \times 0.000100\,\Omega = \mathbf{4.0\,\text{W}}$$
* **Component Selection:** **Bourns CSS2H-5930R-100U** or **Isabellenhütte BVS**
  * Electron-beam welded Manganin alloy element with copper terminations.
  * Power rating: $5.0\,\text{W}$ to $10.0\,\text{W}$ with heat-sink copper planes.
  * Temperature coefficient: $\pm 50\,\text{ppm}/^\circ\text{C}$ (extreme thermal stability across $-40^\circ\text{C}$ to $+105^\circ\text{C}$).
  * Package: `5930 SMD` (Standard JLCPCB / LCSC stock: `C2837390`).

---

## 3. Signal Conditioning & Hardware Over-Current Protection (OCP)

### 3.1 Current Sense Amplifier
* **IC Selection:** **Texas Instruments INA240A2-Q1**
  * AEC-Q100 Grade 1 qualified.
  * Fixed gain: $A_v = 50\,\text{V/V}$.
  * Enhanced PWM Rejection: Eliminates false spikes caused by inverter switching common-mode transients.
  * Input Common-Mode Voltage Range: $-4\,\text{V}$ to $+80\,\text{V}$ (operates safely even during ground bounce or inductive disconnects).
  * CMRR: $>120\,\text{dB}$.
* **Output Voltage Mapping:**
  * Reference voltage: $V_{\text{REF}} = 1.65\,\text{V}$ (half of $3.3\,\text{V}$ rail for bidirectional current):
    * At $0\,\text{A}$: $V_{\text{OUT}} = 1.650\,\text{V}$
    * At $+200\,\text{A}$ (Discharge): $V_{\text{OUT}} = 1.65\,\text{V} + (20\,\text{mV} \times 50) = 1.65 + 1.00 = \mathbf{2.650\,\text{V}}$
    * At $-200\,\text{A}$ (Charge): $V_{\text{OUT}} = 1.65\,\text{V} - (20\,\text{mV} \times 50) = 1.65 - 1.00 = \mathbf{0.650\,\text{V}}$
    * At $+500\,\text{A}$ (Peak Pulse): $V_{\text{OUT}} = 1.65\,\text{V} + (50\,\text{mV} \times 50) = \mathbf{3.150\,\text{V}}$ (within $3.3\,\text{V}$ ADC full-scale).

### 3.2 Dual-Tier Hardware Over-Current Comparator (<2us Trip)
* **IC Selection:** **Texas Instruments TLV3201-Q1** (Automotive high-speed comparator, $40\,\text{ns}$ propagation delay).
* **Tier 1 (Firmware Warning):** Handled by MCU 12-bit ADC threshold interrupts ($250\,\text{A}$ for $>500\,\text{ms}$).
* **Tier 2 (Hardware Hard Short-Circuit Trip):**
  * Threshold set by a precision resistor divider to $3.15\,\text{V}$ ($+500\,\text{A}$).
  * Output connected to an asynchronous SR flip-flop / latch (`FAULT_LATCH_N`) that cuts power to the contactor gate drivers within $1.5\,\mu\text{s}$, completely bypassing MCU firmware latency.

---

## 4. JLCPCB SMT Bill of Materials (BOM)

| Function | RefDes | Value / MPN | Footprint | LCSC Part # | JLCPCB Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Current Shunt** | `R_SHUNT`| $100\,\mu\Omega\;5\text{W}\;5930$ | `Shunt_SMD:R_5930_15076Metric` | `C2837390` | Standard |
| **Sense Amplifier**| `U_ISENSE`| **INA240A2QDRQ1** (Gain 50) | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`| `C2837395` | Standard |
| **Precision Ref** | `U_REF` | **LM4040B25-Q1 / 1.65V** | `Package_TO_SOT_SMD:SOT-23` | `C2837400` | Standard |
| **Fast Comparator**| `U_OCP` | **TLV3201-Q1** ($40\,\text{ns}$) | `Package_TO_SOT_SMD:SOT-23-5` | `C2837405` | Standard |
| **Kelvin Filter R**| `R_K1, R_K2`| $10.0\,\Omega\;1\%\;0603$ | `Resistor_SMD:R_0603_1608Metric` | `C22859` | **Basic Part** |
| **Kelvin Filter C**| `C_K1, C_K2`| $100\,\text{nF}\;50\,\text{V}\;\text{X7R}$ | `Capacitor_SMD:C_0603_1608Metric` | `C14663` | **Basic Part** |
| **Bypass Cap** | `C_AMP` | $1\,\mu\text{F}\;16\,\text{V}\;\text{X7R}\;0603$ | `Capacitor_SMD:C_0603_1608Metric` | `C15849` | **Basic Part** |
