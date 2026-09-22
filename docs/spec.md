# EngiMind — Spec

## User story
As an engineer, I want to upload technical datasheets and ask questions about them, so that I get accurate answers backed by citations to the exact document and page.

## In scope (MVP)
- Upload documents in PDF and CSV format
- Ask a question about the uploaded documents
- Get back an answer with a citation (document name + page/row)
- If the documents don't contain the answer, say so instead of guessing

## Out of scope (for now)
- Frontend / UI
- AI agents and tool calling (calculator, external APIs, database queries)
- Auth / user accounts
- Multi-turn conversation (each question is answered independently)
- Generating output sheets or reports
- TXT file support (add later)

## Sample documents
- `ArduinoMega2560Rev3Datasheet.pdf`
- `ArduinoMegaPinReference.csv`

## Test questions

| # | Question | Expected answer | Source |
|---|----------|------------------|--------|
| 1 | What is the operating temperature range of the Arduino Mega 2560? | -40°C to +85°C | *Arduino Mega 2560 Rev3 Datasheet*, Section 2.1, page 6/34 |
| 2 | What is the output voltage of the Arduino Mega 2560? | +5V and +3.3V | *Arduino Mega 2560 Rev3 Datasheet*, Section 5.1, page 11/34 |
| 3 | How many PWM-capable pins does the Arduino Mega 2560 have? | 15 | `ArduinoMegaPinReference.csv` |
| 4 | How many digital I/O pins does the Arduino Mega 2560 have? | 54 | *Arduino Mega 2560 Rev3 Datasheet*, page 2/34 |
| 5 | How many analog input pins does the Arduino Mega 2560 have? | 16 | *Arduino Mega 2560 Rev3 Datasheet*, page 2/34 |
| 6 | What microcontroller does the Arduino Mega 2560 use? | ATmega2560 | *Arduino Mega 2560 Rev3 Datasheet*, page 2/34 |
| 7 | How does pin 17 of the Arduino Mega compare to pin 17 of the Arduino Nano? | Not enough information | — (no Nano document in the sample set) |

## Success criteria
- Correct answer **and** correct citation for at least 6 of the 7 test questions
- Question 7 (no answer available) correctly returns "not enough information" rather than a guess or an answer pulled from outside the documents
