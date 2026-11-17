# Hardware Design Agent Playbook — Schematic & PCB Engineer (KiCad)

**Audience:** any AI agent (or person) asked to design, review, finish or lay out a KiCad board. Examples: "finish this sheet", "do a BMS", "do an EIS machine", "review this project", "lay out the PCB".
**Your role:** act as a **senior schematic and PCB layout engineer**. You own correctness (electrical), readability (visual), manufacturability (fab and assembly) and evidence (checks you actually ran). The **owner** owns every design decision.

**Files in a project folder:**
* `instruction.md` (this file): generic and project-independent. Copy it unchanged into every new project.
* `PROJECT.md`: the project's facts, nets, domains, verified parts and the **binding owner-decisions log**. It overrides this file for that project. Create it on day 1 of a new project (§3.6).
* `tools/`: `check_env.py` plus `tools/schematic/` (parser, diff, netlist compare, ERC summary, render). See §12.

---

## 0. Rules that override everything else

1. **Never assume.** If a value, part, connection, rating, intent or preference is not in `PROJECT.md`, the schematic, or a datasheet you actually opened, **ask the owner**. Never decide for them.
2. **Never change a circuit decision silently.** That covers values, part numbers, topology, nets, ratings and DNP status. Explain the problem, give options with your recommendation first, and **wait for the answer**. Owners overrule "better" choices for reasons you can't see (requirements, reviewers, stock). Their decision stands. Log it in `PROJECT.md`.
3. **Never edit KiCad files while KiCad has the project open** (§4.1). Never overwrite a file the owner saved after your last read without diffing it and keeping their changes (§4.2).
4. **Connectivity must not change** unless the owner asked for it. Prove this every time with a netlist comparison (§9).
5. **Every part number is verified live** on the distributor page (JLC/LCSC: `https://jlcpcb.com/partdetail/<Cxxxx>`). Never use memory, an old BOM or an existing field without checking.
6. **Evidence or it didn't happen.** Report ERC/DRC results, netlist comparisons and rendered images honestly. Say what failed or was skipped.
7. **One unit of work at a time** (one sheet, one block, one layout stage). Finish it, check it, report, and get the owner's OK before the next.
8. **Nothing outward-facing without being asked:** no commit, push, order, upload or publish.
9. Keep `PROJECT.md` current. Every new owner decision goes into its decisions log the same day.

---

## 1. Start-up checklist (every session, before any work)

1. **Read** `PROJECT.md` (if present) fully, then this file.
2. **Environment:** run `python tools/check_env.py <project_dir>`. It checks Python ≥ 3.10, `kicad-cli` (+ version), `pypdf`, `easyeda2kicad`, a headless Edge/Chrome for renders, git, whether KiCad is running, lock files, and whether the lib tables point at existing project libraries. Install what's missing:
   * KiCad 10 from kicad.org (or set `KICAD_CLI=<path>`). Windows default: `%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe`.
   * `python -m pip install pypdf easyeda2kicad`.
   * Edge or Chrome (or set `RENDER_BROWSER=<path>`).
3. **Tools / MCP connectors:** list the tools you have. You need:
   * **Required:** web search + web fetch, for part, stock and datasheet verification.
   * **Recommended:**
     * a browser-automation tool, for JS-heavy distributor pages;
     * **BoardRepo**, to read published reference boards, run KiCad DRC/ERC and check against a fab house's limits;
     * a file connector (Google Drive or similar), for owner datasheets and specs.
   * If one is missing, tell the owner which and why, and how to add it (Claude Code: `/mcp`, `/plugin`). Don't pretend you checked something you couldn't.
4. **State of the project:** dump the hierarchy, run ERC on the root, render every sheet (§12.3), look at them, and read every note. Summarise to the owner in a few lines before you change anything.

---

## 2. Learning from an existing project (review / take over / reuse)

Use this when told "check this project", "continue this board", or when reusing a finished project as the template for a new one.
1. **Inventory:**
   * sheets and their reference ranges;
   * libraries (`sym-lib-table`, `fp-lib-table`, project `.kicad_sym` / `.pretty` / `.3dshapes`);
   * custom power symbols;
   * domains / grounds;
   * title block;
   * paper size;
   * text size;
   * PCB state.
2. **Electrical baseline:** export the netlist (keep it as `before.net`), run ERC and summarise it per sheet, and note the documented exceptions.
3. **Visual baseline:** render every sheet whole and per block. Write down the house style actually used (box style, field offsets, cap text orientation, decoupling style, test-point style) and adopt it.
4. **Part audit:** for every part check the fields, the live LCSC/MPN match, the package against the footprint, voltage/power derating and stock. Log mismatches as **questions**.
5. **Electrical review** with the §8 checklist. Give each finding:
   * severity (blocker / should-fix / note);
   * the evidence (datasheet page or calculation);
   * options, with your recommendation first.
6. Write or refresh `PROJECT.md` (§3.6). Reusable knowledge goes into the new project's `PROJECT.md` as "inherited decisions" only after the owner confirms it applies.

---

## 3. Starting a new design (e.g. "do a BMS", "do an EIS machine")

### 3.1 Requirements capture — ask, don't guess
Collect these in one structured question round, offering sensible options with a recommendation:
* Function and use case; quantity; target cost; fab/assembly house (default JLCPCB), and Basic vs Extended part policy.
* Electrical: input supply range, fault/transient conditions (hot-plug, reverse polarity, load dump), outputs (V/I range, accuracy, ripple, bandwidth), measurement accuracy and resolution, isolation (kV, which domains), safety standard.
* Interfaces: connectors, buses (CAN, RS-485, I2C, SPI, USB, Ethernet), digital I/O and their fail-safe states, debug (SWD, UART).
* Mechanical: board size, form factor (card edge, DIN, enclosure), **component height limit** (it rules out tall electrolytics, chokes and modules), layer count, connector positions, thermal environment (ambient, airflow).
* Stacking / series use: how many cards in series (e.g. 16S) → the worst-case voltage between domains, which sets connector and board creepage (§8 Isolation).
* Firmware ownership: which MCU family is acceptable, and what the firmware must guarantee (e.g. current limits, SOA trips).

### 3.2 Architecture before schematic
* Block diagram (sheet plan) with one sheet per function and reference ranges by sheet (`x1xx`, `x2xx`, …).
* **Power tree and budget:** every rail with source, regulator, load estimate, limit and % used, plus sequencing requirements (e.g. analog supply before digital), inrush and fuse I²t.
* Domains and grounds: name them, say where they may never be merged, and draw the isolation barrier.
* Interface pinout tables (connector by connector).
* Get the owner's OK on the architecture before drawing.

### 3.3 Part selection
* For each key IC: two or three candidates in a table (key spec, package, LCSC stock, Basic/Extended, price, risk), with a recommendation. Read the datasheet's absolute maximums, recommended operating conditions, layout guidance and reference design.
* Prefer parts in KiCad's libraries. Otherwise `python -m easyeda2kicad --full --lcsc_id=Cxxxx --output <dir>/lib`, then **check every pad against the datasheet land pattern** before use. Put them in the project `.pretty` / `.3dshapes` / `.kicad_sym` and register them in `fp-lib-table` / `sym-lib-table` with `${KIPRJMOD}` paths.
* Derate: MLCC voltage ≥ 2× working (and account for the DC-bias capacitance loss), electrolytics above the TVS clamp voltage, resistors ≤ 50 % of rated power, semiconductors TJ ≤ 125 °C at the worst corner.
* **Reuse parts already in the project** (fewer BOM lines, already verified). If the reused part is electrically wrong for the new spot (voltage rating, ESR that changes a filter's Q, height), say why and offer the closest part of the same family.
* MLCC dielectric: C0G for filters/timing, X7R for decoupling and bulk; avoid X5R next to hot parts (and ask the owner whether X5R is allowed at all). If a value doesn't exist in X7R in the old size, go one size up and update the footprint.
* LEDs: green/blue Vf ≈ 3 V is too close to a 3.3 V rail. Use a 5 V anode with cathodes on **5 V-tolerant** MCU pins in open-drain, LOW = on (check FT pins in the MCU pin table).

### 3.4 Domain checklists (starting points: confirm every item with the owner)
**BMS (battery management system):**
* Cell monitor AFE (stack size, cell-voltage accuracy, balancing current, daisy-chain/isolated comms), cell-tap fusing/filters (RC per datasheet), hot-plug tolerance of cell taps.
* Pack current sense (shunt plus amplifier or coulomb counter, range, accuracy), temperature (NTC count and placement).
* Protection: charge/discharge FETs (back-to-back, gate driver, SOA at the short-circuit current), pre-charge, OV/UV/OC/SC/OT thresholds and response times, secondary protector.
* Isolation to the host (CAN/RS-485 isolators, isolated DC-DC), creepage/clearance for pack voltage, standards (IEC 62619 / UL 2271 / UL 1973 as applicable).
* Wake/sleep current budget, MCU watchdog, fail-safe states (FETs off on reset).
**EIS (electrochemical impedance spectroscopy) machine:**
* Frequency range (e.g. 10 mHz–100 kHz), excitation (galvanostatic/potentiostatic, amplitude), current ranges (auto-ranging TIA / shunts), cell voltage range.
* 4-wire Kelvin connection (CE/RE/WE/sense), guarding and shielded cabling, input bias currents and leakage.
* Signal chain: DAC + reconstruction filter + power stage, synchronous V and I acquisition (matched anti-alias filters, simultaneous-sampling ADC), lock-in/DFT in firmware, reference clock.
* Calibration paths (reference resistors/dummy cells), offset/drift budget, phase-error budget vs frequency.
* Protection of the cell (current limit, disconnect relay), isolation from the host.

### 3.5 Project scaffold
```
<project>/
  <project>.kicad_pro / .kicad_sch (root) / .kicad_pcb / sub-sheets *.kicad_sch
  <project>.kicad_sym   <project>.pretty/   <project>.3dshapes/   (project libraries)
  sym-lib-table  fp-lib-table           (register the project libraries with ${KIPRJMOD} paths; keep these files)
  instruction.md  PROJECT.md  tools/    (this playbook, project facts, helper scripts)
  DESIGN_NOTES.md                        (full calculations / derivations; the sheets carry only short reviewer notes, §7.5)
  datasheets/<Type>/<MPN>_<LCSC>.pdf + datasheets/README.md   (one datasheet per purchased part + index: refs, MPN, LCSC, file)
  production/                            (generated fab outputs only; regenerate, never hand-edit)
  .gitignore                             (see §13)
```
Title block on every sheet: title, company, date, rev, and a comment line with the sheet's key parts. All sheets the same paper size (A3 default).

### 3.6 `PROJECT.md` template
Sections: 1 facts (product, company/title block, KiCad version, libraries, fab house, paper, git) · 1.1 sheets and reference ranges with status · 1.2 architecture (one line per block) · 2 nets, power symbols, domains never to merge, verified facts, known ERC exceptions · 3 verified parts (LCSC + MPN) and custom footprints · 4 project-specific style notes · 5 owner decisions log (date | decision) · 6 layout decisions · 7 scripts used.

---

## 4. Per-sheet schematic workflow (follow in order)

### 4.1 Pre-flight: KiCad must be closed
`python tools/check_env.py <project>` (or `tasklist | grep -iE 'kicad|eeschema|pcbnew'` / `ps -A`). A lock file `~<name>.kicad_pro.lck` alone may be stale. The process list decides. If KiCad is running, **stop and ask the owner to save and close it.** You may prepare and verify the change on a scratch copy meanwhile, but install only after KiCad is closed, and diff first (§4.2): the owner often saves edits while you work.

### 4.2 Detect owner edits since your last write
Compare file mtimes with your last install. If a file changed: `python tools/schematic/semdiff.py <your_last_version> <current_file>` and **adopt every owner change**. A new convention seen in an owner edit goes into `PROJECT.md` §4. A KiCad re-save with no semantic change prints only `paper` lines.

### 4.3 Back up
Copy every file you'll touch to a backup folder **outside** the project (scratch dir `backup/<step>/`). Mention the path in your report.

### 4.4 Understand the sheet
* Dump every symbol with all properties (Reference, lib_id, position, Value, Footprint, Datasheet, Description, MPN, Manufacturer, LCSC, Spec, DNP).
* Export the netlist and list the nets touching the sheet's parts.
* Run ERC and render the sheet.
* Read every note. Owner notes ("check this", "need to use this") are **questions for the owner**, never things to delete.

### 4.5 Verify part data (§5)
Check every part live. Log mismatches. If two fields disagree, ask which part is meant.

### 4.6 Ask the owner
Bundle every decision into one message (use a structured question tool if available). Recommendation first, plain-language consequences for each option.

### 4.7 Edit
* Script the edit: parse → modify → dump, using `tools/schematic/kisexp.py` (lossless round-trip). Compute pin positions with `tools/schematic/pins.py`. `tools/schematic/examples/` holds real scripts from a finished project to copy and adapt.
* Work on a **copy of the whole project** in a scratch folder until §9 passes.
* **Keep existing symbol UUIDs** so the PCB link survives. New wires, junctions, texts and power symbols get new UUIDs.
* Split wires at every pin point: KiCad does **not** connect a pin that touches the middle of a wire.

### 4.8 Verify (§9), install, report (§11)
Re-check §4.1 and §4.2 right before copying the verified files into the project.

---

## 5. Part data standard (house default; `PROJECT.md` may override)

### 5.1 Fields: exact order and visibility
Every real part (not `#PWR` / `#FLG`) has these fields in this order:

| # | Field | Visible | Content |
|---|---|---|---|
| 1 | Reference | yes | e.g. `C204` (inside the sheet's range) |
| 2 | Value | yes | short electrical value (§5.2) |
| 3 | Footprint | no | `Lib:Name` matching the real package |
| 4 | Datasheet | no | **`https://jlcpcb.com/partdetail/<LCSC>`**, so that pressing **D** in KiCad opens the exact part |
| 5 | Description | no | what it is + why it's there + datasheet limit/page (§5.3) |
| 6 | MPN | no | exact manufacturer part number |
| 7 | Manufacturer | no | as listed by the distributor |
| 8 | LCSC | no | `Cxxxxx`. The field name is exactly `LCSC` |
| 9 | Spec | yes | short visible tag (§5.2) |

Hidden fields sit at the symbol origin, angle 0. Rename non-standard field names (e.g. `LCSC Part`) in the sheet's `lib_symbols` copy too.

### 5.2 Value / Spec formats
* Capacitors: Value `22uF 25V`, `100nF 50V`. Spec = dielectric + size (`X5R 1206`, `X7R 0603`, `Polymer 6.3x5.8`, `Al 16x16.5`, `Y2 disc P7.5`).
* Resistors: Value `10k 1%`, `0R47 1%`. Spec `0603 100mW`, `2512 1W`.
* Inductors: `4.7uH`, Spec `5x5 shielded`. Fuses: `3A 125V`, Spec `2410 slow-blow`.
* Diodes/TVS: Value = MPN (`SMBJ15A`), Spec `15V 600W SMB`.
* ICs/modules: Value = full MPN. Spec = key spec (`3.3V 300mA LDO`).
* Test points: Value = net name. Spec `Red hook` / `Black hook` / `THT pad`.
* Never put an MPN in a capacitor's Value.

### 5.3 Description format
`<value> <dielectric> <voltage> <size>, <role> (<datasheet limit>, <DS> p.<page>)`, e.g. `1 uF X5R 50 V 0603, U201 input (CIN >= 0.47 uF effective, TPS7A20 DS p.5)`.

### 5.4 Verification rules
* The distributor page must show the **exact** MPN and manufacturer. If a short URL fails, search `"<MPN> LCSC"` and confirm on the product page before calling a number wrong.
* Check stock and Basic/Extended status, and mention Extended parts (setup fee) and THT parts (extra soldering cost) to the owner.
* Datasheet PDFs: download to a fresh folder and extract with `pypdf`. Scanned PDFs can't be read: say so, don't guess.

### 5.5 Test points (house default)
* **Hooks** for main rails/signals and one GND hook per area. Default: RH-5000 red C5277086, RH-5001 black C5199801, footprint `TestPoint:TestPoint_Keystone_5000-5004_Miniature`.
* **Through-hole pads** `TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm` (`in_bom no`, no LCSC, Spec `THT pad`) for secondary nodes: amplifier outputs, fault flags, SPI lines. Never SMD pads.
* Every block must let you measure each supply before and after its filter, each IC output, each reference and each fault/status line.
* **No** probe points on high-impedance or loop-internal nodes (a probe's capacitance disturbs them).
* Place test points **inline**, next to the part driving the net. No separate test-point box.
* **No** pads on filter-internal nodes (after an RC / bead), and **no duplicates** on one net (one probe point per net). Precision references get one small THT pad at their load, never a hook (a clipped lead injects noise). ADC-feeding outputs (readback buffers) get THT pads, not hooks.
* Hooks are real purchased parts: **`in_bom yes`** with LCSC. Check this; a script that set every TP to `in_bom no` silently drops all hooks from the assembly.
* Do a test-point review per board: list every TP with its net, what it proves at bring-up, and remove the ones that prove nothing new.

### 5.6 DNP parts
`(dnp yes)` with full purchasing data, plus a visible note saying why (`fit only if …`).

---

## 6. Nets, power symbols, labels

* **Rails are global power symbols**, never hierarchical pins. Custom rails (references, isolated rails, backplane rails) get project-library power symbols (copies of `power:+3V3` / `power:GND`, renamed). **Their pin must stay `power_in`.**
* Supply arrows show their Value. Card `GND` hides it. Secondary grounds (other domains) **show** their name beside the symbol.
* PWR_FLAG: one per independently driven rail, and on rails fed through a series R/L/bead. Never add one that creates `pin_to_pin`. After removing any flag, re-run ERC on all sheets.
* Local labels name real internal nodes. Hierarchical labels only for **signals** that cross sheets (inputs left, angle 180; outputs right, angle 0). On a many-pin IC (MCU), put the hierarchical label directly on the pin stub.
* A hierarchical and a local label with the same name on one sheet are the same net.
* Don't rename nets without asking (names reach the PCB). Never merge domains listed in `PROJECT.md` §2.
* No-connect flags only on unused pins of real types (passive/input/output), never on pins already typed NC/DNC.
* Multi-amplifier ICs: one triangle unit per amplifier plus a power unit, keeping the same footprint and pin numbers (see the example in `tools/schematic/examples/mkalm.py`).
* Two-pin parts keep their original pin→net order when rotated. netcmp catches a swap.
* **Bus support parts live with the chip they serve**: pull-ups, series resistors and filters go on the peripheral's sheet, not the MCU sheet (the MCU sheet holds only the MCU, its decoupling, clock, reset, boot, debug and LEDs). Renumber moved parts into the new sheet's reference range, and keep a "PCB: place next to the driver" note for source terminations.
* **Card-edge / board connectors:** draw them with **passive** pins (bare fingers drive nothing; PCIe-typed pins give false `pin_to_pin` / `power_pin_not_driven` errors). Never put signals on special-function fingers of a standard outline (PCIe `PRSNT1/2` are short last-mate fingers; `PERST`, `WAKE` have slot meaning): leave them NC. Keep the domain gap rows empty. Every rail that enters only through a connector needs a PWR_FLAG (put them in a small boxed group).
* **Library edits:** never edit a stock KiCad symbol in place (gives `lib_symbol_mismatch`). Copy it into the project library, edit there and re-point the instance. When you rename a symbol, rename its sub-units too (`<Name>_0_1`, `<Name>_1_1`): KiCad refuses to load the sheet otherwise.
* Pin-graphic styles (`input_low` wedge, `clock` triangle) are cosmetic; owners often find the wedge confusing. Plain line + overbar name is enough.

---

## 7. Visual standard (house default)

### 7.1 Sheet
* All sheets the **same paper size** (A3 default), with the drawing centred above the title block.
* Everything on the **1.27 mm grid**. Pins land exactly on wire ends.
* Title block: title, company, date (YYYY-MM-DD), rev, and comment lines that are true (no stale library names).

### 7.2 Text
* **Fields, labels, pin text, embedded lib symbols: 0.8 mm. Notes and box titles: 1.0 mm** (readable for reviewers); no `thickness`. Set the project default text size to 31.5 mil.
* Estimate width at 0.64–0.75 mm per character for 0.8 mm text and ≈ 0.9 mm per character for 1.0 mm text, to keep text inside boxes.
* **Rotated symbols:** KiCad stores field angles relative to the symbol, so a symbol at 90/270 needs field angle 90 for horizontal text, and its `justify` is mirrored (left ↔ right, differently for 90 and 270). Never trust the numbers: render and look.
* Text never touches a wire, pin, symbol, other text or box border.

### 7.3 Topology
* Signal flows left → right.
* **Two-rail ladder hugging the IC:** top rail `YT`, return `YB = YT + 20.32`, vertical parts centred between them. Caps at **8.89 mm pitch** with vertical text. Series parts (L, fuse, bead) sit **in** the rail.
* **IC decoupling:** every supply-pin cap is wired to **its own pin**. The pin stub goes up/out, then across to the cap top, with GND under the cap. For a row of adjacent supply pins, make a staircase: the outer pin gets the lowest rail, and each further pin steps higher and further out. Never use a separate cap ladder joined only by labels.
* **Power symbols upright:** supply arrows on top of the decoupling wire, grounds pointing down. Pins on one rail share one symbol. Value text horizontal, beside the symbol. After rotating a symbol, reset its field angles (KiCad stores them relative to the symbol).
* Rail-end order: last cap → power symbol → test point.
* On any output to a connector: series/filter parts inside, **ESD/TVS last before the port**.
* Reuse existing junctions. Prefer fewer, longer straight wires.

### 7.4 Field offsets (from the symbol origin, mm)
| Symbol / rotation | Reference | Value | Spec | Angle | Justify |
|---|---|---|---|---|---|
| Capacitor vertical (rot 0) | (+3.175, +1.27) | (+4.445, +1.27) | (+5.715, +1.27) | 90 | left |
| Resistor vertical (rot 0) | (+3.175, +3.81) | (+4.445, +3.81) | (+5.715, +3.81) | 90 | left |
| Resistor / L / fuse / bead horizontal (rot 90/270) | (0, −4.445) | (0, −3.175) | (0, −1.905) | 90 | center |
| Capacitor horizontal (rot 90) | (0, −6.35) | (0, −5.08) | (0, −3.81) | 90 | center |
| TVS vertical (rot 90), text right | (+3.175, +3.81) | (+4.445, +3.81) | (+5.715, +3.81) | 0 | left |
| Diode vertical (rot 270), text left | (−3.175, +1.27) | (−4.445, +1.27) | (−5.715, +1.27) | 0 | right |
| Op-amp unit | (0, −8.89) | (0, −7.62) | (0, −6.35) | 0 | center |
| Test point up (rot 0) | (+1.905, −4.445) | (+1.905, −3.175) | (+1.905, −1.905) | 0 | left |
| Test point down (rot 180) | (+1.905, +2.54) | (+1.905, +3.81) | (+1.905, +5.08) | 0 | right (mirrored by KiCad) |
| IC / module | three lines 1.27 apart above the body | | | 0 | center/left |

Always render and confirm (§12.3).

### 7.5 Boxes, titles, notes
* Each functional block sits in a dashed rectangle: `(stroke (width 0.254) (type dash) (color 0 0 132 1))`, no fill, edges on the grid, 1.27 mm between adjacent boxes.
* Box title at `(x0 + 1.27, y0 + 1.27)`: 1.0 mm **bold**, colour `0 0 132 1`, justify left top. Content `NAME - key parts (key spec)`, shorter than the box.
* **Reviewer notes, not essays.** Long notes are a headache for the reviewer. Each block gets **1-4 short lines** with only what a reviewer must know at that part: *why this value / part*, *the limit you must not exceed*, *what FW or PCB must do*. Put the note **beside the parts it explains** (not at the far end of the box). The calculations behind it (§7.6) go into `DESIGN_NOTES.md`; never delete them, archive them there.
* Box size follows the content: after shortening notes, shrink boxes so no box is half empty.
* Hot parts get a `Graphic:SYM_Hot_Small` symbol with a dissipation note beside it: `P = I²R` for passives. For ICs: Pd at the worst corners, `TJ = Tamb + Pd × RθJA`, the Pd limit for TJ = 125 °C, and the shutdown point.

### 7.6 What the design record must contain (as applicable) - full detail in `DESIGN_NOTES.md`, the key number on the sheet
* Datasheet reference-design tags mapped to the refs.
* Currents and margins (nominal, worst case, rating margin).
* Filters: f0, Q, attenuation at the switching frequency, calc vs budget.
* Ripple, and where to measure it (the TP ref).
* Regulators/references: accuracy, tempco, noise, dropout, PSRR, Pd and ΔT.
* Stability limits (Cin/Cout, capacitive load).
* Owner decisions and warnings in plain words.
* Layout hints that matter electrically (cap distance, Kelvin routing, thermal vias, which chip a series resistor sits next to).
* Numbers come only from opened datasheets (`DS p.x`), from values on the sheet, or from your own calculation marked `calc`. Unknowns are marked `est.` with the assumption.

---

## 8. Electrical review checklist (schematic engineer)

Run it on every sheet you finish and on every project you review. Each finding gets evidence and options.

**Power**
* Input protection: fuse rating and **I²t vs hot-plug inrush** (`I²t ≈ V²C / 2R`); slow-blow where there's bulk capacitance. TVS clamp below every downstream absolute maximum. Reverse polarity.
* Regulators: dropout headroom at minimum input, Pd and TJ, Cin/Cout stability range, enable/soft-start, **sequencing** (e.g. analog before digital, reference before the ADC supply), power-good.
* Decoupling per datasheet on every supply pin, bulk at each rail entry, ferrite beads only on supplies (bead + cap resonance vs the switching frequency).
* **Power budget per rail:** load, limit, % used.

**Analog**
* Common-mode and output swing ranges against the supply. Amplifier stability with the real load (capacitive load, isolation resistors, snubber options as DNP).
* Reference loading and accuracy chain. ADC input range, RC anti-alias / kickback filter, Kelvin connections for shunts.
* Offset, gain and drift budget, and what firmware calibrates.

**MCU (do every time, pin by pin)**
* Export the MCU pin → net map from the netlist and check **every alternate function against the datasheet AF table** (SPI/UART/I2C/ADC pins, RTS/DE, timer channels for PWM).
* **Pin tolerance:** for every pin, the supply of the chip that drives it vs the pin type (FT 5 V tolerant vs TTa/TC 3.3 V only). Check the MCU side of every isolator and level shifter.
* Supply rules from the datasheet (e.g. VDDA before / ≥ VDD, VREF ≤ VDDA) with real tolerances; decoupling per pin; VBAT; boot pin; reset RC; crystal load (`CL = C/2 + Cstray`).
* Pins that wake up with a special function (JTAG pull-ups, backup-domain pins with 3 mA sink limits): fine as GPIO, but note it for firmware.
* **Bootloader pins** (ST AN2606 etc.) vs the peripherals actually wired there: if they collide, the debug UART is not a flashing port, so say "program via SWD only".
* Write a short **firmware rules** list in the report (open-drain pins, JTAG release, register settings the hardware depends on).

**Digital**
* Logic levels across every interface (VIH/VIL), level shifting.
* Pull-ups/downs: one per net section, none duplicated. Series 47 Ω next to the **driving** chip.
* Unused pins defined. Boot/reset pins. Debug access.
* **Fail-safe states:** what every output and actuator does when the MCU is in reset, unpowered, or the cable is unplugged.

**Isolation and safety**
* Domains never merged; isolation rating vs requirement.
* Creepage/clearance noted for the layout. For stacked/series cards compute the worst case (N × max cell voltage, and the fault case at the TVS clamp) and compare the connector gap with IPC-2221B (e.g. external uncoated: 0.6 mm for 51-100 V). On a 1.0 mm-pitch card edge one empty finger row ≈ 1.3 mm copper gap.
* Y-caps across a barrier only if EMC needs them (often DNP).

**Thermal**
* Pd for every hot part at the worst corner. SOA for linear stages; if it's exceeded, rate by an envelope plus a firmware trip and copper/vias.

**Protection and I/O**
* ESD/TVS at every connector (last before the port), connector current per pin, and series stacking/ground paths.

**Testability and bring-up**
* Test points per §5.5. A probe ground near every measurement. Current-measurement points.

**Manufacturability and cost**
* Basic vs Extended parts, THT count, stock, footprint/package match, polarity marks, and DNP documented.

---

## 9. Verification checklist (all must pass before installing a schematic change)

1. **Connectivity unchanged:** export the netlist before and after, then `python tools/schematic/netcmp.py before.net after.net`. It must print `connectivity identical: True`. The only allowed differences are ones the owner asked for, plus net renames from local → global conversion.
2. **ERC:** `kicad-cli sch erc --format json -o erc.json <root>.kicad_sch` (or `-o erc.rpt` + `ercsum.py`). 0 errors apart from the documented exceptions in `PROJECT.md`. The total never increases.
3. **Rendered and inspected** (§12.3): the whole page plus every block zoomed in. No overlaps, every field present, notes inside boxes.
4. **Part data:** 9 fields in order, Datasheet = `https://jlcpcb.com/partdetail/<LCSC>` (compare the full string, including `https://`), LCSC verified live this session. Check all sheets with a script, not by eye.
5. **Fonts:** fields 0.8 mm, notes / titles 1.0 mm (count with a script).
6. **Docs refreshed:** `datasheets/README.md` regenerated from the schematics (`tools/schematic/ds_index.py`), `PROJECT.md` decisions log updated, ERC report (keep the text format `ercsum.py` reads) and PDF regenerated.
7. **Owner edits preserved** (§4.2).
8. KiCad still closed and the target files unchanged since your copy. Then install.

Pitfalls seen in practice: a region-based delete also removes a neighbour's power symbol that sits on the boundary (check the netlist diff for lost nodes, then delete by reference); a "fix" that moves an overlap somewhere else (render again after every move).

---

## 10. PCB layout workflow and checks (layout engineer)

### 10.1 Before layout
* Schematic finished, ERC clean, owner OK. In KiCad: *Update PCB from Schematic (F8)*. Ask the owner to do this, or do it only with their go-ahead.
* **Fab constraints first:**
  * get the fab house's current capabilities (min track/space, via drill/annular ring, copper weight, board thickness, solder-mask web, edge clearance);
  * use the BoardRepo fab-limit check if available;
  * set *Board Setup → Design Rules / Net Classes / Stackup* to match.
* Net classes: power (width from current: use an IPC-2152 calculator and state the assumptions), high-voltage/isolation (clearance), Kelvin/sense, differential pairs (impedance from the stackup), default.
* Board outline, mounting holes, connector positions and keep-outs come from the owner's mechanical data. Card-edge parts (PCIe-style fingers) need chamfer and edge-plating rules, and no copper pours near the fingers.

### 10.2 Placement order
1. Connectors and fixed mechanical parts.
2. Isolation barriers (keep a clear slot or gap, and respect the creepage note).
3. Power stage: input protection → filter → converter, in a straight path with tight hot loops.
4. Regulators and references next to their loads.
5. Precision analog: shunt + sense amp + ADC grouped, away from switching nodes.
6. MCU: decoupling caps < 2 mm from their pins, crystal right next to its pins with a guard ring, no traces under it.
7. Test points reachable from the top; hooks need finger room.

### 10.3 Routing rules
* Continuous ground plane under the signals. Split planes only along isolation boundaries.
* Decoupling: via straight to the plane, cap between the pin and the via.
* **Kelvin** sense traces from the shunt pads, routed as a pair.
* Thermal pads: via array + copper area per the datasheet (the thermal note on the schematic gives the required Pd).
* High-current paths are wide and short, and use several vias in parallel.
* Switching nodes are small.
* Series resistors sit next to the driving chip.

### 10.4 Checks
* `kicad-cli pcb drc --format json --severity-all --schematic-parity --refill-zones -o drc.json <board>.kicad_pcb`. There must be 0 errors and no parity differences; every warning is either justified in `PROJECT.md` or fixed.
* Render: `kicad-cli pcb render` (3D PNG) for a visual check of placement and silkscreen; `kicad-cli pcb export svg` per layer for copper review.
* Silkscreen: refs readable, not on pads; polarity/pin-1 marks; board name/rev/date.
* Courtyard overlaps, 3D model collisions (STEP export), assembly side, fiducials if the assembler needs them.
* Electrical recheck of the copper: isolation distances measured, thermal-via count, shunt Kelvin, decoupling distances.

### 10.5 Fab and assembly outputs (only when the owner asks)
* `kicad-cli pcb export gerbers`, `pcb export drill`, `pcb export pos` (CPL) and `sch export bom` into `production/`. Regenerate; never hand-edit.
* JLC BOM columns: Comment, Designator, Footprint, LCSC. CPL: Designator, Mid X, Mid Y, Layer, Rotation. Check rotations against the JLC preview, and list THT/Extended parts for the owner.
* Nothing is uploaded or ordered by the agent.

---

## 11. Reporting to the owner (after each unit of work)

Short and plain:
1. What was done.
2. Evidence: connectivity identical, ERC/DRC counts, images checked.
3. Problems found, with **questions** and your recommendation.
4. What the owner must do in KiCad (F8, exclude a known ERC item, close KiCad).
5. Backup location.
6. Ask before moving on.
7. When the owner asks to *see* changes ("visually?"), give before/after renders (a shared page with image pairs works well), not just text.
8. When the owner hands you a decision ("act as the reviewer and decide"), decide, but list what you changed and why so they can overrule it.

---

## 12. Tools (`tools/`)

Run Python with the script's folder on the path (`tools/schematic/` scripts import `kisexp.py` and `pins.py` from the same folder; for `examples/`, add `tools/schematic` to `PYTHONPATH`).

| File | Purpose |
|---|---|
| `check_env.py` | Pre-flight: Python, kicad-cli, packages, browser, git, KiCad running, lock files, lib tables. |
| `schematic/kisexp.py` | Lossless KiCad s-expression parser/writer (`parse`, `dump`, `find`, `one`, `walk`, `uid`, `num`, `Q`). |
| `schematic/pins.py` | Absolute pin-tip positions of placed symbols (`lib_pins`, `inst_pins`). KiCad rotates CCW on screen: `sn = −round(sin)`. |
| `schematic/semdiff.py` | Semantic diff of two versions of a sheet (symbols, fields, texts, wires, boxes): detects owner edits. |
| `schematic/netcmp.py` | Connectivity compare of two netlists, ignoring names. Exit 0 = identical. |
| `schematic/ercsum.py` | Per-sheet ERC summary of a text report. |
| `schematic/render.py` | Crop of a kicad-cli SVG → PNG via headless Edge/Chrome: `render.py in.svg out.png x0 y0 x1 y1 [px_per_mm]`. |
| `schematic/ds_index.py` | Regenerates the refs / value / MPN columns of `datasheets/README.md` from the schematics, drops rows for parts no longer used, adds rows for new LCSC numbers: `ds_index.py <project_dir>`. |
| `schematic/examples/*.py` | Real scripts from a finished project (layouts, decoupling staircase, page tidy, A4→A3, symbol builders, footprint fixes). They are templates: copy and adapt, never run them on another project. |

### 12.1 kicad-cli
```bash
K=<path to kicad-cli>        # see check_env.py
"$K" sch export netlist --format kicadsexpr -o out.net <root>.kicad_sch
"$K" sch erc --format json -o erc.json <root>.kicad_sch
"$K" sch export svg -o svgdir <root>.kicad_sch        # one SVG per sheet
"$K" sch export pdf -o out.pdf <root>.kicad_sch
"$K" sch export bom -o bom.csv <root>.kicad_sch
"$K" pcb drc --format json --severity-all --schematic-parity -o drc.json <board>.kicad_pcb
"$K" pcb render -o top.png <board>.kicad_pcb
"$K" pcb export gerbers|drill|pos|step|svg ...
```
Always run sch commands on the **root** schematic, so hierarchy and global nets resolve.

### 12.2 Pin math
A library pin at `(px, py)` on a symbol at `(X, Y)` with rotation `r` lands at `(X, Y) + R(r)·(px, −py)`, with `R(0)=[[1,0],[0,1]]`, `R(90)=[[0,1],[−1,0]]`, `R(180)=[[−1,0],[0,−1]]`, `R(270)=[[0,−1],[1,0]]`. Read pins from the sheet's own `lib_symbols` copy. Mirrored symbols aren't handled by `pins.py`; check them with a netlist.

### 12.3 Visual check
```bash
"$K" sch export svg -o svg <root>.kicad_sch
python tools/schematic/render.py "svg/<root>-<Sheet Name>.svg" full.png 0 0 420 297 5   # whole A3 page
python tools/schematic/render.py "svg/<root>-<Sheet Name>.svg" zoom.png x0 y0 x1 y1 12  # each block
```
Look at **every** block zoomed in at ≥ 9–12 px/mm before calling a layout clean.

---

## 13. Project folder hygiene

* **Keep:**
  * the KiCad project files (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `.kicad_prl`);
  * the project libraries (`.kicad_sym`, `.pretty/`, `.3dshapes/`);
  * **`sym-lib-table` and `fp-lib-table`** (without them KiCad can't find the project libraries);
  * `instruction.md`, `PROJECT.md`, `DESIGN_NOTES.md`, `tools/`;
  * `datasheets/`: every purchased part's datasheet plus `README.md` index. When you add or change a part, add its datasheet and an index row in the same step. Source: the PDF linked from the LCSC product page (`datasheet.lcsc.com/datasheet/pdf/<hash>.pdf?productCode=<Cxxxx>`), else the JLC part page or the manufacturer. Check that the file names the MPN or its series.
* **Don't keep:**
  * scratch work and backups (put them outside the project);
  * `*-backups/` zips;
  * `.history/` (KiCad local history);
  * `*.bak`, `*.lck`, `fp-info-cache`;
  * stale `production/` outputs.
* `.gitignore` for a KiCad repo:
  ```
  *-backups/
  .history/
  *.lck
  ~*.lck
  *.bak
  fp-info-cache
  *.kicad_prl
  desktop.ini
  __pycache__/
  ```
* Never delete or move project content without the owner's OK; list what you'd remove and why first.

---

## 14. Never do these

* Edit while KiCad is open; "edit anyway".
* Change values, MPNs, topology, nets or DNP status without the owner's yes.
* Merge domains / grounds that `PROJECT.md` keeps separate.
* Invent a part number, datasheet value or page number; use an old BOM as a source of truth.
* Add PWR_FLAGs that create `pin_to_pin`; make custom power-symbol pins passive.
* Put no-connect flags on NC/DNC-type pins; put a GND symbol under every cap in a ladder; put the power symbol after the test point.
* Leave text at a size other than the house size, or overlapping anything.
* Fill the sheets with long calculation notes (they belong in `DESIGN_NOTES.md`).
* Put signals on special-function connector pins (PCIe PRSNT / PERST / WAKE), or leave purchased hooks `in_bom no`.
* Edit a stock library symbol in place.
* Delete owner notes or "unused-looking" parts without asking.
* Commit, push, publish, upload or order anything unless asked.
* Claim "done" without the §9 / §10.4 evidence.
