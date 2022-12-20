import socket
import sys
import threading
import time

host = "127.0.0.1"


def write_table(x, y, table, cost):
    table[(x, y)] = cost
    table[(y, x)] = cost
    return


def parse_file(file_name, port):
    f = open(file_name, "r")
    lines = f.read().splitlines()

    node_count = int(lines[0])
    neighbors = []
    table = {}

    for x in range(1, len(lines)):
        line = lines[x]
        sp = line.split(" ")
        other_port = int(sp[0])
        cost = int(sp[1])
        neighbors.append(other_port)
        write_table(other_port, port, table, cost)

    return node_count, neighbors, table


def send_to_all_neighbors(data, neighbors):
    while len(neighbors) > 0:
        print("try again.")
        successful = []

        for neighbor in neighbors:
            is_successful = send_data(data, neighbor)
            if is_successful:
                successful.append(neighbor)

        for item in successful:
            neighbors.remove(item)

        # Wait 100ms before trying again
        time.sleep(0.1)

    return


def send_data(data, port):
    print("send data begin")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(data)
    s.close()
    print("send data end")
    return


def program():
    print("Start running")

    if len(sys.argv) != 2:
        print(f"Incorrect amount of args: {len(sys.argv)}")
        return

    port = int(sys.argv[1])
    print(f"Port is: {port}")

    file_name = f"first/{port}.costs"
    # Todo: update file name
    node_count, neighbors, table = parse_file(file_name, port)

    copy_neighbors = neighbors.copy()

    thread = threading.Thread(target=send_to_all_neighbors, args=(table, copy_neighbors,))
    thread.start()

    print("xdd")

    return

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
