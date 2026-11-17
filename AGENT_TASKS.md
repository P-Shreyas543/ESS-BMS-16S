# AGENT_TASKS.md — task queue for the working agent (Automotive ESS BMS)

This file is the hand-over between the **working agent** (does the work in this folder) and the **reviewer** (checks each finished task and writes the next one). The **owner** makes every design decision.

## Read before every task
1. `instruction.md` (generic playbook: workflow, visual standard, verification) — follow it.
2. `PROJECT.md` (facts, nets, decisions log — it overrides the playbook for this project).
3. This file: do the **first task whose status is TODO**, then stop.

## Standing rules (they apply to every task)
* **One task at a time.** Finish it, verify it, write the report at the bottom of this file, set its status to `DONE - waiting for review`, and **stop**. Do not start the next task.
* **Schematic as drawn is the design** (owner 2026-11-16). Do not add, remove, re-value or swap any part, and do not rename any net, unless the task says so. If you think a circuit change is needed, write it under "Questions for the owner" and carry on with the rest.
* **Connectivity must not change** in a redraw task. Prove it: export the netlist before and after and run `python tools/schematic/netcmp.py before.net after.net` → it must print `connectivity identical: True`, and the set of net names must be the same.
* **Do not touch the PCB** (`*.kicad_pcb`) and do not run *Update PCB from Schematic*. Layout restarts later.
* **Do not run anything in `scripts/`.** Those are old one-off scripts that overwrite the live files without a backup.
* **Do not delete, move or rename existing files.** Do not add reports, netlists or renders to the project root: put scratch output in a folder **outside** the project (e.g. `%TEMP%\bms_work\<task>\`).
* **KiCad must be closed** while files are edited (`python tools/check_env.py .`). If the owner has it open, stop and say so.
* Keep existing symbol UUIDs. Script edits with `tools/schematic/kisexp.py`; pin positions with `tools/schematic/pins.py`.
* **No git commit / push** unless a task says so. Work on branch `rework-2026-11`.
* Never invent a part number, datasheet value or page. Unknown → question for the owner.
* Report honestly: what was done, what failed, what was skipped.

## Report format (append under "Reports", newest last)
```
### Task <n> — <title> — <date>
Status: DONE - waiting for review | BLOCKED (why)
Files changed: ...
Evidence: netcmp line; net-name diff; ERC errors / warnings (kicad-cli sch erc --severity-all on the ROOT sheet); renders looked at (paths outside the project)
What changed (short list):
Not done / left as is (and why):
Questions for the owner:
```

---

## Task 1 — Redraw `01_Power_Supply.kicad_sch` to the playbook style — **DONE - waiting for review**
Goal: the sheet is readable by a reviewer; electrically nothing changes.

Starting point (baseline 2026-11-16, see `PROJECT.md`): 42 parts on this sheet; no wire or junction anywhere; every pin has its own global label; rails and grounds are global labels, not power symbols; reference and value text overlap; notes overlap parts; some notes name parts that are not fitted (e.g. LMR14006, TPS7A2533).

Do:
1. Pre-flight (`instruction.md` §4.1-4.4): KiCad closed; copy the whole project to a scratch folder outside the project and work there; back up the sheet; dump every symbol with its fields; export `before.net`; run ERC; render the sheet.
2. Redraw per `instruction.md` §6 and §7:
   * signal flow left → right in the order of the power tree (pack input and protection → stage 1 buck → stage 2 buck → 3.3 V LDO → isolated 5 V);
   * connect the pins with **wires**; keep one name label per net; nets that leave the sheet keep their global label name exactly (changing global labels to power symbols or hierarchical labels is allowed only if every net keeps the identical name in the netlist — if that cannot be guaranteed, keep the global labels and say so);
   * decoupling capacitors wired to their own IC pin, 8.89 mm pitch, vertical text; series parts (fuse, inductor, bead) in the rail; grounds pointing down, supplies up;
   * every functional block in a dashed box with a title (`NAME - key parts (key spec)`), boxes 1.27 mm apart, drawing centred above the title block;
   * text: fields and labels 0.8 mm, notes and box titles 1.0 mm; nothing touching a wire, pin, symbol, other text or box border; everything on the 1.27 mm grid;
   * notes: 1-4 short lines per block, and they must be true for the parts that are actually fitted. Remove statements about parts that are not on the sheet; move long calculations to `DESIGN_NOTES.md` (section for sheet 01) instead of deleting them.
3. Do **not** change part fields other than text position / size (no Value, MPN, LCSC, Footprint edits). List field problems you notice as questions.
4. Verify (`instruction.md` §9): netcmp identical; same net names; ERC on the root not worse than the baseline (0 errors / 0 warnings); render the whole page and every box zoomed in and look at each image.
5. Install the one sheet file into the project only when step 4 passes. Update `PROJECT.md` §1.1 status for sheet 01 and add a dated row to its decisions log describing the redraw (no owner decision invented).
6. Write the report below and stop.

## Task 2 — Redraw `03_MCU_Control.kicad_sch` — **DONE - waiting for review**
## Task 3 — Redraw `04_Current_Sensing.kicad_sch` — **DONE - waiting for review**
## Task 4 — Redraw `05_Power_Actuators.kicad_sch` — **DONE - waiting for review**
## Task 5 — Redraw `06_Communications.kicad_sch` — **DONE - waiting for review**
## Task 6 — Redraw `02_AFE_Cell_Monitor.kicad_sch` (largest sheet, A2) — **DONE - waiting for review**
## Task 7 — Root sheet tidy and title blocks — WAITING
## Later (need owner decisions first, see `PROJECT.md` §8): MOSFET symbol pin mapping, part-data fields and live part check, electrical review, folder clean-up, PCB layout restart.

---

## Questions for the owner (collected from the tasks)
* (Task 1) **D1 SMCJ64A - possible blocker.** An MPN without "C" is normally a unidirectional TVS; the symbol is the bidirectional `Device:D_TVS`. Netlist: D1 pad 1 = `GND_PWR`, pad 2 = `NET_FUSE`; on `Diode_SMD:D_SMC` pad 1 is the cathode. If the part is unidirectional, it is forward-biased across the pack input and blows F1. Also its 64 V stand-off is below the 68-72 V maximum pack voltage. Datasheet not opened. Options: (a, recommended) check the datasheet, then choose a TVS (e.g. a bidirectional or higher-stand-off part) to the owner's spec; (b) keep the part and swap the pad nets. Both change the circuit, so the owner decides.
* (Task 1) Field contradictions on sheet 01 (already in `PROJECT.md` section 3): R1 `2.4M` vs MPN `RC0603FR-07100KL` (100k); C_FF1 `47pF` vs MPN `...BB103` (10 nF); U4 Mornsun B0505S-1WR3 on the Murata CRE1 symbol and footprint (pin-out, isolation rating vs the planned 2.5 kVrms, minimum load not checked).
* (Task 1) `PWR_PGOOD` (U1 PGOOD + R_PG1 100k) goes nowhere else. Route it to an MCU pin, or leave it as is?
* (Task 1) D7 is a green LED on `+3V3` through 1.0k. If Vf is about 3 V (playbook 3.3), it will be dim or vary with the part. Keep it?
* (Task 1) Bench input J2 -> D3 -> `+12V` has no fuse or TVS. Intended?
* (Task 1) Style: (1) `GND_PWR` hides its name (playbook: the card ground hides it) and `GND_ISO` shows it. OK, or show `GND_PWR` everywhere? (2) Internal nets (`NET_FUSE`, `NET_LM_SW` ...) stay **global** labels, because a local label would rename the net to `/Power_Supply/...`. OK, or allow that rename later? (3) Pin-name text on the stock library symbols stays 1.27 mm, because editing the embedded copies raises `lib_symbol_mismatch`. OK? (4) The project default text size (`.kicad_pro`, 50 mil) is not changed. Set it to 31.5 mil in Task 7?
* (Task 1) Later standardisation, not done: `Spec` field, JLC links in `Datasheet`, field order (the sheet has LCSC / Manufacturer / MPN; the playbook wants MPN / Manufacturer / LCSC), test points (proposal: hooks on `V_BATT+`/`V_IN_BUCK`, `+12V`, `+5V`, `+3V3`, `+5V_ISO` plus a `GND_PWR` and a `GND_ISO` hook), and hot-part symbols for U1 / D2 (these need datasheet Pd).
* (Task 1) Title block: date `2026-10-27` and rev `v1.0` kept. Which date and revision should be used from now on (`PROJECT.md` section 8, question 11)?


## Reports
### Task 1 — Redraw `01_Power_Supply.kicad_sch` — 2026-11-17
Status: DONE - waiting for review
Files changed: `01_Power_Supply.kicad_sch`, `symbols/Automotive_ESS_BMS.kicad_sym` (4 new power symbols), `DESIGN_NOTES.md` (sheet-01 archive), `PROJECT.md` (section 1.1 status, decisions-log row), this file. Backup of the originals: `%TEMP%\bms_work\task1\backup\`. Scripts (reusable for the other sheets): `%TEMP%\bms_work\task1\scripts\` (`schlib.py`, `build_sheet01.py`, `verify.sh`, `netnames.py`, `zooms.py`, `fontcount.py`, `fieldcheck.py`, `dump_sheet.py`).
Evidence: `netcmp.py baseline\before.net task1\out\final\after.net` -> `connectivity identical: True`; net-name sets identical (165 / 165). The power symbols merge with the other sheets' global labels of the same name. ERC `--severity-all` on the root: 0 errors / 0 warnings on all 7 sheets ("Found 0 violations"), the same as the baseline. All 47 original symbols kept, with the same UUIDs, lib_ids and field values (`fieldcheck.py`). Fonts: 456 fields and 14 labels at 0.8 mm; 6 notes and 6 bold titles at 1.0 mm; nothing else (`fontcount.py`). The geometry check reports no unconnected pin, no dangling wire and no wire crossing. Renders looked at: `%TEMP%\bms_work\task1\out\final\full.png`, `z0_INPUT_PROTECTION.png` ... `z5_ISOLATED_5_V.png` (12 px/mm), `z_titleblock.png`.
What changed (short list):
* Label-only drawing replaced by wires (163 segments, split at every pin, 56 junctions). Parts moved to the 1.27 mm grid, in power-tree order. Row 1: input protection -> +12V buck -> +5V buck. Row 2: bench 12 V input -> +3V3 LDO -> isolated 5 V. The drawing is centred on the A3 page.
* Rails: `+12V` `+5V` `+3V3` use stock `power:` symbols. `GND_PWR` `GND_ISO` `+5V_ISO` `V_BATT+` use new project symbols (copies of `power:GND` / `+5V` / `+12V`, pin `power_in`). 19 new `#PWR11..29` symbols. The 5 PWR_FLAGs are kept on the same nets.
* Each internal net keeps exactly one global label with the same name (14 labels).
* Decoupling caps sit on their IC's rail and pin, at 8.89 mm pitch, with vertical text. F1, L1, L2, D2 and D3 sit in the rail. Bootstrap caps go from BST/CB to SW. Each rail LED (R + LED) sits at the end of its rail.
* 6 dashed boxes with bold titles. Notes are 2-4 short lines that are true for the fitted parts. The stale notes and title-block comments are replaced. The title is shortened because it ran out of the title block. The old text is archived in `DESIGN_NOTES.md`.
Not done / left as is (and why): no `Spec` field, test points or hot-part symbols (later owner decision; the Pd numbers need datasheets). Pin-name text on stock symbols stays 1.27 mm (avoids `lib_symbol_mismatch`). `.kicad_pro` default text size not changed. Title-block date / rev not changed. No part data was checked live (not in scope).
Questions for the owner: see "Questions for the owner" above (items marked Task 1). The D1 TVS orientation is the important one.

### Task 2 — Redraw `03_MCU_Control.kicad_sch` — 2026-11-17
Status: DONE - waiting for review (prepared in scratch by a subagent, merged and installed by the coordinator)
Files changed: `03_MCU_Control.kicad_sch`; `symbols/Automotive_ESS_BMS.kicad_sym` (new power symbol `+3V3_A`, copy of `power:+3V3`, pin `power_in`). Backup: `%TEMP%\bms_work\03_MCU_Control\backup\`. Script: `...\03_MCU_Control\scripts\build_sheet03.py`.
Evidence (scratch copy): netcmp `connectivity identical: True`; net names 165/165 identical; ERC --severity-all on root 0 violations; fieldcheck 26/26 symbols unchanged; fonts 0.8 / 1.0 mm only; renders `out\renders\full.png` + 6 box zooms at 12 px/mm.
What changed: wires (104 segments, 26 junctions); 6 boxes on A3 (RESET/WATCHDOG/BOOT, CONFIG SWITCH, MCU, SWD, SPI EEPROM, HEARTBEAT); signal labels on the MCU pin stubs; crystal wired to PF0/PF1; decoupling staircase on VBAT/VDD; VDDA → C_A2, C_A1, `+3V3_A`, PWR_FLAG `#PWR100`, FB1, `+3V3`; power symbols `#PWR301`–`#PWR327`; notes true for the fitted parts; old notes archived in DESIGN_NOTES.
Not done / left as is: known faults drawn as is (`AFE_SDA` on PB7 and PB9, PB6 = `AFE_SCL`); internal MCU-to-peripheral nets carry a label at both ends (style question); no Spec field / test points / live part check.
Questions for the owner: (1) label at MCU pin and at peripheral, OK? (2) I2C pins; (3) TPS3823-33DBVR is not the Q1 part — which to fit? (4) `MCU_RESET_N` driven by U_WDOG1, NRST and the SWD probe: check TPS3823 output type; (5) decoupling vs STM32G431 DS (VBAT no own cap, no bulk); (6) C_X1/C_X2 18 pF vs Y1 CL; (7) PC13 drive of D_HB1; (8) page numbering (Task 7).

### Task 3 — Redraw `04_Current_Sensing.kicad_sch` — 2026-11-17
Status: DONE - waiting for review (prepared and verified in scratch; NOT installed — the reviewer merges)
Files changed: `04_Current_Sensing.kicad_sch` only (scratch copy). No change to `symbols/Automotive_ESS_BMS.kicad_sym` (no new power symbol: `+5V`, `+3V3` stock, `GND_PWR` from Task 1). `.kicad_pro`, PCB and other sheets untouched. Proposed `DESIGN_NOTES.md` text: `%TEMP%\bms_work\04_Current_Sensing\out\design_notes_section.md`. Backup of the original sheet: `%TEMP%\bms_work\04_Current_Sensing\backup\`. Scripts: `%TEMP%\bms_work\04_Current_Sensing\scripts\` (`build_sheet04.py` + the Task 1 helpers; `verify.sh` pointed at `baseline2`).
Evidence:
* `netcmp.py baseline2\before.net out\after.net` -> `connectivity identical: True`.
* `netnames.py` -> `net names: before 165, after 165, identical: True`.
* ERC `--severity-all` on the root: "Found 0 violations"; 0 errors / 0 warnings on all 7 sheets (`out\erc.rpt`), same as the baseline.
* `fieldcheck.py`: original symbols 19, kept with same UUID / lib_id / fields: 19; new symbols: 14 (`#PWR401`-`#PWR414`).
* `fontcount.py`: 220 fields and 8 labels at 0.8 mm; 4 notes and 4 bold titles at 1.0 mm; non-house sizes: none.
* Geometry check (`schlib.check`): no unconnected pin, no dangling wire, no wire crossing; all placements and wires on the 1.27 mm grid (asserted by the script).
* KiCad closed (`check_env.py`: "KiCad closed", no lock files).
* Renders looked at (boxes 12 px/mm, page 5 px/mm): `out\renders\full.png`, `z0_SHUNT_INPUT.png`, `z1_INPUT_FILTER.png`, `z2_CURRENT_SENSE_AMP.png`, `z3_OVER_CURRENT_TRIP.png`, `z_titleblock.png`. No overlaps, no text on wires or pins, every note inside its box.
What changed (short list):
* Label-only drawing replaced by wires (64 segments, split at every pin, 18 junctions); one row of 4 dashed boxes centred on A3, left to right: SHUNT INPUT -> INPUT FILTER -> CURRENT SENSE AMP -> OVER-CURRENT TRIP.
* Kelvin pair drawn as two parallel lines 20.32 mm apart (`SH_P`/`AMP_IN+` on top, `SH_N`/`AMP_IN-` below) from J_KELVIN1 through R_K1 / R_K2 to the INA240 inputs. R_NT1 hangs from `SH_P` to `GND_PWR`; C_K2 / C_K3 from each line to ground; C_K1 and D_TVS_SHUNT1 across the pair.
* Rails as power symbols (`+5V`, `+3V3`, `GND_PWR`; refs `#PWR401..414`, a range chosen so they cannot collide with the sheets redrawn in parallel). C_AMP1 / C_AMP2 wired to INA240 V+, C_CMP1 to TLV3501 V+. One `+3V3` rail feeds R_TH1, U_OCP1 V+, C_CMP1, R_OCP_PU1, R_OCP_LED1. SHDN is wired to its own `+3V3` symbol so the known fault stays visible.
* One global label per net with the original name (`SH_P`, `SH_N`, `AMP_IN+`, `AMP_IN-`, `ADC_I_SENSE`, `V_TH_OCP`, `OCP_TRIP_N`, `NET_LED_OCP`). No local labels. No PWR_FLAG on this sheet (none before).
* Notes: 3-4 short lines per box, true for the fitted parts. No trip current on the sheet (only `V_TH_OCP = 3.15 V (calc)` from R_TH1 / R_TH2). Stale notes (R_SHUNT1, 2.90 V / 250 A, "latch") and old title-block comments archived verbatim in `design_notes_section.md`, with the calculations.
* Title shortened to "Current Sensing - Shunt Amplifier and Over-Current Trip"; comments 1-3 rewritten for the fitted parts; comment 4 keeps "Sheet 5/7". Date / rev unchanged.
Not done / left as is (and why):
* Known faults NOT fixed (owner decisions): TLV3501 SHDN tied to `+3V3`; no trip latch (`OCP_TRIP_N` goes to MCU PA8 and the LED only).
* No part, value, MPN, LCSC, footprint, DNP or net changed. No live part check; no datasheet opened in this task.
* Unused embedded `Device:R_Shunt` lib symbol (left over from R_SHUNT1) stays in `lib_symbols` (no instance; harmless).
* Pin-name text on stock symbols stays at library size (as Task 1). Boxes share one height, as on sheet 01, so the OVER-CURRENT TRIP box has empty space under its note.
* Project `PROJECT.md`, `DESIGN_NOTES.md`, `AGENT_TASKS.md` not edited (parallel run; reviewer merges). Suggested: `PROJECT.md` §1.1 status for sheet 04 "redrawn 2026-11-17, waiting for owner review" and a decisions-log row like Task 1's.
Questions for the owner:
1. **Trip current / shunt.** R_TH1 4.7k / R_TH2 100k give `V_TH_OCP = 3.152 V` (calc) = about 300 A with the plan's 100 uOhm shunt. Old sheet note: 2.90 V / 250 A; plan: 3.15 V / 500 A. Which trip current is intended, and which external shunt (value, part) goes on J_KELVIN1? The shunt sets every current figure on this sheet.
2. **TLV3501 SHDN tied to `+3V3`** (review: this disables the comparator). Options: (a, recommended after a datasheet check) tie SHDN to its enable level, or to an MCU pin for a self-test; (b) keep. Circuit change -> owner decides.
3. **No hardware latch / no direct action on the contactors.** The plan wanted a latch that removes contactor gate drive in < 2 us; today `OCP_TRIP_N` only reaches MCU PA8 and the LED. Add a latch (with a reset path), or leave it to firmware?
4. **Voltage on `ADC_I_SENSE`.** U_ISENSE1 runs from `+5V`, so its output can exceed 3.3 V at large currents or faults; it drives MCU PA0 and the TLV3501 input (comparator on `+3V3`). Check both input limits (datasheets not opened); clamp / divider, or 3.3 V supply for the INA240?
5. **J_KELVIN1 fields** (already in `PROJECT.md` §3): MPN `MKDS 1,5/ 2-5,08` (5.08 mm terminal), footprint 2.54 mm pin header, LCSC C224345 (pin header). Which connector is meant?
6. **R_NT1** has no Manufacturer / MPN. Also confirm that `SH_P` is the ground-side shunt terminal (it is tied to `GND_PWR` through R_NT1).
7. **D_OCP1** was called a "latched" indicator in the old notes; it lights only while `OCP_TRIP_N` is low, so a short trip may not be visible. OK as is?

### Task 4 — Redraw `05_Power_Actuators.kicad_sch` — 2026-11-17
Status: DONE - waiting for review (prepared in scratch by a subagent, merged and installed by the coordinator)
Files changed: `05_Power_Actuators.kicad_sch` only. Backup: `%TEMP%\bms_work\05_Power_Actuators\backup\`. Script: `...\05_Power_Actuators\scripts\build_sheet05.py`.
Evidence (scratch copy): netcmp `connectivity identical: True`; net names 165/165 identical; ERC --severity-all on root 0 violations; fieldcheck 28/28 unchanged + `#PWR501`–`#PWR512`; fonts 0.8 / 1.0 mm only; geometry check clean; renders `out\final\full.png` + box zooms.
What changed: wires (104 segments, 25 junctions), A3; three identical aligned driver channels with a non-crossing staircase into J_CONT1 (each J_CONT1 `+12V` pin has its own `+12V` symbol); PRE-CHARGE and BUS SENSE boxes; one global label per non-rail net (16); notes true for the fields (50R, SS34, 20.0k, 101:1 calc).
Not done / left as is: Q_NMOS D/G/S (owner question); no Spec field / test points / live part check.
Questions for the owner: (1) R_HV_BOT1 value 0.1 % vs MPN 1 %; (2) 101:1 uses ~22 % of the ADC at 72 V — intended?; (3) J_PRE1 pin 1 → pin 2 has no on-board link: pre-charge switch off-board? bus capacitance? R_PRE1 25 W vs 104 W peak at 72 V (calc) unchecked; (4) SQ2318EY at 3.3 V gate drive — RDS(on) and coil current unchecked; (5) SS34 flyback slows release — keep?; (6) LED colours kept per fields; (7) `#PWR5xx` per-sheet numbering OK?

### Task 5 — Redraw `06_Communications.kicad_sch` — 2026-11-17
Status: DONE - waiting for review (prepared in scratch by a subagent, merged and installed by the coordinator)
Files changed: `06_Communications.kicad_sch` only. Backup: `%TEMP%\bms_work\06_Communications\backup\`. Script: `...\06_Communications\scripts\build_sheet06.py`.
Evidence (scratch copy): netcmp `connectivity identical: True`; net names 165/165 identical; ERC --severity-all on root 0 violations; fieldcheck 21/21 kept (DNP/BOM/instances unchanged); fonts 0.8 / 1.0 mm only; renders `out\final\full.png`, z0..z5 at 12 px/mm.
What changed: wires (127 segments, 17 junctions); two rows (CAN, RS-485) × three boxes (isolators, transceivers, bus ports); TVS last before each connector; dark-red dashed isolation barrier through all three ISO7721s with MCU-side / isolated-side notes and "barrier: never join GND_ISO to GND_PWR"; power symbols `#PWR601`–`#PWR632`; one global label per net (15); title block no longer names SN65HVD11HD. Three unavoidable plain wire crossings (reversed pin order): CAN_TX_ISO/CAN_RX_ISO, RS485_TX_ISO/RS485_DIR_ISO, RS485_B/RS485_A.
Not done / left as is: TJA1051T/3 pin 5 VIO unconnected (owner decision; noted on the sheet); no Spec field / test points / part check.
Questions for the owner: (1) U_CAN1 VIO: TJA1051T/3 symbol with VIO to `+5V_ISO` (recommended) or a variant without VIO; (2) THVD1450DR on the SN65HVD11HD symbol: confirm pin-out or make a symbol; (3) no decoupling on U_ISO_485A VCC2 and U_ISO_485B VCC1/VCC2 — add 100 nF each?; (4) `+5V_ISO` on connector pin 4 without fuse / current limit; (5) termination and bias always fitted — is this node always the bus end?; (6) `#PWR6xx` numbering and the dark-red barrier line OK?

### Task 6 — Redraw `02_AFE_Cell_Monitor.kicad_sch` — 2026-11-17
Status: DONE - waiting for review (prepared in scratch by a subagent, merged and installed by the coordinator)
Files changed: `02_AFE_Cell_Monitor.kicad_sch` only (paper A2 → A3). Backup: `%TEMP%\bms_work\02_AFE_Cell_Monitor\backup\`. Script: `...\02_AFE_Cell_Monitor\scripts\build_sheet02.py`.
Evidence (scratch copy): netcmp `connectivity identical: True`; net names 165/165 identical; ERC --severity-all on root 0 violations; fieldcheck 90 symbols unchanged + `#PWR201`–`#PWR212`; fonts 0.8 / 1.0 mm only; geometry check clean (no crossings); renders `out\renders\full.png`, box and region zooms at 10–11 px/mm.
What changed: A3; wires (416 segments, 89 junctions), 12 no-connect flags kept; cell ladder by loop, one row per cell (J_CELL1 rotated 180° so CELL_16 is on top), R_BL/Q_BL between rows, R_VC in the row, C_DF column, fan-in to U_AFE1; one global label per net (65); `V_BAT_FILT` stays a global label + `#PWR_BAT`; REG caps wired to their pins; NTC: TS pin → C_NTC → D_ESD_NTC → J_NTC; 3 boxes (CELL INPUTS, AFE, TEMPERATURE); notes say passive balancing, AO3400A gate on VC(n-1); stale SQ2318EY / "active balancing" text archived.
Not done / left as is: BREG not connected, C_CP1 on V_BAT_FILT, Q_NMOS D/G/S (owner decisions); no Spec field / test points / live part check.
Questions for the owner: (1) R_VC0-16 value 100R vs MPN 1 k (filter corner 7.96 kHz vs 0.80 kHz differential, calc); (2) balance FET gate drive from the AFE balance current across R_VC — intended, enough Vgs for AO3400A?; (3) BREG → GND, CP1 → BAT?; (4) REGIN on GND, REG2 NC, REG1 cannot run — C_R1 DNP?; (5) CHG/DSG/PCHG/PDSG/FUSE NC — protection elsewhere?; (6) I2C CRC: note said CRC, U_AFE1 Description says BQ7695202 without CRC; (7) RT_BOARD fields (MPN, B value); (8) R_BL 1 % tolerance vs MPN; (9) comment 4 "Sheet 4/7".

### Merge — sheets 02–06 installed — 2026-11-17
Status: DONE - waiting for review
The five scratch sheets plus the `+3V3_A` symbol were merged into one scratch copy and checked together, then installed. Evidence on the installed project: netcmp vs the 2026-11-17 baseline `connectivity identical: True`; net names 165/165 identical; ERC --severity-all on the root 0 violations; 123 `#PWR`/`#FLG` references, no duplicate; all 7 sheets A3. Full-page renders: `%TEMP%\bms_work\merge\*.png`. Live backup before install: `%TEMP%\bms_work\merge\backup_live\`.

---

## RESUME HERE (state at end of session 2026-11-17)
1. **Architecture integration (P2): DONE 2026-11-17** — installed as `docs/ARCHITECTURE.md` (47 open decisions D-01..D-47, 16 blocking) + `docs/architecture/A..D`. Original note: Four section files are done: `%TEMP%\bms_work\arch\A_power_stage.md`, `B_power_tree.md`, `C_afe.md`, `D_mcu_comms_io.md`. An integrator agent was merging them into `%TEMP%\bms_work\arch\out\ARCHITECTURE.md` + `out\docs_architecture\*.md`. If `out\` is missing or incomplete, re-run the integration (inputs and the 10 conflict resolutions are listed below).
2. **Next steps:**
   - Check `out\ARCHITECTURE.md` yourself: conflicts resolved, rail budget ≤ 80 %, pin map has every signal.
   - Install it as `docs/ARCHITECTURE.md` + `docs/architecture/` and update `PROJECT.md`.
   - Run the privacy scan, commit as the owner, push.
   - Ask the owner the BLOCKING decisions.
3. **Agent-proposed resolutions (owner to confirm):**
   - The hardware AND gate (`FET_EN` · `OC_TRIP_N` · `MCU_NRST`) drives `AFE_DFETOFF`; the MCU is only an input.
   - `AFE_ALERT` moves to a 5 V-tolerant wake pin.
   - Pull-ups for wake, alert and AFE I2C go to `AFE_REG1`.
   - DDSG / DCHG pull-downs are 1 M.
   - `FET_EN` is pulled down (fail-safe; no live output in sleep).
   - When the sense rail is off, the FETs are held off.
   - One OV margin table, one rail budget, one protection-layer table.
4. **Blocking owner decisions (expected):**
   - inverter DC-link capacitance
   - `FET_EN` default / live output in sleep
   - two-board stack vs one board
   - 100 V FET margin (keep and prove by short-circuit test, or 150 V)
   - keep or drop +12V / EXT coil outputs
   - CAN FD vs classic
   - LM5164 cost
   - fit the USB-C port
5. **Then:** P3 part selection with a live LCSC check of every part. More than 30 wrong LCSC numbers were found in the current fields; see the section files. After that, P4 schematic v1, sheet by sheet.
6. **Git:**
   - Commit on local branch `public` (tracks `origin/main`). Commit and push as the owner after each milestone, with no agent attribution.
   - Never push `rework-2026-11` or `main`.
   - Git runs from PowerShell.
