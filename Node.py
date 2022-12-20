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
    while not program_exit and len(neighbors) > 0:
        successful = []

        for neighbor in neighbors:
            is_successful = send_data(data, neighbor)
            if is_successful:
                successful.append(neighbor)

        for item in successful:
            neighbors.remove(item)

        # Wait 1s before trying again
        time.sleep(1)

    return


def send_data(data, port):
    # print("send data begin")

    str_data = {}

    for key in data.keys():
        str_key = str(key)
        str_value = str(data[key])
        str_data[str_key] = str_value

    json_str = json.dumps(str_data)
    if len(json_str) == 0:
        raise Exception(f"Json length is zero. {str_data}")

    print(f"Sending data: {json_str}")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, port))
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

    print(f"Data Received: {data}")
    # Todo:
    return


def listen_to_messages(port):
    # print("start listening to messages...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()

    while not program_exit:
        connection, addr = s.accept()
        cThread = threading.Thread(target=listen_to_connection, args=(connection,))
        cThread.start()

    return


def print_distances(table, self_port, node_count):
    for x in range(3000, 3000 + node_count):
        key = (self_port, x)
        if key in table:
            distance = table[key]
            print(f"{self_port} -{x} | {distance}")

    return


def program():
    print("Start running")

    if len(sys.argv) != 2:
        print(f"Incorrect amount of args: {len(sys.argv)}")
        return

    port = int(sys.argv[1])
    # print(f"Port is: {port}")

    file_name = f"first/{port}.costs"
    # Todo: update file name
    node_count, neighbors, table = parse_file(file_name, port)

    copy_neighbors = neighbors.copy()

    thread_send = threading.Thread(target=send_to_all_neighbors, args=(table, copy_neighbors,))
    thread_send.start()

    thread_listen = threading.Thread(target=listen_to_messages, args=(port,))
    thread_listen.start()

    global last_message_time
    last_message_time = datetime.now()

    global program_exit
    while not program_exit:
        current_time = datetime.now()
        seconds_passed = timedelta.total_seconds(current_time - last_message_time)
        if seconds_passed > 5:
            print_distances(table, port, node_count)
            program_exit = True

    return


if __name__ == '__main__':
    program()
