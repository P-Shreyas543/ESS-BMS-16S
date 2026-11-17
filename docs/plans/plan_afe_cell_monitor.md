# Stage 2 Engineering Plan: Analog Front End (AFE) & Cell Balancing
## Automotive-Grade, Multi-Chemistry (LFP/NMC), 7S–16S Scalable Architecture

---

## 1. Subsystem Overview & Core Requirements

* **Primary Function:** Continuous high-accuracy cell voltage monitoring, multi-point temperature acquisition, hardware secondary protection (OV/UV), and controlled passive cell balancing.
* **Core Silicon:** **Texas Instruments BQ76952-Q1**
  * AEC-Q100 Grade 1 qualified ($-40^\circ\text{C}$ to $+125^\circ\text{C}$).
  * Supports **3S to 16S** series cell configurations with software register masking.
  * Internal 24-bit $\Delta\Sigma$ ADC delivering typical $\pm 1.5\,\text{mV}$ accuracy per cell.
  * Internal secondary hardware comparators for independent autonomous Over-Voltage (OV) and Under-Voltage (UV) protection.
  * High-speed $400\,\text{kHz}$ $I^2\text{C}$ / SPI interface with CRC checksum verification.
  * High-voltage tolerance: $85\,\text{V}$ absolute maximum on $BAT$ pin.

---

## 2. 7S to 16S Scalability & Multi-Chemistry Scheme

### 2.1 Series Cell Count Configuration (7S to 16S)
The BQ76952-Q1 features an internal `Active Cells` bitmask register:
* **16S Pack (Default):** Bits 0–15 set (`0xFFFF`). All 16 channels converted and monitored.
* **8S Pack (24V Nominal):** Bits 0–7 set (`0x00FF`). Channels $VC1$ through $VC8$ active.
* **7S Pack (Lowest Configuration):** Bits 0–6 set (`0x007F`). Channels $VC1$ through $VC7$ active.
* **Wiring Rule for Unused Pins:**
  * In accordance with TI Application Report SLUA991, when using $<16$ cells, the top battery potential ($Pack+$) is connected to the highest active cell pin ($VC_N$) and tied through adjacent pins up to $VC16$ and $BAT$.
  * This guarantees proper internal bias network operation without false open-wire detection.

### 2.2 Chemistry Voltage Threshold Profiles

| Parameter | LiFePO4 (LFP) Profile | NMC / Li-Ion Profile |
| :--- | :--- | :--- |
| **Over-Voltage (OV) Trip** | $3.650\,\text{V}$ (Delay: $1.0\,\text{s}$) | $4.220\,\text{V}$ (Delay: $1.0\,\text{s}$) |
| **Over-Voltage Recovery** | $3.550\,\text{V}$ | $4.100\,\text{V}$ |
| **Under-Voltage (UV) Trip** | $2.500\,\text{V}$ (Delay: $2.0\,\text{s}$) | $2.850\,\text{V}$ (Delay: $2.0\,\text{s}$) |
| **Under-Voltage Recovery** | $2.800\,\text{V}$ | $3.100\,\text{V}$ |
| **Balance Start Threshold** | $3.400\,\text{V}$ (Top of charge) | $4.000\,\text{V}$ |
| **Balance Delta ($\Delta V$)** | $>15\,\text{mV}$ difference from lowest | $>15\,\text{mV}$ difference from lowest |

---

## 3. Circuit Schematics & Topology Breakdown

### 3.1 Input Low-Pass RC Sense Filters (16 Channels)
To eliminate high-frequency inverter switching ripple ($10\,\text{kHz} - 100\,\text{kHz}$ PWM) from falsifying cell voltage readings:
* **Series Filter Resistors (`R_VC0` .. `R_VC16`):** $1.00\,\text{k}\Omega\;1\%\;0603$ (AEC-Q200).
* **Differential Capacitors (`C_DIFF1` .. `C_DIFF16`):** $100\,\text{nF}\;50\,\text{V}\;\text{X7R}\;0603$ placed directly between adjacent cell sense inputs ($VC_N$ and $VC_{N-1}$).
* **Common-Mode Capacitors (`C_CM1` .. `C_CM16`):** $10\,\text{nF}\;100\,\text{V}\;\text{X7R}\;0603$ connected from each cell sense line to battery ground (`GND_PWR`).
* **Cutoff Frequency:**
  $$f_c = \frac{1}{2\pi \times (2 \times 1\,\text{k}\Omega) \times 100\,\text{nF}} \approx \mathbf{795\,\text{Hz}}$$
  Provides $>40\,\text{dB}$ attenuation at inverter PWM frequencies.

### 3.2 High-Efficiency Passive Balancing Circuit
* **Balance Current Target:** $100\,\text{mA} - 120\,\text{mA}$ per cell.
* **Architecture:** External N-channel MOSFET switches controlled by the BQ76952 `CB1`..`CB16` balance drive pins.
  * Internal AFE FETs can dissipate excessive heat inside the IC package. Using external SOT-23 MOSFETs shifts thermal dissipation entirely to dedicated 2512 power resistors on the board surface!
* **Balancing Resistor Sizing:**
  * For LFP ($3.45\,\text{V}$ balance point):
    $$R_{\text{BAL}} = \frac{3.45\,\text{V}}{100\,\text{mA}} = 34.5\,\Omega \implies \mathbf{33\,\Omega}\quad (\text{yields } 104\,\text{mA})$$
  * Power Dissipation per Resistor:
    $$P = I^2 R = (0.104\,\text{A})^2 \times 33\,\Omega = \mathbf{0.36\,\text{W}}$$
  * Resistor Package: **2512 SMD** rated for $1.0\,\text{W}$ continuous (operating at $<40\%$ of rated power for high reliability and cool surface temperatures).
* **Balance Switching MOSFET:** **AO3400A / DMN3051L-7** (AEC-Q101, $30\,\text{V}$, $R_{\text{DS(on)}} < 30\,\text{m}\Omega$ in compact SOT-23).

### 3.3 Multi-Point Temperature Monitoring
* **Channels:**
  * `TS1`–`TS4`: 4x external NTC thermistors ($10\,\text{k}\Omega, \beta = 3435\,\text{K}$ or $3950\,\text{K}$) distributed across battery cell terminals and busbars.
  * `TS_PCB`: 1x on-board NTC placed adjacent to the balancing resistor bank to automatically throttle or pause balancing if PCB temperatures exceed $+75^\circ\text{C}$.

### 3.4 Galvanic Isolation Interface
* The BQ76952 operates at battery stack potential ($0\text{V} - 72\text{V}$).
* Digital communication ($I^2\text{C}$ / SPI) to the low-voltage safety MCU is routed through a reinforced **TI ISO7741-Q1** quad digital isolator ($5000\,\text{V}_{\text{rms}}$ isolation rating, AEC-Q100).

---

## 4. JLCPCB SMT Bill of Materials (BOM)

| Function | RefDes | Value / MPN | Footprint | LCSC Part # | JLCPCB Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AFE Controller** | `U_AFE` | **BQ76952-Q1** (16S Monitor) | `TQFP-48_7x7mm_P0.5mm` | `C2837375` | Standard |
| **Sense Resistors**| `R_VC0..16`| $1.00\,\text{k}\Omega\;1\%\;0603$ (17x) | `R_0603_1608Metric` | `C21190` | **Basic Part** |
| **Diff Caps** | `C_DF1..16`| $100\,\text{nF}\;50\,\text{V}\;\text{X7R}\;0603$ (16x)| `C_0603_1608Metric` | `C14663` | **Basic Part** |
| **Balance Resistors**| `R_BL1..16`| $33\,\Omega\;1\,\text{W}\;2512$ (16x) | `R_2512_6332Metric` | `C17869` | Standard |
| **Balance MOSFETs**| `Q_BL1..16`| **AO3400A** 30V 5A N-Ch (16x) | `SOT-23` | `C20917` | **Basic Part** |
| **Thermistor NTC**| `NTC1..5` | $10\,\text{k}\Omega\;\beta=3950\text{K}\;0603$ | `R_0603_1608Metric` | `C1984` | **Basic Part** |
| **Digital Isolator**| `U_ISO` | **ISO7741-Q1** Quad Isolator | `SOIC-16-W` | `C2837380` | Standard |
| **Cell Connector** | `J_CELL` | 17-Pin JST-XH / Wire-to-Board | `PinHeader_1x17_P2.50mm` | `C2932840` | Standard |
