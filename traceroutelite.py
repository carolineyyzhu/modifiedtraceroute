import time
import socket
import struct

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
    # source_port = 49152
    # send_sock.bind((source_ip, source_port))

    dest_ip = socket.gethostbyname(website)
    print(dest_ip)
    dest_port = 33434

    # initial ttl value of 64
    ttl = 64
    send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    msg = 'measurement for class project, questions to student cxz424@case.edu, or professor mxr136@case.edu'
    payload = bytes(msg + 'a' * (1472 - len(msg)), 'ascii')

    # start timer
    time_at_send = time.perf_counter()
    send_sock.sendto(payload, (dest_ip, dest_port))

    icmp_packet = recv_sock.recv(1500)
    time_at_receive = time.perf_counter()
    return_time_nanoseconds = time_at_receive - time_at_send
    print('Return time' + str(return_time_nanoseconds))

    print('ICMP packet length: ' + str(icmp_packet.__len__()))
    # Check to see if IP address matches

    icmp_packet_ip_address_tuple = struct.unpack("!BBBB", icmp_packet[44:48])
    icmp_packet_ip_address = ""
    for ip_segment in icmp_packet_ip_address_tuple:
        icmp_packet_ip_address = icmp_packet_ip_address + str(ip_segment) + "."
    icmp_packet_ip_address = icmp_packet_ip_address[:len(icmp_packet_ip_address) - 1]
    ip_match = icmp_packet_ip_address == dest_ip
    print(icmp_packet_ip_address + " ip, + " + str(ip_match))

    # Check to see if port number matches

    send_sock.close()
    recv_sock.close()

icmp_packet_ip_address_tuple = (127, 21, 0, 1)

print(icmp_packet_ip_address)