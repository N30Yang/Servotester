# Servotest
Just another program to test servos if they work

<img width="1153" height="915" alt="image" src="https://github.com/user-attachments/assets/67719df1-015d-4967-9954-34f3f6ba6614" />


This Project is a multi purpose diognostic tool for testing sts3215 servos (also standard pwm servos [i think]).
I needed a way to bench mark my servos for my other projects to test if they even work.
I created this because most other servo testing tools require a raspberry pi to setup and my one only needs a bus servo adapter to work.

---

### YOU WILL NEED
*STS3215* servos (obviously)
**Waveshare bus servo Adapter (A):** (Jumper set to **Mode B**) like this one https://www.amazon.com/Waveshare-Integrates-Control-Circuit-Supports/dp/B0CTMM4LWK/ 
(*now optional!* just enter test mode)
* USB-C cable
* 12V power supply (for the servo)

---

Safety: 
    The servos are quite storong so please remove any obstructions and it has safety features like overcurrent protection and overtemperature protection *BUT* it can still break if you abuse it enough. 
    **Guardrails:** Integrated error handling for disconnected hardware or serial collisions.

---

##  Installation
## Installation
```bash
pip install servo_tester
servotest
```
Update the PORT variable in main.py to match your Device Manager (e.g., COM3 or /dev/ttyUSB0).

---

## Configuration
Open Servo_Benchmark_tester.py in your text editor and check the top of the script:

* Hardware Mode: Change PORT to match your Device Manager (e.g., COM3 on Windows or /dev/ttyUSB0 on Linux).

* Test Mode: Change PORT to "TEST". This lets you run the script without any hardware connected. It will skip the serial check and print the raw hex packets to your screen in BRIGHT RED so you can verify the math and logic.

---

## Select Your Mode
Run the script

* Option [1] Automatic Benchmark: The script performs a "sanity check" sequence. It tests the absolute minimum (0), the absolute maximum (4095), and runs a "sweep-swoop" rapid response test before returning the servo to neutral.

* Option [2] Live/Manual Mode: * Raw: Type a number between 0-4095 to move to a specific register position.

    Degrees: Type a number followed by d (e.g., 180d or 90.5d) to move to a specific angle.

    Exit: Type exit to return to the main menu.

* [3] Macro mode: it will copy all the instrucitons made in the live mode and replay them in the same order.

* [4] Clear Macro & Reset: it will clear all the instrucitons made in the live mode and replay them in the same order.

---
---

# TROUBLESHOOTING
If you see a [GUARDRAIL] ERROR, check the following common issues:

* Power: Is the 12V Power Supply actually plugged into the Driver Board? (USB alone won't move the servos).

* Jumper: Is the jumper on the Waveshare board set to Mode B (USB Mode)?

* Port Busy: Is another program (like Arduino IDE, Serial Monitor, or another Python instance) using your COM port?

* Drivers: If the COM port doesn't show up in your Device Manager, you may need to install the CH340/CP2102 drivers for the adapter board.

* If you (or a user) gets a "Permission Denied" error, they need to run one command to give themselves access to the "dialout" group:
    Linux Fix: sudo usermod -a -G dialout $USER (Then log out and back in).
