# v1.1 power-tree review (sheet 01) — findings and disposition

**Review 2026-11-24; fixes accepted by the owner and applied 2026-11-25.** An independent power-electronics review looked only at the v1.1 change on control-board sheet 01. It covered two changes:

1. The +5V trunk moves from the LM5013-Q1 to an **LM5146-Q1** synchronous buck controller with external SQ2398ES (high-side) and DMN10H220LQ (low-side) FETs, 200 kHz forced PWM and a 68 µH inductor. The PWR_EN latch is re-scaled to suit the new EN/UVLO pin.
2. `+5V_ISO` moves from the **B0505S-2WR3** isolated module (with its dummy load) to an **SN6505B** push-pull driver, an LT31-113 1:1.3 transformer, 2 × MBR0520L rectifiers and a **TLV76750** 5.0 V LDO.

Before the review, the change was worked out in two design studies:

* **Buck study.** The LM5146-Q1 was the only part found that is synchronous, rated 100 V, AEC-Q100, above 1 A, able to run forced PWM, and in stock. It was rejected:
  * LM5164-Q1: its valley current limit (0.95 A min) is below the 0.962 A peak.
  * LM5161-Q1: stock too low.
  * LM5168 / LM5169: current too low.
  * LM5017, LTC7103 and SCT2A23: not AEC-Q.
  * LMR38025: rated 80 V only.
  * LM5012: asynchronous.
* **Iso study.** It found a **v1.0 creepage defect**: on the B0505S footprint only 3.58 mm separates pad 2 (`GND_PWR`) from pad 4 (`GND_ISO`), against the 6.5 mm rule. Because the module is through-hole, a board slot cannot fix this. The transformer footprint has an 8.02 mm pad gap across the barrier.

| BLOCKER | MAJOR | MINOR | NOTE |
|---|---|---|---|
| 0 | 4 | 10 | 12 |

## Verdict

* **Nothing blocked drawing.** Pinning, netlist, footprints, interface nets and LCSC numbers are correct.
* **The control loop is sound.** The reviewer recomputed it independently: fc 20 kHz, PM 57–59°, GM 18 dB nominal; worst corner 33 kHz / 48°.
* **The PWR_EN latch needs no comparator.** Two weaknesses remained:
  * the wake-pulse rule (10 ms) did not cover the 120–300 ms reset supervisor;
  * the Sleep floor rested on a threshold that is only specified as typical.
* **The weak part of v1.1 was the power stage around Q104.** A single SOT-23 low-side FET was both the heat bottleneck and the current-sense element. With its real R_DS(on) temperature curve, the worst-case current limit fell below the 1.00 A peak.

All four MAJOR findings were fixed before drawing. The owner accepted the cost on 2026-11-25:

* about **+6 mA** standby compared with the LM5013 (the owner had first accepted about +3 mA);
* about **81 %** peak buck efficiency (first accepted: about 84 %).

The SN6505B change saves about 9 mA of idle draw, so board standby is still about 3 mA below v1.0.

The checks after the fixes are recorded in the sheet 01 design note: 114 refs, interface net set identical to v1.0, 0 self-check errors. The ERC result of the drawn board is in [`../SCHEMATIC_V1.md`](../SCHEMATIC_V1.md).

## Findings and disposition

| ID | Sev. | Finding | Disposition |
|---|---|---|---|
| V11-01 | MAJOR | In the hot corner the worst-case valley current limit (low-side R_DS(on) sensing) fell to 0.71–0.81 A. The operating valley at the 1.00 A peak is 0.83 A, so the converter would hiccup at the design peak. | **Fixed.** The current limit now uses RSENSE mode: R138 100 mΩ 1 % 1 W shunt in the low-side source path, R131 1.50 k to the shunt top, PGND Kelvin to the shunt. Valley limit 1.29 / 1.52 / 1.76 A (min / typ / max), with no temperature term. Worst peak 2.20 A against the inductor's 4.0 A saturation current. |
| V11-02 | MAJOR | The SOT-23 low-side FET was thermally at or beyond its limit, and its only heat path is the SW node (an EMI conflict). | **Fixed.** Q105 added: a second DMN10H220LQ-7 in parallel, with its own 0 Ω gate resistor R139. Each FET dissipates 0.11–0.13 W, Tj 104–108 °C on the minimum pad. Q103 Tj 131 °C. Cost: +1.7 mA standby. |
| V11-03 | MAJOR | No SW-ringing margin during a TVS-clamp event. The snubber was DNP and the gate resistor 0 Ω, and gate B4 would have passed 54 % overshoot. | **Fixed.** R135 / C138 snubber (10 Ω + 100 pF) fitted. R133 = 4.7 Ω on the high-side gate. Gate B4 rewritten: (V_SW,pk − VSUP) ≤ 8 V, undershoot ≥ −5 V at 58.4 V, and < 95 V at an 80 V bench VSUP. New layout rule for a small input loop. |
| V11-04 | MAJOR | The "AFE_ALERT low ≥ 10 ms" wake rule gives only 0.24–0.32 s of hold. That does not cover the up to 300 ms delay of the TPS3828 reset supervisor plus boot. | **Fixed (firmware and text).** AFE_ALERT latched until the MCU clears it (preferred), or low ≥ 30 ms (0.49–0.63 s hold). PWR_HOLD is the first GPIO action after reset. Gate B2 runs at −40 °C with the minimum pulse. |
| V11-05 | MINOR | Thin Sleep-floor margin on PWR_EN against the typical-only 0.37 V threshold. | **Fixed.** R123 / R124 changed from 100 k to 10 k; the FET leakage term is removed, leaving a 0.17–0.21 V floor. Gate B1 kept. |
| V11-06 | MINOR | SQ2398ES R_DS(on) is specified only at 10 V gate drive; the actual drive is 6.4–6.9 V. | **Accepted with gate B10.** Measure V_DS(on) at 1 A, −40 °C, 9 V AUX. Fallback: DMN10H220LQ-7 in the same footprint. |
| V11-07 | MINOR | 2.2 µF 0805 VCC capacitor sat at the bottom of the 1–5 µF window. | **Fixed.** C135 is now 4.7 µF 50 V 1206 (a part already in the BOM). |
| V11-08 | MINOR | Risk of C·dv/dt turn-on of the low-side FETs. | **Note and gate.** R134 / R139 stay 0 Ω ("never increase"). Gate B4 also scopes the low-side gate: bump < 0.8 V. |
| V11-09 | MINOR | SN6505B VCC bulk capacitor below "4.7 µF or greater" after DC bias. | **Fixed.** C127 is now 10 µF 25 V 1206. |
| V11-10 | MINOR | PWR_FLAG placement for the new rails (ERC). | **Fixed.** PWR_FLAG on `VSUP`, `+3V3_A`, `GND_ISO`, `01_U101_VIN` and `01_ISO_RECT`; none on `+5V_ISO`. |
| V11-11 | MINOR | In the worst-low corner `+5V_ISO` would be about 4.90 V, with the LDO in dropout. | **Fixed.** R105 changed from 10.5 k to 10.7 k: +5V = 5.08 V nominal (4.95–5.22 V); `+5V_ISO` = 4.94–5.05 V. |
| V11-12 | MINOR | The LT31-113 spec gives no operating-temperature range and no AEC statement (P-13 requires −40 °C). | **Owner decision 2026-11-25.** Keep the LT31-113 with a −40 °C qualification gate (B8); Würth 760390014 (AEC-Q200) is the drop-in alternate. The isolation is recorded as **functional, not reinforced**. |
| V11-13 | MINOR | In forced PWM the stage can run backwards: a back-fed `+5V` is boosted into VSUP, which the diodes cannot return to the pack. | **Firmware / bench rule and gate B11.** Never back-feed `+5V` while U101 is enabled. For back-powered tests, hold PWR_EN low or move R132 to GND. |
| V11-14 | MINOR | The T101 barrier keep-out existed only as description text. | **Fixed.** A rule area (no tracks, vias or pours, all copper layers, ±4.0 × ±3.4 mm) is now in the footprint. |
| N-01 … N-07 | NOTE | Confirmations: U101 pin check, independent loop calculation, VOUT / ripple / timing values, symbol-to-pad mapping, T101 polarity and 8.02 mm barrier gap, interface net set unchanged, LCSC numbers. N-05 also showed that the 6.55 mm T101 body length runs along the pin rows, so the "body vs 6.5 mm rule" owner question does not apply. | Noted; that owner question is closed. |
| N-08 | NOTE | AUX-only UVLO is about 7.1 V on / 4.4 V off (bench-only dropout behaviour). | **Text** added to the box-7 note. |
| N-09 | NOTE | Optional 100 k gate-source resistors on the FETs (gates held at about 0.7 V in Sleep). | Not applied; bring-up option. |
| N-10 | NOTE | R137 VIN filter 2.2 Ω (the datasheet example uses 4.7 Ω). | Not applied; value-only bring-up option. |
| N-11 | NOTE | TLV767 output capacitor ESR window 2–500 mΩ confirmed. | **Text**; open item closed. |
| N-12 | NOTE | Text inconsistencies (TVS clamp corners, R824 value), and no test pad on `01_U101_VCC`. | **Partly.** Clamp corners stated: 79 V at 25 °C, 84–87 V hot, ≈ 91 V at 96.8 V VC. A pad on `01_U101_VCC` was not added (owner option). |
