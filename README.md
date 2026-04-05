# Servotester
Just another program to test servos if they work

    <img width="1153" height="915" alt="image" src="https://github.com/user-attachments/assets/67719df1-015d-4967-9954-34f3f6ba6614" />


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


# HOW TO USE
1. Configuration
Open Servo_Benchmark_tester.py and check the top of the script:

Hardware Mode: Change PORT to match your Device Manager (e.g., COM3 or /dev/ttyUSB0).

Test Mode: Change PORT to "TEST". This lets you run the script without any hardware connected. It will skip the serial check and print the raw hex packets to your screen in BRIGHT RED so you can check the math.

2. Running the Script
Run the program in your terminal:

Bash
python Servo_Benchmark_tester.py
3. Select Your Mode
Once the intro screen clears, you will have two options:

Option [1] Automatic Benchmark: The script will automatically test the servo's absolute minimum (0), absolute maximum (4095), and perform a "sweep-swoop" rapid response test before returning to neutral.

Option [2] Live/Manual Mode: * Type a raw number (0-4095) to move the servo to that specific register position.

Type a degree followed by 'd' (e.g., 180d or 90d) to have the script automatically calculate the position.

Type exit to return to the main menu.

TROUBLESHOOTING
If you see the [GUARDRAIL] ERROR, check the following:

Is the 12V power supply actually plugged in?

Is the jumper on the Waveshare board set to B?

Is another program (like Arduino IDE) using your COM port?
