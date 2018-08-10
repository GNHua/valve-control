# valve-control
Use Arduino Uno to control solenoid valves

# How to setup

## Purchase

### Send [PCB design](pcb_layout/plots.zip) out for manufacturing

* Highly recommond [JLCPCB](https://jlcpcb.com/). Fabrication and shipping took ~1 week for me in the U.S.
* If you choose JLCPCB, go [here](https://jlcpcb.com/quote), upload [plots.zip](pcb_layout/plots.zip), and leave everything else as default.
* If you have access to a PCB baking oven, buying a SMT-Stencil will save you a lot of time for soldering. If not, all the components can still be soldered by hand.

**Top Layer**  
![PCB top layer](pcb_layout/top.png?raw=true "Top Layer")  
**Bottom Layer**  
![PCB bottom layer](pcb_layout/bottom.png?raw=true "Bottom Layer")

### Buy electrical components

| Part | Qty. (per PCB) | Label on PCB |
| ---- | :------------: | :----------: |
| [Shift register, SN74HC595N](https://www.digikey.com/product-detail/en/texas-instruments/SN74HC595N/296-1600-5-ND/277246?utm_adgroup=Integrated%20Circuits&slid=&gclid=Cj0KCQjwzK_bBRDDARIsAFQF7zN5-LHxIfRLcNVY-gf6gJ_lS_RSs-WGzMVOjYGovQlShfyqFOsZDr0aAqcmEALw_wcB) | 1 | N/A |
| [Optoisolator, HCPL 2731](https://www.digikey.com/product-detail/en/on-semiconductor/HCPL2731/HCPL2731QT-ND/31642) | 4 | N/A |
| [Resistor, 2.32 k&Omega;, package 0805](https://www.digikey.com/product-detail/en/stackpole-electronics-inc/RMCF0805FT2K32/RMCF0805FT2K32DKR-ND/1943295) | 16 | R1-R16 |
| [Common anode diode](https://www.digikey.com/product-detail/en/diodes-incorporated/BAT54AT-7-F/BAT54AT-FDICT-ND/821941) | 4 | D1-D4 |
| [PMOS](https://www.digikey.com/product-detail/en/toshiba-semiconductor-and-storage/SSM3J338RLF/SSM3J338RLFCT-ND/5810258) | 8 | Q1-Q8 |
| [1 uF capacitor, package 0805, voltage rating 10V](https://www.digikey.com/product-detail/en/yageo/CC0805KKX7R6BB105/311-1458-1-ND/2833764) | 1 | C1 |
| [DIP socket, 2x8](https://www.digikey.com/product-detail/en/assmann-wsw-components/A-16-LC-TT/AE9992-ND/821746) | 1 | U1 |
| [DIP socket, 2x4](https://www.digikey.com/product-detail/en/assmann-wsw-components/A-08-LC-TT/AE9986-ND/821740) | 4 | U2-U5 |
| [Stacking headers](https://www.digikey.com/products/en?mpart=85&v=1528) | 1 | N/A |
| [Connector, Molex 50212-8000](https://www.digikey.com/product-detail/en/molex-llc/50212-8000/WM4561CT-ND/2524899) | 18 | N/A |
| [Connector housing, Molex 0873690200](https://www.digikey.com/product-detail/en/molex-llc/0873690200/WM10118-ND/3264531) | 9 | N/A |
| [JST header, Molex 0894010210](https://www.digikey.com/products/en?keywords=0894010210) | 9 | J5-J13 |
| [2.5 mm barrel jack, 5A max, CUI PJ-057BH ](https://www.digikey.com/product-detail/en/cui-inc/PJ-057BH/CP-057BH-ND/1644602?WT.srch=1&gclid=Cj0KCQjwzK_bBRDDARIsAFQF7zMAA_lLykibpOltGBij_q3GgaALm4U1mWajtnpzEGkrmGGN8nhqwBUaAmMTEALw_wcB) | 1 for each setup | J1 |

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

Solder all the components according to the table above. The surface mount components are soldered to the bottom layer, while the rest are mounted on the top layer. 

More on how to solder stacking headers, 5V power and ground header, and barrel jack. 

## Assembly

Stack, and mount with standoffs.  
How to connect J5. 
