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
self_port = -1
node_count = -1
neighbors = []
distances = {}
start_node = 3000


def update_distance(x, y, cost):
    distances[(x, y)] = cost
    distances[(y, x)] = cost
    return


def parse_file(file_name):
    f = open(file_name, "r")
    lines = f.read().splitlines()

    global node_count
    node_count = int(lines[0])

    global neighbors

    for x in range(1, len(lines)):
        line = lines[x]
        sp = line.split(" ")
        other_port = int(sp[0])
        cost = int(sp[1])
        neighbors.append(other_port)
        update_distance(other_port, self_port, cost)

    return neighbors


def send_to_all_neighbors():
    to_send = neighbors.copy()
    while not program_exit and len(to_send) > 0:
        successful = []

        for neighbor in to_send:
            is_successful = send_data(neighbor)
            if is_successful:
                successful.append(neighbor)

        for item in successful:
            to_send.remove(item)

        # Wait 1s before trying again
        time.sleep(1)

    return


def send_data(send_port):
    str_table = {}

    for key in distances.keys():
        str_key = str(key)
        str_value = str(distances[key])
        str_table[str_key] = str_value

    json_str = json.dumps([self_port, str_table])
    if len(json_str) == 0:
        raise Exception(f"Json length is zero.")

    # print(f"Sending data: {json_str}")

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
    print("start listening to connection...")

    while not program_exit:
        data_str = connection.recv(1024).decode("utf-8")
        if len(data_str) == 0:
            print("Close connection as received zero length.")
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
    distance_to_port = distances[(self_port, other_port)]
    updated = False

    for x in range(start_node, start_node + node_count):
        if (other_port, x) in other_distances:
            other_cost = other_distances[(other_port, x)]
            new_cost = other_cost + distance_to_port

            if (self_port, x) not in distances:
                # Adding for the first time
                update_distance(self_port, x, new_cost)
                updated = True
            else:
                current_cost = distances[(self_port, x)]
                if new_cost < current_cost:
                    update_distance(self_port, x, new_cost)
                    updated = True

    if updated:
        broadcast_distances()
        return

    print("update distances!")
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


def print_distances():
    for x in range(start_node, start_node + node_count):
        key = (self_port, x)
        if key in distances:
            distance = distances[key]
            print(f"{self_port} -{x} | {distance}")

    return


def broadcast_distances():
    thread_send = threading.Thread(target=send_to_all_neighbors)
    thread_send.start()
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
    parse_file(file_name)

    broadcast_distances()

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
            print_distances()
            program_exit = True

    return


if __name__ == '__main__':
    program()
    print("done")
