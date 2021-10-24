# Contains functions which are used for communication with network.
import os  # used for pinging etc.
import time  # used for counting execution time
import socket  # for working with network con
import nodeTools as nt
from subprocess import check_output


# CLASS DEF START - Class object represent one node in the network. Each node is represented by color, hostname and IP.
class NetworkNode:
    def __init__(self, hostname, IP):
        self.node_hostname = hostname  # hostname of node
        self.node_ip = IP  # IP of node
        self.assigned_color = nt.NODE_COLOR_NONE
# CLASS DEF END - Class object represent one node in the network. Each node is represented by color, hostname and IP.

# Returns hostname of the current machine.
def get_node_hostname():
    try:
        node_hostname = socket.gethostname()
        return node_hostname
    except:
        print('Error while getting node hostname', flush=True)

# Returns IP of the current machine.
# node_hostname - hostname of the machine
def get_node_ip(node_hostname):
    try:
        node_ip = socket.gethostbyname(node_hostname)
        return node_ip
    except:
        print('Error while getting node IP', flush=True)


# Starts pinging specified node. Ie. node with highest hostname 'node-x'.
# timeout: seconds within which master node should be up. If time runs out, node will be terminated.
# node_num: number of node which should be pinged.
# On start of algo every node should be up... During time some may disconnect, algo is ok with that.
def start_node_ping(timeout, node_num):
    remaining_time = timeout  # remaining time of execution before node termination
    hostname_to_ping = 'node-' + str(node_num)

    while remaining_time > 0:  # ping server till time runs out / success
        start_time = time.time()
        ping_resp = os.system("ping -c 1 " + hostname_to_ping)

        if ping_resp == 0:
            print(hostname_to_ping, 'is up!', flush=True)
            return True  # ok, server is up
        else:
            print(hostname_to_ping, 'is down!', flush=True)  # server is down, try again till time runs out

        end_time = time.time()
        remaining_time -= (end_time - start_time)

    return False  # timeout, server is not up!


# Retrieves information about other nodes which are present in the network (hostname, IP).
# expect_node_count - expected count of nodes
# timeout: seconds within which all nodes should be up. If time runs out, node will be terminated.
# On start of algo every node should be up... During time some may disconnect, algo is ok with that.
def retrieve_network_nodes(expect_node_count, timeout):
    print('***Scanning network for other nodes - START***', flush=True)
    remaining_time = timeout  # remaining time of execution before node termination

    network_nodes = []
    node_name = 'node-'
    node_counter = 1

    while True and remaining_time > 0:  # add nodes to list till non-existing node is encountered or time runs out
        start_time = time.time()
        node_hostname = node_name + str(node_counter)

        try:
            if node_hostname == get_node_hostname():  # getting ip of node itself, localhost ; right ip is the second one, eth1...
                ips = check_output(['hostname', '--all-ip-addresses'])
                ip = ips.split()[1]

                node_ip = ip.decode('UTF-8')
            else:  # getting ip of other node in network
                node_ip = socket.gethostbyname(node_hostname)

        except:
            print('Discovered ', len(network_nodes), ' other nodes in network.', flush=True)
            if len(network_nodes) == int(expect_node_count):  # all expected nodes discovered
                print('Discovered nodes: ', len(network_nodes), ', expected: ', expect_node_count, ' - OK!', flush=True)
                return network_nodes
            else:  # not all nodes already up, try again
                print('Discovered nodes: ', len(network_nodes), ', expected: ', expect_node_count, ' - RETRYING!', flush=True)
                network_nodes *= 0  # remove all items in list
                node_counter = 1

                scan_time = time.time() - start_time
                if scan_time < 5:  # if scan took < 5, wait for few sec before another try
                    time.sleep(5 - scan_time)
                continue

        if start_node_ping(3, node_counter):  # node is pinging within 3s, ok, add
            network_nodes.append(NetworkNode(node_hostname, node_ip))

        node_counter += 1

        end_time = time.time()
        remaining_time -= (end_time - start_time)
    print('***Scanning network for other nodes - END***', flush=True)
    return False
