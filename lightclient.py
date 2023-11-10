#client
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
    # Parse command line arguments
    # server_ip = '192.168.1.35'
    server_ip = '127.0.0.1'
    port = 1337
    log_file = '/home/pi/Desktop/lab4200'

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (server_ip, port)
    message = create_packet(100, 0, 'Y', 'N', 'N', 'Hello, server')
    try:
        # Send data
        sock.sendto(message, server_address)

        # Receive response
        data, server = sock.recvfrom(4096)
        s_n, ack_n, ack, syn, fin, payload = struct.unpack('!IIccc', data)
        with open(log_file, 'a') as f:
            f.write(f'SEND {s_n} {ack_n} {ack} {syn} {fin}\n')

        # Detect motion
        if GPIO.input(PIR):
            # Motion detected, send a packet to the server
            message = create_packet(100, 0, 'Y', 'N', 'N', 'MotionDetected')
            sock.sendto(message, server_address)
    finally:
        sock.close()

if __name__ == "__main__":
    main()
