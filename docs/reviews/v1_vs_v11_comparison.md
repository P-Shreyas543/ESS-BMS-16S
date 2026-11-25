# Independent Hardware Review: v1 (`0f11683`) vs v1.1 (`ca3a7a3`)

- **Repository:** `Automotive-ESS-BMS` (git branch `public`)
- **Revisions compared:** `v1 = 0f11683` vs `v1.1 = ca3a7a3` (HEAD)
- **Verification date:** 2026-11-25 (live LCSC/JLCPCB API queries, `kicad-cli` 10.0.7 netlist & ERC exports, primary datasheets)
- **Methodology:** Adversarial read-only audit; `git archive` comparison of `0f11683` (`v1`) vs `ca3a7a3` (`v1.1`), independent netlist export & diff across both KiCad projects (`Automotive_ESS_BMS.kicad_sch` and `power_board/power_board.kicad_sch`), ERC on all four board states, independent Bode/loss/thermal/latch math from downloaded datasheets, and live LCSC/JLCPCB API stock/price verification.

---

## 0. Scope & Netlist Verification

Confirmed via `kicad-cli sch export netlist` + `netcmp` across both projects:
- **Power board (`power_board/power_board.kicad_sch`, sheets 04 & 07):** `connectivity identical: True`. Only a text note in Box 5 of `power_board/07_Power_Stage.kicad_sch` changed (`B2B unplugged` warning per P5-03).
- **Control board (`Automotive_ESS_BMS.kicad_sch`, sheets 01, 02, 03, 05, 06, 08, 09, 10):** Every netlist difference between `v1` and `v1.1` is strictly confined to **sheet 01 (`1xx` references)**. Sheets 02, 03, 05, 06, 08, 09, and 10 are **100% electrically identical**.
- **ERC (`kicad-cli sch erc --severity-all`):** Both `v1` and `v1.1` produce **0 errors, 2 documented warnings** on the control board (`U1002` pins 3/7 `WP`/`HOLD` tied to `+3V3`, `pin_to_pin`), and **0 errors, 0 warnings** on the power board.

---

## 1. Detailed Aspect-by-Aspect Comparison (v1 vs v1.1)

### 1.1 Switching Noise & EMC
- **Fundamental frequency & CISPR 25 bands (LW 150–300 kHz, MW 0.53–1.8 MHz):**
  - **v1 (`LM5013-Q1`):** CCM frequency `FSW = 5.03 V × 2500 / 39 kΩ = 322 kHz` (`lm5013-q1.pdf` p.12 Eq.4, `calc`), just above CISPR 25 LW (`300 kHz`). **However**, critical conduction boundary at `51.2 V` (`L = 22 µH`) is `I_crit = ΔIL / 2 = 0.5 × 5.03×(1−5.03/51.2)/(22 µH × 322 kHz) = 0.320 A` (`calc`). Both Standby (`~85–130 mA` on `+5V`) and typical load (`0.164 A`) sit in **DCM / pulse-skipping**, where switching frequency scales down (`~85–165 kHz`, `est.`), sweeping directly across the **LW (150–300 kHz)** band and shifting harmonics across **MW (0.53–1.8 MHz)**.
  - **v1.1 (`LM5146-Q1`):** Fixed `FSW = 10^4 / 49.9 kΩ = 200.4 kHz` (`±5%` → `190–210 kHz`, `lm5146-q1.pdf` p.9, p.20 Eq.3) in **forced PWM (FPWM)** across all loads (`SYNCIN` pulled to `VCC` via `R132`). While load-invariant, **`200 kHz` places the fundamental switching tone directly inside CISPR 25 LW (150–300 kHz)** and harmonics 3–9 (`600 kHz – 1.8 MHz`) inside **MW**, with **no spread spectrum** (`SYNCIN` is static DC, not modulated). Note that TI's CISPR 25 Class 5 compliance plot (`lm5146-q1.pdf` p.45 Fig 9-31) uses `400 kHz` (above LW) plus a π input filter (`p.34–35`).
- **`+5V_ISO` switching & spread spectrum:**
  - **v1 (`B0505S-2WR3`):** Unregulated free-running Royer oscillator at `200–340 kHz` (`b0505s-2wr3.pdf` p.3), no spread spectrum, `C_iso = 20 pF` (`p.3`).
  - **v1.1 (`SN6505BDBVR` + `LT31-113`):** Push-pull at `424 kHz` typ (`363–517 kHz`, `sn6505b.pdf` p.5) — fundamental sits cleanly in the gap **between LW (300 kHz) and MW (530 kHz)** — with internal **Spread Spectrum Clocking (SSC)** (`p.1, p.20`), slew-rate control (`152 V/µs`, `41 A/µs`, `p.5`), `0%` typ duty mismatch (`p.5`), and lower transformer coupling capacitance (`~12.5 pF`, `LT31-113` spec, `~38%` lower CM injection than `B0505S`).
- **Hot loop, dv/dt, snubber & switch-node ringing:**
  - **v1:** Integrated HS MOSFET inside `LM5013-Q1` (`SO-PowerPAD-8`) + single `200 V` `SS520` (`D104`); compact internal HS-to-SW loop and no LS reverse-recovery (`Qrr ≈ 0` Schottky).
  - **v1.1:** External `Q103` (`SQ2398ES`) + `Q104 // Q105` (`DMN10H220LQ-7`) + `R138` (`1206` shunt) in the LS source return enlarges the high-`di/dt` switching loop (`C137 → Q103 → Q104/Q105 → R138 → C137`), adds LS `Qrr = 2 × 9.8 nC = 19.6 nC` (`dmn10h220lq.pdf` p.2), and requires `R133 = 4.7 Ω` + fitted RC snubber (`R135 10 Ω + C138 100 pF`) to tame switch-node overshoot.
- **Ripple on `+5V`, `+3V3`, `+3V3_A` & impact on `INA240` / `VREF+`:**
  - `+5V` CCM ripple (`ΔV = ΔIL / (8·FSW·COUT)`): v1 = `0.65 A / (8 × 322 kHz × 37.4 µF) = 6.7 mV pp` (`calc`); v1.1 = `0.335 A / (8 × 200.4 kHz × 51 µF eff) = 4.1 mV pp` (`calc`, `5.6 mV pp` on `C108/C109` alone). In DCM below `0.32 A`, v1 exhibits `~10–25 mV pp` low-frequency burst ripple from its `~40 mV pp` Type-3 FB ripple (`lm5013-q1.pdf` p.20). Downstream `U103` (`TPS7B8233-Q1`) + `FB101` + `C120` attenuate `200–322 kHz` content strongly (`~35–45 dB` LDO PSRR), but `FB101` provides almost zero impedance below `1 MHz`, making v1.1's constant-frequency `200 kHz` cleaner for `+3V3_A` (`INA240A1`, `VREF+`) at typical/standby loads (`164 mA`) than v1's low-frequency DCM bursts.

### 1.2 Efficiency & Power (Pack Drain on 100–280 Ah)
Independent datasheet loss calculations (`lm5013-q1.pdf` p.5/12/15, `lm5146-q1.pdf` p.8–9/30 Table 9-1, `sq2398es.pdf` p.2, `dmn10h220lq.pdf` p.2, `smdri127.pdf` p.9, `b0505s-2wr3.pdf` p.1–3, `sn6505b.pdf` p.5, `mbr0520lt1g.pdf` p.2):

| Operating Point (`+5V` Buck Only) | v1 (`LM5013-Q1` COT/DCM, `VOUT=5.03 V`) `calc` | v1.1 (`LM5146-Q1` FPWM, `VOUT=5.08 V`) `calc` |
|---|---|---|
| **Idle (`0 A`)** @ `40 / 51.2 / 58.4 V` | `~3 mW` (`IQ-SLEEP = 10–20 µA`, p.5) | `0.300 / 0.387 / 0.445 W` (`IQ 1.8 mA + Igate 3.1 mA + Qoss/snb`) |
| **Typical (`0.164 A`, `0.83 W`)** @ `40 / 51.2 / 58.4 V` | `0.132 / 0.167 / 0.192 W` (**86.2 / 83.2 / 81.2%**) | `0.374 / 0.414 / 0.475 W` (**69.0 / 66.8 / 63.7%**) |
| **Peak (`0.962 A` v1 / `1.00 A` v1.1)** @ `40 / 51.2 / 58.4 V` | `0.591 / 0.665 / 0.718 W` (**89.1 / 87.9 / 87.1%**) | `0.928 / 1.069 / 1.164 W` (**84.6 / 82.6 / 81.4%**) |

- **Why v1.1 buck is less efficient:** In FPWM at `200 kHz`, `LM5146-Q1` pulls `~4.9–5.6 mA` continuously from `VIN` through its internal 7.5 V linear regulator (`~0.25–0.33 W` at `51.2–58.4 V`), plus `R138` 100 mΩ shunt loss (`92 mW` at 1 A), `Qrr` (`~150–230 mW`), `R135/C138` snubber (`52–68 mW`), and `68 µH` `L101` (`0.14 Ω` DCR vs `0.043 Ω` on `22 µH`).
- **`+5V_ISO` idle/standby loss (`20 mA` bus load, `EN_ISO` ON):**
  - **v1 (`B0505S-2WR3` + `150 Ω` dummy `R122 || R128`):** `20 mA` bus + `33.3 mA` dummy = `53.3 mA` out (`0.267 W`). At `~50–65%` light-load efficiency (`0.2 W` no-load loss, `b0505s-2wr3.pdf` p.2), input draw from `+5V` is `~95–109 mA` (`~0.50–0.55 W`).
  - **v1.1 (`SN6505B` + `LT31-113` + `2×MBR0520L` + `TLV76750`):** `20 mA` bus + `~1.6 mA` `SN6505B` `ICC` + `~10–15 mA` magnetizing/diode/LDO overhead ≈ `32–38 mA` from `+5V` (`~0.16–0.19 W`, **saves `~70 mA` on `+5V` ≈ `9 mA` at `51.2 V`**). Note: at `85 °C` ambient, `MBR0520LT1G` reverse leakage rises up to `8 mA` max at `20 V / 100 °C` (`mbr0520lt1g.pdf` p.2), eroding `~20–50 mW` (`est.`) of hot idle savings.
- **Monthly pack drain (`720 h/month`, `51.2 V` nominal, `calc`/`est.`):**
  - **Sleep (output off):** v1 `~54 µA` (`0.039 Ah/mo` = `0.04%` of 100 Ah / `0.014%` of 280 Ah) vs v1.1 `~64 µA` typ (`0.046 Ah/mo` = `0.05%` / `0.016%`). **Negligible delta (+0.007 Ah/mo)** — *unless* `PWR_EN` hangs above `VSHDN-FALL`, trapping `U101` in `1.75–2.0 mA` Standby (`1.30 Ah/mo` = `1.30%` / `0.47%`).
  - **Standby (`EN_ISO` ON):** v1 (with fitted `150 Ω` dummy) `~13.5 mA` (`9.72 Ah/mo` = `9.7%` of 100 Ah / `3.5%` of 280 Ah) vs v1.1 `~10.5 mA` (`7.56 Ah/mo` = `7.6%` / `2.7%`). v1.1 wins by `~3 mA` (`~2.16 Ah/mo`) **only while `EN_ISO` is ON**; if firmware turns `EN_ISO` OFF in a deeper Standby, v1.1 draws `~8.1 mA` (`5.83 Ah/mo`) vs v1's `~2.1 mA` (`1.51 Ah/mo`).
  - **Run (`~164 mA` `+5V` typ):** v1.1 uses `+0.25 W` extra (`+4.8 mA` at `51.2 V`) in the buck, offset by `-0.35 W` saved on `+5V_ISO` when comms are active (`net ~ -2 mA` at `51.2 V`).

### 1.3 Cost (Live JLCPCB Prices, Verified 2026-11-25)
- **Sheet 01 fitted BOM count:** `v1 = 90` (`47` unique LCSCs) vs `v1.1 = 114` (`66` unique LCSCs) → **+24 parts (+26.7%)**; control board total unique fitted LCSCs `140 → 155` (**+15**).
- **Per-board BOM delta (`v1.1 − v1`, exact live JLC component pricing across all changed sheet-01 rows):**
  - **At 100 pcs:** **`+$4.93 / board`** (`+$4.31` buck delta: `LM5146Q $6.55` + FETs `$0.74` + shunt `$0.08` + passives − `LM5013Q $3.50` − `SS520 $0.08`; `+$0.62` iso delta: `SN6505B $0.38` + `LT31-113 $0.61` + `TLV76750 $0.35` + `2×MBR0520L $0.10` + caps − `B0505S $0.82`). Note: using `Würth 760390014` (`$2.16`) adds another `+$1.55` (`+$6.48` total @ 100).
  - **At 1,000 pcs:** **`+$4.76 / board`** (`+$4.38` buck, `+$0.38` iso).
- **JLCPCB Extended-part setup fees (`$3` per unique Extended LCSC per assembly batch):** Control board adds **17 Extended LCSCs** and removes **4 Extended LCSCs** (`+13` net) → **`+$39` per batch** (`+$0.39/board` @ 100 pcs, `+$0.04/board` @ 1,000 pcs).
- **PCB area & assembly:** Buck footprint grows `~+25 mm²` (`est.`), iso shrinks `~-41 mm²` (`est.`, net `~-16 mm²`), **AND** v1.1 eliminates the **THT SIP-4** module (`B0505S-2WR3`), converting `+5V_ISO` to 100% single-sided SMD reflow (saving manual/wave THT soldering cost on U106, though `J101` & test hooks remain THT). Schematic sheet 01 grew from A3 to A2.

### 1.4 Reliability & Robustness
- **Thermal (`85 °C` ambient, `58.4 V`, `1.00 A`):**
  - **v1 (`LM5013-Q1`):** `RθJA = 34.8 °C/W` (`29.0 °C/W` EVM, `lm5013-q1.pdf` p.5). Total IC loss `~0.28 W` (`P_cond 0.032 W + P_sw 0.22 W + IQ 0.026 W`) → `ΔT ≈ 10 °C` → **`Tj ≈ 95 °C`** (`150 °C` max); `SS520` (`0.36 W`) `Tj ≈ 105 °C` (`175 °C` max).
  - **v1.1 (`LM5146-Q1` + external FETs + `TLV76750`):**
    - `U101 LM5146-Q1`: `0.29 W` VCC LDO loss × `36.8 °C/W` (`lm5146-q1.pdf` p.7) → **`Tj ≈ 96 °C`** (`150 °C` max).
    - `Q103 SQ2398ES`: `~0.32–0.35 W` (includes `0.15 W` from `2/3 × Qrr`) × `130 °C/W` (`sq2398es.pdf` p.1, 1" sq FR4) → **`Tj ≈ 127–131 °C`** (up to `~145 °C` on tight SOT-23 copper, vs `175 °C` max).
    - `Q104 // Q105 DMN10H220LQ-7`: `~0.125 W` each × `177 °C/W` min pad (`dmn10h220lq.pdf` p.2) → **`Tj ≈ 107 °C`** (`150 °C` max).
    - `U107 TLV76750DRVR`: at `300 mA` hot/high (`01_ISO_RECT ≈ 6.1–6.2 V` loaded, `V_out = 5.0 V`, `P = 0.33–0.36 W`) × `77.7 °C/W` (`tlv767.pdf` p.6) → **`Tj ≈ 111–113 °C`** (`125 °C` ROC / `150 °C` abs max).
- **Current-limit accuracy over temperature:**
  - **v1 (`LM5013-Q1`):** Peak limit `3.7 – 5.0 A` (`4.2 A` typ, `lm5013-q1.pdf` p.5), generous margin for `0.96 A` load and `7.0 A` `L101` `Isat` (`smdri127.pdf` p.9), though loose (`±15%`) and foldback-based.
  - **v1.1 (`LM5146-Q1` `RSENSE` mode):** `R138 = 0.100 Ω ±1%`, `R131 = 1.50 kΩ ±1%`, `IRS = 90–110 µA` (`0 ppm/°C`), `VILIM-TH = −8 to +3.5 mV` (`lm5146-q1.pdf` p.9, p.23). Valley limit = **`1.29 A min / 1.52 A typ / 1.76 A max`** (`calc`, output limit `~1.46–1.93 A`), `≥ +55%` above `0.83 A` operating valley at `1.00 A`, and max peak `2.20 A < 4.0 A` `Isat` (`smdri127.pdf` p.9). **Temperature-independent** (huge fix over the draft `RDS(on)` mode).
- **TVS clamp (`79–91 V`) & switch-node overshoot vs `100 V` abs max:**
  - `VSUP` clamp via `R_DAMP = 4.4 Ω` (`R101 + R102`): `SMCJ60A` (`D103`) clamps at `~79 V` (`25 °C`), `~84–87 V` hot, `~91 V` at `96.8 V` `VC` corner (`calc`/`est.`).
  - **v1:** `LM5013-Q1` `VIN/SW` abs max `100 V` (`lm5013-q1.pdf` p.4), `SS520` `200 V` (`ss520.pdf` p.1); internal switch minimizes loop `L·di/dt` ringing.
  - **v1.1:** `LM5146-Q1` `VIN/SW` (`100 V`, `lm5146-q1.pdf` p.6), `Q103` (`100 V`), and `Q104/Q105` (`100 V`) all share `9–21 V` headroom to `100 V`. External FET loop + shunt inductance increases ringing risk; mitigated by `R133 4.7 Ω` and fitted snubber `R135/C138`, still requires **gate B4** verification at `80 V` bench `VSUP`.
- **Start-up / shutdown & power-latch robustness (`PWR_EN`):**
  - **v1 (`LM5013-Q1`):** `V_EN-RISING = 1.43–1.60 V`, `V_EN-FALLING = 1.35–1.47 V`, `V_SD-FALLING = 0.45 V` typ (`lm5013-q1.pdf` p.5), `IQ-STBY = 25 µA typ / 40 µA max`. `C111 = 1 µF` charges in `τ = 1 ms` (even a `3 ms` `AFE_ALERT` pulse holds `~0.40–0.53 s`), and `R109 = 1 MΩ` gives `0.66 s` hold with no EN hysteresis current fighting it.
  - **v1.1 (`LM5146-Q1`):** `EN/UVLO` sources **`9–11 µA` above `1.2 V`** (`lm5146-q1.pdf` p.8, p.19), forcing `R109` down from `1 MΩ` to `56 kΩ` and `C111` up to `10 µF` (`X7R 25 V 1206`, `τ_charge = 9.8 ms`). Consequence:
    1. A **`10 ms` `AFE_ALERT` pulse** (still wrongly documented on `R125/R126` in the schematic/BOM!) only charges `PWR_EN` to `~1.43 V` at `-40 °C`, holding `~136 ms` (`< 300 ms` `TPS3828` reset delay `t_d max`!) — requires **latched `AFE_ALERT` or `≥ 30 ms` pulse** (`V11-04`).
    2. **`VSHDN-FALL = 0.37 V` is typical only** (no min/max, `lm5146-q1.pdf` p.8/25); if `PWR_EN` stays above `VSHDN-FALL` (floor `0.21 V` from `ES2D` hot leakage), `U101` stalls in `1.75–2.0 mA` Standby (`30×` Sleep drain).
    3. `AUX`-only UVLO drops to `~7.1 V` on / `~4.4 V` off (v1: `~9.0 V` / `~8.4 V`).
- **Back-feed:**
  - **v1 (`LM5013-Q1`):** Non-synchronous (`SS520` blocks reverse current). Back-feeding `+5V` on bench does not boost into `VSUP`.
  - **v1.1 (`LM5146-Q1`):** In FPWM, `Q104/Q105` conduct negative inductor current (`lm5146-q1.pdf` p.5, p.26). Back-powering `+5V` above `5.08 V` while `U101` is enabled **boosts energy backward into `VSUP`** (blocked from returning to `BAT+` by `D101`, pumping `VSUP` until `D103 SMCJ60A` clamps & overheats!). Requires strict bench prohibition (`B11`).
- **FMEA (key single-point failure modes):**
  - `Q103` short D-S (v1.1) or `U101` HS short (v1): puts `58.4 V` onto `+5V` (`C108/C109` 25 V, all 5.5 V loads destroyed unless `F701` / `R101/R102` open — both versions lack a `+5V` OVP crowbar, though v1.1 `PGOOD` flags OV `> 5.40 V` at MCU).
  - `R138` open (v1.1): `Q104/Q105` sources float → `01_U101_RS` rises to `SW`, stops LS conduction; buck runs in body-diode mode, `D` drops, `ILIM` sees high voltage → thermal/fault shutdown.
  - `R132` (`SYNCIN` pull-up) open (v1.1): internal `20 kΩ` pull-down drops `SYNCIN` to `0 V` → safely switches to **DCM** (fail-safe).
  - `D110` or `D111` short (v1.1): shorts half of `T101` secondary on alternate half-cycles → `SN6505B` hits `1.75 A` cycle-by-cycle `ILIM` (`sn6505b.pdf` p.5) and thermal shutdown (`168 °C`, p.5); `+5V` stays up via `U105` or `U106` TSD.
  - `U107` (`TLV76750`) short IN-OUT (v1.1): puts `01_ISO_RECT` (`≤ 6.92 V` no-load) onto `+5V_ISO` → exceeds `6.0 V` abs max of `CA-IS3050CW` / `CA-IS3082WX`. (Same overvoltage hazard exists in v1 whenever `B0505S` runs unloaded, though via single failure in v1.1 vs normal light-load operation in v1).

### 1.5 Isolation & Safety
- **Creepage & clearance vs `6.5 mm` project rule (`PROJECT.md` §5 D-10):**
  - **v1 (`B0505S-2WR3`):** `2.54 mm` SIP grid, pin 2 (`GND_PWR`) to pin 4 (`GND_ISO`) = `5.08 mm` center-to-center minus `1.5 mm` pad = **`3.58 mm` copper-to-copper** (`b0505s-2wr3.pdf` p.5, `Converter_DCDC_Murata_NMAxxxxSC_THT`). **FAILS `6.5 mm` rule**; THT pins prevent a slot from restoring `6.5 mm` surface creepage across the body.
  - **v1.1 (`LT31-113` / `WE 760390014`):** Row pitch `9.14 mm`, pad `1.12 mm` → **`8.02 mm` copper-to-copper gap** (`Transformer_WE-PPTI_760390014.kicad_mod`), **MEETS `6.5 mm` rule**. **HOWEVER**, the `T101_barrier_keepout` rule area claimed in `V11-14` is **missing from the committed `.kicad_mod` file** (lines 1–227)!
- **Hipot & insulation class:**
  - **v1:** `1500 VDC / 1 min` (`~1060 Vrms`, `b0505s-2wr3.pdf` p.1/3) — **FAILS `≥ 2.5 kVrms` rule**.
  - **v1.1:** `2.5 kVAC / 60 s` (`LT31-113` spec, `WE 760390014` `2500 VAC` / `400 Vrms` working voltage, **functional insulation only, not reinforced**). Meets the `≥ 2.5 kVrms` functional target, though transceivers (`CA-IS3050CW` / `CA-IS3082WX`) are rated `5 kVrms / 8 mm` (`SCHEMATIC_V1.md` §8).
- **Output voltage window vs transceiver abs max (`6.0 V` max / `5.5 V` rec max):**
  - **v1:** Unregulated `B0505S-2WR3` (`12%` load reg, `40 mA` min load, `b0505s-2wr3.pdf` p.1/3/4) can exceed `5.5 V` below `40 mA`; dummy load `R122 || R128` (`33.3 mA`) leaves it still dependent on transceiver idle draw.
  - **v1.1:** `TLV76750` LDO regulates `+5V_ISO` to **`4.94 – 5.05 V` (`±1%` over temperature, `tlv767.pdf` p.6)** from `0 – 300 mA` with **zero minimum load**. (In the cold/low `300 mA` corner, `01_ISO_RECT ≈ 5.36–5.47 V` minus `VDO ≈ 0.25–0.35 V` at `0.3 A` from `tlv767.pdf` p.10 Fig 7-17 keeps output `≥ 4.94 V`).

### 1.6 Supply Chain (Live JLCPCB & LCSC Verification, 2026-11-25)

| Part | LCSC | Revision | JLC Type | JLC Stock | LCSC Stock | Price @100 / @1k | Temp / AEC-Q Status |
|---|---|---|---|---|---|---|---|
| `LM5013QDDARQ1` | `C5219285` | v1 | Extended | **213** | **213** | `$3.50 / $3.21` | `-40..150 °C`, AEC-Q100 |
| `B0505S-2WR3` | `C7465195` | v1 | Extended | 4,124 | 4,124 | `$0.82 / $0.76` | `-40..105 °C`, non-AEC |
| `SS520-SMC` | `C2891410` | v1 | Extended | 14,606 | 14,605 | `$0.08 / $0.06` | `-65..175 °C`, non-AEC |
| `LM5146QRGYRQ1` | `C1850329` | v1.1 | Extended | **9,124** | **8,853** | `$6.55 / $6.55` | `-40..150 °C`, AEC-Q100 |
| `SQ2398ES-T1_GE3` | `C727466` | v1.1 | Extended | 10,266 | 10,266 | `$0.27 / $0.23` | `-55..175 °C`, AEC-Q101 |
| `DMN10H220LQ-7` | `C5260572` | v1.1 | Extended | 3,646 | 3,645 | `$0.24 / $0.18` | `-55..150 °C`, AEC-Q101 |
| `HoLRTX1206-1W-100mR` | `C5123673` | v1.1 | Extended | 20,224 | 20,220 | `$0.08 / $0.07` | `-55..155 °C`, non-AEC |
| `SN6505BDBVR` | `C74518` | v1.1 | Extended | 1,541 | 1,423 | `$0.38 / $0.32` | `-55..125 °C`, non-AEC |
| `LT31-113` | `C7471252` | v1.1 | Extended | **771** | **0 (none)** | `$0.61 / $0.50` | **No DS temp**, non-AEC |
| `760390014` (alt) | `C2802211` | v1.1 alt | Extended | **0** | **0 (none)** | `$2.16 / $2.03` | `-40..125 °C`, AEC-Q200 |
| `MBR0520LT1G` | `C23848` | v1.1 | Extended | 260,687 | 260,680 | `$0.05 / $0.04` | `-65..125 °C`, AEC-Q101 |
| `TLV76750DRVR` | `C2872569` | v1.1 | Extended | 4,647 | 4,647 | `$0.35 / $0.31` | `-40..125 °C`, non-AEC |
| *Alt: `LM5013DDAR`* | `C5383001` | *neither* | Extended | **6,930** | **6,930** | `$0.97 / $0.89` | `-40..125 °C`, non-AEC |
| *Alt: `SN6505BQDBVRQ1`* | `C1849490` | *neither* | Extended | **3,000** | **3,000** | `$0.99 / $0.88` | `-40..125 °C`, AEC-Q100 |

- **Key supply findings:** v1's `LM5013QDDARQ1` dropped further from `250` to **`213 pcs`** (unusable for volume without switching to commercial `LM5013DDAR` at `6,930 pcs`). Meanwhile v1.1's `LT31-113` is **JLC-only (`771 pcs`) with no published temperature range** and its alternate `760390014` is **0 stock**. Also note `SN6505BQDBVRQ1` (`C1849490`, 3,000 stock) costs only **`+$0.61`** over `SN6505BDBVR` (not `+$2.18` as reported in `sheet01_power_supply.md` §10.3).

### 1.7 Design Risk & Complexity
- **Part & net proliferation:** Sheet 01 grew by `+24` fitted parts (`90 → 114`), `+15` unique LCSCs on the control board (`140 → 155`), and `40` new local nets; `B0505S` had 1 IC + 2 dummy resistors, whereas `+5V_ISO` now has 4 active/magnetic ICs + 6 passives.
- **Loop stability (independently recomputed via `lm5146-q1.pdf` p.32 Table 9-3):**
  - Note: actual board `+5V` capacitance includes `C108/C109` (`37.4 µF` eff) **plus** downstream `C117, C118, C121, C125` (`~13.6 µF` eff → **`51 µF`** with `EN_ISO=0`, **`59 µF`** with `C127` on).
  - Independent Bode calculation confirms stability across all corners:
    - Doc nominal (`37.4 µF, 68 µH`): `fc = 20.18 kHz, PM = 60.9°, GM = 21.9 dB`
    - Actual board (`51 µF, 68 µH, 0.2 A`): `fc = 15.31 kHz, PM = 60.9°, GM = 25.2 dB`
    - Actual board (`59 µF, 68 µH, 1.0 A`): `fc = 13.49 kHz, PM = 62.8°, GM = 27.1 dB`
    - Worst low (`26 µF, 54.4 µH, 1.0 A`): `fc = 33.50 kHz, PM = 51.7°, GM = 16.2 dB`
    - Worst high (`65 µF, 81.6 µH, 50 mA`): `fc = 10.59 kHz, PM = 58.4°, GM = 28.7 dB`
- **Layout sensitivity, bring-up & firmware rules:**
  - v1.1 adds **11 new bring-up gates (`B1–B11`)** including 80 V SW overshoot tuning, `< 1 cm²` input hot-loop, Kelvin routing on `R138`/`PGND`, symmetric `Q104/Q105` gate/source layout, `-40 °C` qualification of `LT31-113`, and `SQ2398ES` `VDS(on)` check at `9 V` AUX.
  - Firmware rules added: `PWR_HOLD` must be **first GPIO action** after reset (`300 ms` `TPS3828` reset delay eats into `0.49–0.68 s` hold), `AFE_ALERT` must be **latched or `≥ 30 ms`** (contradicting stale `10 ms` text on `R125/R126`), `1.3 s` shutdown wait, `≥ 25 ms` `EN_ISO` wait, and **strict prohibition on back-feeding `+5V`**.

### 1.8 Power Stage (Sheet 07) & Other Sheets (02–10)
All sheets other than 01 are **electrically identical** between `v1` and `v1.1`. Brief independent audit of the unchanged design:
- **Gate drive & kill chain (Sheet 07 / 02):** `Q723/Q724` (`IRF9640S`, `-200 V`) sources correctly tied to `FET_MID`; `D229–D231` (`BAS21`) clamp `AFE_DSG/LD/PACK` to `GND_PWR`; `U701–U703` (`74LVC1G11/1G04`) + `R756/R757` `10 kΩ` B2B isolation resistors + `Q729` static-floor PNP (`R755 100 kΩ`) cleanly drive both banks off (`AO3407A` + `BSS131` 240 V). **Unresolved risk (`P5-01`):** `R759 = 0 Ω` fitted causes `AFE_FLT_CHG_N` (`DCHG`) to kill **both** banks on `UTC (0 °C)` / `OTC (45 °C)`, starving the `PACK+`-fed heater (`F702 / Q726`) so the pack cannot self-heat below 0 °C.
- **Clamps & 100 V FET margin (Sheet 07):** `4 × 5.0SMDJ60CA` (`BAT+`) and `4 × 5.0SMDJ60A` + `MBRB20200CT` (`PACK+`) have `VC = 96.8 V @ 51.7 A` (`207 A` total). Margin to `100 V` `IPT015N10N5` is `15%` in nominal `800 A` controlled turn-off (`78–85 V`), **`3.2%` at rated clamp `VC`**, and **`0%` / negative** in an SCD-only double fault or reversed parallel pack (`~117 V`, pending mandatory `D-04` short-circuit bench test).
- **Shunt Kelvin & OC latch (Sheet 04):** `2 × HolRS3920` (`100 µΩ` total) cleanly separated from `200 A` `BAT-` copper via single star tie `NT401` at the Kelvin edge; `TLV803S` (`U404`) + `R415` on `+3V3_A` + `R420/C411` (`OC_CLR` glitch filter) work properly. **Watch item (`R1-11`):** `TLV1702AIDGKR` `VOL` is uncharacterized at `3.3 V / 0.33 mA` vs `SN74AUP1G74` `VIL = 0.9 V` (bring-up gate 12).
- **Fail-safes & AFE/MCU/Comms (Sheets 02, 03, 05, 06, 08, 09, 10):** B2B unplugged leaves power-board `+3V3` and BQ drivers disconnected (`10 MΩ` passive bleed, `τ ≈ 1.0–1.4 s` if separated live — documented in v1.1 sheet 07 note); `CELL_0` return (`R274 10 Ω` + `NT201`) forces firmware CC compensation for `B−` lug/cable drop (`~20–40 mV @ 200 A`); `TCA9539` (`U801/U802`) reset on `MCU_NRST` guarantees safe outputs on MCU reset.

### 1.9 Alternatives Neither Version Took (Live-Verified 2026-11-25)
1. **Hybrid: Commercial `LM5013DDAR` (`C5383001`, 6,930 pcs, `$0.97 @100`) or `LM5013-Q1` + `SN6505B` (`C1849490` `-Q1`, 3,000 pcs, `$0.99`) + `LT31-113`/`760390014` + `TLV76750`:**
   - **Why better than both v1 and v1.1:** Fixes v1's fatal `B0505S` creepage/isolation/regulation defects **AND** avoids v1.1's `+$4.31` buck cost, `+17` parts, `200 kHz` LW-band EMI, `1.75 mA` `EN/UVLO` standby trap, and back-feed hazard. `LM5013DDAR` (`C5383001`) is rated `-40..+125 °C` (`LM5013` non-Q, consistent with owner's non-Q picks for `STM32G473`, `INA240A1PWR`, `TLV1702`, `TLV76750`), has **32× the stock** of `-Q1`, saves **`$5.58`** over `LM5146Q` + FETs + shunt, and cuts Standby pack current to **`~4.5 mA`** (`3.24 Ah/mo` vs `7.56 Ah/mo` in v1.1 and `9.72 Ah/mo` in v1)!
   - *Trade-off:* Non-Q silicon and DCM switching below `0.32 A` (`85–165 kHz`).
2. **If FPWM is mandatory on `LM5146-Q1`: move `FSW` to `400 kHz` (`R104 = 24.9 kΩ`) and swap `Q103` to `DMN10H220LQ-7` (`C5260572`):**
   - Moves the fundamental **out of CISPR 25 LW (`150–300 kHz`)** (matching TI's CISPR 25 Class 5 reference design on `lm5146-q1.pdf` p.45; `tON` at `96.8 V` is `131 ns > 60 ns` `tON(min)`), allows a smaller `33–47 µH` inductor (`SMDRI127-330MT`/`470MT`), and eliminates the uncharacterized `6.7 V` `RDS(on)` risk and unique Extended BOM line of `SQ2398ES`.
3. **`SCT2A23ASTER` (`C2901894`, 100 V 2 A monolithic synchronous buck, `2,271` pcs, `$1.84 @100`):**
   - Monolithic `100 V / 2 A` synchronous buck (no external FETs/shunt), much cheaper/simpler than `LM5146-Q1`, though non-AEC (`-40..125 °C`) and datasheet not opened in this review (unverified `IQ` / FPWM / `tON(min)`).

---

## 2. Summary Comparison Table

| Aspect | v1 (`0f11683`) | v1.1 (`ca3a7a3`) | Winner | Evidence |
|---|---|---|---|---|
| **1. Switching noise & EMC** | `LM5013` CCM `322 kHz` sweeps DCM (`85–165 kHz`) at typ/standby; `B0505S` `200–340 kHz` no SSC, `20 pF` `C_iso`; compact internal HS switch + `200 V` `SS520` | `LM5146` FPWM fixed `200.4 kHz` **inside CISPR 25 LW (150–300 kHz)**, no SSC, larger external FET+shunt loop; `SN6505B` `424 kHz` **with SSC**, `~12.5 pF` `C_iso`, cleaner `+5V` (`4.1 mV pp`) | **Split** (v1.1 iso wins; buck mixed) | `lm5013-q1.pdf` p.12/20; `lm5146-q1.pdf` p.20/45; `sn6505b.pdf` p.5/20; `b0505s-2wr3.pdf` p.3 |
| **2. Efficiency & power** | Buck `η = 83%` typ / `88%` peak (`51.2 V`), `3 mW` idle; `B0505S + 150 Ω` dummy wastes `~109 mA` → Standby `~13.5 mA` (`9.7 Ah/mo`), Sleep `~54 µA` | Buck `η = 67%` typ / `83%` peak (`51.2 V`), `0.39 W` idle; `SN6505B + LDO` saves `~9 mA` → Standby `~10.5 mA` (`7.6 Ah/mo`), Sleep `~64 µA` (`1.81 mA` if stuck) | **v1 buck / v1.1 iso** (`v1.1` net `-3 mA` only with `EN_ISO` ON) | `lm5013-q1.pdf` p.5; `lm5146-q1.pdf` p.8/30; `b0505s-2wr3.pdf` p.2; `calc` |
| **3. Cost (2026-11-25)** | 90 sheet-01 parts (47 unique), 140 ctrl LCSCs; **baseline**, THT `B0505S` | 114 sheet-01 parts (66 unique), 155 ctrl LCSCs; **`+$4.93` @100 / `+$4.76` @1k**, **`+$39`/batch** (+13 Ext fees), 100% SMD iso | **v1** (cost) / **v1.1** (SMD asm) | Live JLCPCB API 2026-11-25; `bom_schematic_v1.csv` |
| **4. Reliability & robustness** | `B0505S` overvoltages `> 5.5 V` at light load; `LM5013` `3.1 µA` shutdn, `25 µA` stby, `3 ms` wake pulse OK, no back-feed, `SS520` `200 V` | `TLV76750` `4.94–5.05 V` reg; accurate `1.29–1.76 A` shunt `ILIM`; **typ-only `0.37 V` shutdn** (`1.75 mA` stby trap), `30 ms` wake rule, back-feed boost hazard | **v1** (latch/buck) / **v1.1** (`ILIM` & `+5V_ISO` reg) | `lm5013-q1.pdf` p.5; `lm5146-q1.pdf` p.8/23/25; `tlv767.pdf` p.6; `b0505s-2wr3.pdf` p.3-4 |
| **5. Isolation & safety** | **FAILS:** `3.58 mm` creepage (`< 6.5 mm`), `1500 VDC` hipot (`< 2.5 kVrms`), `> 5.5 V` unloaded output | **PASSES (with footprint fix):** `8.02 mm` gap (`> 6.5 mm`), `2.5 kVAC / 60 s` functional, `4.94–5.05 V` output (`≥ 8%` margin to `5.5 V`); **missing keepout zone in `.kicad_mod`** | **v1.1** (decisively) | `b0505s-2wr3.pdf` p.1/3/5; `Transformer_WE-PPTI_760390014.kicad_mod` |
| **6. Supply chain** | `LM5013Q` **213 pcs** (critical); `B0505S` 4,124 pcs | `LM5146Q` 9,124 pcs; **`LT31-113` 771 pcs JLC-only, NO temp rating**; `760390014` **0 stock**; non-AEC `SN6505B`/`TLV76750` | **Tie (both have 1 critical bottleneck)** | Live JLCPCB / LCSC APIs 2026-11-25 |
| **7. Design risk & complexity** | Simple integrated buck + module; 0 loop tuning; only `R2-01` & `R3-02` iso gates | `+24` parts, Type-III loop (sound `52–63°` PM), 11 new bring-up gates (`B1–B11`), strict layout & FW rules | **v1** (simplicity) | `v11_ctrl.net`; `SCHEMATIC_V1.md` §5-6 |
| **8. Sheets 02–10 & Power Stage** | Identical electrical netlist; stale sheet 07 B2B note | Identical electrical netlist; corrected sheet 07 B2B note; `P5-01` (`R759 0R`) & `100 V` `D-04` risks unchanged | **v1.1** (doc note only) | `netcmp` = identical; `v11_pwr.net` |

---

## 3. Adversarial Findings Table

| ID | Severity | Rev | Refs / Nets | Finding | Evidence | Concrete Fix |
|---|---|---|---|---|---|---|
| **F-01** | **BLOCKER** | v1 | `U106`, `GND_PWR`, `GND_ISO` | `B0505S-2WR3` THT footprint has **`3.58 mm`** pad gap (`5.08 mm` pitch − `1.5 mm` pad), violating the `6.5 mm` creepage rule, and **`1500 VDC / 1 min`** (`~1060 Vrms`) isolation, violating `≥ 2.5 kVrms` (`PROJECT.md` §5). | `b0505s-2wr3.pdf` p.1, p.3, p.5; `v1_ctrl.net` (`U106`) | Replace `B0505S-2WR3` with `SN6505B` + `8.02 mm` `2.5 kVAC` transformer + `TLV76750` (already done in v1.1). |
| **F-02** | **MAJOR** | v1 | `U106`, `+5V_ISO`, `R122`, `R128` | Unregulated `B0505S-2WR3` (`12%` load reg, `40 mA` min load) rises above `5.5 V` rec. max `VCC2` of `CA-IS3050CW`/`CA-IS3082WX` when transceivers idle; `150 Ω` dummy (`33.3 mA`) wastes `167 mW` yet still drops below `40 mA` at bus idle. | `b0505s-2wr3.pdf` p.1, p.3, p.4; `v1_ctrl.net` | Use `TLV76750` post-regulator (`4.94–5.05 V`, zero min load) per v1.1. |
| **F-03** | **MAJOR** | v1 | `U101` (`C5219285`) | `LM5013QDDARQ1` live JLC/LCSC stock is **`213 pcs`** (2026-11-25) — insufficient for even a 250-board lot. | JLCPCB & LCSC APIs 2026-11-25 | Switch to commercial `LM5013DDAR` (`C5383001`, `6,930 pcs`, `$0.97`) if retaining COT buck, or use `LM5146Q` (`9,124 pcs`). |
| **F-04** | **MAJOR** | v1.1 | `U101`, `R104`, `R132`, `01_U101_SW` | `200.4 kHz` FPWM fundamental sits **dead-center inside CISPR 25 LW (`150–300 kHz`)** and harmonics 3–9 inside MW (`0.53–1.8 MHz`), with no SSC (`SYNCIN` tied static high to `VCC`). TI's CISPR 25 Class 5 plot uses `400 kHz`. | `lm5146-q1.pdf` p.20 Eq.3, p.45 Fig 9-31; `v11_ctrl.net` (`R104`, `R132`) | Change `R104` to `24.9 kΩ` (`400 kHz`, `tON = 131 ns @ 96.8 V > 60 ns`) + `L101` to `33–47 µH` and re-comp, or inject MCU SSC clock on `R132`. |
| **F-05** | **MAJOR** | v1.1 | `U101`, `PWR_EN`, `R109`, `D102`, `R136` | `LM5146-Q1` shutdown threshold (`VSHDN-FALL = 0.37 V`) is **typical only (no min/max)**. Any unit skewing below `0.21 V` (`D102` hot leakage floor) stalls in `1.75–2.0 mA` Standby, increasing Sleep drain **30×** (`64 µA → 1.81 mA`). | `lm5146-q1.pdf` p.8, p.13 Fig 7-17, p.25; `v11_ctrl.net` | Add a cheap open-drain comparator or NPN/PFET clamp on `PWR_EN` (or move `D102` bleeder / use `LM5013` which has `25–40 µA` standby). Test worst-case hot units at `B1`. |
| **F-06** | **MAJOR** | v1.1 | `T101` (`C7471252`), `Transformer_WE-PPTI_760390014.kicad_mod` | `LT31-113` has **no stated temp range** (`P-13` needs `-40..+85 °C`), `771 pcs` JLC-only stock (`760390014` `0` stock); **AND** the committed `.kicad_mod` file **omits the `T101_barrier_keepout` `(zone ...)`** claimed fixed in `V11-14`. | `footprints.pretty/Transformer_WE-PPTI_760390014.kicad_mod` L1–227; JLCPCB API 2026-11-25 | Add the `(zone (keepout ...))` across `*.Cu` (`±4.0 × ±3.4 mm`) to `Transformer_WE-PPTI_760390014.kicad_mod` immediately; qualify `LT31-113` at `-40 °C` (`B8`) or pre-stock `760390014`. |
| **F-07** | **MAJOR** | Both | `R759`, `R760`, `U702`, `Q701–Q716`, `D713–D718` | Sheet 07 `R759 0 Ω` fitted causes `DCHG` (`UTC 0 °C`/`OTC 45 °C`) to kill **both** banks, starving the `PACK+`-fed heater; `100 V` FETs have `3.2%` margin at clamp `VC = 96.8 V` and `0%` in SCD double fault. | `v11_pwr.net` (`R759`, `U702`); `sheet07_power_stage.md` §13–14 | Remove `R759` / fit `R760 10 kΩ` if cold-discharge/self-heating is needed (`P5-01`); execute `D-04` bench short-circuit test before PCB release. |
| **F-08** | **MINOR** | v1.1 | `Q103` (`SQ2398ES`) | `RDS(on)` specified only at `10 V` (`VGS(th)` up to `3.5 V` at 25 °C / `~3.9 V` at `-40 °C`), driven at `6.4–6.9 V` (`~5.9 V` on `9 V` AUX). | `sq2398es.pdf` p.2, p.4; `lm5146-q1.pdf` p.8–9 | Replace `Q103` with `DMN10H220LQ-7` (`C5260572`, already used for `Q104/Q105`, `250 mΩ` guaranteed @ `4.5 V`, `-$0.03`, `-1` Extended fee). |
| **F-09** | **MINOR** | v1.1 | `R125`, `R126`, `C111`, `PWR_EN` | `R125`/`R126` BOM & schematic descriptions still state `wake pulse >= 10 ms`, which gives only `~136–320 ms` hold at `-40 °C` against `300 ms` `TPS3828` reset delay (contradicting `V11-04` `≥ 30 ms` / latched rule). | `docs/bom/bom_schematic_v1.csv` (`ca3a7a3`) vs `sheet01_power_supply.md` §12.4–12.5 | Update `R125`/`R126` descriptions to `>= 30 ms or latched`; enforce latched `AFE_ALERT` in BQ76952 OTP. |
| **F-10** | **MINOR** | v1.1 | `U106` (`SN6505BDBVR`) | Non-AEC `SN6505BDBVR` selected over `SN6505BQDBVRQ1` (`C1849490`) assuming `+$2.18` delta; live JLC price of `C1849490` (3,000 stock) is `$0.9862` (`+$0.61` only). | JLCPCB API 2026-11-25 (`C74518` vs `C1849490`) | Consider `C1849490` (`+$0.61`) for AEC-Q100 compliance and double the JLC stock (`3,000` vs `1,541`). |
| **F-11** | **MINOR** | Both | `U402` (`TLV1702AIDGKR`), `04_CLR_N` | `TLV1702` `VOL` is not specified at `3.3 V / 0.33 mA` (`0.6–0.9 V` at `36 V`) vs `SN74AUP1G74` `VIL = 0.9 V`. | `sheet04_current_sensing.md` §Unverified #3; `v11_pwr.net` | Execute bring-up gate #12 (`≤ 0.6 V` across `-40..85 °C`) or swap to an open-drain comparator specified at `3.3 V`. |
| **F-12** | **NOTE** | v1.1 | `D110`, `D111` (`MBR0520LT1G`) | `MBR0520LT1G` reverse leakage rises to `8 mA` max at `20 V / 100 °C`; `sn6505b.pdf` p.23 warns to use low-leakage diodes (`RB168MM-40`) above `85 °C` ambient. | `mbr0520lt1g.pdf` p.2; `sn6505b.pdf` p.23 | Monitor `+5V_ISO` hot idle current and diode temp in gate `B8` at `85 °C`. |
| **F-13** | **NOTE** | v1.1 | `U101`, `+5V` | FPWM `LM5146-Q1` boosts a back-fed `+5V` supply into `VSUP`, heating `D103 SMCJ60A` (`B11`). | `lm5146-q1.pdf` p.5, p.26; `v11_ctrl.net` | Never back-feed `+5V` with `U101` enabled; document prominently on PCB silkscreen near `TP102`. |

---

## 4. Final Verdict: **HYBRID (Keep v1.1 `+5V_ISO`, Revert/Fix `+5V` Trunk)**

**Recommendation:** **Do NOT ship v1 verbatim (BLOCKER F-01), and do NOT ship v1.1 unchanged (MAJOR F-04, F-05, F-06). Adopt a Hybrid:**
- **Keep from v1.1:** The entire **`+5V_ISO` chain (`U105 TPS22918` + `U106 SN6505B` [prefer `-Q1 C1849490` for `+$0.61`] + `T101 LT31-113 / 760390014` + `2×MBR0520L` + `U107 TLV76750`)** AND the **sheet 07 Box-5 note fix**. First fix **F-06** by restoring the missing `T101_barrier_keepout` zone to `Transformer_WE-PPTI_760390014.kicad_mod`.
- **Change on `+5V` trunk:**
  - **Preferred Hybrid (Option A — Revert `+5V` buck to `LM5013` using `LM5013DDAR` `C5383001`):** Keeps v1's simpler, cooler, back-feed-immune `LM5013` buck (`+5V` `164 mA` eff `83%` vs `67%`, `1 A` eff `88%` vs `83%`, no `200 kHz` LW fundamental, no `0.37 V` typ-only shutdown trap, `3 ms` wake pulse OK, `6,930 pcs` in stock at `$0.97`). Combined with v1.1's `SN6505B + TLV76750`, **BOM drops `-$5.58 @ 100` vs v1.1 (`-$0.65` vs v1)**, Extended setup fee drops **`-$27`/batch**, and **Standby pack current drops to `~4.5 mA` (`3.24 Ah/mo` on 100–280 Ah vs `7.56 Ah/mo` in v1.1 and `9.72 Ah/mo` in v1)**.
  - **Alternative if AEC-Q100 + fixed-frequency FPWM on `+5V` are strictly non-negotiable (Option B — Keep `LM5146-Q1` with targeted fixes):** Change `R104` to `24.9 kΩ` (`400 kHz` above CISPR 25 LW) + `33–47 µH` inductor, swap `Q103` to `DMN10H220LQ-7`, update `R125/R126` descriptions to `30 ms`, and strictly gate `B1/B2/B4/B8/B10` on the first prototype.

### Top 3 Reasons for This Verdict
1. **v1's `B0505S-2WR3` is a hard safety/compliance BLOCKER (F-01, F-02):** `3.58 mm` creepage (`< 6.5 mm`), `1500 VDC` isolation (`< 2.5 kVrms`), and `> 5.5 V` light-load overvoltage make v1 unusable as-is. v1.1's `SN6505B + T101 + TLV76750` completely solves all three with `8.02 mm` gap, `2.5 kVAC`, `4.94–5.05 V` regulation, SSC, and `~9 mA` lower standby.
2. **v1.1's `LM5146-Q1` buck introduces worse efficiency, higher cost, and new reliability risks without solving CISPR 25 LW:** At `+$4.31/board` (`+18` parts, `+9` Extended fees), it loses `5–16%` efficiency (`67%` vs `83%` at typical `164 mA`), adds back-feed boost risk, relies on an unguaranteed `0.37 V` typical shutdown threshold (`1.75 mA` Standby trap), and puts its `200.4 kHz` FPWM fundamental *inside* CISPR 25 LW (`150–300 kHz`).
3. **v1.1 has an unapplied footprint safety fix (F-06):** The `T101_barrier_keepout` rule area required by `V11-14` is absent from the committed `Transformer_WE-PPTI_760390014.kicad_mod`, and `LT31-113` still lacks a `-40 °C` rating (`771` JLC-only stock).

### Quantified Trade-off Summary (51.2 V Pack, 100 pcs Pricing)

| Configuration | BOM Δ vs v1 (@100) | Ext. Setup Δ | `+5V` Eff (Typ / Peak) | Standby Pack Drain (`EN_ISO` ON) | CISPR 25 LW (`150–300 kHz`) | Isolation Barrier |
|---|---|---|---|---|---|---|
| **v1 (`LM5013-Q1` + `B0505S`)** | `$0.00` | `$0` | `83.2% / 87.9%` | `~13.5 mA` (`9.7 Ah/mo`) | Sweeping DCM (`~85–165 kHz`) | **FAILS** (`3.58 mm`, `1.5 kVDC`) |
| **v1.1 (`LM5146-Q1` + `SN6505B`)** | **`+$4.93`** | **`+$39`** | `66.8% / 82.6%` | `~10.5 mA` (`7.6 Ah/mo`) | **200.4 kHz fundamental in LW** | **PASSES** (`8.02 mm`, `2.5 kVAC`, needs keepout) |
| **Recommended Hybrid (`LM5013` + `SN6505B`)** | **`-$0.65`** *(with `LM5013DDAR`)* | **`+$12`** | `83.2% / 87.9%` | **`~4.5 mA` (`3.2 Ah/mo`)** | Sweeping DCM (`~85–165 kHz`); iso clean (`424 kHz` SSC) | **PASSES** (`8.02 mm`, `2.5 kVAC`, with keepout) |

---

## 5. Items That Could Not Be Verified

1. **Physical PCB layout & DRC:** No PCB exists yet for the v1/v1.1 architecture (`Automotive_ESS_BMS.kicad_pcb` in the repo is a stale Nov 2 layout); actual `< 1 cm²` hot-loop inductance, SW-node ringing (`B4`), `NT401` Kelvin symmetry, and `8.02 mm` isolation routing/slot could not be measured.
2. **Linekey `LT31-113` primary PDF:** Not hosted on LCSC/JLC product APIs (`dataManualUrl` empty); electrical parameters (`1:1.3`, `2.5 kVAC/60 s`, `0.31/0.37 Ω`, `12.5 pF`) were corroborated via cached distributor data and `Würth 760390014` (`we-online.com` PDF returned HTTP 403 to scripted download; specs corroborated via search & `sn6505b.pdf` Table 9-3). Operating temperature range for `LT31-113` remains unverified.
3. **Unguaranteed datasheet parameters:** `LM5146-Q1` `VSHDN` (`0.42/0.37 V` typical only), `SQ2398ES` `RDS(on)` at `6.4–6.9 V` / `-40 °C`, `DMN10H220LQ-7` switching times at `7.5 V`, `TLV1702` `VOL` at `3.3 V / 0.33 mA`, and `SMDRI127-680MT` core loss at `200 kHz` (estimated `30 mW`).
4. **Capacitor DC-bias curves:** Effective capacitance of `250 V 2220` (`C153032`) at `58.4 V` and `25 V 1210` (`C2918511`) at `5 V` used `-30%` / `-15%` engineering estimates (`sheet01_power_supply.md` §9 #2) rather than manufacturer bias plots.
5. **High-voltage transient bench behavior:** `D-04` `800 A` FET turn-off / `5.0SMDJ60CA` clamping margin, `ES2D` `85 °C` leakage at `58.4 V`, and `TPS3828` + `PWR_EN` `-40 °C` wake margin remain analytical pending prototype bench verification.

---

## Independent Verification & v1.2 Disposition (2026-11-25)

Every BLOCKER/MAJOR finding, live price/stock figure, and EMC point above was checked against the repository, footprints, and live distributor APIs on 2026-11-25 before adopting **v1.2** (`PROJECT.md` §5, [`docs/SCHEMATIC_V1.md`](../SCHEMATIC_V1.md#10-revision-v12-2026-11-25)):

| Item | Claim in v1 vs v1.1 comparison | Live / Design Verification (2026-11-25) | Disposition in v1.2 |
|---|---|---|---|
| **F-06** (`T101` barrier keepout) | Copper keep-out under `T101` (`Transformer_WE-PPTI_760390014.kicad_mod`) must be verified | **Confirmed and fixed:** rule area `T101_barrier_keepout` (`*.Cu`, x ±4.0 / y ±3.4 mm, tracks/vias/pours disallowed) verified in footprint | **Fixed in v1.2** |
| **F-09** (wake-pulse doc mismatch) | Docs/notes still cited stale `>= 10 ms` wake pulse vs TPS3828 120–300 ms reset | **Confirmed and fixed:** restored v1.0 latch (`1 MΩ` / `1 µF`); real firmware rule set to **`AFE_ALERT` latched until MCU clears (preferred), or low ≥ 2 ms** (≥ 1.4 ms worst-case) | **Fixed in v1.2** |
| `LM5013QDDARQ1` (`C5219285`) | Low stock risk in v1 | **213 pcs** live on LCSC & JLCPCB (`$3.53` LCSC / `$3.50` JLC @100) | Replaced by `LM5013DDAR` |
| `LM5013DDAR` (`C5383001`) | Commercial-grade pin-identical alternative | **6,940 pcs** live on LCSC & JLCPCB, **`$0.98`** (`$0.9828` LCSC / `$0.9748` JLC @100) | **Selected for U101 (v1.2)** |
| `SN6505BQDBVRQ1` (`C1849490`) | AEC-Q100 Grade 1 drop-in alternative for U106 | **3,000 pcs** live on LCSC & JLCPCB, **`$0.995`** (`$0.9954` LCSC / `$0.9862` JLC @100) | **Selected for U106 (v1.2)** |
| `LM5146QRGYRQ1` (`C1850329`) | Expensive controller in v1.1 (+$5.6/board delta) | **8,853 pcs** LCSC (`$6.61` / `$6.6068`) / **9,124 pcs** JLC (`$6.5527` @100) | Archived (`ca3a7a3` fallback) |
| **EMC bands (CISPR 25 vs ESS)** | Moving switching fundamental to 400 kHz clears CISPR 25 LW (150–300 kHz) | **CISPR 25 LW point is valid for automotive**, whereas **stationary-ESS conducted emission limits (CISPR 11 / 32, IEC 61000-6-x) start at 150 kHz** regardless, so moving to 400 kHz does not escape stationary ESS limits | **Bring-up gate B12** (LISN pre-scan of LM5013 buck before board release) |
