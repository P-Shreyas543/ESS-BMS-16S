> Detailed section; where it conflicts with ../ARCHITECTURE.md, ARCHITECTURE.md wins.

# Architecture part C: AFE integration (U_AFE1, BQ76952, 16S LFP)

Date 2026-11-17. Architecture only. No project file or KiCad file was changed.

Scope: the complete BQ76952 integration on sheet 02. This covers:
* every one of the 48 pins
* the cell input network and the cell-tap connector
* external balancing (TI NPN option) and the active-balancer header
* temperature sensing
* fault outputs and host control
* the FUSE pin
* production: OTP golden image, calibration, security, and the LFP data-memory image

Binding inputs (PROJECT.md decisions log, 2026-11-17):
* on-board back-to-back high-side N-FET banks driven by CHG / DSG, with PCHG / PDSG
* 200 A continuous, LFP only
* STM32G473RCT6
* improved balancing: TI NPN external balancing, an active-balancer header, and charge-based firmware
* an MCU-independent safety trip

## 0. Sources and conventions

| Tag | Document | Revision |
|---|---|---|
| DS | BQ76952 data sheet SLUSE13 | B, Nov 2021 |
| TRM | BQ76952 Technical Reference Manual SLUUBY2 | B, May 2022 |
| AN81 | Cell Balancing With BQ769x2 Battery Monitors, SLUAA81 | A, Feb 2022 |
| AN32 | BQ769x2 Calibration and OTP Programming Guide, SLUAA32 | A, Sep 2021 |
| AN11 | BQ769x2 Software Development Guide, SLUAA11 | B |
| AN84 | Using Low-Side FETs with the BQ769x2, SLUAA84 | A |
| AN09 | Multiple FETs with the BQ769x2, SLUAA09 | A |
| FAQ | BQ769x2 Frequently Asked Questions, SLUAAQ5 | May 2024 |
| SS8050-DS | JSCJ SS8050 SOT-23 data sheet, Rev 2.1 (downloaded live from the LCSC C2150 product page) | – |

* Page numbers are PDF pages of the TI documents. They equal the printed page numbers.
* **calc** marks my arithmetic. **est.** marks an engineering estimate. **unverified** means not confirmed in any document or live source this session.
* **LCSC data source.** Every LCSC number in this file was queried live on 2026-11-17 from two places:
  * the LCSC product-detail API behind `lcsc.com/product-detail` (`wmsc.lcsc.com/ftps/wm/product/detail`), for part identity and LCSC stock
  * the JLCPCB parts API (`jlcpcb.com` SMT component list), for Basic / Extended status and JLC stock
  * In the parts table, "L+J" means both were checked; "J" means the JLC API only.
  * The `jlcsearch.tscircuit.com` mirror was also tried. It returns identity and Basic flags but **no stock** (stock = null for every part), so it was not used for stock.

---

## 1. Key decisions (summary)

| # | Decision | Evidence |
|---|---|---|
| D-C1 | **Host link = I2C Fast + CRC (Comm Type 0x12), 400 kHz. The research choice is confirmed; SPI is rejected** (§2.3) | TRM p.138–139; FAQ p.11; DS p.47–48 |
| D-C2 | **Order the base BQ76952PFBR (LCSC C2862742, 11 814 in stock)**, not BQ7695202PFBR (C3038665, only 83 in stock). The EOL OTP image sets CRC, REG1 and everything else anyway. Owner question Q1 | live LCSC / JLC; DS p.4 |
| D-C3 | **Fault outputs:** DDSG / DCHG are push-pull, REG1-driven, active-low "fault" outputs: `AFE_FLT_DSG_N` / `AFE_FLT_CHG_N`. A 100 k pull-down on each makes Hi-Z (SHUTDOWN, blank part) read as "fault" | TRM p.60–61, p.153 |
| D-C4 | **DFETOFF = BOTHOFF, active-low**, as a wired-AND node: pull-up to REG1, an MCU-driven NFET, and the latched `OC_TRIP_N` through a Schottky diode | TRM p.59, p.143; DS p.48 |
| D-C5 | **Temperature map:** <br>• TS1 / TS3 / HDQ = pack NTC 1–3 (cell protections) <br>• CFETOFF = **FET-bank NTC** (OTF, MCU-independent) <br>• die sensor = AFE / board <br>• MCU ADC = pack NTC 4 (+ optional 5–6), shunt, balancer bank, ambient <br>• Total 9 sensors (11 with options) | TRM p.141, p.146; DS p.38, p.65 |
| D-C6 | **TS2 = wake input** (SHUTDOWN ship mode). No NTC on TS2 | DS p.9, p.75; TRM p.136 |
| D-C7 | **Cell inputs:** <br>• R_VC = 100 Ω (VC0–VC15), **20 Ω on VC16** <br>• **C_DF = 220 nF** differential <br>• **no common-mode capacitors** <br>• VC0 tied to VSS on the PCB | DS p.9, p.70–71, p.75; AN81 p.3, p.8; FAQ p.17 |
| D-C8 | **Balancing:** <br>• TI NPN option (AN81 Fig 2-5): SS8050 + 33 Ω 1 W + 220 Ω base resistor + 1N4148WS clamp <br>• about 100–108 mA external plus 16–21 mA internal per cell <br>• odd / even groups, at most 8 cells at once | AN81 p.7; SS8050-DS p.1; calc §4 |
| D-C9 | **REG0 pre-regulator:** <br>• FCX495TA NPN (the TI EVM part) <br>• 3.3 kΩ collector resistor plus a separate collector diode <br>• 22 nF on REGIN, 10 MΩ on BREG <br>• REG1 = 3.3 V "AFE safety island", budget ≤ 5 mA | DS p.13, p.46, p.64, p.67, p.69; FAQ p.18 |
| D-C10 | **CP1 = 2.2 µF** (FET-bank build). **LD and PACK each through 10 kΩ to PACK+** | DS p.20, p.46, p.65 |
| D-C11 | **FUSE: DNP footprint** for a chemical-fuse heater or a breaker shunt-trip, driven by a 100 V NFET | DS p.12, p.49; TRM p.61, p.135, p.156–157 |
| D-C12 | **Production:** <br>• golden image in OTP (2 writes: configuration, then calibration) at 11.5 V on BAT / VC16 with no cells, ≤ 45 °C <br>• customer keys, SEAL in OTP <br>• runtime PF-to-OTP is allowed at full pack voltage | DS p.9; TRM p.14–15, p.157, p.197; AN32 p.14; FAQ p.12 |

---

## 2. U_AFE1 pin-by-pin (TQFP-48, PFB)

### 2.1 Notes for the table

* **Pin order and functions:** DS p.4–6, Table 6-1.
* **"Today":** the current sheet 02 (netlist via `docs/research/01_bq76952_features.md` §5) and the part fields read from `02_AFE_Cell_Monitor.kicad_sch`.
* **Power path:** the high-side back-to-back FET banks, the PCHG / PDSG P-FETs and their resistors belong to the power-stage part of the architecture. This table names only the AFE-side net and what the AFE needs from that part.
* **Topology assumed** (DS p.66 Fig 16-1, p.72): stack+ → CHG bank (source at BAT+ side) → DSG bank (source at PACK+) → PACK+.

### 2.2 Pin table

| Pin | Function | Net (target) | External parts on sheet 02 | Change from today |
|---|---|---|---|---|
| 1 | VC15: cell 15 sense / balance (DS p.4) | `VC15` | R_VC15 100 Ω from `CELL_15`; C_DF15 220 nF VC15–VC14; Q_BL16 base network (R_BB16, D_BB16) | C_DF 100 nF → 220 nF; add R_BB / D_BB; FET → NPN |
| 2 | VC14 | `VC14` | R_VC14, C_DF14, R_BB15 / D_BB15 | as pin 1 |
| 3 | VC13 | `VC13` | R_VC13, C_DF13, R_BB14 / D_BB14 | as pin 1 |
| 4 | VC12 | `VC12` | R_VC12, C_DF12, R_BB13 / D_BB13 | as pin 1 |
| 5 | VC11 | `VC11` | R_VC11, C_DF11, R_BB12 / D_BB12 | as pin 1 |
| 6 | VC10 | `VC10` | R_VC10, C_DF10, R_BB11 / D_BB11 | as pin 1 |
| 7 | VC9 | `VC9` | R_VC9, C_DF9, R_BB10 / D_BB10 | as pin 1 |
| 8 | VC8 | `VC8` | R_VC8, C_DF8, R_BB9 / D_BB9 | as pin 1 |
| 9 | VC7 | `VC7` | R_VC7, C_DF7, R_BB8 / D_BB8 | as pin 1 |
| 10 | VC6 | `VC6` | R_VC6, C_DF6, R_BB7 / D_BB7 | as pin 1 |
| 11 | VC5 | `VC5` | R_VC5, C_DF5, R_BB6 / D_BB6 | as pin 1 |
| 12 | VC4 | `VC4` | R_VC4, C_DF4, R_BB5 / D_BB5 | as pin 1 |
| 13 | VC3 | `VC3` | R_VC3, C_DF3, R_BB4 / D_BB4 | as pin 1 |
| 14 | VC2 | `VC2` | R_VC2, C_DF2, R_BB3 / D_BB3 | as pin 1 |
| 15 | VC1 | `VC1` | R_VC1, C_DF1 (VC1–VC0), R_BB2 / D_BB2 | as pin 1 |
| 16 | VC0: cell 1 negative (DS p.5) | `VC0` | R_VC0 100 Ω from `CELL_0`. **`CELL_0` is tied to VSS (`BAT-` Kelvin star) on the PCB** (DS p.70, p.75). Q_BL1 base network (R_BB1, D_BB1) | add the on-board CELL_0–VSS tie (review A10). VC0 may rise to ≈ 1.7 V during cell-1 balancing; allowed up to 6 V abs max (DS p.8, p.10 note 5) |
| 17 | VSS | `GND_PWR` = `BAT-` star at the shunt cell-side Kelvin | REG18 / REGIN / filter returns, short to the star | layout only |
| 18 | SRP (top of shunt; charge = positive, DS p.5) | `SRP_F` (filtered) | R_SRP1 100 Ω from `SHUNT_K_BAT`; C_SR1 100 nF SRP–SRN; C_SR2 100 pF SRP–SRN; C_SR3 100 nF SRP–VSS **DNP** (DS p.65, p.76) | today `SH_P` direct, no filter. Own Kelvin pair, separate from the INA240 network |
| 19 | NC | `GND_PWR` | – | tie to VSS (allowed, DS p.75) |
| 20 | SRN | `SRN_F` | R_SRN1 100 Ω from `SHUNT_K_PACK`; C_SR4 100 nF SRN–VSS **DNP** | as pin 18 |
| 21 | TS1: thermistor (DS p.5) | `NTC_TS1` | J_NTC1 pins 1–2; R_TS1 100 Ω series; C_TS1 **1 nF** at the pin; D_ESD1 at the connector | cap: the value field says 10 nF, but the fitted C1588 is really **1 nF**. Keep 1 nF, fix the field. ESD part replaced (§7) |
| 22 | TS2: wake from SHUTDOWN (DS p.5, p.9) | `AFE_TS2_WAKE` | D_WAKE1 BAV170 (common cathode) anode 1; cathode = `WAKE_BTN_RAW` | today NTC_TS2 on this pin, which blocks SHUTDOWN (TRM p.136). NTC moves to HDQ |
| 23 | TS3 | `NTC_TS3` | J_NTC1 pins 3–4; R_TS3, C_TS3 1 nF, D_ESD3 | cap / field / ESD as pin 21 |
| 24 | REG18 (internal 1.8 V, DS p.6) | `AFE_REG18` | C_R18 2.2 µF at the pin (1.8–22 µF, DS p.12) | none (keep C23630) |
| 25 | ALERT | `AFE_ALERT` | R_ALRT1 10 kΩ to `+3V3`. Pin configured open-drain active-low | **add the pull-up** (review A8). MCU pin from the MCU part |
| 26 | SCL | `AFE_SCL` | R_SCL1 4.7 kΩ to `+3V3` (FAQ p.11: 4.7–10 k); R_SCLS1 100 Ω series at the pin (DS p.76) | fix the pull-up LCSC (C22822 is 17.8 Ω); add series R. The MCU pin must be a real I2C SCL (MCU part) |
| 27 | SDA | `AFE_SDA` | R_SDA1 4.7 kΩ to `+3V3`; R_SDAS1 100 Ω series | as pin 26; one MCU pin only (today PB7 + PB9) |
| 28 | HDQ → thermistor | `NTC_TS2` (pack NTC 2) | J_NTC1 pins 5–6; R_TS2 100 Ω, C_TS2 1 nF, D_ESD2 | new (today open) |
| 29 | CFETOFF → **FET-bank thermistor** (OTF) | `NTC_FET` | RT_FET1 NCP18XH103F03RB at the FET bank (power-stage area); C_TS4 1 nF at the pin; R_TS4 100 Ω | new (today open). Config 0x0F, "FET temperature" |
| 30 | DFETOFF → **BOTHOFF**, active-low | `AFE_BOTHOFF_N` (local node); MCU input signal `AFE_DFETOFF` | R_DOFF1 10 kΩ to `AFE_REG1`; Q_DOFF1 2N7002 (drain = node, gate = `AFE_DFETOFF`, R_DOFFG1 100 kΩ gate–VSS); D_DOFF1 BAT54WS (anode = node, cathode = `OC_TRIP_N`) | new (today open) |
| 31 | DCHG → fault output | `AFE_FLT_CHG_N` | R_DCHG1 100 kΩ to VSS (fail = "fault") | today NTC_TS4 (a thermistor) is here; the NTC moves to the MCU ADC |
| 32 | DDSG → fault output | `AFE_FLT_DSG_N` | R_DDSG1 100 kΩ to VSS | today RT_BOARD is here; RT_BOARD's LCSC C19702 is really a 10 µF capacitor. Board temperature moves to die + MCU NTCs |
| 33 | RST_SHUT | `AFE_RST_SHUT` | R_RST1 10 kΩ to VSS (keep). Driven by an MCU push-pull GPIO | none (net renamed from `AFE_RST`) |
| 34 | REG2 | `AFE_REG2` | C_REG2 1 µF **DNP**; REG2 disabled in the image | float, allowed (DS p.75) |
| 35 | REG1 = 3.3 V "AFE safety island" | `AFE_REG1` | C_R1 2.2 µF (≥ 1 µF, DS p.14). Loads: DDSG / DCHG high level, R_DOFF1, any gate-kill logic; budget ≤ 5 mA (§3.4) | REG1 is dead today (REGIN on VSS); fed from REG0 after the change |
| 36 | REGIN | `AFE_REGIN` | C_REGIN1 22 nF (15–27 nF, > 7 nF after derating, DS p.13); Q_REG0 1 emitter | today on VSS |
| 37 | BREG | `AFE_BREG` | Q_REG0 1 base; R_BREG1 10 MΩ to VSS (DS p.69); no added cap (≤ 150 pF, DS p.13) | today floating (review A5) |
| 38 | FUSE | `AFE_FUSE` | DNP fuse / breaker-trip driver (§7) | today open; add DNP footprint |
| 39 | PDSG | `AFE_PDSG` | to the power-stage pre-discharge P-FET gate (1 MΩ G–S required, DS p.45) | new (today open) |
| 40 | PCHG | `AFE_PCHG` | to the power-stage pre-charge P-FET gate (1 MΩ G–S) | new |
| 41 | LD | `AFE_LD` | R_LD1 10 kΩ 1206 to `PACK+` (DS p.46) | today on VSS |
| 42 | PACK | `AFE_PACK` | R_PACK1 10 kΩ 1206 to `PACK+` (0–80 V ±0.5 V, DS p.10) | today on VSS |
| 43 | DSG | `AFE_DSG` | to the DSG bank gate network (power-stage part). Any hardware gate-kill must clamp **gate to source (PACK+)**, never to VSS (DS p.72) | new |
| 44 | NC | `GND_PWR` | – | tie to VSS |
| 45 | CHG | `AFE_CHG` | to the CHG bank gate network (power stage); CHG turns off toward BAT (DS p.72) | new |
| 46 | CP1 | `AFE_CP1` | C_CP1 **2.2 µF 50 V X7R 1206**, CP1–BAT (100 nF–2.2 µF, DS p.20) | today 100 nF with a wrong LCSC (C14666 does not exist) |
| 47 | BAT | `AFE_BAT` | D_BAT1 1N4148WS from `BAT_SNS` (J_CELL1 pin 18, a second `CELL_16` contact); R_BAT1 100 Ω; C_BAT1 **1 µF 100 V** to VSS (DS p.64, p.75) | **C_BAT1 today is C28323, which is 50 V on a 58.4 V node: must change.** D_BAT1 LCSC C8677 is an XH housing, not SS110. Separate the BAT diode from the REG0 diode (DS p.64) |
| 48 | VC16: cell 16 sense, top of stack | `VC16` | **R_VC16 20 Ω** from `CELL_16`; C_DF16 220 nF VC16–VC15 | 100 Ω → 20 Ω (AN81 p.8; FAQ p.17) |

### 2.3 I2C + CRC vs SPI: decision

**Decision: keep I2C Fast with CRC, Comm Type 0x12** (TRM p.138–139). This **confirms** the research; SPI is not needed.

| Criterion | I2C + CRC | SPI + CRC | Source |
|---|---|---|---|
| Throughput for a 16-cell read | Block read: 4 + 32 data bytes, each byte with its CRC, ≈ 1.6 ms at 400 kHz (calc) | **No block read or write.** One byte per transaction (24 bits with CRC), so 32 transactions ≈ 2 ms (calc) | FAQ p.11 §4.5; DS p.57 |
| Integrity | CRC-8 (x⁸+x²+x+1) on every byte, NACK on error | Same CRC, plus a retry scheme | FAQ p.11 §4.2 |
| Pins used on the AFE | SCL, SDA | SCL / SDA **plus CFETOFF (CS) and HDQ (MOSI)** | DS p.6 |
| Effect on this design | none | **Loses the FET-bank NTC (CFETOFF) and pack NTC 2 (HDQ).** That would break D-C5, so OTF could no longer be MCU-independent | §5 |
| Electrical | Open-drain, pull-ups to +3V3 | MISO drives **1.8 V** unless REG1 is on and [MISO_REG1] = 1 | TRM p.139 |
| Isolation | Not needed: with high-side FETs the AFE and MCU share `GND_PWR` | – | FAQ p.11 §4.6 |
| Limitation | CRC and timeouts cannot both be selected (no such Comm Type). The always-on 2 s SCL-low bus reset remains | – | TRM p.138–139 |

SPI would only win with a digital isolator between AFE and MCU, which this topology does not need. Clock stretching is supported on I2C (FAQ p.11 §4.4), so the STM32 I2C must allow stretching.

---

## 3. Supply and housekeeping circuit (REG0 / REG1, BAT, CP1)

```
 BAT_SNS (J_CELL1 pin 18 = CELL_16, own contact)
   │
   ├──|>|── D_BAT1 1N4148WS ──[R_BAT1 100R]──┬──── BAT (47)
   │                                         ═ C_BAT1 1u/100V ── VSS
   │
   └──|>|── D_REG0 1N4148WS ──[R_REG0C1 3k3 1W 2512]──┐  (separate diode, DS p.64)
                                                      │ C
                                    BREG (37) ───B── Q_REG0 1 FCX495TA (SOT-89, 150 V, 1 W)
                                         │            │ E
                                   R_BREG1 10M        ├──── REGIN (36) ── C_REGIN1 22n ── VSS
                                         │
                                        VSS   REG1 (35) = AFE_REG1 3.3 V ── C_R1 2u2 ── VSS
 CP1 (46) ──── C_CP1 2u2/50V ──── BAT (47)
 REG18 (24) ── C_R18 2u2 ── VSS          REG2 (34) ── C_REG2 1u (DNP)
```

### 3.1 REG0 pre-regulator (calc)

* **Normal load.** At 3 mA on REG1, the collector resistor drops 9.9 V.
  * Q_REG0 then dissipates (58.4 − 0.6 − 9.9 − 5.5) V × 3 mA = 0.13 W.
* **Worst case for the transistor,** with any load or a REG1 short: P_Q ≤ V²/(4R) = 57.8² / (4 × 3300) = **0.25 W** in a 1 W SOT-89. Without the resistor, a REG1 short (up to 80 mA, DS p.14) would put about 4 W in the NPN.
  * FAQ p.18 recommends series resistance in the BJT path.
  * The only overload is a REGIN short: R_REG0C1 then sees 1.0 W for the duration of that board fault.
* **Headroom at 2.5 V × 16 = 40 V:** 40 − 0.6 − 16.5 − 5.5 = 17 V at 5 mA. This is why **REG1 is budgeted at ≤ 5 mA**. At 10 mA the headroom disappears.

### 3.2 Why REGIN comes from REG0 and not from +5V

REGIN has a diode to BAT and must never exceed BAT (DS p.7, p.46). A +5V-fed REGIN would back-power the AFE whenever the board runs from a bench input with no pack attached.

### 3.3 BAT hold-up (calc)

* 1 µF at about 0.5 mA AFE draw droops 0.5 V/ms.
* That is ample to ride through an SCD event, whose detection delay is about 30 µs (DS p.64).

### 3.4 REG1 load budget (≤ 5 mA)

| Load | Current |
|---|---|
| DDSG / DCHG into logic inputs plus the 100 k pull-downs | 2 × 33 µA |
| R_DOFF1 when BOTHOFF is asserted | 0.33 mA |
| Optional gate-kill logic of the safety part | ≤ 2 mA |

Set HWD Regulator Options = 0x00, so the host watchdog never switches off REG1, because REG1 feeds the safety island (TRM p.138).

### 3.5 CP1 sizing

* Use 2.2 µF, the DS maximum (p.20).
* TI's example: with 400 nF of total gate load, 2.2 µF drops from 11 V to about 9 V at turn-on (DS p.65).
* The FET-bank Ciss belongs to the power-stage part. If it exceeds about 400 nF, a gate buffer is needed (AN09).
* X7R derating at 11 V keeps the effective value below the 2.2 µF maximum (est.).
* Start-up is slower than the 60 ms quoted for 470 nF: about 0.3 s (est.).

---

## 4. Cell input network, connector and balancing

### 4.1 Cell input network (per pin)

| Item | Value | Reason |
|---|---|---|
| R_VC0–R_VC15 | **100 Ω 1 % 0603** | DS range 20–100 Ω (p.9). External-switch designs use the 100 Ω maximum to get base drive (AN81 p.3). 1 kΩ (the old plan and the MPN field) is outside the DS range |
| R_VC16 | **20 Ω** | The top input carries 35 µA per balancing cell: 8 × 35 µA × 100 Ω = 28 mV error, against 5.6 mV at 20 Ω (calc; AN81 p.8, FAQ p.17) |
| C_DF1–16 (VCn–VC(n−1)) | **220 nF 50 V X7R 0603** | DS 0.1 / **0.22** / 1 µF min / typ / max (p.9). FAQ p.17 recommends 0.22 µF. 100 nF −10 % X7R sits below the 0.1 µF minimum. τ = 2 × 100 Ω × 220 nF = 44 µs, against a 3 ms conversion (calc; AN81 p.8) |
| Common-mode caps (VCn–VSS) | **none** | TI: large capacitance from a cell pin to VSS or another pin makes hot-plug transient current excessive; limit caps to the specified values (DS p.71). The old plan's 10 nF common-mode caps are dropped |
| VC0 | R_VC0 to `CELL_0`; `CELL_0` = VSS on the PCB | Required for random connection order (DS p.70, p.75) |

**Hot-plug and connection order** (DS p.70–71):
* Any order of tap connection is supported, provided all of the following hold:
  * VC0 is already tied to VSS through its resistor on the PCB
  * cells are in ascending pin order
  * cell-pin capacitances stay within the specified values
* The VC1–VC16 pins tolerate up to 85 V each (DS p.7–8).
* The BAT diode and RC allow ride-through (DS p.64, p.75).

**Balancing-transistor caution (est.).** During a partial plug, a floating tap can briefly put more than 25 V across one SS8050 C–E (VCEO = 25 V, SS8050-DS p.1). The energy is limited to the charge on the floating node's capacitors, but survival is not guaranteed.
* Assembly rule: connect the B− power cable first, then the single latched tap connector.
* Drop-in fallback with a higher VCEO: BC817-40 (45 V, C8589).

### 4.2 Cell-tap connector J_CELL1

* **Part:** Molex Micro-Fit 3.0, **2 × 9, right angle, polarized and latched**: 430451800, C293541. Listing: 8.5 A per contact, 600 V.
* **Assignment:**
  * pins 1–9 = `CELL_0`…`CELL_8`
  * pins 10–17 = `CELL_9`…`CELL_16`
  * pin 18 = `BAT_SNS` (a second contact to the cell-16 positive terminal, used only for the AFE supply)
  * Keeping BAT current out of the VC16 sense wire keeps the 0.3 mA supply current off the top-cell reading.
* **Current per contact:**
  * steady state ≤ 0.13 A: 100–108 mA through R_BL plus up to 21 mA into the pin (calc §4.4)
  * the active-balancer module has **its own harness**, so its 1–2 A never flows in J_CELL1 (research 03 §3)
* **Why it replaces today's header:** today J_CELL1 is a 1 × 17 2.54 mm header, unkeyed and unlatched. Its LCSC number C224359 is really an NVE IL610 isolator.
* Mating housing and terminals: harness bill of materials, not checked on LCSC (unverified).
* Recommend an inline fuse per tap wire at the cell end (owner question Q6). An open B− cable would otherwise push load current through the `CELL_0` sense wire.

### 4.3 Per-channel balancing circuit (TI NPN option, AN81 §2.4 Fig 2-5)

```
                     (J_CELL1)
 CELL_n ●───────┬──────────────[R_VCn 100R]───────────────●── VCn      (U_AFE1)
                │                                         │
          R_BLn 33R 1W 2512                         C_DFn 220n
                │                                         │
                │ C (pin 3)                               │
           Q_BLn SS8050 ─B (pin 1)──●──[R_BBn 220R]───────●── VC(n-1)  (U_AFE1)
                │ E (pin 2)         │                     │
                │                 D_BBn 1N4148WS          │
                │                 K = base, A = emitter   │
 CELL_(n-1) ●───┴───────────────────●─────[R_VC(n-1) 100R]┘
```

How it works:
* The AFE closes its internal switch between VCn and VC(n−1) (R_CB 15 / 28 / 46 Ω, DS p.18).
* I_CB flows out of the VC(n−1) pin. Part of it passes through R_VC(n−1), part through R_BBn into the base, and Q_BLn saturates (AN81 p.7).
* D_BBn clamps the reverse V_BE during pack transients. A standard diode is acceptable for a BJT (AN81 p.7). R_BBn limits the clamp current.

**SS8050 (C2150, JSCJ), checked live in SS8050-DS Rev 2.1 p.1:**
* pinout 1 = Base, 2 = Emitter, 3 = Collector (the same order as the AO3400A G / S / D footprint)
* V_CEO 25 V, V_EBO 5 V, I_C 1.5 A, P_C 300 mW, RθJA 417 °C/W
* **hFE(1) = 120–400 at V_CE = 1 V, I_C = 100 mA.** The "RANGE 200-350" listing is rank H.
* hFE(2) ≥ 40 at 800 mA
* V_CE(sat) ≤ 0.5 V at I_C = 800 mA, I_B = 80 mA. There is no V_CE(sat) line at 100 mA; it is about 0.1 V from the typical curve (est.).

**Base drive** (calc; node equations including the clamp path D_BB(n+1)–R_BB(n+1) of the channel above; V_BE 0.72 V, diode 0.6 V):

| V_cell | R_CB | I_CB (into AFE) | I_B | I_C ≈ (V − 0.1)/33 | Forced β | Margin vs hFE min 120 |
|---|---|---|---|---|---|---|
| 2.8 V | 46 Ω | 13.0 mA | 1.8 mA | 82 mA | 45 | 2.7× |
| 3.2 V | 28 Ω | 16.8 mA | 3.0 mA | 94 mA | 31 | 3.9× |
| 3.4 V | 46 Ω | 16.3 mA | 2.8 mA | 100 mA | 35 | 3.4× |
| 3.65 V | 15 Ω | 21.2 mA | 4.4 mA | 108 mA | 25 | 4.8× |

* The transistor stays saturated even if hFE halves when cold (est.).
* **I_CB ≤ 21 mA, against the 100 mA abs max** (DS p.8).
* **Cross-check:** TI's NPN build (Rn 100 Ω, Rbn 240 Ω, 4 V) measured I_B ≈ 4.5 mA and about 22 mA internal (AN81 p.7), consistent with the model.

**Power and thermal (calc):**

| Item | Per channel | Notes |
|---|---|---|
| R_BLn at 3.65 V | (3.55 / 33)² × 33 = **0.38 W** | 1 W 2512, 38 % load |
| R_BLn at 3.40 V | 0.33 W | – |
| Q_BLn | about 0.1 V × 108 mA ≈ 11 mW (est.) | – |
| Total cell current | 3.4 V: 100 + 18 ≈ **118 mA**; 3.65 V: 108 + 21 ≈ **129 mA** | – |
| 8 channels at once | ≤ **3.0 W** on the B.Cu bank | – |
| AFE internal per cell | I_CB² × R_CB ≤ 21² mA² × 15 Ω ≈ 7 mW, or 17.6² × 46 ≈ 14 mW | 8 cells ≤ 0.12 W |

* AFE total ≈ 0.14 W → +9 K junction rise at 66 °C/W (DS p.10, calc).
* 2512 derating near 100 °C local is assumed to leave ≥ 0.6 W of capability (UNI-ROYAL derating curve **unverified**).
* Expected hot-spot ΔT on the bank: 30–40 K (est., not simulated). Throttle on `NTC_BAL` (MCU) and on Max Internal Temp.

**Odd / even constraint.**
* If cells n and n+1 balance together, the currents in R_VCn cancel and Q_BL(n+1) loses its base drive (research 03 §1.4, calc).
* Firmware therefore uses **group A = odd cells 1, 3 … 15 or group B = even cells 2 … 16, at most 8 cells**, and never adjacent cells.
* `Cell Balance Max Cells` is ignored in host mode (TRM p.175; AN81 p.9), so the firmware enforces the limit.
* Autonomous mode only ever picks non-adjacent cells (DS p.63), so the fallback is safe.
* **Duty:**
  * Balancing pauses while the cell or a neighbour is measured, and for about 20 ms every second for the COV / CUV checks (AN81 p.9, p.11).
  * [CB_LOOP_SLOW] = 3 slows the loop to 1/8 speed (TRM p.136), giving about 96 % duty (research 03 §1.3, calc).
* **Rate:** 1 % of 280 Ah = 2.8 Ah takes ≈ 2.8 / (0.118 × 0.96) ≈ **25 h** of balancing (calc). That is about 3–5× the published Daly / JBD figures (research 02 / 03; vendor claims).

### 4.4 Active-balancer module header J_ABAL1 (`BAL_EXT_EN`)

```
 MCU BAL_EXT_EN ──┬── gate Q_ABAL1 2N7002 (60 V)     J_ABAL1 (JST-XH-compatible 4P, keyed)
                  │        drain ───────────────────── 1  BAL_EN_OD (open drain, sinks ≤ 100 mA)
           R_ABAL1 100k    source ── GND_PWR ───────── 2  GND_PWR
                  │                                     3  +5V via F_ABAL1 100 mA PTC
                 GND_PWR                                4  spare / key (NC)
```

* The default is off (gate pull-down).
* The module **must use its own cell harness**.
* The enable inputs of JK / Heltec / NEEY modules were not checked (unverified). If a module needs a floating dry contact, a DNP opto-MOS footprint in parallel is an option (part not selected).
* Firmware enables the module only when:
  * ΔSOC > 3 % (from the charge-based algorithm), and
  * the cells are in the knee or at rest.

---

## 5. Temperature

| Sensor | Where | Input | Mode / filter | Protection |
|---|---|---|---|---|
| Pack NTC 1 | cell surface (harness) | **TS1** | 18 k pull-up, 18K model, "cell" → config 0x07 (TRM p.146) | OTC / OTD / UTC / UTD, autonomous |
| Pack NTC 2 | cell (harness) | **HDQ** | 0x07 (TRM p.148 format as p.141) | autonomous |
| Pack NTC 3 | cell (harness) | **TS3** | 0x07 | autonomous |
| **FET bank** | RT_FET1 0603 at the DSG / CHG banks | **CFETOFF** | 18 k, 18K model, **FET temperature** → **0x0F** (TRM p.141) | **OTF (MCU-independent)**, SOTF PF |
| AFE die | internal | – | [TINT_EN] = 0 (TRM p.154) | OTINT / UTINT, balancing cut-off |
| Pack NTC 4 | cell (harness) | MCU ADC `NTC_PACK4` | 10 k to `+3V3_A` (MCU part) | firmware |
| Pack NTC 5–6 (option) | cells | MCU ADC via J_NTC2 | – | firmware |
| Shunt | next to the 2 × WSLP5931 | MCU ADC `NTC_SHUNT` | – | firmware, CC temperature compensation |
| Balancer bank | among the R_BL on B.Cu | MCU ADC `NTC_BAL` | – | balancing throttle |
| Ambient / board | board edge, away from heat | MCU ADC `NTC_AMB` | – | heater control, derating |

**Count (calc).**
* 4 pack NTCs (6 with the option) + FET + shunt + balancer + ambient + die = **9 sensors (11 with options)**.
* This meets the 4–8 requirement for pack temperatures and adds the board temperatures.
* **Three pack NTCs and the FET NTC act autonomously in the AFE.**

**Filter and ESD.**
* **1 nF** at each AFE pin: τ ≈ 18 kΩ × 1 nF = 18 µs, against the TI rule τ < 5 % of 3 ms (C < 4 nF with 18 k, DS p.65). This is ≤ 3.3 nF as required.
* R_TSx 100 Ω in series limits clamp current. Its error is +1 % of R_NTC, about 0.25 °C at 25 °C and about 0.8 °C at 60 °C (calc); it can be trimmed with the temperature offsets (AN32 p.7).
* ESD: PESD5V0S1BA (bidirectional, 5 nA leakage) at the connector, last before J_NTC1.
  * Leakage matters because the thermistor pins are high-impedance and limited to VREG18 + 0.3 V (DS p.7).
  * The old part number C84296 does not exist on LCSC.

**Probes and board NTCs.**
* TI's default 18K polynomial is characterized with a Semitec 103AT (B ≈ 3435) and the internal 18 k pull-up (DS p.69–70). Specify 103AT-compatible 10 k probes for the harness.
* The board NTC NCP18XH103F03RB is B 3380, which gives a small polynomial error at the extremes (est. ≤ 2 °C). Use the custom model (TRM p.199) if needed (unverified magnitude).

**Connectors.**
* J_NTC1 = 8-pin XH (C157972): NTC 1–4, one pair each.
* J_NTC2 = 4-pin XH (option, C2908602): NTC 5–6.
* Today's J_NTC1–4 carry LCSC C224345, which is an RS-485 transceiver, not a connector.

---

## 6. Fault outputs, host control and response times

### 6.1 Circuit

```
 DDSG (32) ── AFE_FLT_DSG_N ──┬── to the gate-kill logic (safety part) and an MCU EXTI
                              R_DDSG1 100k ── VSS     (Hi-Z in SHUTDOWN → "fault", TRM p.61)
 DCHG (31) ── AFE_FLT_CHG_N ──┬── as above
                              R_DCHG1 100k ── VSS
                  AFE_REG1
                     │
                  R_DOFF1 10k
                     │
 DFETOFF (30) ───────●──── drain Q_DOFF1 2N7002 ── source VSS
                     │       gate ── AFE_DFETOFF (MCU, high = all FETs off) ── R_DOFFG1 100k ── VSS
                     └──|>|── D_DOFF1 BAT54WS (anode at node) ── OC_TRIP_N (latched, active low)
 ALERT (25) ── AFE_ALERT ── R_ALRT1 10k ── +3V3
 RST_SHUT (33) ── AFE_RST_SHUT ── R_RST1 10k ── VSS
 TS2 (22) ──|>|── WAKE_BTN_RAW ──|<|── WAKE_BTN_N (MCU pull-up)      D_WAKE1 = BAV170, common cathode
                                 └── push-button to GND_PWR (power part)
```

### 6.2 Pin configuration

| Pin | Data-memory value | Meaning | Source |
|---|---|---|---|
| DDSG Pin Config 0x9302 | **0xAA** | DDSG function, active-low ("low when DSG is disabled"), REG1 drive, push-pull | TRM p.153 |
| DCHG Pin Config 0x9301 | **0xAA** | as DDSG, for CHG | TRM p.150 (same format) |
| DFETOFF Pin Config 0x92FB | **0xC2** | BOTHOFF, active-low | TRM p.143 |
| ALERT Pin Config 0x92FC | **0x82** | alarm, active-low, open-drain (Hi-Z when inactive) | TRM p.145 |
| CFETOFF Pin Config 0x92FA | **0x0F** | thermistor, FET temperature | TRM p.141 |
| TS1 / TS3 / HDQ 0x92FD / 0x92FF / 0x9300 | **0x07** | thermistor, cell, 18K model | TRM p.146–148 |
| TS2 Config 0x92FE | **0x00** | unused, free for wake. [SHUT_TS2] = 0 | TRM p.136, p.146 |

### 6.3 Rationale

* **DDSG / DCHG.**
  * The datasheet's own use case is "control external protection circuitry" or host interrupts (DS p.49; TRM p.60). Here they feed the MCU-independent gate-kill (safety part).
  * They stay active in NORMAL, SLEEP **and DEEPSLEEP** (TRM p.61).
  * [DPSLP_LDO] = 1 keeps REG1 on in DEEPSLEEP, so the outputs stay driven (TRM p.136).
  * **Firmware rule:** do not use DSG_PDSG_OFF(), CHG_PCHG_OFF() or FET_CONTROL() while these pins are in DDSG / DCHG mode. Use ALL_FETS_OFF() or BOTHOFF instead (TRM p.34 Table 5-8).
* **BOTHOFF wired-AND.**
  * Any source pulling the node low turns all four FETs off (DS p.48).
  * BAT54WS forward drop at 0.33 mA is about 0.25 V. With the OC latch output at ≤ 0.1 V, the pin sits at ≤ 0.35 V, below V_IL = 0.33 × VREG18 ≈ 0.59 V (DS p.11, calc).
  * If the MCU is in reset, Q_DOFF1's gate is pulled low, so the AFE keeps autonomous control. The AFE host watchdog then trips if the MCU stays silent (§8).
* **TS2 wake.**
  * In SHUTDOWN, TS2 is driven weakly to about 5 V (R_OH ≈ 4.6 MΩ). A falling edge below 0.7–1.1 V wakes the part (DS p.9, p.11).
  * BAV170 (silicon, ≤ 5 nA) is used instead of a Schottky: 5 nA × 4.6 MΩ = 23 mV, so no false wake from leakage (calc).
  * When pressed, TS2 sits at the diode drop at about 1 µA, ≈ 0.4 V (est.).
  * **The button must switch the separate node `WAKE_BTN_RAW`.** If the button were wired straight to `WAKE_BTN_N`, the dead `+3V3` pull-up in ship mode would hold TS2 low and the part could never stay in SHUTDOWN (calc reasoning).
* **LD wake.** A charger on PACK+ raises LD above 0.8–2.25 V and wakes from SHUTDOWN (DS p.9), and from DEEPSLEEP with [DPSLP_PD] = 1 (TRM p.136).

### 6.4 Response times

| Event | Time | Source |
|---|---|---|
| SCD detection | setting (here 30 µs) + comparator: 600 ns at 25 mV overdrive, 8 µs at 3 mV | DS p.22; TRM p.182 |
| Fault → FET off for SCD / OCD1 / OCD2 / CUV (DSG) and SCD / OCC / COV (CHG) | **"fast response"**, only if CHG FET Prot A = 0x98 / 0x18 and DSG FET Prot A = 0xE4 / 0x80; otherwise up to 250 ms (NORMAL) or 1 s (SLEEP) | TRM p.34, p.62 Table 6-9 |
| DSG gate discharge | 2–20 µs at 20 nF / 100 Ω (bank: longer) | DS p.20 |
| CHG gate discharge | 46–65 µs at 20 nF | DS p.20 |
| OCC / OCD1 / OCD2 delay | 10–425 ms in 3.3 ms steps | DS p.22 |
| COV / CUV delay | 10 ms–6.75 s; about 1 s on balanced or adjacent cells | DS p.21; AN81 p.11 |
| OCD3, temperatures, HWD, PF checks | evaluated every **1 s** | TRM p.62 |
| ALERT for hardware faults [SSA] | fast; other alarm bits every 250 ms | TRM p.62 |
| DDSG / DCHG after a fault | **not stated by TI.** AN84 p.3 implies they follow the FET decision | **unverified, bench** |
| BOTHOFF asserted → FETs off | **not stated** | **unverified, bench** |
| BOTHOFF released / ALL_FETS_ON → FETs on | evaluated every 250 ms | TRM p.62 |
| RST_SHUT high | immediate digital reset (FET and FUSE state kept); held 1 s → SHUTDOWN | DS p.48 |
| Wake (TS2 / LD) → REG1 up → FETs on | 20 ms → 282 ms | DS p.71 Table 16-2 |

---

## 7. FUSE pin (DNP footprint)

```
 FUSE (38) ──[R_FU1 5k1]──●── gate Q_FU1 IRLML0100 (100 V, 1.6 A, SOT-23)
                          │       drain ── J_FUSE1 pin 2 ──(fuse heater / shunt-trip coil)── pin 1 ── PACK+ or BAT+ (per fuse position)
          R_FU3 100k ── VSS       source ── VSS
 2nd-level protector out ──[R_FU2 5k1]──┘ (option)
 D_FU1 ES1D across the coil (DNP; only for an inductive shunt-trip)
```

**Component values.** These follow TRM Fig 6-1 (p.61): 5.1 kΩ, 5.1 kΩ and 100 kΩ. The exact topology was read from figure labels only (**unverified**). The figure confirms an NFET driven by FUSE and OR-ed with a secondary protector.

**Pin limits.**
* Drive: V_OH 6–9 V at 5 kΩ (DS p.12).
* Input current ≤ 2 mA; pin abs max = min(20 V, VBAT + 0.3 V) (DS p.7–8).
* Detect: V_IH 2–12 V, so the device can sense a secondary protector (DS p.12; TRM p.61).

**Configuration** (TRM p.135, p.156–157):
* [PF_FUSE] = 1, and [FETF_FUSE] = 1 so a welded-FET PF blows the fuse regardless of voltage
* Min Blow Fuse Voltage = 3000 (30 V)
* Fuse Blow Timeout = 30 s (chemical fuse) or about 2 s (shunt-trip coil, owner question)
* [PACK_FUSE] = 1 if the fuse sits on the PACK side
* 2LVL PF only if a secondary protector is fitted

All parts DNP until the owner picks a fuse or breaker (Q5). For 200 A, a breaker shunt-trip is the likely choice, because 3-terminal chemical fuses in the 200 A class are rare (est.).

---

## 8. LFP 16S 280 Ah / 200 A data-memory image

### 8.1 Basis

* **Shunt:** 100 µΩ (2 × WSLP5931L2000FEA, research 04).
* **Current units:** USER_AMPS = 100 mA, so 1 userA = 0.1 A (TRM p.154).
* **Thresholds:** all 3.3 ms delays use the code n → (n + 2) × 3.3 ms (TRM p.179–181). Comparator accuracy is from DS p.21–22.
* **Addresses and defaults:** TRM p.197–204. All values are proposals for owner review.

### 8.2 Image table

| Group | Setting (address) | Default | **LFP value** | Result / reason | TRM page |
|---|---|---|---|---|---|
| Comms | Comm Type (0x9239) | 0 | **0x12** | I2C Fast + CRC | 138–139 |
| | I2C Address (0x923A) | 0 | 0 | 0x10 / 0x11 | 139 |
| Units | DA Configuration (0x9303) | 0x05 | **0x07** | USER_AMPS = 100 mA (±3276 A), centivolts | 154 |
| Cells | Vcell Mode (0x9304) | 0x0000 | **0xFFFF** | 16 cells | 154–155 |
| Regulators | REG0 Config (0x9237) | 0x00 | **0x01** | REG0 on | 137–138 |
| | REG12 Config (0x9236) | 0x00 | **0x0D** | REG1 = 3.3 V on; REG2 off | 137 |
| | HWD Regulator Options (0x9238) | 0x00 | **0x00** | HWD never toggles REG1 | 138 |
| Power | Power Config (0x9234) | 0x2982 | **0x2DB1** | +[DPSLP_LDO], CB_LOOP_SLOW = 3, WK_SPD = 1 (24 ms; setting 2 "may exhibit a large offset"), SLEEP on, OTSD on, [SHUT_TS2] = 0 | 135–137 |
| Calibration | CC Gain (0x91A8) | 7.4768 | **74.768** (then calibrate) | 7.4768 / 0.1 mΩ | 198; AN32 p.5 |
| | Capacity Gain (0x91AC) | 2 230 042 | **22 300 425** | CC Gain × 298 261.6 (calc). TRM max 4.19 E8; AN32 lists a lower max (discrepancy, §11) | 198; AN32 p.6 |
| COV | Threshold (0x9278) / Delay (0x9279) / Hyst (0x927C) | 86 / 74 / 2 | **72 / 301 / 2** | **3.643 V**, 1.00 s, recovery 3.542 V. ±25 mV over −40…85 °C | 179, 202; DS p.21 |
| CUV | Threshold (0x9275) / Delay (0x9276) / Hyst (0x927B) | 50 / 74 / 2 | **49 / 604 / 2** | **2.479 V**, 2.0 s, recovery 2.580 V | 179, 202 |
| COVL | Latch Limit (0x927D) | 0 | **3** | repeated COV latches the charger off | 202 |
| OCC | Threshold (0x9280) / Delay (0x9281) | 2 / 4 | **13 / 28** | 26 mV = **260 A** (±40 A), 99 ms. The precise charge limit is MCU firmware | 180, 202; DS p.22 |
| OCD1 | Threshold (0x9282) / Delay (0x9283) | 4 / 1 | **28 / 4** | 56 mV = **560 A** (±50 A), 19.8 ms. Lets the 500 A peak through (duration: Q2) | 181, 202 |
| OCD2 | Threshold (0x9284) / Delay (0x9285) | 3 / 7 | **15 / 119** | 30 mV = **300 A** (±40 A), 399 ms | 181, 202 |
| OCD3 (FW, CC1) | Threshold (0x928A) / Delay (0x928C) | −4000 / 2 | **−2200 / 30** | **−220 A**, 30 s. Accurate continuous limit | 183, 202 |
| SCD | Threshold (0x9286) / Delay (0x9287) / Recovery (0x9294) | 0 / 2 / 5 | **4 / 3 / 5** | 80 mV = **800 A** (680–920 A at ±15 %), 30 µs | 182, 202; DS p.22 |
| SCDL | Latch Limit (0x9295) | 0 | **1** | no time-based recovery after SCD (TRM p.182); recover by LD or host | 182–184 |
| OCDL | Latch Limit (0x928F) | 0 | **3** | – | 202 |
| Load detect | Active Time / Retry / Timeout (0x92B4–B6) | 0 / 50 / 1 | **6 / 30 / 2** | Active Time > Sleep Voltage Time (5 s), as required | 188–189, 203 |
| Temperature | OTC thr / dly / rec (0x929A–C) | 55 / 2 / 50 | **45 / 2 / 40** °C | LFP charge window | 203 |
| | OTD (0x929D–F) | 60 / 2 / 55 | **60 / 2 / 55** | – | 203 |
| | UTC (0x92A6–8) | 0 / 2 / 5 | **0 / 2 / 3** | no charging below 0 °C (heater output) | 203 |
| | UTD (0x92A9–B) | 0 / 2 / 5 | **−20 / 2 / −15** | – | 203 |
| | OTF (0x92A0–2) | 80 / 2 / 65 | **85 / 2 / 70** | FET bank via CFETOFF | 203 |
| | OTINT / UTINT | 85 / −20 | 85 / **−40** (rec −35) | outdoor ESS | 203 |
| Enables | Enabled Protections A (0x9261) | 0x88 | **0xFC** | SCD, OCD2, OCD1, OCC, COV, CUV | 157–158 |
| | Enabled Protections B (0x9262) | 0x00 | **0xF7** | OTF, OTINT, OTD, OTC, UTINT, UTD, UTC | 158–159 |
| | Enabled Protections C (0x9263) | 0x00 | **0xF6** | OCD3, SCDL, OCDL, COVL, PTO, HWDF | 159 |
| FET action | CHG FET Prot A / B / C | 0x98 / 0xD5 / 0x56 | **0x98 / 0xD5 / 0x56** (keep) | A = 0x98 keeps the fast path | 159–161 |
| | DSG FET Prot A / B / C | 0xE4 / 0xE6 / 0xE2 | **0xE4 / 0xE6 / 0xE2** (keep) | A = 0xE4 keeps the fast path | 161–162 |
| | Body Diode Threshold (0x9273) | 50 mA | **1000 mA** | 50 mA = 5 µV, below the CC offset at 100 µΩ (calc) | 163 |
| FET | FET Options (0x9308) | 0x0D | **0x1F** | SFET, SLEEPCHG, HOST_FET_EN, FET_CTRL_EN, **PDSG_EN**; FET_INIT_OFF = 0 (autonomous) | 168 |
| | Chg Pump Control (0x9309) | 0x01 | **0x01** | 11 V overdrive (FET V_GS(max) ≥ 15 V required, DS p.69); no source-follower | 168–169 |
| | Precharge Start / Stop (0x930A / 0x930C) | 0 / 0 | **2500 / 2700 mV** | PCHG recovery charge of an over-discharged pack | 169 |
| | Predischarge Timeout / Stop Delta (0x930E / 0x930F) | 5 / 50 | **250 / 100** | 2.5 s maximum, exit at LD within 1.0 V of TOS. Power part sizes R_PDSG | 35, 169 |
| | PTO Charge Thr / Delay | 250 mA / 1800 s | keep | – | 203 |
| Thresholds | Dsg / Chg Current Threshold (0x9310 / 0x9312) | 100 / 50 userA | **10 / 10** | 1.0 A relax window (defaults would be 10 A / 5 A in 100 mA units) | 170, 200–201 |
| Sleep | Sleep Current (0x9248) / Wake Comparator (0x924B) | 20 / 500 mA | **1000 / 1000 mA** | – | 202 |
| Shutdown | Shutdown Cell V / Stack V / Delay | 0 / 600 / 1 | **2300 mV / 3600 (36 V) / 10 s** | 1 µA ship / storage protection; wake by TS2 or LD | 176, 202 |
| HWD | Delay (0x92B2) | 60 s | **10 s** | second watchdog → FETs off through Prot C (Q3) | 188, 203 |
| Alarm | Default Alarm Mask (0x926D) | 0xF800 | **0xFA69** | + INITCOMP, XCHG, XDSG, FUSE, WAKE | 163–164 |
| PF | Enabled PF A (0x92C0) | 0x00 | **0x5F** | SUV, SOV, SOCC, SOCD, SOT, SOTF | 165–166 |
| | Enabled PF B (0x92C1) | 0x00 | **0x0B** | CFETF, DFETF, VIMR (+ 2LVL = 0x0F with a secondary protector) | 166 |
| | Enabled PF C / D | 0x07 / 0x00 | **0xFF / 0x01** | all internal diagnostics + commanded PF; TOS vs cell sum | 167 |
| | SOV / SUV (0x92CE / 0x92CB) | 4500 / 2200 | **3800 / 2000 mV**, 5 s | (Q4: SUV permanence) | 203 |
| | SOCC / SOCD | 10000 / −32000 userA | **3000 / −4000** (300 A / −400 A) | – | 203 |
| | SOT / SOTF | 65 / 85 °C | **70 / 100 °C** | – | 203 |
| | CFETF / DFETF OFF Threshold | 20 / −20 mA | **500 / −500 mA**, 5 s | avoids a false PF from CC offset at 100 µΩ (calc) | 204 |
| | VIMR Check V / Thr / Max Relax I / Duration | 3500 / 500 / 10 / 100 | **3300 mV / 300 mV / 1000 mA / 600 s** | LFP rest window | 203 |
| | Protection Configuration (0x925F) | 0x0002 | **0x0022** (fuse fitted: **0x0132**) | PF_OTP, PF_FETS (+ PF_FUSE, FETF_FUSE); PF_REGS = 0 keeps REG1 | 156–157 |
| Manufacturing | Mfg Status Init (0x9343) | 0x0040 | **0x00D0** | FET_EN (leave FET Test mode), PF_EN, OTPW_EN | 173 |
| Balancing | Balancing Configuration (0x9335) | 0x00 | **0x0F** | CB_CHG, CB_RLX, CB_SLEEP, CB_NOSLEEP (autonomous fallback; host commands still accepted) | 174 |
| | Min / Max Cell Temp, Max Internal | −20 / 60 / 70 | **0 / 50 / 70 °C** | – | 174 |
| | Interval / Max Cells | 20 s / 1 | **20 s / 8** | – | 175 |
| | Min Cell V (Charge / Relax) | 3900 / 3900 | **3400 / 3400 mV** | The default would never balance LFP | 175, 201 |
| | Min Delta / Stop Delta (Charge / Relax) | 40 / 20 | **20 / 8 mV** | – | 201 |
| Interconnect | Cell 1–16 Interconnect (0x9315…) | 0 | measured per harness (mΩ) | Accurate V under 200 A | 173, 201 |
| Fuse | Min Blow V / Timeout | 500 / 30 | **3000 / 30 s** (or about 2 s) | §7 | 135, 199 |
| Security | Security Settings (0x9256) | 0x00 | **0x01** (SEAL) | §9 | 196–197 |
| | Unseal / Full Access keys (0x9257–0x925D) | 0x0414 / 0x3672 / 0xFFFF / 0xFFFF | **customer keys** (not the TI-published ones) | §9 | 197 |
| Integrity | Config RAM Signature (0x91E0) | 0 | lower 15 bits of STATIC_CFG_SIG() | MCU checks the configuration at every boot | 72, 179 |

---

## 9. Production: calibration, OTP golden image and security

### 9.1 Test-point access

| TP | Net | Purpose |
|---|---|---|
| J_CELL1 pins 17 + 18 | `CELL_16` / `BAT_SNS` | 11.5 V for OTP (VC16 and BAT) |
| J_CELL1 pin 1 | `CELL_0` = VSS | return |
| TP_VSS | `GND_PWR` (star) | – |
| TP_SCL / TP_SDA | `AFE_SCL` / `AFE_SDA` | Fixture I2C master. The MCU is held in reset through SWD NRST, so its pins are Hi-Z |
| TP_3V3 | `+3V3` | Fixture supplies the pull-up rail if the board DC/DC does not start at 11.5 V |
| TP_REG1 / TP_REGIN | `AFE_REG1` / `AFE_REGIN` | check 3.3 V / about 5.5 V after OTP |
| TP_ALERT, TP_RST | `AFE_ALERT`, `AFE_RST_SHUT` | INITCOMP and reset control |
| TP_SRP / TP_SRN | filtered SRP / SRN | offset check |
| Fixture cell ladder | J_CELL1 pins 1–17 | 2-point cell calibration (relays) |
| High-current DC source | `BAT-` / `PACK-` lugs (through the shunt) | CC gain |

**OTP supply** (calc): 11.5 V ± 0.2 V on pins 17 + 18.
* BAT ≈ 11.5 − 0.55 V (1N4148WS at 0.3 mA, est.) ≈ 10.9 V, inside 10–12 V.
* VC16 ≈ 11.5 V, also inside 10–12 V.
* Required: 10–12 V on BAT and VC16, **no cells**, −40…45 °C (DS p.9; FAQ p.12 §4.10; AN32 p.14).

### 9.2 Procedure

1. **Blank check.** Read a programmed register; blank parts show the defaults (AN32 p.14 step 1).
   * BQ76952PFBR blank parts talk I2C **without** CRC. The fixture or firmware tries CRC and falls back to plain I2C (DS p.4).
2. **Fixture state:** board populated, no cells. Apply the cell ladder (16 × about 3.3 V) and BAT through pin 18.
   * Hold the MCU in reset, or use the MCU "factory mode" (owner choice).
3. **Unseal and enter configuration mode.**
   * Default keys 0x0414 / 0x3672, then full access 0xFFFF / 0xFFFF (TRM p.197).
   * Check Battery Status[SEC1:0] = FULLACCESS.
   * Enter CONFIG_UPDATE (0x0090) (AN32 p.14).
4. **Load the configuration image** into RAM (§8). Exit CONFIG_UPDATE (0x0092), read back and verify every field (AN32 p.14 steps 4–6).
5. **Calibrate** (AN32 p.2–8). First disable SLEEP (0x009A).
   * **Cell gain, 2-point:** ladder at 2.50 V and 3.60 V per cell; read DASTATUS1–4 (0x0071–0x0074); compute Cell n Gain → 0x9180–0x919E (AN32 p.2–4).
   * **Vcell Offset:** the average of the per-cell offsets → 0x91B0 (AN32 p.4).
   * **TOS / PACK / LD gain:** 2-point through READ_CAL1 0xF081 → 0x91A0–0x91A4 (AN32 p.4–5).
   * **Board offset:** 0 A, average CC2 counts × Coulomb Counter Offset Samples (64) → 0x91C8. This is **mandatory**: DS accuracy is "after board-offset calibration" (DS p.10 note 2; AN32 p.5).
   * **CC gain:** 2 currents through the shunt, e.g. 0 A and 50 A.
     * 50 A gives 5 mV, against the 7.6 µV CC LSB.
     * Write CC Gain (F4, IEEE-754) → 0x91A8 and Capacity Gain = CC Gain × 298 261.6178 → 0x91AC (AN32 p.6).
   * **Temperature offsets:** at a stabilized 25 °C fixture ambient, internal plus the board NTC on CFETOFF → 0x91CA / 0x91CB (AN32 p.6–7). Harness probes are not part of the board test.
   * **Optional:** CAL_COV / CAL_CUV (0xF091 / 0xF090) set the override codes at 3.643 / 2.479 V (AN32 p.7).
6. **Drop to OTP conditions without a reset.**
   * Relays disconnect the ladder; BAT and VC16 stay at 11.5 V.
   * BAT never falls below POR (3–4 V, DS p.9), so the RAM contents survive (TRM p.14).
7. **Write OTP 1 (configuration and calibration).**
   * CONFIG_UPDATE; Battery Status[OTPB] clear; OTP_WR_CHECK 0x00A0 must return 0x80 (bits HighTemp / LowVoltage / HighVoltage clear).
   * OTP_WRITE 0x00A1; wait 100 ms; read 0x40 = 0x80; exit (TRM p.14–15; AN32 p.14). About 200 µs per byte (TRM p.15).
   * The configuration and the calibration may be split into two OTP writes (AN32 p.14). **Budget: 8 signature writes in the device's life** (TRM p.14; FAQ p.12).
8. **Lock.**
   * Program the customer keys and Security Settings [SEAL] = 1 in the same image (TRM p.196–197).
   * Write MANU_DATA (serial number, image version, calibration date; 32 bytes, DS p.34) in FULLACCESS.
   * Program Config RAM Signature = STATIC_CFG_SIG() & 0x7FFF (TRM p.72, p.179).
9. **Power-cycle check.**
   * Remove and re-apply 11.5 V; wait for INITCOMP; read back key settings, STATIC_CFG_SIG() and the SEALED state.
   * Check REG1 = 3.3 V, DDSG / DCHG high (no fault) and Comm Type = CRC.
10. **Functional checks.**
    * With FET_EN = 1, use the FET test subcommands **before** OTP: PDSGTEST / PCHGTEST / CHGTEST / DSGTEST (TRM p.33–34).
    * Wake via TS2 and LD; BOTHOFF via Q_DOFF1 and `OC_TRIP_N`.
    * Balancing on one odd and one even group.

### 9.3 Security

* **Keys.** Never ship the TI-published keys (TRM p.197).
  * Recommended: per-unit keys derived in the MCU from the STM32 UID and a product secret, stored in read-protected flash (MCU part).
  * Keys are sent little-endian through 0x3E / 0x3F; SECURITY_KEYS() 0x0035 changes them (TRM p.71).
* **SEALED operation still allows** measurements, host balancing commands (AN81 p.10) and FET commands with [HOST_FET_EN] = 1 (TRM p.34, p.168).
* **[LOCK_CFG] and [PERM_SEAL]:** not set by default. They would block any field re-configuration forever (TRM p.197). Owner question Q7.

### 9.4 Runtime PF-to-OTP

* **This resolves an open research question.** With [PF_OTP] = 1 and [OTPW_EN] = 1, PF status and MANU_DATA writes during operation still check the **minimum** BAT voltage, but **the maximum is not restricted**. So they work at 16S pack voltage, at about 125 ms per byte (TRM p.15, p.157).
* These writes are outside the configuration signature (TRM p.14).

---

## 10. Parts table (sheet 02 after the change)

Stock figures are LCSC / JLC on 2026-11-17. B/E: B = JLC Basic ("base"), E = Extended ("expand").

| Ref-to-be | Function | Part | LCSC | Stock (LCSC / JLC) | B/E | Key rating | Source |
|---|---|---|---|---|---|---|---|
| U_AFE1 | AFE | TI **BQ76952PFBR** (rec.) | **C2862742** | 11 814 / 11 814 | E | 3–16S, 80 V, TQFP-48 | L+J |
| (U_AFE1 alt.) | AFE, I2C + CRC + REG1 default | TI BQ7695202PFBR | C3038665 | 83 / 83 | E | as above | L+J |
| R_VC0–R_VC15 | cell input R | UNI-ROYAL 0603WAF1000T5E 100 Ω 1 % | C22775 | 2 378 600 / 10 828 740 | B | 0603, 100 mW, 75 V | L+J |
| R_VC16 | top input R | UNI-ROYAL 0603WAF200JT5E 20 Ω 1 % | C22950 | 434 800 / 1 215 783 | B | 0603 | L+J |
| C_DF1–16 | differential cell cap | Samsung CL10B224KB8NNNC 220 nF 50 V X7R | C64705 | 341 140 / 444 773 | E | 0603 | L+J |
| (C_DF alt.) | if Basic is preferred | Yageo CC0603KRX7R9BB104 100 nF 50 V | C14663 | 122 400 / 32 827 472 | B | at the DS minimum | L+J |
| Q_BL1–16 | balance NPN | JSCJ SS8050 (RANGE 200–350) | **C2150** | 1 862 700 / 3 025 020 | B | 25 V, 1.5 A, hFE 120–400 at 100 mA | L+J + SS8050-DS |
| (Q_BL alt.) | higher V_CEO | JSCJ BC817-40 | C8589 | – / 64 170 | E | 45 V, 500 mA | J |
| R_BL1–16 | balance resistor | UNI-ROYAL 25121WF330JT4E 33 Ω 1 % 1 W | **C53728** | 29 460 / 43 865 | E | 2512, 1 W, 200 V | L+J |
| (R_BL alt.) | 2 W | UNI-ROYAL PS122WF330JT4E 33 Ω 2 W | C2793905 | 3 040 / 3 042 | E | 2512, 2 W | L+J |
| R_BB1–16 | base resistor | UNI-ROYAL 0603WAF2200T5E 220 Ω | C22962 | 115 400 / 1 877 700 | B | 0603 | L+J |
| D_BB1–16 | B–E reverse clamp | JSCJ 1N4148WS | C2128 | 1 861 350 / 3 944 705 | B | 100 V, 150 mA, SOD-323 | L+J |
| J_CELL1 | cell taps 16S + 1 (+ BAT) | Molex Micro-Fit 3.0 430451800, 2 × 9 R/A | C293541 | 367 / 637 | E | 8.5 A, 600 V, latched, polarized | L+J |
| (J_CELL1 alt.) | clone | HCTL HC-MX3.0-2*9AW | C3294390 | 878 / 878 | E | 5 A, 250 V | L+J |
| Q_REG0 1 | REG0 NPN | Diodes FCX495TA | C150457 | 1 567 / 2 223 | E | 150 V, 1 A, 1 W, SOT-89 | L+J |
| R_REG0C1 | collector R | UNI-ROYAL 25121WF3301T4E 3.3 kΩ 1 W | C620876 | 3 680 / 24 242 | E | 2512 | L+J |
| D_REG0, D_BAT1 | collector / BAT diodes (separate) | JSCJ 1N4148WS | C2128 | as above | B | 100 V | L+J |
| (D alt.) | if surge margin above 100 V is needed | LRC LBAS21HT1G | C12742 | 125 600 / 144 761 | E | 250 V | L+J |
| R_BAT1 | BAT RC | 0603WAF1000T5E 100 Ω | C22775 | as above | B | – | L+J |
| C_BAT1 | BAT cap | Samsung CL31B105KCHNNNE 1 µF **100 V** X7R | C13832 | 195 290 / 267 002 | E | 1206 | L+J |
| C_REGIN1 | REGIN cap | Samsung CL10B223KB8NNNC 22 nF 50 V | C21122 | 266 750 / 1 052 410 | B | 0603 | L+J |
| R_BREG1 | BREG leakage R | UNI-ROYAL 0603WAF1005T5E 10 MΩ | C7250 | 522 900 / 996 885 | B | 0603 | L+J |
| C_R1, C_R18 | REG1, REG18 caps | Samsung CL10A225KO8NNNC 2.2 µF 16 V X5R | C23630 | 824 300 / 2 956 741 | B | 0603 | L+J |
| C_REG2 (DNP) | REG2 cap | Samsung CL10A105KB8NNNC 1 µF 50 V | C15849 | 0 / 12 889 672 | B | 0603 | L+J |
| C_CP1 | charge-pump cap | Samsung CL31B225KBHNNNE 2.2 µF 50 V X7R | C50254 | 10 / 273 424 | B | 1206 | L+J |
| R_SRP1, R_SRN1 | CC filter | 0603WAF1000T5E 100 Ω | C22775 | as above | B | – | L+J |
| C_SR1 (+ C_SR3 / C_SR4 DNP) | CC filter | Yageo CC0603KRX7R9BB104 100 nF | C14663 | as above | B | – | L+J |
| C_SR2 | CC filter, optional | Samsung CL10C101JB8NNNC 100 pF C0G | C14858 | 0 / 3 299 264 | B | – | L+J |
| R_LD1, R_PACK1 | LD / PACK series R | UNI-ROYAL 1206W4F1002T5E 10 kΩ | C17902 | 509 100 / 1 850 096 | B | 1206, 200 V | L+J |
| R_SCL1, R_SDA1 | I2C pull-ups | UNI-ROYAL 0603WAF4701T5E 4.7 kΩ | C23162 | 2 171 400 / 14 572 957 | B | – | L+J |
| R_SCLS1, R_SDAS1 | I2C series R | 0603WAF1000T5E 100 Ω | C22775 | as above | B | – | L+J |
| R_ALRT1, R_RST1, R_DOFF1 | pull-up / pull-down | UNI-ROYAL 0603WAF1002T5E 10 kΩ | C25804 | 5 900 / 41 699 172 | B | – | L+J |
| R_DDSG1, R_DCHG1, R_DOFFG1, R_ABAL1, R_FU3 | 100 k pull-downs | UNI-ROYAL 0603WAF1003T5E 100 kΩ | C25803 | 5 057 200 / 14 359 332 | B | – | L+J |
| Q_DOFF1, Q_ABAL1 | BOTHOFF / balancer-enable switch | JSCJ 2N7002 | C8545 | 5 535 000 / 6 186 382 | B | 60 V, 115 mA | L+J |
| D_DOFF1 | OC_TRIP_N into BOTHOFF | Diodes BAT54WS-7-F | C124205 | 58 835 / 59 176 | E | 30 V Schottky, SOD-323 | L+J |
| D_WAKE1 | TS2 / button OR | JSCJ BAV170 (common cathode, low leakage) | C68970 | 11 520 / 12 111 | E | 75 V, 5 nA | L+J |
| C_TS1–4 | NTC filter | Samsung CL10B102KB8NNNC **1 nF** | C1588 | 634 800 / 5 537 091 | B | 0603 | L+J |
| R_TS1–4 | NTC series R | 0603WAF1000T5E 100 Ω | C22775 | as above | B | – | L+J |
| D_ESD1–4 (+ 5–6 option) | NTC ESD | Nexperia PESD5V0S1BA,115 | C19224 | 79 275 / 86 061 | E | 5 V, bidirectional, 5 nA | L+J |
| RT_FET1 (+ NTC_SHUNT / NTC_BAL / NTC_AMB) | board NTC | Murata NCP18XH103F03RB 10 k B3380 1 % | C13564 | 259 330 / 271 017 | E | 0603 | L+J |
| J_NTC1 | pack NTC 1–4 | JST B8B-XH-A(LF)(SN) | C157972 | 54 115 / 55 099 | E | 8P, 2.5 mm, 3 A | L+J |
| J_NTC2 (option) | pack NTC 5–6 | HCTL XH-4A | C2908602 | 184 240 / 196 359 | E | 4P | L+J |
| J_ABAL1 | active-balancer header | HCTL XH-4A | C2908602 | as above | E | 4P keyed | L+J |
| F_ABAL1 | +5V to the module | RUILON SMD0805P010TF | C20975 | 49 860 / 51 701 | E | 100 mA hold, 15 V | L+J |
| R_FU1, R_FU2 (DNP) | FUSE drive | UNI-ROYAL 0603WAF5101T5E 5.1 kΩ | C23186 | 13 607 000 / 19 035 360 | B | – | L+J |
| Q_FU1 (DNP) | fuse / trip driver | Infineon IRLML0100TRPBF | C53658 | 7 260 / 7 264 | E | 100 V, 1.6 A, ±16 V V_GS | L+J |
| D_FU1 (DNP) | coil flyback | Vishay ES1D-E3/61T | C82648 | 96 183 / 98 068 | E | 200 V, 1 A | L+J |
| J_FUSE1 (DNP) | fuse / trip output | HCTL XH-2A | C2908600 | – / 164 120 | E | 2P, 3 A | J |

### 10.1 Wrong LCSC numbers found on the current sheet (all checked live)

| Ref today | LCSC in field | What it really is | Correct LCSC |
|---|---|---|---|
| U_AFE1 | C2687103 | Fuzetec FRVL050-120F **PTC fuse** | C2862742 (or C3038665) |
| R_BL1–16 | C17936 | 1206 **4.7 kΩ** (confirmed) | C53728 |
| Q_BL1–16 | C85073 | **does not exist** (LCSC and JLC) | C2150 (SS8050) |
| C_DF1–16, C_CP1 | C14666 | **does not exist** | C64705 (220 nF) / C50254 (CP1) |
| R_VC0–16 | C22775 is correct (100 Ω) | MPN field says RC0603FR-071KL (1 kΩ) | fix the MPN to 0603WAF1000T5E |
| C_NTC1–4, C_TS_PCB | C1588 | **1 nF**, not 10 nF | keep C1588, fix the value |
| RT_BOARD | C19702 | **10 µF capacitor** | C13564 (NTC), relocated |
| D_ESD_NTC1–4 | C84296 | does not exist | C19224 |
| D_BAT1 | C8677 | XH-2Y **connector housing** | C2128 |
| C_BAT1 | C28323 | 1 µF **50 V** (under-rated for 58.4 V) | C13832 (100 V) |
| R_SCL1, R_SDA1 | C22822 | **17.8 Ω** | C23162 (4.7 kΩ) |
| J_CELL1 | C224359 | NVE IL610A-2E **isolator** | C293541 |
| J_NTC1–4 | C224345 | NVE IL3285E **RS-485 transceiver** | C157972 |
| C_R1, C_R18 | C23630 | 2.2 µF **16 V** X5R (field says 10 V): acceptable | keep |

---

## 11. Interface signals

### 11.1 Contract signals used by part C

| Signal | Direction (from the AFE side) | Electrical | Owner of the other end |
|---|---|---|---|
| `AFE_SCL`, `AFE_SDA` | bidirectional | open-drain, 4.7 k to `+3V3`, 400 kHz, CRC | MCU (a real I2C peripheral, clock stretching on) |
| `AFE_ALERT` | AFE → MCU | open-drain active-low, 10 k to `+3V3` | MCU EXTI |
| `AFE_RST_SHUT` | MCU → AFE | push-pull, 10 k to VSS; high = reset, ≥ 1 s = SHUTDOWN | MCU |
| `AFE_DFETOFF` | MCU → AFE | logic high (3.3 V) = all FETs off (inverted by Q_DOFF1); 100 k pull-down | MCU |
| `OC_TRIP_N` | latch → AFE | active-low latched trip, open-drain or push-pull 3.3 V; pulls BOTHOFF through D_DOFF1 | safety / current part |
| `AFE_FLT_DSG_N`, `AFE_FLT_CHG_N` | AFE → gate-kill and MCU | push-pull 0 / 3.3 V from REG1; low = fault; 100 k to VSS (Hi-Z = fault) | safety (gate-kill) + MCU |
| `KILL_N`, `FET_EN` | – | must clamp the **gate to source** of the banks (DSG to PACK+, CHG to BAT+), never to VSS (DS p.72) | power / safety part |
| `WAKE_BTN_N` | button → MCU | MCU pull-up; joined to TS2 only through D_WAKE1 | power part |
| `BAL_EXT_EN` | MCU → Q_ABAL1 | 3.3 V logic, high = module enabled | MCU |
| `+3V3` | supply | I2C / ALERT pull-ups | power |
| `GND_PWR` | – | = AFE VSS = `BAT-` star at the shunt cell-side Kelvin | power |
| `BAT+`, `PACK+`, `BAT-`, `PACK-` | – | R_LD1 / R_PACK1 to `PACK+`; VSS at `BAT-` | power stage |
| `CELL_0..16` | harness → board | J_CELL1 pins 1–17; `CELL_0` tied to VSS on the PCB | – |
| `VC0..16` | – | AFE-side nodes after R_VC | – |
| `+5V` | supply | to J_ABAL1 pin 3 through F_ABAL1 | power |

### 11.2 New signals

| New signal | Direction | Electrical | Counterpart |
|---|---|---|---|
| `AFE_REG1` | AFE out | 3.3 V, ≤ 5 mA budget, alive whenever the AFE is not in SHUTDOWN | safety island (gate-kill logic supply); optionally an enable for the power part |
| `AFE_CHG`, `AFE_DSG` | AFE out | CHG / DSG gate drive (BAT + 11 V) | power-stage FET banks |
| `AFE_PCHG`, `AFE_PDSG` | AFE out | P-FET gate drive (about 8.4 V below PACK / BAT, 30 µA) | power-stage pre-charge / pre-discharge |
| `AFE_LD`, `AFE_PACK` | sense in | through 10 k to `PACK+` | power stage |
| `AFE_FUSE` | AFE I/O | 6–9 V drive / 2–12 V sense | DNP fuse / trip, optional secondary protector |
| `SHUNT_K_BAT`, `SHUNT_K_PACK` | sense in | Kelvin pair to SRP / SRN (separate from the INA240 pair) | current part |
| `BAT_SNS` | harness → AFE | J_CELL1 pin 18, second `CELL_16` contact, AFE supply only | – |
| `WAKE_BTN_RAW` | button node | button contact to `GND_PWR`; the cathode node of D_WAKE1 | power part (button wiring) |
| `NTC_FET` | sensor → AFE CFETOFF | 10 k NTC to VSS at the FET bank | power-stage layout |
| `NTC_PACK4`, `NTC_SHUNT`, `NTC_BAL`, `NTC_AMB` (+ `NTC_PACK5/6`) | sensor → MCU ADC | 10 k NTC to `GND_PWR` / `GND`; bias from `+3V3_A` | MCU |
| `CB_ACTIVE` (firmware only) | – | not a net | – |

---

## 12. Open questions for the owner

1. **AFE variant.** BQ76952PFBR (11.8 k in stock; CRC and REG1 come from the EOL OTP) or BQ7695202PFBR (83 in stock; CRC and REG1 3.3 V by default)? I recommend the base part.
   * No "-Q1" BQ76952 was found on LCSC. The current Value field "BQ76952-Q1" should become "BQ76952".
2. **Charge current rating and the 500 A peak duration.** These set OCC (260 A here) and the OCD1 delay (20 ms here).
3. **HWD timeout** (10 s proposed). During MCU firmware update the AFE turns the FETs off unless the bootloader keeps talking to it. Is an output drop during an update acceptable?
4. **SUV PF at 2.0 V with PF_OTP.** This permanently disables an over-discharged pack. Keep it (safety), lower it to 1.8 V, or disable PF_OTP for SUV?
5. **FUSE:** a 200 A breaker with a shunt-trip coil, a chemical fuse, or none? Is a secondary OV protector (2LVL) wanted?
6. **Harness:** inline fuses per tap wire at the cells? Assembly order (B− first, then taps)? 103AT-type probes?
7. **Security:** per-unit keys (recommended)? [LOCK_CFG] / [PERM_SEAL]? Both block any field re-configuration forever.
8. **Active-balancer module:** which module and which enable interface (open-drain to B−, or a floating dry contact → add an opto-MOS)?
9. **Ship mode:** auto-SHUTDOWN at 2.3 V per cell (1 µA). Acceptable, given that the MCU, comms and LEDs then go dark until the button or a charger wakes the pack?
10. **Autonomous balancing fallback** running alongside SOC-based host balancing: keep it enabled (0x0F) or disable it while the MCU is alive (RAM change)?
11. **Shunt TCR.** The WSLP5931L2000 is ±125 ppm/°C against TI's ≤ 50 ppm/°C (DS p.75). Accept it, or use the `NTC_SHUNT` compensation in firmware (current part)?

---

## 13. Unverified items

* **DDSG / DCHG response time** after a fault, and whether they also assert for host-commanded OFF or BOTHOFF. No TI number was found (AN84 p.3 is indirect). Bench test.
* **BOTHOFF assert → FET-off timing.** Not in the TI text that was read. Bench test.
* **FUSE application circuit topology** (TRM Fig 6-1, DS Fig 12-1). Only the labels 5.1 k / 5.1 k / 100 k were readable in the text extract.
* **SS8050:**
  * V_CE(sat) at 100 mA (spec only at 800 mA; the 0.1 V is from the typical curve, est.)
  * hFE at −40 °C
  * survival of > 25 V C–E stress during a partial plug
* **R_BB 0603 pulse rating** during pack transients. The thermal figures for the balancing bank are estimates and not simulated. The UNI-ROYAL 2512 derating curve was not opened.
* **BAV170** leakage at 85 °C (5 nA is the 25 °C listing figure). The TS2 low level (≈ 0.4 V when pressed) is an estimate.
* **Default REG0_EN on the BQ7695202** (irrelevant if the base part is chosen).
* **COV delay encoding.** The TRM states the 6.6 ms-offset rule for CUV, OCC and OCD (p.179–181); the same rule is assumed for COV.
* **Predischarge exit logic** when both a timeout and a stop delta are set ("either … or … or both", TRM p.35).
* **Interaction of autonomous balancing with host CB_ACTIVE_CELLS** commands.
* **CC Gain / Capacity Gain range.** AN32 p.6 lists CC Gain 0.1–10 and Capacity Gain ≤ 4.19 E6; the TRM (p.198) lists 0.01–1000 and ≤ 4.19 E8. The TRM was used. Confirm that 74.768 / 22.3 E6 are accepted.
* **Temperature error** of the B3380 board NTC with the 18K (103AT) polynomial. Magnitude estimated, not computed.
* **Harness mating parts** (Micro-Fit housing and terminals, XH housings) on LCSC. **Enable interface** of commercial active-balancer modules.
* **STM32G473RCT6 I2C pin mapping and clock-stretch support:** for the MCU part. DS12589 / the G473 data sheet was not opened here.
* **Pack-level surge clamp below 100 V:** the 1N4148WS BAT and REG0 diodes rely on it. Owned by the power part.
* **CP1 behaviour with the actual FET-bank gate charge.** Ciss is unknown until the power stage is chosen.
* **Stock figures** change daily. Re-check in the JLCPCB BOM tool before ordering. LCSC shows 0 or very low stock for C14858, C15849 and C50254, while the JLC Basic stock is high.
