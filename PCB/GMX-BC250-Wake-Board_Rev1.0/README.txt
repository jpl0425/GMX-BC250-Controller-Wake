GMX BC-250 Wake Board - Rev 1.0  (GMX Mods)
============================================

A small PCB that replaces the perfboard build of the GMX BC-250 Controller Wake
project. A Raspberry Pi Pico W or Pico 2 W plugs into two 1x20 sockets on the board.
Same firmware as the Controller Wake project (Firmware folder) - no changes.

Board: 58 x 43 mm, 2 layers, ground pour both sides.
Outside wires solder to 6 labelled wire pads along the top edge (J3-J8).
Works for Option A (power supply always on) and Option B (Pico switches the supply).
For Option A, Q2 and R2 can be left off and J5 stays empty.

FOLDERS
  Gerbers   Gerber + drill zip - upload this to JLCPCB to order the bare board
  BOM       full parts list with LCSC numbers
  JLC_BOM   BOM in JLCPCB's format (SMD parts only) - only if JLCPCB fits the parts
  CPL       placement file for JLCPCB (SMD parts only) - only if JLCPCB fits the parts
  ibom      interactive BOM - open in a web browser while hand-soldering
  Renders   pictures of the board: bare, with parts, with the Pico
  Docs      wiring diagrams (Option A, Option B), DRC report, cross-check report
  Firmware  .uf2 files: PicoW for a Pico W, Pico2W for a Pico 2 W
  Source    KiCad 7 board, footprint libraries and the scripts that build everything

PARTS
  Q1, Q2  BSS138LT1G      SOT-23   LCSC C82045
  R1, R2  10k 0603        YAGEO RC0603FR-0710KL   LCSC C98220
  R3      1k 0603         YAGEO RC0603FR-071KL    LCSC C22548
  D1      1N5819WS        SOD-323  LCSC C191023
  SW1     TS-1187A-B-A-B  5.1 x 5.1 mm SMD button  LCSC C318884
  J1, J2  female socket 1x20, 2.54 mm  ZHOURI PM2.54-1*20  LCSC C5224030
          (alternative: BOOMELE 2.54-1*20P, LCSC C50984)
  Q2 and R2: Option B only.

ORIENTATION
  D1: the band on the part goes toward the right edge of the board (silkscreen bar).
  Q1, Q2: the dot on the silkscreen marks the gate (pin 1).
  Pico: parts side up, USB end at the right edge ("Pin 1" is printed on the board).
