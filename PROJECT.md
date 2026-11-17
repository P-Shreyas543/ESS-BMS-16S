# PROJECT.md — Automotive-Grade ESS BMS

Project-specific facts, conventions and the decisions log for this board.
The generic way of working (setup, workflow, house standards, checks) is in **`instruction.md`**. Read that first, then this file.
Where this file and `instruction.md` disagree, **this file wins** for this project.

Written 2026-11-16 by an inventory pass (playbook section 2). Every number below was measured that day with a script or `kicad-cli` 10.0.7 on the files as they are on disk (uncommitted work included), or is quoted from a project file that is named. Nothing here was verified against a datasheet or a distributor page. Items that could not be established are in section 8.

---

## 1. Project facts

| Item | Value |
|---|---|
| Product | Battery management system for 7S–16S LFP / NMC energy-storage packs, 16–72 V pack input (root title block; `instructions.md` §1–2; `system_architecture_master_plan.md` §1) |
| Company / title block | `NextGen Automotive Energy Storage Solutions`, rev `v1.0`, date `2026-10-27` on all 7 sheets; 4 comment lines per sheet (several are stale, section 4) |
| KiCad | 10.0. Schematic file format `version 20260101`, board `version 20260206`. `kicad-cli` 10.0.7 reads both without converting |
| Root sheet | `Automotive_ESS_BMS.kicad_sch`: 6 sheet symbols (50.8 x 50.8 mm, no sheet pins), 2 text blocks, no parts |
| Project symbol library | `symbols/Automotive_ESS_BMS.kicad_sym` (nickname `Automotive_ESS_BMS`) — **empty**, no symbol in it |
| Project footprints / 3D | `footprints.pretty/` holds one footprint, `R_Shunt_CSS2H-5930` (generator `antigravity`), **not used** on the board. `3d_models/` is empty |
| Lib tables | `sym-lib-table`, `fp-lib-table`: one project library each, `${KIPRJMOD}` paths, both exist. Every part uses a stock KiCad library (`Device` 193 of 224 parts) |
| Datasheets | no `datasheets/` folder |
| Fab / assembly | JLCPCB, 4-layer JLC04161H-7628, 1.6 mm (recorded in `instructions.md` §4 and `plan_pcb_manufacturing.md` §1) |
| Paper | A3 on all 7 sheets (sheet 02 moved from A2 to A3 on 2026-11-17) |
| Project text size | default 50 mil (1.27 mm) in `.kicad_pro` |
| Folder layout | everything in the root: KiCad files, 9 plan / architecture `.md` files, about 55 ERC / DRC reports, 21 test-board files, `scripts/` (228 Python files), `fabrication/` (2026-10-27 outputs). See section 9 |
| Location | the repository root (docs use relative paths only) |
| Git | the folder is a repo, branch `main`, **no remote**, **one commit** (`95686f8`, 2026-11-02 10:00, "Baseline before rework"). Everything after it is uncommitted: all 6 sub-sheets, the board, `.kicad_pro`, the `.net`, the BOM csv, plus 72 untracked files (`scripts/` is untracked). Commit only when the owner asks |

### 1.1 Sheets and reference ranges

References are **name-based** (`R_VC0`, `Q_BL1`, `U_AFE1`); only the Power Supply sheet uses plain numbers. There are no numeric ranges per sheet.

| Page | Sheet | File | Parts | References | Status |
|---|---|---|---|---|---|
| 1 | Root | `Automotive_ESS_BMS.kicad_sch` | 0 | – | sheet symbols only |
| 2 | Power_Supply | `01_Power_Supply.kicad_sch` | 42 | C1-C16, C_FF1, D1-D8, F1, J1-J2, L1-L2, R1-R7, R_PG1, U1-U4 | **redrawn 2026-11-17** to the playbook style (wires, power symbols, 6 boxes); netlist identical; waiting for owner review (`AGENT_TASKS.md` Task 1) |
| 3 | AFE_Cell_Monitor | `02_AFE_Cell_Monitor.kicad_sch` | 89 | U_AFE1, J_CELL1, R_VC0-16, C_DF1-16, R_BL1-16, Q_BL1-16, J_NTC1-4, D_ESD_NTC1-4, C_NTC1-4, RT_BOARD, C_TS_PCB, C_BAT1, C_CP1, C_R1, C_R18, D_BAT1, R_RST1, R_SCL1, R_SDA1 | **redrawn 2026-11-17** to the sheet-01 style (wires, power symbols, boxes, A3); netlist identical; waiting for owner review |
| 4 | MCU_Control | `03_MCU_Control.kicad_sch` | 25 | U_MCU1, U_WDOG1, U_MEM1, Y1, C_X1-2, C_VDD1-3, C_A1-2, C_MEM1, C_RST2, FB1, SW_CFG1, R_SW1-4, R_CS1, R_RST2, R_BOOT0, R_HB1, D_HB1, J_SWD1 | **redrawn 2026-11-17** to the sheet-01 style (wires, power symbols, boxes, A3); netlist identical; waiting for owner review |
| 5 | Current_Sensing | `04_Current_Sensing.kicad_sch` | 19 | U_ISENSE1, U_OCP1, J_KELVIN1, R_NT1, R_K1-2, C_K1-3, C_AMP1-2, C_CMP1, R_TH1-2, C_TH1, R_OCP_PU1, R_OCP_LED1, D_OCP1, D_TVS_SHUNT1 | **redrawn 2026-11-17** to the sheet-01 style (wires, power symbols, boxes, A3); netlist identical; waiting for owner review |
| 6 | Power_Actuators | `05_Power_Actuators.kicad_sch` | 28 | Q_POS1, Q_NEG1, Q_PRE1, R_G1-3, R_GS1-3, D_Z_POS1 / NEG1 / PRE1, D_FLY1-3, D_LED_P1 / N1 / R1, R_LED_P1 / N1 / R1, J_CONT1, J_PRE1, R_PRE1, R_HV1-2, R_HV_BOT1, C_HV1 | **redrawn 2026-11-17** to the sheet-01 style (wires, power symbols, boxes, A3); netlist identical; waiting for owner review |
| 7 | Communications | `06_Communications.kicad_sch` | 21 | U_ISO_CAN1, U_ISO_485A, U_ISO_485B, U_CAN1, U_485_1, J_CAN1, J_485_1, D_TVS_CAN1, D_TVS_485_1, R_TRM1-2, C_TRM1, R_TRM_485, R_FS_A1, R_FS_B1, C_CAN1-2, C_485_1, C_ISO_C1-2, C_ISO_485 | **redrawn 2026-11-17** to the sheet-01 style (wires, power symbols, boxes, A3); netlist identical; waiting for owner review |

Total **224 parts, 165 nets** (141 named + 24 `unconnected-…` single-pin nets), 665 nodes. No DNP part, no `in_bom no` part, no test point, no multi-unit symbol.
The page numbers above are the ones stored in the root sheet instances. The plotted title blocks show `Id` 2, 4, 6, 3, 5, 7 for the six sub-sheets in file order, and the comment-4 text of each sheet says "Sheet 2/7 … 7/7" in file order.

### 1.2 Architecture (one line per block, as netlisted 2026-11-16)

* **Pack input:** J1 (2-pin 5.08 mm terminal) `V_BATT+` / `GND_PWR` → F1 → `NET_FUSE` → D1 TVS to `GND_PWR` → D2 series Schottky → `V_IN_BUCK`.
* **+12V:** U1 LM5164 buck from `V_IN_BUCK` (EN/UVLO tied to VIN, L1, feedback R2 / R3 + C_FF1, PGOOD pulled up by R_PG1) → `+12V`. J2 (2-pin header) `V_AUX_12V` → D3 → `+12V` (bench input).
* **+5V:** U2 LMR16006Y buck from `+12V` (L2, D5; FB pin on `+5V`) → `+5V`.
* **+3V3:** U3 AP2112K-3.3 from `+5V` → `+3V3`. `+3V3_A` = `+3V3` through FB1 (MCU VDDA and VREF+ only).
* **+5V_ISO:** U4 isolated module from `+5V` / `GND_PWR` → `+5V_ISO` / `GND_ISO`. LEDs D4, D6, D7, D8 on the four rails.
* **AFE:** U_AFE1 BQ76952 on `V_BAT_FILT` (`V_BATT+` through D_BAT1, C_BAT1). J_CELL1 (1x17) `CELL_0..16` → R_VC0-16 → `VC0..16` with C_DF1-16 between adjacent taps. Balancing: R_BL1-16 (33 R 2512) + Q_BL1-16; each FET has drain `NET_BALn`, **gate on `VC(n-1)`**, source `CELL_(n-1)` (section 8, question 6). NTC: J_NTC1-4 → TS1, TS2, TS3, DCHG pin; on-board RT_BOARD → DDSG pin. `SH_P` / `SH_N` on SRP / SRN. I2C `AFE_SCL` / `AFE_SDA` (4k7 pull-ups to `+3V3`), `AFE_ALERT`, `AFE_RST` go **straight to the MCU** — there is no isolator between AFE and MCU on the schematic.
* **MCU:** U_MCU1 STM32G431CBT6 LQFP-48, 8 MHz crystal Y1, SWD header J_SWD1, watchdog / supervisor U_WDOG1 TPS3823-33 (WDI from PB0, RESET on NRST), SPI EEPROM U_MEM1 25LC256, 4-way DIP switch SW_CFG1 (`CFG_CHEM`, `CFG_CELL_0..2`, 10k resistors R_SW1-4), heartbeat LED on PC13.
* **Current sense:** external shunt through J_KELVIN1 (`SH_P` / `SH_N`; no shunt on the board) → R_K1 / R_K2 10 R + C_K1-3 → U_ISENSE1 INA240A2 (REF1 `+3V3`, REF2 `GND_PWR`, supply `+5V`) → `ADC_I_SENSE` → MCU PA0 and comparator U_OCP1 TLV3501 (threshold `V_TH_OCP` from R_TH1 / R_TH2) → `OCP_TRIP_N` → MCU PA8 + LED D_OCP1. R_NT1 0 R ties `SH_P` to `GND_PWR`. `OCP_TRIP_N` reaches only the MCU and the LED.
* **Actuators:** Q_POS1 / Q_NEG1 / Q_PRE1 low-side N-MOSFETs (gate R 100 R, 47k gate-source, 18 V zener, flyback diode to `+12V`, LED) switch `COIL_POS-` / `COIL_NEG-` / `COIL_PRE-` on J_CONT1 (6-pin terminal, three `+12V` pins). J_PRE1 (4-pin terminal): `V_BATT+`, `NET_PRE_IN`, `V_INVERTER_BUS`, `GND_PWR`; R_PRE1 between `NET_PRE_IN` and `V_INVERTER_BUS`. Bus-voltage divider R_HV1 + R_HV2 / R_HV_BOT1 + C_HV1 → `V_HV_SENSE` → MCU PA1.
* **Communications (isolated side on `+5V_ISO` / `GND_ISO`):** U_ISO_CAN1 ISO7721 → U_CAN1 TJA1051T/3 → `NET_CANH` / `NET_CANL`, split termination R_TRM1 / R_TRM2 + C_TRM1, D_TVS_CAN1, J_CAN1. U_ISO_485A (TX / RX) + U_ISO_485B (DIR) ISO7721 → U_485_1 (half duplex, DE and RE joined) → `RS485_A` / `RS485_B`, R_TRM_485 120 R, bias R_FS_A1 / R_FS_B1 560 R, D_TVS_485_1, J_485_1. J_CAN1 and J_485_1 are 1x4 2.54 mm headers: bus pair, `GND_ISO`, `+5V_ISO`.

**MCU pin map (netlist):** PA0 ADC_I_SENSE · PA1 V_HV_SENSE · PA2 CTRL_CONT_POS · PA3 CTRL_CONT_NEG · PA4 CTRL_PRECHARGE · PA5 / PA6 / PA7 SPI1 SCK / MISO / MOSI · PA8 OCP_TRIP_N · PA9 / PA10 RS485_TX / RX · PA11 / PA12 CAN_RX / TX · PA13 / PA14 SWDIO / SWCLK · PB0 MCU_WDOG_WDI · PB1 SPI1_CS_MEM · PB2 RS485_DIR · PB6 AFE_SCL · **PB7 and PB9 both AFE_SDA** · PB8 MCU_BOOT0 (R_BOOT0) · PB10 AFE_ALERT · PB11 AFE_RST · PB12 CFG_CHEM · PB13-15 CFG_CELL_0..2 · PC13 MCU_HEARTBEAT · PF0 / PF1 crystal · PG10 MCU_RESET_N · unconnected: PA15, PB3, PB4, PB5, PC14, PC15.

---

## 2. Nets, power symbols, domains

### 2.1 Rails and grounds
There are **no power symbols** in this project. Every rail and ground is a **global label**; the only `power:` symbols are 7 `PWR_FLAG`s.

| Net | Nodes | Source | PWR_FLAG |
|---|---|---|---|
| `GND_PWR` | 100 | battery / logic ground (one ground for pack, AFE, MCU, drivers) | `#PWR2` (sheet 2) |
| `GND_ISO` | 21 | U4 −VOUT, isolated comms ground | none |
| `V_BATT+` | 4 | J1 pin 1 | `#PWR1` |
| `V_IN_BUCK` | 6 | after F1 / D2 | `#PWR3` |
| `+12V` | 21 | U1 through L1 | `#PWR4` |
| `+5V` | 13 | U2 through L2 | `#PWR5` |
| `+3V3` | 39 | U3 VOUT | none |
| `+3V3_A` | 5 | `+3V3` through FB1 | `#PWR100` (sheet 4) |
| `+5V_ISO` | 16 | U4 +VOUT | none |
| `V_BAT_FILT` | 4 | `V_BATT+` through D_BAT1 | `#PWR_BAT` (sheet 3) |
| `V_AUX_12V` | 2 | J2 pin 1 | none |
| `V_INVERTER_BUS` | 3 | J_PRE1 pin 3 | none |

Other named groups: `CELL_0..16`, `VC0..16`, `NET_BAL1..16`, `NTC_TS1..4`, `NTC_TS_PCB`, `SH_P` / `SH_N`, `AMP_IN+` / `AMP_IN-`, `COIL_POS-` / `COIL_NEG-` / `COIL_PRE-`, `CTRL_CONT_POS` / `CTRL_CONT_NEG` / `CTRL_PRECHARGE`, `CAN_TX` / `CAN_RX` (+ `_ISO`), `RS485_TX` / `RX` / `DIR` (+ `_ISO`), `NET_CANH` / `NET_CANL`, `RS485_A` / `RS485_B`.
Sheets are joined only by global labels: 644 label instances, no hierarchical label, no sheet pin, no local label.

### 2.2 Domains that must NEVER be merged
* `GND_ISO` / `+5V_ISO` (external CAN and RS-485 side, behind U4 and the ISO7721 isolators) vs `GND_PWR` and the non-isolated rails. This is the only isolation barrier on the schematic. The plans ask for at least 2.5 kVrms and a milled slot under the isolators (`plan_isolated_comms.md` §1, `plan_pcb_manufacturing.md` §2).
* Keep `SH_P` / `SH_N` and `AMP_IN+` / `AMP_IN-` as a Kelvin pair; `SH_P` meets `GND_PWR` only at R_NT1.
* `system_architecture_master_plan.md` §3 and `plan_powerstage.md` §5 also name a separate analog logic ground `GND`. It does not exist in the schematic (section 8, question 5).

### 2.3 Facts measured in this project (2026-11-16)
* **No wire, junction or bus exists on any sheet.** Every pin carries its own global label. Any edit that moves a symbol must move its labels with it.
* `Device:Q_NMOS` is used for all 19 MOSFETs with pin **numbers `D`, `G`, `S`**; the footprint `Package_TO_SOT_SMD:SOT-23` has pads 1, 2, 3. The netlist therefore gives these transistors no pad nets (114 parity errors, section 2.5). `scripts/sync_q_pins.py` patched the board for this on 2026-11-02.
* `Automotive_ESS_BMS.net` in the root has the same connectivity as a fresh export (`netcmp.py`: `connectivity identical: True`). Command: `kicad-cli sch export netlist --format kicadsexpr -o <out>.net Automotive_ESS_BMS.kicad_sch` (2026-11-16, kicad-cli 10.0.7; output written outside the project and not kept). To compare a later state, export again and run `python tools/schematic/netcmp.py Automotive_ESS_BMS.net <new>.net`.
* `kicad-cli` prints "schematic has annotation errors, please use the schematic editor to fix them" on every export. The cause was not established; the references without a trailing number are RT_BOARD, C_TS_PCB, U_ISO_485A, U_ISO_485B.
* No net class has a net assigned: `.kicad_pro` defines 6 classes but `netclass_patterns` is empty, so every net is in `Default` (0.2 mm track, 0.15 mm clearance).

### 2.4 Known ERC state (measured 2026-11-16)
Command (2026-11-16, kicad-cli 10.0.7): `kicad-cli sch erc --severity-all --format json -o <out>.json Automotive_ESS_BMS.kicad_sch`. Result: **0 errors, 0 warnings, 0 exclusions on all 7 sheets** ("Found 0 violations"). The report file was written outside the project and not kept; these numbers are the record.
Four checks are switched to `ignore` in `.kicad_pro`: `single_global_label`, `four_way_junction`, `simulation_model_issue`, `footprint_filter`. With a label-only schematic the first one hides one-ended nets.
ERC cannot see the transistor pin problem of 2.3 or a wrong label name. Treat "0 errors" as "labels are consistent", not as "circuit checked".

### 2.5 Known DRC state (measured 2026-11-16, zones not refilled)
Command (2026-11-16, kicad-cli 10.0.7): `kicad-cli pcb drc --severity-all --schematic-parity --format json -o <out>.json Automotive_ESS_BMS.kicad_pcb` (no `--refill-zones`, board not saved). Output: "Found 344 violations, 240 unconnected items, 339 schematic parity issues". The report file was written outside the project and not kept; the table is the record.

| Group | Count | By type |
|---|---|---|
| Violations | 344 (47 errors, 297 warnings) | errors: 33 `clearance`, 8 `tracks_crossing`, 3 `shorting_items` (`+3V3` to `GND_PWR` at R_SDA1 pad 1), 2 `solder_mask_bridge`, 1 `hole_clearance`. Warnings: 175 `via_dangling`, 96 `silk_overlap`, 22 `silk_over_copper`, 2 `hole_to_hole`, 1 `track_dangling` (`+12V` on In2.Cu, 55 mm), 1 `lib_footprint_mismatch` (U1) |
| Unconnected | 240 | 39 nets. 190 are on zone nets (`GND_PWR` 96, `+3V3` 38, `+12V` 21, `GND_ISO` 20, `+5V_ISO` 15): the board file stores no filled zone copper and the run did not refill |
| Schematic parity | 339 | 199 `footprint_symbol_field_mismatch` (field `LCSC` missing in the footprint), 114 `net_conflict` (the 19 MOSFETs, 6 each), 19 `footprint_symbol_mismatch` (values of D1, R1, R_VC0-16: the board still has the older values), 7 `extra_footprint` (MH1-4, FID1-3) |

Five DRC checks are `ignore` in `.kicad_pro`: `missing_courtyard`, `track_not_centered_on_via`, `tuning_profile_track_geometries`, `footprint_filters_mismatch`, `footprint_type_mismatch`. No exclusions are stored.

---

## 3. Parts (as found in the fields — NOT verified live)

Fields on every part, in this order: `Reference`, `Value`, `Footprint`, `Datasheet`, `Description`, `LCSC`, `Manufacturer`, `MPN`. The LCSC field name is exactly `LCSC` and is filled on all 224 parts. `Manufacturer` and `MPN` are missing on 4 parts (RT_BOARD, C_TS_PCB, R_BOOT0, R_NT1). There is no `Spec` field. `Datasheet` is empty on 199 parts and a manufacturer PDF link on 25 (none is a JLC part page). 85 different LCSC numbers.

| Ref | Value | MPN (field) | LCSC (field) | Footprint |
|---|---|---|---|---|
| U1 | LM5164-Q1 | LM5164QDDARQ1 | C444643 | HSOP-8-1EP 3.9x4.9 ThermalVias |
| U2 | LMR16006YQ5 | LMR16006YQ5DDCRQ1 | C86381 | SOT-23-6 |
| U3 | AP2112K-3.3 | AP2112K-3.3TRG1 | C352467 | SOT-23-5 |
| U4 | B0505S-1WR3 | B0505S-1WR3 (Mornsun) | C265225 | symbol `CRE1S0505SC`, footprint `Converter_DCDC_Murata_CRE1xxxxxxSC_THT` |
| U_AFE1 | BQ76952-Q1 | BQ7695202PFBR | C2687103 | TQFP-48 7x7 |
| U_MCU1 | STM32G431CBT6 | STM32G431CBT6 | C529329 | LQFP-48 7x7 |
| U_WDOG1 | TPS3823-33DBVR | TPS3823-33DBVR | C80145 | SOT-23-5 |
| U_MEM1 | 25LC256-I/SN | 25LC256-I/SN | C5426 | SOIC-8 |
| U_ISENSE1 | INA240A2-Q1 | INA240A2QDRQ1 | C205934 | SOIC-8 |
| U_OCP1 | TLV3501AIDBVR | TLV3501AIDBVR | C131010 | SOT-23-6 |
| U_ISO_CAN1, U_ISO_485A, U_ISO_485B | ISO7721-Q1 | ISO7721QDRQ1 | C129202 | SOIC-8 |
| U_CAN1 | TJA1051T/3 | TJA1051T/3,118 | C385473 | SOIC-8 |
| U_485_1 | THVD1450DR | THVD1450DR | C395353 | SOIC-8, symbol `Interface_UART:SN65HVD11HD` |
| Q_BL1-16 | AO3400A (30V 5A) | AO3400A | C85073 | SOT-23 |
| Q_POS1, Q_NEG1, Q_PRE1 | SQ2318EY (40V 8A) | SQ2318EY-T1_GE3 | C148416 | SOT-23 |
| D1 | SMCJ64A | SMCJ64A (MDD) | C284346 | D_SMC |
| D2 | SS310 (100V 3A) | SS310 | C8678 | D_SMB |
| D3, D_FLY1-3 | SS34 (40V 3A) | SS34 | C8679 | D_SMB |
| D5 | SS14 | SS14 | C8675 | D_SMA |
| D_BAT1 | SS110 (100V 1A) | SS110 | C8677 | D_SMA |
| D_Z_POS1 / NEG1 / PRE1 | BZX84-C18 | BZX84-C18,215 | C2194 | D_SOD-323 |
| D_TVS_SHUNT1 | SMAJ5.0CA | SMAJ5.0CA | C8063 | D_SMA |
| D_ESD_NTC1-4 | ESD5V0D3B | ESD5V0D3B | C84296 | D_SOD-323 |
| D_TVS_CAN1 | NUP2105LT1G | NUP2105LT1G | C12948 | SOT-23 |
| D_TVS_485_1 | SM712 | SM712-02HTG | C19002 | SOT-23 |
| F1 | 2.5A 125V | 046602.5NR | C2891395 | Fuse 1206 |
| L1 / L2 | 47uH 1.8A / 10uH 1.5A | SWPA8040S470MT / SWPA8040S100MT | C408332 / C344383 | L_Sunlord_SWPA8040S |
| Y1 | 8.000MHz | X32258MOB4SI | C115962 | Crystal 3225 4-pin |
| FB1 | 600R @ 100MHz | CBG201209U601T | C1015 | `Resistor_SMD:R_0805` |
| SW_CFG1 | 4-way DIP | CHS-04B | C318884 | Copal CHS-04B |
| R_PRE1 | 50R 25W 5% | PWR263S-20-50R0J | C463124 | TO-263-2 |
| R_BL1-16 | 33R 1W 1% | 25121WF330JT4E | C17936 | R 2512 |
| J1 / J_CONT1 / J_PRE1 | terminals | MKDS 1,5/ 2- / 6- / 4-5,08 | C462688 / C462691 / C462689 | Phoenix MKDS 5.08 mm |
| J_CELL1 | 1x17 header | 2.54-1x17P | C224359 | PinHeader 1x17 2.54 mm |
| J_SWD1 | 2x5 1.27 mm | 20021111-00010T4LF | C2932845 | PinHeader 2x05 1.27 mm SMD |

**Field mismatches seen while listing (a script compared value / MPN / footprint text; nothing was looked up):**
* R1 value `2.4M`, MPN `RC0603FR-07100KL`. R_VC0-16 value `100R 1%`, MPN `RC0603FR-071KL`. C_FF1 `47pF`, MPN `CC0603KRX7R9BB103`. R_HV_BOT1 `20.0k 0.1%`, MPN `RC0603FR-0720KL`.
* One MPN `CC0603KRX7R9BB104` carries three LCSC numbers (C14663, C14664, C14666, by voltage text). `CL10A475KP8NNNC` is on a 0603 part (C12) and on 0805 parts (C14, C_CAN2). `CL21B106KOQNNNE` is on C8 `10uF 25V` and C15 `10uF 16V`.
* J_KELVIN1: MPN `MKDS 1,5/ 2-5,08` (terminal) with a 2.54 mm pin-header footprint and LCSC C224345 (the pin-header number used on J2 and J_NTC1-4).
* D_Z_*: MPN `BZX84-C18,215` on a SOD-323 footprint. FB1 on a resistor footprint. U4: Mornsun part on a Murata CRE1 symbol and footprint. U_485_1: THVD1450 on the SN65HVD11HD symbol.
* X5R capacitors by MPN (`CL..A…`): C4, C9, C12, C14, C_R1, C_R18, C_CAN2.
* The 2026-11-02 rework changed many LCSC numbers (`scripts/fix_all_bom_lcsc.py`, `fix_remaining_bom.py`, `check_fake_lcsc.py`); the numbers in several plan files are the older ones.

No custom symbol or footprint is in use. Per playbook rule 0.5, every number above needs a live check before it is ordered or copied.

---

## 4. Project-specific style notes (as observed 2026-11-16)

This is what the sheets look like today. It is **not** the playbook house style; the owner decides whether to convert (section 8, question 2).
* Label-only drawing: no wires, no junctions, a global label on every pin; rails and grounds as global labels, no power symbols.
* No boxes. Each sheet has 4–6 blue note blocks titled `SECTION n: …` (1.5 mm text; root 1.8 / 2.0 mm). Fields and labels are 1.27 mm.
* Parts sit in the top-left third of the page; the rest is empty. Fields are auto-placed: Reference and Value overlap each other, labels and pins on most two-pin parts. Notes overlap parts on all six sub-sheets. On the root, a note overlaps the lower sheet symbols.
* Name-based references (section 1.1).
* **Stale text:** sheet 2 title block and notes say LMR14006, TPS7A2533, L1 100 uH, L2 22 uH, D5 B2100A, F1 3 A, D1 SMCJ75A, CMC1, all LEDs green; the parts are LMR16006YQ5, AP2112K-3.3, 47 uH, 10 uH, SS14, 2.5 A, SMCJ64A, no choke, blue / yellow / green / orange. Sheet 3 notes say "SQ2318EY dual N-MOSFETs controlled by BQ76952 internal gate logic" (parts: AO3400A, gates on VCn) and "active balancing" in the title (circuit is passive). Sheet 5 notes name R_SHUNT1 (not on the sheet) and a 2.90 V / 250 A trip. Sheet 6 notes say R_PRE1 47 R, S3M flyback diodes, R_HV_BOT1 68k, ratio 30.4 : 1; the fields say 50 R, SS34, 20.0k. Sheet 7 comment 3 says SN65HVD11HD; the value is THVD1450DR.

---

## 5. Decisions log

**Reconstructed from project files; owner to confirm.** No row below is a confirmed owner decision. "Recorded in" names the file that states it. Where the schematic differs from the plan, the last column says so.

| Date | Decision | Recorded in | Schematic today |
|---|---|---|---|
| 2026-10-26 | Product: low-cost automotive-grade BMS for stationary ESS, AEC-Q parts, JLCPCB fab and assembly, 4-layer board | `instructions.md` §1 | – |
| 2026-10-26 | Base pack 16S LFP 40.0–58.4 V; ±1.5 mV cell accuracy; 4–8 NTC inputs; shunt current sense ±200 A continuous, 500 A peak | `instructions.md` §2.1 | – |
| 2026-10-26 | Hierarchy: root + 6 sub-sheets `01`–`06`; project-local libraries through `${KIPRJMOD}` | `instructions.md` §5 | as built |
| 2026-10-26 | JLCPCB rules and 6 net classes (Default, Power_HV, Power_LV, Balance_Lines, CAN_Bus, Current_Sense) | `instructions.md` §4.2–4.3 | rules and classes are in `.kicad_pro` (class name `Current_Sense_Kelvin`); no net is assigned to a class |
| 2026-10-26 | Scope 7S–16S, LFP and NMC, pack 16–72 V | `system_architecture_master_plan.md` §1, `plan_powerstage.md` §3 | title blocks agree |
| 2026-10-26 | Rails `+12V` (contactors), `+5V`, `+3V3`, `+5V_ISO`; buck for 12 V → 5 V instead of an LDO (2.1 W vs about 0.12 W) | `plan_powerstage.md` §1–3 | as built |
| 2026-10-26 | Stage 1 = LM5164-Q1, 12.1 V from 90.9k / 10.0k; Stage 2 = LMR36506-Q1 / MP2315 / TPS62933; Stage 3 = AP2112K-3.3 (or TPS7A25); Stage 4 = B0505S-1WR3 or SN6505B | `plan_powerstage.md` §3–4 | U2 is LMR16006YQ5; L1 47 uH; others as planned |
| 2026-10-26 | Input protection: fuse 2.5 A, SMCJ75A TVS, SS310 reverse diode, 12 V auxiliary bench input | `plan_powerstage.md` Stage 0 | D1 is SMCJ64A; rest as planned |
| 2026-10-26 | AFE = BQ76952-Q1; 1.00k + 100 nF differential + 10 nF common-mode cell filter; external SOT-23 FET + 33 R 2512 balancing at about 100 mA; 4 pack NTC + 1 PCB NTC; ISO7741-Q1 isolator to the MCU | `plan_afe_cell_monitor.md` §1, §3 | R_VC = 100 R; no common-mode capacitors; **no ISO7741**; FET gates on VCn |
| 2026-10-26 | MCU = NXP S32K144 or ST STM32G4, LQFP-64; external window watchdog TPS3851-Q1; 25LC256 or FRAM; 4-way DIP switch for chemistry and cell count; 8 MHz crystal; 10-pin SWD | `plan_mcu_safety.md` §1–4 | STM32G431CBT6 LQFP-48; watchdog TPS3823-33; 25LC256 |
| 2026-10-26 | Current sense: 100 µΩ 5930 shunt on the board, INA240A2-Q1 gain 50 with 1.65 V reference, TLV3201-Q1 comparator at 3.15 V (500 A), latch that removes contactor gate drive in under 2 µs | `plan_current_sensing.md` §2–3 | external shunt through J_KELVIN1; TLV3501; no latch, `OCP_TRIP_N` goes to the MCU and an LED only |
| 2026-10-26 | Actuators: three low-side drivers (SQ2318EY), 50 R pre-charge, 100 : 1 bus divider (1M + 1M / 20k), PWM economiser in firmware, 6-pin 5.08 mm terminal | `plan_power_actuators.md` §2–4 | as built by field values (notes differ, section 4) |
| 2026-10-26 | Comms: isolated CAN-FD (TCAN1042V-Q1 + ISO7721-Q1 + common-mode choke + NUP2105L, split termination 2 x 60.4 R + 4.7 nF) and isolated RS-485 (THVD1429-Q1, 560 R bias, SM712), at least 2.5 kVrms | `plan_isolated_comms.md` §1–2 | TJA1051T/3, THVD1450DR, no choke; rest as planned |
| 2026-10-27 | Board 160 x 100 mm, 1.6 mm, ENIG, JLC04161H-7628; In1 = ground, In2 = power; balance resistors on the bottom side; 1.5 mm milled slot under the isolators; 6.5 mm creepage across the barrier | `plan_pcb_manufacturing.md` §1–3 | outline and slots present (section 6) |
| 2026-10-27 | TVS / ESD part on every external port (CAN, RS-485, NTC, shunt input, contactor gates, battery input) | `system_architecture_master_plan.md` §7, `plan_pcb_manufacturing.md` §5 | parts are on the sheets |
| 2026-10-27 | Fabrication package generated ("0 ERC, 0 DRC errors", 221 components, 94 BOM rows) | `plan_pcb_manufacturing.md` §4, `fabrication/` (dated 2026-10-27) | outputs predate the rework and do not match the current files |
| 2026-11-02 | Git baseline commit `95686f8` "Baseline before rework" | `git log` | – |
| 2026-11-02 | Schematic rework by scripts (uncommitted): LCSC numbers replaced on most parts; R_SHUNT1 + J_SHUNT1 removed, J_KELVIN1 + R_NT1 added; C_SS1 → C_FF1; RT_BOARD, C_TS_PCB, R_BOOT0 added; 3 no-connect flags removed on the MCU sheet | `scripts/apply_sheet1..6.py`, `fix_sheet1..5.py`, `fix_all_bom_lcsc.py`; diff of the sheets against `95686f8` | current state |
| 2026-11-02 | Board: netlist re-sync, placement fixes, zones on 4 layers, slots, several scripted autorouting attempts; the result was saved into the main board file at 13:53 | `scripts/` (section 7), `drc_*.rpt`, `test_*.kicad_pcb` | section 6 |
| 2026-11-04 | `instruction.md` overwritten with an instruction file that did not belong to this project (it described another board) | file mtime, diff against `95686f8` | replaced 2026-11-16, next row |
| 2026-11-16 | Tracking set-up: `instruction.md` = the generic, project-independent hardware playbook, `PROJECT.md`, `DESIGN_NOTES.md`, `tools/` added. The original BMS runbook stays in `instructions.md` (identical to `instruction.md` of commit `95686f8`). No KiCad file touched | this file | – |
| 2026-11-16 | **OWNER (confirmed):** the **schematic as drawn is the design to complete** (parts already on the six sheets stay, e.g. STM32G431CBT6); the plan files are background only. Planned functions that are not on the schematic (AFE-to-MCU isolator, hardware trip latch, CAN choke ...) are listed for the owner, not added | owner answer, section 8 question 1 | – |
| 2026-11-16 | **OWNER (confirmed):** **redraw the six sheets to the playbook style** (`instruction.md` section 7): wires instead of label-only, power symbols, boxed blocks, short notes; one sheet at a time, netlist proven unchanged after each | owner answer, section 8 question 3 | label-only today |
| 2026-11-16 | **OWNER (confirmed):** **PCB: restart the layout later.** Finish and verify the schematic first; the current board file is not edited until then and is kept as the backup | owner answer, section 8 question 4 | section 6 |
| 2026-11-16 | **OWNER (confirmed):** git checkpoint before the rework: branch `rework-2026-11`, commit `d3d356e` (sheets, board, project file, BOM and the tracking files as of this date). Work continues on that branch; no push (no remote) | `git log` | – |
| 2026-11-16 | **OWNER:** the work on this project is carried out by the Antigravity agent, following `instruction.md`, this file and the task queue in `AGENT_TASKS.md`; a second agent reviews each finished task (netlist, ERC, renders) and writes the next task there | owner instruction | – |

| 2026-11-17 | **OWNER (confirmed):** run the redraw with subagents as **pilot, then parallel**: sheet 01 (Task 1) is redrawn first and reviewed by the owner; after the owner's OK the other five sheets are redrawn in parallel in the same style. A read-only requirements check of all six sheets against `instructions.md` runs alongside the pilot | owner answer 2026-11-17 | – |
| 2026-11-17 | **OWNER (confirmed):** requirements gaps (e.g. no AFE-to-MCU isolator, no hardware OCP latch) are **reported only** (evidence, severity, options). No circuit change until the owner decides each one | owner answer 2026-11-17 | – |
| 2026-11-17 | Sheet 01 `01_Power_Supply.kicad_sch` redrawn by script (Task 1, pilot): wires instead of label-only; rails `+12V` `+5V` `+3V3` as stock power symbols, `GND_PWR` `GND_ISO` `+5V_ISO` `V_BATT+` as new project power symbols in `symbols/Automotive_ESS_BMS.kicad_sym` (pins `power_in`); one global label kept per internal net; 6 dashed boxes; text 0.8 / 1.0 mm; stale notes, title and title-block comments replaced (old text archived in `DESIGN_NOTES.md`). No part, value, field or net changed: netcmp identical, 165 net names identical, ERC 0 / 0. Not an owner decision; style waits for owner review | `AGENT_TASKS.md` Task 1 report | redrawn |

| 2026-11-17 | **OWNER (confirmed):** sheet 01 redraw style accepted ("yes plz go ahead"); redraw sheets 02–06 now, in parallel, in the sheet-01 style, connectivity unchanged. Circuit blockers from the requirements review are fixed afterwards, each after an owner decision | owner answer 2026-11-17 | – |
| 2026-11-17 | Sheets 02–06 redrawn by five parallel subagents in scratch, merged and installed by the coordinator (`AGENT_TASKS.md` Tasks 2–6 + merge report). New project power symbol `+3V3_A`. Power-symbol references by sheet range (`#PWR2xx`…`#PWR6xx`). Netlist identical, 165 net names, ERC 0. **Not an owner decision**; waiting for owner review. §2.3 first bullet and §4 (label-only style) now describe the state before the redraw | `AGENT_TASKS.md` | all 6 sheets redrawn |
| 2026-11-17 | **OWNER (confirmed):** product goal = compete with Chinese ESS BMS makers (Daly, JBD, JK, etc.) with a compact board and **more features than they offer**, for energy-storage use. Use **every useful BQ76952 feature**; the AFE interface may move to **SPI** if needed. Shunt goes **on the board** (replaces the external shunt on J_KELVIN1). Balancing to be reviewed. Research by parallel agents first (report only); circuit changes follow, each after an owner decision | owner message 2026-11-17 | external shunt on J_KELVIN1, I2C to the AFE |
| 2026-11-17 | Research done by 5 parallel agents (report only): BQ76952 features, competitors, balancing, on-board shunt / power path, MCU / system features. Reports and summary: `%TEMP%\bms_work\research\00_SUMMARY.md` and `01`–`05_*.md`. Many LCSC numbers in the fields point to other parts (summary §4) | research | – |
| 2026-11-17 | **OWNER (confirmed): power switching = on-board back-to-back high-side N-MOSFET banks driven by BQ76952 CHG/DSG with PCHG/PDSG pre-charge.** Contactor driver channels become optional outputs (breaker trip / external contactor). This supersedes "schematic as drawn is the design" for the power path | owner answer 2026-11-17 | contactor drivers only |
| 2026-11-17 | **OWNER (confirmed): rating 200 A continuous, LFP only** (100 V MOSFETs; 16S NMC out of scope). Board size / split to be proposed in the architecture | owner answer 2026-11-17 | – |
| 2026-11-17 | **OWNER (confirmed): MCU = STM32G473RCT6 (LQFP-64, 3 FDCAN)**, replacing STM32G431CBT6. Not AEC-Q (no STM32G4 is) | owner answer 2026-11-17 | STM32G431CBT6 |
| 2026-11-17 | **OWNER (confirmed): v1 feature set** = competitor must-haves (sleep / wake + button, SOC LEDs + RUN/ALM, 2 dry contacts, heater output, parallel packs with RJ45 x4 + 2nd RS-485 + 2nd CAN + DIP pack address, RTC + FRAM + 8 MB log flash, firmware update) + ESP32-C3 BLE / WiFi module + improved balancing (TI NPN external balancing + active-balancer header + charge-based FW) + MCU-independent safety trip (AFE fault outputs + latched bidirectional OC trip into a hardware gate-kill, switch / pre-charge fault checks) | owner answer 2026-11-17 | – |
| 2026-11-17 | **OWNER (confirmed):** the project is a **public GitHub showcase**; documentation is mandatory (`README.md`, `docs/`). Commits are made **as the owner**, without agent attribution; no personal paths in committed files | owner message 2026-11-17 | – |
| 2026-11-17 | **OWNER (confirmed): license** = CERN-OHL-S-2.0 for the hardware (`LICENSE`, official SPDX text) and MIT for `tools/` (`tools/LICENSE`) | owner answer 2026-11-17 | – |
| 2026-11-17 | **OWNER (confirmed): repo clean-up = move, not delete.** 95 items (old ERC / DRC reports, test boards, `scripts/`, netlists, SVG exports, `.bak`, `fabrication/` of 2026-10-27, duplicate `power_stage_plan.md` and schematics PDF, old BOM csv, `log.txt`, `.history/`, `.mcp-backups/`) moved to the sibling folder `../Automotive-Grade-ESS-BMS_archive/2026-11-17_repo_cleanup/` with a `MANIFEST.txt`. The 8 plan files moved to `docs/plans/` (references to `plan_*.md` elsewhere in this file now mean `docs/plans/plan_*.md`). Netlist identical and ERC 0 after the move. Section 9 below is done | owner answer 2026-11-17 | – |

When the owner makes a new decision, add it to this table.

---

## 6. Layout / PCB state and notes

**State of `Automotive_ESS_BMS.kicad_pcb` (2026-11-16, saved 2026-11-02 13:53):**
* 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu, all typed `signal`), thickness 1.6 mm, **no stackup section** in the file.
* Outline 160.0 x 100.0 mm (4 lines, 20,20 to 180,120) plus three 1.2 x 4.4 mm rectangles on Edge.Cuts at x = 115.4, 126.4, 135.4, y = 90.8–95.2 (slots).
* 231 footprints: 215 top, 16 bottom; 224 schematic parts + MH1-4 + FID1-3. All from stock KiCad libraries.
* **22 240 track segments** (F.Cu 14 809, B.Cu 7 430, In2.Cu 1), total length about 5.7 m, average 0.26 mm per segment (script-generated routing); 434 vias; widths 0.2 mm (19 542), 0.5, 0.35, 0.25, one 1.0 mm.
* 10 zones, none filled in the file: `GND_PWR` and `GND_ISO` on F.Cu, B.Cu, In1.Cu; `+12V` (2), `+3V3`, `+5V_ISO` on In2.Cu.
* The routing is **not usable as it stands**: 3 shorts, 8 crossings, 33 clearance errors, 240 unconnected items, 114 parity errors on the MOSFETs (section 2.5). Board values are older than the schematic for D1, R1, R_VC0-16.
* Other board files in the root are experiments of 2026-11-02 (`test_*.kicad_pcb`, `Automotive_ESS_BMS_short_test`, `_clean_backup`); which of them, if any, is the intended starting point is not recorded (section 8, question 3).

**Layout notes recorded in the plans (apply when the layout is redone; owner to confirm):**
* Stackup JLC04161H-7628: 1 oz all layers, prepreg 0.21 mm, core 1.065 mm; In1 solid ground, In2 power planes (`plan_pcb_manufacturing.md` §1).
* Barrier: at least 4.0 mm clearance and 6.5 mm creepage; 1.5 mm milled slot under every isolator and the isolated DC-DC (`plan_pcb_manufacturing.md` §2).
* U1 thermal pad: 3 x 3 vias (0.3 mm drill) into the ground plane. Balance resistors on B.Cu, at least 3.0 mm centre to centre, copper pours and vias. Shunt: heavy pours with 12 stitching vias per side for 4.0 W at 200 A (`plan_pcb_manufacturing.md` §3; the shunt is now external).
* Fiducials: 3, 1.0 mm pad with 2.0 mm mask opening. Tooling holes: 4 x 3.2 mm at 5 mm from the edges (`instructions.md` §4.4).
* Design rules in `.kicad_pro`: min track and clearance 0.127 mm, via 0.45 / 0.20 mm, annular ring 0.125 mm, hole to hole 0.5 mm, copper to edge 0.3 mm, silk text 0.8 mm (`instructions.md` §4.2 says 1.0 mm).

---

## 7. Scripts in `scripts/`

228 one-off Python files, almost all dated 2026-11-02, untracked in git. They open project files by bare name (`Automotive_ESS_BMS.kicad_pcb`, `02_AFE_Cell_Monitor.kicad_sch`), so they act on the **live files of whatever folder they are run from**, with no backup step. 98 use `pcbnew`; the schematic ones edit text with regular expressions. 53 write files, 175 only read. They are records of what was done: **do not run them on the current files.**

| Group | Files | What they do |
|---|---|---|
| Schematic rework | `apply_sheet1..6.py`, `apply_all_schematic_fixes.py`, `fix_sheet1..5.py`, `fix_annotation.py`, `fix_instances.py`, `fix_sheet_instances.py`, `fix_cff1_inst.py`, `fix_d3.py`, `remove_dangling_s4.py` | regex edits of the `.kicad_sch` files: rewire labels, add / rename parts, repair instance paths and annotation, delete dangling labels |
| BOM / LCSC | `fix_all_bom_lcsc.py`, `fix_remaining_bom.py`, `generate_bom.py`, `check_bom_dupes*.py`, `check_fake_lcsc.py` | replace LCSC / MPN fields in the sheets, write `JLCPCB_BOM_Automotive_ESS_BMS.csv`, look for duplicate or suspect numbers |
| Board sync and placement | `sync_pcb_netlist.py`, `sync_q_pins.py`, `fix_fpids.py`, `prefix_fp_libs.py`, `fix_placement_and_zones.py`, `reposition_right_edge.py`, `compare_sch_pcb.py` | push netlist nets onto pads (including the D / G / S transistor pins), fix footprint ids, move connectors |
| Zones and vias | `build_all_zones.py`, `write_4layer_zones.py`, `write_clean_zones.py`, `place_safe_plane_vias.py`, `run_log_zones.py`, `run_debug_zones.py` | delete and rewrite the zone blocks, drop plane vias |
| Routers | `router_engine.py`, `production_router.py`, `production_pcb_router.py`, `clean_production_router.py`, `full_board_router.py`, `full_clean_autorouter.py`, `route_bal_nets.py`, `route_group1.py`, `run_*pipeline*.py`, `run_routing_all.py`, `run_all_routing_verified.py`, `execute_full_production_routing.py`, `clear_tracks.py`, `benchmark_router.py` | home-made grid autorouters (heapq) and the pipelines that clear tracks, route and save the board |
| Router experiments | `test_*.py` (37) | router variants; several write `test_*.kicad_pcb` copies or the main board |
| Read-only probes | `inspect_*.py` (55), `find_*.py` (29), `check_*.py` (27), `read_*.py`, `parse_*.py`, `analyze_*.py`, `debug_*.py`, `dump_*.py`, `print_*.py`, `classify_signal_nets.py`, `detailed_annotation_check.py` | print positions, pads, nets, labels, DRC items for one question each |

`tools/` (added 2026-11-16, the generic helper scripts named in `instruction.md` section 12): `check_env.py` and `tools/schematic/` `kisexp.py`, `pins.py`, `semdiff.py`, `netcmp.py`, `ercsum.py`, `render.py`, `ds_index.py`. They take the project folder or file names as arguments; nothing in them points outside this folder. `tools/schematic/examples/` (mentioned in `instruction.md`) is not present here. `ds_index.py` needs a `datasheets/README.md` index, which this project does not have yet; it prints a message and stops until one exists.

---

## 8. Open questions for the owner

1. **Which design is the truth: the plans or the schematic?** They differ in parts and in function (decisions log, last column): MCU family, watchdog type, 5 V buck, TVS voltage, comparator, CAN and RS-485 transceivers, shunt on board or external, no AFE isolator, no hardware trip latch, no CAN choke, cell filter 100 R instead of 1.00k.
2. **Schematic style:** keep the label-only drawing, or redraw to the playbook style (wires, power symbols, boxes, 0.8 / 1.0 mm text, A3 everywhere, test points, `Spec` field, JLC links in `Datasheet`)? This is a full redraw of six sheets.
3. **Board:** start the layout again from placement, or keep one of the 2026-11-02 files? If keep, which file?
4. **MOSFET symbols:** `Device:Q_NMOS` pins D / G / S do not map to SOT-23 pads 1 / 2 / 3. OK to change the 19 parts to a symbol with numbered pins after a pin-out check on the AO3400A and SQ2318EY datasheets?
5. **Grounds:** the plans name `GND_PWR`, an analog logic `GND` and `GND_ISO`; the schematic has `GND_PWR` and `GND_ISO` only, and the MCU sits on battery ground with a direct I2C link to the AFE. Intended?
6. **Balancing drive:** each balance FET gate is on the filtered tap `VC(n-1)` and its source on `CELL_(n-1)`. Is this the intended circuit? `plan_afe_cell_monitor.md` §3.2 describes FETs driven by the BQ76952.
7. **AFE pins:** REGIN, LD and PACK on `GND_PWR`; NTC 4 on DCHG and the board NTC on DDSG; CHG, DSG, PCHG, PDSG, FUSE, BREG, REG2 unconnected. Confirm against the BQ76952 datasheet (not opened yet).
8. **MCU:** `AFE_SDA` is on both PB7 and PB9; U2 FB is tied straight to `+5V`. Intended?
9. **Over-current trip:** threshold 2.90 V / 250 A (sheet note) or 3.15 V / 500 A (plan)? Should `OCP_TRIP_N` act on the contactor drivers in hardware?
10. **Part numbers:** all 85 LCSC numbers are unverified and several fields contradict each other (section 3). OK to run a live part audit sheet by sheet and bring the fields to the playbook standard?
11. **Title block:** is `NextGen Automotive Energy Storage Solutions` the right company name? Revision and date to use from now on?
12. **Ignored ERC / DRC checks** (sections 2.4, 2.5): keep them ignored?
13. **`instructions.md`:** it holds the original BMS runbook. Keep it as a requirements file under another name (for example `docs/01_Requirements/`), or fold it into this file and remove it? `instruction.md` is now the generic playbook; the unrelated text that was in it since 2026-11-04 is no longer in this folder.
14. **Git:** commit the current state as a checkpoint before any further work? There is one commit and no remote.
15. **Fabrication outputs** in `fabrication/` are from 2026-10-27 and do not match the current files. Was anything ordered from them?

---

## 9. Folder clean-up proposal (nothing was deleted or moved)

| Category | Files | Proposal |
|---|---|---|
| DRC reports | 30 (`drc_*.rpt`, `drc_initial.json`, `Automotive_ESS_BMS_drc.rpt`) | remove; regenerate when needed |
| ERC reports | 25 (`erc_*.rpt`, `erc_*.json`, `Automotive_ESS_BMS_erc.rpt`) | remove; keep one current report only if the owner wants one in the repo |
| Test and backup boards | 21 (`test_*.kicad_pcb / .kicad_pro / .kicad_prl`, `Automotive_ESS_BMS_short_test.*`, `_gnd_test.*`, `_test_slot.*`, `_clean_backup.kicad_pcb`), about 20 MB | remove after question 3 is answered |
| Schematic backups | 4 (`*.kicad_sch.bak`) | remove (already git-ignored) |
| Netlists and net dumps | 5 (`Automotive_ESS_BMS.net`, `_new.net`, `_clean.net`, `netlist.xml`, `all_nets_detail.txt`) | remove; exports are regenerated |
| SVG exports | 2 folders, 14 files (`schematic_svgs/` and a folder named `01_Power_Supply.svg/`) | remove |
| Tool backups / history | `.mcp-backups/` (3 board copies, tracked in git), `.history/` (KiCad local history, a nested git repo) | remove from the repo and add to `.gitignore` |
| Duplicates | `power_stage_plan.md` (identical to `plan_powerstage.md`), `Automotive_ESS_BMS_Schematics.pdf` (identical to the copy in `fabrication/`) | remove the duplicate |
| Empty | `log.txt` (0 bytes), `3d_models/` | remove `log.txt`; keep the folder only if 3D models are planned |
| One-off scripts | `scripts/` 228 files + `__pycache__/` | move out of the project or into an `archive/`; keep at most the few worth reusing |
| Stale outputs | `fabrication/` (2026-10-27), `JLCPCB_BOM_Automotive_ESS_BMS.csv` (2026-11-02) | regenerate into `production/` when the design is ready; remove the old set after question 15 |
| Plans | 7 `plan_*.md` + `system_architecture_master_plan.md` + `instructions.md` | move to `docs/` (requirements / architecture) once `DESIGN_NOTES.md` carries their content; their `file:///` links and several part numbers are out of date |
| `.gitignore` | – | add the playbook §13 lines: `*-backups/`, `.history/`, `~*.lck`, `fp-info-cache`, `desktop.ini`, `__pycache__/`; drop `*.kicad_dru` only if custom rules are wanted in git |
