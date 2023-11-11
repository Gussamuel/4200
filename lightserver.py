# lightserver.py
# from EmulatorGUI import GPIO
import socket
import struct
import RPi.GPIO as GPIO
import time
import sys

LED = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)

def create_packet(s_n, ack_n, ack, syn, fin, payload):
    header = struct.pack('!II', s_n, ack_n)
    flags = (ack << 2) | (syn << 1) | fin
    header += struct.pack('!B', flags)
    data = header + payload.encode()
    return data


def main():
    if len(sys.argv) != 5 or sys.argv[1] != "-p" or sys.argv[3] != "-s":
        print("Usage: lightserver -p <PORT> -s <LOGFILE>")
        sys.exit(1)

    port = int(sys.argv[2])
    log_file = sys.argv[4]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', port)
    sock.bind(server_address)

    seq_num = 200
    ack_num = 0

    # Step 1: SYN
    data, client = sock.recvfrom(4096)
    s_n, ack_n, flags, payload = struct.unpack('!IIB' + str(len(data)-9) + 's', data)
    if flags & 0b010:
        seq_num += 1
        ack_num = s_n + 1

        # Step 2: SYN|ACK
        message = create_packet(seq_num, ack_num, 1, 1, 0, '')
        sock.sendto(message, client)

        # Step 3: ACK
        data, client = sock.recvfrom(4096)
        s_n, ack_n, flags, payload = struct.unpack('!IIB' + str(len(data)-9) + 's', data)
        if flags & 0b001:
            print("Handshake completed.")

    # Receive duration and blinks from client
    data, client = sock.recvfrom(4096)
    s_n, ack_n, flags, payload = struct.unpack('!IIB' + str(len(data)-9) + 's', data)
    if flags & 0b001:
        print(f"Received: {payload.decode()}")

        # Acknowledge the receipt of duration and blinks
        message = create_packet(seq_num, s_n + 1, 1, 0, 0, 'ACK')
        sock.sendto(message, client)

    # Detect motion
    motion_detected = False
    while not motion_detected:
        data, client = sock.recvfrom(4096)
        s_n, ack_n, flags, payload = struct.unpack('!IIB' + str(len(data)-9) + 's', data)
        if flags & 0b001 and payload.decode() == 'MotionDetected':
            motion_detected = True

    # Log motion detection
    with open(log_file, 'a') as f:
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        f.write(f'{timestamp} :MotionDetected\n')

    # Blink the LED
    GPIO.output(LED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(LED, GPIO.LOW)

    # Send FIN packet
    message = create_packet(seq_num, ack_num, 0, 0, 1, 'InteractionCompleted')
    sock.sendto(message, client)

    sock.close()

if __name__ == "__main__":
    main()
