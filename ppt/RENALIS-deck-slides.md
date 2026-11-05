# RENALIS jury deck: build instructions (8 slides)

Virtual Jury Round, Friday 13 November 2026. The deck is used for the **5-minute presentation**, which comes after the 10-minute live demo. So it does not repeat the demo click by click. It covers the problem, the solution, why it is different, the results, the healthcare impact and the path to real use.

This file is written for Claude Code web to build the slides. After that, the owner screenshots each slide, makes the icons in GPT, and finishes the slides in Canva. Every icon slot below has a ready-to-use GPT prompt.

---

## 0. Rules for the builder (read first)

1. **Canvas:** 16:9, 1920 × 1080 px. All positions below are in pixels on this canvas: `x, y, w, h` from the top-left corner.
2. **Background:** plain white `#FFFFFF` on every slide. No background images, gradients or patterns. Colour comes only from panels, text accents and icons.
3. **Panels:** rounded rectangles, corner radius 18 px, border 2.5 px, white fill unless the slide says otherwise. Panels never touch: keep a 24 px gap between panels and a 48 px outer margin.
4. **Panel titles:** bold, ALL CAPS, 26 px, colour Forest, placed 20 px from the panel's top-left corner.
5. **Item style (the main pattern of this deck):** an icon slot on the left (72 × 72 px), then a **bold coloured lead phrase** on the first line (22 px, Green), then one or two plain sentences under it (19 px, Ink). Line height 1.3.
6. **Number tiles:** a big number (44 to 52 px, bold, Forest or Amber) with a short caption under it (17 px, Muted).
7. **Icon slots:** draw a 72 × 72 px light-grey placeholder square (`#F1F4EF`, radius 14 px) with the slot ID in small text, for example `ICON 2.3`. The owner replaces it with a GPT icon.
8. **Image slots:** draw a placeholder rectangle with a thin Line-coloured border and the file name written inside. The screenshots are in `ppt/deck-screens/`.
9. **Text:** use the text exactly as written. Do not add words, do not shorten sentences, and do not use em dashes. Use a normal dash "-" only.
10. **Fonts:** Poppins for everything. Titles in Poppins ExtraBold (800). Lead phrases in Poppins SemiBold (600). Body text in Poppins Regular (400).
11. **Header (same on slides 2 to 8):**
    - Team pill, top left: `x 48, y 36, w 210, h 58`, white fill, 2.5 px Forest border, fully rounded ends. Text "Sigmoid", 24 px bold, Forest, centred.
    - Slide title, centred: ALL CAPS, Poppins ExtraBold 64 px, colour Forest, centred at `y 64`.
    - Event box, top right: `x 1592, y 30, w 280, h 70`. Two lines, right-aligned: "Happiest Health" (24 px bold, Forest) and "Digital Twin Challenge 2026" (17 px, Green). The owner may paste the official event logo here in Canva.
    - Headline line: `x 48, y 122, w 1824, h 44`. It starts with a CAPS label in Green bold (for example "THE PROBLEM:"), followed by one sentence in Forest, 28 px semibold.
12. **Speaker notes:** paste each slide's "Speaker notes" into the notes field of that slide.

### Colour tokens (the same colours as the RENALIS app)

| Token | Hex | Use |
|---|---|---|
| Forest | `#133B2E` | Titles, panel titles, big numbers, pill borders |
| Green | `#2C7858` | Lead phrases, CAPS labels, main panel borders |
| Sage | `#6F8F5F` | Secondary borders, small labels |
| Lime | `#D4EDAA` | Highlight fills (our row, chips, key tiles) |
| Lime tint | `#F2F8E6` | Soft fill for number tiles and callouts |
| Amber | `#B4774C` | Warning words, "risk" numbers, limits |
| Amber tint | `#FBF1E8` | Fill for the limits / risks panels |
| Sky | `#65C9F1` | Small accents only (arrows, one chip per slide at most) |
| Ink | `#213C31` | Body text |
| Muted | `#7B877E` | Captions, sources |
| Line | `#E2E8E0` | Table lines, image borders |

### Icon style for GPT (use for every icon)

Paste this before each icon prompt:

> A single glossy 2.5D isometric icon, soft 3D look with gentle highlights and soft shadow, rounded friendly shapes, on a plain white background, no text, no letters. Colour palette: deep forest green #133B2E, medium green #2C7858, fresh lime #D4EDAA, warm amber #B4774C, with a small sky-blue #65C9F1 accent. Medical and clean, not cartoonish. Square image. Subject:

Then add the "Icon prompt" text from the slot.

### Screens the builder needs

Copy these into the slides as images. They are in `ppt/deck-screens/`:

| File | What it shows |
|---|---|
| `twin-min70.jpg` | Patient twin for Meera at minute 70: the 82% risk box, her record and the smartwatch heart rate |
| `step4-check.jpg` | Step 4: the suggested next check and "chance of backing the wrong cause: 50% → 8%" |
| `causebar-after.jpg` | The four-cause bar before and after one check |
| `whatif.jpg` | The "what if" panel: slowing the machine to 1,000 mL per hour takes the risk to 0% |
| `dots.jpg` | Real-data result: of every 100 drops, 60 warned in time |
| `step2-tanks.jpg` | The two water tanks: water out 1,150 mL per hour, refill about 890 |
| `hero.jpg` | The RENALIS home page |

---

## Slide 1 · TITLE

**Purpose:** say what RENALIS is in one look.

**Layout map (1920 × 1080):**

```
+------------------------------------------------------------------+
| [Sigmoid pill]                               [Happiest Health]    |
|                                                                    |
|  RENALIS (huge)                  +-----------------------------+   |
|  Warn before blood pressure      |                             |   |
|  falls. Then explain why.        |   HERO IMAGE SLOT           |   |
|  (one paragraph)                 |   (2.5D illustration)       |   |
|                                  +-----------------------------+   |
|  [chip] [chip] [chip] [chip]                                       |
|  +--------------------------------------------------------------+  |
|  | TEAM NAME        | DOMAIN / THEME                             |  |
|  | TEAM LEADER      | COLLEGE                                    |  |
|  +--------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

**Boxes:**

1. **Team pill:** same as the header rule, `x 48, y 36`. Text "Sigmoid".
2. **Event box:** same as the header rule, top right.
3. **Product name:** `x 80, y 170, w 900, h 170`. Text "RENALIS", Poppins ExtraBold 150 px, colour Forest, letter spacing 2 px.
4. **Tagline:** `x 80, y 340, w 900, h 140`. Two lines, Poppins ExtraBold 54 px. Line 1 "Warn before blood pressure falls." in Forest. Line 2 "Then explain why." in Green.
5. **Description:** `x 80, y 490, w 860, h 150`, 24 px, Ink:
   "A live digital twin of one dialysis patient. It learns her health record and past sessions, warns about half an hour before her blood pressure falls, shows the likely cause, and suggests the one quick check that would settle it. A doctor makes every decision."
6. **Hero image slot:** `x 1010, y 150, w 860, h 520`, rounded 24 px. Placeholder text "HERO ILLUSTRATION". Owner makes it in GPT with this prompt:
   > Glossy 2.5D isometric illustration, white background: a patient resting in a dialysis chair beside a dialysis machine, and next to them a translucent glowing digital copy of the same patient made of soft green light, with a small floating screen showing a blood pressure line dipping and a warning badge. Colours forest green #133B2E, green #2C7858, lime #D4EDAA, amber #B4774C, sky blue #65C9F1. Calm, clinical, friendly. No text.
7. **Four chips:** row at `y 680`, starting `x 80`, each `h 58`, gap 20 px, fully rounded, 2.5 px Green border, white fill, text 20 px bold Forest, ALL CAPS:
   - "WORKING PROTOTYPE" (w 300)
   - "PERSONAL DIGITAL TWIN" (w 340)
   - "TESTED ON REAL RECORDS" (w 360)
   - "EXPLAINS THE CAUSE" (w 300)
8. **Team panel:** `x 80, y 780, w 1760, h 250`, white, 2.5 px Sage border. Two columns, each with two label/value pairs. Labels 18 px CAPS Muted, values 28 px bold Forest:
   - Left column (`x 120`): "TEAM NAME" → "Team Sigmoid". "TEAM LEADER" → "Rehaan Ahmad Khan".
   - Right column (`x 980`): "DOMAIN / THEME" → "Healthcare Digital Twin - Dialysis Safety". "COLLEGE" → "JSS University, Noida".

**Speaker notes (about 15 seconds):**
"You have just seen RENALIS working. In the next five minutes I will cover the problem, what makes our approach different, what the tests show, and what it could change for patients in India."

---

## Slide 2 · PROBLEM STATEMENT

**Headline line:** "THE PROBLEM:" + "during dialysis, blood pressure can crash, and staff usually find out only after it happens."

**Layout map:**

```
+--------------------------------+  +------------------------------+
| WHAT HAPPENS TODAY             |  | EXISTING GAPS (table)        |
|  [icon] item 1                 |  |  Approach | Gives | Missing  |
|  [icon] item 2                 |  |  ...                         |
|  [icon] item 3                 |  |  RENALIS row (lime)          |
|  [icon] item 4                 |  +------------------------------+
+--------------------------------+  +------------------------------+
| [tile] [tile] [tile]           |  | WHY IT MATTERS               |
+--------------------------------+  |  [icon] [icon] [icon]        |
                                    +------------------------------+
```

**Boxes:**

1. **Panel "WHAT HAPPENS TODAY"**: `x 48, y 186, w 900, h 590`, 2.5 px Green border. Four items, each about 120 px tall, starting `y 250`:
   - ICON 2.1 · lead: "The machine removes water fast" · text: "Failed kidneys cannot remove extra water, so a dialysis machine pulls it out of the blood over about four hours."
     - Icon prompt: "a dialysis machine with a water droplet being drawn out through a tube"
   - ICON 2.2 · lead: "The body cannot always keep up" · text: "If water leaves the blood faster than the body refills it, blood pressure falls. Patients get dizzy, cramp or faint."
     - Icon prompt: "a blood pressure gauge with the needle dropping into an amber zone"
   - ICON 2.3 · lead: "Checks are spaced out" · text: "Blood pressure is often checked only every 30 minutes, so a fall is usually seen after it starts."
     - Icon prompt: "a blood pressure cuff next to a clock showing a 30-minute gap"
   - ICON 2.4 · lead: "The same fall has different causes" · text: "Low blood volume, loose blood vessels or a tired heart each need a different response, but they look the same on the monitor."
     - Icon prompt: "one downward arrow splitting into three paths, each ending in a different small organ symbol (blood drop, blood vessel, heart)"
2. **Three number tiles**: row inside one panel at `x 48, y 800, w 900, h 232`, 2.5 px Sage border, Lime tint fill. Three tiles side by side (each about w 280):
   - "138 million" (Forest) · "Indian adults had chronic kidney disease in 2023, the second-highest number in the world"
   - "7 in 100" (Amber) · "real dialysis sessions in a public hospital dataset had a drop to 90 or below"
   - "Most dangerous" (Amber, 40 px) · "a fall below 90 is the form most strongly linked with death"
   - Under the tiles, 14 px Muted: "Sources: GBD 2023, The Lancet. HEMOBP public dataset (our analysis of 18,420 sessions). Flythe et al. 2015, JASN."
3. **Panel "EXISTING GAPS"**: `x 972, y 186, w 900, h 470`, 2.5 px Green border. A table with a Forest header row (white text) and three columns: "Approach", "What it gives", "What is still missing". Rows:
   - "Cuff every 30 minutes" | "A reading" | "No warning ahead, no cause"
   - "Machine alarms" | "An alarm once pressure is already low" | "No lead time"
   - "Research risk scores" | "A risk percentage" | "No reason, no 'what if'"
   - **RENALIS** (row filled Lime, bold) | "A warning about 30 minutes ahead, the likely cause, and the next best check" | "Proof in real care: a study with a dialysis unit is our next step"
4. **Panel "WHY IT MATTERS"**: `x 972, y 680, w 900, h 352`, 2.5 px Sage border. Three items side by side, icon on top, lead and text under:
   - ICON 2.5 · lead: "Patients" · text: "Each crash is frightening and painful, and frequent drops below 90 are linked with a higher risk of death."
     - Icon prompt: "a patient in a dialysis chair holding their head, feeling dizzy, soft amber glow"
   - ICON 2.6 · lead: "Nurses" · text: "One nurse watches many chairs. A warning is only useful if it comes early."
     - Icon prompt: "a nurse looking at several dialysis chairs in a row"
   - ICON 2.7 · lead: "Treatment" · text: "A crash often means slowing or stopping the session, so less water is removed."
     - Icon prompt: "a dialysis session timer stopped early, with a water droplet left behind"

**Speaker notes (about 35 seconds):**
"About 138 million adults in India have chronic kidney disease. Many will need dialysis. During dialysis, a machine pulls water out of the blood. If it pulls faster than the body can refill, blood pressure crashes. In a public hospital dataset, this happened in about 7 of every 100 sessions. Today, staff usually see it only after it starts, and the same falling number can have different causes. Existing tools give a reading, an alarm or a risk score. None of them warns early and says why."

---

## Slide 3 · OUR SOLUTION

**Headline line:** "OUR SOLUTION:" + "a live copy of one patient that warns early, explains the cause, and suggests the next check."

**Layout map:**

```
+--------------------------------+  +------------------------------+
| HOW IT WORKS                   |  |  [twin-min70.jpg]            |
|  [icon] 1 Learn                |  |  caption                     |
|  [icon] 2 Predict              |  +------------------------------+
|  [icon] 3 Explain              |  +------------------------------+
|  [icon] 4 Suggest              |  | ONE SESSION, WORKED THROUGH  |
|                                |  |  minute 50 / 70 / 90 tiles   |
+--------------------------------+  +------------------------------+
| 1 LEARN -> 2 PREDICT -> 3 EXPLAIN -> 4 SUGGEST (flow strip)      |
+------------------------------------------------------------------+
```

**Boxes:**

1. **Panel "HOW IT WORKS"**: `x 48, y 186, w 860, h 640`, 2.5 px Green border. Four items:
   - ICON 3.1 · lead: "1. Learn her" · text: "It reads her health record (blood tests, medicines) and past sessions, and learns how fast her body refills the blood."
     - Icon prompt: "a medical record clipboard with a small blood test tube and a pill, connected to a glowing person outline"
   - ICON 3.2 · lead: "2. Predict" · text: "192 slightly different copies of her run forward in time. The risk is the share of copies whose pressure falls below 90 in the next 30 minutes."
     - Icon prompt: "many small translucent copies of a person fanning out into future lines on a chart"
   - ICON 3.3 · lead: "3. Explain" · text: "Four possible causes stay side by side: low blood volume, loose vessels, a tired heart, or a mix. Each says what happens next."
     - Icon prompt: "four coloured cards side by side, each with a small symbol: blood drop, blood vessel, heart, puzzle piece"
   - ICON 3.4 · lead: "4. Suggest" · text: "It picks the one quick check that would best tell the causes apart, and shows what the check is worth."
     - Icon prompt: "a magnifying glass over a small medical sensor, with a green tick"
2. **Image slot** `twin-min70.jpg`: `x 932, y 186, w 940, h 470`, rounded 16 px, 2 px Line border. Caption under it (16 px Muted): "Live screen: Meera at minute 70. Her pressure still reads 111, but the twin gives an 82% chance of a fall within 30 minutes."
3. **Panel "ONE SESSION, WORKED THROUGH"**: `x 932, y 676, w 940, h 236`, 2.5 px Sage border, Lime tint fill. Three tiles in a row with a thin arrow between them:
   - "Minute 50" → big "0%" (Forest) → "All looks calm."
   - "Minute 70" → big "82%" (Amber) → "Pressure still looks normal. The twin warns 28 minutes ahead."
   - "Minute 90" → big "100%" (Amber) → "Pressure is now falling. The warning was right."
4. **Flow strip**: `x 48, y 850, w 860, h 182`, no border, four small rounded boxes (each w 190, h 120, Lime fill, Forest text 20 px bold) joined by Green arrows: "LEARN", "PREDICT", "EXPLAIN", "SUGGEST". Under the strip (16 px Muted): "A doctor approves every action. Nothing changes a real machine."

**Speaker notes (about 35 seconds):**
"RENALIS does four things. It learns the patient from her record and past sessions. It predicts, using 192 slightly different copies of her that run forward in time. It explains, by keeping four possible causes side by side. And it suggests the one check that would settle which cause is right. In the demo, Meera's pressure still looked normal at minute 70, but the twin warned 28 minutes before it fell."

---

## Slide 4 · TECH STACK AND FLOW

**Headline line:** "HOW IT'S BUILT:" + "a physics-based body model and a cause lab, fed by the record and live readings, behind a strict time check."

**Layout map:**

```
+-------------------------------------------+  +------------------+
| DATA FLOW (diagram)                        |  | TECHNOLOGY STACK |
|  [Record] [Past sessions]   [Cuff][Machine]|  |  [icon] rows     |
|        \       |              |   [Watch] |  +------------------+
|         +--> [TIME CHECK] <---+           |  +------------------+
|                 |                          |  | WHY THESE        |
|        [PATIENT TWIN] [CAUSE LAB]          |  | CHOICES          |
|                 |                          |  |  [icon] x3       |
|          [DOCTOR'S SCREEN]                 |  +------------------+
+-------------------------------------------+
| [tile] [tile] [tile] [tile] [tile]                                |
+------------------------------------------------------------------+
```

**Boxes:**

1. **Panel "DATA FLOW"**: `x 48, y 186, w 1150, h 640`, 2.5 px Green border, dashed 2 px Sage inner groups.
   - Group "PATIENT HISTORY" (dashed, `x 80, y 250, w 520, h 170`): two boxes, "Health record" (sub: "albumin, diagnoses, medicines") and "Past sessions" (sub: "blood pressure, water removed").
   - Group "LIVE SESSION" (dashed, `x 640, y 250, w 520, h 170`): three boxes, "Cuff" (sub: "blood pressure"), "Dialysis machine" (sub: "water removal speed"), "Smartwatch" (sub: "heart rate").
   - Centre box, Forest fill, white text: "TIME CHECK" with sub "only what was known at that minute" (`x 430, y 455, w 400, h 80`). Arrows from both groups into it.
   - Two boxes under it, side by side (`y 575`, each w 400, h 100, Lime fill): "PATIENT TWIN" (sub: "192 copies of her, two-tank water model") and "CAUSE LAB" (sub: "4 causes × 48 copies each").
   - Bottom box (`x 430, y 720, w 400, h 80`, white, 2.5 px Forest border): "DOCTOR'S SCREEN" (sub: "risk, cause, what-if, full log"). Arrow from both boxes above.
   - Small side tag next to the doctor's screen, Amber text: "The doctor decides. Nothing changes a real machine."
2. **Panel "TECHNOLOGY STACK"**: `x 1222, y 186, w 650, h 430`, 2.5 px Green border. Six rows, each a small icon (48 px) + bold name + plain text, 19 px:
   - ICON 4.1 "Website:" React, TypeScript, Vite, Recharts
   - ICON 4.2 "Model and API:" Python, FastAPI, NumPy (particle filter written from scratch)
   - ICON 4.3 "Real-data test:" pandas, scikit-learn (gradient-boosted trees)
   - ICON 4.4 "Storage:" SQLite, every reading kept, never erased
   - ICON 4.5 "Hospital format:" FHIR R4 export
   - ICON 4.6 "Hosting:" Vercel (website), Hugging Face Spaces (API)
   - Icon prompts: 4.1 "a browser window with a small chart", 4.2 "a gear made of tiny dots, like particles", 4.3 "a hospital building with a small bar chart", 4.4 "a database cylinder with a lock", 4.5 "two hospital systems linked by a document arrow", 4.6 "a cloud with two small server boxes"
3. **Panel "WHY THESE CHOICES"**: `x 1222, y 636, w 650, h 396`, 2.5 px Sage border. Three items:
   - ICON 4.7 · lead: "A body model, not only a black box" · text: "It can explain why pressure falls and test 'what if', which a plain risk score cannot."
     - Icon prompt: "two water tanks connected by a pipe, inside a soft human outline"
   - ICON 4.8 · lead: "A strict time check" · text: "The twin can never peek at future readings, so the demo cannot cheat."
     - Icon prompt: "a clock with a shield in front of it"
   - ICON 4.9 · lead: "Runs on a normal computer" · text: "No GPU and no paid AI service. It can run on a hospital's own server."
     - Icon prompt: "a simple desktop computer with a green tick, no graphics card"
4. **Number tiles row**: `x 48, y 850, w 1150, h 182`, Lime tint fill, 2.5 px Sage border, five tiles:
   - "192" · "copies of the patient in the twin"
   - "4" · "possible causes compared"
   - "3" · "live data streams"
   - "59" · "automatic tests on every change"
   - "0" · "future readings ever used"

**Speaker notes (about 30 seconds):**
"Two kinds of data feed one virtual patient: her history, meaning the record and past sessions, and the live session, meaning the cuff, the machine and a smartwatch. A strict time check makes sure the twin only sees what was known at that minute. The patient twin and the cause lab then feed the doctor's screen. It is built in Python and React, runs on a normal computer, and every change runs 59 automatic tests."

---

## Slide 5 · OUR USP

**Headline line:** "WHAT MAKES IT DIFFERENT:" + "others predict a number. RENALIS learns the patient, explains the cause, and asks for the right check."

**Layout map:**

```
+-------------------------------+  +-------------------------------+
| COMPARISON TABLE              |  | 1 [icon] It is personal        |
|  Typical warning | RENALIS    |  | 2 [icon] It explains the cause |
|  ...6 rows                    |  | 3 [icon] It asks for the check |
|                               |  | 4 [icon] It shows its limits   |
+-------------------------------+  +-------------------------------+
| [step4-check.jpg]             |  | [causebar-after.jpg]          |
+-------------------------------+  +-------------------------------+
```

**Boxes:**

1. **Comparison table**: `x 48, y 186, w 900, h 520`. Two columns. Left header "Typical warning tools" (Sage fill, white text). Right header "RENALIS" (Forest fill, Lime text). Right column cells bold, Forest text, Lime tint fill. Rows:
   - "Same rule for every patient" | "Learns her record and past sessions"
   - "A risk number only" | "A risk number and the likely cause"
   - "Silent about what to do" | "Suggests the one check that settles it"
   - "Cannot test changes" | "Tests 'what if the machine went slower'"
   - "Black box" | "Every reading and reason is logged and can be checked"
   - "Claims accuracy" | "Shows what worked and what did not"
2. **Four numbered USP boxes**: right column `x 972, y 186, w 900`, four boxes each `h 118`, gap 16 px, 2.5 px Green border. Each has a number circle (Lime fill, Forest number), an icon slot, a bold lead and one sentence:
   - 1 · ICON 5.1 · "It is personal" · "Her low albumin and past sessions change her starting point, so she is not treated as average."
     - Icon prompt: "a fingerprint inside a heart-shaped outline"
   - 2 · ICON 5.2 · "It explains the cause" · "Four causes compete in the open, and the screen shows which fits best and why."
     - Icon prompt: "four small coloured bars with one glowing taller than the rest"
   - 3 · ICON 5.3 · "It asks for the right check" · "One check cut the chance of backing the wrong cause from 50% to 8% in the demo."
     - Icon prompt: "a medical sensor clip on a finger with a small target symbol"
   - 4 · ICON 5.4 · "It is honest by design" · "No future data, no warning when pressure is already low, and every limit is on screen."
     - Icon prompt: "a shield with a check mark and a small eye symbol"
3. **Image slot** `step4-check.jpg`: `x 48, y 730, w 900, h 302`, rounded 16 px, 2 px Line border. Caption on the image's bottom edge (white pill, 15 px): "The suggested check, and what it is worth."
4. **Image slot** `causebar-after.jpg`: `x 972, y 730, w 900, h 302`, rounded 16 px, 2 px Line border. Caption: "After one check, two causes are almost ruled out."

**Speaker notes (about 35 seconds):**
"What makes RENALIS different? Typical tools apply one rule to everyone and give a number. RENALIS learns the patient. It keeps four causes in the open and shows which one fits. It asks for the one check that would settle it: in the demo, one check cut the chance of backing the wrong cause from 50 percent to 8 percent. And it is honest by design: it never uses future data, and its limits are on the screen."

---

## Slide 6 · RESULTS

**Headline line:** "TESTED ON REAL RECORDS:" + "176 patients it had never seen, from a public hospital dataset. Here is where it stands."

**Layout map:**

```
+-------------------------------+  +-------------------------------+
| WARNINGS ON REAL DATA         |  | IN CONTEXT                    |
|  [dots.jpg]                   |  |  [tile] 5.8x vs 5.4x          |
|  60 of 100 drops warned       |  |  [tile] 76% sessions          |
|                               |  |  [tile] 1 per 7 hours         |
+-------------------------------+  +-------------------------------+
| WHAT WE IMPROVED THIS WEEK (3 items in a row)                    |
+------------------------------------------------------------------+
| BUILT AND WORKING | TESTED ON REAL DATA | NEXT TO PROVE          |
+------------------------------------------------------------------+
```

**Boxes:**

1. **Panel "WARNINGS ON REAL DATA"**: `x 48, y 186, w 900, h 420`, 2.5 px Green border. Image slot `dots.jpg` inside (`w 840, h 270`). Under it, 20 px:
   "**60 of every 100 real drops** were warned in time. **15 of every 100 warnings** were right. Drops are rare, so most warnings are still false alarms, and we show that openly."
2. **Panel "IN CONTEXT"**: `x 972, y 186, w 900, h 420`, 2.5 px Green border, three stacked tiles (Lime tint fill, each h 112):
   - "5.8×" (Forest, 52 px) · "A RENALIS warning is 5.8 times more likely to be right than a random one. The best comparable published system: 5.4 times (Zhang et al. 2023)."
   - "76%" (Forest) · "of real sessions with a drop got a warning first."
   - "1 per 7 h" (Forest) · "about one warning every 7 hours of dialysis, so it does not flood the nurse."
3. **Panel "WHAT WE IMPROVED THIS WEEK"**: `x 48, y 630, w 1824, h 210`, 2.5 px Sage border. Three items side by side:
   - ICON 6.1 · lead: "13% fewer false alarms" · text: "Five facts hospitals already record, like weight gained since the last session, sharpened the warning."
     - Icon prompt: "a bell with a small downward arrow and a green tick"
   - ICON 6.2 · lead: "The twin now matches the simple method" · text: "Corrected using training patients only, its forecast on real records is level with repeating the last reading, and it can also explain why."
     - Icon prompt: "two lines on a chart meeting and running together, one green, one grey"
   - ICON 6.3 · lead: "Smarter checks now win" · text: "On 384 new test cases, a more careful planner made 9% smaller mistakes than just re-checking blood pressure."
     - Icon prompt: "a checklist with a small brain symbol and an upward arrow"
4. **Bottom strip, three columns**: `x 48, y 864, w 1824, h 168`. Three boxes side by side (each w 592):
   - "BUILT AND WORKING" (Green border, tick icon ICON 6.4): "Live twin, cause lab, next-check planner, what-if, full log, FHIR export."
   - "TESTED ON REAL DATA" (Green border, ICON 6.5): "Forecast and warnings on HEMOBP: 563 patients to learn, 141 to tune, 176 to test, no overlap."
   - "NEXT TO PROVE" (Amber border, Amber tint fill, ICON 6.6): "Lab and heart-rate inputs on real patients, and benefit in real care. Both need a hospital study."
   - Icon prompts: 6.4 "a green check mark badge", 6.5 "a hospital folder with a magnifying glass", 6.6 "a stethoscope with a small calendar"

**Speaker notes (about 45 seconds):**
"We tested on real dialysis records from a public dataset, on 176 patients the model had never seen. It warned in time for 60 percent of real drops. 15 percent of its warnings were right. That sounds low, but drops are rare. A RENALIS warning is 5.8 times more likely to be right than chance, slightly better than the best comparable published system. This week we cut false alarms by 13 percent, brought the twin level with the simple method on real records, and a more careful planner now beats plain re-checking on new test cases. What we still need to prove is benefit in real care, which needs a hospital study."

---

## Slide 7 · HEALTHCARE IMPACT

**Headline line:** "THE IMPACT:" + "half an hour of warning turns a crash into a calm adjustment."

**Layout map:**

```
+------------------------------------------------------------------+
| ONE SESSION, TWO WAYS (two timelines)                            |
|  TODAY:    ---- reading ---- reading ---- CRASH ---- stop early   |
|  RENALIS:  ---- warning (28 min ahead) -- slow machine -- safe    |
+------------------------------------------------------------------+
| [icon] Patients | [icon] Nurses | [icon] Doctors | [icon] India   |
+------------------------------------------------------------------+
| [tile 28 min] [tile 82% -> 0%] [tile 50% -> 8%] [tile 1 per 7 h] |
+------------------------------------------------------------------+
```

**Boxes:**

1. **Panel "ONE SESSION, TWO WAYS"**: `x 48, y 186, w 1824, h 330`, 2.5 px Green border. Two horizontal timelines, each a thick line (8 px, rounded) from `x 300` to `x 1820` with labelled dots:
   - Row 1 at `y 290`, label on the left "TODAY" (Amber, 26 px bold). Line colour Line grey. Dots: "Reading looks fine" (grey), "Reading looks fine" (grey), "Pressure crashes" (Amber dot, larger, ICON 7.1 above it), "Session stopped early" (Amber).
     - ICON 7.1 prompt: "a red-amber lightning bolt hitting a small blood pressure gauge"
   - Row 2 at `y 430`, label "RENALIS" (Green, 26 px bold). Line colour Green. Dots: "Warning, 28 minutes ahead" (Lime dot with Forest border, ICON 7.2 above), "Nurse slows the machine" (Lime), "Pressure stays up" (Green), "Water target kept" (Green).
     - ICON 7.2 prompt: "a calm bell with a small clock showing 28 minutes"
   - Small note at bottom right of the panel (15 px Muted): "Based on the demo patient Meera. A hospital study is needed to measure this in real care."
2. **Four "who benefits" boxes**: row at `y 540`, each `w 444, h 250`, gap 16 px, 2.5 px Sage border. Each has an icon (72 px), a bold lead and two short sentences:
   - ICON 7.3 · "Patients" · "Fewer sudden crashes, cramps and fainting. Safer, fuller sessions."
     - Icon prompt: "a smiling patient relaxed in a dialysis chair with a small green heart"
   - ICON 7.4 · "Nurses" · "A heads-up half an hour early. One clear check to do, not guesswork."
     - Icon prompt: "a nurse holding a tablet with a small bell notification"
   - ICON 7.5 · "Nephrologists" · "The likely cause, a 'what if' for the machine setting, and a full log to review."
     - Icon prompt: "a doctor looking at a screen with four coloured bars"
   - ICON 7.6 · "India's dialysis units" · "Runs on a normal computer with the machines units already have."
     - Icon prompt: "a small Indian clinic building with a dialysis machine symbol and a green cross"
3. **Four number tiles**: row at `y 814`, each `w 444, h 218`, Lime tint fill, 2.5 px Green border:
   - "28 min" · "warning before the fall, while pressure still looked normal (demo)"
   - "82% → 0%" · "risk after slowing the machine from 1,150 to 1,000 mL per hour (demo)"
   - "50% → 8%" · "chance of backing the wrong cause, after one check (demo)"
   - "1 per 7 h" · "warnings on real records, so alerts stay rare enough to act on"

**Speaker notes (about 40 seconds):**
"Here is the healthcare impact. Today, the readings look fine until the pressure crashes, and the session is often stopped early. With RENALIS, the nurse gets about half an hour of warning. In the demo, slowing the machine a little took Meera's risk from 82 percent to almost zero, for only 75 millilitres more water left for later. Patients get safer and fuller sessions. Nurses get one clear check to do. Doctors get the reason and a full log. And because it runs on a normal computer, it can fit dialysis units across India."

---

## Slide 8 · FEASIBILITY, VIABILITY & SCALE

**Headline line:** "READY FOR THE NEXT STEP:" + "built and tested, cheap to run, and a clear path into a real dialysis unit."

**Layout map:**

```
+------------------------+ +------------------------+ +------------------+
| WHERE IT STANDS        | | RISKS AND HOW WE       | | WHAT IT TAKES     |
|  Built / Tested / Next | | ANSWER THEM (table)    | | TO RUN            |
+------------------------+ +------------------------+ +------------------+
| PATH TO ADOPTION: Phase 1 -> Phase 2 -> Phase 3 (three boxes + arrows)  |
+-------------------------------------------------------------------------+
```

**Boxes:**

1. **Panel "WHERE IT STANDS"**: `x 48, y 186, w 600, h 500`, 2.5 px Green border. Three sub-blocks, each with a small coloured label:
   - "BUILT AND WORKING" (Green label, tick icon ICON 8.1): "Live twin, cause lab, next-check planner, what-if, full log, FHIR export, 59 automatic tests."
   - "TESTED" (Green label, ICON 8.2): "Real hospital records (176 unseen patients) and 576 hard simulated cases."
   - "NEXT TO PROVE" (Amber label, ICON 8.3): "Benefit for real patients, and the lab and heart-rate inputs on real data."
   - Icon prompts: 8.1 "a green check badge", 8.2 "a test tube with a bar chart", 8.3 "a hospital with a small flag"
2. **Panel "RISKS AND HOW WE ANSWER THEM"**: `x 672, y 186, w 760, h 500`, 2.5 px Green border. Table, header row Forest with white text, columns "Risk" and "How we answer it":
   - "Too many false alarms" | "Warnings are 5.8 times better than chance, and the line is set by doctors. Stricter settings are already tested."
   - "Made-up demo patients" | "Allowed by the challenge. The forecast is also tested on real records."
   - "Lab and heart-rate rules" | "Each rule is backed by a study or labelled as our assumption on screen."
   - "Trusting a model too much" | "It shows its reasons, never changes a machine, and a doctor decides."
3. **Panel "WHAT IT TAKES TO RUN"**: `x 1456, y 186, w 416, h 500`, 2.5 px Sage border. Five short rows with small icons (48 px):
   - ICON 8.4 "One small server, no GPU" · prompt: "a small server box with a leaf"
   - ICON 8.5 "Free and open-source tools" · prompt: "an open box with a heart"
   - ICON 8.6 "Opens in any web browser" · prompt: "a browser window with a green tick"
   - ICON 8.7 "Reads the cuff, the machine and the record" · prompt: "three small devices joined by lines"
   - ICON 8.8 "Exports in FHIR hospital format" · prompt: "a document with a hospital cross and an arrow"
4. **Panel "PATH TO ADOPTION"**: `x 48, y 710, w 1824, h 322`, 2.5 px Green border. Three phase boxes (each `w 560, h 230`, Lime tint fill) with Green arrows between them:
   - ICON 8.9 · "Phase 1: Silent study" · "One Indian dialysis unit. RENALIS reads the real data but shows nothing to staff, so we measure its accuracy safely." · Amber italic line: "A study protocol is already drafted. Ethics approval comes first."
     - Icon prompt: "a dialysis unit with a small eye symbol and a lock"
   - ICON 8.10 · "Phase 2: Nurse pilot" · "Warnings shown to nurses on a few chairs. We measure crashes, early stops and alarm load." · Amber italic line: "Doctors set the warning line."
     - Icon prompt: "a nurse at a dialysis chair with a tablet showing a green bell"
   - ICON 8.11 · "Phase 3: Scale" · "More units, more patient types, and plug-in support for common dialysis machines." · Amber italic line: "Each new unit needs data, not new code."
     - Icon prompt: "three connected clinic buildings with a small map of India in the background"

**Speaker notes (about 40 seconds):**
"Where are we? The prototype is built and working, and tested on real records and hundreds of hard simulated cases. It runs on one small server with free tools, so it is cheap to run. The main risk is false alarms, and the line is set by doctors. Our path is clear. First, a silent study in an Indian dialysis unit, where RENALIS reads real data but shows nothing to staff. Then a small nurse pilot. Then scale. Thank you. I am happy to take your questions."

---

## Timing check (5 minutes)

| Slide | Seconds |
|---|---|
| 1 Title | 15 |
| 2 Problem | 35 |
| 3 Solution | 35 |
| 4 Tech | 30 |
| 5 USP | 35 |
| 6 Results | 45 |
| 7 Impact | 40 |
| 8 Feasibility | 40 |
| **Total** | **275 s, about 4 min 35 s, leaving 25 s spare** |

## Sources for every number on the slides

- 138 million Indian adults with CKD in 2023: GBD 2023 Chronic Kidney Disease Collaborators, The Lancet, doi 10.1016/S0140-6736(25)01853-7.
- 7 in 100 sessions with a drop to 90 or below: our analysis of the HEMOBP public dataset (Lin et al. 2019, Scientific Data, doi 10.1038/s41597-019-0319-8), 1,345 of 18,420 test sessions. File `docs/warnings-v05.json`.
- A fall below 90 most strongly linked with death: Flythe et al. 2015, JASN, doi 10.1681/ASN.2014020222.
- Blood pressure every 30 minutes: Lin et al. 2019 (HEMOBP data description).
- 60%, 15%, 5.8×, 76%, 1 per 7 h, 13% fewer false alarms: `docs/warnings-v05.json`.
- 5.4× comparison: Zhang et al. 2023, Nephrology Dialysis Transplantation, doi 10.1093/ndt/gfad070.
- Twin level with the simple method: `docs/twin-hemobp.json` (12.2 vs 12.2 average miss).
- 9% smaller mistakes on 384 new cases: `docs/policy-validation-v05.json`.
- 82%, 28 min, 82% → 0%, 50% → 8%: the live demo, patient Meera (RNL-014), minute 70 and 90.
- 59 automatic tests: `tests/` folder.
