# Contains functions which are connected directly with nodes (master / slave).
import math
import time

import netTools as net  # tools for network connection
import socket  # for working with network con
import threading  # create thread for each connection

MASTER_CONTACT_SEC = 15  # contact master every x sec
MASTER_CONNECT_SEC = 100  # total secs within which master should be reached, then timeout
MASTER_WAIT_BETWEEN_CON_SEC = 3  # secs between tries to connect to master

NODE_COLOR_GREEN = 'GREEN'  # color of node, assigned to NetworkNode.assigned_color
NODE_COLOR_RED = 'RED__'  # color of node, assigned to NetworkNode.assigned_color
NODE_COLOR_NONE = 'NONE_'  # color of node, assigned to NetworkNode.assigned_color

HEADER_LENGTH = 6  # max length of messages used during communication master <-> slave
FORMAT = 'utf-8'  # format of received messages

node_current_color = NODE_COLOR_NONE  # describes current color of the node, every node starts as non-colored

# Performs steps which lead to setting the node to slave mode (client; listens for instructions from server).
# retrieved_network_nodes - list with NetworkNode objects, in which each obj represents one node in network.
def start_slave_node(retrieved_network_nodes):
    print('***Setting the node as slave (client) - START***', flush=True)
    slave_sock = slave_node_connect(retrieved_network_nodes)  # connect to node with highest IP, hostname
    slave_send_color_mes(slave_sock)  # send req to master to set color of the node

    # nodes are ready, connect to master
    print('***Setting the node as slave (client) - END***', flush=True)


# Performs steps which lead to setting the node to master mode (server; can set colors of other nodes etc). Server is always node with highest IP.
# retrieved_network_nodes - list with NetworkNode objects, in which each obj represents one node in network.
def start_master_node(retrieved_network_nodes):
    print('***Setting node as master - START***', flush=True)
    dict_node_color = master_count_colors(retrieved_network_nodes)  # assign ideal color to each node, get dict
    dict_ip_hostname = master_create_ip_hostname_dict(retrieved_network_nodes)  # map ip -> hostname
    # ok, nodes are ready, got list of all nodes and all of them are in ready state, get ready for client connection
    master_node_listen(len(retrieved_network_nodes), dict_node_color, dict_ip_hostname)
    print('***Setting node as master - END***', flush=True)


# Determine which color should be assigned to each node - for master node!
# retrieved_network_nodes - list with NetworkNode objects, in which each obj represents one node in network.
# return: dictionary, where keys = hostnames (node-X), values = colors (GREEN / RED)
def master_count_colors(retrieved_network_nodes):
    global node_current_color
    print('***Printing planned coloring of nodes - START', flush=True)
    total_node_count = len(retrieved_network_nodes)  # number of all nodes present in network
    green_node_count = math.ceil((1.0 / 3.0) * total_node_count)  # count of nodes, which should be green; round to next whole num
    red_node_count = total_node_count - green_node_count  # count of nodes, which should be red; remaining nodes must be red (2 / 3)

    assigned_green_count = 1  # number of nodes to which green is assigned, master always green
    assigned_red_count = 0  # number of nodes to which red is assigned

    #  color each node + create dictionary in which keys = nodes (node-X), values = colors (GREEN / RED)
    node_color_dict = dict()  # dict with node colors

    for netNode in retrieved_network_nodes:
        # if traversed node is master, set green an continue
        if netNode.node_hostname == net.get_node_hostname():  # master will be always green
            netNode.assigned_color = NODE_COLOR_GREEN
        elif assigned_green_count < green_node_count:  # node color green
            netNode.assigned_color = NODE_COLOR_GREEN
            assigned_green_count += 1
        elif assigned_red_count < red_node_count:  # node color red
            netNode.assigned_color = NODE_COLOR_RED
            assigned_red_count += 1
        node_color_dict[netNode.node_hostname] = netNode.assigned_color  # node colored, add to dict
        print('Assigned ', netNode.node_hostname, ' color ', netNode.assigned_color, flush=True)
    print('***Printing planned coloring of nodes - END', flush=True)
    print('Coloring master as GREEN!', flush=True)
    node_current_color = NODE_COLOR_GREEN
    return node_color_dict

# Returns dictionary, where keys = IPs, values = hostnames of nodes.
def master_create_ip_hostname_dict(retrieved_network_nodes):
    ip_hostname_dict = dict()
    for netNode in retrieved_network_nodes:
        ip_hostname_dict[netNode.node_ip] = netNode.node_hostname

    return ip_hostname_dict

# Start listening for new connections - only for master node!
# expect_node_count - number of all nodes present in net
# node_color_dict - dictionary, where keys = nodes (node-X), values = colors (GREEN / RED)
# dict_ip_hostname - dictionary, where keys = IPs, values = hostnames of nodes
def master_node_listen(expect_node_count, node_color_dict, dict_ip_hostname):
    # RELATED TO MASTER - START
    total_connected_nodes = 0  # number of nodes which are connected to the master
    MASTER_PORT = 5051  # port to be used by the master (server)
    MASTER_HOSTNAME = net.get_node_hostname()  # hostname of current machine
    MASTER_ADDR = ('', MASTER_PORT)
    # RELATED TO MASTER - END

    master_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket for communication with other nodes
    master_sock.bind(MASTER_ADDR)  # bind socket with local machine
    master_sock.listen(5)
    print('Master node: ', MASTER_HOSTNAME, ' is listening on port: ', MASTER_PORT, flush=True)
    while total_connected_nodes < (int(expect_node_count) - 1):  # wait for new clients in a loop
        con, addr = master_sock.accept()  # keep port and ip of connected device
        thread = threading.Thread(target=master_node_accept_con, args=(con, addr, node_color_dict, dict_ip_hostname))
        thread.start()
        total_connected_nodes += 1


# Handle connection of new slave node - only for master node! Then accept messages from slave
# node_color_dict - dictionary, where keys = nodes (node-X), values = colors (GREEN / RED)
# dict_ip_hostname - dictionary, where keys = IPs, values = hostnames of nodes
def master_node_accept_con(conn, addr, node_color_dict, dict_ip_hostname):
    len_to_receive = len(str(NODE_COLOR_GREEN).encode(FORMAT))
    node_hostname = dict_ip_hostname[addr[0]]  # hostname of node which contacted master
    while True:  # receive messages from slaves
        color_which_should_be_as = node_color_dict[node_hostname]  # get color which should be assigned to node from dict
        rec_mes_color = conn.recv(len_to_receive).decode(FORMAT)  # receive messages from slave and respond with new color

        info_to_print = 'Node hostname: ' + node_hostname + ' with IP: ' + addr[0] + ' is reporting color: '
        if rec_mes_color:  # message is valid
            if rec_mes_color == NODE_COLOR_GREEN:  # slave is green, color is assigned
                info_to_print += 'GREEN. '
                if color_which_should_be_as == NODE_COLOR_GREEN: # GREEN already assigned and should be GREEN, nutin to change
                    info_to_print += 'OK, stays GREEN.'
                else:
                    info_to_print += 'WRONG COLOR REPORTED, assigning ' + color_which_should_be_as + '!'
                conn.send(color_which_should_be_as.encode(FORMAT))
                print(info_to_print, flush=True)
            elif rec_mes_color == NODE_COLOR_RED:  # slave is red, color is assigned
                info_to_print += 'RED. '
                if color_which_should_be_as == NODE_COLOR_RED:  # RED already assigned and should be RED, nutin to change
                    info_to_print += 'OK, stays RED.'
                else:
                    info_to_print += 'WRONG COLOR REPORTED, assigning ' + color_which_should_be_as + '!'
                conn.send(color_which_should_be_as.encode(FORMAT))
                print(info_to_print, flush=True)
            elif rec_mes_color == NODE_COLOR_NONE:  # slave color not yet assigned
                info_to_print += 'NO COLOR REPORTED, assigning ' + color_which_should_be_as + '!'
                conn.send(color_which_should_be_as.encode(FORMAT))
                print(info_to_print, flush=True)
            else:  # no other message is expected / valid, drop connection...
                conn.close()


# Connect to master - only for slave node!
# retrieved_network_nodes - list with NetworkNode objects, in which each obj represents one node in network. Node with highest hostname will be contacted.
def slave_node_connect(retrieved_network_nodes):
    print('***Connect to master - START***', flush=True)
    print('Searching for node with highest hostname / IP', flush=True)
    highest_node_num = -1  # discovered node with highest node num / IP

    for netNode in retrieved_network_nodes:
        node_num = netNode.node_hostname.split('node-')  # split hostname and get num of node
        if int(node_num[1]) > int(highest_node_num):  # node with highest hostname / IP found, assign it
            highest_node_num = node_num[1]

    # RELATED TO SLAVE - START
    TARGET_PORT = 5051  # port used to connect to master
    TARGET_IP = socket.gethostbyname('node-' + highest_node_num)  # get ip of target machine
    TARGET_ADDR = (TARGET_IP, TARGET_PORT)
    # RELATED TO SLAVE - END

    slave_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Trying to connect to node-' + highest_node_num, flush=True)

    remaining_time = MASTER_CONNECT_SEC  # remaining time of execution before node termination
    while remaining_time > 0:  # ping server till time runs out / success
        start_time = time.time()

        try:
            slave_sock.connect(TARGET_ADDR)
            print('Connected to node-' + highest_node_num + ' successfully!', flush=True)
            print('***Connect to master - END***', flush=True)
            return slave_sock
        except:
            print('Error while connecting to node-' + TARGET_IP + ', retrying...', flush=True)

        end_time = time.time()
        connect_time = time.time() - start_time
        if connect_time < MASTER_WAIT_BETWEEN_CON_SEC:  # if connect took < 3, wait before another try
            time.sleep(MASTER_WAIT_BETWEEN_CON_SEC - connect_time)

        remaining_time -= (end_time - start_time)
    print('***Connect to master - END***', flush=True)


# Send current node color to server -> server should respond with new color of the node. Used by slave node!
# slave_socket - socket which will be used for communication with the server
def slave_send_color_mes(slave_socket):
    global node_current_color
    while True:
        start_time = time.time()
        message = node_current_color.encode(FORMAT)  # send current color to server
        slave_socket.send(message)
        server_response = slave_socket.recv(len(NODE_COLOR_GREEN)).decode(FORMAT)
        if server_response == node_current_color:
            print('Server responded: ', server_response, '. OK, color stays the same.', flush=True)
        else:
            print('Server responded: ', server_response, '. SETTING NEW COLOR OF THE NODE!', flush=True)
            node_current_color = server_response
        info_time = time.time() - start_time
        if info_time < MASTER_CONTACT_SEC:  # report color every 15 seconds
            print('Zzz... Node is sleeping 15sec before contacting master again!', flush=True)
            time.sleep(MASTER_CONTACT_SEC - info_time)
