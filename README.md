# ESS-BMS-16S — Open 16S LFP Battery Management System for Energy Storage

A compact, open-hardware battery management system for 16S LFP (51.2 V) energy-storage packs — home storage, server-rack batteries, telecom backup — designed in KiCad 10 for JLCPCB fabrication and assembly.

The goal is a BMS that matches the features of the widely used Chinese ESS boards (Daly, JBD, JK, Seplos, PACE) and goes beyond them where they are weak: protection that does not depend on firmware, measured switch and pre-charge health, deeper diagnostics, and open, documented protocols.

> **Status (2026-11-25): schematic v1.2 done — PCB layout next. Not built, not tested, not production ready.**
> v1.2 installs a hybrid control-board power tree: restores the v1.0 `+5V` LM5013 non-synchronous buck with the commercial `LM5013DDAR` and v1.0 power latch, and keeps the v1.1 transformer-isolated (2.5 kVAC) `+5V_ISO` chain with the AEC-Q100 `SN6505B-Q1` ([what changed](docs/SCHEMATIC_V1.md#10-revision-v12-2026-11-25)).
> The schematic is complete for both boards of the stack (control board + power board), verified against its pin-level spec and independently reviewed: [`docs/SCHEMATIC_V1.md`](docs/SCHEMATIC_V1.md), PDFs [control board](docs/schematic/control_board_v1.pdf) / [power board](docs/schematic/power_board_v1.pdf). Do not order boards from this repository yet: several bring-up gates (including an LM5013 EMC pre-scan) and owner decisions are open. See [Project status](#project-status).

---

## Target specification (v1)

| Item | Target |
|---|---|
| Cells | 16S LFP, 40.0–58.4 V pack |
| Current | 200 A continuous, on-board back-to-back high-side N-MOSFET switch |
| Current sense | on-board 100 µΩ shunt, BQ76952 coulomb counter + independent fast trip |
| Cell monitor | TI BQ76952 (16 cells, hardware protections, high-side FET drivers, pre-charge) |
| Balancing | external passive ~105 mA per cell + header for an optional 1–2 A active balancer, charge-based balancing firmware |
| Temperature | pack NTCs + FET-bank and shunt sensors |
| MCU | STM32G473RCT6 (3× FDCAN, 256 KB flash) |
| Communications | 2× isolated CAN, 2× isolated RS-485 (inverter + parallel-pack link, RJ45 ×4), ESP32-C3 Bluetooth / Wi-Fi |
| Safety | MCU-independent hardware gate-kill (AFE faults + latched over-current), dual watchdog, switch / pre-charge fault checks |
| Other | sleep / ship mode with wake button, SOC LEDs, 2 dry contacts, heater output, RTC-stamped fault log (FRAM + flash), field firmware update |

The numbers above are design targets; the verified values are kept in [`PROJECT.md`](PROJECT.md) and the architecture documents as they are confirmed.

## How it compares

A feature benchmark of current Daly, JBD, JK, Seplos, PACE and ANT products is in [`docs/research/02_competitors.md`](docs/research/02_competitors.md). In short: every serious product has sleep mode, an app, parallel packs, dry contacts and inverter protocols — this design adds those, plus features none of them documents (independent hardware trip, switch health checks, busbar / cell resistance diagnostics, open protocols, timestamped deep logging).

## Project status

| Step | State |
|---|---|
| Requirements and original runbook | done ([`instructions.md`](instructions.md)) |
| Schematic redraw to house style (6 sheets, connectivity proven unchanged) | done 2026-11-17 |
| Electrical / requirements review | done — findings in [`docs/research/`](docs/research/) and [`AGENT_TASKS.md`](AGENT_TASKS.md) |
| Feature and component research (AFE, competitors, balancing, power path, MCU) | done — [`docs/research/00_SUMMARY.md`](docs/research/00_SUMMARY.md) |
| Architecture v1 (power tree, power stage, AFE, MCU pin map, sheet plan) | done — [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (updated for schematic v1) |
| Part selection with live LCSC verification | done — [`docs/BOM_v1.md`](docs/BOM_v1.md) |
| Schematic v1 / v1.2: two KiCad projects, 10 sheets, 784 references (v1.2); pin-level spec → independent review → scripted drawing → netlist-vs-spec match on all 10 sheets, ERC 0 errors on both boards → final independent review (0 blockers) + v1-vs-v1.1 comparison | v1 done 2026-11-24, v1.1 2026-11-25 (`ca3a7a3` fallback), v1.2 hybrid power tree 2026-11-25 — [`docs/SCHEMATIC_V1.md`](docs/SCHEMATIC_V1.md), [design notes](docs/design/), [reviews](docs/reviews/), [BOM CSV](docs/bom/bom_schematic_v1.csv) |
| PCB layout, DRC, fabrication outputs | **next** |
| Bring-up and bench tests (incl. the short-circuit test) | planned |

## Repository layout

| Path | Content |
|---|---|
| `Automotive_ESS_BMS.kicad_pro` / `.kicad_sch` | control-board KiCad project and root schematic (with block diagram) |
| `01_*`, `02_*`, `03_*`, `05_*`, `06_*`, `08_*`, `09_*`, `10_*.kicad_sch` | control-board sheets: power supply, AFE / cell monitor, MCU, aux outputs, communications, IO / front panel, wireless, memory / sensors |
| `power_board/` | power-board KiCad project: `04_Current_Sensing`, `07_Power_Stage` |
| `docs/SCHEMATIC_V1.md`, `docs/schematic/` | schematic v1 overview (board split, B2B pin map, verification, bring-up gates, firmware rules, open decisions) and PDFs of both boards |
| `docs/design/`, `docs/reviews/` | per-sheet design notes (calculations, decisions, LCSC verification) and the spec / schematic reviews |
| `docs/ARCHITECTURE.md`, `docs/architecture/`, `docs/BOM_v1.md`, `docs/bom/` | system architecture and part selection |
| `symbols/`, `footprints.pretty/`, `3d_models/` | project-local libraries (`${KIPRJMOD}` paths, portable) |
| `PROJECT.md` | project facts, nets, domains, parts and the owner **decisions log** |
| `DESIGN_NOTES.md` | calculations and design reasoning, per sheet |
| `docs/research/` | research reports with datasheet / source citations |
| `docs/plans/` | the original 2026-10 subsystem plans (historical background; the decisions log in `PROJECT.md` wins) |
| `LICENSE`, `tools/LICENSE` | CERN-OHL-S-2.0 (hardware), MIT (tools) |
| `instruction.md` | the engineering playbook this project follows (workflow, style, verification) |
| `instructions.md` | original product requirements |
| `AGENT_TASKS.md` | task queue and verification reports of each work step |
| `tools/` | Python helpers: environment check, lossless KiCad s-expression edit, netlist compare, ERC summary, render |

## Engineering method

Every change follows [`instruction.md`](instruction.md):

* **Connectivity proof:** each redraw is verified with a netlist comparison (`tools/schematic/netcmp.py`) — the net list must be identical unless a change was decided.
* **ERC** on the root sheet after every step, with the result recorded.
* **Visual check** of every sheet and block from rendered images.
* **Part data** verified on the distributor page (LCSC number, MPN, stock) — never from memory.
* **Decisions** recorded with date in `PROJECT.md`; calculations in `DESIGN_NOTES.md` with datasheet page references (`DS p.x`), own calculations (`calc`) and estimates (`est.`) marked.

## Opening the project

1. Install KiCad 10.
2. Open `Automotive_ESS_BMS.kicad_pro`. The project libraries resolve through `${KIPRJMOD}`; no global library setup is needed.
3. Optional: `python tools/check_env.py .` checks the toolchain (KiCad CLI, Python packages, renderer).

## Standards referenced

IPC-2221B (clearance), IPC-7351B (land patterns), IPC-A-610 Class 3, IEC 60664-1, IEC 62619 / UL 1973 (stationary storage), UL 9540A, ISO 26262 principles, AEC-Q100/101/200 where available. Certification is not claimed.

## Third-party material

* **Datasheets and app notes are not included.** They are copyrighted by their manufacturers. The design notes and research reports cite them by document number and page; download them from the manufacturer (TI, ST, Vishay, …) or the LCSC product page.
* **3D models are not included** (vendor licences vary). Footprints reference them under `${KIPRJMOD}/3d_models/`; fetch them from the manufacturer or with `easyeda2kicad` for local use.
* Product and company names (Daly, JBD, JK, Seplos, PACE, ANT, Pylontech, Victron, …) are trademarks of their owners and are used only to identify products in the comparison. Competitor data is taken from public documents and listings, cited in `docs/research/02_competitors.md`; no affiliation or endorsement is implied.

## Disclaimer

This is a **work-in-progress design shared for learning and review, not a certified product.** Lithium battery packs store large amounts of energy; a fault in a BMS can cause fire, explosion, electric shock or injury. Anyone who builds, modifies or uses this design does so at their own risk and is responsible for testing it and for meeting the safety standards that apply where it is used (for example IEC 62619, UL 1973, UL 9540A). The design is provided **"as is", without any warranty**, as stated in section 6 (Disclaimer and Liability) of the CERN-OHL-S-2.0 licence. No certification or compliance is claimed.

## License

* **Hardware** (schematics, PCB, libraries, design documentation): [CERN Open Hardware Licence v2 — Strongly Reciprocal](LICENSE) (`CERN-OHL-S-2.0`). You may use, modify, make and sell it; if you distribute a modified design or products made from it, you must publish your modified source under the same licence.
* **Software tools** in `tools/`: [MIT](tools/LICENSE).

Copyright © 2026 Shreyas P. Source location: this repository.
