# Research 06 — BQ76952 48-Pin Audit and I2C vs SPI Link Trade-Off (2026-11-25)

**Sources verified directly:**
* TI BQ76952 Datasheet (`ZHCSM58B`, rev. Nov 2021): Pin Configuration & Functions (p.4–6 Table 6-1), Absolute Maximum Ratings (p.7–8), Electrical Characteristics (p.10–12), Serial Interfaces & CRC-8 (p.55–58), Application Circuit (p.65–77).
* TI BQ76952 Technical Reference Manual (`SLUUBY2B`): `Settings:Configuration:Comm Type` / `SPI Configuration`, Pin Configuration Registers (TS1/TS2/TS3/HDQ/CFETOFF/DFETOFF/ALERT/DCHG/DDSG, TRM p.56–57), `SLEEP` / `DEEPSLEEP` / `SHUTDOWN` (TRM p.77).
* ST STM32G473RCT6 Datasheet (`DS12712` Rev 2): LQFP64 Pin Definitions Table 12 (p.53–68) & Alternate Functions Table 13 (p.69–77).
* Project design baselines: Sheet 02 netlist / [`sheet02_afe_cell_monitor.md`](../design/sheet02_afe_cell_monitor.md), Sheet 03 [`sheet03_mcu_control.md`](../design/sheet03_mcu_control.md), Sheet 08 [`sheet08_io_front_panel.md`](../design/sheet08_io_front_panel.md), Sheet 10 [`sheet10_memory_sensors.md`](../design/sheet10_memory_sensors.md), and [`ARCHITECTURE.md`](../ARCHITECTURE.md) §8.

---

## 1. Complete 48-Pin Audit (`U201` BQ76952PFBR)

**Verdict:** **All 48 pins match TI datasheet intent.** Zero miswired pins; 2 minor layout/derating notes (`CFETOFF` ESD on `NTC_FET` across B2B pin 15; `CP1` at 2.2 µF datasheet max).

Reach legend: **LOC** = Sheet 02 only · **MCU** = direct STM32G473 pin · **EXP** = TCA9539 read-back (Sheet 08) · **B2B** = J206 ↔ J701 to Power Board.

| Pin | DS Name | Our Net(s) & External Network | Reach | Matches DS Intent? & Reference |
|---|---|---|---|---|
| 1 | `VC15` | `02_VC15` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 15 sense & bal. return (DS p.4, p.71, p.76) |
| 2 | `VC14` | `02_VC14` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 14 sense & bal. (DS p.4, p.71, p.76) |
| 3 | `VC13` | `02_VC13` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 13 sense & bal. (DS p.4, p.71, p.76) |
| 4 | `VC12` | `02_VC12` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 12 sense & bal. (DS p.5, p.71, p.76) |
| 5 | `VC11` | `02_VC11` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 11 sense & bal. (DS p.5, p.71, p.76) |
| 6 | `VC10` | `02_VC10` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 10 sense & bal. (DS p.5, p.71, p.76) |
| 7 | `VC9` | `02_VC9` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 9 sense & bal. (DS p.5, p.71, p.76) |
| 8 | `VC8` | `02_VC8` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 8 sense & bal. (DS p.5, p.71, p.76) |
| 9 | `VC7` | `02_VC7` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 7 sense & bal. (DS p.5, p.71, p.76) |
| 10 | `VC6` | `02_VC6` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 6 sense & bal. (DS p.5, p.71, p.76) |
| 11 | `VC5` | `02_VC5` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 5 sense & bal. (DS p.5, p.71, p.76) |
| 12 | `VC4` | `02_VC4` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 4 sense & bal. (DS p.5, p.71, p.76) |
| 13 | `VC3` | `02_VC3` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 3 sense & bal. (DS p.5, p.71, p.76) |
| 14 | `VC2` | `02_VC2` (100 Ω + 220 nF + SS8050 bal. tap) | LOC | **OK** — cell 2 sense & bal. (DS p.5, p.71, p.76) |
| 15 | `VC1` | `02_VC1` (100 Ω + 220 nF C201 directly to `VSS`) | LOC | **OK** — `C201` VC1→`VSS` per TI FAQ for stack stability (DS p.5, p.76) |
| 16 | `VC0` | `02_VC0` (`R201` + `NT201` star tie to `VSS` / `GND_PWR`) | LOC | **OK** — bottom cell reference, Kelvin-referenced to `GND_PWR` (DS p.5, p.71) |
| 17 | `VSS` | `GND_PWR` (star ground island) | LOC | **OK** — analog/ground reference (DS p.5, p.76) |
| 18 | `SRP` | `02_SRP` (100 Ω + 100 nF ∥ 100 pF from `SHUNT_K_BAT` via J206-11) | B2B | **OK** — differential current sense + (DS p.66, p.77) |
| 19 | `NC` | Unconnected | – | **OK** — no connect per DS p.5 |
| 20 | `SRN` | `02_SRN` (100 Ω + 100 nF ∥ 100 pF from `SHUNT_K_PACK` via J206-12) | B2B | **OK** — differential current sense − (DS p.66, p.77) |
| 21 | `TS1` | `02_TS1` (Pack `NTC1`, 100 Ω + 1 nF + ESD) | LOC | **OK** — `C < 4 nF` limit met (DS p.66) |
| 22 | `TS2` | `AFE_TS2_WAKE` (1 kΩ → `BAV170` → `WAKE_BTN_RAW`) | Indirect (Btn) | **OK** — must stay unloaded by NTC when `SHUTDOWN` push-button wake is used (`TS2 Config = 0x00`, DS p.76) |
| 23 | `TS3` | `02_TS3` (Pack `NTC3`, 100 Ω + 1 nF + ESD) | LOC | **OK** — `C < 4 nF` limit met (DS p.66) |
| 24 | `REG18` | `02_REG18` (4.7 µF MLCC, `TP203`) | LOC | **OK** — 1.8 V internal LDO bypass within 1.8–22 µF range (DS p.13) |
| 25 | `ALERT` | `AFE_ALERT` (10 kΩ PU to `AFE_REG1` → `PB9` + `Q102` wake) | MCU | **OK** — symbol pin still shows `HDQ_IO/ALERT` (cosmetic P5C-08); configured as active-low `ALERT` (TRM p.56) |
| 26 | `SCL` | `02_SCL_PIN` (100 Ω → `PA15` `I2C1_SCL`, 4.7 kΩ PU to `02_I2C_PU`) | MCU | **OK** — note: add optional DNP zeners (DS p.77) if desired |
| 27 | `SDA` | `02_SDA_PIN` (100 Ω → `PB7` `I2C1_SDA`, 4.7 kΩ PU to `02_I2C_PU`) | MCU | **OK** — same as pin 26 |
| 28 | `HDQ` | `02_HDQ` (Pack `NTC2` in thermistor ADC mode, 100 Ω + 1 nF) | LOC | **OK** — thermistor config valid per TRM p.56–57; sacrificed if SPI is chosen |
| 29 | `CFETOFF` | `02_CFETOFF` (`NTC_FET` via J206-15, 100 Ω + 1 nF) | B2B | **OK (minor)** — HV-adjacent analog input (`VMAX = VREG18 + 0.3 V` in ADC mode, DS p.7 note 3); verify ESD protection on `NTC_FET` at B2B J206-15 in layout; sacrificed if SPI is chosen |
| 30 | `DFETOFF` | `AFE_DFETOFF` (`BOTHOFF` from hardware kill AND `U701`, 100 kΩ PD, `U801` P07 RB) | B2B + EXP | **OK** — fail-safe active-low `BOTHOFF` input |
| 31 | `DCHG` | `AFE_FLT_CHG_N` → kill AND `U701` (`U801` P05 RB) | B2B + EXP | **OK** — charge protection fault output (3.3 V on `AFE_REG1`) |
| 32 | `DDSG` | `AFE_FLT_DSG_N` → kill AND `U701` (`U801` P04 RB) | B2B + EXP | **OK** — discharge protection fault output (3.3 V on `AFE_REG1`) |
| 33 | `RST_SHUT` | `AFE_RST_SHUT` (10 kΩ PD → MCU `PB5`) | MCU | **OK** — `< 1 s` pulse = partial reset; `> 1 s` pulse = `SHUTDOWN` (DS p.6) |
| 34 | `REG2` | `02_REG2` (disabled; `C221` DNP) | LOC | **OK** — leave disabled (fit `C221` if ever enabled in OTP) |
| 35 | `REG1` | `AFE_REG1` (2.2 µF; always-on 3.3 V island, max 1.8 mA used / 5 mA budget) | LOC | **OK** — supplies `DDSG`/`DCHG` high logic, I2C PU, `ALERT`, `WAKE_BTN_N`, `VBAT_MCU` OR |
| 36 | `REGIN` | `02_REGIN` (`FCX495` `REG0` emitter, 22 nF, fed from `BAT_SNS`) | LOC | **OK** — DS p.13, p.65, p.70 |
| 37 | `BREG` | `02_BREG` (`FCX495` base, 10 MΩ to `VSS`) | LOC | **OK** — external NPN pre-regulator drive (DS p.6, p.70) |
| 38 | `FUSE` | `AFE_FUSE` (100 kΩ PD; `Q202` driver DNP, open D-16) | LOC | **OK** — `< 2 mA` limit noted (DS p.7 note 2) |
| 39 | `PDSG` | `AFE_PDSG` → J206-6 → `Q723` P-FET gate | B2B | **OK** — high-side pre-discharge P-FET control (DS p.6) |
| 40 | `PCHG` | `AFE_PCHG` → J206-5 → `Q724` P-FET gate | B2B | **OK** — high-side pre-charge P-FET control (DS p.6) |
| 41 | `LD` | `AFE_LD` → J206-7 → 10 kΩ (`R751`) to `PACK+`, `BAS21` clamp to `VSS` | B2B | **OK** — charger / load-detect (0–80 V ROC, delays `SHUTDOWN` while high, DS p.53) |
| 42 | `PACK` | `AFE_PACK` → J206-2 → 10 kΩ (`R752`) to `PACK+`, `BAS21` clamp to `VSS` | B2B | **OK** — pack top sense (DS p.6) |
| 43 | `DSG` | `AFE_DSG` → J206-4 & J206-8 (2× B2B contacts) → DSG FET bank | B2B | **OK** — high-side N-FET charge-pump gate drive (DS p.6) |
| 44 | `NC` | Unconnected | – | **OK** — not connected to silicon (DS p.6) |
| 45 | `CHG` | `AFE_CHG` → J206-3 → CHG FET bank | B2B | **OK** — high-side N-FET charge-pump gate drive (DS p.6) |
| 46 | `CP1` | `02_CP1` (2.2 µF 50 V X7R to `BAT`) | LOC | **OK (minor)** — at TI's 2.2 µF max (`100 / 470 / 2200 nF`, DS p.21); charge-pump start-up ≈ 0.28 s (`calc`) |
| 47 | `BAT` | `02_BAT` (`1N4148WS` + `100 Ω` from `BAT_SNS` + `CELL16` backup diode, 1 µF 250 V) | LOC | **OK** — primary HV supply pin, 85 V abs max (DS p.7) |
| 48 | `VC16` | `02_VC16` (20 Ω `R217` + 220 nF + SS8050 bal. tap) | LOC | **OK** — top cell sense (DS p.6, p.71, p.76) |

Notice that **all 9 multifunction/thermistor-capable pins** (`TS1`, `TS2`, `TS3`, `HDQ`, `CFETOFF`, `DFETOFF`, `ALERT`, `DCHG`, `DDSG`) are actively assigned in v1.2, while pack/board thermistors `NTC4–NTC6`, `NTC_BAL`, and `NTC_AMB` already sit on the MCU `TMUX1308` mux (Sheet 10).

---

## 2. I2C vs SPI Comparison & Recommendation

**Recommendation: KEEP I2C Fast (400 kHz) + CRC-8 (`Settings:Configuration:Comm Type = 0x12`).**

| Criterion | Current I2C + CRC (`0x12`) | Alternative SPI + CRC (`0x10`) | Winner |
|---|---|---|---|
| **AFE Pin Cost** | 2 pins (`SCL` 26, `SDA` 27) | 4 pins: `HDQ` (28) becomes `SPI_MOSI` and **`CFETOFF` (29) becomes `SPI_CS`** (DS p.5–6) → **loses `NTC2` and hardware `NTC_FET` monitoring inside AFE!** Either FET OT protection becomes firmware-only (`Option S-a`) or pack loses `NTC2` redundancy (`Option S-b`) | **I2C** |
| **STM32G473 LQFP64 Allocation** | All 52 GPIOs already mapped (`sheet03`); uses hardware `I2C1` (`PA15`/`PB7`) cleanly | `SPI1` used by FRAM/Flash; `SPI4` not bonded on LQFP64; `SPI2` pins busy (`PB12–15` used by `CAN_LINK`/`NTC_MUX`/`BUZZER`). **Only `SPI3` (`AF6`) fits** (`PB3`=SCK, `PB4`=MISO, `PB5`=MOSI, `PA15`=CS) → **drops `SWO` debug trace**, bumps `KILL_N` (`PB4`→`PB7`), moves `AFE_RST_SHUT` (`PB5`) off-MCU onto `U802 P15` (adds I2C latency before hardware shutdown!) | **I2C** |
| **Throughput (16 cells + V/I/T)** | `≈ 1.6 ms` (`calc`, continuous block read @ 400 kHz) | `≈ 2.0 ms` (`calc`): BQ76952 SPI transfers one register/subcommand byte per transaction with `≥ 50 µs` inter-byte idle requirement (DS p.58) | **I2C** |
| **Data Integrity** | Identical CRC-8 polynomial `x⁸ + x² + x + 1` supported in both modes (DS p.55–58) | Same CRC-8, **except an all-zero MISO line has valid CRC (`0x00`)** if disconnected — requires external pull-up on MISO | **Tie / I2C** |
| **Sleep / Silicon Traps** | Open-drain idle; no CS float issue. Watch for rare clock-stretch / stuck-low SDA (handle via 9-clock recovery + `RST_SHUT` reset) | 1.8 V MISO default unless `SPI Configuration[MISO_REG1] = 1` (TRM `SLUUBY2B`); **floating `SPI_CS` during MCU off/Sleep causes continuous HFO wakes adding `≈ 30 µA`** (TRM p.77) — needs external PU to `AFE_REG1`; SPI OTP stock (`BQ7695201/04`) is scarce vs standard `BQ76952PFBR` (`0x12` programmable at EOL/runtime via `SWAP_COMM_MODE`) | **I2C** |
| **Noise Immunity** | Short local PCB trace on unified `GND_PWR` (adequate with 100 Ω series + CRC + retry) | Push-pull edges resist CM transients — only decisive across an isolation barrier or off-board cable | **Tie locally** |

### Low-Cost I2C Hardening Actions (Recommended Regardless of Board Rev)
1. Optionally add **DNP 5.6 V zener / ESD footprints** on `02_SCL_PIN` / `02_SDA_PIN` (DS p.77) during PCB layout.
2. Firmware: enforce **CRC-8 always enabled**, **9-clock SCL bus-clear routine** on timeout, **retry counter**, and treat persistent `SCL` low as an unrecoverable AFE fault (`FET_EN = 0`).

---

## 3. Exact Hardware & OTP Change List (Only If Owner Overrules and Selects SPI)

1. **Sheet 02 (`02_AFE_Cell_Monitor`):**
   - Repurpose `R267` (`02_HDQ`) → `SPI3_MOSI` (33 Ω), `R269` (`02_CFETOFF`) → `SPI3_CS` (33 Ω); remove `C228`, `C230` (1 nF therm. filter caps) and unlink `NTC2` / `NTC_FET` from AFE.
   - Remove or DNP `R257`/`R258`/`D227` (`I2C1` pull-up island); add **10 kΩ PD** on `SPI_SCLK` (optional idle state), **10 kΩ PU to `AFE_REG1`** on `SPI_CS` (prevents 30 µA SLEEP wake when MCU is off), and **10 kΩ PU to `+3V3`** on `SPI_MISO` (blocks all-zero valid-CRC false frames).
   - OTP / Runtime Config: program `Settings:Configuration:Comm Type = 0x10` (SPI+CRC) and `SPI Configuration = 0x60` (`MISO_REG1 = 1` for 3.3 V MISO) using `SWAP_TO_SPI()` + `RESET()`.
2. **Sheet 03 (`03_MCU_Control`):** Map `PB3`=`SPI3_SCK`, `PB4`=`SPI3_MISO`, `PB5`=`SPI3_MOSI`, `PA15`=`AFE_CS_N`; drop `SWO` from `J301` (`NC`); move `KILL_N` to `PB7`; move `AFE_RST_SHUT` off `PB5`.
3. **Sheet 08 (`08_IO_Front_Panel`):** Assign `U802 P15` spare to drive `AFE_RST_SHUT` (adds expander latency).
4. **Sheet 10 (`10_Memory_Sensors`):** Connect `NTC2` and `NTC_FET` to unused `TMUX1308` channels `S5` / `S6` with 2 × 10 kΩ bias + 2 × 100 nF filter caps (`+3V3_A` NTC bias reaches `1.49 mA`, still within budget; note `NTC_FET` becomes MCU-only protection).
5. **Docs:** Update `ARCHITECTURE.md` §7/§8/§10 and `SCHEMATIC_V1.md` §1.1/§6.
