# lightclient.py
# from EmulatorGUI import GPIO
import socket
import struct
import RPi.GPIO as GPIO
import time
import sys

PIR = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR, GPIO.IN)

def create_packet(s_n, ack_n, ack, syn, fin, payload):
    header = struct.pack('!II', s_n, ack_n)
    flags = (ack << 2) | (syn << 1) | fin
    header += struct.pack('!B', flags)
    data = header + payload.encode()
    return data

def main():
    if len(sys.argv) != 7 or sys.argv[1] != "-s" or sys.argv[3] != "-p" or sys.argv[5] != "-l":
        print("Usage: lightclient -s <SERVER-IP> -p <PORT> -l <LOGFILE>")
        sys.exit(1)

    server_ip = sys.argv[2]
    port = int(sys.argv[4])
    log_file = sys.argv[6]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (server_ip, port)

    try:
        # Three-way handshake
        seq_num = 100
        ack_num = 0
        message = create_packet(seq_num, ack_num, 0, 1, 0, '')
        sock.sendto(message, server_address)

        data, server = sock.recvfrom(4096)
        s_n, ack_n, flags, payload = struct.unpack('!IIB' + str(len(data)-9) + 's', data)
        if flags & 0b010:
            print("Handshake completed.")
            seq_num += 1
            ack_num = ack_n + 1

        message = create_packet(seq_num, ack_num, 1, 0, 0, 'DurationAndBlinks')
        sock.sendto(message, server_address)

        data, server = sock.recvfrom(4096)
        s_n, ack_n, flags, payload = struct.unpack('!IIB' + str(len(data)-9) + 's', data)
        if flags & 0b001:
            print(f"Server acknowledged: {payload.decode()}")

        # Main loop
        while True:
            if GPIO.input(PIR):
                message = create_packet(seq_num, ack_num, 1, 0, 0, 'MotionDetected')
                sock.sendto(message, server_address)

                data, server = sock.recvfrom(4096)
                s_n, ack_n, flags, payload = struct.unpack('!IIB' + str(len(data)-9) + 's', data)
                if flags & 0b001:
                    print(f"Server acknowledged motion detection.")

            # Your other conditions and actions can be added here

            time.sleep(1)  # Adjust the sleep duration as needed

    except KeyboardInterrupt:
        print("Keyboard interrupt. Exiting.")
    finally:
        # Send FIN packet
        message = create_packet(seq_num, ack_num, 0, 0, 1, 'InteractionCompleted')
        sock.sendto(message, server_address)
        sock.close()

if __name__ == "__main__":
    main()
