import random
import time
import socket
import struct
import select

port_nums_in_use = []

def generate_random_port_num():
    port_num_found = False
    port_num = 0
    while not port_num_found:
        port_num = random.randrange(49152, 65535)
        if not port_num in port_nums_in_use:
            port_num_found = True
            port_nums_in_use.append(port_num)
    return port_num

def read_file_for_websites(filename):
    with open(filename) as filereader:
        file_strip = filereader.readlines()
    website_list = []
    for line in file_strip:
        if(line[len(line) - 1] == '\n'):
            website_list.append(line[:len(line) - 1])
        else:
            website_list.append(line)
    print(website_list)

def run_simplified_traceroute(website):
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    source_ip = socket.gethostname()
    # ephemeral port number assigned to source port
    source_port = generate_random_port_num()
    send_sock.bind((source_ip, source_port))
    print("source port" + str(source_port))

    dest_ip = socket.gethostbyname(website)
    dest_port = 33434

    # initial ttl value of 64
    ttl = 64
    send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    msg = 'measurement for class project, questions to student cxz424@case.edu, or professor mxr136@case.edu'
    payload = bytes(msg + 'a' * (1472 - len(msg)), 'ascii')

    # start timer
    time_at_send = time.perf_counter()
    send_sock.sendto(payload, (dest_ip, dest_port))

    #Wait 5 seconds to time out
    select_timeout = select.select([recv_sock], [], [], 2)
    if not select_timeout[0]:
        print("This website timed out and failed to respond")
        return

    icmp_packet = recv_sock.recv(1500)
    time_at_receive = time.perf_counter()
    return_time_milliseconds = (time_at_receive - time_at_send) / 1000

    # Check to see if IP address matches
    icmp_packet_ip_address_tuple = struct.unpack("!BBBB", icmp_packet[44:48])
    icmp_packet_ip_address = ""
    for ip_segment in icmp_packet_ip_address_tuple:
        icmp_packet_ip_address = icmp_packet_ip_address + str(ip_segment) + "."
    icmp_packet_ip_address = icmp_packet_ip_address[:len(icmp_packet_ip_address) - 1]
    ip_match = icmp_packet_ip_address == dest_ip

    # Check to see if port number matches
    icmp_packet_port_number_tuple = struct.unpack("!BB", icmp_packet[48:50])
    icmp_packet_port_number = bin((icmp_packet_port_number_tuple[0] << 8) + icmp_packet_port_number_tuple[1])
    port_number_match = icmp_packet_port_number == source_port

    return_ttl = icmp_packet[36]
    hops_taken = ttl - return_ttl

    print("It took " + str(hops_taken) + " hops to reach " + website + ". The RTT was " + str(return_time_milliseconds) + " milliseconds.\nThe returned packet matched the IP address correctly: " + ip_match + ". The returned packet matched the port number correctly: " + port_number_match)
    send_sock.close()
    recv_sock.close()

run_simplified_traceroute("www.google.com")