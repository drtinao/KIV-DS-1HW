# Contains various functions which are used for tasks which does not fit to any other python file.
import netTools as nt
import ipaddress

import netTools as net  # tools for network connection
from subprocess import check_output

DISCOVERY_TIMEOUT_SEC = 1200  # secs within which all nodes should be reached ; if timeout, node terminated

NODE_ROLE_MASTER = 'MASTER'  # const - machine is identified as master
NODE_ROLE_SLAVE = 'SLAVE'  # const - machine is identified as a slave

# Check whether program args entered by user are valid or not. Program expects two args - 0: name of prog, 1: count of started nodes.
def check_args(args):
    if len(args) == 2:
        return True
    else:
        return False


# Prints information about the node itself (hostname and ip addr).
def print_info_node():
    print('***Printing info about newly created node - START***', flush=True)
    node_hostname = nt.get_node_hostname()
    ips = check_output(['hostname', '--all-ip-addresses'])
    ip = ips.split()[1]

    node_ip = ip.decode('UTF-8')
    print('Node hostname: ', node_hostname, ', IP: ', node_ip, flush=True)
    print('***Printing info about newly created node - END***', flush=True)


# Function determines starting role of the node. Node with highest IP will start as master, others as slave. This can change later on (some may disc etc)...
# expect_node_count - expected count of nodes to be present in the network
def determine_node_start_role(total_node_num):
    print('***Determining role of node (wait for all nodes to come up) - START***', flush=True)
    retrieved_network_nodes = net.retrieve_network_nodes(total_node_num,
                                                         DISCOVERY_TIMEOUT_SEC)  # scan network for other nodes
    if not retrieved_network_nodes:  # no nodes found till time ran out
        print('Not all nodes are up within time, terminating master node...', flush=True)
        return
    else:  # ok, nodes up within time, continue
        print('All nodes are up and ready!', flush=True)

    highest_ip = None  # highest IP encountered in net list
    node_w_highest_ip = None  # hostname of node with highest IP
    for netNode in retrieved_network_nodes:
        traversed_node_ip = ipaddress.IPv4Address(netNode.node_ip)
        if highest_ip is None or traversed_node_ip > highest_ip:  # if no IP assigned or traversed IP higher
            highest_ip = traversed_node_ip
            node_w_highest_ip = netNode.node_hostname  # get hostname of node with highest IP
    print('***Determining role of node (wait for all nodes to come up) - END***', flush=True)

    if net.get_node_hostname() == node_w_highest_ip:  # machine with highest IP will become master, others are slaves
        print('Node is acting as master!', flush=True)
        return [NODE_ROLE_MASTER, retrieved_network_nodes]
    else:  # machine is gonna be a slave
        print('Node is acting as slave!', flush=True)
        return [NODE_ROLE_SLAVE, retrieved_network_nodes]
