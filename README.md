# GMX BC-250 Controller Wake (Rev 1.2)

Grumblymanx Mods — turns an AMD BC-250 (running Bazzite) **on** when you switch on an
**Xbox Series X|S controller**, using a Raspberry Pi **Pico W** or **Pico 2 W**.

The Pico stays powered from the ATX power supply's +5VSB standby line and listens for the
controller's Bluetooth LE broadcast. When it hears a saved controller it (optionally) switches
the power supply on via PS_ON, "presses" the BC-250 power button with a MOSFET, then waits for
the BC-250's "PC is on" signal (TPMS1 pin 9). The controller still connects to the BC-250 as normal.

> **Status:** firmware compiles cleanly for both boards but has **not yet been tested on real hardware**. The Pico shell has **not been test-printed yet**.

## Revisions
| Folder | What it is |
|---|---|
| `Rev 1.2/` | **Newest.** Install guide Rev 1.2: two completely separate install options (A: power supply always on, B: Pico switches the power supply), one step per page, a realistic picture for every step, page numbers for each option on the first page. Firmware Rev 1 (unchanged). Includes the 3D-printed Pico Shell. |
| `Rev 1.1/` | Previous: guide Rev 1.1 with BC-250 / ATX renders, firmware Rev 1, Pico Shell Rev 1. |

Inside `Rev 1.2/`:
| Folder | Contents |
|---|---|
| `Firmware/` | `GMX-BC250-Wake_Rev1_PicoW.uf2` (Pico W, RP2040) and `GMX-BC250-Wake_Rev1_Pico2W.uf2` (Pico 2 W, RP2350) |
| `Docs/` | Install guide (PDF) — start here, choose Option A or B on page 1. Also the Pico Shell print/assembly guide |
| `Renders/` | Every step picture (`S_A..` Option A, `S_B..` Option B, others shared) + BC-250 renders R1–R4 + Pico Shell pictures |
| `STL/`, `STEP/` | Pico Shell enclosure print and CAD files |
| `Source/` | Firmware source (Pico SDK 2.2.0 + BTstack), Pico Shell source, and the scripts that make the pictures and the guide |

## Optional PCB — GMX BC-250 Wake Board (+ 3D-printed shell)
A small board that replaces the perfboard build. The Pico W / Pico 2 W plugs into two 1x20 sockets;
BSS138LT1G MOSFETs (Q1, Q2), 1N5819WS diode (D1), resistors and the SW1 button are on the board;
outside wires solder to six labelled pads (J3–J8). Works for Option A and Option B (Option A: Q2, R2 and J5 not needed). Same firmware.

| Folder | What it is |
|---|---|
| `PCB/GMX-BC250-Wake-Board_Rev1.1/` | **Newest.** 70.5 × 43 mm board with 4 × M3 mounting holes, plus the 3D-printed **Wake Board Shell Rev 1** (Base, Button, 4 lids: GMX-Mods, Bazzite, BC-250, Blank) and its print/assembly guide |
| `PCB/GMX-BC250-Wake-Board_Rev1.0/` | Previous: 58 × 43 mm board, no mounting holes (does not fit the shell) |

Inside each PCB folder: `Gerbers/`, `BOM/`, `JLC_BOM/`, `CPL/`, `ibom/`, `Renders/`, `Docs/` (wiring diagrams, reports, shell guide), `Firmware/`, `Source/`; Rev 1.1 also has `STL/` and `STEP/` for the shell.

> The PCB and the shell have **not been ordered, printed or tested yet**.

## Pins (Pico GPIO)
GP2 power-button MOSFET · GP3 PS_ON MOSFET (Option B) · GP4 PC-on sense · GP5 optional button · GP6 optional LED · VSYS ← +5VSB through a Schottky diode

## Credits
Wake method from **dexikdex** (ESP32-BC250-LOP_PSU-PowerON-Xbox) and **GreatApo** (BC250_ESP32_ATX_PSU).
BC-250 details from **tfabris/BC-250** and the **elektricm amd-bc250-docs**. New Pico firmware written for this project.
