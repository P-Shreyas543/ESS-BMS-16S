# Project Specification & Engineering Runbook
## Low-Cost, Market-Ready, Automotive-Grade Battery Management System (BMS) for Energy Storage Systems (ESS)

---

## 1. Project Overview & Objectives

* **Project Title:** Automotive-Grade Low-Cost ESS Battery Management System (BMS)
* **Application Domain:** Stationary Energy Storage Systems (Residential ESS, Commercial & Industrial (C&I) Microgrids, Telecom Backup, and Grid-tied Battery Packs)
* **Target Chemistries:** Lithium Iron Phosphate (LiFePO4 / LFP) — primary for ESS safety and cycle life — with optional NMC/LCO profile compatibility.
* **Core Philosophy:**
  1. **Automotive Grade:** AEC-Q qualified silicon and passives (AEC-Q100, AEC-Q101, AEC-Q200) ensuring high reliability, MTBF, and wide operating temperature range (-40°C to +105°C).
  2. **Low Cost / Market-Ready:** BOM-optimized for cost-competitive manufacturing using widely sourced components, 4-layer standard PCB fabrication, and high-efficiency automated assembly (DFM/DFA).
  3. **Functional Safety & Standards Compliance:** Designed in accordance with ISO 26262 principles (ASIL-B/C metrics), IEC 62619, UL 1973, and UL 9540A stationary storage standards.
  4. **JLCPCB PCB & PCBA Optimized:** Tailored to JLCPCB standard capabilities for automated high-yield fabrication and assembly.

---

## 2. Technical Specifications & Architecture

### 2.1 Voltage & Topology
* **Standard Pack Base Configuration:** 16S LFP (Nominal: 51.2V, Operating Range: 40.0V – 58.4V).
* **High-Voltage Scalability:** Modular architecture supporting multi-pack daisy-chaining up to 400V–800V strings via isolated communications (iso-SPI or isolated CAN).
* **Cell Voltage Measurement Accuracy:** $\pm 1.5\,\text{mV}$ typical across the full operating temperature range.
* **Cell Temperature Channels:** Minimum 4 to 8 NTC thermistor inputs per 16S module.
* **Pack Current Measurement:** Bi-directional isolated shunt-based current sensing (range: $\pm 200\,\text{A}$ continuous, up to $500\,\text{A}$ peak pulse) with high-resolution Coulomb counting.

### 2.2 Functional Blocks
```
+-----------------------------------------------------------------------------------------+
|                               HIGH-VOLTAGE BATTERY DOMAIN                              |
|                                                                                         |
|   +---------------------+        +--------------------------------------------------+   |
|   | 16S LFP Cell Stack  | ------ | Analog Front End (AFE) Multi-Cell Monitor        |   |
|   | (Cell V & NTC Temp) |        | (e.g., TI BQ76952 / BQ79616-Q1, ST L9963E)       |   |
|   +---------------------+        | - 16-channel cell voltage ADC                    |   |
|              |                   | - Hardware OV / UV comparators                   |   |
|              |                   | - On-chip passive cell balancing (100 - 200 mA)  |   |
|   +---------------------+        +--------------------------------------------------+   |
|   | Current Shunt       |                                 |                             |
|   | (Manganin 100uOhm)  |                                 | Isolated SPI / I2C / UART   |
+-----------------------------------------------------------|-----------------------------+
                                                            | Galvanic Isolation Barrier
                                                            | (Reinforced 2.5kV - 5kVrms)
+-----------------------------------------------------------|-----------------------------+
|                               LOW-VOLTAGE CONTROL DOMAIN  v                             |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   | Safety Microcontroller (MCU)                                                    |   |
|   | (e.g., Automotive-Grade NXP S32K144 / ST SPC58 / TI TMS570)                     |   |
|   | - Real-time SoC (State of Charge) & SoH (State of Health) Estimation             |   |
|   | - Contactors & Pre-charge Sequencing                                            |   |
|   | - Hardware Safety Watchdog & Fault Logging (FRAM / Flash)                       |   |
|   +---------------------------------------------------------------------------------+   |
|              |                                        |                                 |
|              v                                        v                                 |
|   +---------------------+                  +---------------------+                      |
|   | Communication Ports |                  | Power Actuators     |                      |
|   | - Dual CAN-FD (EMS) |                  | - Main Contactor    |                      |
|   | - Isolated RS-485   |                  | - Pre-charge Relay  |                      |
|   |   (Inverter Modbus) |                  | - High-Side Pyro/FET|                      |
|   +---------------------+                  +---------------------+                      |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Strict Industry Standards Applied

| Standard | Domain | Applied Design Rules |
| :--- | :--- | :--- |
| **IPC-2221B** | Generic PCB Design | Table 6-1 electrical clearance and creepage rules for HV conductors up to 60V–400V. |
| **IPC-7351B** | SMD Land Patterns | Standard courtyard boundaries, pad dimensions, and solder fillets for robust assembly. |
| **IPC-A-610 Class 3** | High-Reliability Assembly | Solder joint volume, component placement tolerances, and thermal relief requirements. |
| **IEC 60664-1** | Insulation Coordination | $\ge 6.5\,\text{mm}$ creepage and clearance across the galvanic isolation barrier. |
| **ISO 26262 (ASIL B/C)** | Functional Safety | Dual-point fault mitigation, independent hardware watchdogs, and CRC protected buses. |
| **IEC 62619 / UL 1973** | Industrial / Stationary ESS | Secondary hardware over-voltage protection, redundant thermal shutdown. |
| **UL 9540A** | Thermal Runaway Safety | Multi-point cell temperature monitoring, anti-propagation interlocks. |
| **AEC-Q Qualification** | Component Quality | AEC-Q100 (ICs), AEC-Q101 (Discretes), AEC-Q200 (Passives) for -40°C to +105°C rating. |

---

## 4. JLCPCB PCB & PCBA Fabrication Constraints

### 4.1 4-Layer Standard Stackup (JLC04161H-7628)
* **Total Thickness:** $1.6\,\text{mm} \pm 10\%$
* **Layer 1 (Top / F.Cu):** $1\,\text{oz}$ Finished Copper ($35\,\mu\text{m}$)
* **Dielectric 1 (Core to Top):** Prepreg $7628 \times 1$ ($0.21\,\text{mm}, \varepsilon_r \approx 4.6$)
* **Layer 2 (Inner 1 / In1.Cu):** $1\,\text{oz}$ Finished Copper ($35\,\mu\text{m}$) — Dedicated GND Plane
* **Core:** FR4 Core ($1.065\,\text{mm}, \varepsilon_r \approx 4.6$)
* **Layer 3 (Inner 2 / In2.Cu):** $1\,\text{oz}$ Finished Copper ($35\,\mu\text{m}$) — Power / Signal Plane
* **Dielectric 2 (Core to Bottom):** Prepreg $7628 \times 1$ ($0.21\,\text{mm}, \varepsilon_r \approx 4.6$)
* **Layer 4 (Bottom / B.Cu):** $1\,\text{oz}$ Finished Copper ($35\,\mu\text{m}$)

### 4.2 DRC Constraints Configured in Project
* **Min Trace Width:** $0.127\,\text{mm}$ ($5\,\text{mil}$) [JLCPCB 4-layer absolute limit: $0.09\,\text{mm}$]
* **Min Trace Spacing (Clearance):** $0.127\,\text{mm}$ ($5\,\text{mil}$)
* **Min Via Diameter / Drill:** $0.45\,\text{mm} / 0.20\,\text{mm}$ (or standard $0.50\,\text{mm} / 0.30\,\text{mm}$)
* **Min Annular Ring:** $\ge 0.125\,\text{mm}$ ($5\,\text{mil}$)
* **Hole-to-Hole Distance:** $\ge 0.50\,\text{mm}$ ($20\,\text{mil}$)
* **Copper to Board Edge:** $\ge 0.30\,\text{mm}$ ($12\,\text{mil}$)
* **Solder Mask Expansion:** $0.05\,\text{mm}$ ($2\,\text{mil}$)
* **Solder Mask Bridge (Dam):** $\ge 0.10\,\text{mm}$ ($4\,\text{mil}$)
* **Silkscreen Min Text Height:** $1.0\,\text{mm}$ ($40\,\text{mil}$), line width $\ge 0.15\,\text{mm}$ ($6\,\text{mil}$)

### 4.3 Netclasses Configured in Project

| Netclass | Track Width | Clearance | Via Dia / Drill | Application |
| :--- | :--- | :--- | :--- | :--- |
| **`Default`** | $0.20\,\text{mm}$ | $0.15\,\text{mm}$ | $0.50 / 0.30\,\text{mm}$ | Standard digital logic, GPIOs, ADC signals |
| **`Power_HV`** | $1.00\,\text{mm}$ | $0.80\,\text{mm}$ | $0.80 / 0.40\,\text{mm}$ | High-voltage battery pack lines, contactor feeds |
| **`Power_LV`** | $0.50\,\text{mm}$ | $0.25\,\text{mm}$ | $0.60 / 0.35\,\text{mm}$ | 12V, 5V, 3.3V system power rails |
| **`Balance_Lines`**| $0.40\,\text{mm}$ | $0.30\,\text{mm}$ | $0.60 / 0.35\,\text{mm}$ | Cell balance current lines ($100 - 200\,\text{mA}$) |
| **`CAN_Bus`** | $0.254\,\text{mm}$ | $0.25\,\text{mm}$ | $0.50 / 0.30\,\text{mm}$ | CAN-FD diff pair ($100\,\Omega$ diff impedance) |
| **`Current_Sense`**| $0.254\,\text{mm}$ | $0.25\,\text{mm}$ | $0.50 / 0.30\,\text{mm}$ | Kelvin 4-wire sense connections to shunt resistor |

### 4.4 PCBA Assembly Provisions
* **Optical Fiducials:** 3 fiducials ($1.0\,\text{mm}$ round copper pad with $2.0\,\text{mm}$ mask opening, no silk) placed near board corners.
* **Tooling Holes:** 4 non-plated holes ($3.2\,\text{mm}$ M3) at $(5\,\text{mm}, 5\,\text{mm})$ offsets from edges.
* **Component Sourcing:** Select parts available in JLCPCB Basic / Extended Parts Library (LCSC Part Numbers populated in schematic fields).

---

## 5. Project Portability & Directory Architecture

To guarantee 100% portability across different computers, OS environments, and team members without missing paths:

```
Automotive-Grade-ESS-BMS/
 ├── Automotive_ESS_BMS.kicad_pro       # Master project file
 ├── Automotive_ESS_BMS.kicad_sch       # Root hierarchical schematic
 ├── Automotive_ESS_BMS.kicad_pcb       # 4-layer PCB layout (160x100mm)
 ├── sym-lib-table                      # Project symbol library table (uses ${KIPRJMOD})
 ├── fp-lib-table                       # Project footprint library table (uses ${KIPRJMOD})
 ├── symbols/                           # Project-local schematic symbols
 │    └── Automotive_ESS_BMS.kicad_sym  # Project symbol database
 ├── footprints.pretty/                 # Project-local footprints folder (*.kicad_mod)
 ├── 3d_models/                         # Project-local 3D CAD models (*.step, *.wrl)
 ├── 01_Power_Supply.kicad_sch          # Sub-sheet: Power supply
 ├── 02_AFE_Cell_Monitor.kicad_sch      # Sub-sheet: AFE & Cell Monitor
 ├── 03_MCU_Control.kicad_sch           # Sub-sheet: Safety MCU & Logic
 ├── 04_Current_Sensing.kicad_sch       # Sub-sheet: Isolated Current Shunt
 ├── 05_Power_Actuators.kicad_sch       # Sub-sheet: Contactor & Relay drivers
 ├── 06_Communications.kicad_sch        # Sub-sheet: Isolated CAN-FD & RS-485
 ├── .gitignore                         # Version control exclusions
 └── instruction.md                     # Engineering runbook (this document)
```

* **Symbol URI:** `${KIPRJMOD}/symbols/Automotive_ESS_BMS.kicad_sym`
* **Footprint URI:** `${KIPRJMOD}/footprints.pretty`
* **3D Model Path in Footprints:** `${KIPRJMOD}/3d_models/<part_name>.step`

---

## 6. Development Milestones

| Milestone | Deliverables | Status |
| :--- | :--- | :--- |
| **M1: Architecture & Portable Setup** | Project init, hierarchical subsheets, JLCPCB rules, local lib tables | **Completed** |
| **M2: Subsystem 01 — Power Supply** | Wide-input buck (16V–72V to 5V/3.3V), reverse polarity, TVS surge, LCSC IDs | **Completed** |
| **M3: Subsystem 02 — AFE & Balancing**| BQ76952-Q1 integration, 7S–16S input RC filters, balance switches | **In Progress** |
| **M4: Subsystem 03 — Safety MCU** | Automotive MCU (NXP S32K144/ST), crystal oscillator, debug & reset | Pending |
| **M5: Subsystem 04 — Current Sensing** | Kelvin shunt amplifier, isolated $\Delta\Sigma$ modulator, over-current trip | Pending |
| **M6: Subsystem 05 — Power Actuators** | Low-side smart drivers, pre-charge relay, contactor economizer PWM | Pending |
| **M7: Subsystem 06 — Communications** | Isolated CAN-FD transceiver and isolated RS-485 Modbus interface | Pending |
| **M8: PCB Layout & Thermal Plan** | 4-layer routing, thermal relief, isolation gap check, DRC verification | Pending |
| **M9: JLCPCB Production Package** | Gerber RS-274X, Excellon drill, CPL (Pick & Place), BOM with LCSC IDs | Pending |
