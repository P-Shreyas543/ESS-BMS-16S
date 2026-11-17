# 03 — Cell balancing review and proposal (sheet 02, U_AFE1 BQ76952)

Date: 2026-11-17. Research only. No project file was changed.

## Sources

Tags used below: **[DS]** = datasheet, **[TRM]** = technical reference manual, **[AN]** = app note, **calc** = my own arithmetic, **est.** = estimate or engineering judgement.

| Tag | Document | Status |
|---|---|---|
| [DS] | TI SLUSE13B, BQ76952 datasheet (local `review/ds/bq76952.txt`) | opened |
| [TRM] | TI SLUUBY2B, BQ76952 TRM, rev. May 2022 (ti.com/lit/pdf/sluuby2) | opened: §10 (p.85–88), §4.1 (p.18), §13.3.11 (p.174–176) |
| [AN] | TI **SLUAA81A**, *Cell Balancing With BQ769x2 Battery Monitors*, Feb 2022 (ti.com/lit/pdf/SLUAA81) | opened in full; Figure 2-2 viewed as an image |
| SLUA964 | the note named in the brief | **wrong reference**: SLUA964 is *Improving Efficiency of DC-DC Conversion through Layout* (UCC27524A). The balancing note is SLUAA81. SLVAE65 was not looked up. |
| [AO] | AOS AO3400A datasheet (local) | opened |
| [JBD] | JBD-UP16S010-L16S-200A spec A03 | opened, p.8 and p.11 |
| Daly / JK | web search only | Daly 16S 100 A: 30 ± 5 mA. JK-PB2A16S20P: 1–2 A active, 10 mV trigger. These are vendor claims and were not tested. |
| LCSC | jlcpcb.com/partdetail and lcsc.com product pages, for identity | opened |
| LCSC stock / Basic | jlcsearch.tscircuit.com, a mirror of the JLCPCB catalogue (fetched 2026-11-17) | Stock and Basic/Extended come from the mirror, not from live LCSC. Some Basic resistors show stock "null" in the mirror. **Re-check in the JLCPCB BOM tool before ordering.** |

Netlist facts were checked in `baseline/before.net`:
* `NET_BAL1 = Q_BL1.D + R_BL1.2`
* `CELL_1 = J_CELL1.2 + R_BL1.1 + R_VC1.1 + Q_BL2.S`
* `VC0 = U_AFE1.16 + R_VC0.2 + C_DF1.2 + Q_BL1.G`
* `CELL_0 = J_CELL1.1 + R_VC0.1 + Q_BL1.S`
* The same pattern repeats up to `Q_BL16`: gate on `VC15`, source on `CELL_15`, drain through R_BL16 to `CELL_16`.

---

## 1. Today's external balancing circuit compared with TI's reference

### 1.1 Topology: polarity and pin connections are correct. Two parts TI asks for are missing.

TI reference, [AN] Figure 2-2 (p.4), shown for one channel n:

```
 CELL_n ──┬──────────────[ Rn 100R ]──────────┬── VCn pin ─┐
          │                                   │            │ internal CB switch (RCB 15–46 R)
       [Rbal]                               Cn ═           │
          │ D                                 │            │
          ├──|N-FET  G ──[ Rgn 1k ]──┬────────┴── VC(n-1) pin ─┘
          │ S                        │
          │                  Dgate (Zener, cathode at gate)
          │                          │
 CELL_n-1 ┴──────────────────────────┴──[ R(n-1) 100R ]── (filter node above)
               VGS = I_CB × R(n-1)   ("–  VGS  +" across R(n-1), Fig 2-2)
```

When the internal switch turns on, current flows out of the VC(n-1) pin through R(n-1) into CELL_(n-1). This lifts the pin-side node above the cell node by I_CB × R. That voltage drives the gate, with the source on CELL_(n-1). [AN] p.3: *"the current flowing through Rn-1 provides the VGS for the external FET."*

Today's design (sheet 02, from the netlist):

```
 CELL_n ──┬──[R_VCn 100R]── VCn
       R_BLn 33R 2512
          │ D
          ├──| AO3400A  G ─────────────── VC(n-1)    ← no Rgn, no Zener
          │ S
 CELL_n-1 ┴──[R_VC(n-1) 100R]── VC(n-1)
```

| Item | TI [AN] | Today | Verdict |
|---|---|---|---|
| Switch type | N-FET (or P-FET Fig 2-4, or NPN BJT Fig 2-5) | N-FET AO3400A | OK |
| Drain | through Rbal to the top of cell n | through R_BLn to CELL_n | OK |
| Source | CELL_(n-1) (cell side of R(n-1)) | CELL_(n-1) | OK |
| Gate | VC(n-1) pin side of R(n-1), **through Rgn = 1 kΩ** | straight to VC(n-1) | **Missing Rgn** |
| Gate protection | *"A Zener diode is needed to protect the external FET gate from pack transients"* (p.4) | none | **Missing.** A pack short puts tens of volts across R_VC (TI example: ~40 V on a 10S pack). AO3400A VGS abs max is ±12 V [AO]. |
| Input resistor | 100 Ω, the DS maximum, when external switches are used (p.3) | 100 Ω | OK |
| Top-cell input resistor | 20 Ω on VC16 to cut the IR drop from 35 µA × N cells (p.8; [TRM] p.87) | 100 Ω | **Change.** 35 µA × 8 cells × 100 Ω = **28 mV** low reading on cell 16 while balancing (calc). That error is too large for LFP balancing decisions. |

**Answer to PROJECT.md §8 Q6:** the polarity and the gate/source connections are right and match TI. The circuit is incomplete: it has no gate resistor and no clamp. The gate drive is also not guaranteed (§1.2).

### 1.2 Internal balance current, VGS and AO3400A suitability

Internal switch R_CB = 15 / 28 / 46 Ω (min / typ / max) at 1.5 V [DS] p.18 §7.20.

* I_CB = Vcell / (2·R_VC + R_CB) [AN] p.2
* VGS = I_CB × R_VC = Vcell × 100 / (200 + R_CB) (calc)

| Vcell | I_CB (typ) | VGS @ R_CB 15 Ω | VGS @ 28 Ω (typ) | VGS @ 46 Ω |
|---|---|---|---|---|
| 3.00 V | 13.2 mA | 1.40 V | 1.32 V | 1.22 V |
| 3.20 V | 14.0 mA | 1.49 V | 1.40 V | 1.30 V |
| 3.40 V (LFP knee) | 14.9 mA | 1.58 V | 1.49 V | 1.38 V |
| 3.45 V | 15.1 mA | 1.60 V | 1.51 V | 1.40 V |
| 3.65 V (LFP max) | 16.0 mA | 1.70 V | 1.60 V | 1.48 V |

AO3400A [AO] p.2: VGS(th) = 0.65 / 1.05 / **1.45 V** at ID = 250 µA. RDS(on) is specified only down to **VGS = 2.5 V** (48 mΩ).

TI's sizing rule [AN] p.4: choose an FET *"with an RDSON defined at or below"* Vmin × 100 / 225. For an LFP start of 3.40 V that is ≈ 1.5 V typical, or 1.38 V with the worst-case R_CB.

**Verdict: the AO3400A does not meet TI's rule.**
* A typical part (Vth ≈ 1.05 V) will probably switch on at 1.4–1.5 V.
* A high-Vth part, or any part when cold (Vth rises as temperature falls), will sit at 1.38 V gate drive against a 1.45 V threshold. It then carries anywhere from 0 to ~100 mA, set by part spread.
* **Today's circuit works on most boards, by luck, and is not guaranteed.**

### 1.3 Balance current and heat (calc)

With the switch fully on, I_ext = Vcell / 33 Ω, and the internal ~15 mA adds to it.

| Vcell | I_ext | Total | P per R_BL | 8 cells at once | all 16 |
|---|---|---|---|---|---|
| 3.20 V | 97 mA | 111 mA | 0.31 W | 2.5 W | n/a, see §1.4 |
| 3.45 V | 105 mA | 120 mA | 0.36 W | 2.9 W | n/a |
| 3.65 V | 111 mA | 127 mA | 0.40 W | 3.2 W | n/a |

* A 1 W 2512 runs at 36–40 % load. With typical thick-film derating above 70 °C, it still has margin at an 85 °C board (est.).
* The AFE die adds I_CB² × R_CB ≈ 10 mW per cell at worst, so 80 mW for 8 cells. That is negligible against the 66 °C/W die-to-ambient figure ([AN] p.3).
* The board maximum is ≈ **3 W**, not the 6.4 W in review A13. Only 8 external channels can be driven at once (§1.4).
* Local hot-spot: about +20–30 K over the bank with B.Cu pours (est., not simulated). RT_BOARD (the board NTC on DDSG) is the right sensor to throttle on.

**Averaged current:** balancing pauses when the cell itself or a neighbour is measured, for the top-of-stack read, and for ~20 ms every second for the COV/CUV checks ([TRM] p.87–88).
* At full loop speed (21 slots × 3 ms = 63 ms, [TRM] p.18), about 3 of 21 slots are blocked: ≈ 86 % duty (calc).
* With `CB_LOOP_SLOW = 11` (1/8 speed, 504 ms loop), duty is ≈ 96 % (calc).

### 1.4 Adjacent-cell limits

* Autonomous mode only balances **non-adjacent** cells ([DS] p.63; [AN] p.11).
* Host mode may balance adjacent cells, but TI warns about the 100 mA abs-max per pin and the abs max on VC0 ([AN] p.11; [DS] p.8).
* **This external circuit cannot drive adjacent channels anyway.** If cells n and n+1 balance together, the internal currents through R_VCn cancel (one flows in, one flows out). Q_BL(n+1) then gets VGS ≈ 0 and only the ~15 mA internal current flows in cell n+1 (calc).
* Firmware must therefore balance in **odd / even groups**, with at most 8 cells at once.

### 1.5 R_VC: 100 Ω or 1 kΩ?

The project data disagree:
* Value field: `100R 1%`
* LCSC field: **C22775**. Verified: UNI-ROYAL 0603WAF1000T5E, **100 Ω**, Basic.
* MPN field: `RC0603FR-071KL`, which is a Yageo **1 kΩ** part.

**Use 100 Ω.** 1 kΩ is outside the DS input window of 20–100 Ω ([DS] p.9). It would also cut the internal current to ~1.7 mA, and TI's external-switch designs use 100 Ω ([AN] p.3–4).

Fix the MPN to 0603WAF1000T5E. Make R_VC16 20 Ω (§1.1): C22950, 0603WAF200JT5E, Basic.

### 1.6 BOM errors found while checking (not asked for, but important)

| Ref | LCSC in schematic / BOM | What it really is | Fix |
|---|---|---|---|
| R_BL1-16 | **C17936** | **1206 4.7 kΩ** (1206W4F4701T5E), verified on jlcpcb.com and lcsc.com. JLCPCB would fit 4.7 k parts, giving ~0.7 mA of balancing. | C53728 (25121WF330JT4E 33 Ω 1 W 2512, Extended; mirror shows no stock) **or** C2793905 (PS122WF330JT4E 33 Ω **2 W** 2512, Extended, stock 3 042 in the mirror) |
| Q_BL1-16 | **C85073** | Not found: LCSC says "Part not found" and the JLCPCB page is empty | C20917 AO3400A (AOS, **Basic**, stock 989 942), or replace per §4 |
| C_DF1-16 (+ C3, C6, C16, C_CP1, C_K1) | **C14666** | JLCPCB page empty. The MPN CC0603KRX7R9BB104 is **C14663** (verified) | C14663 |

PROJECT.md line 154 also lists C17936.

### 1.7 Changes needed: summary

1. **Make the switch's turn-on deterministic.** Either:
   * (rec) replace the FET with an NPN BJT, per TI [AN] §2.4 *"for applications that need … to balance at lower cell voltages"*. That describes LFP exactly. See §4.
   * or keep an FET, but choose one with RDS(on) specified at VGS ≤ 1.5 V and Vth(max) ≤ 1.0 V.
2. Add the gate/base resistor and the clamp per TI (Rgn 1 k + 5.6 V Zener for an FET; Rbn 220–240 Ω + a small-signal diode for a BJT).
3. Set R_VC16 to 20 Ω.
4. Correct the three LCSC numbers and the R_VC MPN (§1.5–1.6).
5. Firmware: odd/even groups, at most 8 cells, LFP thresholds (§3).

---

## 2. Balancing options for 16S LFP, 100–280 Ah

Assumptions:
* Charge to move: 1 % / 5 % of 100 Ah is 1 / 5 Ah; of 280 Ah it is 2.8 / 14 Ah.
* Average current includes the ~90 % duty (§1.3).
* Active-balancer current is taken as **0.5–1 A average**. A capacitive balancer's current scales with ΔV, and on the LFP plateau ΔV is only a few mV (est.).
* Times are **continuous** balancing hours. Passive balancing on LFP is only useful at the top knee (≥ 3.40 V) unless the firmware balances by SOC (§3).

| Option | Avg. I | 1 % / 5 % @100 Ah | 1 % / 5 % @280 Ah | BOM cost (16S, est.) | Area | Heat | Complexity | LCSC |
|---|---|---|---|---|---|---|---|---|
| **(a)** BQ76952 internal only (R_VC 100 Ω) | ~13.5 mA | 74 h / 370 h | 207 h / 1 040 h | $0 (remove 32 parts, save ~$1.5) | saves ~6 cm² | ~0.1 W in the AFE | lowest | – |
| (a') internal with R_VC 20 Ω | ~55 mA, limit to ~5 cells for AFE heat ([AN] p.3) | 18 h / 90 h | 51 h / 255 h | $0 | – | 0.1 W per cell **in the AFE**; die heat limits it | low | – |
| **(b1)** today: AO3400A + 33 Ω | 0–105 mA (not guaranteed) | 9.6 h / 48 h if the FET turns on | 27 h / 135 h | ~$1.9 | ~6 cm² | ≤ 3 W | low | C20917 Basic |
| **(b2)** fixed external passive, NPN + 33 Ω (**rec.**) | ~105 mA guaranteed | 9.6 h / 48 h | 27 h / 135 h | ~$1.0–2.0 (cheaper than b1) | ~7.5 cm² (+1.3 cm²) | ≤ 3 W | low | all Basic except R_BL |
| (b3) as b2 with 22 Ω (≈150 mA) | ~150 mA | 6.7 h / 33 h | 19 h / 93 h | same | same | ≤ 4.1 W, 0.51 W per 2512 | low | needs a thermal test |
| (b4) 300 mA passive (11 Ω, 1 W per channel) | ~300 mA | 3.3 h / 17 h | 9 h / 47 h | ~$3 | 2 W parts, ~12 cm² | **≤ 8 W**: not compact, needs heatsinking | low | 2 W 2512 Extended |
| **(c1)** DIY switched capacitor (15 flying caps, 32 FETs, level-shifted drive) | 0.1–1 A, scales with ΔV; weak on the LFP plateau | 1–10 h / 5–50 h | 3–28 h / 14–140 h | $10–20 (est.) | 20–30 cm² | low, efficient | **high**: gate drive across 16 levels, EMI | parts yes, design no |
| (c2) inductor / flyback, **ADI LTC3300-1** (6 cells/IC, 3 ICs + 16 transformers + 32 FETs) | 1–5 A, bidirectional | < 1 h / 1–5 h | 1–3 h / 3–14 h | **$80–120+** (IC $9.9–20.7 each) | 40–60 cm² | low | very high | LTC3300HUK-1 **C684431, $20.67, stock 35**; LTC3300HLXE-1 C684428, $9.88–12.24, **stock 2**; Extended. Transformers: not checked |
| (c3) other dedicated ICs: ADI LT8584 (not found in the mirror); TI EMB1428/EMB1499 (not found; lifecycle not verified); TI BQ796xx, NXP MC3377x, ST L9963, ADI LTC68xx | – | – | – | – | – | – | – | To my knowledge (not verified this session) the TI BQ79xx, NXP and ST monitors are **passive** only. No cheap active IC exists on LCSC. |
| (c4) **external JK / Heltec / NEEY-style 1–2 A capacitive active module** with its own cell harness | 1–2 A peak; 0.2–1 A on LFP (est.) | 1–5 h / 5–25 h | 3–14 h / 14–70 h | $0 on board; module about $20–60 retail (est., not verified) | 0 on board | in the module | none on board | AliExpress, not LCSC |
| (c5) active-balancer **daughter board on a header** (our own design) | as c1/c2 | as c1/c2 | as c1/c2 | as c1/c2 + connector | off board | – | high (second product) | – |
| **(d)** **hybrid: b2 on board + an enable port for an optional c4 module** (**rec.**) | 105 mA standard; +1–2 A when fitted | 9.6 h → 1–2 h | 27 h → 3–6 h | ~$1.2 + ~$0.2 port | +~1.5 cm² | ≤ 3 W | low | Basic + 1 header |

Competitor data:
* Daly 16S: 30 ± 5 mA passive (search; spec sheet not opened).
* JBD 16S 200 A: passive, **20–60 mA**, starts at 3.47–3.53 V and Δ 30 mV, "time-sharing / pulse" mode ([JBD] p.8, §4.6 p.11).
* JK-PB2A16S20P: 1–2 A active, 10 mV trigger, start 3.0 V (gobelpower spec via search; not opened).

Option (b2) is about **2× JBD and 3–4× Daly**. Only JK beats it on current, and JK's capacitive balancer helps little on the LFP plateau where ΔV is a few mV.

**Holding balance:** LFP cells usually drift apart by about 0.5–2 %/month in self-discharge (est.).
* (b2) at 105 mA × 2 h/day ≈ 6 Ah/month, which keeps a 280 Ah pack in balance easily.
* (a) internal only gives ≈ 0.8 Ah/month (0.3 %). That is **not enough** for 280 Ah.

**Initial balance of a new 280 Ah pack at 5 %:** b2 needs ~6 days of continuous balancing; an active module needs < 1 day.

---

## 3. Recommendation: how to "beat Daly / JBD / JK"

**Hardware:** option **(d)**.
* Guaranteed ~105 mA on-board passive balancing (NPN, TI [AN] §2.4).
* R_VC16 = 20 Ω.
* An **"ACTIVE BAL" port**: a 3-pin header with BAL_EN (open drain), GND_PWR and a spare, so the BMS can switch an optional JK / Heltec-style module **on and off**.
* The module must use **its own cell harness**. 1–2 A flowing in the J_CELL1 sense wires (a 2.54 mm header) would corrupt the AFE readings.
* The enable input of commercial modules was not verified, so make the port generic (open drain plus a pull-up option).

The real lead over the Chinese BMS makers comes from **firmware**: they all balance on voltage alone. Our firmware should do the following.

1. **Host-controlled, SOC-based balancing** (`CB_ACTIVE_CELLS` 0x0083, [AN] p.10 Table 4-1).
   * During each charge, record the **Ah count** (coulomb counter, CC2) at the moment each cell crosses the LFP knee (e.g. 3.45 V).
   * ΔAh_i = I × (t_i − t_last) gives each cell's real charge surplus in Ah, even though the voltages were equal on the plateau.
   * Compute the balance time t_i = ΔAh_i / I_bal and run it **at any time**: during rest, discharge or the plateau. You are no longer restricted to the short window above 3.45 V.
   * Refresh the command inside `Cell Balance Interval` (default 20 s, [TRM] p.175).
   * Read `CBSTATUS2/3` (0x0086/0x0087) for the cumulative time per cell ([AN] p.11).
2. **Groups:** odd/even only, at most 8 cells. `Cell Balance Max Cells` is ignored in host mode ([TRM] p.175), so the firmware enforces the limit. Throttle on RT_BOARD (e.g. full at < 60 °C, half at 60–75 °C, off above 75 °C).
3. **Fallback autonomous mode,** for when the MCU sleeps or hangs. The defaults are Li-ion values and **must change for LFP**: with the default 3 900 mV start, an LFP pack would never balance.
   * `Balancing Configuration` = CB_CHG | CB_RLX | CB_SLEEP | CB_NOSLEEP (0x0F) ([TRM] p.174)
   * `Cell Balance Min Cell V (Charge)` = 3 400 mV and `(Relax)` = 3 400 mV
   * `Min Delta (Charge/Relax)` = 20 mV
   * `Stop Delta (Charge/Relax)` = 8 mV
   * `Cell Balance Max Cells` = 8
   * `Min Cell Temp` = 5 °C, `Max Cell Temp` = 50 °C, `Max Internal Temp` = 70 °C
   * `Cell Balance Interval` = 20 s
   * `Power Config[CB_LOOP_SLOW]` = 11
   * TI default sources: [TRM] p.174–176. The LFP values are my proposal.
4. **LFP plateau rule:** never balance on voltage deltas between 3.25 and 3.35 V. A few mV there is noise or IR drop, not SOC. Balance on voltage only at rest (> 30 min, |I| below the relax threshold) in the knee, or by the Ah method above.
5. **Diagnostics competitors don't offer:**
   * per-cell cumulative balance Ah logged over time, which gives a **self-discharge / weak-cell trend alarm**
   * a balance-effectiveness report over CAN / RS-485
   * an automatic active-module enable only when ΔSOC is greater than e.g. 3 % and the cells are in the knee or at rest

---

## 4. Circuit proposal (per channel n = 1…16; refs are proposals)

```
 CELL_n ───────────────┬──────────[R_VCn 100R]──── VCn
                     R_BLn 33R 2512 (1 W, or 2 W)
                       │ C
 CELL_n-1 ──┬──────────┤                    Q_BLn  SS8050 NPN, SOT-23
            │        E ┤ B
            │          └──[R_BBn 220R 0603]──┬──── VC(n-1)
            │                                │
            └──────|<|── D_BBn 1N4148WS ─────┘     anode = CELL_(n-1) (emitter), cathode = base side
 CELL_n-1 ───[R_VC(n-1) 100R]─── VC(n-1)          (R_VC16 = 20R)
```

**Base drive (calc):** solve I_CB = (Vcell − Vx)/(100 + R_CB) = Vx/100 + (Vx − 0.7)/220.

| Vcell | R_CB | IB | Forced β at ~95 mA |
|---|---|---|---|
| 3.0 V | 46 Ω | ≈ 1.8 mA | ≈ 53 |
| 3.3 V | 46 Ω | ≈ 2.3 mA | ≈ 45 |

The SS8050 C2150 is binned at hFE 200–350, so it stays deeply saturated, even with hFE halved at −40 °C. I_CB stays ≤ 20 mA, far below the 100 mA abs max.

As a cross-check, TI's own build (Rn 100 Ω, Rbn 240 Ω, 4 V cell) measured IB ≈ 4.5 mA and ~22 mA internal ([AN] p.7). My model gives ~3.6 mA and ~19 mA at the same point.

**Other circuit points:**
* **Footprint:** the SOT-23 pin order is the same as the AO3400A (1 = G/B, 2 = S/E, 3 = D/C). The SS8050 datasheet was not opened, so confirm the pinout. It needs the X1 pin-numbering fix from the review either way.
* **Clamp:** TI [AN] p.7: *"A standard diode is also suitable … because it is the forward voltage … that protects the transistor."* R_BB limits the base current during pack transients. Its 0603 pulse rating was not checked.
* **Port:** `BAL_EN` on a spare MCU pin (PA15 or PB4, unconnected per PROJECT.md) → AO3400A C20917 open drain → 3-pin 2.54 mm header (J_ABAL1: BAL_EN, GND_PWR, NC). One 10 k gate pull-down.

| Function | Part | LCSC | Type | Stock (mirror) | ~Unit $ |
|---|---|---|---|---|---|
| Q_BL1-16 | SS8050 (RANGE 200-350), CJ, SOT-23, 25 V 1.5 A | **C2150** | **Basic** | 3 119 252 | 0.014 |
| R_BB1-16 | 220 Ω 1 % 0603, 0603WAF2200T5E | **C22962** | **Basic** | null in mirror | 0.0014 |
| D_BB1-16 | 1N4148WS SOD-323 | **C2128** | **Basic** | null in mirror (alt. C7420319, Extended/preferred, 2 253 018) | ~0.01 |
| R_BL1-16 | 33 Ω 1 % 1 W 2512, 25121WF330JT4E | **C53728** | Extended | not shown; **verify** | 0.034 |
| (alt.) R_BL | 33 Ω 1 % **2 W** 2512, PS122WF330JT4E | **C2793905** | Extended | 3 042 | 0.107 |
| R_VC0-15 | 100 Ω 1 % 0603, 0603WAF1000T5E | **C22775** | **Basic** | null in mirror | 0.0023 |
| R_VC16 | 20 Ω 1 % 0603, 0603WAF200JT5E | **C22950** | **Basic** | null in mirror | 0.0016 |
| Port switch | AO3400A | **C20917** | **Basic** | 989 942 | 0.085 |
| FET fallback, if staying with an FET | AO3416, SOT-23, 20 V, ~1 V Vth, 34 mΩ @ 1.8 V (from the mirror description) | e.g. C43307 | Extended | 33 986 | 0.12 → 0.055 |

* **FET fallback:** add Rgn 1 k + BZT52C5V6 (C397930, Extended). The AOS AO3416 datasheet was not opened.
* **Cost against today, 16 channels (calc):**
  * SS8050 instead of AO3400A: −$1.13
  * add 16 × 220 Ω: +$0.02
  * add 16 × diodes: +$0.16
  * net **≈ −$0.95 per board**, plus the port at ≈ +$0.15
  * No new Extended-part loading fee: everything new is Basic, and R_BL is Extended already.
* **Area:** 32 small parts ≈ +1.3–1.5 cm² beside the existing bank, plus ~0.5 cm² for the header and FET.

---

## 5. What I could not verify

* SLUA964 is not the balancing note, and SLVAE65 was not looked up. SLUAA81A was used instead.
* Live LCSC stock and the Basic flags: the mirror shows Basic resistors with stock "null". Re-check in the JLCPCB BOM tool.
* Datasheets **not opened**:
  * SS8050 (CJ): pinout, hFE at 100 mA, VCE(sat) at 100 mA
  * AO3416, 1N4148WS, BZT52C5V6
  * LTC3300-1 (only the LCSC listing)
  * Daly and JK specs (search snippets only)
  * JK / Heltec / NEEY enable-input details
* AO3400A behaviour below 1.5 V gate drive: it has no RDS(on) spec there, and the transfer curve was not read numerically.
* Thermal figures are estimates. A thermal test or simulation of the B.Cu bank at 3 W (or 4 W with 22 Ω) is needed.
* The R_BB 0603 surge rating under a pack short.
* The LFP drift rate (0.5–2 %/month) and the active-module average current are engineering estimates.
