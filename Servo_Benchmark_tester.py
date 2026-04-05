import serial
import time
import sys

# config
PORT = 'COM3'
BAUD = 1000000
ID = 1

def send_packet(ser,servo_id, addr, value, speed=0):
    # consructs and sends packet for servo
    # addr 0x2A is the position
    # addr 0x3E is the speed it moves

    # using 'write position' command with speed and acceleration
    # register 0x2A, 2 bytes for position and 2 bytes for speed
    length = 7
    cmd= 0x03

    # writing to position (aka 0x2A)
    packet = [0xFF, 0xFF, servo_id, length, cmd, addr]
    packet.append(value & 0xFF) # pos low
    packet.append((value >>8) & 0xFF) # pos high

    #checksum calc for error checking
    checksum = ~(sum(packet[2:]) & 0xFF) & 0xFF
    packet.append(checksum)

    try:
        ser.write(bytearray(packet))
    except Exception as e:
        print(f"Uh oh transmission error: {e} try turning on and off again and replugging the servos")


def intro():
    #intoduction screen
    print("="*50)
    print("sts3215 servo tester benchamark thingymagig")
    print("="*50)
    print(f"Target Servo ID: {ID}")
    print(f"Connection Port: {PORT} @ {BAUD} bps")
    print("-"*50)
    print("SAFETY CHECKLIST:")
    print("1. 12V Power Supply connected to Driver Board?")
    print("2. Jumper set to 'B' (USB Mode)?")
    print("3. Servo horn clear of any obstructions?")
    print("-"*50)
    input("\n>>> PRESS [ENTER] TO COMMENCE TEST SEQUENCE <<<")
    
def run_full_benchamrk():
    try:
        # 1sec timeout so i don't waste 30 buckaroonies
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"starting full benchmark on {PORT} !!!!!!! ")

        # 1st test absoulute minimum 
        print("1st test absoulute minimum (0)")
        send_packet(ser,ID,0x2A, 0)
        time.sleep(1.5) #allow it to move


        # 2nd testabsoulute max
        print("2nd test absoulute max (4095)")
        send_packet(ser,ID,0x2A, 4095)
        time.sleep(2.5) #allow it to move (longest possible travel time)


        # 3rd test rapid sweepswoop 
        print("3rd test rapid response to command test")
        send_packet(ser,ID,0x2A,2048)
        time.sleep(0.8)
        send_packet(ser,ID,0x2A,3000)
        time.sleep(0.5)
        send_packet(ser,ID,0x2A,2048)
        time.sleep(0.8)
        send_packet(ser,ID,0x2A,3000)
        time.sleep(0.5)
        send_packet(ser,ID,0x2A,2048)
        time.sleep(0.8)
        send_packet(ser,ID,0x2A,3000)
        time.sleep(0.5)       

        # 4th test return to home
        print("4th test return to neutral (2048)")
        send_packet(ser,ID,0x2A,2048)
        time.sleep(1.0)

        print("Benchmark complete!!! :) operational")

    except serial.SerialException:
        print("\n[GUARDRAIL] ERROR: COULD NOT OPEN SERVO PORT")
        print("common troubleshooting")
        print("is the servo plugged in")
        print("is jumper on B?")
        print("is another device (ie arduino) using this port (COM3) currently")
    except KeyboardInterrupt:
        print("\n[GUARDRAIL] USER ABORT: Stopping test...")
    except Exception as e:
        print(f"\n[GUARDRAIL] UNKNOWN ERROR: {e}")
        print("i don't know bro :skull:, this is beyond my skill")

if __name__ == "__main__":
    intro() # Added this so your intro actually shows up!
    run_full_benchmark()
