import socket
import sys


def parse_file():

    return

def program():
    print("Start running")

    if len(sys.argv) != 2:
        print(f"Incorrect amount of args: {len(sys.argv)}")
        return

    port = int(sys.argv[1])
    print(f"Port is: {port}")

    host = "127.0.0.1"

    connections = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        connection, addr = s.accept()
        with connection:

            print(f"Connected by {addr}")
            while True:
                data = connection.recv(1024)
                if not data:
                    break

                # TODO: Send your table to others
                connection.sendall(data)

    # Stages:
    # Read neighborhood info from .costs
    # Send distance vector to every neighbor
    # Listen from updates from all neighbors
    # if no update happens, close all connections and print

    print("Finished")
    return


if __name__ == '__main__':
    program()
