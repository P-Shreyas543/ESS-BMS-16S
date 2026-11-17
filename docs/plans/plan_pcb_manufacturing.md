# Stage 7 Engineering Plan: 4-Layer PCB Stackup, Thermal Design & JLCPCB PCBA
## High-Reliability, Industrial Energy Storage DFM/DFA Manufacturing Guide

---

## 1. 4-Layer PCB Stackup Definition (JLC04161H-7628)

* **Overall Board Dimensions:** $160.0 \times 100.0\,\text{mm}$ (Eurocard Standard).
* **Nominal Finished Thickness:** $1.6\,\text{mm} \pm 10\%$.
* **Solder Mask Color:** Matte Green (or Matte Black) with White Silkscreen.
* **Surface Finish:** **ENIG (Electroless Nickel Immersion Gold)** — strictly required for high-reliability contactor signals and flat SMD pads on $0.5\,\text{mm}$ pitch QFP/QFN ICs.

```
====================================================================================================
LAYER NAME      MATERIAL               THICKNESS     COPPER WEIGHT     FUNCTION / ROUTING
====================================================================================================
Top Copper      Cu Foil                0.035 mm      1.0 oz            Signal routing & SMD pads
Prepreg         7628 x 1 (Dielectric)  0.210 mm      -- (Er ≈ 4.6)     Dielectric barrier
Inner Layer 1   Inner Copper Foil      0.035 mm      1.0 oz            Solid continuous GND plane
Core            FR4 Core (Dielectric)  1.065 mm      -- (Er ≈ 4.6)     Mechanical structural core
Inner Layer 2   Inner Copper Foil      0.035 mm      1.0 oz            Power planes (+12V, +5V, +3V3)
Prepreg         7628 x 1 (Dielectric)  0.210 mm      -- (Er ≈ 4.6)     Dielectric barrier
Bottom Copper   Cu Foil                0.035 mm      1.0 oz            Balance resistors & Sec GND
====================================================================================================
TOTAL FINISHED BOARD THICKNESS: 1.625 mm (~1.6 mm)
```

---

## 2. High-Voltage Clearance, Creepage & Isolation Slot

* **IEC 60664-1 & IPC-2221B Table 6-1 Compliance:**
  * For $60\,\text{V} - 400\,\text{V}$ rated peak working voltage:
    * Minimum electrical clearance across external conductors: $\ge 4.0\,\text{mm}$.
    * Minimum creepage distance across surface with Pollution Degree 2: $\ge 6.5\,\text{mm}$.
* **Physical Isolation Trench (Milled Air Gap):**
  * A $1.5\,\text{mm}$ wide physical slot routed on the `Edge.Cuts` layer underneath all digital isolator ICs (`ISO7741-Q1`, `ISO7721-Q1`, and `B0505S-1WR3`).
  * Air dielectric withstand is $>3000\,\text{V}/\text{mm}$, ensuring complete immunity to surface moisture or carbon contamination.

---

## 3. Thermal Management & Heat Dissipation Strategy

1. **High-Voltage Buck (`U1` LM5164-Q1):**
   * Exposed thermal pad (Pin 9) soldered with an array of $3 \times 3 = 9$ thermal vias ($0.3\,\text{mm}$ drill, $0.6\,\text{mm}$ pad) connected directly into the continuous ground plane on Inner Layer 1.
2. **Passive Balancing Resistor Bank (`R_BL1` through `R_BL16`):**
   * Placed on Bottom Layer (`B.Cu`) with large copper polygon pours and thermal vias to the top surface.
   * Resistors spaced by at least $3.0\,\text{mm}$ center-to-center to avoid thermal mutual coupling.
3. **Current Sense Shunt (`R_SHUNT` $5930$):**
   * Massive $2\,\text{oz}$ equivalent top/bottom copper pours with $12\times$ through-hole stitching vias on each side to sink the continuous $4.0\,\text{W}$ heat load at $200\,\text{A}$.

---

## 4. JLCPCB Automated PCBA Deliverables Package

When exporting from KiCad 10 for automated JLCPCB SMT production, the complete fabrication package is generated and verified with **0 ERC errors/warnings** and **0 physical DRC errors**:

1. **Gerber & Drill Archive (`fabrication/Automotive_ESS_BMS_Gerbers.zip` - 370 KB):**
   * Standard RS-274X format across 4 copper layers (`F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`), solder masks, solder pastes, silkscreens, and edge outline.
   * Excellon PTH/NPTH drill files (`Automotive_ESS_BMS.drl`) and drill map PDF.
2. **Bill of Materials (`fabrication/assembly/BOM.csv` and `JLCPCB_BOM_Automotive_ESS_BMS.csv`):**
   * 94 grouped rows covering all 221 schematic components.
   * Columns: `Comment`, `Designator`, `Footprint`, `LCSC Part #`.
   * 100% pre-populated with active LCSC catalog codes matching JLCPCB basic & preferred SMT stock.
3. **Centroid / Pick-and-Place File (`fabrication/assembly/CPL.csv`):**
   * 228 rows covering all components and mounting hardware.
   * Columns: `Ref`, `Val`, `Package`, `PosX`, `PosY`, `Rot`, `Side`.
   * Standardized component orientation for JLCPCB tape-and-reel feeders.
4. **Schematics & PCB Documentation:**
   * Multi-page high-resolution schematic drawing: `fabrication/Automotive_ESS_BMS_Schematics.pdf`
   * 4-layer PCB engineering layout drawing: `fabrication/Automotive_ESS_BMS_PCB_Layout.pdf`

---

## 5. Automotive Protection & Transient Clamping Verification

All external ports, inductive gates, and low-level sensing lines meet **ISO 7637-2 / ISO 16750-2**, **ISO 10605** ($\pm 30\text{kV}$ ESD), and **AEC-Q101**:
* **CAN-FD Bus (`J_CAN1`):** `D_TVS_CAN1` (`NUP2105LT1G` SOT-23, LCSC `C12948`)
* **RS-485 Modbus (`J_485_1`):** `D_TVS_485_1` (`SM712` SOT-23, LCSC `C19002`)
* **Contactor Gate Clamps (`Q_POS1`, `Q_NEG1`, `Q_PRE1`):** `D_Z_POS1`, `D_Z_NEG1`, `D_Z_PRE1` (`BZX84-C18` SOD-323, LCSC `C22809`)
* **Current Sense Shunt (`U_ISENSE1`):** `D_TVS_SHUNT1` (`SMAJ5.0CA` SMA, LCSC `C8063`)
* **External NTC Thermistors (`J_NTC1..4`):** `D_ESD_NTC1..4` (`ESD5V0D3B` SOD-323, LCSC `C84296`)
* **Battery Input (`J1`):** `D1` (`SMCJ75A` 1500W SMC, LCSC `C14480`) + `D2` (`SS310` 100V 3A SMB, LCSC `C2494`)
* **Physical Layout Validation:** Courtyard overlap check verifies **0 boundary violations** and **0 courtyard overlaps** across all TVS and ESD components.

