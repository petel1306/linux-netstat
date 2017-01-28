#!/usr/bin/python
import os
import glob
import re

def htod(num):
    '''from hex to decimal'''
    return int(num, 16)

def trans_ipv4(hex_address):
    '''parse ip address and port'''
    hex_ip, hex_port = hex_address.split(':')
    port = htod(hex_port)
    parts = ('*' if port == 0 else port, htod(hex_ip[:2]), htod(hex_ip[2:4]),
          htod(hex_ip[4:6]), htod(hex_ip[6:8]))
    return '{}.{}.{}.{}:{}'.format(*parts[::-1])

def trans_state(proto, state):
    '''returns the socket state, if the socket is tcp'''
    return '-' if proto == 'udp' else {
        '01': 'ESTABLISHED',
        '02': 'SYN_SENT',
        '03': 'SYN_RECV',
        '04': 'FIN_WAIT1',
        '05': 'FIN_WAIT2',
        '06': 'TIME_WAIT',
        '07': 'CLOSE',
        '08': 'CLOSE_WAIT',
        '09': 'LAST_ACK',
        '0A': 'LISTEN',
        '0B': 'CLOSING'
    }[state]

def trans_timer(timer):
    '''returns a string describing the timer'''
    kind, time = timer.split(':')
    kind = {
        '00': 'off',
        '01': 'on',
        '02': 'keepalive',
        '03': 'timewait'
    }[kind]
    time = htod(time)/100.0
    return '{} ({})'.format(kind, time)

def find_pid(inode):
    '''finds the pid of the process which has the requested inode'''
    for fd in glob.glob('/proc/[0-9]*/fd/[0-9]*'):
        try:
            if re.search(inode, os.readlink(fd)):
                return fd.split('/')[2]
        except:
            pass
    return '-'

class Socket(object):
    '''parses parts of a socket'''
    def __init__(self, proto, row):
        parts = row.split()
        self.proto = proto
        self.local_address = trans_ipv4(parts[1])
        self.foreign_address = trans_ipv4(parts[2])
        self.state = trans_state(proto, parts[3])
        self.send_q, self.recv_q = map(htod, parts[4].split(':'))
        self.timer = trans_timer(parts[5])
        self.pid = find_pid(parts[9])

def get_sockets(proto):
    '''reads info about sockets for this protocol'''
    sockets = []
    with open('/proc/net/{}'.format(proto)) as socket_info:
        socket_info.readline()
        for line in socket_info:
            sockets.append(Socket(proto, line))
        return sockets

def netstat():
    sockets = get_sockets('tcp') + get_sockets('udp')
    table_format = '{:5}  {:6}  {:6}   {:23} {:23} {:11} {:7} {}'
    print table_format.format('Proto', 'Recv-Q', 'Send-Q', 'Local Address',
        'Foreign Address', 'State', 'PID', 'Timer')
    for socket in sockets:
        print table_format.format(socket.proto, socket.recv_q, socket.send_q, socket.local_address,
            socket.foreign_address, socket.state, socket.pid, socket.timer)

if __name__ == '__main__':
    netstat()
