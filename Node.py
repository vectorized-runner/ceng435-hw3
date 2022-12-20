import json
import socket
import sys
import threading
import time
from datetime import datetime
from datetime import timedelta

host = "127.0.0.1"
last_message_time = None
program_exit = False
self_port = None
distances = {}

def update_distance(x, y, cost):
    distances[(x, y)] = cost
    distances[(y, x)] = cost
    return


def parse_file(file_name):
    f = open(file_name, "r")
    lines = f.read().splitlines()

    node_count = int(lines[0])
    neighbors = []

    for x in range(1, len(lines)):
        line = lines[x]
        sp = line.split(" ")
        other_port = int(sp[0])
        cost = int(sp[1])
        neighbors.append(other_port)
        update_distance(other_port, self_port, cost)

    return node_count, neighbors


def send_to_all_neighbors(neighbors):
    while not program_exit and len(neighbors) > 0:
        successful = []

        for neighbor in neighbors:
            is_successful = send_data(neighbor)
            if is_successful:
                successful.append(neighbor)

        for item in successful:
            neighbors.remove(item)

        # Wait 1s before trying again
        time.sleep(1)

    return


def send_data(send_port):
    # print("send data begin")

    str_table = {}

    for key in distances.keys():
        str_key = str(key)
        str_value = str(distances[key])
        str_table[str_key] = str_value

    json_str = json.dumps([self_port, str_table])
    if len(json_str) == 0:
        raise Exception(f"Json length is zero.")

    print(f"Sending data: {json_str}")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, send_port))
        s.sendall(json_str.encode("utf-8"))
    except:
        s.close()
        return False

    # print("send data end")
    s.close()
    return True


def listen_to_connection(connection):
    # print("start listening to connection...")

    while not program_exit:
        data_str = connection.recv(1024).decode("utf-8")
        if len(data_str) == 0:
            # print("Close connection as received zero length.")
            connection.close()
            break

        data = json.loads(data_str)
        on_data_received(data)

    connection.close()
    return


def on_data_received(data):
    global last_message_time
    last_message_time = datetime.now()

    other_port, str_distances = data
    value_dict = {}
    for key in str_distances.keys():
        value_dict[eval(key)] = eval(str_distances[key])

    update_distances(other_port, value_dict)
    return


def update_distances(other_port, other_distances):
    print(f"Data Received: {other_port}, {other_distances}")
    return


def listen_to_messages():
    # print("start listening to messages...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, self_port))
    s.listen()

    while not program_exit:
        connection, addr = s.accept()
        cThread = threading.Thread(target=listen_to_connection, args=(connection,))
        cThread.start()

    return


def print_distances(node_count):
    for x in range(3000, 3000 + node_count):
        key = (self_port, x)
        if key in distances:
            distance = distances[key]
            print(f"{self_port} -{x} | {distance}")

    return


def program():
    print("Start running")

    if len(sys.argv) != 2:
        print(f"Incorrect amount of args: {len(sys.argv)}")
        return

    global self_port
    self_port = int(sys.argv[1])
    print(f"Port is: {self_port}")

    file_name = f"first/{self_port}.costs"
    # Todo: update file name
    node_count, neighbors = parse_file(file_name)

    copy_neighbors = neighbors.copy()

    thread_send = threading.Thread(target=send_to_all_neighbors, args=(copy_neighbors,))
    thread_send.start()

    # todo: kill this thread
    thread_listen = threading.Thread(target=listen_to_messages)
    thread_listen.start()

    global last_message_time
    last_message_time = datetime.now()

    global program_exit
    while not program_exit:
        current_time = datetime.now()
        seconds_passed = timedelta.total_seconds(current_time - last_message_time)
        if seconds_passed > 5:
            print_distances(node_count)
            program_exit = True

    return


if __name__ == '__main__':
    program()
    print("done")
