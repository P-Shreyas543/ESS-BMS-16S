# PLAN.md — hand-off for the next agent (state 2026-11-25)

Read this first, then `PROJECT.md` §5 (decisions log), `AGENT_TASKS.md` (last updates), `instruction.md` (house rules), `docs/SCHEMATIC_V1.md`.
Scratch work lives in `%TEMP%\bms_work\p4\` (not in git). Never write personal paths, user names or agent attribution into committed files.

---

## 1. Where things stand

| Item | State |
|---|---|
| Schematic v1 (both boards, 779 parts) | committed `0f11683` |
| Schematic v1.1 (LM5146-Q1 sync buck + SN6505B isolated 5 V) | committed `ca3a7a3` (on `origin/main`, local branch `public`) |
| **Schematic v1.2 (hybrid)** | **installed in the working tree, verified, NOT committed yet** |
| Block diagram (web page) | published as a private Claude artifact; content summarised in §4 below |
| Research for the owner's Word document | 3 agents were running; results may not have been saved — see §5 |
| Word document (.docx) | **not started** |
| PCB layout (P6) | not started; old `.kicad_pcb` is untouched and obsolete |

**v1.2 = owner decision 2026-11-25** (`PROJECT.md` §5 row "v1.2"): +5V trunk back to the **LM5013 non-sync buck, commercial LM5013DDAR (C5383001)** with the v1.0 power-latch values; keep the v1.1 isolated supply (TPS22918 → **SN6505B-Q1 C1849490** → T101 LT31-113 1:1.3 → 2 × MBR0520L → TLV76750). Reason: an independent v1-vs-v1.1 comparison (Antigravity) found LM5013-Q1 stock 213 pcs, LM5146 option +$5.6/board, +17 parts, ≈ +3 mA standby and a complex latch. Fixed in v1.2: transformer barrier keep-out zone (F-06), stale "10 ms" wake-pulse text (F-09; real requirement now: AFE_ALERT latched in firmware or low ≥ 2 ms). New bring-up gate B12: EMC pre-scan of the LM5013 buck.

**v1.2 verification (done 2026-11-25, in the repo working tree):** netlist-vs-spec SPEC MATCH on all 10 sheets; B2B J206 = J701 on 30 pins; ERC control 0 errors (2 documented U1002 WP/HOLD pin_to_pin warnings), power 0 / 0. Sheet 01 = 95 refs, A3.

Changed files not yet committed: `01_Power_Supply.kicad_sch`, `footprints.pretty/Transformer_WE-PPTI_760390014.kicad_mod`, `PROJECT.md`, `AGENT_TASKS.md`, this `PLAN.md`.

---

## 2. Tools and how to verify (Windows, KiCad 10)

* kicad-cli: `%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe`. KiCad must be closed while files are edited (`python tools/check_env.py .`).
* Frozen pin-level specs (source of truth for every sheet): `%TEMP%\bms_work\p4\spec_frozen\G1..G4\sheetNN.parts.csv / .nets.csv / .md`. Snapshots: `spec_v1`, `spec_v10`, `spec_v11`.
* Checker: `python %TEMP%\bms_work\p4\infra\speccheck.py <root.kicad_sch> sheetNN.parts.csv sheetNN.nets.csv` → must print `SPEC MATCH: True`. Roots: `Automotive_ESS_BMS.kicad_sch` (sheets 01 02 03 05 06 08 09 10), `power_board/power_board.kicad_sch` (04 07).
* B2B: `python %TEMP%\bms_work\p4\infra\b2bcheck.py <control root> <power root>` → `B2B MATCH: True`.
* ERC: `kicad-cli sch erc --severity-all -o erc.rpt <root>`; summary `python tools/schematic/ercsum.py erc.rpt`.
* Whole-design merge + all checks: `%TEMP%\bms_work\p4\integ\merge.sh` (copies built sheets into `integ\proj`, runs everything). Builder library and per-sheet build scripts: `%TEMP%\bms_work\p4\infra\README.md`, `%TEMP%\bms_work\p4\build\<sheet>\build_sheetNN.py`.
* Any schematic change follows: edit spec → independent review → rebuild with the sheet's script → SPEC MATCH + ERC + render check → install → docs → commit.

## 3. Commit rules (owner's standing instruction)

Commit and push **as the owner only** (git identity already configured), **no Co-Authored-By / agent attribution** in commits or PRs. Before each commit: privacy scan of staged files (no personal paths, user names, e-mail, datasheet PDFs, vendor 3D models). Commit from PowerShell with `git commit -F <msgfile>`, then `git push origin public:main`. Never push branches `main` or `rework-2026-11` from local.

---

## 4. Next tasks, in order

### Task A — finish v1.2 docs and commit
1. `docs/SCHEMATIC_V1.md`: add "§10 Revision v1.2 (2026-11-25)" (what/why above, verification line, B12 gate, wake-pulse rule ≥ 2 ms or latched; mark the v1.1 buck section superseded but keep it for history). Update sheet table (sheet 01: A3, 95 refs), bring-up gates, firmware rules, open decisions.
2. `docs/design/sheet01_power_supply.md`: regenerate from `spec_frozen\G1\sheet01.md` (public-clean: no scratch paths, no tool chatter).
3. `docs/design/sheet06_communications.md`: U106 is SN6505B-Q1.
4. `docs/ARCHITECTURE.md` §4 power tree / budget / sleep, parts list: LM5013DDAR + SN6505B-Q1; add a dated v1.2 line in the update note.
5. `docs/bom/bom_schematic_v1.csv` regenerate from all `spec_frozen` parts.csv; update counts in `docs/BOM_v1.md`.
6. Regenerate `docs/schematic/control_board_v1.pdf`, `power_board_v1.pdf` (`kicad-cli sch export pdf`).
7. `docs/reviews/`: add `v1_vs_v11_comparison.md` = the Antigravity comparison (owner pasted it) + verification table: F-06 confirmed and fixed; F-09 confirmed and fixed; LM5013-Q1 213 pcs / LM5013DDAR 6 940 pcs $0.98 / SN6505B-Q1 C1849490 3 000 pcs $0.995 / LM5146-Q1 8 853 pcs $6.61 (all live 2026-11-25); CISPR 25 LW-band point is valid for automotive, but stationary-ESS conducted limits (CISPR 11/32, IEC 61000-6-x) start at 150 kHz, so moving to 400 kHz does not escape them.
8. README status → v1.2. Privacy scan, commit ("schematic: v1.2 hybrid power tree …"), push.

### Task B — block diagram for the repo
Make `docs/block_diagram.svg` (draw.io or hand SVG; readable in GitHub light and dark) and link it from README and SCHEMATIC_V1.md. Content (mark each block: **in v1.2** / **to add** / **owner decision**):
* **Power path:** Battery+ M6 lug → CHG bank 8 × IPT015N10N5 → FET_MID → DSG bank 8 × IPT015N10N5 → Pack+. Battery− lug → 2 × 0.2 mΩ shunt (100 µΩ) → Pack−. Pre-discharge P-FET Q723 + 50 Ω/100 W (PDSG), pre-charge P-FET Q724 + 100 Ω/50 W (PCHG), sources on FET_MID.
* **Power board (sheets 04, 07):** FET banks + gate networks + PNP turn-off; hardware kill (74LVC1G11 AND: AFE faults, OC latch, FET_EN, MCU reset); OC latch (INA240 → TLV1702 window +599/−305 A → AUP1G74, TLV803 POR); clamps (TVS both sides, snubbers, reverse clamp); F701 supply-tap fuse; NTC_FET, NTC_SHUNT; heater switch Q726 + F702 5 A (**decision: 3.5 A limit**); J701.
* **B2B J206 ↔ J701** 2 × 15: HV group pins 1-8, gap 9-10, Kelvin, analog, logic, rails.
* **Control board:** power latch & wake (button, AFE ALERT, AUX, PWR_HOLD); +5V LM5013DDAR; +3V3 / +3V3_A TPS7B82; +3V3_ESP TLV62569; +12V LM5163 (switched); +5V_ISO SN6505B-Q1 chain (2.5 kV); AFE BQ76952 (16 cells, external NPN balancing, 4 NTC, CC); **AFE link I2C+CRC (decision: SPI?)**; MCU STM32G473 + TPS3828 watchdog + RTC; FRAM + 8 MB flash + NTC mux; 2 × isolated CAN, 2 × isolated RS-485, 4 × RJ45; isolated USB-C service; ESP32-C3; 2 × TCA9539 (SOC LEDs, RUN/ALM, address DIP, wake button); dry contacts + DI; 2 × EXT_OUT + PWM fan; active-balancer header; buzzer (**DNP, decision**); **to add:** OLED front panel via J801, deep-UV shutdown policy, AFE pin audit, possibly isolated display I2C, possibly CAN/RS-485 wake receiver.
* **Must-have list** (all ✓ except): deep-UV behaviour (to add), local display (to add), heater (decision).

### Task C — research: DONE 2026-11-25 (do not redo)
Finished reports — use them for Task D and copy their content, public-clean, into `docs/research/06_afe_pins_spi.md`, `07_power_states.md`, `08_front_panel.md`:
* `%TEMP%\bms_work\p4\research_v12\afe\REPORT.md` — all 48 AFE pins used as intended; keep I2C + CRC (SPI would cost 2 AFE NTC inputs and 4 MCU pins, no speed gain).
* `%TEMP%\bms_work\p4\research_v12\power_states\REPORT.md` — state machine; SLEEP with FETs on ≈ 7 mA (NOT 65-75 µA; that figure is STORAGE ≈ 40 µA, FETs off); gaps G1-G10 (G1 charger-wake config and G2 AFE host-watchdog are firmware/config blockers); pre-charge-path idea rejected with numbers.
* `%TEMP%\bms_work\p4\research_v12\front_panel\REPORT.md` — 1.3" SH1106 OLED C7465997 (+80 °C deviation, 70 °C blanking), non-isolated + TCA4307 buffer, CLIK-Mate 10-pin J801, full sheet 08 change list.

Original research briefs, for reference:
1. **AFE pin audit + I2C vs SPI:** table of all 48 BQ76952 pins (function, our net, MCU / B2B / NTC, matches datasheet intent?, page). SPI: which pins become SCLK/MOSI/MISO/CS, what they lose (HDQ, CFETOFF thermistor inputs → move to the MCU mux), how SPI mode is selected (TRM SLUUBY2), CRC, free STM32G473 SPI pins (SPI1 is used by FRAM/flash), exact change list for sheets 02/03/10, recommendation.
2. **Power states / sleep / deep-UV:** state machine RUN → SLEEP (FETs on, AFE SLEEP, MCU STOP) → STORAGE (FETs off after long inactivity) → DEEP-UV SHUTDOWN (AFE SHUTDOWN, µA) + FAULT + turn-on with pre-discharge. Entry/exit thresholds, current budget per state (cite AFE/MCU/regulator data), wake paths (charger via LD/PACK, button, ALERT, CAN/RS-485 activity — check whether a low-power wake receiver is needed), drain per month for 100/280 Ah, inverter standby is the dominant drain (≈ 0.4 A at 20 W ≈ 290 Ah/month).
   **Owner's idea "run the idle load through the pre-charge path to save battery" — answer: no.** Saves only ≈ 10-20 µA of gate drive; a 20 W inverter idle (0.4 A) drops ≈ 20 V and dissipates ≈ 8 W in the 50 Ω pulse resistor; load steps collapse the DC link and the main FETs then close with inrush. Keep pre-discharge as a turn-on sequence only; save battery with AFE SLEEP (FETs on) and a STORAGE mode (FETs off after long inactivity, wake by button / charger / comms).
3. **Front panel:** OLED options (SSD1306/SH1106/SSD1309 0.96-1.54", memory/segment LCD alternatives) vs −40 °C rating and 85 °C lifetime; live-verified LCSC parts; connector (PicoBlade or locking −40 °C), pinout (+3V3, GND, SCL, SDA, wake button tied to WAKE_BTN_RAW, LEDs, INT); I2C cable length (P82B96 / PCA9615 if long); isolation: needed for ESD / ground loops (not shock, pack ≤ 60 V) when the panel is on a long cable or a metal door — ISO1540-class + isolated 3.3 V; otherwise ESD + series R + PTC. Change list for sheet 08.

### Task D — owner Word document `docs/BMS_design_review_v1.2.docx`
Sections: 1 Block diagram (Task B) · 2 Must-have functions and status · 3 Power path incl. main and pre-charge FETs (answers "did we miss pre-charge / main FETs?" — no, sheet 07) · 4 Power states, sleep, storage, deep-UV (Task C2, with a state diagram) and the pre-charge-path idea verdict · 5 AFE pin audit and I2C vs SPI (C1) · 6 Front panel, OLED, wake switch, isolated I2C (C3) · 7 Revision history v1 → v1.1 → v1.2 with the Antigravity comparison and its verification · 8 Open owner decisions with recommendation:
  * P5-01 charge-side temperature faults kill both banks + heater (R759 0 Ω fitted) vs charge-only (remove R759, fit R760) — recommend charge-only after firmware review;
  * heater limited to 3.5 A by F702 5 A (451 series breaks 10 kA @ 75 V DC only up to 5 A);
  * buzzer fit / DNP; supercap for RTC in ship mode; B− cable ≤ 0.1 mΩ (cell-1 reading); stock reservations (J201 cell connector, R_PRE / R_PCHG, LT31-113 + its −40 °C qualification);
  * AFE link I2C vs SPI; OLED panel + isolation; deep-UV cutoff and wake; CAN/RS-485 wake;
  * 100 V FET margin → D-04 short-circuit bench test; TLV1702 output-low at 3.3 V bench check.
  · 9 Bring-up gates and firmware rules (from SCHEMATIC_V1.md). Use python-docx or docx-js; keep it free of personal paths.

### Task E — after the owner answers the decisions
Apply chosen changes through the spec → review → build → verify pipeline (§2), then start **P6 PCB layout** (two boards: power ≈150 × 100 mm 4 L 2 oz on Al plate; control 160 × 100 mm 4 L; stack via J206/J701, 11 mm; 6.5 mm creepage across isolation barriers; T101 keep-out; Kelvin shunt routing; FET-bank thermal and current copper; slot under isolators).
