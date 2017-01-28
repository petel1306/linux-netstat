#!/usr/bin/python
import os
import glob

def trans_ipv4(hex_address):
    '''parse ip address and port'''
    hex_ip, hex_port = hex_address.split(':')
    parts = (htod(hex_port), htod(hex_ip[:2]), htod(hex_ip[2:4]), htod(hex_ip[4:6]), htod(hex_ip[6:8]))
    return '{}.{}.{}.{}:{}'.format(*parts[::-1])

def htod(num):
    '''from hex to decimal'''
    return int(num, 16)
