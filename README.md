# valve-control

Use Arduino Uno to control solenoid valves.  
Follow the steps below to set up your own valve control station.

## Purchase

### Solenoid Valves

* [Clippard, E310C-2C012, 10 mm N-C 3-way Valve, In-line Connector w/LED, 0.030" Orifice, 1.3W, 12 VDC](http://www.clippard.com/part/E310C-2C012)
* [Valve connector cable](http://www.clippard.com/products/electronic-valve-10mm-connector)
* [Manifold](http://www.clippard.com/products/electronic-valve-10mm-manifolds)

Details can be found on page 215-221 in [Clippard Full-line Catalog](http://www.clippard.com/downloads/PDF_Documents/Clippard%20Full%20Line%20Catalog/Clippard%20Full-Line%20Catalog.pdf)

### Send [PCB design](https://github.com/GNHua/valve-control/raw/master/pcb_layout/plots.zip) Out For Manufacturing

* Highly recommend [JLCPCB](https://jlcpcb.com/). Fabrication and shipping took ~1 week for me in the U.S.
* If you choose JLCPCB, go [here](https://jlcpcb.com/quote), upload [plots.zip](pcb_layout/plots.zip), and leave everything else as default.
* If you have access to a PCB baking oven, buying a SMT-Stencil will save you a lot of time for soldering. If not, all the components can still be soldered by hand.

| Top Layer | Bottom Layer |
| --------- | ------------ |
| <img src="https://github.com/GNHua/valve-control/raw/master/pcb_layout/top.png" width="400"> | <img src="https://github.com/GNHua/valve-control/raw/master/pcb_layout/bottom.png" width="400"> |

### Electrical Components To Buy

| Part | Label on PCB | Qty. (per PCB) | Purchase |
| ---- | :----------- | :------------: | :------: |
| [Shift register, SN74HC595N](https://www.digikey.com/product-detail/en/texas-instruments/SN74HC595N/296-1600-5-ND/277246?utm_adgroup=Integrated%20Circuits&slid=&gclid=Cj0KCQjwzK_bBRDDARIsAFQF7zN5-LHxIfRLcNVY-gf6gJ_lS_RSs-WGzMVOjYGovQlShfyqFOsZDr0aAqcmEALw_wcB) | plug on the DIP socket (U1) | 1 | [link](https://www.digikey.com/product-detail/en/texas-instruments/SN74HC595N/296-1600-5-ND/277246?utm_adgroup=Integrated%20Circuits&slid=&gclid=Cj0KCQjwzK_bBRDDARIsAFQF7zN5-LHxIfRLcNVY-gf6gJ_lS_RSs-WGzMVOjYGovQlShfyqFOsZDr0aAqcmEALw_wcB)
| [Optoisolator, HCPL 2731](https://www.digikey.com/product-detail/en/on-semiconductor/HCPL2731/HCPL2731QT-ND/31642) | plug on the DIP sockets (U2-U5) | 4 | [link](https://www.digikey.com/product-detail/en/on-semiconductor/HCPL2731/HCPL2731QT-ND/31642) |
| [Resistor, 2.32 k&Omega;, package 0805](https://www.digikey.com/product-detail/en/stackpole-electronics-inc/RMCF0805FT2K32/RMCF0805FT2K32DKR-ND/1943295) | R1-R16 | 16 | [link](https://www.digikey.com/product-detail/en/stackpole-electronics-inc/RMCF0805FT2K32/RMCF0805FT2K32DKR-ND/1943295) |
| [Common anode diode](https://www.digikey.com/product-detail/en/diodes-incorporated/BAT54AT-7-F/BAT54AT-FDICT-ND/821941) | D1-D4 | 4 | [link](https://www.digikey.com/product-detail/en/diodes-incorporated/BAT54AT-7-F/BAT54AT-FDICT-ND/821941) |
| [PMOS](https://www.digikey.com/product-detail/en/toshiba-semiconductor-and-storage/SSM3J338RLF/SSM3J338RLFCT-ND/5810258) | Q1-Q8 | 8 | [link](https://www.digikey.com/product-detail/en/toshiba-semiconductor-and-storage/SSM3J338RLF/SSM3J338RLFCT-ND/5810258) |
| [1 uF capacitor, package 0805, voltage rating 10V](https://www.digikey.com/product-detail/en/yageo/CC0805KKX7R6BB105/311-1458-1-ND/2833764) | C1 | 1 | [link](https://www.digikey.com/product-detail/en/yageo/CC0805KKX7R6BB105/311-1458-1-ND/2833764) |
| [DIP socket, 2x8](https://www.digikey.com/product-detail/en/assmann-wsw-components/A-16-LC-TT/AE9992-ND/821746) | U1 | 1 | [link](https://www.digikey.com/product-detail/en/assmann-wsw-components/A-16-LC-TT/AE9992-ND/821746) |
| [DIP socket, 2x4](https://www.digikey.com/product-detail/en/assmann-wsw-components/A-08-LC-TT/AE9986-ND/821740) | U2-U5 | 4 | [link](https://www.digikey.com/product-detail/en/assmann-wsw-components/A-08-LC-TT/AE9986-ND/821740) |
| [Stacking headers](https://www.digikey.com/products/en?mpart=85&v=1528) | J2-J4, H1, H2 | 1 | [link](https://www.digikey.com/products/en?mpart=85&v=1528) |
| [Connector, Molex 50212-8000](https://www.digikey.com/product-detail/en/molex-llc/50212-8000/WM4561CT-ND/2524899) | N/A | 18 | [link](https://www.digikey.com/product-detail/en/molex-llc/50212-8000/WM4561CT-ND/2524899) |
| [Connector housing, Molex 0873690200](https://www.digikey.com/product-detail/en/molex-llc/0873690200/WM10118-ND/3264531) | N/A | 9 | [link](https://www.digikey.com/product-detail/en/molex-llc/0873690200/WM10118-ND/3264531) |
| [JST header, Molex 0894010210](https://www.digikey.com/products/en?keywords=0894010210) | J5-J13 | 9 | [link](https://www.digikey.com/products/en?keywords=0894010210) |
| [2.5 mm barrel jack, 5A max, CUI PJ-057BH ](https://www.digikey.com/product-detail/en/cui-inc/PJ-057BH/CP-057BH-ND/1644602?WT.srch=1&gclid=Cj0KCQjwzK_bBRDDARIsAFQF7zMAA_lLykibpOltGBij_q3GgaALm4U1mWajtnpzEGkrmGGN8nhqwBUaAmMTEALw_wcB) | J1 | 1 for each setup | [link](https://www.digikey.com/product-detail/en/cui-inc/PJ-057BH/CP-057BH-ND/1644602?WT.srch=1&gclid=Cj0KCQjwzK_bBRDDARIsAFQF7zMAA_lLykibpOltGBij_q3GgaALm4U1mWajtnpzEGkrmGGN8nhqwBUaAmMTEALw_wcB) |

## Download

Download [zip](https://github.com/GNHua/valve-control/archive/master.zip) and extract all files.

## Prepare Software

### Flash Arduino Uno

* Connect an Arduino Uno to computer via USB
* Download and Install [Arduino IDE](https://www.arduino.cc/en/Main/Software)
* Open `arduino_valve_control.ino` in `arduino_valve_control` folder with Arduino IDE
* Select USB port: `Tools` > `Port`
* Click `Upload` (the right arrow at the top left corner)
* Wait for uploading to complete

### Python

* Download and Install Python 3.6
  * The Python distribution, [Anaconda](https://www.anaconda.com/download) is recommended, because it comes with pre-installed packages. 
  * Note: On Windows, the directory of installed Python must be added to environment variable. 
* Install Python dependencies
  * Windows: double click `platforms/windows/setup.bat`
  * MacOSX: `$ bash <path to>/platforms/macosx/setup.sh`

## Soldering

(ADD photos of top and bottom layer after soldering)

Solder all the components according to the [table above](#Electrical-Components-To-Buy). The surface mount components are soldered to the bottom layer, while the rest are mounted on the top layer.

### Stacking Headers

In the [table above](#Electrical-Components-To-Buy), the [stacking headers](https://www.digikey.com/products/en?mpart=85&v=1528) contains the following headers.

| Stacking Header | Label on PCB         | Qty. |
| --------------- | :------------------- | :--: |
| 1 x 10          | cut out a 1x2 for J4 | 1    |
| 1 x  8          | H1, H2               | 2    |
| 1 x  6          |                      | 2    |
| 2 x  3          | J2+J3                | 1    |

### H3 - 5V and GND

Because the JST headers at J11 and J12 block H3 on the top layer, I would do the following:

1. Cut a 1x2 stacking header out of an unused one
2. Solder it on H3 from the bottom layer
3. Cut off the female portion on the top layer
4. Put more solder from the top layer

### Barrel Jack

Each setup only needs one barrel jack to connect to a 12 V power supply. The barrel jack can be soldered on any one of the boards.

## Assembly

### Shift Register and Optoisolators

(The images shown below are all taken for the previous PCB design, which is marginally different from the current design.)

After soldering, plug the shift register and optoisolators into their corresponding DIP sockets. Refer to the following image for their orientation.

![image](pics/assembled_top.jpg)

### Stacking PCBs

#### For the inpatient

1. Bend or remove the data pins on all boards except Board 1. See the left image below.
2. Make a connector for serial input and serial output. See the right image below.
3. Stack the PCBs and plug in the connector just made.

| Data Pin | Serial Input/Output |
| -------- | ------------------- |
| <img src="https://github.com/GNHua/valve-control/raw/master/pics/datapin.jpg" height="300"> | <img src="https://github.com/GNHua/valve-control/raw/master/pics/serial_in_serial_out_connector.jpg" height="300"> |

#### Details

In the images above, there are 4 boards stacked on an Arduino Uno.  
Each board provides 8 solenoid valve connectors, and the current design supports up to 6 boards.  
**Before putting the boards together, the data pins on all boards except Board 1 must be bent or removed.**
This is because the data pin connects to the serial input of shift register.
On Board 1, the shift register receives data from the Arduino directly.
For the Board 2-n, their shift registers must have its serial input connected to the serial output of board right beneath it.
