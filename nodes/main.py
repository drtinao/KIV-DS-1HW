import supportTools as st
import nodeTools as nt
import sys  # read args


# Start operation of the node - depending on IP, the node is started in master / slave mode. Node with highest IP is always a master.
# expect_node_count - expected count of nodes
def start_node(expect_node_count):
    result = st.determine_node_start_role(expect_node_count)  # determine start role of node and get all nodes in net
    node_role = result[0]  # role of the node
    retrieved_network_nodes = result[1]  # nodes present in the net
    if node_role == st.NODE_ROLE_MASTER:  # node should act as master
        nt.start_master_node(retrieved_network_nodes)
    else:  # node should act as slave
        nt.start_slave_node(retrieved_network_nodes)


# EXECUTION START
if not st.check_args(sys.argv):  # args are not ok, exit
    print('Args are not valid, exiting node...', flush=True)
else:  # args are valid continue with exec
    st.print_info_node()  # print info about node
    count_of_started_nodes = sys.argv[1]
    start_node(count_of_started_nodes)
