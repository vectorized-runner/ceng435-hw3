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

    try:
        s.connect((host, port))
        s.sendall(data)
    except:
        s.close()
        return False

    print("send data end")
    s.close()
    return True


def listen_to_connection(connection):
    while True:
        data = connection.recv(1024)
        print(f"Data Received: {data}")

    return


def listen_to_messages(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()

    while True:
        connection, addr = s.accept()
        cThread = threading.Thread(target=listen_to_connection, args=(connection,))
        cThread.start()

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

    thread_send = threading.Thread(target=send_to_all_neighbors, args=(table, copy_neighbors,))
    thread_send.start()

    thread_listen = threading.Thread(target=listen_to_messages, args=(port,))
    thread_listen.start()

    # Todo: Here we do the waiting...

    print("xdd")

    return

    # Stages:
    # Read neighborhood info from .costs
    # Send distance vector to every neighbor
    # Listen from updates from all neighbors
    # if no update happens, close all connections and print

    print("Finished")
    return


if __name__ == '__main__':
    program()
