import random
import time
import socket
import struct
import select
import csv

port_nums_in_use = []
rtt_list = []
hops_list = []

#function to check that the port number assigned is unique and is an ephemeral port number
def generate_random_port_num():
    port_num_found = False
    port_num = 0
    while not port_num_found:
        port_num = random.randrange(49152, 65535)
        if not port_num in port_nums_in_use:
            port_num_found = True
            port_nums_in_use.append(port_num)
    return port_num

#reads the file targets.txt for website names separated by "\n", where the last line does not have a newline after it
#returns a list of website names to trace
def read_file_for_websites(filename):
    with open(filename) as filereader:
        file_strip = filereader.readlines()
    website_list = []
    for line in file_strip:
        if(line[len(line) - 1] == '\n'):
            website_list.append(line[:len(line) - 1])
        else:
            website_list.append(line)
    return website_list

#runs a trace along the website provided as an argument; tracks the RTT and the number of hops
def simplified_traceroute_instance(website, failed_flag):
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    #setting up the sending socket with IP address and port number
    source_ip = socket.gethostname()
    # ephemeral port number assigned to source port
    source_port = generate_random_port_num()
    send_sock.bind((source_ip, source_port))

    #destination IP from the website name; destination port is one that is meant to take in misc. requests
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

    #Wait 10 seconds to time out
    select_timeout = select.select([recv_sock], [], [], 10)
    if not select_timeout[0]:
        print("This website: " + website + " timed out and failed to respond")
        if failed_flag > 0:
            print("Re-running trace to " + website + "...")
            return simplified_traceroute_instance(website, failed_flag - 1)
        else:
            print("This website: " + website + " has timed out multiple times. Failure.")
            return -1

    icmp_packet = recv_sock.recv(1500)
    #stop timer, calculate RTT here
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
    icmp_packet_port_number = (icmp_packet_port_number_tuple[0] << 8) + icmp_packet_port_number_tuple[1]
    port_number_match = icmp_packet_port_number == source_port

    return_ttl = icmp_packet[36]
    hops_taken = ttl - return_ttl

    print("It took " + str(hops_taken) + " hops to reach " + website + ". The RTT was " + str(return_time_milliseconds) + " milliseconds.\nThe returned packet matched the IP address correctly: " + str(ip_match) + ". The returned packet matched the port number correctly: " + str(port_number_match))
    rtt_list.append(return_time_milliseconds)
    hops_list.append(hops_taken)

    send_sock.close()
    recv_sock.close()
    return 1

#overall function to run traceroute, including writing to a separate CSV file the findings from this traceroute run.
def run_simplified_traceroute():
    website_list = read_file_for_websites("targets.txt")
    with open("results.csv", mode='w') as csv_file:
        column_names = ['Website', 'RTT', 'Hops']
        csv_writer = csv.DictWriter(csv_file, column_names)
        for i in range(len(website_list)):
            #can fail 3 times until done
            if(simplified_traceroute_instance(website_list[i], 3) == 1):
                csv_writer.writerow({'Website' : website_list[i], 'RTT': str(rtt_list[i]), 'Hops': str(hops_list[i])})
            else:
                rtt_list.append(0)
                hops_list.append(0)
                csv_writer.writerow({'Website' : website_list[i], 'RTT': 'Timeout', 'Hops': 'Timeout'})

run_simplified_traceroute()
