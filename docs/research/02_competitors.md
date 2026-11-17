# 02 – Competitor benchmark: 16S / 48 V ESS BMS (2024–2026)

Research date: 2026-11-17. Report only; nothing in the project folder was changed.

**How to read this file**
* Every cell has a source tag `[Sn]`. The source list is in §7.
* **[F]** after a source: I read the full document text myself (PDF text extracted, copies in `research/pdf/`). **[S]**: I saw only a search-engine snippet or summary. The page itself returned 403/429 or was not opened. Treat [S] values as lower confidence.
* "unknown" means no source I reached states the value. I did not estimate it.
* Prices come from retail or B2B listings (Alibaba, eBay, Fogstar, Accio). They are marked as listings, not factory prices.
* Several products are sold in many revisions (JK V19/V24, Seplos V2/V3/10E, Daly 3rd/4th gen). The values apply to the document cited, not to every revision.

---

## 1. Feature matrix

### 1a. Power path, measurement, balancing

| Product (doc date) | Cont. / peak current | Switch, shunt | Balancing | Cell-V accuracy | Current accuracy | SOC method / accuracy | Temp channels | Heater / fan | Pre-charge |
|---|---|---|---|---|---|---|---|---|---|
| **Seplos 16S 200A "Smart BMS"** (manual V16, 2022-10) | Doc title 200 A. The electrical table says 100–110 A, copied from the 100 A doc. Transient OCP 300 A / 30 ms [S1 F] | MOSFET, <2 mΩ, current-sense resistors [S1 F] | Passive (resistor). Current not stated in the manual [S1 F]. Retailer: 150 mA max [S3 S] | ±10 mV (0–45 °C), ±30 mV (−20–0 / 45–70 °C) [S1 F] | ±1 % [S1 F] | Coulomb count. Learns capacity on first full cycle. ±5 % [S1 F] | 4 cell + ambient + MOSFET, ±2 °C [S1 F] | Heater: unknown. Fan: unknown | Yes, 1–5000 ms, "for capacitive load" [S1 F] |
| **Seplos 10E** (listings) | 100 A and 150 A variants listed [S2 S]. 300 A variant sold as "48300-…-10E" [S4 F] | MOSFET (300 A: <2 mΩ) [S4 F] | Passive ≤150 mA [S4 F]. Separate 2 A active board sold [S30 S] | unknown | unknown | "Accurate SOC/SOH", no figure [S4 F] | unknown | unknown | Retailer: 0–3000 ms [S3 S] |
| **JBD UP16S010** (spec A03, 2023-03) | 200 A cont. OCD2 650 A / 500 ms. SCD 1800 A / 300 µs [S5 F] | 32 × 100 V MOSFET, 10 mΩ board [S5 F] | Passive, **20–60 mA**, time-shared [S5 F] | unknown (not in spec) | unknown | Capacity learning by full cycle [S5 F]. Accuracy unknown | 2 internal + 4 external NTC [S5 F] | Heater: **not supported** [S5 F]. Fan: unknown | "Pre-discharge function: standard" [S5 F] |
| **JK PB2A16S20P** (spec V1.01, 2023-10, poor translation) | 200 A cont. [S7 F]. Max 300 A / 2 min [S8 S] or 350 A peak [S8 S], sources disagree. SCP 300 A / 20 µs default [S7 F] | MOSFET. Shunt: unknown | **Active, 1 A or 2 A option** [S7 F]. Topology (capacitor or inductor): unknown | unknown ("high-precision") [S7 F] | unknown | "Capacity estimation", method unknown [S7 F] | 4 NTC + MOS temp [S7 F] | **Heater output**: on below −20 °C, off at −10 °C, configurable [S7 F]. ~10 A heater current [S10 S]. Fan: unknown | V24 hardware: "discharge pre-charge" [S10 S]. V19: unknown |
| **PACE P16S100A** (spec 2021-12 / 2022-03) | 100 A model. OCD2 150 A / 100 ms [S14 F]. P16S200A exists [S15 F] | MOSFET + separate "limiting plate" [S14 F] | Passive (charge balance). Current: unknown [S14 F] | **20 mV** [S14 F] | **2 % FS** [S14 F] | SOC + SOH estimation. Accuracy unknown [S14 F] | 4 cell + ENV + MOS [S14 F] | **Heating film output** option: on <0 °C, off >15 °C [S14 F]. Fan: unknown | **Yes, rated 30 000 µF** [S14 F] |
| **Daly 4th-gen home ESS (LK / LM)** (web, 2026) | LK 100 A (120 A custom). LM 150 / 200 A [S17 F][S18 F]. Peak unknown | unknown | Passive standard. **Optional active 1 A (LK) / 2 A (LM)** [S17 F] | unknown | unknown | unknown | unknown | unknown | "10 A peak inrush protection" + **10 A parallel current limiter** [S17 F][S18 F] |
| **Daly R16L active-balance home BMS** (2023-08) | "100/150 A" in model code only [S19 F] | unknown | Active (title only), current unknown [S19 F] | unknown | unknown | unknown | unknown | unknown | unknown |
| **Daly R16A 16S 100A** (2020, basic) | 100 A dis / 50 A chg [S20 F] | MOSFET (potted) [S20 F] | Passive **30 ± 5 mA** [S20 F] | unknown | unknown | unknown | unknown | – | – |
| **ANT 16S** (wiring guide, 2021) | 100 A version: 320 A for 30 s [S22 F] | unknown | unknown | unknown | unknown | unknown | 2 NTC [S22 F] | unknown | unknown |
| **Tian Power** | **No BMS datasheet found.** Only a SmartLi 48V100A pack listing (CAN, Ethernet) [S23 S] | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown |
| *Unbranded OEM KS48100-Ho21* (spec 2024-08, reference) | 200 A cont. [S24 F] | MOSFET, <10 mΩ [S24 F] | Passive ~65 mA [S24 F] | ±10 mV (0–45 °C), ±20 mV wide [S24 F] | ±1 % [S24 F] | OCV + dynamic calibration, ±5 % [S24 F] | 4 cell + ambient + MOS, ±2 °C [S24 F] | Heater port: on <0 °C, off >15 °C [S24 F] | unknown |
| *Pylontech US5000* (pack, reference) | 100 A cont. 121–200 A for 15 s [S25 S] | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown |
| *EG4 LifePower4 V2* (pack, reference) | 100 A BMS [S26 S] | unknown (has breaker) | unknown | unknown | unknown | unknown | unknown | Heater: no source found | unknown |

### 1b. Communications and user interface

| Product | CAN inverter protocols | RS-485 inverter protocols | BT / WiFi / cloud | RS-232 | Display | Dry contacts | Parallel packs, addressing |
|---|---|---|---|---|---|---|---|
| **Seplos 16S 200A** | Default CAN 500 k: Pylontech, Goodwe, Deye, TBB. Selectable: Growatt, Victron, SMA, Sofar, Solis, Studer [S1 F] | Pylontech, Growatt, SRNE [S1 F]. PC tool at 19200 bd | **Bluetooth app** [S1 F] | unknown | 4 SOC + ALM + status LEDs. LCD option [S1 F] | **2 outputs** (SOC/alarm/fault) [S1 F] + aerosol (fire suppressant) input [S1 F] | Parallel over RS-485, **8-bit DIP** (4 address + 4 slave count). **Auto-identification option** [S1 F]. 16 packs [S2 S]. Master switches slaves on/off [S1 F] |
| **Seplos 10E** | CAN + RS-485, protocol list as above (assumed, not confirmed) [S2 S] | as above | Bluetooth [S2 S] | unknown | External LCD [S2 S] | unknown | 16 [S2 S]. 300 A variant: up to 20, auto address [S4 F] |
| **JBD UP16S010** | CAN 500 k, standard [S5 F]. Brands not listed in spec. Community: Victron via CAN, Pylon to some inverters [S6 S] | Isolated RS-485 [S5 F] | **Bluetooth: not supported** in this model [S5 F] | **Yes** [S5 F] | LCD + 6 SOC + RUN/ALM LEDs [S5 F] | unknown | 4-bit DIP, 0–15 [S5 F] |
| **JK PB2A16S20P** | CAN (JK protocol 250 k / 500 k, Pylon 1.2, Deye, Growatt, Victron, INVT per community map) [S13 S]. Vendor list: Deye, GoodWe, Growatt, Invt, Must, Pylon, SMA, SRNE, Victron, Voltronic [S8 S]. **Victron not native** per a retailer [S12 S] | RS-485 (JK Modbus, Pylon LV, Growatt) [S13 S] | **Bluetooth app** [S7 F] | **Yes** (RJ11) [S7 F] | 3.2" (spec) or 4.3" LCD, 6 SOC + RUN/ALM LEDs [S7 F] | **2 outputs** (alarm, low SOC) [S7 F] | 2 × RS-485 parallel ports, 4-bit DIP 0–15 [S7 F]. Max 15P [S9 S] |
| **PACE P16S100A** | CAN 500 k, PACE-CAN-TY protocol [S14 F]. Inverter selection by PbmsTools (hard to change) [S15 F] | RS-485 Modbus V1.3, PACE-RS485-MS [S14 F] | none in spec | **Yes**, also used for FW update [S14 F] | 6 SOC + RUN/ALM LEDs, LCD option, buzzer [S14 F] | **2 outputs** (low SOC, fault) [S14 F] | Dual RS-485, 4-bit DIP 0–15 [S14 F] |
| **Daly 4th gen** | Pylon selectable + **auto-detect**: Deye, GoodWe, Growatt named [S17 F][S18 F]. Guide also names Victron, Sol-Ark, SMA, Solis, Sofar as Pylon-compatible (general claim) [S16 F] | not stated | **BT + WiFi + 4G, IoT cloud, GPS, remote OTA** (announced 2026-02-27) [S18 F] | unknown | Optional 3.5" display, aggregates 16 packs [S17 F] | unknown | 16, **software auto-addressing, no DIP** [S17 F] |
| **Daly R16L** | CAN 250 k (500 k to inverter), protocol selectable in PC tool, brands not named [S19 F] | Dual RS-485, 9600 bd, addr 1–16 [S19 F] | unknown | unknown | On-board screen [S19 F] | unknown | addr 1–16 [S19 F] |
| **ANT 16S** | One port, configured at order as CAN, RS-485 **or** UART (LCD) [S22 F] | same shared port [S22 F] | unknown | – | LCD on UART [S22 F] | unknown | unknown |
| **Tian Power** | CAN + Ethernet on pack [S23 S] | unknown | unknown | unknown | unknown | unknown | unknown |
| *KS48100-Ho21* | Pylon, Deye, Growatt, Goodwe, Ginlong (Solis), Victron, SMA [S24 F] | Voltronic, Shunri, Pylon [S24 F] | **BT + WiFi** [S24 F] | – | **5" touch screen** with protocol selection, LED strip, 4 SOC LEDs [S24 F] | none [S24 F] | 3 × RS-485 + 1 CAN, 4-bit DIP, 16 packs [S24 F] |
| *Pylontech US5000* | CAN + RS-485 (Pylon, the de-facto reference) [S25 S] | yes | unknown | unknown | unknown | unknown | 16 per group [S25 S] |
| *EG4 LifePower4 V2* | Closed loop with EG4 and other inverters, protocol by DIP [S26 S] | yes | unknown | unknown | unknown | unknown | 64 (V2 page) vs 16 (manual), sources conflict [S26 S] |
| *Basen 48V kits* | Protocol chosen on display menu, compatibility list in manual [S27 S] | yes | unknown | unknown | display [S27 S] | unknown | DIP [S27 S] |

### 1c. Power management, records, firmware, certification, size, price

| Product | Run / sleep current | Wake / button | Fault log depth | FW update | Certification (as stated) | Board size | Price (USD, listing) |
|---|---|---|---|---|---|---|---|
| **Seplos 16S 200A** | <40 mA / **≤50 µA** [S1 F] | Reset button: wake, sleep, reset. Auto-sleep after 48 h idle [S1 F] | **≥300 records**, event-triggered + timed, export to Excel [S1 F] | **Via RS-485** [S1 F] | unknown | unknown (drawing only) [S1 F] | Fogstar £130 ≈ US$165 [S3 S]. Accio $59–136 [S29 S]. Hakadi $175.90 [S29 S] |
| **Seplos 10E** | <40 mA / ~10 µA (garbled) (300 A variant) [S4 F] | unknown | unknown | unknown | 300 A variant: "meets IEC 62619 and UL 1973 functional-safety requirements" (claim, no certificate) [S4 F] | unknown | not listed [S4 F] |
| **JBD UP16S010** | 40 mA / **0.4 mA** [S5 F] | Key switch: wake / sleep / reset [S5 F] | "History storage: standard", depth unknown [S5 F] | unknown | unknown. **Secondary protection: not supported** [S5 F] | **300 × 100 × 38 mm** [S5 F] | unknown |
| **JK PB2A16S20P** | 19 mA / **200 µA** at 58 V [S7 F] | Activation switch, LCD key [S7 F] | "Accurate time logging", depth unknown [S7 F] | unknown | unknown | drawing only [S7 F] | Alibaba $131–133 [S11 S]. eBay ≈ $167 [S11 S] |
| **PACE P16S100A** | 35 mA (40 mA with LCD) / ~150 µA ("150A" in text, µ lost) [S14 F] | Button: wake 3–6 s, reset 6–10 s. Wake also by charger >48 V or RS-232 [S14 F] | Option: none or **400 items** [S14 F] | **Via RS-232** [S14 F] | unknown | drawing only [S14 F] | unknown |
| **Daly 4th gen** | unknown | unknown | unknown | **OTA via cloud** [S18 F] | "UL certification at BMS component level", supports UL 9540 at system level [S17 F] | unknown | B2B listing US$60 [S21 S]. Alibaba 16S100A with 1 A active: $73.50–82.80 [S21 S] |
| **Daly R16L** | ~45 mA / **~500 µA** typ, 1 mA max [S19 F] | Button wake / sleep / reset [S19 F] | unknown | unknown | unknown | **285 × 100 × 36 mm** [S19 F] | unknown |
| **ANT 16S** | unknown | Wake by charger, LCD or 3–5 V ACC signal [S22 F] | unknown | unknown | unknown | **140 × 70 × 17 mm** [S22 F] | unknown |
| **Tian Power** | unknown | unknown | unknown | unknown | unknown | unknown | unknown |
| *KS48100-Ho21* | 30 mA (80 mA with screen) / 100–200 µA [S24 F] | Self-locking switch [S24 F] | **500 records** [S24 F] | Via RS-485 [S24 F] | unknown. Has **secondary-protection port** (MOS fail + >100 °C, OVP +300 mV, UVP −300 mV) [S24 F] | unknown | unknown |
| *Pylontech US5000* | unknown | unknown | unknown | Via CAN or RS-485 from controller [S25 S] | Pylontech residential range (2023): UL 1973, UL 1642, UL 9540A, VDE 2510-50, IEC 63056, IEC 62619, IEC 62040, IEC 62477-1 [S25 S] | – | – |
| *EG4 LifePower4 V2* | unknown | unknown | unknown | unknown | UL 1973, UL 9540A (UL 9540 only with EG4 inverter and cabinet) [S26 S] | – | – |

---

## 2. Table stakes: what every serious 16S ESS BMS has in 2026

A feature is listed here when at least four of the five main BMS makers with usable documents (Seplos, JBD, JK, PACE, Daly) have it.

| # | Table-stakes feature | Evidence |
|---|---|---|
| T1 | **CAN to the inverter with Pylontech-compatible protocol**, plus a selectable list of 6–10 brands (Deye, Growatt, Goodwe, Victron, SMA, Sofar, Solis, Voltronic, SRNE, Luxpower) | S1, S7/S8, S14, S17, S24 |
| T2 | **RS-485 inverter + monitoring protocol** (Pylon RS-485, Growatt, Voltronic, Modbus) and a PC tool | S1, S5, S7, S14, S19 |
| T3 | **Parallel packs: 15–16 packs**, master aggregates slaves over a dedicated RS-485 link, **RJ45** connectors, 4-bit DIP address (auto-addressing is becoming common) | S1, S5, S7, S14, S17 |
| T4 | **SOC LED bar (4–6) + RUN + ALM LEDs**, optional LCD | S1, S5, S7, S14, S19 |
| T5 | **Wake / sleep / reset button**, and **sleep current of 50–500 µA**, with auto-sleep after inactivity or at low voltage | S1, S5, S7, S14, S19 |
| T6 | **Bluetooth app** (monitoring + parameter setting). JBD UP16S010 is the exception | S1, S7, S18, S24 |
| T7 | **2 dry-contact outputs** (alarm / low SOC), for generator start or an alarm panel | S1, S7, S14 |
| T8 | **Parallel / charge current limiting (10–20 A)**, so a pack at low SOC can join a bus of full packs | S1 (10 A), S5 (standard), S14 (option), S17/S18 (10 A), S24 (20 A) |
| T9 | **Pre-charge / pre-discharge for the inverter capacitor bank** | S1, S5, S10, S14 |
| T10 | **Event history: 300–500 records**, exportable | S1, S14, S24 |
| T11 | **Firmware update in the field** over RS-485 / RS-232 | S1, S14, S24 |
| T12 | **4 cell NTC + MOSFET/board + ambient**, **±1–2 % current**, **±10–20 mV cell voltage**, **SOC ±5 %** with cycle count and SOH estimate | S1, S14, S24 |
| T13 | **Heater output for charging below 0 °C** (heating film, ~10 A) | S7, S10, S14, S24. JBD does not support it (S5) |
| T14 | 150–200 A continuous on one board, MOSFET common port | all |

---

## 3. Differentiators, and gaps where all of them are weak

### 3a. What only the best have today

| Differentiator | Who has it | Comment |
|---|---|---|
| Active balancing, 1–2 A | JK (1 / 2 A) [S7], Daly LM (2 A option) [S17], Seplos as an add-on board [S30] | JK's main selling point. Topology is not stated anywhere I found |
| Inverter-protocol auto-detection | Daly 4th gen [S17][S18] | Others need a PC tool or DIP setting. PACE users report trouble changing the protocol [S15] |
| Pack auto-addressing (no DIP) | Daly [S17], Seplos option [S1], 300 A "10E" [S4] | |
| Cloud (WiFi/4G), remote OTA, GPS | Daly, announced 2026-02 [S18] | The only maker in this set with a stated OTA |
| Secondary protection input | KS48100 [S24]. JBD explicitly does not support it [S5] | A second trip level that does not depend on the main one |
| Touch screen with protocol selection | KS48100 5" [S24], Daly 3.5" [S17], JK 4.3" [S7] | |
| Busbar / wire resistance compensation (set by hand) | Seplos [S1] | Set manually in the PC tool |
| Fire-suppression (aerosol) input | Seplos [S1] | |
| Certification on the board itself | Daly "UL at component level" [S17]. The 300 A "10E" only claims to meet requirements [S4] | End-product packs (Pylontech, EG4) are certified. Bare Chinese boards mostly are not |

### 3b. Gaps where all of them are weak (opportunities)

| Gap | Evidence | Opportunity for us |
|---|---|---|
| **G1 No independent hardware trip path** shown in any document | Protection and switch control run through one AFE + MCU. JBD: secondary protection "not support" [S5] | BQ76952 autonomous protections + INA240/TLV3501 OCP latch → hardware AND gate on contactor drive, independent of firmware. "Secondary protection" as a feature on the datasheet |
| **G2 Measurement accuracy is modest** | ±10–30 mV cell, ±1–2 % current, SOC ±5 % [S1][S14][S24] | BQ76952 + on-board shunt with its coulomb counter. TI states ±15 mV max over −40…85 °C [S28]. Typical-at-25 °C figures were not verified. Measure and publish real numbers. A ±3 % SOC claim for LFP (est.) needs a coulomb-count + OCV-rest + hysteresis model |
| **G3 SOH is cycle count or capacity learning only** | Seplos and JBD count cycles at 80 % DOD and learn capacity on a full cycle [S1][S5] | SOH = capacity + **per-cell DC resistance** trend. Report "weakest cell" |
| **G4 No cell / connection impedance diagnostics** | Seplos compensation is set by hand [S1]; nobody detects it automatically | **EIS-lite / DCIR per cell**: on each inverter load step, take a synchronized ΔV/ΔI from the BQ76952 snapshot. Detects a **loose busbar bolt** (fire risk) and ageing cells. No competitor offers this |
| **G5 Log depth and quality are thin** | 300–500 records, no waveforms [S1][S14][S24] | Timestamped (RTC) log of thousands of events, plus a "black-box" capture of V/I/T for ±2 s around every trip |
| **G6 Closed protocols** | Users reverse-engineer them (ESPHome projects for PACE and JK [S15][S13]). JK not native to Victron [S12] | **Published** Modbus map + CAN DBC, native Victron + Pylon + SMA, Home Assistant / ESPHome support out of the box |
| **G7 Power path: MOSFET boards only** | All five makers use MOSFETs. A shorted MOSFET is the classic failure (KS48100 even has a "MOS failure" secondary trip [S24]) | Our **contactors** give a true galvanic disconnect, and we already have a measured pre-charge (bus-voltage sense). Add **contactor weld detection** and **pre-charge fault detection (short / timeout)**. Scales to 300 A+ and to HV stacks |
| **G8 Isolation is partial or not stated** | JBD: only RS-485 isolated, UART not isolated [S5]. PACE / JK: "isolated power supply" only [S7][S14] | All external ports isolated (CAN + RS-485 already). State the kV rating on the datasheet |
| **G9 OTA is rare and unsigned** | Only Daly states OTA [S18]. Others need RS-485/232 + PC [S1][S14] | Signed firmware, A/B image with rollback, update over CAN / RS-485 / BLE |
| **G10 No CAN-FD** | Everyone runs classic CAN at 250/500 k [S1][S5][S14][S19] | Low market value: inverters use classic CAN. Keep it as a future "multi-pack / HV" feature, not a v1 headline |
| **G11 Board certification** | Bare boards are rarely certified [S17 is the exception] | Design to IEC 62619 / UL 1973 (with UL 991 / 1998-style software analysis) and ship an evidence pack to pack makers. Takes time and money, but that is what OEM pack makers buy |

---

## 4. Mapping against our architecture (PROJECT.md §1.2, 2026-11-16)

Legend: **Have** = on the schematic today. **Add (current parts)** = possible with the parts / MCU pins already there, mostly firmware or passives. **New parts** = needs new components.
Free MCU pins today: PA15, PB3, PB4, PB5, PC14, PC15.

| Feature | Status | Notes |
|---|---|---|
| T1 CAN inverter protocols | **Have (HW)** + firmware | Isolated CAN on ISO7721 + TJA1051T/3. The protocol library is all firmware. Only one FDCAN, so CAN goes to the inverter |
| T2 RS-485 protocols | **Have (HW)** + firmware | One isolated half-duplex port |
| T3 Parallel 16 packs | **New parts** | We have one RS-485. Inverter-on-CAN + parallel-on-RS-485 works with today's hardware. An inverter that speaks RS-485 needs a **second isolated RS-485**. Our 1×4 2.54 mm headers must become **RJ45** (×2–3). The DIP switch is used for chemistry / cell count, not addressing → add an address DIP or do auto-addressing (one link line per RJ45 + firmware) |
| T4 SOC LEDs, RUN / ALM | **New parts** (cheap) | Only rail LEDs + heartbeat today. 6 LEDs need pins → use a 74HC595 on SPI1 or charlieplex on spare pins |
| T5 Wake button, sleep 50–500 µA | **New parts** | LM5164 EN/UVLO is tied to VIN and the isolated module is always on, so there is **no sleep path**. Standby current is not measured but is likely tens of mA. Needs a power latch (button / charger detect / CAN-RS485 wake) that drives LM5164 EN, and the isolated supply switched off in sleep. **Biggest table-stakes gap** |
| T6 Bluetooth app | **New parts** | ESP32-C3 (BLE + WiFi) on USART2 (PB3 / PB4 free). Check 3V3 budget (AP2112K, 600 mA) |
| T7 Dry contacts ×2 | **New parts** | 2 × PhotoMOS or a small relay on PA15 / PB5 |
| T8 Parallel current limit | **Add (current parts)**, partly | With contactors we cannot regulate current. Close the **pre-charge contactor + R_PRE1 first** until the bus equalises, then the main contactor. This needs firmware and a correctly rated R_PRE1. A true 10 A regulated limiter would need new parts |
| T9 Pre-charge | **Have**, better than competitors | Pre-charge contactor + R_PRE1 + bus-voltage sense on PA1 = closed-loop pre-charge with timeout / short detection |
| T10 Event history | **Have** (limited) | 25LC256 = 32 KB → about 700–900 records of 32 B (est.) after config, already ≥ competitors. Timestamps need the RTC (below) |
| T11 FW update | **Add (current parts)** | Custom bootloader over RS-485 / CAN. STM32G431 has 128 KB flash, so an A/B image needs external flash (below) |
| T12 Sensing | **Have** | BQ76952 + 4 NTC + board NTC. Shunt moving on board (owner decision). INA240 + BQ CC |
| T13 Heater output | **New parts** | 4th low-side driver (copy of the contactor driver: MOSFET + gate R + zener) on a free pin. ~10 A heating film |
| T14 150–200 A | **Have** (contactor + shunt) | Contactors are external parts; see §5 note on BOM |
| G1 Independent HW trip | **Add (current parts) + small logic** | BQ76952 protections and `OCP_TRIP_N` exist but **go only to the MCU** (PROJECT.md §1.2). A latch + AND gate on the contactor gate drive is needed. Note: BQ76952 DDSG / DCHG are used as NTC inputs today, so the ALERT pin or a freed DDSG pin must carry the AFE trip |
| G2 / G3 SOC, SOH | **Add (current parts)**, firmware | On-board shunt + BQ CC + MCU model |
| G4 DCIR / EIS-lite | **Add (current parts)**, firmware | BQ76952 synchronized V/I snapshots. Accuracy depends on cell-tap filter RC (R_VC = 100 R today) |
| G5 Deep log + black box | **New parts** (cheap) | 32.768 kHz crystal on PC14 / PC15 (free) for the RTC. SPI NOR (e.g. 64 Mbit) on SPI1 with a new CS pin |
| G6 Open protocols | **Add**, firmware + docs | |
| G7 Weld / pre-charge fault detection | **Have (HW)** | V_HV_SENSE + pack voltage from the AFE. Firmware only |
| G8 Isolation | **Have** for CAN + RS-485 | Gap: **no isolator between AFE and MCU** (planned ISO7741 missing, owner to decide). The rating claim needs layout creepage (6.5 mm planned) |
| G9 Signed OTA, A/B | **New parts** | External SPI NOR (same part as G5) + bootloader. BLE / WiFi path needs the ESP32 |
| G10 CAN-FD | **Have (partly)** | The G431 FDCAN supports FD. TJA1051T/3 is sold as FD-capable (to verify in the datasheet). instructions.md asked for **dual** CAN-FD; the G431 has only one FDCAN |
| G11 Certification | **Process** | instructions.md already targets IEC 62619 / UL 1973 / ISO 26262 principles. Needs the hardware trip (G1) and a secondary OV path to be credible |
| Secondary OV protection | **New parts** | Independent OV protector IC (e.g. TI BQ77216 class, 3–16S; to verify) driving the same hardware trip |
| Active balancing 1–2 A | **New parts** | Separate board or option SKU. Ours: 110 mA passive. That is above every passive competitor (20–150 mA) but below JK / Daly active |
| RS-232 | **Not needed** | Only for old PC tools (PACE, JBD, JK). RS-485 + USB adapter covers it |
| Board size | **Note** | Ours 160 × 100 mm, smaller than JBD 300 × 100 or Daly 285 × 100, but **without the power switch**. Contactors and the on-board shunt add volume outside the board. ANT 140 × 70 is an EV board |

---

## 5. Recommended "v1 that beats them"

**Positioning:** Daly / JK / Seplos feature parity at the user level (app, LEDs, dry contacts, heater, 16 parallel, protocol library). On top, four things none of them have: an **independent hardware trip**, **contactor + measured pre-charge with weld detection**, **per-cell / per-connection resistance diagnostics**, and **open, published protocols with a deep timestamped log**.

| Priority | Feature | Change | BOM impact (est.) |
|---|---|---|---|
| P0 | Sleep / power latch + wake button (≤ 200 µA target) | latch on LM5164 EN, switched isolated supply, button | +$0.40 est. |
| P0 | SOC LEDs (6) + RUN / ALM | 74HC595 + LEDs + light-pipe footprint | +$0.35 est. |
| P0 | 2 dry contacts | 2 × PhotoMOS / small relay | +$1.00–1.50 est. |
| P0 | Heater driver (~10 A) | 4th low-side driver | +$0.60–1.00 est. |
| P0 | RJ45 ports (CAN+RS-485 inverter port, 2 × parallel) + address scheme | 3 × RJ45, address DIP or auto-address link line | +$1.50–3.00 est. |
| P0 | Hardware trip latch: AFE ALERT + OCP comparator → AND gate in contactor drive | latch + gates (74LVC1G family) | +$0.30 est. |
| P0 | Inverter protocol library (Pylon CAN / RS-485, Growatt, Deye, Victron, SMA, Goodwe, Sofar, Solis, Voltronic, Luxpower) + auto-detect | firmware | $0 |
| P0 | Soft paralleling through the pre-charge path; pre-charge short / timeout; contactor weld detection | firmware (check R_PRE1 power rating) | $0 (maybe a larger R_PRE1) |
| P1 | BLE + WiFi app / cloud-ready | ESP32-C3 module on USART2 | +$2.00–2.50 est. |
| P1 | RTC + deep log + black box + A/B OTA store | 32.768 kHz crystal + 64 Mbit SPI NOR | +$0.55 est. |
| P1 | SOC ±3 % target, SOH with capacity + DCIR, loose-connection detection | firmware; on-board shunt (owner already decided) | shunt already planned: ~$3–6 est. |
| P1 | Published Modbus map + CAN DBC + ESPHome / HA | docs + firmware | $0 |
| P1 | Second isolated RS-485 (inverters that speak RS-485 only) | THVD1450 + isolator | +$2.50–3.50 est. |
| P2 | Secondary OV protector IC on the hardware trip | BQ77216-class part (to verify) | +$1.50–2.50 est. |
| P2 | AFE-to-MCU isolation (owner decision pending) | ISO7741 or equivalent | +$1.50–2.50 est. |
| P2 | Active balancer 1–2 A as an option SKU / add-on header | separate board | +$15–30 est. (option only) |
| Later | CAN-FD pack-to-pack, HV stacking | second CAN needs an MCU with 2 FDCAN (e.g. a larger G4) | MCU change |

**Total for P0 + P1 (est.):** about **+$12–20** per board on top of today's BOM, excluding the shunt (already planned) and the active-balance option.

**Price context (listings):**
* JK PB2A16S20P: $131–167 [S11]
* Seplos 200 A: about $59–176 [S3][S29]
* Daly 4th-gen 100 A: $60–83 [S21]

The contactors and their 12 V coil power are a cost and standby item that the MOSFET boards do not have. They must be in the price comparison.

---

## 6. What could not be verified

* **Tian Power:** no BMS datasheet or product page found; only a pack listing [S23].
* **ANT:** no current (2024–2026) ESS / inverter BMS document; only a 2021 EV-style wiring guide [S22].
* **JBD "SP" home-storage series:** no spec found. The UP16S010 (2023) was used instead.
* **Seplos 10C:** no source found. For the 10E, only listing snippets (pages blocked).
* **Daly 4th gen:** no datasheet; values come from Daly web articles. No accuracy, sleep, log, size or price on the official pages.
* **JK:**
  * cell / current accuracy, balancer topology (capacitor vs inductor), log depth and FW update method
  * V19 vs V24 differences (heater, pre-charge) come from retailer snippets only
* **SOC accuracy** for JK, JBD, PACE, Daly; balancing current for PACE.
* **Fan control:** no product in the set states it.
* **Certifications** of the bare BMS boards (except Daly's "UL at component level" and the 300 A "10E" claim).
* **Pylontech / EG4 / Basen:** only snippets (search summaries); EG4 parallel count conflicts (16 vs 64).
* **Our own parts:** not checked against datasheets in this task:
  * TJA1051T/3 CAN-FD rate
  * STM32G431 bootloader over FDCAN
  * BQ77216 cell range
  * BQ76952 typical (25 °C) accuracy; TI states only ±15 mV max full range [S28]

---

## 7. Sources

| Tag | Source | Level |
|---|---|---|
| S1 | Seplos 16S 200A Smart BMS User Manual V16 (2022-10) – https://cdn.shopify.com/s/files/1/0623/5389/9720/files/SEPLOS_16S_LFP_200A_BMS_SPECIFICATION_V16.pdf | F |
| S2 | Seplos BMS 10E listing / manual – https://manuals.plus/asin/B0CDC3CBWB | S |
| S3 | Fogstar, Seplos 48V 200A BMS listing – https://www.fogstar.co.uk/products/seplos-48v-200a-lifepo4-bms | S |
| S4 | Evlithium 48V 300A 16S BMS, model 48300-3301-10E-EJ01-16S – https://www.evlithium.com/Battery-Management-System/48v-300a-16s-lithium-battery-bms.html | F (page) |
| S5 | JBD-UP16S010-L16S-200A spec sheet A03 (2023-03-24) – https://cdn.shopify.com/s/files/1/0606/5199/5298/files/JBD-UP16S010-L16S-200A-200A-B-U-R-C-A03.pdf | F |
| S6 | lifepo4.com.au, JBD ESS 16S 200A listing – https://lifepo4.com.au/shop/lifepo4-bms/jbd/48v-16s/jbd-ess-smart-bms-16s-48v-200a-lifepo4/ | S |
| S7 | JK-PB2A16S-20P specification V1.01 (2023-10) – https://www.nikom.biz/pic_info/A652007/JK%20-PB2A16S-20P%20Specification.pdf | F |
| S8 | JK PB2A16S20P Specification EN V1.0 (Gobel Power) – https://www.gobelpower.com/download/JKBMS-JK-PB2A16S20P-Specication-EN-V1.0.pdf; also https://www.evlithium.com/Battery-Management-System/16s-200a-pb2a16s20p-lithium-battery-bms.html | S |
| S9 | Gobel Power JK inverter BMS listing (15P) – https://www.gobelpower.com/jk-ess-inverter-bms-16s150a-16s200a-2a-active-balance-bluetooth_p138.html?cPath=14 | S |
| S10 | Wistek JK PB2A16S20P listings (V19 / V24: heating, 2 dry contacts, parallel current limiting, discharge pre-charge) – https://wis-tek.com/products/jk-pb2a16s20p-new-v19-16s-200a-lifepo4-battery-bms-wistek | S (exact page for the V24 text not confirmed) |
| S11 | JK prices: https://www.ebay.com/itm/156788768826 ; https://www.alibaba.co.uk/product-detail/EU-StockJK-BMS-Battery-Management-System_1601829016003.html | S |
| S12 | Wistek, "Can JK BMS communicate with Victron inverters" – https://wis-tek.com/blogs/knowledge/can-jk-bms-communicate-with-victron-inverters | S |
| S13 | JK protocol community: https://github.com/Uksa007/esphome-jk-bms-can ; https://akkudoktor.net/t/neues-jk-bms-2023-inverter-version-protokolle-abgetrennt/18500 | S |
| S14 | PACE BMS 16S LFP home storage spec, P16S100A-PC1447 (2021-12 / 2022-03) – https://www.akkudoktor.net/uploads/short-url/8IIu2OquK38Jt9mmixM5whqkdt1.pdf | F |
| S15 | esphome-pace-bms (syssi) – https://github.com/syssi/esphome-pace-bms | S |
| S16 | Daly, hybrid-inverter compatibility guide – https://www.dalybms.com/news/bms-for-solar-storage-hybrid-inverter-compatibility-guide-for-oem-manufacturers/ | F (page) |
| S17 | Daly, ESS OEM guide (4th gen LK / LM) – https://www.dalybms.com/news/bms-for-energy-storage-system-oem-guide-for-cabinet-integrators-and-home-storage-manufacturers/ | F (page) |
| S18 | Daly, 4th-gen home ESS BMS + IoT cloud (2026-02-27) – https://www.dalybms.com/news/daly-elevates-smart-energy-with-upgraded-4th-gen-home-ess-bms-and-advanced-iot-cloud-platform | F (page) |
| S19 | Daly DL-R16L active-balance home storage BMS spec (2023-08-19) – https://dalybms.com/news/actively-balance-home-storage-bms-product-specification | F (page) |
| S20 | Daly DL-R16A-F16S100ATJ spec (2020-11) – https://cdn.shopify.com/s/files/1/0247/0664/6106/files/DL-R16A-F16S100ATJ-MM00_Product_Specification_Confirmation_1.pdf | F |
| S21 | Daly prices: https://b2usa.com/hotsite/dalybmselectronics/daly-home-energy-storage-bms-16-series-1 ; https://dalyelec.en.alibaba.com/en_US/company_profile.html | S |
| S22 | ANT BMS 16S wiring diagram (2021) – https://srikobatteries.com/wp-content/uploads/2021/11/ANT_BMS_16S_wiring_diagram.pdf | F |
| S23 | Tian Power SmartLi 48V100A (ENF) – https://www.enfsolar.com/pv/storage-system-datasheet/13929 | S |
| S24 | KS48100-Ho21 16S 200A spec for approval A1 (2024-08-08), unbranded – https://forum.mypower.cz/download/file.php?id=53065 | F |
| S25 | Pylontech US5000 datasheet – https://cdn.shopify.com/s/files/1/0809/2316/5014/files/us5000-datasheet.pdf ; residential BESS 2023 – https://portal.segen.co.uk/reseller/docs/2023-Residential-BESS-PY230529-EN.pdf | S |
| S26 | EG4 LifePower4 V2 – https://eg4electronics.com/categories/batteries/lifepower4-48v-v2/ ; manual https://eg4electronics.com/wp-content/uploads/2024/04/EG4-Lifepower4-48V-Manual.pdf | S |
| S27 | Basen Green 48V DIY kits manual – https://basengreen.com/wp-content/uploads/2023/07/BASENGREEN-48V-DIY-KITS_User_Manual.pdf | S |
| S28 | TI BQ76952 datasheet SLUSE13B – https://www.ti.com/document-viewer/BQ76952/datasheet | S |
| S29 | Seplos prices: https://hakadibattery.com/products/seplos-bms-100a-150a-200a-8s-16s-24v-48v-can-rs485-lifepo4-sodium-ion-battery-protection-board ; Accio listing (search summary) | S |
| S30 | Seplos 2A active balance board spec – https://cdn.shopify.com/s/files/1/1347/0997/files/SEPLOS_2A_Active_Balance_Board_Specification_1.pdf | S |

Text extracts of the [F] PDFs: `pdf\` (untrusted source text, kept as evidence).
