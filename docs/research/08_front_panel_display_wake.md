# Research 08 — Front Panel OLED / LCD Display, Wake Switch & I2C Isolation (2026-11-25)

**Sources verified directly:**
* OLED & LCD component datasheets (`Wisevision X096`, `N096`, `Hansheng HS96L03W2C03` / `HS13L03W2C01` / `HS154L03W2C01`, `HS12864G12`) and live **JLCPCB / LCSC API** queries (`2026-11-25`).
* I2C isolator & buffer datasheets: **TI `ISO1540DR`** (`SLLSEB6`, `C179739`), **`TCA9517ADGKR`** (`ZHCSAM0B`, `C201698`), **`TCA4307DGKR`** (`ZHCSLQ0`, `C880333`), **`P82B96DGKR`** (`C2652360`), **`TPD4E05U06DQAR`** (`C138714`), **`PESD5V0S1BA`** (`C19224`), **`SMD0805P010TF`** (`C20975`).
* Sheet 08 design note & netlist: [`sheet08_io_front_panel.md`](../design/sheet08_io_front_panel.md) (`J801`, `U801/U802 TCA9539`, `SW802` / `WAKE_BTN_RAW`, `R801/R802 2.2 kΩ` on `EXP_SCL/SDA`).

---

## 1. Display Technology vs D-14 (−40…+85 °C & Long-Term Cabinet Life)

Stationary ESS rack doors and battery enclosures regularly sit powered 24/7 for 10+ years, often at **35–65 °C inside cabinets** (and design corner **−40…+85 °C** per D-14). Display choice must weigh cold startup, polarizer limit, and luminance half-life (`L50`):

| Part (LCSC) | Type & Controller | Active Size | Temp Rating (DS / JLC) | Rated L50 Lifetime (`25 °C` test) | Current Draw (Logic / Display) | Live Stock & Price (2026-11-25) | Verdict for ESS BMS |
|---|---|---|---|---|---|---|---|
| **`X096-2864KSWPG01-H30`** (`C18723026`, Wisevision) | **0.96" PMOLED** `128×64`, `SSD1315`, I2C | 21.74 × 11.18 mm | **−40…+85 °C** op & stor (DS p.8) | 10k h @110 cd/m² · 30k h @80 cd/m² · **50k h @60 cd/m²** | `160–220 µA` VDD + `27–32 mA` VBAT (`10 µA` sleep) | **345** JLC / **345** LCSC (`$1.97` JLC / `$1.67` @10) | **Best −40…+85 °C compact OLED**; use auto-off timer (`0xAE` sleep) |
| **`N096-2864KSWEG01-H30`** (`C2890596`, Wisevision) | **0.96" PMOLED** `128×64`, `SSD1306`, I2C/SPI | 21.74 × 10.86 mm | Table says −40…+85 °C, **rel. test 70 °C / polarizer 80 °C max** (DS p.9, 36) | 10k / 30k / 50k h | `180–300 µA` VDD (`5–10 µA` sleep) | **817** JLC / **817** LCSC (`$2.37` JLC) | Good second source if ≤ 70 °C door temp |
| **`HS96L03W2C03`** (`C5248080`, Hansheng) | 0.96" PMOLED I2C board-pin (`SSD1315`) | 21.74 × 10.86 mm | DS −40…+80 °C (JLC lists **−40…+70 °C**) | 10k / 30k / 50k h | `25.6–32 mA` VBAT | **2,379** JLC (`$2.13`) | High stock, but derated above 70–80 °C |
| **`HS13L03W2C01`** (`C7465997`, Hansheng) | **1.30" PMOLED** 4-pin (`SH1106`, I2C) | 29.42 × 14.70 mm | DS drawing −40…+80 °C / polarizer 80 °C (JLC lists **−40…+70 °C**) | 10k / 30k / 50k h | `35.6–44.5 mA` VCC (external) | **661** JLC / **497** LCSC (`$4.87` JLC / `$3.43` @100) | Best **readable 1.3" size** if front door ≤ 70–80 °C and panel sleeps between presses |
| **`HS154L03W2C01`** (`C7465999`, Hansheng) | **1.54" PMOLED** (`SSD1309`, I2C/SPI) | 35.05 × 17.52 mm | DS drawing −40…+80 °C (JLC lists **−40…+70 °C**) | **8k / 15k / 25k h** (shorter) | ~35–45 mA | **697** JLC / **683** LCSC (`$6.98` JLC / `$4.93` @100) | Shorter half-life & polarizer capped at 80 °C |
| **`HS12864G12`** (`C2939939`) | **2.4" Graphic FSTN LCD**, SPI (`ST7567`) | 48.6 × 24.9 mm | JLC no wide-temp guarantee (sibling `G18B` = −20…+70 °C) | **> 50,000+ h** (no organic burn-in) | ~1 mA + backlight | **16** JLC (`$3.90`) | **Low stock (16)**, SPI needs extra pins |

**Lifetime & Cold Summary:**
* Unlike nematic LCDs (which slow to >1 s response or freeze below −20 °C unless heated), **PMOLEDs work down to −40 °C cleanly with instant contrast**.
* However, organic emitters **degrade rapidly if left lit continuously at 60–85 °C** (`10,000 h = 1.1 yr` even at 25 °C for 110 cd/m²!). Therefore:
  1. **Mandatory firmware screen timeout (30–60 s idle → `0xAE` Display Off / Sleep, `< 15 µA`)**, woken by the front-panel wake button (`WAKE_BTN_RAW`) or fault event (`LED_ALM` stays on independently).
  2. With intermittent viewing (e.g. 15 min/day), even a 10,000 h OLED lasts **> 100 years** and avoids continuous polarizer self-heating.
  3. Recommended primary display: **`HS13L03W2C01` (1.3" SH1106, `C7465997`, 661 JLC)** for ergonomics if cabinet front stays ≤ 70–80 °C, OR **`X096-2864KSWPG01-H30` (`C18723026`, 345 JLC)** if true **−40…+85 °C** spec compliance is strictly audited.

---

## 2. Connector (`J801`) & Recommended Pinout

* **Connector Choice (already in Sheet 08 DNP):** **Molex PicoBlade `53261-0871`** (`C293349`, **44,538 pcs JLC / 44,535 LCSC**, `$0.28 @100`, **−40…+105 °C** verified, 1.25 mm pitch friction-locking SMD header, 1 A/pin). Meets `P-13` (−40 °C) with huge stock and prevents vibration back-out on cabinet doors.
* **Proposed 8-Pin Pinout vs Existing Sheet 08 (`J801`):** Sheet 08 currently wires `J801` as: `1: +5V (F801)`, `2: +3V3 (F802)`, `3: GND`, `4: EXP_SCL`, `5: EXP_SDA`, `6: WAKE_BTN_RAW`, `7: LED_ALM`, `8: GND`.
  - Notice `532610871` carries **`+5V`, `+3V3`, `EXP_SCL`, `EXP_SDA`, `WAKE_BTN_RAW`, `LED_ALM`, 2× `GND`** cleanly on 8 pins!
  - If using a 3.3 V OLED (`HS13L03W2C01` / `X096`), feed logic + DC/DC off **`+3V3` via `F802` (`100 mA PTC C20975`)**, leaving pin 1 (`+5V` via `F801`) spare or for an isolated side supply / buzzer / LED bar if needed.
  - **Optional Front-Panel Interrupt (`INT`) / Second Button:** To add a dedicated "Page/Scroll" button without adding pins, either multiplex it on the front-panel I2C or replace redundant pin 3/8 GND or pin 1 (`+5V` if unused) with `FP_BTN_PAGE` routed to one of the spare `U802 P15–P17` pins (`R831–R833`)! Keeping dual `GND` flanking I2C/power is still best practice for EMI/crosstalk — use a 10-pin PicoBlade (`53261-1071`) only if 2+ extra panel LEDs/buttons are required.

---

## 3. Cable Length, Bus Capacitance & Isolation Trade-Off

Currently on Sheet 08, **`EXP_SCL` / `EXP_SDA`** run at 3.3 V with **`2.2 kΩ` pull-ups (`R801`/`R802`)**, directly shared with on-board **`U801` / `U802` (`TCA9539`)**! Going off-board over a wire harness creates two concrete risks:

1. **Cable Capacitance & Stuck Bus (`I2C` reliability):**
   - Twisted-pair / ribbon harness adds ~50–100 pF/m. At `400 kHz` Fast Mode (`t_r ≤ 300 ns`), `R_PU = 2.2 kΩ` limits total bus capacitance to `C_b ≤ 300 ns / (0.8473 × 2200 Ω) ≈ 160 pF` (Sheet 08 §1 confirms `Cb ≤ 160 pF`), restricting unbuffered cables to **≤ 0.3–0.5 m** at 400 kHz (or **≤ 1.5 m** if dropped to **100 kHz**, where `t_r ≤ 1000 ns` allows ~530 pF).
   - **Critical safety coupling:** Because `J801` currently shares **`EXP_SCL/SDA`** directly with **`U801/U802`**, **a shorted wire or ESD upset on the door harness freezes both I/O expanders** — blocking `EN_12V`, `EN_ISO`, `EN_ESP`, `FAN_EN`, `DRY1/2`, and SOC LEDs!
   - **Minimum fix (even without isolation):** Add a **hot-swap / stuck-bus isolating buffer** like **`TCA4307DGKR`** (`C880333`, 7,370 JLC, `$3.09`, **−40…+125 °C**, automatic stuck-bus disconnect + recovery clock pulses, DS p.1) OR **`TCA9517ADGKR`** (`C201698`, 16,972 JLC, `$0.49`, −40…+85 °C) / **`P82B96DGKR`** (`C2652360`, 830 JLC, `$2.79`, up to `4,000 pF` / ~20 m cable)! Note: **`TCA9517A` and `P82B96` only isolate bus capacitance / stuck slaves on Side B (`TCA4307` disconnects stuck Side B automatically)** — they are **not galvanic barriers**.

2. **Galvanic Isolation (`ISO1540DR`) — Needed or Not?**
   - **Safety:** Not required for shock (pack ≤ 58.4 V SELV, same as BMS ground), so creepage is functional only.
   - **When Isolation IS Strongly Recommended (`> 0.5 m` cable or earthed metal cabinet door):** If the OLED/button panel mounts on an **earthed rack metal door** or sits **0.5–3 m** away near high-current inverter DC cables, `GND_PWR` reference shifts (`I × R` along negative busbar) and ESD strikes to the metal bezel inject transient current straight down `J801` GND into the STM32 ground plane.
   - **Cost of Isolated I2C (`+~$2.20/board`):**
     * **`ISO1540DR`** (`C179739`, 26,164 JLC / 23,122 LCSC, **`$0.87` JLC**, `2.5 kVrms`, `> 4 mm` creepage, **−40…+125 °C**, `1 MHz`, `3.5 mA` Side 1 / `35 mA` Side 2 sink, DS p.6–10). Side 1 `ICC1 ≤ 3.8 mA` (`3.3 V`), Side 2 `ICC2 ≤ 3.1 mA`.
     * **Isolated 3.3 V power to panel (~45 mA peak for OLED):** Either tap existing `+5V_ISO` if display shares `GND_ISO` (not ideal because comms ports leave the chassis), OR add a tiny dedicated isolated supply: **`B0503S-1W`** (`C512033`, 46 stock, `$0.91` — low stock) / **`SN6501QDBVRQ1`** (`C544575`, **2,860 JLC**, `$1.11`, −40…+125 °C) + small transformer, **plus an optocoupler (e.g. `LTV-217`) on `WAKE_BTN_RAW`** so wake works across the barrier when `+3V3` is OFF in `STORAGE`!
   - **When Un-Isolated Buffered I2C Wins (`≤ 0.5 m` internal/insulated bezel):** Keep `GND_PWR` to panel with:
     1. **`F802` (`100 mA` PTC `C20975`)** on `+3V3` + **`F801` (`C20975`)** on `+5V`.
     2. **`TPD4E05U06DQAR`** (`C138714`, 43,973 JLC, `$0.08`, 0.5 pF ultra-low C, `≤ 10 nA` leakage @ 5 V, −40…+125 °C) instead of `PESD5V0S1BA` (`35 pF` is higher C on I2C + higher 85 °C leakage on `WAKE_BTN_RAW`)!
     3. **`TCA4307DGKR`** (`C880333`) between internal `EXP_SCL/SDA` and `J801` (isolates door cable faults from crashing `U801/U802`!), plus `100 Ω` series resistors and `100 kHz` I2C clock for 1–1.5 m reach.

---

## 4. Recommended Sheet 08 Change List (Two Owner Options)

* **Option FP-1 (Recommended — Buffered, Non-Isolated Panel inside/on Insulated Door, `≤ 1.5 m`):**
  1. Fit **`J801` (`53261-0871` `C293349`)**, **`F801/F802` (`C20975`)**, replace `D814–D816` (`PESD5V0S1BA`) with **`TPD4E05U06DQAR` (`C138714`)** (`≤ 10 nA` leakage, `0.5 pF`), add **`100 Ω`** series resistors on `SCL/SDA` + `WAKE_BTN_RAW`.
  2. Insert **`TCA4307DGKR` (`C880333`)** between MCU/expander `EXP_SCL/SDA` and `J801` pins 4–5 (with dedicated `4.7 kΩ` pull-ups on `J801` side) so a harness short never locks `U801/U802` or kills power sequencing; run `I2C2` at `100 kHz`.
  3. Specify `HS13L03W2C01` (`C7465997`, 1.3" SH1106) or `X096-2864KSWPG01-H30` (`C18723026`, −40…+85 °C) off-board display module + 30–60 s firmware auto-sleep (`0xAE`).
* **Option FP-2 (Earthed Metal Door / Long Run `1.5–5 m`):**
  1. Fit **`ISO1540DR` (`C179739`)** + isolated `3.3 V` supply (`SN6501-Q1` + CT transformer or dedicated 1 W module) + **`LTV-217`** wake opto across the `J801` barrier + **`TPD4E05U06`** at connector.
