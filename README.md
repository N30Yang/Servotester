# Servotester
Just another program to test servos if they work

This Project is a dual purpose diognostic tool for testing sts3215 servos (also standard pwm servos [i think]).
I needed a way to bench mark my servos for my other projects to test if they even work.
### YOU WILL NEED
*STS3215* servos (obviously)
**Wonrabai/Waveshare bus servo Adapter (A):** (Jumper set to **Mode B**) like this one https://www.amazon.com/Waveshare-Integrates-Control-Circuit-Supports/dp/B0CTMM4LWK/
* USB-C cable
* 12V power supply (for the servo)

Safety: 
    The servos are quite storong so please remove any obstructions and it has safety features like overcurrent protection and overtemperature protection *BUT* it can still break if you abuse it enough. 
    **Guardrails:** Integrated error handling for disconnected hardware or serial collisions.

##  Installation
1. Clone this repo:
   ```
   bash
   git clone [https://github.com/your-username/sts3215-benchmark.git](https://github.com/your-username/sts3215-benchmark.git)
   ```
2. Install dependencies:
    ```
    bash
    pip install pyserial
    ```
Update the PORT variable in main.py to match your Device Manager (e.g., COM3 or /dev/ttyUSB0).

