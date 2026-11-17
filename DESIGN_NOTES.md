# Design notes archive - Automotive-Grade ESS BMS

Scaffold written 2026-11-16. One section per sheet. Each section summarises the calculations and design reasoning that already exist in the plan files and names the file; the plan files stay the full text until the owner moves them.
The plans were written on 2026-10-26 / 27, before the 2026-11-02 rework. Where the schematic differs from a plan this file says "schematic today". None of the numbers below was re-calculated or checked against a datasheet on 2026-11-16: they are **quoted**, not verified.
Where a block below disagrees with `PROJECT.md` section 5, `PROJECT.md` wins.
The calculations and derivations live here; the schematic keeps only the key point next to each part (playbook 7.5 / 7.6).

Marking used from now on: `DS p.x` = from an opened datasheet, `calc` = own calculation, `est.` = estimate with its assumption, `plan` = quoted from a plan file and not yet re-checked.

## System level (root, `Automotive_ESS_BMS.kicad_sch`)

Sources: `instructions.md` §1-4, `system_architecture_master_plan.md` §1, §3, §7.

```
Pack: 7S-16S LFP / NMC; 16S LFP nominal 51.2 V, 40.0-58.4 V (plan, instructions.md 2.1)
Pack supply envelope 16-72 V, 100 V transient (plan; root title block)
Targets: cell accuracy +/-1.5 mV, 4-8 NTC inputs, current +/-200 A continuous / 500 A peak (plan, instructions.md 2.1)
Standards named: IPC-2221B, IPC-7351B, IEC 60664-1 (6.5 mm creepage over the barrier), ISO 26262 ASIL B/C principles,
  IEC 62619 / UL 1973, UL 9540A, AEC-Q100/101/200 (plan, instructions.md 3)
Global signal list (plan, master plan 3): V_BATT+, GND_PWR, +12V, +5V, +3V3, +5V_ISO, GND_ISO, VC0..16, NTC1..4, ...
  schematic today uses other names for several of them (CELL_n / VCn, NTC_TSn, SH_P / SH_N, CTRL_CONT_POS ...)
Port protection table (plan, master plan 7): one TVS / ESD part per external port
```

To do:
* Power budget per rail (load, limit, % used) from the parts actually fitted. Plan figures are in the next section.
* Domain and isolation statement: working voltage across the barrier, creepage and clearance required and achieved.
* Fail-safe table: state of every contactor output with the MCU in reset, unpowered, or a cable unplugged.
* Firmware rules list (pin modes, watchdog timing, balancing limits).

## 01_Power_Supply.kicad_sch

Source: `plan_powerstage.md` (identical copy: `power_stage_plan.md`).

```
Rail budget (plan 2):   +12V    12.0 V +/-3 %   1.5 A peak (contactor pull-in), 250 mA hold with PWM
                        +5V      5.0 V +/-2 %   600 mA peak, 200 mA continuous
                        +3V3     3.30 V +/-1 %  300 mA peak, 85 mA continuous
                        +5V_ISO  5.0 V +/-4 %   200 mA peak, 60 mA continuous
Input envelope (plan 3, stage 0): 16.0 V (7S LFP at 2.28 V/cell) to 68.0 V (16S NMC at 4.25 V/cell), 100 V for < 100 ms
Input protection (plan): F1 2.5 A 125 V fast 1206; D1 SMCJ75A (75 V stand-off, 120 V clamp at 12.5 A); D2 SS310 series
  Schottky; J_AUX 12 V bench input
Stage 1, LM5164-Q1 (plan): VOUT = 1.20 V x (1 + 90.9k / 10.0k) = 12.1 V; L1 47-68 uH, Isat >= 1.8 A;
  duty 17.6 % at 68 V, 75 % at 16 V
Stage 2, 12 V -> 5 V buck (plan): LDO would burn (12 - 5) x 0.3 A = 2.1 W; buck at > 92 % about 0.12 W
Stage 3, 5 V -> 3.3 V LDO (plan): (5.0 - 3.3) x 0.1 A = 0.17 W in SOT-23-5; AP2112K-3.3 600 mA, 250 mV dropout
Stage 4, isolated 5 V (plan): 3000 VDC / 2500 Vrms; B0505S-1WR3 module or SN6505B + transformer
```

Schematic today: U2 = LMR16006YQ5 (plan: LMR36506 / MP2315 / TPS62933), L2 10 uH, D5 SS14; D1 = SMCJ64A; L1 47 uH; R1 2.4M from `V_IN_BUCK` to the RON pin, EN/UVLO tied to VIN; U2 FB tied to `+5V` with no divider; sheet notes still describe LMR14006, TPS7A2533, 100 uH, 22 uH and a common-mode choke.

To do:
* TVS clamp voltage against the absolute maximum of U1 and everything on `V_BATT+` (BQ76952 BAT pin, D_BAT1, J_PRE1 path).
* F1 rating and I2t against inrush into C1 / C2 and the load.
* U1: RON / switching frequency, inductor ripple and saturation margin, output ripple, UVLO threshold, Pd and TJ.
* U2: output voltage setting (fixed or adjustable version), inductor and diode currents, Pd.
* U3: dropout headroom, Pd at the real +3V3 load. U4: minimum load, isolation rating, output ripple.
* MLCC DC-bias derating (10 uF 100 V input, X5R parts listed in `PROJECT.md` section 3).
* LED currents on the four rails.

### Sheet 01 redraw (2026-11-17): notes moved off the sheet

On-sheet notes after the redraw (short reviewer notes, 1-4 lines per box) and their basis:
* Input: F1 then D1 TVS to `GND_PWR`, D2 SS310 series diode to `V_IN_BUCK` (netlist).
* +12V: `VOUT = 1.20 V x (1 + R2 / R3) = 1.20 x (1 + 90.9k / 10.0k) = 12.1 V` (plan; the 1.20 V reference is not checked against the LM5164 datasheet). EN/UVLO tied to VIN, no UVLO divider; R1 2.4M on RON; C_FF1 47 pF across R2; `PWR_PGOOD` has only U1 pin 6 and R_PG1 (netlist).
* +5V: U2 FB on `+5V`, no divider; the KiCad symbol description says "Fixed 5.0V output voltage" (not checked against the datasheet). ~SHDN on `+12V`. D5 SS14 catch diode, C7 bootstrap (netlist).
* +3V3: EN on VIN, pin 4 NC. `Pd = (5.0 V - 3.3 V) x I(+3V3)` (calc; the +3V3 load is not yet budgeted, see "To do").
* +5V_ISO: B0505S-1WR3 (Mornsun) placed with the Murata CRE1 symbol and footprint (fields).

Notes that were on the sheet until 2026-11-17, archived verbatim; the remarks in brackets on the right were added on 2026-11-17. The notes are **stale**: the parts named do not match the fitted parts (`PROJECT.md` section 4). Kept only as a record.
```
SECTION 1: BATTERY INPUT TRANSIENT PROTECTION
Input: 16V - 72V Nom, 100V Trans
F1: 3A 125V Fast-Acting Fuse                      (fitted: 2.5A 125V, 046602.5NR)
D1: SMCJ75A 1500W TVS (ISO 16750-2)               (fitted: SMCJ64A)
D2: SS310 100V 3A Reverse Schottky
SECTION 2: PRIMARY 12V BUCK REGULATOR
IC: LM5164-Q1 Sync Buck (300kHz)                  (switching frequency not checked)
L1: 100uH 1.8A Shielded Inductor                  (fitted: 47uH 1.8A)
Output: +12V @ 1.0A for Contactors
SECTION 3: 5V AUXILIARY BUCK
IC: LMR14006 Step-Down (12V -> 5V)                (fitted: LMR16006YQ5)
L2: 22uH Inductor, D5: B2100A                     (fitted: 10uH, SS14)
Output: +5V @ 600mA Intermediate
SECTION 4: ULTRA-LOW-NOISE 3.3V LDO
IC: TPS7A2533 High-PSRR LDO                       (fitted: AP2112K-3.3)
PSRR: >60dB @ 100kHz
Output: +3V3 @ 300mA for MCU/ADC
SECTION 5: 3.0kVrms ISOLATED DC-DC
Module: B0505S-1WR3 (5V -> 5V_ISO)
CMC1: Common Mode Choke + LC Filter               (no choke or LC filter on the sheet)
Output: +5V_ISO for Comms & Transceivers
SECTION 6: POWER STATUS LEDS
D4: +12V Active (Green)   D6: +5V Active (Green)  (fitted: blue, yellow,
D7: +3V3 MCU Rail (Green) D8: +5V_ISO (Green)      green, orange)
```
Old title-block comments (stale, replaced): "Wide-Input 12V High-Voltage Synchronous Buck (LM5164-Q1, 16V - 72V Nom, 100V Trans)"; "Intermediate 5V Step-Down (LMR14006) & Ultra-Low-Noise 3.3V Logic LDO (TPS7A2533)"; "Galvanic 3000Vrms Isolated 5V/5V DC-DC Converter (B0505S-1WR3) with Common-Mode Choke". Old title: "Automotive High-Voltage Power Supply & Multi-Rail Conditioning Stage" (ran out of the title block).


## 02_AFE_Cell_Monitor.kicad_sch

Source: `plan_afe_cell_monitor.md`.

```
AFE BQ76952-Q1: 3S-16S, +/-1.5 mV typical, internal OV / UV comparators, 400 kHz I2C with CRC, BAT pin 85 V abs max (plan 1)
Cell-count setting (plan 2.1): Active Cells mask 0xFFFF (16S), 0x00FF (8S), 0x007F (7S); for fewer than 16 cells
  the top of stack goes to the highest used VC pin and is tied through the unused pins up to VC16 and BAT (TI SLUA991)
Thresholds (plan 2.2):          LFP                    NMC
  OV trip / recovery            3.650 V (1.0 s) / 3.550 V   4.220 V (1.0 s) / 4.100 V
  UV trip / recovery            2.500 V (2.0 s) / 2.800 V   2.850 V (2.0 s) / 3.100 V
  balance start / delta         3.400 V / > 15 mV           4.000 V / > 15 mV
Cell filter (plan 3.1): 1.00k series, 100 nF differential, 10 nF common mode;
  fc = 1 / (2 pi x 2 x 1k x 100 nF) = 795 Hz, > 40 dB at inverter PWM frequencies
Balancing (plan 3.2): 3.45 V / 100 mA = 34.5 R -> 33 R (104 mA); P = 0.104^2 x 33 = 0.36 W in a 1 W 2512 (< 40 %);
  external SOT-23 FET (AO3400A / DMN3051L) so the heat is in the resistors, not in the AFE
Temperature (plan 3.3): 4 pack NTC 10k + 1 board NTC next to the balance bank (throttle above +75 C)
Isolation (plan 3.4): ISO7741-Q1 between the AFE I2C / SPI and the MCU
```

Schematic today: R_VC0-16 = 100 R (sheet note: fc = 15.9 kHz); no common-mode capacitors; no ISO7741, I2C direct to the MCU on a common `GND_PWR`; balance FET gates on `VC(n-1)`; 4th pack NTC on the DCHG pin, board NTC on DDSG; REGIN / LD / PACK on `GND_PWR`.

To do:
* Decide the cell filter value and redo fc; check it against the BQ76952 input and balancing requirements (DS).
* Balancing drive: document how each FET is turned on, VGS available, current through R_VC during balancing, cell-voltage error while balancing.
* Balance bank thermal: 16 x 0.36 W on the bottom side, copper area, board temperature limit.
* BQ76952 pin configuration: REG1 / REG18 capacitors, REGIN, LD, PACK, charge pump, unused FET driver pins, TS pin functions.
* Cell-tap protection: hot-plug, fusing, tap current limits, connector pin rating.
* NTC inputs: pull-up source, RC, ESD part capacitance.

### Sheet 02 - AFE / Cell Monitor (`02_AFE_Cell_Monitor.kicad_sch`) - redraw 2026-11-17

The sheet was redrawn to the house style (Task 6). Connectivity did not change (netcmp identical, same 165 net names).
The old on-sheet notes are archived below word for word. Several of their statements are not true for the fitted
parts; the corrections follow the archive.

### Archived on-sheet notes (before the redraw, verbatim)
```
SECTION 1: 16-CELL BATTERY TAP CONNECTOR & RC FILTERING
J_CELL1: 1x17 2.54mm Pin Header
Low-Pass Anti-Aliasing Filter: R_VC0..16 (100 Ohm) + C_DF1..16 (100nF)
Cut-off Frequency: f_c = 1 / (2 * pi * 100 * 100nF) ~ 15.9 kHz

SECTION 2: 16-CHANNEL PASSIVE CELL BALANCING ARRAY
R_BL1..16: 33 Ohm 1W 2512 SMT Resistors (Placed on PCB Bottom Layer B.Cu)
Balancing Current: I_bal = V_cell / R_bal = 3.65V / 33 Ohm ~ 110 mA
Drivers: SQ2318EY Dual N-MOSFETs controlled by BQ76952 internal gate logic

SECTION 3: AUTOMOTIVE 16S AFE (BQ76952-Q1)
16-bit Delta-Sigma ADC, Synchronous V/I Measurement
I2C Communication with Hardware CRC
Internal Regulators: REG1 (3.3V) & REG2 (5.0V)
Hardware Protection: Over/Under Voltage, Over/Under Temp

SECTION 4: PACK TEMPERATURE SENSING & ESD HARNESS PROTECTION
J_NTC1..4: External 10k NTC Thermistor Wire Harness Connectors
D_ESD_NTC1..4: ESD5V0D3B SOD-323 Bidirectional ESD Suppressors
Rating: +/-30kV Air & Contact ESD per ISO 10605
```
Archived title block: title `16S Precision Cell Monitoring & Active Balancing Stage`; comments
`Automotive 16S AFE Monitor (BQ76952-Q1) with Synchronous Sub-mV Cell ADC`,
`16-Channel 1W 2512 Heat-Sunk Passive Balancing Array (33-Ohm ~100mA Balancing)`,
`4-Channel External Battery Module Thermistors with Dedicated ISO 10605 ESD Clamping`,
`Sheet 3/7: Cell Voltage Sense, Balance & Thermal Frontend`. Paper was A2.

### What is true for the fitted parts (as drawn)
* **Balancing is passive**, not active (the old title said "Active Balancing").
* **Balance FETs are AO3400A** (Q_BL1-16, `Device:Q_NMOS`), not SQ2318EY dual MOSFETs. Per cell n:
  CELL_n - R_BLn - NET_BALn - Q_BLn drain; Q_BLn source on CELL_(n-1); **gate on VC(n-1)** (the AFE side of
  R_VC(n-1)). No other gate drive is on the sheet. The `Device:Q_NMOS` D/G/S pin map against the SOT-23 footprint is
  an open owner question (not changed).
* **Balance current / power (calc):** 3.65 V / 33 R = 110 mA; P = 3.65^2 / 33 = 0.40 W per R_BLn (1 W part).
  FET Rds(on) and R_VC ignored. 3.65 V is the cell voltage used by the old note (not checked against PROJECT.md cell data).
* **RC filter:** R_VCn in series from CELL_n to VCn; C_DFn across VCn / VC(n-1) (differential). The old 15.9 kHz
  figure used 100 R. **Value `100R 1%` but MPN `RC0603FR-071KL` (1 k) on all 17 R_VC** - which one is fitted
  decides f_c. calc, single RC: 100 R -> 15.9 kHz, 1 k -> 1.59 kHz; seen differentially (two R_VC in series with one
  C_DF): 100 R -> 7.96 kHz, 1 k -> 0.80 kHz. Not checked against the BQ76952 datasheet recommendation.
* **Regulators:** REGIN is tied to GND_PWR, REG2 is NC, C_R1 2.2 uF on REG1 and C_R18 2.2 uF on REG18. The old
  "REG1 3.3 V & REG2 5.0 V" statement does not match the wiring. (The U_AFE1 Description field says "REG1 LDO disabled".)
* **I2C CRC:** the old note says "with hardware CRC"; the U_AFE1 Description says "I2C interface without CRC"
  (MPN BQ7695202PFBR). Not verified - owner question.
* **Protection outputs:** CHG, DSG, PCHG, PDSG, FUSE are NC on this sheet, so the AFE drives no protection FET here.
  PACK and LD are on GND_PWR.
* **Supply:** BAT = V_BAT_FILT = V_BATT+ through D_BAT1 SS110, C_BAT1 1 uF 100 V to GND_PWR, PWR_FLAG #PWR_BAT.
  C_CP1 100 nF sits between CP1 and V_BAT_FILT; BREG is NC. Known owner questions (CP1 cap should go to BAT?
  BREG to GND?) - not changed.
* **Temperature:** NTC_TS1-3 on TS1-3, NTC_TS4 on DCHG, NTC_TS_PCB (RT_BOARD) on DDSG. Each external channel:
  C_NTCn 10 nF + D_ESD_NTCn ESD5V0D3B to GND_PWR, ESD last before J_NTCn. No external bias resistor on the sheet:
  firmware must set the pin modes (DCHG / DDSG as thermistor inputs). The ESD rating (+/-30 kV, ISO 10605) and the
  SOD-323 package were not checked against a datasheet.
* **Reset:** R_RST1 10 k pulls RST_SHUT (AFE_RST) to GND_PWR; the MCU drives AFE_RST.
* **Layout hint (from the old note, unverified):** R_BL1-16 were planned on the bottom layer (B.Cu) to spread heat.

## 03_MCU_Control.kicad_sch

Source: `plan_mcu_safety.md`.

```
MCU requirement (plan 1): Cortex-M4F with FPU, AEC-Q100 grade 1, ECC flash / RAM, CAN-FD, SPI, UART; S32K144 or STM32G4, LQFP-64
Watchdog (plan 2.1): external window watchdog TPS3851-Q1, kick window for example 50-100 ms; on failure reset the MCU
  and trip the hardware safety latch that opens the contactors
Memory (plan 2.2): 25LC256 SPI EEPROM or CY15B104Q FRAM: lifetime counters and a 50-event fault log
DIP switch (plan 2.3): SW1 chemistry (OFF = LFP 3.2 / 3.65 V, ON = NMC 3.7 / 4.20 V);
  SW2-4 cell count 000 = 7S, 001 = 8S, 010 = 10S, 011 = 12S, 100 = 13S, 101 = 14S, 110 = 15S, 111 = 16S (default)
Crystal (plan 4): 8.000 MHz, 12 pF load, 2 x 18 pF
```

Schematic today: STM32G431CBT6 in LQFP-48; watchdog TPS3823-33 (sheet note: 1.6 s timeout, not a window type); 25LC256; no safety latch. Pin map in `PROJECT.md` section 1.2.

To do:
* Pin by pin check of every alternate function against the STM32G431 datasheet AF table (FDCAN on PA11 / PA12, USART1 on PA9 / PA10, I2C1 on PB6 / PB7 / PB9, SPI1, ADC channels on PA0 / PA1, PB8 BOOT0, PG10 NRST).
* Supply rules: VDDA / VREF+ through FB1, decoupling per pin, VBAT.
* Crystal load: CL = C/2 + Cstray with the fitted 18 pF.
* Reset network with the supervisor on NRST and the SWD header; boot pin state.
* ADC ranges: `ADC_I_SENSE` and `V_HV_SENSE` against VREF+.
* Watchdog timing against the firmware loop; what the outputs do during reset.
* Pin tolerance of every pin driven from a 5 V part.

### Sheet 03 redraw (2026-11-17): notes moved off the sheet


On-sheet notes after the redraw (short reviewer notes, 1-4 lines per box) and their basis:
* MCU: C_VDD1 / C_VDD2 / C_VDD3 100 nF on VDD pins 24 / 36 / 48; VBAT (pin 1) on `+3V3` with no cap of its own. VDDA (pin 21) and VREF+ (pin 20) on `+3V3_A` = `+3V3` through FB1 600R @ 100 MHz, with C_A1 1 uF and C_A2 100 nF. Y1 8.000 MHz with C_X1 / C_X2 18 pF to `GND_PWR`. The load capacitance of Y1 (MPN X32258MOB4SI) has not been checked: `CL = C/2 + Cstray = 9 pF + Cstray` (calc). The plan asks for 12 pF. Source: the netlist and the fields.
* MCU, as drawn (owner question, `PROJECT.md` section 8 question 8): `AFE_SDA` is on PB7 **and** PB9, and `AFE_SCL` is on PB6. Not changed.
* Reset / watchdog / boot: U_WDOG1 RESET (pin 1) drives `MCU_RESET_N`, which goes to PG10-NRST, R_RST2 10k to `+3V3`, C_RST2 100 nF to `GND_PWR` and J_SWD1 pin 10. WDI comes from PB0 (`MCU_WDOG_WDI`). ~MR is on `+3V3` (no reset button). R_BOOT0 10k pulls PB8-BOOT0 (`MCU_BOOT0`) to `GND_PWR`. Source: the netlist. The TPS3823 timeout and RESET output type were not checked against the datasheet.
* Config switch: SW_CFG1 pins 1-4 = `CFG_CHEM`, `CFG_CELL_0..2`, each with a 10k pull-up (R_SW1-4) to `+3V3`; pins 5-8 go to `GND_PWR`. Switch ON reads 0, OFF reads 1 (netlist). The coding table is in the plan quote above (firmware).
* SPI EEPROM: U_MEM1 ~WP and ~HOLD on `+3V3`; R_CS1 10k pull-up on `SPI1_CS_MEM`; C_MEM1 100 nF at VCC (netlist).
* SWD: J_SWD1 pin 1 `+3V3`, pins 3 / 5 / 9 `GND_PWR`, 2 `SWDIO`, 4 `SWCLK`, 10 `MCU_RESET_N`. Pins 6, 7 and 8 have no-connect flags (netlist; Cortex 10-pin pin 6 = SWO).
* Heartbeat: PC13 (`MCU_HEARTBEAT`) → R_HB1 1.0k → `NET_LED_HB` → D_HB1 (blue) → `GND_PWR`. PC13 is a backup-domain pin with a low drive limit. Check the limit and the LED current (blue Vf about 3 V at 3.3 V, est.) against the STM32G431 and LED datasheets.

Drawing conventions on this sheet: every MCU signal pin carries its global label on the pin stub (playbook section 6). The peripheral blocks carry the same global label names at their own pins, so the internal nets (`MCU_RESET_N`, `MCU_WDOG_WDI`, `MCU_BOOT0`, `SPI1_*`, `CFG_*`, `SWDIO`, `SWCLK`, `MCU_HEARTBEAT`) have one label at the MCU and one at each peripheral block. The crystal and the supply pins are wired. `+3V3_A` is a new project power symbol (copy of `power:+3V3`, pin `power_in`). The power-symbol references are `#PWR301`-`#PWR327`.

Notes that were on the sheet until 2026-11-17, archived verbatim. The remarks in brackets on the right were added on 2026-11-17. Several notes are **stale**: the parts or values they name do not match the fitted parts. They are kept only as a record.
```
SECTION 1: AUTOMOTIVE MCU (STM32G431CBT6)
Arm Cortex-M4F @ 170MHz with FPU & CORDIC Accelerator           (not checked against the DS)
128KB Dual-Bank Flash, 32KB SRAM with Parity                    (not checked against the DS)
3x Fast 12-bit ADCs (4.25 MSPS), Dual CAN-FD Controllers         (not checked against the DS)
SECTION 2: ANALOG POWER FILTERING
FB1: 600 Ohm @ 100MHz Ferrite Bead
C_VDDA1: 10uF + 100nF High-Frequency Filtering                  (fitted: C_A1 1uF + C_A2 100nF; no part C_VDDA1)
SECTION 3: HARDWARE WATCHDOG
IC: TPS3823-33QDBVRQ1 Automotive Supervisor                     (fitted value / MPN: TPS3823-33DBVR, non-Q1)
Timeout: 1.6s. Asserted on MCU NRST line upon firmware hang     (timeout not checked against the DS)
SECTION 4: SPI CALIBRATION EEPROM
IC: 25LC256 256-Kbit Automotive EEPROM                          (fitted MPN 25LC256-I/SN: industrial grade)
Stores SoC/SoH Calibration, Cycle Count & Fault History         (firmware intent)
SECTION 5: CHEMISTRY & CELL COUNT SELECTION SWITCH
SW_CFG1: 4-Position SMT DIP Switch
SW1: OFF = LiFePO4 (3.2V / 3.65V), ON = NMC (3.7V / 4.2V)
SW2..SW4: Series Cell Count (000=7S, 001=8S, 010=10S, ... 111=16S)   (full table in the plan quote above)
SECTION 6: SWD DEBUG & HEARTBEAT
J_SWD1: Cortex 10-pin Debug Interface
D_HB1: 1Hz Heartbeat Health Status Indicator                     (1 Hz is firmware)
```
Old title-block comments (replaced): "STM32G431CBT6 170MHz Arm Cortex-M4F with Hardware CORDIC & Math Accelerators"; "Hardware Power Supervisor & Windowed Watchdog Timer (TPS3823-33QDBVRQ1, 1.6s)" (stale: the fitted value is TPS3823-33DBVR; whether it is a window type was not checked, and the earlier archive note says it is not); "256-Kbit Automotive SPI Calibration EEPROM (25LC256) & Hardware DIP Switch Selector"; "Sheet 4/7: Core Processing, State Machine & Safety Logic". Old title: "Safety Controller, Supervisory Watchdog & Configuration Stage".

## 04_Current_Sensing.kicad_sch

Source: `plan_current_sensing.md`.

```
Requirement (plan 1): +/-200 A continuous, +/-500 A for 10 s, resolution <= 50 mA, hardware short-circuit trip < 2.0 us
Shunt (plan 2): 100 uOhm; 20.0 mV at 200 A, 50.0 mV at 500 A; P = 200^2 x 100u = 4.0 W; 5930 Manganin, +/-50 ppm/C
Amplifier (plan 3.1): INA240A2-Q1, gain 50, CM range -4 V to +80 V, VREF = 1.65 V:
  0 A -> 1.650 V; +200 A -> 2.650 V; -200 A -> 0.650 V; +500 A -> 3.150 V
Trip (plan 3.2): tier 1 firmware 250 A for > 500 ms; tier 2 comparator (TLV3201-Q1, 40 ns) at 3.15 V = +500 A into a
  latch (FAULT_LATCH_N) that removes contactor gate drive within 1.5 us
Kelvin filter (plan 4): 2 x 10.0 R, 100 nF
```

Schematic today: no shunt on the board, external shunt through J_KELVIN1, R_NT1 0 R from `SH_P` to `GND_PWR`; `SH_P` / `SH_N` also on the BQ76952 SRP / SRN pins; comparator TLV3501; sheet notes give V_TH = 2.90 V (250 A) and a linear range of +/-330 A; R_TH1 4.7k / R_TH2 100k; no latch.

To do:
* Decide shunt location and value; redo the transfer function and range from the fitted parts.
* Threshold from R_TH1 / R_TH2 (calc) against the intended trip current; comparator input range and hysteresis.
* Reference accuracy (REF1 = `+3V3`, REF2 = `GND_PWR`): error of the 1.65 V mid-point with +3V3 tolerance.
* Common-mode voltage at the amplifier inputs for the chosen shunt position; TVS D_TVS_SHUNT1 leakage and capacitance.
* Error budget: offset, gain, drift, ADC resolution against the 50 mA target.
* Response time of the full trip path.

### Sheet 04 redraw (2026-11-17): notes moved off the sheet


On-sheet notes after the redraw (short reviewer notes, 1-4 lines per box) and their basis:
* Shunt input: the shunt is external, on J_KELVIN1. `SH_P` / `SH_N` are drawn as a Kelvin pair and also go to U_AFE1 SRP / SRN (pins 18 / 20, netlist). R_NT1 0R is the only tie between `SH_P` and `GND_PWR` (netlist).
* Input filter: R_K1 / R_K2 10.0R in series with each line, C_K1 100 nF differential across `AMP_IN+` / `AMP_IN-`, C_K2 / C_K3 10 nF from each line to `GND_PWR`, D_TVS_SHUNT1 SMAJ5.0CA (bidirectional) across the pair (fields, netlist).
  * Differential corner (calc): `C_eff = C_K1 + C_K2 x C_K3 / (C_K2 + C_K3) = 100 nF + 5 nF = 105 nF`; `fc = 1 / (2 pi x (R_K1 + R_K2) x C_eff) = 1 / (2 pi x 20 R x 105 nF) = 75.8 kHz`.
  * Common-mode corner (calc): `fc_cm = 1 / (2 pi x 10 R x 10 nF) = 1.59 MHz`.
* Amplifier: U_ISENSE1 INA240A2-Q1, gain 50 V/V ("A2", also in the KiCad symbol description; datasheet not opened). V+ on `+5V`, REF1 on `+3V3`, REF2 on `GND_PWR`, so the zero-current output is `3.3 V / 2 = 1.65 V` (calc; it follows the +3V3 tolerance). `ADC_I_SENSE = 1.65 V + 50 x (V(SH_P) - V(SH_N))` (calc; pin 8 "+" = `AMP_IN+` from `SH_P`).
* Over-current comparator: U_OCP1 TLV3501. IN- (pin 1) = `ADC_I_SENSE`, IN+ (pin 3) = `V_TH_OCP`. `OCP_TRIP_N` is high while `ADC_I_SENSE < V_TH_OCP` and goes low above it; D_OCP1 (cathode on `OCP_TRIP_N`, anode through R_OCP_LED1 1.5k to `+3V3`) lights while it is low. R_OCP_PU1 10k pulls `OCP_TRIP_N` up to `+3V3`. `OCP_TRIP_N` goes only to the MCU (PA8) and the LED: there is no latch and no direct action on the contactor drivers.
  * Threshold (calc): `V_TH_OCP = 3.3 V x R_TH2 / (R_TH1 + R_TH2) = 3.3 x 100k / 104.7k = 3.152 V`. C_TH1 10 nF filters it: `tau = (4.7k || 100k) x 10 nF = 44.9 us` (calc).
  * Trip current: **not on the sheet**, because the shunt is not a part of this board. With the plan's 100 uOhm shunt (`plan_current_sensing.md` 2): `I_trip = (3.152 V - 1.65 V) / (50 x 100 uOhm) = 300 A` (calc). The old sheet note said 2.90 V / 250 A, which these resistors do not give; the plan says 3.15 V / 500 A. Owner question.
  * SHDN (pin 6) is tied to `+3V3`. Reported as a known fault (the review says this shuts the comparator down; datasheet not opened by this task). Not changed: owner decision.

Notes that were on the sheet until 2026-11-17, archived verbatim; the remarks in brackets on the right were added on 2026-11-17. Several statements are **stale** (R_SHUNT1 is no longer on the sheet; the threshold numbers do not match R_TH1 / R_TH2; there is no latch).
```
SECTION 1: KELVIN SHUNT & INDUCTIVE CLAMP
R_SHUNT1: 100uOhm 5W 5930 Shunt (+/-500A range)   (removed 2026-11-02; shunt is external, on J_KELVIN1)
D_TVS_SHUNT1: SMAJ5.0CA 400W Bidirectional TVS
Filter: R_K1/2 (10 Ohm) + C_K1/2/3 (10nF Diff)    (fitted: C_K1 100nF differential, C_K2/C_K3 10nF to GND_PWR)
SECTION 2: CURRENT SENSE AMPLIFIER (INA240A2-Q1)
Enhanced PWM Rejection Architecture
Gain: 50 V/V. Zero-Current Ref: V_REF = 1.65V
Transfer: V_OUT = 1.65V + (I_pack * 5.0 mV/A)     (5.0 mV/A only with a 100 uOhm shunt, not on this board)
Linear Range: -330A to +330A into 3.3V ADC         (depends on the external shunt)
SECTION 3: HARDWARE FAST OVER-CURRENT TRIP
IC: TLV3501 4.5ns Ultra-Fast Rail-to-Rail Comparator
Threshold: V_TH = 2.90V (I_trip = +250A Short-Circuit)   (R_TH1 4.7k / R_TH2 100k give 3.152 V (calc); 300 A on 100 uOhm)
Output: OC_ALERT Fast Latch Line to Safety MCU    (net is OCP_TRIP_N; no latch; MCU PA8 + LED only)
SECTION 4: FAULT STATUS
D_OCP1: Red LED Latched Over-Current Indicator    (not latched: lights only while OCP_TRIP_N is low)
```
Old title-block comments (stale, replaced): "100-micro-Ohm 5W 5930 Ultra-Low TCR Kelvin Shunt with Transient TVS Clamping" (no shunt on the board); "Automotive Bidirectional Current Sense Amplifier (INA240A2-Q1, Gain = 50 V/V)"; "Ultra-Fast 4.5ns Hardware Analog Comparator (TLV3501) with Latched Trip Indicator" (no latch); "Sheet 5/7: Pack Current Sense & Sub-Microsecond Fast Fault Trip" (response time not established). Old title: "Bidirectional Current Sensing & Hardware Over-Current Protection".

Redraw facts: 19 parts kept (same UUIDs, lib_ids and field values); 14 new power symbols `#PWR401`-`#PWR414` (`+5V`, `+3V3`, `GND_PWR`); one global label per net (`SH_P`, `SH_N`, `AMP_IN+`, `AMP_IN-`, `ADC_I_SENSE`, `V_TH_OCP`, `OCP_TRIP_N`, `NET_LED_OCP`); no PWR_FLAG on this sheet (none before). The unused embedded `Device:R_Shunt` library symbol (left over from R_SHUNT1) stays in the sheet's `lib_symbols`; it has no instance.

## 05_Power_Actuators.kicad_sch

Source: `plan_power_actuators.md`.

```
Channels (plan 1): main positive, main negative, pre-charge; coils on regulated +12 V
Pre-charge sequence (plan 2): close NEG -> close PRE (50 R: I_peak = 58 V / 50 R = 1.16 A) -> wait until
  V_INVERTER >= 95 % of V_BATT (typically 200-800 ms, read through a 100 : 1 divider) -> close POS -> open PRE 50 ms later
Drivers (plan 3.1): low-side N-MOSFET SQ2318EY (40 V, 8 A, < 25 mOhm) or a smart driver; gate pull-down; clamp
Economiser (plan 3.2): pull-in 1.0-1.5 A at 12 V (18 W) for 100 ms at 100 % duty, then 25-30 % PWM at 20 kHz,
  hold about 250 mA, about 1.5 W
Divider (plan 4): 2 x 1.00M 1206 (200 V each) + 20.0k 0.1 %
Gate clamp (plan_pcb_manufacturing 5): BZX84-C18 keeps VGS below 18 V
```

Schematic today: three SQ2318EY with 100 R gate, 47k gate-source, 18 V zener, flyback diodes SS34 (40 V) to `+12V`; R_PRE1 50 R 25 W (sheet note: 47 R, tau = R x C); R_HV_BOT1 20.0k (sheet note: 68k, 30.4 : 1, 100 V -> 3.28 V).

To do:
* Divider ratio and ADC voltage at the maximum bus voltage from the fitted values; divider power and resistor voltage rating; filter corner with C_HV1.
* Pre-charge resistor energy for the real DC-link capacitance and bus voltage; number of consecutive attempts allowed.
* Coil current, MOSFET dissipation, flyback path and turn-off time with the chosen diode; diode voltage rating against the clamp level.
* Gate state with the MCU in reset (47k pull-down) and the resulting contactor state.
* Connector current per pin (J_CONT1, J_PRE1) and the voltage between adjacent pins of J_PRE1 (pin 3 `V_INVERTER_BUS` next to pin 4 `GND_PWR`).

### Sheet 05 - Power Actuators (`05_Power_Actuators.kicad_sch`)

Redrawn 2026-11-17 (Task 4) in the sheet-01 style. No part, value or net changed. Numbers below come from the fitted field values or are marked `calc`. No datasheet was opened.

### Contactor drivers (Q_POS1, Q_NEG1, Q_PRE1: three identical channels)
* Channel: `CTRL_x` (MCU) -> R_G 100R -> gate (`NET_GATE_x`) -> Q SQ2318EY (40V 8A), source on `GND_PWR`, drain on `COIL_x-` -> J_CONT1. R_GS 47k gate to source, D_Z BZX84-C18 (cathode on gate, anode on `GND_PWR`).
* D_FLY SS34 (40V 3A): cathode `+12V`, anode `COIL_x-`. It carries the coil current when Q opens. A plain diode clamp makes the contactor open slower than a Zener or TVS clamp would. The release time is not checked.
* Status LED: `+12V` -> R_LED 4.7k -> LED -> `COIL_x-`. It lights when Q pulls `COIL_x-` low. LED current = (12 V - Vf) / 4.7k, about 2 mA with Vf assumed at 2 V (est.).
* J_CONT1 pinout (netlist): 1 `+12V`, 2 `COIL_POS-`, 3 `+12V`, 4 `COIL_NEG-`, 5 `+12V`, 6 `COIL_PRE-`.
* Drawing: the three `+12V` pins each have their own `+12V` power symbol. The pins alternate, so tying them with one wire would cross a coil wire.
* Not checked (datasheet needed): SQ2318EY Rds(on) and Vgs(th) at the MCU's 3.3 V gate drive, coil current, SS34 surge rating against the coil energy.
* Open: `Device:Q_NMOS` pins are D/G/S, the SOT-23 footprint pads are 1/2/3 (`PROJECT.md` §8 q4). Not changed.

### Pre-charge (J_PRE1, R_PRE1)
* J_PRE1 pins: 1 `V_BATT+`, 2 `NET_PRE_IN`, 3 `V_INVERTER_BUS`, 4 `GND_PWR`. R_PRE1 50R 25W 5% (PWR263S-20-50R0J) between pins 2 and 3. No part on this board connects pin 1 to pin 2, so the pre-charge switch is off-board.
* Peak current at 72 V: 72 / 50 = 1.44 A (calc). Peak power: 72^2 / 50 = 104 W (calc), falling with tau.
* tau = 50R x C_bus (calc). Example only: with C_bus = 2000 uF (the old note's assumption, not a known value), tau = 100 ms and the resistor absorbs 0.5 x C x V^2 = 5.2 J at 72 V (calc). The pulse-energy rating of the PWR263S was not checked.

### Bus-voltage sense (R_HV1, R_HV2, R_HV_BOT1, C_HV1)
* V_HV_SENSE = V_INVERTER_BUS x 20.0k / (1.00M + 1.00M + 20.0k) = bus / 101 (calc).
* 72 V -> 0.713 V; 58.4 V -> 0.578 V (calc). If VREF is 3.3 V, full scale is 333 V (calc), so the 72 V bus uses about 22 % of the ADC range.
* Source impedance 20.0k || 2.02M = 19.8k. With C_HV1 10 nF: fc = 1 / (2 pi x 19.8k x 10 nF) = 0.80 kHz (calc).
* Divider current at 72 V: 36 uA, about 2.6 mW (calc). Each 1206 1M sees about 36 V (calc), well under its 200 V field rating.
* The value field says R_HV_BOT1 `20.0k 0.1%`, but the MPN RC0603FR-0720KL is a 1 % part (owner question).

### Archived sheet notes (pre-2026-11-17, verbatim; they do NOT match the fitted parts)
```
SECTION 1: CONTACTOR TERMINAL INTERFACE
J_CONT1: Phoenix MKDS 6-pin heavy duty terminal block
Pinout: POS Coil (+/-), NEG Coil (+/-), PRE Coil (+/-)

SECTION 2: MAIN POSITIVE CONTACTOR DRIVER
Driver: Q_POS1 SQ2318EY 40V 8A N-MOSFET
Gate Protection: D_Z_POS1 BZX84-C18 (18V Clamp)
Flyback Clamp: D_FLY1 S3M 1000V 3A Fast Diode
State Monitor: D_LED_P1 Blue Active LED

SECTION 3: MAIN NEGATIVE CONTACTOR DRIVER
Driver: Q_NEG1 SQ2318EY 40V 8A N-MOSFET
Gate Protection: D_Z_NEG1 BZX84-C18 (18V Clamp)
Flyback Clamp: D_FLY2 S3M 1000V 3A Fast Diode
State Monitor: D_LED_N1 Blue Active LED

SECTION 4: ACTIVE SOLID-STATE PRE-CHARGE STAGE
R_PRE1: 47 Ohm 25W Chassis Mount Power Resistor
Inverter Bus Pre-charge Time: tau = R*C = 47 * 2000uF ~ 94ms
Driver: Q_PRE1 SQ2318EY, Gate Clamp D_Z_PRE1, Flyback D_FLY3
State Monitor: D_LED_R1 Yellow Pre-Charge Active LED

SECTION 5: INVERTER DC-LINK VOLTAGE SENSE DIVIDER
Divider: R_HV1 (1M) + R_HV2 (1M) + R_HV_BOT1 (68k), C_HV1 (100nF)
Ratio: 30.4 : 1 (100V Inverter Bus mapped to 3.28V MCU ADC)
```
Differences from the fields: S3M -> SS34 (D_FLY1-3); 47R -> 50R (R_PRE1); 68k -> 20.0k (R_HV_BOT1); 100nF -> 10nF (C_HV1); 30.4:1 -> 101:1 (calc); blue / yellow LEDs -> green, green, amber (D_LED_P1 / N1 / R1 values).

Old title block (replaced): "High-Voltage Power Actuators, Contactors & Pre-Charge Stage"; comment 1 "Main Positive & Negative Low-Side Contactor Drivers (SQ2318EY, 40V 8A N-MOSFET)"; comment 2 "18V Gate-Source Zener Clamps (BZX84-C18) & Inductive Flyback Diodes (S3M 1000V 3A)"; comment 3 "Solid-State Active Pre-Charge Circuit with 25W High-Energy Power Resistor (47-Ohm)"; comment 4 "Sheet 6/7: High-Current Actuation & Inverter Bus Pre-Charge".

## 06_Communications.kicad_sch

Source: `plan_isolated_comms.md`.

```
Ports (plan 1): isolated CAN-FD up to 5 Mbps; isolated RS-485 Modbus RTU 115.2 kbps; barrier >= 2.5 kVrms for
  signals (digital isolators) and power (isolated DC-DC)
CAN (plan 2.1): TCAN1042V-Q1, ISO7721-Q1, common-mode choke 51-100 uH, NUP2105L / PESD2CAN,
  split termination 2 x 60.4 R with 4.7 nF to GND_ISO
RS-485 (plan 2.2): THVD1429-Q1, direction from the MCU through an isolator, bias 560 R to +5V_ISO and to GND_ISO, SM712
```

Schematic today: TJA1051T/3 (sheet note "or TCAN1042-Q1"), THVD1450DR on the SN65HVD11HD symbol, no common-mode choke, three ISO7721 (CAN, RS-485 data, RS-485 direction), R_TRM_485 120 R, connectors carry `+5V_ISO` and `GND_ISO`.

To do:
* `+5V_ISO` budget: transceivers, isolator secondary sides, bias network, LED, against the U4 rating and its minimum load.
* Logic levels across the isolators (3.3 V side VCC1, 5 V side VCC2) and the default output state with the MCU side unpowered.
* Bias network: idle differential voltage with 560 R / 120 R / 560 R; bus loading in a multi-node network.
* Termination: whether the fixed 120 R and 2 x 60.4 R should be switchable (jumper / DNP).
* TVS working voltage against the bus common-mode range; creepage across each isolator and U4.
* Decision on the CAN common-mode choke.

### Sheet 06 - Communications (`06_Communications.kicad_sch`)

Redrawn 2026-11-17 to the house style (Task 5). Connectivity unchanged (netcmp identical, 165 net names identical). The text below archives the notes and title-block text that were on the sheet before the redraw, and says which parts of it are stale. Nothing here was checked against a datasheet.

### Fitted circuit (from the netlist)
* MCU side `+3V3` / `GND_PWR`; isolated side `+5V_ISO` / `GND_ISO`. The barrier runs through U_ISO_CAN1, U_ISO_485A and U_ISO_485B (ISO7721-Q1, ISO7721QDRQ1).
* CAN: `CAN_TX` / `CAN_RX` -> U_ISO_CAN1 -> `CAN_TX_ISO` / `CAN_RX_ISO` -> U_CAN1 TJA1051T/3 (S pin 8 on `GND_ISO`, pin 5 not connected, see below) -> `NET_CANH` / `NET_CANL` -> split termination R_TRM1 / R_TRM2 60.4 R 1 % to `NET_CAN_SPLIT`, C_TRM1 4.7 nF 50 V to `GND_ISO` -> D_TVS_CAN1 NUP2105LT1G -> J_CAN1 (1 CANH, 2 CANL, 3 `GND_ISO`, 4 `+5V_ISO`). Decoupling: C_ISO_C1 / C_ISO_C2 100 nF on the isolator, C_CAN1 100 nF + C_CAN2 4.7 uF on U_CAN1 VCC.
* RS-485: `RS485_TX` / `RS485_RX` -> U_ISO_485A, `RS485_DIR` -> U_ISO_485B (OUTA no-connect, INA on `GND_ISO`) -> `RS485_TX_ISO` / `RS485_RX_ISO` / `RS485_DIR_ISO` -> U_485_1 THVD1450DR on the `Interface_UART:SN65HVD11HD` symbol, ~RE and DE joined on `RS485_DIR_ISO` -> `RS485_A` / `RS485_B` -> R_TRM_485 120 R 1 % A-B, fail-safe bias R_FS_A1 560 R A to `+5V_ISO`, R_FS_B1 560 R B to `GND_ISO` -> D_TVS_485_1 SM712-02HTG -> J_485_1 (1 A, 2 B, 3 `GND_ISO`, 4 `+5V_ISO`). Decoupling: C_ISO_485 100 nF on U_ISO_485A VCC1, C_485_1 100 nF on U_485_1 VCC.
* calc: split termination 2 x 60.4 R = 120.8 R differential.

### Open points (owner decisions, not fixed)
* U_CAN1 is drawn with the `TJA1051T` symbol, whose pin 5 is NC. On the TJA1051T/3 pin 5 is VIO. It is unconnected on the schematic.
* U_485_1 is a THVD1450DR on the SN65HVD11HD symbol (same 8-pin RS-485 function names; pin-out not DS-checked).
* No decoupling on VCC2 of U_ISO_485A / U_ISO_485B, and none of its own on U_ISO_485B VCC1 (only C_ISO_485 on U_ISO_485A VCC1).
* J_CAN1 / J_485_1 export `+5V_ISO` to the bus connector with no fuse or current limit.

### Archived sheet text (before the redraw, 2026-11-17)
Title: `Galvanically Isolated CAN-FD & RS-485 Modbus Telemetry Stage`

Title-block comments:
1. `High-Speed Dual Digital Isolators (ISO7721D, 3000Vrms Withstand, 100Mbps)`
2. `Automotive High-Speed CAN-FD Transceiver (TJA1051T/3) with Split Termination & NUP2105L TVS`
3. `Industrial RS-485 Modbus Transceiver (SN65HVD11HD) with Fail-Safe Biasing & SM712 TVS` - **stale**: the fitted part is THVD1450DR.
4. `Sheet 7/7: External Telemetry & Inverter Comms Architecture`

Notes:
* SECTION 1: 3.0kVrms DIGITAL GALVANIC ISOLATION BARRIER / U_ISO_CAN1 & U_ISO_485A/B: ISO7721D Dual Digital Isolators / Withstand Voltage: 3000Vrms per UL 1577 / Data Rate: Up to 100 Mbps (CAN-FD & High-Speed UART compatible). (Ratings not DS-checked.)
* SECTION 2: AUTOMOTIVE HIGH-SPEED CAN-FD TRANSCEIVER / IC: TJA1051T/3 (or TCAN1042-Q1) CAN-FD Physical Layer / Termination: Split 60 Ohm (R_TRM1) + 60 Ohm (R_TRM2) + C_TRM1 (4.7nF) / Common-Mode Noise Filtering & Ground Return Decoupling. (Stale: "or TCAN1042-Q1" is not fitted; resistors are 60.4 R.)
* SECTION 3: CAN-FD BUS TRANSIENT & ESD PROTECTION / D_TVS_CAN1: NUP2105LT1G SOT-23 AEC-Q101 Dual TVS Array / Protection: ISO 10605 +/-30kV ESD & ISO 7637-3 Pulse Clamp / J_CAN1: Isolated CAN-FD Connector (CANH, CANL, GND_ISO, +5V_ISO). (Ratings not DS-checked.)
* SECTION 4: INDUSTRIAL RS-485 MODBUS TRANSCEIVER / IC: SN65HVD11HD Industrial RS-485 Transceiver / Fail-Safe Biasing: R_FS_A1 (1k to 5V_ISO), R_FS_B1 (1k to GND_ISO) / Bus Termination: R_TERM_485 (120 Ohm, 1%). (Stale: part is THVD1450DR; bias resistors are 560 R; the reference is R_TRM_485.)
* SECTION 5: RS-485 ASYMMETRICAL SURGE PROTECTION / D_TVS_485_1: SM712 SOT-23 Asymmetrical TVS (-7V to +12V) / Protection: IEC 61000-4-2 ESD & IEC 61000-4-5 Lightning Surge / J_485_1: Isolated RS-485 Modbus Connector (A, B, GND_ISO, +5V_ISO). (Ratings not DS-checked.)

## PCB and manufacturing

Sources: `plan_pcb_manufacturing.md`, `instructions.md` §4.

```
Stackup JLC04161H-7628 (plan): Top 0.035 / prepreg 7628 0.21 (Er about 4.6) / In1 0.035 solid GND / core 1.065 /
  In2 0.035 power planes / prepreg 0.21 / Bottom 0.035; total 1.625 mm; board 160 x 100 mm; ENIG
Isolation (plan 2): 60-400 V class: clearance >= 4.0 mm, creepage >= 6.5 mm (pollution degree 2);
  1.5 mm milled slot under all isolators and the isolated DC-DC
Thermal (plan 3): U1 pad 3 x 3 vias 0.3 / 0.6 mm into In1; balance resistors on B.Cu >= 3.0 mm apart with pours;
  shunt 12 stitching vias per side for 4.0 W
Rules (instructions.md 4.2): track / space 0.127 mm, via 0.45 / 0.20 mm, ring 0.125 mm, hole to hole 0.50 mm,
  copper to edge 0.30 mm, mask expansion 0.05 mm, mask dam 0.10 mm, silk 1.0 mm / 0.15 mm
Net classes (instructions.md 4.3): Default 0.20 / 0.15; Power_HV 1.00 / 0.80; Power_LV 0.50 / 0.25;
  Balance_Lines 0.40 / 0.30; CAN_Bus 0.254 / 0.25 (100 R differential); Current_Sense 0.254 / 0.25
```

Board today: see `PROJECT.md` section 6 (script-routed, not usable as it stands; no net is assigned to a net class; no stackup stored in the board file).

To do:
* Track widths from current (IPC-2152, assumptions stated) for `V_BATT+`, `+12V` coil paths, balance lines.
* Creepage / clearance actually achieved: barrier, cell-tap connector (adjacent taps up to one cell, end to end full pack), J_PRE1, J1.
* CAN differential impedance from the stackup.
* Fab limits re-checked against the current JLCPCB capability page.
