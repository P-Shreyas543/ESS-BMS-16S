# Spec review R1–R3 (2026-11-23) — findings and disposition

Before any sheet was drawn, the pin-level spec of every sheet (parts with live-verified LCSC numbers, and every pin of every part with its net) was given to three independent reviewers who had not written it. Their brief was adversarial: find what is wrong, cite the datasheet page or the netlist row, propose a concrete fix. Each finding was then dispositioned in the sheet design notes ([`../design/`](../design/)) and the fixes were applied to the spec before it was frozen and drawn.

| Review | Scope | BLOCKER | MAJOR | MINOR | NOTE |
|---|---|---|---|---|---|
| R1 | power board: sheet 04 Current Sensing, sheet 07 Power Stage | 1 | 8 | 9 | 9 |
| R2 | sheet 01 Power Supply, sheet 02 AFE / Cell Monitor | 1 | 4 | 13 | 12 |
| R3 | sheets 03 MCU, 05 Aux Outputs, 06 Communications, 08 IO / Front Panel, 09 Wireless, 10 Memory / Sensors | 0 | 2 | 13 | 12 |
| **Total** | | **2** | **14** | **35** | **33** |

Outcome: **both blockers and all 14 MAJOR findings were fixed** in the spec (R1-03 with footprints now and values set by the D-04 bench test; R1-04 with one documented deviation). MINOR findings were fixed or turned into bring-up / layout gates; one (R1-11) is a bench item with a fallback part. The drawn schematic was later checked against this fixed spec by netlist comparison (SPEC MATCH on all 10 sheets) and reviewed again after drawing ([`schematic_review_p5.md`](schematic_review_p5.md)).

Tags in the findings: **DS** = datasheet page, `calc` = reviewer's arithmetic, `est.` = estimate. Nothing was measured.

---

## R1 — power board (sheets 04, 07)

| ID | Sev. | Sheet | Finding | Outcome |
|---|---|---|---|---|
| R1-01 | **BLOCKER** | 07 | Pre-charge / pre-discharge P-FET sources (and their 1 MΩ gate resistors) were on `PACK+` / `BAT+`. With the output off and a load attached, the BQ PCHG / PDSG pin would be pulled far below its abs-max floor max(VBAT − 10, VLD − 10) V, or the P-FET would see V_GS ≈ 48 V. TI's circuit (BQ DS p.67 Fig 16-1) ties both sources to the common-drain node | **Fixed:** Q723 / Q724 sources and R734 / R736 on `FET_MID`; new 16 V gate-source zeners D725 / D726 |
| R1-02 | MAJOR | 07 + 02 | DSG turn-on diode D706 in parallel with the 100 Ω gate resistor: no pin isolation on turn-on, and on an inductive turn-off the DSG pin was pulled below VSS through D706 and the kill path. No VSS clamps on `AFE_DSG` / `AFE_LD` / `AFE_PACK` | **Fixed:** gate networks rebuilt per TI AN09 Fig 5-2 — DSG turn-on R718 + R753 5.1 k + D706; base path R754 1 k + D732; CHG R717 1 k → base node → D705; BAS21 VSS clamps D229 / D230 / D231 at the BQ pins on sheet 02; D722 removed. DSG turn-on 10.2 k × 135 nF ≈ 1.4 ms |
| R1-03 | MAJOR | 07 | A single 22 Ω R_OFF gives a current fall of about 1 µs, not the 15–20 µs controlled turn-off; the interruption is TVS / avalanche-clamped and V_DS > 100 V is expected | **Fixed (footprints; values by SPICE + D-04 bench test):** two-stage turn-off — fast 22 Ω + 5.6 V zener (R721 / D731, R722 / D733), slow 470 Ω (R723 / R724); C716 / C717 22 nF G-S DNP. Sheet note states the TVS-clamped case |
| R1-04 | MAJOR | 07 | DSG kill clamp referenced to `GND_PWR`, not to the bank source: with `PACK+` near 0 V the kill FET turns off early; a stuck AFE driver could hold the bank linear | **Fixed with one deviation:** C718 10 nF hold cap on Q720; C702 → 4.7 nF 2 kV; static-floor PNP Q729 MMBT5401 with **R755 = 100 k 1206 instead of the proposed 4.7 k** (4.7 k would dissipate 0.68 W with `PACK+` at 58 V; 100 k still gives 0.57 mA base, calc); AN09 reverse clamp Q725 / R740 / R741 / D720 / D721 now fitted. Kill-only bench test added to D-04 |
| R1-05 | MAJOR | 04 | The RC + diode power-on reset held CLR_N low for only ≈ 0.12 ms (R415 charged C409 through D401); "power-up tripped" was not guaranteed and brown-out was not covered | **Fixed:** RC / diodes deleted; TLV803SDBZR supervisor U404 wired-OR on `04_CLR_N` holds the latch tripped until 200 ms after `+3V3` > 2.93 V and on brown-out |
| R1-06 | MAJOR | 04 / 07 | `OC_TRIP_N` and `KILL_N`, nodes inside the MCU-independent chain, were wired straight to MCU GPIOs: a GPIO driven high could override the latch or fight U702 | **Fixed:** chain nodes `OC_TRIP_N_PB` and `07_KILL_N_INT` on the power board; 10 k R756 / R757 to the B2B nets |
| R1-07 | MAJOR | 07 | PACK-side clamp (2 × SMCJ60A) too small for the charge-direction interruption and marginal as a freewheel | **Fixed:** 4 × 5.0SMDJ60A (D717, D718, D728, D729); MBRB20200CT freewheel D719 fitted |
| R1-08 | MAJOR | 07 | Heater output at pack potential with no on-board fuse | **Fixed:** F702 0451005.MRL 5 A on board. 7–8 A was asked, but only the 2–5 A rows of the 451 series list 10 kA at 75 VDC, so the heater is limited to 3.5 A continuous (AGENT DECISION, owner may overrule); hardware thermostat in the pad required |
| R1-09 | MAJOR | 04 / 07 | One net carried both the 200 A return and every signal ground, so nothing enforced the star point | **Fixed:** `BAT-` net for the power copper, joined to `GND_PWR` only by NT401 at the shunt Kelvin edge |
| R1-10 | MINOR | 04 | Loss of `+3V3_A` alone left the OC window blind with the latch un-tripped | **Fixed:** CLR_N pull-up R415 from `+3V3_A` (lost analog rail trips the latch) |
| R1-11 | MINOR | 04 | TLV1702 output-low level at 0.33 mA / 3.3 V is not specified; only 0.27 V guaranteed margin to the latch VIL | **Deferred to bench:** measure CLR_N low level at −40 / 25 / 85 °C, pass ≤ 0.6 V; fallback is an open-drain comparator with VOL specified at 3.3 V |
| R1-12 | MINOR | 07 | A single open contact on B2B pin 3 or 4 removes the gate driver undetected | **Fixed:** B2B pin 8 = second `AFE_DSG` contact; firmware watch on (stack − `PACK+`) |
| R1-13 | MINOR | 07 | −100 V pre-charge P-FETs with 0 % margin | **Fixed:** IRF9640SPBF (−200 V) |
| R1-14 | MINOR | 07 | `MCU_NRST` crosses the B2B next to the FET banks with no series impedance | **Fixed:** R758 1 k at J701-22, C719 100 pF at U701, R750 pull-down moved to the gate side (2.97 V high level, calc) |
| R1-15 | MINOR | 04 | INA240 drives the B2B and two MCU pins directly (1 nF max load) | **Fixed:** R419 100 Ω series; ADC reservoir C318 1 nF added on the MCU side in the P5 round (P5-08) |
| R1-16 | MINOR | 07 | Sheet note claimed "unpowered → BOTHOFF + kill" | **Fixed (note):** "+3V3 lost → BOTHOFF only; kill needs +3V3". Refined later by P5-03 (B2B unplugged) |
| R1-17 | MINOR | 07 | THT pads on the 10 MΩ gate buses can be loaded by probes and flux | **Fixed (bring-up note):** ×100 / ≥ 100 MΩ probe only; no-clean flux removed |
| R1-18 | MINOR | 07 | No gate-source clamp on the heater FET | **Fixed:** D730 MMSZ5246BS 16 V from `07_HTR_G` to `PACK-` |
| R1-19 | NOTE | 07 | IPT015N10N5 SOA at 60–100 V not read | **Bring-up plan:** read Diagram 3 before the D-04 test |
| R1-20 | NOTE | 07 | Charge-pump load with hot zener leakage not specified | **Bring-up plan:** measure CP1 − BAT at 85 °C |
| R1-21 | NOTE | 07 | CHG pin in SHUTDOWN through Q717 E-B with no base resistor | Covered by R1-02 (1 k base resistor) |
| R1-22 | NOTE | 07 | F701 ratings confirmed | Noted |
| R1-23 | NOTE | 04 | Window maths confirmed: +599 A / −305 A | Noted |
| R1-24 | NOTE | 04 | INA240, TLV1702, AUP1G74 pin maps and shunt polarity confirmed | Noted |
| R1-25 | NOTE | 07 | All discrete pin numbers vs symbols vs pads checked: no error | Noted |
| R1-26 | NOTE | 04 / 07 | No single-connection nets; no rail-domain mix | Noted |
| R1-27 | NOTE | 07 | NTC_FET thermally weakly coupled to the FET island | **Bring-up plan:** characterise the offset, lower OTF |

---

## R2 — power tree and AFE (sheets 01, 02)

| ID | Sev. | Sheet | Finding | Outcome |
|---|---|---|---|---|
| R2-01 | **BLOCKER** | 01 | B0505S-2WR3 input pins swapped against its own datasheet (DS p.5: pin 1 = Vin, pin 2 = GND) | **Fixed:** U106 pin 1 = Vin, pin 2 = GND, symbol corrected. **Bring-up gate before the board order:** confirm on a physical sample |
| R2-02 | MAJOR | 02 | CELL_0: the hard VC0–VSS tie is right, but J201 pin 1 formed a second low-impedance return in parallel with the B− cable | **Fixed:** NT201 kept for the on-board VC0 node; J201 pin 1 on `02_CELL0_HARN` → R274 10 Ω pulse-proof → `GND_PWR`. Cell 1 then reads I × R of the B− path: firmware compensates from the CC current; **B− cable + lug ≤ 0.1 mΩ**; pin 1 optional in the harness, B− lug first on / last off |
| R2-03 | MAJOR | 02 | Cell-1 filter capacitor drawn VC1–VC0; TI requires VC1 to VSS | **Fixed:** C201 pin 2 → `GND_PWR` |
| R2-04 | MAJOR | 02 | A blank BQ76952 (REG1 disabled) could not be programmed: the only I2C pull-ups went to the dead `AFE_REG1`, and a fixture pull-up would back-feed REG1 | **Fixed:** D227 BAT54WS from `AFE_REG1` to the new pull-up node `02_I2C_PU`; blank-part programming sequence written into the sheet 02 note |
| R2-05 | MAJOR | 01 | Power-latch off-state not guaranteed: shutdown is 0.45 V falling, not 1.1 V; AO3401A off-leakage on the 1 MΩ `PWR_EN` node; AUX bleeder undersized and over-stressed | **Fixed:** R123 / R124 100 k drain pull-downs, R125 / R126 1 k drain series resistors; R_AUXB = 2 × 33 k 1206 in parallel (R103 + R127); notes say 0.45 V falling |
| R2-06 | MINOR | 02 | REG0 headroom during OTP is thin at 11.5 V | **Fixed (procedure):** fixture 12.3 V on J201 pin 18, 11.5 V on pin 17, I2C ≤ 100 kHz |
| R2-07 | MINOR | 02 | R251 (0603) takes the hot-plug pulse of the 1 µF BAT capacitor | **Fixed:** 100 Ω 1206 pulse-proof CRCW-HP |
| R2-08 | MINOR | 02 | R216 (VC16) above 50 % of its rating while balancing cell 16 | **Fixed:** 100 Ω 1206 (62 mW = 25 %) |
| R2-09 | MINOR | 02 | 2N7002 balancer-enable FET not specified at a 3.3 V gate | **Fixed:** BSS138BK (≤ 4.5 Ω at VGS 2.5 V, 60 V) |
| R2-10 | MINOR | 02 | Active-balancer header ground is a second parallel path to B− | **Fixed:** J204 pin 2 via R275 10 Ω (may become 0 Ω or an opto once the module is known) |
| R2-11 | MINOR | 02 | TS2 wake line goes off-board with no series resistor | **Fixed:** R276 1 kΩ; leakage budget on `WAKE_BTN_RAW` handed to sheet 08 |
| R2-12 | MINOR | 02 | One connector pin (18) feeds the whole AFE | **Fixed:** D228 1N4148WS backup from `02_CELL16` to `BAT_SNS` (owner may overrule D-15) |
| R2-13 | MINOR | 02 / 07 | SHUTDOWN / Ship is delayed while LD stays high (charger or parallel pack) | **Fixed (note):** documented system behaviour; no LD pull-down option added |
| R2-14 | MINOR | 01 / doc | Sleep budget assumed 470 kΩ AFE_FLT pull-downs; they are now 100 kΩ | **Fixed (text):** with output off the pins are low (0 µA); "output live" option adds 2 × 33 µA. ARCH §4.3 corrected for schematic v1 |
| R2-15 | MINOR | 01 | Supply-input clamp margin shrinks hot (≈ 96 V at 85 °C against 100 V) | **Fixed:** R_DAMP 2 × 2.2 Ω 2 W 2512 (RC2512FK-7W2R2L): TVS current ≈ 3.8 A, clamp ≈ 79 V at 25 °C (calc) |
| R2-16 | MINOR | 01 / 09 | `+3V3_ESP` output capacitance beyond the TLV62569 proven matrix | **Fixed:** C123 DNP (22 µF + 10 µF at the module) |
| R2-17 | MINOR | 02 / 07 | B2B pin n ↔ pin n only holds for one placement; a row swap puts `VSUP_TAP` on `AFE_PACK` | **Layout gate:** pin 1 ↔ pin 1 in the 3D stack and on a 1:1 print |
| R2-18 | MINOR | 08 | 1 MΩ wake pull-up too weak against P-FET / pin leakage | **Fixed on sheet 08:** R824 220 kΩ |
| R2-19 | NOTE | 01 | Regulator networks reproduced; no finding | Noted |
| R2-20 | NOTE | 01 | Worst-case +5V ≈ 5.25 V against 5.5 V | Noted, no change |
| R2-21 | NOTE | 01 | Latch hold worst case ≈ 0.43 s against 0.21 s wake latency | Noted, no change |
| R2-22 | NOTE | 01 | AUX-only bench mode back-energises `VSUP_TAP` / `BAT+` through SS320 leakage | **Bring-up note:** treat BAT+ as live |
| R2-23 | NOTE | 01 | DC-bias loss of the input MLCCs at 58 V not read | Noted (read curve or measure) |
| R2-24 | NOTE | 01 | D103 polarity confirmed | Noted |
| R2-25 | NOTE | 01 / 02 | Symbol / footprint / netlist cross-check: no mismatch | Noted |
| R2-26 | NOTE | 02 | FCX495 pinout confirmed | Closed (unverified item closed) |
| R2-27 | NOTE | 02 | BQ pin map, SRP / SRN polarity, J206 vs the pin map confirmed | Noted |
| R2-28 | NOTE | 02 | Balancing stage matches TI AN81 Fig 2-5 | Noted |
| R2-29 | NOTE | 02 | An open B− cable under load is destructive in every variant | **Harness spec:** ≤ 0.5 A fuse per cell tap |
| R2-30 | NOTE | 01 / 03 | `AFE_ALERT` / `WAKE_BTN_N` read low while the AFE is off | **Firmware rule** |
| R2-31 | NOTE | 02 / 07 | `AFE_CHG` transient; TP212 / TP213 are 58–71 V pads | **Layout:** HV clearance; `AFE_CHG` watched in P5-14 / D-04 |
| R2-32 | NOTE | 01 | Isolation 1500 VDC against ≥ 2.5 kVrms | Noted (D-09 still open) |

---

## R3 — MCU, IO, comms (sheets 03, 05, 06, 08, 09, 10)

R3 found no wiring error that would make a board non-functional: every MCU alternate function, UART / CAN / SPI / I2C direction, isolator side and symbol-pin ↔ net assignment it could check was correct. Its two MAJOR items were fail-safe / rail-limit gaps.

| ID | Sev. | Sheet | Finding | Outcome |
|---|---|---|---|---|
| R3-01 | MAJOR | 08 | TCA9535 expanders have no reset pin: on an MCU reset the last written outputs (dry contacts, rail enables, balancer enable) stay latched | **Fixed:** TCA9539PWR (C131972) with RESET = `MCU_NRST`; pin-out verified on TI SCPS202C p.3–4; addresses 0x74 / 0x75 |
| R3-02 | MAJOR | 06 / 01 | `+5V_ISO` runs far below the 40 mA minimum load of the B0505S in idle; the dummy load was DNP | **Fixed:** R122 + R128 300 Ω 1206 fitted in parallel = 150 Ω / 33 mA. **Bring-up gate:** ≤ 5.5 V at idle and −40 °C |
| R3-03 | MINOR | 09 | Ninth GND EPAD square missing from the generated ESP32-C3 footprint | **Fixed:** pad 49 restored; re-checked against the module land pattern (DS fig 11-1) |
| R3-04 | MINOR | 08 | 10 kΩ read-back resistors let a stuck expander output override "Hi-Z = fault" on the kill inputs | **Fixed:** R809–R811 470 kΩ series (worst case lifts the node to 0.58 V, calc) |
| R3-05 | MINOR | 05 | EXT PTC trips above the LM5163 current limit at −40 °C | **Fixed:** SMD1206P012TF (C20982); EXT rating ≤ 70 mA at 85 °C / ≤ 120 mA at 25 °C |
| R3-06 | MINOR | 05 | 25 kHz low-side PWM of a 3-wire fan's supply | **Fixed:** 4-pin fan header (DLL 2510-4A), open-drain PWM on pin 4 (Q504); Q501 on / off from new `FAN_EN` (U801 P14) |
| R3-07 | MINOR | 06 | No current limit between the RS-485 TVS and the −8 / +13 V transceiver pins | **Fixed:** 10 Ω anti-surge ESR10 resistors R630–R633 |
| R3-08 | MINOR | 03 | No way to disable the external watchdog for debugging | **Fixed:** JP302 normally-closed solder jumper in `WDI`, TP305 on the supervisor side |
| R3-09 | MINOR | 10 | FRAM CS high level in ROM-bootloader mode only 47 mV above VIH | **Fixed:** R1001 / R1002 4.7 kΩ (2.78 V worst case) |
| R3-10 | MINOR | 08 | Wake button is a touch point without ESD protection | **Fixed, partly verified:** D817 PESD5V0S1BA always fitted + R837 100 Ω; leakage at 85 °C is a **bring-up gate** |
| R3-11 | MINOR | 08 | `GND_PWR` (= battery minus) on a field terminal with no impedance | **Fixed:** R836 100 Ω 1206 in the J802 pin-6 return |
| R3-12 | MINOR | 03 | MCU inputs from the power board float with the B2B unplugged | **Fixed:** R304 / R305 / R306 1 MΩ to `GND_PWR` on `OC_TRIP_N`, `KILL_N`, `ISENSE_OUT` |
| R3-13 | MINOR | 09 | UART4 RX undefined while the ESP is off | **Fixed:** R911 100 k pull-up on `ESP_TXD` |
| R3-14 | MINOR | 06 | Split-termination poles must be switched together | **Fixed (text):** on-sheet note, PCB silk "1+2 = CAN TERM, switch together", manual note |
| R3-15 | MINOR | 08 / 01 | `+5V` / `+3V3` leave the board on J801 without a current limit | **Fixed:** F801 / F802 PTC 100 mA, DNP with J801 |
| R3-16 | NOTE | 03 / 06 | UCPD dead-battery Rd on PB4 / PB6 after reset | **Firmware rule:** set UCPD_DBDIS early (sharpened by P5C-10) |
| R3-17 | NOTE | 03 | PB4 is NJTRST: SWD works, JTAG would not | Noted (SWD only) |
| R3-18 | NOTE | 03 | PA8 I2C2_SDA confirmed against DS12712 Table 12 | Closed |
| R3-19 | NOTE | 03 | EXTI map has no conflict | Noted (firmware note) |
| R3-20 | NOTE | 03 / 01 | ROM bootloader / blank MCU does not drive `PWR_HOLD`: first flashing needs FORCE_ON | Carried as a bring-up rule (SCHEMATIC_V1 §5 gate 8) |
| R3-21 | NOTE | 03 | PC0–PC3 share TIM1 | **Firmware note** |
| R3-22 | NOTE | 03 | LSE drive level on the FC-135 class crystal | Carried as a bring-up item: start-up at −40 °C with LSEDRV 10 / 11 |
| R3-23 | NOTE | 06 | RJ45 pin 1 from a generated footprint; a mirror swaps CANH / CANL | **Layout gate** |
| R3-24 | NOTE | 06 | Receiver output state with `EN_ISO` = 0 not specified | **Firmware rule;** RS-485 closed by P5C-14 from the datasheet, CAN RXD measured at bring-up |
| R3-25 | NOTE | 08 | SMAJ36CA clamp vs 60 V photoMOS rating | Dry contacts stated as ≤ 30 V working (sheet 08 decision 7); no part change |
| R3-26 | NOTE | 08 / 02 / 07 | Stale cross-references (R827, 470 k vs 100 k) | **Fixed** in the sheet notes and in ARCH for schematic v1 |
| R3-27 | NOTE | 08 | Expander INT not connected: ≤ 50 ms polling latency | Noted |
