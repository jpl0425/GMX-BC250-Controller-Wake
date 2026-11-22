# GMX BC-250 Controller Wake (Rev 1)

Grumblymanx Mods — turns an AMD BC-250 (running Bazzite) **on** when you switch on an
**Xbox Series X|S controller**, using a Raspberry Pi **Pico W** or **Pico 2 W**.

The Pico stays powered from the ATX power supply's +5VSB standby line and listens for the
controller's Bluetooth LE broadcast. When it hears a saved controller it (optionally) switches
the power supply on via PS_ON, "presses" the BC-250 power button with a MOSFET, then waits for
the BC-250's "PC is on" signal (TPMS1 pin 9). The controller still connects to the BC-250 as normal.

> **Status:** firmware compiles cleanly for both boards but has **not yet been tested on real hardware**.

## Folders
| Folder | Contents |
|---|---|
| `Firmware/` | `GMX-BC250-Wake_Rev1_PicoW.uf2` (Pico W, RP2040) and `GMX-BC250-Wake_Rev1_Pico2W.uf2` (Pico 2 W, RP2350) |
| `Docs/` | Build, flash & install guide (PDF) — start here |
| `Diagrams/` | Wiring pictures (PNG) + editable SVG sources |
| `Source/firmware/` | Pico SDK 2.2.0 + BTstack source code, CMakeLists, build notes |
| `Source/docs-tools/` | Scripts that generate the diagrams and the PDF |

## Pins (Pico GPIO)
GP2 power-button MOSFET · GP3 PS_ON MOSFET (Option B) · GP4 PC-on sense · GP5 optional button · GP6 optional LED · VSYS ← +5VSB through a Schottky diode

## Credits
Wake method from **dexikdex** (ESP32-BC250-LOP_PSU-PowerON-Xbox) and **GreatApo** (BC250_ESP32_ATX_PSU).
BC-250 details from **tfabris/BC-250** and the **elektricm amd-bc250-docs**. New Pico firmware written for this project.
