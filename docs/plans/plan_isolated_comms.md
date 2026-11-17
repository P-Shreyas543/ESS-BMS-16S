# Stage 6 Engineering Plan: Isolated Communications (CAN-FD & RS-485)
## Automotive-Grade, 2.5kV Galvanically Isolated Industrial Inverter & EMS Ports

---

## 1. Subsystem Overview & Core Requirements

* **Primary Function:** Reliable, noise-immune communication with external Energy Management Systems (EMS), hybrid solar inverters, and battery aggregation gateways.
* **Ports Configured:**
  1. **Isolated Port A: CAN-FD Bus (5 Mbps)** — Direct connection to automotive/industrial EMS master controller.
  2. **Isolated Port B: RS-485 Modbus RTU (115.2 kbps)** — Universal protocol integration with popular ESS inverters (Deye, Growatt, Victron, GoodWe, Solis protocols).
* **Isolation Barrier:** $\ge 2.5\,\text{kV}_{\text{rms}}$ galvanic isolation across signal lines (digital isolators) and power lines (isolated DC-DC converter). Eliminates ground loops between battery packs and grid-tied inverters.

---

## 2. Port Architecture & Circuit Topology

### 2.1 Isolated CAN-FD Port (5 Mbps)
* **Transceiver IC:** **Texas Instruments TCAN1042V-Q1** (AEC-Q100, up to $5\,\text{Mbps}$ CAN-FD, bus fault protection $\pm 70\,\text{V}$).
* **Digital Isolator:** **Texas Instruments ISO7721-Q1** (High-speed dual-channel isolator, $100\,\text{Mbps}$, $5000\,\text{V}_{\text{rms}}$).
* **Common-Mode Choke:** $51\,\mu\text{H} - 100\,\mu\text{H}$ automotive CAN choke (TDK ACT45B-510-2P) to suppress common-mode EMI radiated onto the wiring harness.
* **Bus Protection:** **Nexperia PESD2CAN** / **OnSemi NUP2105L** (Dual bidirectional TVS diode, $350\,\text{W}$ surge, low capacitance $<30\,\text{pF}$).
* **Split Termination:** Dual $60.4\,\Omega\;1\%\;0603$ resistors with a central $4.7\,\text{nF}\;50\,\text{V}$ capacitor to chassis ground (`GND_ISO`).

### 2.2 Isolated RS-485 Modbus RTU Port
* **Transceiver IC:** **Texas Instruments THVD1429-Q1** (AEC-Q100, $18\,\text{V}$ bus fault protection, IEC ESD protection $\pm 16\,\text{kV}$).
* **Direction Control:** Automatic hardware TX/RX direction steering or MCU GPIO drive via high-speed optocoupler / digital isolator.
* **Fail-Safe Biasing:** $560\,\Omega$ pull-up on line A to $+5\text{V}_{\text{ISO}}$ and $560\,\Omega$ pull-down on line B to `GND_ISO` ensures known idle logic high state even when cables are disconnected.
* **Bus Protection:** **Semtech SM712** (Asymmetrical TVS diode designed specifically for RS-485 lines operating from $-7\,\text{V}$ to $+12\,\text{V}$ common-mode).

---

## 3. JLCPCB SMT Bill of Materials (BOM)

| Function | RefDes | Value / MPN | Footprint | LCSC Part # | JLCPCB Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CAN-FD Transceiver** | `U_CAN` | **TCAN1042V-Q1** | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`| `C2837425` | Standard |
| **RS-485 Transceiver** | `U_485` | **THVD1429-Q1** | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`| `C2837430` | Standard |
| **Dual Isolators** | `U_ISO1, U_ISO2`| **ISO7721-Q1** (High-Speed) | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`| `C2837435` | Standard |
| **CAN Choke** | `L_CAN` | $51\,\mu\text{H}$ Common-Mode | `Inductor_SMD:L_CommonMode_Wuerth_WE-CNSW_1812` | `C114532` | Standard |
| **CAN TVS** | `D_CAN` | **NUP2105L** (24V Dual TVS) | `Package_TO_SOT_SMD:SOT-23` | `C14486` | **Basic Part** |
| **RS-485 TVS** | `D_485` | **SM712** (Asymmetric TVS) | `Package_TO_SOT_SMD:SOT-23` | `C18197` | **Basic Part** |
| **Termination Resistors**| `R_TERM` | $60.4\,\Omega\;1\%\;0603$ (2x) | `Resistor_SMD:R_0603_1608Metric` | `C23145` | **Basic Part** |
| **Comms Connector** | `J_COM` | 6-Pin RJ45 or $3.81\,\text{mm}$ Screw | `Connector_RJ:RJ45_Amphenol_RJHSE5380` | `C2837440` | Standard |
