import socket
import sys


def write_table(x, y, table, cost):
    table[(x, y)] = cost
    table[(y, x)] = cost
    return


def parse_file(file_name, port):
    f = open(file_name, "r")
    lines = f.read().splitlines()

    node_count = int(lines[0])

    table = { }

    for x in range(1, len(lines)):
        line = lines[x]
        sp = line.split(" ")
        other_port = int(sp[0])
        cost = int(sp[1])
        write_table(other_port, port, table, cost)

    return table


def program():
    print("Start running")

    if len(sys.argv) != 2:
        print(f"Incorrect amount of args: {len(sys.argv)}")
        return

    port = int(sys.argv[1])
    print(f"Port is: {port}")

    file_name = f"first/{port}.costs"
    # Todo: update file name
    table = parse_file(file_name, port)

    print(table)

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

                print("I should be sending data now!")
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
