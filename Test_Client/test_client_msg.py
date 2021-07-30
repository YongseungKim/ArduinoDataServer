"""
tcp client with reconnect
- This Program is a socket client program that transfer ArduinoDataServer's message
- message type : id:value;
"""

# ! /usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys, time
import socket


def doConnect(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except:
        pass
    return sock


def main():
    host, port = "127.0.0.1", 9999
    print(host, port)
    sockLocal = doConnect(host, port)
    meter_id = 1
    meter_count = 0
    while True:
        try:
            meter_count += 1
            msg = '{}:{};'.format(meter_id, meter_count)
            sockLocal.send(msg.encode('utf-8'))
            print('send ==> ' + msg)
            if meter_count > 1000:
                meter_count = 0
        except socket.error:
            print("\r\nsocket error,do reconnect ")
            time.sleep(3)
            sockLocal = doConnect(host, port)
        except:
            print('\r\nother error occur ')
            time.sleep(10)
        time.sleep(5)


if __name__ == "__main__":
    main()