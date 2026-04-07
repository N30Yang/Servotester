import serial
import time
import sys
import os

# config
PORT = "COM3" # !!!!! CHANGE TO "TEST" (FULL CAPS NO QUOTES) FOR TEST MODE !!!!!
BAUD = 1000000
ID = 1

# Color Constants
R = "\033[91m"  # Red
G = "\033[92m"  # Green
Y = "\033[93m"  # Yellow
C = "\033[96m"  # Cyan
RESET = "\033[0m"

MACRO_LIST=[]

def clear_consle():
    #keeps the screen tidy for stats
    os.system('cls' if os.name =='nt' else 'clear')

def get_telementry(ser):
    # feature 2 for stats of the temp and volatage in real time
    if ser is None:
        return f"{C}Temperature = --°C | Voltage = --V{RESET} {R}[SIMULATION]{RESET}"

    # READ command (0x02) for 2 bytes starting at 0x2C (Temp/Volt)
    packet = [0xFF, 0xFF, ID, 0x04, 0x02, 0x2C, 0x02]
    checksum = ~(sum(packet[2:]) & 0xFF) & 0xFF
    packet.append(checksum)

    try:
        ser.write(bytearray(packet))
        time.sleep(0.02)  # wait for servo to respond
        response = ser.read(8)
        if len(response) >= 8:
            temp = response[5]
            volt = response[6] / 10.0
            
            # Thermal Logic
            if temp > 50:
                t_color = R
                warning = f" {R}!!! CRITICAL OVERHEAT !!!{RESET}"
            else:
                t_color = G
                warning = ""

            return f"{t_color}Temp: {temp}°C{RESET} | {G}Voltage: {volt}V{RESET}{warning}"
            
    except Exception:
        pass
    return f"{R}Failed to read telemetry{RESET}"

def draw_bar(val):
    # Feature 4 live bar for position
        bar_len = 20
        filled=int((val/4095)*bar_len)
        bar = "█"*filled + "-"* (bar_len - filled)
        return f"{C}[{bar}] {val}/4095{RESET}"



def send_packet(ser, servo_id, addr, value, speed=0):
    """
    consructs and sends packet for servo
    addr 0x2A is the position
    addr 0x3E is the speed it moves
    using 'write position' command with speed and acceleration
    register 0x2A, 2 bytes for position and 2 bytes for speed
    """
    length = 7
    cmd = 0x03

    # writing to position (aka 0x2A)
    packet = [0xFF, 0xFF, servo_id, length, cmd, addr]
    packet.append(value & 0xFF)  # pos low
    packet.append((value >> 8) & 0xFF)  # pos high

    # checksum calc for error checking
    checksum = ~(sum(packet[2:]) & 0xFF) & 0xFF
    packet.append(checksum)

    try:
        if ser is None:
            # ALL RED NOTIFICATION FOR TEST MODE
            print(f"{R}[TEST MODE] Packet sent to ID {servo_id}: {packet}{RESET}")
        else:
            ser.write(bytearray(packet))
    except Exception as e:
        print(
            f"{R}Uh oh transmission error: {e} try turning on and off again and replugging the servos{RESET}"
        )


def intro():
    # intoduction screen
    print(f"{C}{'=' * 50}")
    print("sts3215 servo tester benchamark thingymagig")
    print(f"{'=' * 50}{RESET}")
    print(f"Target Servo ID: {Y}{ID}{RESET}")
    print(f"Connection Port: {Y}{PORT}{RESET} @ {BAUD} bps")
    print("-" * 50)
    print(f"{R}SAFETY CHECKLIST:{RESET}")
    print("1. 12V Power Supply connected to Driver Board?")
    print("2. Jumper set to 'B' (USB Mode)?")
    print("3. Servo horn clear of any obstructions?")
    print("-" * 50)
    input(f"\n{G}>>> PRESS [ENTER] TO COMMENCE TEST SEQUENCE <<<{RESET}")


def run_full_benchmark():
    global MACRO_LIST
    try:
        # TEST MODE 
        if PORT == "TEST":
            print(f"\n{R}*** IN TEST MODE NO HARDWARE REQ ***{RESET}")
            ser = None
        else:
            # 1sec timeout so i don't waste 30 buckaroonies
            ser = serial.Serial(PORT, BAUD, timeout=0.1)
        
        while True: # Added a loop so you don't have to restart script to pick new modes
            clear_consle() # CHANGE: Clears screen when returning to menu
            print(f"\n{C}--- MAIN MENU ---{RESET}")
            print("1. Run Full Auto Benchmark")
            print("2. Live/Manual Control (Records to Macro)")
            print(f"3. Replay Recorded Macro ({len(MACRO_LIST)} steps)")
            print("4. Clear Macro & Reset")
            print("5. Exit")

            choice = input(f"{C}Select mode [1-5]: {RESET}")
            
            if choice == "1":
                clear_consle() # CHANGE: Clears screen before starting tests
                print(f"\n{G}starting full benchmark on {PORT} !!!!!!!{RESET} ")

                # 1st test absoulute minimum
                print("1st test absoulute minimum (0)")
                send_packet(ser, ID, 0x2A, 0)
                time.sleep(1.5)  # allow it to move

                # 2nd test absoulute max
                print("2nd test absoulute max (4095)")
                send_packet(ser, ID, 0x2A, 4095)
                time.sleep(2.5)  # allow it to move (longest possible travel time)

                # 3rd test rapid sweepswoop
                print("3rd test rapid response to command test")
                for _ in range(3):
                    send_packet(ser, ID, 0x2A, 2048)
                    time.sleep(0.8)
                    send_packet(ser, ID, 0x2A, 3000)
                    time.sleep(0.5)

                # 4th test return to home
                print("4th test return to neutral (2048)")
                send_packet(ser, ID, 0x2A, 2048)
                time.sleep(1.0)

                for move, label in [(0, "min"), (4095, "max"), (2048, "mid")]:
                    print(f"Moving to {label}...")
                    send_packet(ser, ID, 0x2A, move)
                    print(get_telementry(ser))
                    time.sleep(1.5)
                input(f"\n{G}Benchmark complete! Press Enter to go back...{RESET}")

            elif choice == "2":
                while True:
                    clear_consle() # CHANGE: Keeps telemetry and bar at the top of the screen
                    print(f"\n {C}LIVE/MANUAL MODE: Type 2048 or 180d. type exit to end.{RESET}")
                    print(f" {Y}[NUMBER]d{RESET} for degrees | {Y}[NUMBER]{RESET} for raw")
                    print("-" * 30)
                    
                    stats = get_telementry(ser)
                    print(f"STATUS: {stats}")
                    
                    # Show the bar for the last position moved to if available
                    if MACRO_LIST:
                        print(f"CURRENT POS: {draw_bar(MACRO_LIST[-1])}")
                    
                    cmd = input(f"\n{C}Move to >>{RESET} ").lower().strip()
                    
                    if cmd == "exit":
                        break
                    try:
                        if cmd.endswith("d"):
                            val = int((float(cmd[:-1]) / 360) * 4095)
                        else:
                            val = int(cmd)

                        if 0 <= val <= 4095:
                            send_packet(ser, ID, 0x2A, val)
                            MACRO_LIST.append(val)
                        else:
                            print(f"{R}Value must be between 0-4095 or 0d-360d{RESET}")
                            time.sleep(1)
                    except ValueError:
                        print(f"{R}Invalid input.{RESET}")
                        time.sleep(1)


            elif choice == "3":
                if not MACRO_LIST:
                    input(f"{R} No moves recorded, press Enter...{RESET}")
                else:
                    clear_consle() # CHANGE: Tidy replay screen
                    print(f"{G}Replaying {len(MACRO_LIST)} steps...{RESET}")
                    for move in MACRO_LIST:
                        send_packet(ser, ID, 0x2A, move)
                        print(draw_bar(move))
                        time.sleep(0.8)
                    input(f"\n{G}Replay done! Press Enter...{RESET}")

            elif choice == "4":
                MACRO_LIST = []
                print(f"{Y}Macro list cleared.{RESET}")            
                time.sleep(1)

            elif choice =="5":
                exit()

    except serial.SerialException:
        print(f"\n{R}[GUARDRAIL] ERROR: COULD NOT OPEN SERVO PORT{RESET}")
        input("Check connections and press Enter...")
    except KeyboardInterrupt:
        print(f"\n{R}[GUARDRAIL] USER ABORT: Stopping test...{RESET}")
    except Exception as e:
        print(f"\n{R}[GUARDRAIL] UNKNOWN ERROR: {e}{RESET}")
        input("Press Enter to continue...")

def start_app():
    intro()
    run_full_benchmark()

if __name__ == "__main__":
<<<<<<< HEAD
    start_app()
=======
    intro()
    run_full_benchmark()
>>>>>>> df42a6e5c7a5a36d20af6c7b8ddc194ecd24bb91
