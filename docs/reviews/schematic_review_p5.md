# Final schematic review P5 (2026-11-24) — both boards

After both KiCad projects were drawn and had passed the netlist-vs-spec check (SPEC MATCH on all 10 sheets) and ERC, an independent reviewer who had neither designed nor drawn them reviewed the **drawn** schematics. Method: netlists exported with `kicad-cli` from both projects and joined at J206 pin n ↔ J701 pin n by script; every sheet rendered whole and in zoomed crops; items already settled in the spec review ([`spec_review.md`](spec_review.md)) were not re-opened unless the drawing disagreed with their disposition. Nothing was measured.

| Board | BLOCKER | MAJOR | MINOR | NOTE |
|---|---|---|---|---|
| Power (sheets 04, 07 + joint with the control board) | 0 | 2 | 7 | 8 |
| Control (root + sheets 01, 02, 03, 05, 06, 08, 09, 10) | 0 | 0 | 9 | 14 |

**No wiring error was found in either drawing.** On the control board the reviewer's own netlist diff against the frozen spec gave 0 differences (549 components and 393 nets at review time); the ground-domain scan found only the isolated DC-DC and the isolators bridging `GND_PWR` to `GND_ISO` / `GND_USB`. On the power board every pin of the TOLL / TO-263 / TDSON / SOT parts, every diode direction and all 30 B2B pins agree with the datasheets and the pin map. Both MAJOR items are system behaviour that only shows when the two netlists and the AFE configuration are read together.

The fix round of 2026-11-24 was applied to the spec and the drawing, then re-verified: SPEC MATCH on all 10 sheets, B2B match, ERC 0 errors on both boards (control: the 2 documented U1002 WP / HOLD `pin_to_pin` warnings; power: 0 warnings).

---

## Power board

| ID | Sev. | Finding | What was done |
|---|---|---|---|
| P5-01 | **MAJOR** | Every charge-direction AFE fault — including the temperature limits UTC (0 °C) and OTC (45 °C) — asserts DCHG, which kills **both** banks. So there is no discharge below 0 °C or above 45 °C (UTD / OTD are −20 / 60 °C), and the heater, fed from `PACK+`, cannot self-heat the pack. Owner decision D-12 accepted "kill both" for COV / OCC only | **Hardware hook fitted; policy is an owner decision.** R759 0R 0603 (fitted) between `AFE_FLT_CHG_N` and U702 pin 6 (new local net `07_FLT_CHG_K`), R760 10 k (DNP) from `07_FLT_CHG_K` to `+3V3`. On-sheet note: "R759 0R fitted = DCHG kills both banks (D-12, as built); remove 0R + fit R760 10k = charge faults do not kill discharge (owner decision pending)". No new LCSC numbers (C21189, C25804 reused) |
| P5-02 | **MAJOR** | The OC-latch re-arm input (`OC_CLR` → AUP1G74 CLK, positive-edge) was an unfiltered clock line crossing the B2B next to the FET banks, held only by 100 kΩ; one spurious edge re-arms the latch into the fault that tripped it | **Fixed (sheet 04):** R416 → 10 k pull-down on `OC_CLR` (connector side), TP405 stays on `OC_CLR`; new R420 1 k series → new net `04_OC_CLK` → U403 CLK; new C411 100 pF C0G at the pin (1 k + 100 pF ≈ 67 ns/V edge against the 200 ns/V limit). Firmware rule: PD2 idle low, re-arm only after the fault is classified; re-arm glitch check added to the D-04 bench test |
| P5-03 | MINOR | "B2B unplugged → killed + BOTHOFF" is not what the hardware does: without J701 the power board has no `+3V3`, so the kill FETs are not driven and the BQ drivers are disconnected; the banks are held off only by 10 MΩ + zeners (gate decay ≈ 1.0–1.4 s under load, calc) | **Documentation:** ARCH §5.3 fail-safe row corrected; rule "never separate the boards with the output on; standoffs screwed before the lugs are connected". No hardware change proposed. On-sheet note on sheet 07 corrected in v1.1 |
| P5-04 | MINOR | Test access thin for the D-04 transient: no point on `BAT-`, `07_KILL`, `07_OFF_CHG / DSG`; no low-inductance V_DS probe points | **Fixed in part:** THT pads TP713 `07_KILL`, TP714 `07_OFF_CHG`, TP715 `07_OFF_DSG`, TP716 `BAT-` (at the B− lug; sheet 04 deliberately has no second `BAT-` pad). Coaxial V_DS probe sockets not added; bench current via Rogowski coil / coaxial shunt |
| P5-05 | MINOR | Box title "… reverse clamp (DNP)" contradicted the fitted reverse clamp | **Fixed:** title "PACK clamp, snubbers, reverse clamp" |
| P5-06 | MINOR | Safety-island and pack-voltage nodes had auto-names in the netlist, so HV net classes could not address them by name | **Fixed:** visible local label on every `04_*` and `07_*` net |
| P5-07 | MINOR | `OC_TRIP_N` / R756 drawn so the signal seemed to enter the AND gate from the MCU side | **Fixed:** R756 redrawn from `OC_TRIP_N_PB` (gate side, global label) to `OC_TRIP_N` (B2B side), with "B2B side" / "gate side" text |
| P5-08 | MINOR | The ADC kick-back capacitor promised in the R1-15 disposition was missing on the control board | **Fixed (sheet 03):** C318 1 nF C0G from `ISENSE_OUT` to `GND_PWR` at the MCU (series R = R419 100 Ω on the power board) |
| P5-09 | MINOR | ARCHITECTURE.md still described the earlier circuit (RC power-up reset, 470 kΩ DDSG / DCHG pull-downs, BSS123 level shifters, 2 × SMCJ60A PACK clamp) | **Fixed in the documentation pass for schematic v1** ([`../ARCHITECTURE.md`](../ARCHITECTURE.md), dated note at the top) |
| P5-10 | NOTE | Single-tie check: `BAT-` meets `GND_PWR` only at NT401; the deliberate soft path CELL_0 → R274 10 Ω is on the control board | Confirmed, no action |
| P5-11 | NOTE | Shunt Kelvin path and polarity correct; control-board supply current returns through J701 13 / 17 / 30 and NT401, ≈ 0.5 A per mV of ground offset on `ISENSE_OUT` | Bring-up: calibrate the zero with the boards stacked |
| P5-12 | NOTE | Gate-drive trace CHG / DSG / PCHG / PDSG / LD / PACK agrees with the sheet 07 design note | Confirmed |
| P5-13 | NOTE | Heater path correct; heater outside the kill chain by design | Confirmed (supply: see P5-01) |
| P5-14 | NOTE | During a `BAT+` lug transient Q717 E-B injects ≤ ≈ 38 mA for ≈ 20 µs into the CHG pin (calc, est.); no TI figure for injected current | Bring-up: watch `AFE_CHG` in the D-04 test |
| P5-15 | NOTE | DDSG / DCHG must drive from REG1 = 3.3 V (with REG18 the high level is 1.8 V < 2.0 V VIH and the kill stays asserted) | OTP checklist item (0xAA) |
| P5-16 | NOTE | B2B pin n ↔ pin n holds only with J206 on the bottom of the control board facing J701 on top of the power board | Layout gate (with R2-17) |
| P5-17 | NOTE | Showcase polish: ground symbols show no net name; root sheets nearly empty; partly used pages | Root block diagrams added (P5C-07); ground-symbol names left for the next revision |

### Fail-safe table, verdict from the joined netlists

| Condition | Verdict | Trace |
|---|---|---|
| MCU reset / watchdog | **PASS** | `MCU_NRST` (TPS3828, R302 10 k) → J206.22 ↔ J701.22 → R758 → U701 (R750, C719) → `AFE_DFETOFF` low → BOTHOFF; U702 → U703 → `07_KILL` → kill FETs. `FET_EN` Hi-Z → R731 |
| `FET_EN` = 0 | **PASS** | PB6 → pin 21 → U701, same chain |
| `+3V3` lost | **PASS** | U701–U703 unpowered (Ioff), R263 100 k asserts BOTHOFF at the BQ, R749 holds `07_KILL` low, 10 MΩ + zeners hold the gates. Also for J701 pin 28 open alone |
| AFE SHUTDOWN | **PASS** | DDSG / DCHG Hi-Z → R732 / R733 100 k → kill, if `+3V3` is on |
| OC latch tripped | **PASS** (weak point fixed by P5-02) | U403 → `OC_TRIP_N_PB` → U701 direct; MCU reads it behind R756 |
| B2B unplugged | **PARTIAL** (P5-03) | Control side: R263 asserts BOTHOFF, R304 / R305 / R306 define the MCU inputs. Power side: pull-downs present but no `+3V3`, no kill, no BQ driver on the gates; off-state held by 10 MΩ |
| Power-up | **PASS** | U404 TLV803S holds CLR_N low until 200 ms after `+3V3` > 2.93 V → latch tripped; `FET_EN`, `MCU_NRST` low |
| Sense rail off | n/a | No switched sense rail; R415 from `+3V3_A`, so a lost analog rail (or J701.18 open) trips the latch |

Single open B2B contact: pins 21, 22, 23, 24, 27 → power-board pull-down → safe; 25 → R263 → BOTHOFF; 28 → BOTHOFF; 18 → latch trips; 20 → cannot re-arm; 19 / 26 / 14 → read-back only; 13 / 17 / 30 → two grounds remain; 4 or 8 → second DSG contact.

---

## Control board

| ID | Sev. | Finding | What was done |
|---|---|---|---|
| P5C-01 | MINOR | The DNP hardware-alarm LED option sank its LED into `KILL_N`; behind the new 10 k R757 it would corrupt the `KILL_N` read-back | **Fixed:** D809, R829 and their net deleted |
| P5C-02 | MINOR | Ship-mode button wake has little margin in the cold: TS2 must fall below 0.7 V (min) through R276 + a BAV170 junction at ≈ 1 µA (≈ 0.55–0.7 V at −40 °C, est.) | **Fixed (option + gate):** D232 BAT54WS (DNP) across the D225 TS2 leg; bring-up gate "TS2 < 0.6 V with the button pressed at −40 °C, else fit D232" |
| P5C-03 | MINOR | RS-485 DE held low only by the transceiver's internal weak pull-down in reset / ROM / blank MCU | **Fixed:** R634 / R635 10 k to `GND_PWR` on `RS485_INV_DE` / `RS485_LINK_DE` |
| P5C-04 | MINOR | Field input DI_AUX1 had no series impedance in front of its ESD diode | **Fixed:** R838 2.2 k 1206 (C17948, new, live-verified 2026-11-24) between J802 pin 5 and the input node; closed contact reads 0.62 V < VIL 0.99 V (calc) |
| P5C-05 | MINOR | `CHASSIS` had no defined connection to the enclosure (no mounting holes) | **Fixed:** MH601–MH604 M3 plated on `CHASSIS`; note "MH on CHASSIS, standoffs to the power board / Al plate; MH601 next to the RJ45 row" |
| P5C-06 | MINOR | No probe access on nets that must be forced or watched before firmware exists | **Fixed:** THT pads TP306 `PWR_HOLD`, TP307 `FET_EN`, TP308 `KILL_N`, TP804 `EN_12V`, TP805 `EN_ISO`, TP806 `EN_ESP` |
| P5C-07 | MINOR | The root sheet told a reader nothing; title said "7S-16S" | **Fixed:** block diagram on the control root (power tree, ground domains, B2B, wake and kill chains), title "16S LFP"; note block on the power-board root |
| P5C-08 | MINOR | BQ76952 symbol pin 25 named "HDQ_IO/ALERT" (pin 25 = ALERT, HDQ = pin 28); connections correct | **Fixed by note:** on-sheet note "pin 25 = ALERT, pin 28 = HDQ (stock symbol name)"; no netlist change |
| P5C-09 | MINOR | ARCHITECTURE.md contradicted the drawn circuit in several places (TPS3823, TCA9535, LED rails, R_DAMP, 100 V MLCCs, 470 kΩ pull-downs, AUX bleeder) | **Fixed in the documentation pass for schematic v1** |
| P5C-10 | NOTE | With R757 in series, the UCPD dead-battery Rd on PB4 makes `KILL_N` read ≈ 1.1 V until firmware sets UCPD_DBDIS | Firmware rule |
| P5C-11 | NOTE | External watchdog is off whenever PC12 is Hi-Z (blank MCU, ROM, early start-up); Stop mode needs PC12 analog | Firmware rule |
| P5C-12 | NOTE | Watchdog reset leaves ≈ 0.2 s margin on the `PWR_EN` hold; a long NRST turns the board off | Firmware rule (PC6 high first); bring-up: FORCE_ON / AUX for debug on battery |
| P5C-13 | NOTE | Back-power into the unpowered ESP32 limited only by 1 kΩ (≈ 2.7 mA per pin) | Firmware rule |
| P5C-14 | NOTE | RS-485 RO idles high with `+5V_ISO` off (datasheet answers R3-24); CAN RXD not specified | Closes R3-24 for RS-485; CAN measured at bring-up |
| P5C-15 | NOTE | AUX return is `GND_PWR` = battery minus; an AUX supply tied to PACK− parallels the shunt | Note: AUX supply floating or referenced to B− only |
| P5C-16 | NOTE | Charger wake from Ship works only through the AFE configuration (ALERT active-low, INITCOMP unmasked) | OTP checklist item |
| P5C-17 | NOTE | During MCU reset all LEDs are off, also ALM | Accepted with P5C-01 |
| P5C-18 | NOTE | Two hooks on `GND_ISO` (TP108, TP601) | Open (cosmetic) |
| P5C-19 | NOTE | Title-block "Sheet n/9" numbering and bottom-up comment order | Open (cosmetic) |
| P5C-20 | NOTE | U103 note says "TP402, sheet 04" without naming the power board | Open (cosmetic) |
| P5C-21 | NOTE | Pin-name overlaps (U103, U901), J801 pin numbers under the DNP cross | Open (cosmetic) |
| P5C-22 | NOTE | Cell filter ↔ balancer joined only by labels on sheet 02 | Open (cosmetic) |
| P5C-23 | NOTE | Five bring-up gates still open from R1–R3 (U106 pins, `+5V_ISO`, D817 leakage, RJ45 pin 1, B2B row orientation) | Consolidated in [`../SCHEMATIC_V1.md`](../SCHEMATIC_V1.md) §5 |

### Readability verdict (control board)

| Sheet | Verdict |
|---|---|
| Root | Weak before P5 (empty sheet symbols) → block diagram added |
| 01 Power Supply | Good: clear left-to-right flow; boxes and key numbers match the circuit |
| 02 AFE | Acceptable: A2 and dense but ordered |
| 03 MCU | Good: the clearest sheet |
| 05 Aux Outputs | Good |
| 06 Communications | Good, dense; barrier lines and domains clear |
| 08 IO / Front Panel | Good |
| 09 Wireless | Good |
| 10 Memory / Sensors | Good |

Power board: sheet 04 clear and correct to read; sheet 07 power spine and safety island read well once P5-05, P5-06 and P5-07 were fixed.

## Not verified by the review

* Amplitude of any disturbance on `OC_CLR` (P5-02 is argued from the netlist and the latch datasheet).
* DCHG behaviour under UTC / OTC is taken from the TI datasheet / reference manual and the planned AFE image, not from a programmed part.
* BAV170 forward drop at 1 µA and −40 °C (P5C-02); UCPD dead-battery behaviour and the STM32 ROM pin list; CA-IS3050 RXD with VCC2 off.
* All timing and energy numbers remain calc / est. pending the D-04 short-circuit bench test.
