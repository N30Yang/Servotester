from re import DEBUG
import serial
import time
import sys
import os
import serial.tools.list_ports

# config
PORT = "COM3" # !!!!! CHANGE TO "TEST" (FULL CAPS NO QUOTES) FOR TEST MODE !!!!!
BAUD = 1000000
ID = 1
DEBUG = False

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


def start_app():
    intro()
    global PORT

    print("\n[Select mode]")
    print("1. Physical hardware mode (servo is connected)")
    print("2. Test mode (test logic and packets, with no servo)")
    choice=input("\n choose a mode [1] or [2]")

    if choice == "2":
        PORT = "TEST"
        print(f"{G}Test mode selected{RESET}")
    else:
        ports = sorted(serial.tools.list_ports.comports())

        if not ports:
            print("\n No serial devices found")
            print("Check you usb cable, defulting to test mode")
            PORT = "TEST"
        
        else:
            print("\n[Detected devices:]")
            for i, p in enumerate(ports):
                # On Linux/Mac, p.device looks like /dev/ttyUSB0
                # On Windows, p.device looks like COM3
                print(f"{i + 1}. {p.device} ({p.description})")

            try:
                val = input(f"\nSelect port (1-{len(ports)}) or enter name: ").strip()
                if val.isdigit():
                    PORT = ports[int(val)-1].device
                else:
                    PORT = val.upper() # If they type 'com3', it becomes 'COM3'
            except (ValueError, IndexError):
                PORT = ports[0].device
                print(f"Invalid choice, selecting {PORT}")
        print(f"\n--- TARGETING: {PORT} ---")
    run_full_benchmark()

def read_register(ser, addr, length, servo_id):
    """Robust read for STS protocol"""
    packet = [0xFF, 0xFF, servo_id, 0x04, 0x02, addr, length]
    checksum = ~(sum(packet[2:]) & 0xFF) & 0xFF
    packet.append(checksum)

    ser.reset_input_buffer()
    ser.write(bytearray(packet))
    ser.flush()

    # Wait for full response
    expected_len = 6 + length
    start_time = time.time()
    buffer = bytearray()

    while len(buffer) < expected_len:
        if ser.in_waiting:
            buffer.extend(ser.read(ser.in_waiting))
        if time.time() - start_time > 0.05:  # 50ms timeout
            break

    return bytes(buffer)

def get_telementry(ser, servo_id=1):
    if ser is None or not getattr(ser, 'is_open', False):
        return f"{C}Volt: --V{RESET} {R}[SIMULATION]{RESET}"
    
    try:
        resp_v = read_register(ser, 0x3C, 1, servo_id)

        if not resp_v or len(resp_v) < 7:
            return f"{R}Telemetry Error (Short Read){RESET}"

        # Validate header
        if resp_v[0] != 0xFF or resp_v[1] != 0xFF:
            return f"{R}Bad Packet{RESET}"

        # Error byte
        if resp_v[4] != 0:
            return f"{R}Servo Error: {resp_v[4]}{RESET}"

        raw_volt = resp_v[5]
        volt = raw_volt / 10.0

        return f"{G}Voltage: {volt:.1f}V{RESET}"

    except Exception as e:
        return f"{R}Read Error: {e}{RESET}"


def draw_bar(val):
    # Feature 4 live bar for position
        bar_len = 20
        filled=int((val/4095)*bar_len)
        bar = "█"*filled + "-"* (bar_len - filled)
        return f"{C}[{bar}] {val}/4095{RESET}"




"""
    consructs and sends packet for servo
    addr 0x2A is the position
    addr 0x3E is the speed it moves
    using 'write position' command with speed and acceleration
    register 0x2A, 2 bytes for position and 2 bytes for speed
"""
def send_packet(ser, servo_id, addr, value, speed=0):
    # Length = Instruction(1) + Address(1) + Data(2) + Checksum(1) = 5
    length = 5 
    cmd = 0x03 

    # Construct packet
    packet = [0xFF, 0xFF, servo_id, length, cmd, addr]
    packet.append(value & 0xFF)
    packet.append((value >> 8) & 0xFF)

    # Checksum calculation (usually includes everything after ID)
    checksum = ~(sum(packet[2:]) & 0xFF) & 0xFF
    packet.append(checksum)

    # --- DEBUGGING TOOL ---
    # Print the packet to see exactly what is being sent
    if DEBUG:
        print(f"DEBUG: Sending bytes: {[hex(b) for b in packet]}")
    # ----------------------

    try:
        if ser is None:
            print(f"{R}[TEST MODE] Packet sent: {packet}{RESET}")
        else:
            ser.write(bytearray(packet))
            ser.flush() # Ensure the bytes are actually pushed out of the buffer
    except Exception as e:
        print(f"{R}Transmission error: {e}{RESET}")

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


if __name__ == "__main__":
    start_app()