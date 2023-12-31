import socket
import sys
import struct
import RPi.GPIO as GPIO
import time

LED = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)

def create_packet(s_n, ack_n, ack, syn, fin, payload):
    data = struct.pack('!I', s_n) #pack the sequence number
    data += struct.pack('!I', ack_n) #pack the acknowledgement number
    data += struct.pack("!c", ack.encode()) #pack the ACK
    data += struct.pack("!c", syn.encode()) #pack the SYN
    data += struct.pack("!c", fin.encode()) #pack the FIN
    data += payload.encode() #pack the payload
    return data  

def blink_led():
    # Blink the LED in intervals of 0.2 seconds for a total of 2 seconds
    for _ in range(10):
        GPIO.output(LED, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(LED, GPIO.LOW)
        time.sleep(0.2)

def main():
    try:
        # Parse command line arguments
        port = 1337
        log_file = '/home/pi/Desktop/lab4200/4200/server.log'

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        server_address = ('', port)
        sock.bind(server_address)

        while True:
            data, address = sock.recvfrom(4096)
            if data:
                # Unpack the data and log it
                s_n, ack_n, ack, syn, fin, payload = struct.unpack('!IIccc'+str(len(data)-11)+'s', data)
                with open(log_file, 'a') as f:
                    f.write(f'RECV {s_n} {ack_n} {ack} {syn} {fin}\n')

                print("Received payload:", payload.decode())

                if payload.decode() == 'MotionDetected':
                    print("Motion detected payload received!")
                    blink_led()
            if payload.decode() == 'Hello, server':
                print("Hello, server payload received!")

    except KeyboardInterrupt:
        print("Closing...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
