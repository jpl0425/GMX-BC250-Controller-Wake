# GMX BC-250 Controller Wake (Rev 1.1)

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
| `Rev 1.1/` | **Newest.** Guide Rev 1.1 with realistic renders (R1–R5) of the BC-250 solder points and the ATX 24-pin plug. Firmware unchanged (Rev 1). Also holds the 3D-printed **Pico Shell Rev 1** (fits Pico W and Pico 2 W; works with Rev 1 and Rev 1.1). |
| `Rev 1/` | First release: firmware Rev 1, guide with drawn BC-250/ATX pictures. |

Inside each revision folder:
| Folder | Contents |
|---|---|
| `Firmware/` | `GMX-BC250-Wake_Rev1_PicoW.uf2` (Pico W, RP2040) and `GMX-BC250-Wake_Rev1_Pico2W.uf2` (Pico 2 W, RP2350) |
| `Docs/` | Build, flash & install guide (PDF) — start here. (Rev 1.1) also `GMX-BC250-Pico-Shell_Rev1_Guide.pdf` (print + assembly) |
| `Diagrams/` | Wiring / overview / Pico pin pictures (PNG) + editable SVG sources |
| `Renders/` | (Rev 1.1) Realistic renders of the BC-250 power-button pad, ground pad, TPMS1 pin 9, AUTO_PWRON1 jumper and the ATX 24-pin plug; `Shell_*.png` = Pico shell pictures |
| `Source/` | Firmware source (Pico SDK 2.2.0 + BTstack) and the scripts that make the diagrams, renders and PDF. (Rev 1.1) `Source/pico-shell/` = CadQuery source for the Pico shell |
| `STL/` | (Rev 1.1) Pico Shell Rev 1 print files: one shared `Pico-Shell_Base.stl` + 4 lids (GMX-Mods logo, Bazzite, BC-250, Blank) |
| `STEP/` | (Rev 1.1) Pico Shell Rev 1 CAD files |

## Pins (Pico GPIO)
GP2 power-button MOSFET · GP3 PS_ON MOSFET (Option B) · GP4 PC-on sense · GP5 optional button · GP6 optional LED · VSYS ← +5VSB through a Schottky diode

## Credits
Wake method from **dexikdex** (ESP32-BC250-LOP_PSU-PowerON-Xbox) and **GreatApo** (BC250_ESP32_ATX_PSU).
BC-250 details from **tfabris/BC-250** and the **elektricm amd-bc250-docs**. New Pico firmware written for this project.
