import socket
import sys
import struct
import RPi.GPIO as GPIO

PIR = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR, GPIO.IN)

def create_packet(s_n, ack_n, ack, syn, fin, payload):
    data = struct.pack('!I', s_n) #pack the sequence number
    data += struct.pack('!I', ack_n) #pack the acknowledgement number
    data += struct.pack("!c", ack.encode()) #pack the ACK
    data += struct.pack("!c", syn.encode()) #pack the SYN
    data += struct.pack("!c", fin.encode()) #pack the FIN
    data += payload.encode() #pack the payload
    return data  

def main():
    try:
        # Parse command line arguments
        server_ip = '127.0.0.1'
        port = 1337
        log_file = '/home/pi/Desktop/lab4200/4200/server.log'

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_address = (server_ip, port)
        
        while True:
            try:
                # Detect motion
                if GPIO.input(PIR):
                    print("Motion detected!")
                    # Motion detected, send a packet to the server
                    message = create_packet(100, 0, 'Y', 'N', 'N', 'MotionDetected')
                    print("Sending 'MotionDetected' message to server...")
                    sock.sendto(message, server_address)
                    time.sleep(3)
                else:
                    # No motion detected, send 'Hello, server' message
                    message = create_packet(100, 0, 'Y', 'N', 'N', 'Hello, server')
                    print("Sending 'Hello, server' message to server...")
                    sock.sendto(message, server_address)
                    time.sleep(2)

            except KeyboardInterrupt:
                print("Closing...")
                break
    finally:
        sock.close()

if __name__ == "__main__":
    main()


