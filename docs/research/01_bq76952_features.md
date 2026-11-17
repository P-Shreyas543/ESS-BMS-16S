# BQ76952 (U_AFE1, BQ7695202PFBR): getting the most out of the AFE

Research only, 2026-11-17. No project file was changed. Topic owner: AFE features. Balancing is covered in depth by another agent; this file covers the AFE side of it only.

## 0. Sources and how to read the citations

All documents below were downloaded from ti.com and read as text extracts. They are saved in `research\ds_trm\` (PDF and `.txt` with page markers). The page numbers are PDF pages, and they match the printed page numbers of each document.

| Tag | Document | Revision |
|---|---|---|
| **DS** | BQ76952 data sheet, SLUSE13 | SLUSE13B, Nov 2021 (`review\ds\bq76952.pdf`) |
| **TRM** | BQ76952 Technical Reference Manual, SLUUBY2 | SLUUBY2B, May 2022 |
| **AN09** | Multiple FETs with the BQ769x2 Battery Monitors | SLUAA09A, Mar 2022 |
| **AN84** | Using Low-Side FETs with the BQ769x2 Battery Monitor Family | SLUAA84A, Feb 2022 |
| **AN81** | Cell Balancing With BQ769x2 Battery Monitors | SLUAA81A, Feb 2022 |
| **AN32** | BQ769x2 Calibration and OTP Programming Guide | SLUAA32A, Sep 2021 |
| **AN11** | BQ769x2 Software Development Guide (CRC examples) | SLUAA11B, Aug 2021 |
| **FAQ** | BQ769x2 Frequently Asked Questions | SLUAAQ5, May 2024 |
| **ANn9** | Design Considerations of Stacked BQ769x2 With High-Side N-MOSFET | SLUAAN9, Feb 2023 (title page only; not used) |

**Correction to `requirements_review.md`.** That review names **SLUA964** as TI's external-balancing note. SLUA964 is "Improving Efficiency of DC-DC Conversion through Layout" (opened, page 1). The correct note is **SLUAA81A** (AN81).

Other markings used in this file:
* "calc" means my arithmetic.
* "inferred" means my reading of TI text that TI does not state outright.
* "unverified" means not checked in any document.
* No competitor (Daly / JBD / JK) data sheet was opened. The "Value" column states what the feature enables. It makes no claim about what a given competitor lacks.

### 0.1 Facts about this variant (BQ7695202)

* **Defaults that differ from the base part.** I2C interface, **CRC enabled**, **REG1 LDO enabled at 3.3 V** (DS p.4 Device Comparison Table; FAQ p.3).
  * Comm Type default 0 means "use the variant default" (TRM p.73 Table 9-1, p.138).
  * I2C address 0x10 write / 0x11 read (TRM p.74).
  * CRC is CRC-8, polynomial x⁸+x²+x+1, initial value 0. On a block transfer it is sent per byte: the first byte's CRC covers the address bytes, and each later byte's CRC covers that byte only (DS p.54–55; TRM p.74–75; worked examples in AN11 p.12–13).
* **REG0 default for the -02 variant: not verified.** The data memory table lists REG0 Config default 0x00 and REG12 Config 0x00 for the base part (TRM p.200). The -02 data sheet row only says "REG1 enabled, 3.3 V". FAQ p.11 says the -02 lets REG1 power an MCU without OTP, which suggests REG0 is also on by default for -02 (inferred). On this board it does not matter today, because REGIN is tied to VSS.
* **Defaults that matter for safety** (base data-memory defaults, TRM p.197–203; assumed equal for -02 except comm and REG1):

| Setting | Default | What it means |
|---|---|---|
| Enabled Protections A | 0x88 | Only SCD and COV are on |
| Enabled Protections B / C | 0x00 | No temperature, OCD3 or latch protections |
| COV threshold | 86 × 50.6 mV = **4.35 V** | Far above LFP (calc) |
| SCD threshold | code 0 = **10 mV** | 100 A with a 100 µΩ shunt |
| Mfg Status Init | 0x0040 | **[FET_EN] = 0, so the part starts in FET Test mode**: FETs are not enabled autonomously (TRM p.33) |
| DA Configuration | 0x05 | USER_AMPS = 1 mA, so 16-bit current reports **saturate at ±32.7 A** (TRM p.20, p.154) |
| Pin configs | TS1 = 0x07 (18 k NTC, cell temperature); TS2, TS3, ALERT, DCHG, DDSG, CFETOFF, DFETOFF, HDQ = 0x00 (unused) | |
| Security keys | Unseal 0x0414 / 0x3672 (TI-published); full access 0xFFFF / 0xFFFF | TRM p.197 |

  **Conclusion:** without OTP or a host write after every power-up, the AFE is **not** a usable MCU-independent protector for LFP.

---

## 1. Feature table

Effort: **S** = config or 1–3 passives. **M** = small circuit plus firmware. **L** = new power-stage design or production process.

| # | Feature | Used today | How to use it | Parts / pins / FW | Value | Effort |
|---|---|---|---|---|---|---|
| 1a | **CUV / COV** (comparator; 1.012–5.566 V / 1.012–4.048 V in 50.6 mV steps; delay 10 ms–6.75 s) (DS p.21; TRM p.35–38) | Detection only, and COV only by default (0x88). No action path: CHG / DSG not connected, ALERT to MCU only | Enable CUV + COV. Set LFP thresholds (e.g. COV 3.65 V → code 72 = 3.643 V; CUV 2.5 V → code 49 = 2.479 V, calc). COV snapshot through 0x0081, CUV through 0x0080 (TRM p.37–38). COVL latch for repeated COV (TRM p.36) | OTP / host config only | Hardware OV / UV with ±5–25 mV threshold accuracy (DS p.21), independent of the MCU once wired to a gate-kill (§1.3) | S |
| 1b | **OCC / OCD1 / OCD2 / SCD** (comparators on SRP–SRN). OCC 4–124 mV, 2 mV steps; OCD1/2 4–200 mV; delay 10–425 ms. SCD 10–500 mV in 16 steps, delay "fastest" or 15–450 µs; fastest is ≈600 ns at 25 mV overdrive (DS p.22; TRM p.38–41) | SRP/SRN wired to `SH_P/SH_N`; external shunt; only SCD on by default | With the on-board shunt (§1.4), set the tiers: OCD3 = firmware, CC1-based, accurate, 0–255 s (TRM p.41); OCD1/OCD2 = fast comparator tiers; SCD = short circuit. Add latches OCDL / SCDL with Load-Detect / time / command recovery (TRM p.39–42) | Shunt + 100 Ω / 100 nF filter (DS p.65, p.76) | Sub-µs short-circuit detect in silicon; a 3-tier OC profile like an automotive pack | S (config), M (shunt) |
| 1c | **Temperature protections** OTC / OTD / OTF / OTINT / UTC / UTD / UTINT; −40…120 °C (OTF 0–150 °C), 1 °C steps, delay 0–255 s (TRM p.43–45) | None enabled (Prot B default 0x00). Only TS1 configured | Enable with ESS limits; assign each NTC as "cell" or "FET" through pin config OPT bits (TRM p.58 Table 6-6) | Config | Redundant thermal shutdown (requirement R16), once wired to a gate-kill | S |
| 1d | **Latch / recovery** — autonomous (COV/CUV hysteresis + Recovery Time; OCC via PACK–TOS delta or discharge current; OCD via charge current; SCD via time; SCDL/OCDL via Load Detect, charge current, time or command) (TRM p.36–42, p.46) | – | Choose per fault: autonomous for COV/CUV/temperature; latched with host or LD recovery for SCD/OCD | Config + LD pin (§1.6) | Self-recovering pack without a host is possible | S |
| 1e | **Works without MCU?** Yes, "fully autonomous" mode exists (DS p.44, p.47 §12.4; TRM p.32), **provided** (a) [FET_EN] = 1 and protections enabled (OTP, §1.9), and (b) a hardware path from the AFE decision to the power switch exists. Turn-off is "fast" only if CHG FET Prot A = 0x18 / 0x98 and DSG FET Prot A = 0x80 / 0xE4; otherwise up to 250 ms (NORMAL) or 1 s (SLEEP) (TRM p.34, p.62 Table 6-9) | **No** (review A9 / R15 / R16) | DDSG / DCHG to a gate-kill (§1.3), or CHG / DSG to a FET bank (§1.2) | – | Closes blocker A9 | M |
| 2a | **CHG / DSG high-side NFET drivers + charge pump.** Overdrive 11 V (10–13 V) or 5.5 V; CP1 cap 100 nF–2.2 µF (470 nF typ); tON 21–40 µs at 20 nF; DSG off 2–20 µs. DSG off-drive pulses toward LD; source-follower mode in SLEEP (DS p.20, p.44, p.72–74; TRM p.31–33) | Not used. CP1 has 100 nF to BAT; charge pump enabled by default (Chg Pump Control 0x01, TRM p.197) | **Contactor build:** CHG / DSG float, CP1 tied to BAT, [CPEN] = 0 (DS p.75; AN84 p.9). **FET build:** §2 | – | – | – |
| 2b | **PCHG / PDSG** PFET drivers (BAT−8.4 V gate, 30 µA sink; 1 MΩ G–S recommended). Precharge by min-cell threshold; predischarge by timeout or LD-delta (DS p.12, p.45; TRM p.35) | Not used | FET build only: PDSG PFET + R replaces Q_PRE1 / R_PRE1 / pre-charge contactor; PCHG for deep-discharged LFP recovery charge. PTO timeout fault (TRM p.45) | PFET + R + 1 MΩ each | Inrush control and recovery charge in silicon | M (FET build) |
| 2c | **Body-diode protection** (series FETs) (TRM p.33) | – | FET build: [SFET] = 1 | Config | Protects an off FET from body-diode heating | S |
| 3a | **FUSE pin.** Drives an NFET gate (6–9 V at 5 kΩ, ≤ 2 mA in), senses a second-level protector's drive, PF-triggered; fuse-blow only above Min Blow Fuse Voltage (stack or PACK); timeout 30 s default (DS p.12, p.49–50 Fig 12-1; TRM p.61, p.197) | Unconnected | NFET (≥ 100 V) driving a 3-terminal chemical fuse heater, or a DC-breaker shunt-trip coil. Optional external OV protector OR-ed onto the same node (2LVL PF) | 1 NFET, series R, 100 kΩ pull-down (Fig 12-1 labels read 5.1 kΩ and 100 kΩ; garbled in extract, inferred); fuse or shunt-trip part not selected | Permanent, MCU-independent last-resort disconnect (UL 1973 / IEC 62619 "secondary protection" story) | M |
| 3b | **DDSG / DCHG** logic outputs: assert on any fault that would turn off DSG / CHG. Active in NORMAL, SLEEP and **DEEPSLEEP**; Hi-Z in SHUTDOWN; polarity programmable; drive from REG18 (> 1 MΩ loads only) or **REG1** (TRM p.56–61; DS p.48–49). They "combine the FET output states with the precharge and predischarge states" (AN84 p.3) | Used as **thermistor inputs** (NTC4, RT_BOARD) | Re-assign to DDSG / DCHG and feed a hardware gate-kill (AND / NOR + small FETs) in front of R_G1-3, together with the OCP latch and the MCU command (§3). Needs REG1 powered for a 3.3 V high level. Do **not** use DSG_PDSG_OFF / CHG_PCHG_OFF / FET_CONTROL with DDSG / DCHG mode (TRM p.34) | 2 pins, 1 logic IC, pull-downs (fail-safe = kill), REG1 | The key fix: the AFE can open the contactors itself | M |
| 3c | **ALERT** (open-drain / push-pull, maskable alarm; SSA comparator faults are "fast" (TRM p.59–62) | To PB10, **no pull-up** (A8); pin config default 0x00, i.e. alarm **not enabled** | ALERT Pin Config [PIN_FXN] = 0b10, open-drain active-low; 10 kΩ to +3V3; mask SF / PF alerts; INITCOMP / FULLSCAN for startup sync | 1 R; FW | Interrupt-driven host; no polling | S |
| 3d | **CFETOFF / DFETOFF / BOTHOFF** inputs (TRM p.56–59) | Unconnected | DFETOFF as **BOTHOFF**, driven by the MCU and/or the OCP latch, so every kill source goes through one AFE decision (and so through DDSG / DCHG). CFETOFF is then free for an NTC (DS p.48) | 1 pin + R | Fast host kill without the bus | S |
| 3e | **Host watchdog (HWD)**, 0–65535 s; turns FETs off, can toggle or disable REG1/REG2 (TRM p.45) | Not enabled | Enable (e.g. 2–5 s) and map it to the DSG/CHG FET Protections C → DDSG/DCHG → gate-kill | Config | **A second, independent MCU watchdog** next to TPS3823 | S |
| 4 | **Coulomb counter (SRP/SRN)**: ±200 mV measuring range; pins tolerate up to 0.75 V without measuring. CC1 16-bit every 250 ms; CC2 24-bit every 3 ms (1.5 ms FASTADC), 14–15 noise-free bits; CC3 average of up to 255 CC2 samples; 64-bit accumulated charge + time; offset ≤ ±1 LSB (7.6 µV) uncalibrated, drift 0.03 LSB/°C; gain 130845–132335 LSB/V; 50 ppm/°C shunt required (DS p.9, p.15–16, p.37–38, p.76; TRM p.20–21) | Wired straight to the external shunt (shared with INA240), no own RC filter (C9), units 1 mA | On-board shunt, own 100 Ω + 100 nF filter at the pins; USER_AMPS = 100 mA (±3276 A range); CC Gain = 7.4768 / R(mΩ) = 74.77 for 100 µΩ (TRM p.127; range 0.01–1000; AN32 p.6 prints 0.1–10, so the TRM is used here). Board-offset and CC-gain calibration (AN32 p.5–6). Shunt sizing in §4 | Shunt, 2 R, 1–3 C | Precise SoC in the AFE, running also in SLEEP; synchronized V/I | M |
| 4b | **Synchronized V + I** per cell (DASTATUS1-4, 0x0071–0x0074) (DS p.38; TRM p.21) | – | FW: per-cell DC impedance → SoH / weak-cell / loose-busbar detection | FW | Diagnostics beyond SoC (sales feature) | M (FW) |
| 4c | **Interconnect-resistance compensation** (TRM p.18–20, "Cell n Interconnect" in mΩ) | – | Enter busbar resistances; or use spare VC inputs as Kelvin interconnect sense (DS p.75) | Config | Accurate cell V under 200 A | S |
| 5 | **Multifunction pins**: up to **9 NTCs** (TS1-3, CFETOFF, DFETOFF, ALERT, HDQ, DCHG, DDSG); 18 k or 180 k internal pull-up, 18K / 180K / custom polynomial; ADCIN 0–≈2.02 V reported in mV; GPO high/low by command (0x2800–0x2818) (DS p.38, p.47–48; TRM p.20, p.56–58; FAQ p.13–14) | 5 NTCs on TS1, TS2, TS3, DCHG, DDSG; NTC caps **10 nF** | See the pin plan in §5 / §2 table: 4 pack NTCs on TS1, TS3, HDQ, CFETOFF; board temperature from the die sensor (or TS2); DCHG / DDSG become fault outputs. Reduce NTC caps to ≤ 3.3 nF: rule τ < 5 % of 3 ms with 18 k → C < 4 nF (DS p.65) | Re-label 2 nets, swap 5 caps | 5–6 temperatures plus 2 hardware fault outputs from one chip | S |
| 6a | **REG1 / REG2** LDOs: 1.8 / 2.5 / 3.0 / 3.3 / 5.0 V, 45 mA each, 47–80 mA short-circuit limit; ≥ 1 µF; REG1 needs REGIN ≥ 4.1 V for 3.3 V (DS p.13–14) | REG1 has 2.2 µF but **REGIN = VSS**, so it is dead; REG2 open | Power REGIN from the REG0 pre-regulator (§6b). Use REG1 3.3 V as the AFE-side logic supply (DDSG/DCHG high level, gate-kill logic, ALERT/I2C pull-ups if wanted). **Not** for the STM32 main supply (45 mA limit, NPN heat, calc below) | Config (REG1 already on in -02) | Protection logic stays powered from the stack even if the buck chain fails (only if fed from REG0, not from +5V, see §6) | S–M |
| 6b | **REG0 pre-regulator** (BREG drives an external NPN; REGIN 5–5.8 V; REGIN cap 15–27 nF; BREG ≤ 3.3 mA; 10 MΩ BREG–VSS; collector diode; REGIN must never exceed BAT) (DS p.13, p.46, p.64, p.69) | BREG floating, REGIN on VSS (A5 deviation: both must go to VSS if unused, DS p.75) | NPN (Vce ≥ 100 V, e.g. SOT-89; part not selected), diode in collector from stack, 22 nF REGIN, 10 MΩ BREG; REG0_EN = 1. Power at 5 mA load: (58.4 − 5.5) V × 5 mA = 0.26 W (calc); at 45 mA it is 2.4 W, too much | 4 parts | Enables REG1 / DDSG / DCHG drive | S |
| 6c | **LD / PACK** pins: 0–80 V divider measurement ±0.5 V; LD 100 µA pull-up for load detect, wake on LD rising 0.8–2.25 V; PACK–TOS delta used for OCC recovery and SLEEP charger detect (DS p.9–10, p.12, p.45, p.52; TRM p.40, p.46, p.66–68) | **Both on VSS.** PACK reads 0 V, so the OCC "PACK ≤ TOS − delta" recovery is always true (inferred from TRM p.40–41) and charger detect is dead | PACK → 10 kΩ → `V_INVERTER_BUS` (bus voltage for pre-charge-done and contactor-weld checks; valid only with NEG closed, same limit as R_HV divider D5) or to top of stack (DS p.65). LD: contactor build stays on VSS, or use a "remote-ON / wake" input that pulls LD above 2.25 V to wake from SHUTDOWN (DS p.65). FET build: 10 kΩ to PACK+ | 1–2 R, small clamp | Bus-voltage measurement without the MCU ADC; wake-on-switch | S |
| 6d | **Power modes**: NORMAL 286 µA; SLEEP 24–41 µA (comparator protections stay on, wake on 12 ms current check); DEEPSLEEP 9.2–10.7 µA (REG1/2 can stay on, no protection); SHUTDOWN 1 µA typ / 3.1 µA max, wake by TS2 pulled low or LD rising; auto-shutdown on low stack / cell / high temperature (DS p.10–11, p.51–53; TRM p.66–69) | Sleep possible; SHUTDOWN **blocked by the NTC on TS2** (DS p.53; TRM p.136 [SHUT_TS2]) | Free TS2 for a wake button / remote input. Low-V auto-shutdown protects a pack left empty in storage. Whole-board ship mode needs the LM5164 enable gated by the AFE (e.g. REG2): option, not costed | TS2 re-map; option: EN gating | Storage self-discharge / ship mode | S (TS2) / M (EN) |
| 7 | **Comms**: I2C 100 / 400 kHz with optional CRC, clock-stretch, block R/W, 2 s bus reset, optional timeouts (no Comm Type combines CRC + timeouts: TRM p.73). SPI ≤ 2 MHz, CPOL = CPHA = 0, 16-bit (24-bit with CRC) per byte, **no block R/W**, ≥ 50 µs between transactions, **MISO drives 1.8 V unless [MISO_REG1] = 1 with REG1 on**. HDQ one-wire, ~190 µs bit cycle (DS p.23–25, p.54–63; TRM p.73–83; FAQ p.11) | I2C+CRC (-02 default) on **PB6 (no I2C AF) / PB7 + PB9** | **Recommend: stay on I2C Fast with CRC (Comm Type 0x12)** and fix the pins: SCL → **PA15** (I2C1_SCL), SDA → PB7 only (I2C1_SDA), drop PB9 (KiCad symbol `STM32G431C_6-8-B_Tx` alternates; DS12589 still not opened). Optional per DS p.76: series R + Zener on SCL / SDA. Reasons in §7 | 2 nets moved | Robust, CRC-protected link, fewer AFE pins used | S |
| 8 | **Balancing (AFE side)**: internal R_CB 15/28/46 Ω; 100 mA abs-max per cell; autonomous = non-adjacent only, "Cell Balance Max Cells" (default 1), charge / relax windows, die-temperature cut-off, CB_LOOP_SLOW to raise the average current; host mode = adjacent allowed, auto-stop after Cell Balance Interval (default 20 s); CBSTATUS1-3 timers (DS p.8, p.18, p.63–64; TRM p.85–87, p.200; AN81 p.3, p.11; FAQ p.16–17) | External N-FET topology like AN81 Fig 2-2 (gate on R_VC(n−1) drop), **no gate Zener / gate resistor** (AN81 p.4 says one is needed) | Host-controlled (MCU algorithm, SoC-based) using CB_ACTIVE_CELLS; keep the autonomous algorithm as fallback. AN81 rule: FET R_DS(on) must be specified at V_GS ≤ V_cell × R / (2R + R_CB), e.g. 1.73 V at 3.9 V (AN81 p.4); at 3.4 V (LFP) with 100 Ω/100 Ω/28 Ω → 1.49 V (calc). FAQ p.17: VC16 R = 20 Ω recommended (today 100 Ω). **Details: balancing agent** | Zener + R per FET (balancing agent) | Faster, cooler balancing | – |
| 9a | **Permanent Fail** suite: SUV, SOV, SOCC, SOCD, SOT, SOTF, CUDEP, VIMR / VIMA, TOS-vs-cell-sum, CFETF / DFETF, 2LVL, OTP / ROM / LFO / VREF / VSS / MUX faults, commanded PF; 1 s evaluation; actions: flag / FETs off / FUSE / DEEPSLEEP; PF status optionally written to OTP (DS p.42–44; TRM p.46–51) | Not used (Enabled PF C = 0x07 memory checks only, by default) | Enable SOV / SUV / SOT / VIMR / TOS + PF_OTP; route to FUSE (3a) and DDSG / DCHG | Config | Field-traceable permanent faults (warranty and safety evidence) | S |
| 9b | **Diagnostics**: VREF1 vs VREF2, VSS, LFO, protection-mux, TOS check, cell open-wire (22–95 µA pulses), memory signatures, internal watchdog (DS p.18, p.33, p.50; TRM §11) | – | Enable open-wire + diagnostics; log in EEPROM | Config / FW | IEC 60730-style self-test story | S |
| 9c | **Security**: SEALED / UNSEALED / FULLACCESS; change keys with 0x0035; [SEAL] at power-up, [LOCK_CFG], [PERM_SEAL]; IROM / DROM / static-config signatures (DS p.34; TRM p.71–72, p.197) | Defaults (published keys) | Set customer keys, SEAL in OTP; read STATIC_CFG_SIG at boot | Config | Tamper resistance; configuration integrity check at boot | S |
| 9d | **OTP programming**: two XOR images, ≤ 8 signature writes; **10–12 V on BAT (and VC16, FAQ p.12), cells NOT connected, −40…45 °C**, FULLACCESS + CONFIG_UPDATE, OTP_WR_CHECK 0x00A0 → OTP_WRITE 0x00A1 (DS p.9; TRM p.14–15; AN32 p.14; FAQ p.11–12). 32-byte scratchpad / MANU_DATA for serial numbers (DS p.34) | Not planned | EOL station: 11–12 V on J1 (BAT through D_BAT1; check that BAT ends up ≥ 10 V) and on `CELL_16`, MCU firmware in "factory mode" writes the golden image over I2C (+3V3 comes up through LMR16006Y / AP2112 at that input, inferred; LM5164 runs in dropout) | Fixture + FW | Safe defaults from first power-up; MCU-independent protection | M–L |
| 9e | **Calibration**: cell gain (2-point), cell offset, TOS / PACK / LD gain, board offset, CC gain, temperature offsets, COV / CUV comparator calibration (DS p.39–41, p.70; AN32 p.2–8) | – | 2-point cell calibration (2.5 V / 4.2 V) and CC gain at 2 currents on the EOL station; write into the same OTP image | Fixture + FW | Datasheet accuracy is "after board-offset calibration" (DS p.10 note 2) | M |

---

## 2. FETs instead of, or as well as, the contactors

| Topology | How the AFE drives it | What it takes (48 V, 200 A cont / 500 A peak) | Notes |
|---|---|---|---|
| **A. Keep contactors + AFE gate-kill** (recommended now) | DDSG / DCHG (REG1-driven) → AND with MCU commands and the OCP latch → Q_POS1 / Q_NEG1 / Q_PRE1 gates | 1 logic IC (e.g. a 3-input AND per channel, or a single kill FET per gate), 2–3 pull-downs, REG0 NPN, CPEN = 0, CP1 tied to BAT | Contactors open in ms; they are not a short-circuit interrupter, so a main fuse is still needed. SCD detection and DDSG are fast; contact opening is not |
| **B. High-side N-FET bank** (TI native; FET build variant) | CHG / DSG + charge pump; PCHG / PDSG PFETs for pre-charge and pre-discharge; LD 10 kΩ to PACK+ | Back-to-back banks of N parallel 100 V FETs per direction, each with its own ≈ 51 Ω gate resistor (oscillation), PNP local turn-off for large banks, gate Zeners, reverse-charge clamp (AN09 p.4–8), TVS across the banks. **CP1 2.2 µF**: with 12 FETs × 9.25 nF Ciss, V2 = 11 V × 2.2 / (2.2 + 0.111) = **10.5 V** (calc, AN09 Eq. 1 p.7); 470 nF would give 8.9 V. Conduction example: 6 FETs per direction at an assumed 3 mΩ hot R_DS(on): (200 / 6)² × 3 mΩ = **3.3 W per FET, ≈ 40 W for both banks** (calc) → heatsink. Charge pump keeps CP1 = BAT + 11 V ≤ 85 V, so **BAT ≤ ≈ 74 V while the pump runs** (DS p.8, p.10 note 1); OK for 16S LFP 58.4 V and 16S NMC 67.2 V, but surge clamping must hold below that | Removes 3 contactors, R_PRE1, the +12 V coil supply problem (P4) and coil drivers; µs-level SCD turn-off (DSG off 2–20 µs at 20 nF, slower with a bank; gate R trades speed against inductive spike, DS p.72–74). Communications stay ground-referenced (FAQ p.11 §4.6) |
| **C. Low-side N-FET bank** (common-port style) | DDSG / DCHG → gate driver IC (e.g. UCC27524, AN84 p.16) | Driver + regulator, charge-FET turn-off clamp; LD control circuit for load-removal recovery (AN84 p.27) | PACK− floats when the FETs are off, so **communications must be isolated** (FAQ p.11). This board already isolates CAN / RS-485, but the INA240 / MCU ground references move. More circuit than B for the same result |

**My view:** do **A** in this revision; it fixes blocker A9 with a few parts. Offer **B** as a separate "FET edition" layout, because the BQ76952 is designed for it and it removes the contactor and coil-supply problems. **C** is not recommended.

---

## 3. Hardware gate-kill (feature 3, detail)

* **Signals into the kill.** These must allow the coil drivers to be on:
  * `AFE_DDSG_OK` (DDSG, polarity "high = no fault")
  * `AFE_DCHG_OK`
  * `OCP_LATCH_OK` (the TLV3501 latch, review C2)
  * the MCU command
* **Fail-safe default.** Use pull-downs on all of them, so that while the AFE is unconfigured or in SHUTDOWN (DDSG/DCHG Hi-Z, TRM p.61), or REG1 is off, the coils cannot be energised.
* **Startup consequence.** With the TI default [FET_EN] = 0 the AFE reports the FETs as off, so the contactors stay blocked until FW (or OTP) sets FET_EN (TRM p.33, p.197). This is safe, but production needs OTP (9d) for MCU-independent behaviour.
* **Fast-path rule.**
  * Recommended mapping: **DSG FET Protections A = 0x80** (SCD only, fast) and **CHG FET Protections A = 0x18** (COV + OCC, fast) (TRM p.34).
  * Put temperatures and HWD in Protections B / C. They are 1 s firmware checks anyway (TRM p.62).
  * Leave CUV to the MCU (alarm), because a CUV hard-kill on a shared contactor would block the recharge that clears it (inferred system issue).
  * That DDSG follows the same fast path as the DSG driver is inferred from AN84 p.3. **Verify on the bench.**
* **One OR point for host kills.** Drive DFETOFF as BOTHOFF from the MCU and from the OCP latch, so both also pass through the AFE logic (DS p.48). Keep the latch's direct input to the AND as well.

---

## 4. On-board shunt: sizing for the AFE coulomb counter

Constraints:
* Measuring range ±200 mV (DS p.9, p.15).
* SRN may swing to −I·R during charge, because SRP = VSS here. Its recommended range is −0.2 V while measuring, abs-max −0.3 V (DS p.7, p.9).
* TI design example: ≤ 1 mΩ for 200 A (DS p.37).
* Tempco ≤ 50 ppm/°C (DS p.76).
* Comparator steps: OCC / OCD 2 mV, SCD 10–500 mV (DS p.22).

| R_shunt | V at 200 A / 500 A | P at 200 A / 500 A | OCD / OCC step | SCD range | CC offset (1 LSB = 7.6 µV) | CC2 one-sample resolution (14 bit over ±200 mV ≈ 24 µV) |
|---|---|---|---|---|---|---|
| **100 µΩ** | 20 / 50 mV | **4 W** / 25 W | 20 A | 100–5000 A | 76 mA | ≈ 0.24 A |
| 200 µΩ | 40 / 100 mV | 8 W / 50 W | 10 A | 50–2500 A | 38 mA | ≈ 0.12 A |
| 250 µΩ | 50 / 125 mV | 10 W / 62.5 W | 8 A | 40–2000 A | 30 mA | ≈ 0.10 A |
| 400 µΩ (max for 500 A in range) | 80 / 200 mV | 16 W / 100 W | 5 A | 25–1250 A | 19 mA | ≈ 0.06 A |

All values in the table are calc.

* **Recommendation: 100 µΩ** (4 W continuous; the project already holds a `R_Shunt_CSS2H-5930` footprint; that part's power rating and available values were **not checked**).
  * Use OCD3 (firmware, CC1-based) for the accurate continuous-overcurrent tier.
  * Use OCD1/OCD2/SCD for the fast tiers. Comparator accuracy is ±4 mV at 20–56 mV (DS p.22), which is ±40 A at 100 µΩ: fine for fast tiers, too coarse for the precise one.
  * If heat allows, 200 µΩ halves those errors.
* **Mandatory configuration:**
  * USER_AMPS = 100 mA (TRM p.20). 10 mA units cap at ±327 A, which is below the 500 A peak.
  * CC Gain = 74.77 (TRM p.127), then calibrate (AN32 p.5–6).
  * Thresholds given in userA (OCD3, SOCD, current thresholds) must be rescaled.
* **Filter:** 100 Ω in each line + 100 nF differential (+ optional 100 pF, + optional 100 nF to VSS), placed at the AFE and symmetric (DS p.65, p.76). Keep it separate from the INA240's 10 Ω / 100 nF network.
* **INA240: complement, not needed for metering.**
  * The AFE gives metering, SoC, SCD and OCC/OCD on its own, so the INA240 is not needed for those.
  * Keep the INA240 (A1 gain 20; review C5) plus a window comparator **only** as an independent, bidirectional µs channel into the OCP latch. The AFE's SCD is discharge-only, and OCC is ≥ 10 ms.
  * This dual-channel current protection is the sellable reason to keep it. If cost wins, delete U_ISENSE1 / U_OCP1 and their parts.

---

## 5. Pin-by-pin target for U_AFE1 (TQFP-48)

Today = netlist `baseline\before.net` (via `review\comp_pins.txt`). Target = "contactor build" (topology A); FET-build differences are in brackets.

| Pin | Name | Today | Target | Change |
|---|---|---|---|---|
| 1–15 | VC15…VC1 | VC15…VC1 via R_VC (100 Ω) + C_DF | same | none (balancing agent: gate Zener/R per AN81 p.4) |
| 16 | VC0 | VC0 via R_VC0 to `CELL_0` | same **plus** an on-board R/C path to VSS so VC0 never floats (DS p.75) | add link (review A10) |
| 17 | VSS | GND_PWR | GND_PWR, star at shunt B− Kelvin | layout |
| 18 | SRP | `SH_P` direct | 100 Ω to shunt B− Kelvin sense; 100 nF SRP–SRN at the pins | add 2 R + 1–3 C; on-board shunt |
| 19 | NC | open | open or VSS | none |
| 20 | SRN | `SH_N` direct | 100 Ω to shunt P− Kelvin sense | as pin 18 |
| 21 | TS1 | NTC_TS1, 10 nF | NTC pack 1, **≤ 3.3 nF** | cap value |
| 22 | TS2 | NTC_TS2 | **Wake input** (push-button / remote-ON to VSS), otherwise float; enables SHUTDOWN ship mode (DS p.53, p.75) | move NTC2 to pin 28 |
| 23 | TS3 | NTC_TS3, 10 nF | NTC pack 3, ≤ 3.3 nF | cap value |
| 24 | REG18 | 2.2 µF | same | none |
| 25 | ALERT | `AFE_ALERT` → PB10, no pull-up | same + **10 kΩ to +3V3**; config alarm, open-drain, active-low | add R; FW |
| 26 | SCL | `AFE_SCL` → **PB6** | `AFE_SCL` → **PA15** (I2C1_SCL); 4.7 kΩ to +3V3 | MCU pin move |
| 27 | SDA | `AFE_SDA` → PB7 **and PB9** | → PB7 only | remove PB9 |
| 28 | HDQ | open | NTC pack 2 (18 k, cell) + ESD + ≤ 3.3 nF | new net |
| 29 | CFETOFF | open | NTC pack 4 (or [FET build] a FET-temperature NTC for OTF) | new net (from DCHG) |
| 30 | DFETOFF | open | **BOTHOFF** input from MCU GPIO (PB5) OR-ed with the OCP latch; pull-down | new net |
| 31 | DCHG | NTC_TS4 | **DCHG output** (REG1 drive) → gate-kill | function change |
| 32 | DDSG | NTC_TS_PCB (RT_BOARD) | **DDSG output** (REG1 drive) → gate-kill. Board temperature from the internal die sensor (DS p.38), or RT_BOARD moves to TS2 if ship mode is dropped ([SHUT_TS2], TRM p.136) | function change |
| 33 | RST_SHUT | PB11 + 10 kΩ to VSS | same (MCU can reset the AFE interface, or hold it high 1 s for SHUTDOWN, DS p.48) | none |
| 34 | REG2 | open | optional 3.3 V, 1 µF, for the gate-kill logic and ALERT / I2C pull-ups as an AFE-powered "safety island"; else open | optional |
| 35 | REG1 | 2.2 µF, dead (no REGIN) | 3.3 V (on by default in -02), drives DDSG / DCHG high level | works once REGIN is fed |
| 36 | REGIN | **VSS** | NPN emitter, 22 nF to VSS (15–27 nF, DS p.13) | change |
| 37 | BREG | **floating** | NPN base, 10 MΩ to VSS (DS p.69); NPN collector via diode from the stack (DS p.64) | change (fixes A5) |
| 38 | FUSE | open | footprint: series R + 100 kΩ pull-down + NFET to chemical-fuse heater or shunt-trip coil (DNP until the owner decides) | add DNP footprint |
| 39 | PDSG | open | open [FET build: PDSG PFET + R + 1 MΩ G–S] | none |
| 40 | PCHG | open | open [FET build: PCHG PFET + R + 1 MΩ] | none |
| 41 | LD | VSS | VSS, or a remote-ON wake circuit (DS p.65) [FET build: 10 kΩ to PACK+] | optional |
| 42 | PACK | **VSS** | 10 kΩ (+ small clamp) to `V_INVERTER_BUS` for bus voltage (0–80 V ±0.5 V, DS p.10) [FET build: PACK+] | change |
| 43 | DSG | open | open [FET build: DSG bank] | none |
| 44 | NC | open | open | none |
| 45 | CHG | open | open [FET build: CHG bank] | none |
| 46 | CP1 | 100 nF to BAT | **tie to BAT**, remove C_CP1, [CPEN] = 0 (DS p.75) [FET build: 2.2 µF to BAT] | change |
| 47 | BAT | `V_BAT_FILT` (D_BAT1 + 1 µF) | same + series R for the RC filter (DS p.75 §17); keep the diode separate from the NPN diode (DS p.64) | add R |
| 48 | VC16 | VC16 via 100 Ω | consider 20 Ω (FAQ p.17; balancing agent) | optional |

### MCU sheet changes that follow

* **Pin moves (I2C option, recommended):**
  * PB6 → free; `AFE_SCL` moves to PA15.
  * PB9 → free.
  * New: PB5 → `AFE_BOTHOFF`; PB3 / PB4 → read back `AFE_DDSG_OK` / `AFE_DCHG_OK` for diagnostics.
  * These alternates come from the KiCad 10 symbol `STM32G431C_6-8-B_Tx`; DS12589 is still not opened.
* **SPI option, for reference:**
  * SPI3 on PB3 (SCK), PB4 (MISO), PB5 (MOSI) and PA15 (NSS). All four pins are free today and carry SPI3 alternates in the same symbol.
  * AFE pins 29 / 28 become CS / MOSI.
  * The MISO high level is 1.8 V unless REG1 is powered and [MISO_REG1] is set, then the comm mode is swapped (DS p.57; AN11 p.13).
  * The -02 part would need SWAP_TO_SPI at every boot or OTP. Alternatively order BQ7695204 (SPI + CRC + REG1 3.3 V, FAQ p.3).

---

## 6. Notes behind the less obvious choices

* **REGIN from REG0 (NPN), not from +5V.**
  * REGIN has a diode to BAT and must never exceed BAT (DS p.46; abs-max VBAT + 0.3 V, DS p.7).
  * With the J2 bench input powering +12 V / +5 V while no pack is on BAT, a +5V-fed REGIN would violate that.
  * REG0 also keeps REG1 alive if the buck chain fails.
* **REG1 will not power the MCU.** 45 mA maximum (DS p.13), and the NPN would dissipate (58.4 − 5.5) V × 45 mA ≈ 2.4 W (calc). The bucks stay.
* **OTP needs 10–12 V, not "≈10 V on LD".** The requirement is on **BAT** (DS p.9: min 10, max 12 V; layout extract confirms the columns) and also on **VC16** (FAQ p.12), at ≤ 45 °C, with **no cells connected**. LD plays no part.
  * Because of the 12 V maximum, OTP can **not** be written with a 16S pack attached.
  * PF-to-OTP writes in the field may be "delayed in low-voltage and high-temperature conditions" (DS p.43). My inference is that they are also impossible above 12 V. **Check with TI** before relying on [PF_OTP] in a 48 V pack.
* **I2C CRC and timeouts are exclusive** (TRM p.73 Table 9-1). Pick CRC (0x12). Keep the 2 s SCL-low bus reset, which is always active (TRM p.74).

## 7. I2C vs SPI vs HDQ: recommendation

| Criterion | I2C + CRC (-02 default) | SPI + CRC | HDQ |
|---|---|---|---|
| Speed | 400 kHz, block reads (FAQ p.11) | 2 MHz, but 1 data byte per 24-bit transaction + ≥ 50 µs gap (DS p.24, p.57) | ~190 µs per bit (DS p.24) |
| 16-cell read, calc | (4 + 32 × 2) bytes × 9 bit / 400 kHz ≈ **1.5 ms** | 32 × (12 µs + 50 µs) ≈ **2.0 ms** | ≫ 50 ms |
| Integrity | CRC-8 per byte, NACK on error | CRC-8, error flags 0xFFFFAA / 0xFFFF00 / 0xFFFFFF, retry scheme needed (DS p.62) | none |
| AFE pins used | 2 | 4 (loses CFETOFF and HDQ, i.e. 2 NTC / control pins) | 1 |
| Extra needs | pull-ups only | REG1 must be on for 3.3 V MISO; OTP or SWAP_TO_SPI on every boot | – |
| Isolation (if added later) | needs a bidirectional I2C isolator | easy with unidirectional isolators | easy |

**Recommendation: I2C Fast with CRC on PA15 / PB7.**
* SPI does not help this board. It is not faster for the AFE's data pattern, it costs two of the multifunction pins that §5 needs for NTCs and BOTHOFF, and it adds a REG1 dependency.
* Re-open the choice only if the owner adds an AFE-to-MCU digital isolator (review S1). Then order BQ7695204 and use SPI3.

---

## 8. Top-10 recommended changes (highest priority first)

1. **Give the AFE a hardware path to the contactors** (fixes blocker A9; requirements R15, R16).
   * DDSG / DCHG become REG1-driven "OK" outputs into an AND gate-kill with the MCU command and the OCP latch; pull-downs make the default "kill".
   * Set DSG FET Prot A = 0x80 and CHG FET Prot A = 0x18 for the fast path; temperatures and HWD go through Prot B / C.
   * Map host kills through DFETOFF = BOTHOFF.
   * Sources: TRM p.34, p.56–62; AN84 p.3; DS p.48–49.
2. **Program a golden LFP image into OTP at end of line.**
   * The TI defaults are not safe on their own: COV 4.35 V, only SCD + COV enabled, SCD 10 mV, FET Test mode, 1 mA current units.
   * Fixture: 10–12 V on BAT and VC16 with cells not attached, ≤ 45 °C; the MCU writes the image in a factory mode.
   * Sources: DS p.9; TRM p.14–15, p.197–203; AN32 p.14; FAQ p.12.
3. **Keep I2C + CRC; fix the MCU pins.** SCL from PB6 to PA15, remove the PB9 SDA, add a 10 kΩ pull-up on ALERT and configure it as the alarm output. Do not move to SPI (§7).
4. **On-board 100 µΩ, ≤ 50 ppm/°C shunt with its own Kelvin pair and 100 Ω / 100 nF filter at SRP / SRN.**
   * Set USER_AMPS = 100 mA and CC Gain = 74.77, then calibrate board offset and CC gain.
   * Use the AFE CC as the primary meter, with OCD3 / OCD1 / OCD2 / SCD tiers.
   * The INA240 stays only as an independent bidirectional fast-trip channel, or is deleted.
   * Sources: DS p.15–16, p.22, p.37, p.65, p.76; TRM p.20, p.127; AN32 p.5–6.
5. **Power the LDOs properly.**
   * Add the REG0 NPN pre-regulator: BREG, collector diode, 22 nF on REGIN, 10 MΩ on BREG. This gives REG1 = 3.3 V.
   * Tie CP1 to BAT and clear CPEN in the contactor build.
   * This fixes review A5. Sources: DS p.13, p.46, p.64, p.69, p.75.
6. **Re-map the multifunction pins.**
   * 4 pack NTCs on TS1, TS3, HDQ and CFETOFF; DCHG / DDSG become outputs; TS2 freed for a wake button and SHUTDOWN ship mode; board temperature from the die sensor.
   * NTC filter caps from 10 nF to ≤ 3.3 nF.
   * Sources: DS p.38, p.53, p.65; TRM p.56–58, p.136.
7. **Connect PACK to the bus (10 kΩ) instead of VSS.** This gives bus voltage for pre-charge-done and weld checks, correct OCC recovery and charger detect. Keep LD on VSS, or use it for remote-ON wake. Sources: DS p.10, p.12, p.65; TRM p.40, p.66.
8. **Enable the host watchdog, PF set, diagnostics and open-wire detection.**
   * HWD gives a second, independent MCU watchdog acting through DDSG / DCHG.
   * Enable SOV / SUV / SOT / VIMR / TOS PF.
   * Add a DNP FUSE-pin footprint to drive a chemical fuse or a breaker shunt-trip, with optional external OV-protector OR-ing.
   * Check field PF-to-OTP behaviour above 12 V with TI.
   * Sources: TRM p.45–51, p.61; DS p.43, p.49–50.
9. **Plan a "FET edition" variant on CHG / DSG / PCHG / PDSG.**
   * Back-to-back 100 V banks with per-FET gate resistors, PNP turn-off and CP1 = 2.2 µF.
   * Keep BAT ≤ ≈ 74 V while the charge pump runs.
   * This removes the contactors, R_PRE1 and the coil-supply problem.
   * Sources: DS p.10, p.20, p.44–45, p.72–74; AN09 p.4–8, p.27.
10. **Use the "free" data features and lock the part.**
    * Synchronized per-cell V / I for impedance and SoH.
    * Interconnect-resistance compensation.
    * Host-controlled balancing with CBSTATUS logging (AFE side; details from the balancing agent).
    * SLEEP with current wake (24–41 µA).
    * Change the TI default unseal and full-access keys, SEAL at power-up, check STATIC_CFG_SIG at boot.
    * Sources: DS p.10–11, p.38; TRM p.18–21, p.71–72, p.85–87.

---

## 9. Not verified / open

* **Default REG0_EN on the -02 variant.** It is not in any opened document (inferred "on" from FAQ p.11). It is irrelevant if REG0 is wired and configured as recommended.
* **DDSG / DCHG response time** after a comparator fault. TI text implies they follow the FET decision (AN84 p.3), but no timing number was found. Bench-measure it.
* **Whether a PF-to-OTP write can happen at 16S stack voltage** (OTP needs BAT ≤ 12 V). Ask TI.
* **FUSE application figure values** (5.1 kΩ / 100 kΩ). They were read from a garbled figure extract (DS p.50 Fig 12-1).
* **STM32G431 alternate functions** (PA15 I2C1_SCL / SPI3_NSS; PB3 / PB4 / PB5 SPI3; PB7 I2C1_SDA). These are from the KiCad 10 symbol only, not from ST DS12589.
* **Parts not checked in any document:**
  * shunt part (CSS2H-5930 values and power rating)
  * NPN for REG0
  * gate-kill logic IC
  * FET-bank MOSFETs (the 3 mΩ hot R_DS(on) and 9.25 nF Ciss figures are AN09's CSD19536KCS figure or my assumption)
  * chemical fuse / shunt-trip part
* **CC Gain range discrepancy.** AN32 p.6 lists 0.1–10, while the TRM p.127 / p.198 lists 0.01–1000. The TRM value was used; 74.77 for 100 µΩ needs the TRM range.
* **BQ7697202** (±3 mV, same comm and LDO defaults, FAQ p.3). Pin compatibility and AEC status were not checked.
* **Competitor feature sets** (Daly / JBD / JK). Not researched; no competitor claim is made here.
* **SLUAAN9** (stacked high-side) was downloaded but not read beyond its title.
