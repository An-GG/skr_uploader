#!/usr/bin/env python2
import sys
import os
import time
import binproto2 as mbp
import platform 

def upload(port, baudrate, firmware_path):
    k_blocksize=512
    k_timeout_ms=1000
    k_target_fname="firmware.bin"
    k_reconnect_poll_interval_s=0.2
    k_reconnect_timeout_s=20
    print("""
SKR UPLOADER
============
DEV PORT:       %s
BUADRATE:       %s
FIRMWARE:       %s
"""%(port, baudrate, firmware_path))
    
    print("""Preparing transfer session...""")
    protocol = mbp.Protocol(port, baudrate, k_blocksize, k_timeout_ms) 

    protocol.send_ascii("M21")          # INIT SD CARD
    protocol.send_ascii("M155 S0")      # STOP AUTO TEMP REPORTING

    protocol.connect()
    print("MBTP Connect")
    transfer_session = mbp.FileTransferProtocol(protocol)
    print("Flashing...")
    transfer_session.copy(firmware_path, k_target_fname, True, False)
    print("Flashing successful.")
    protocol.disconnect()
    print("MBTP Disconnect")
    protocol.shutdown()
    print("Session successfully shut down.")
    reset(port, baudrate)
    wait_for_reconnect(port, k_reconnect_timeout_s, k_reconnect_poll_interval_s)
	time.sleep(0.5)
	send_post_upload_gcode(port, baudrate)
    print("Done.")

def configure_tty(port, baudrate):
    if platform.system() == 'Darwin': # bsd fuckers...
        os.system('stty -f ' + port + ' speed ' + str(baudrate)  + ' -echo > /dev/null')
    else:
        os.system('stty -F ' + port + ' ospeed ' + str(baudrate) + ' ispeed ' + str(baudrate)  + ' -echo > /dev/null')
    print("Device tty configured.")

def reset(port, baudrate):
	configure_tty(port, baudrate)
    os.system('echo M997 >> ' + port)
    print("M997 RESET sent.")


def wait_for_reconnect(port, timeout, poll_interval):
    print("Waiting for recconnect...")
    check_command = 'ls ' + port + ' > /dev/null 2>&1'
    waiting=True
    time_spent=0
    while(waiting and time_spent < timeout):
        time.sleep(poll_interval);
        time_spent+=poll_interval;
        if os.system(check_command) == 0:
            waiting=False
    if waiting:
        sys.exit("ERROR: Wait for reset timeout after %s seconds."%timeout)
    else:
        print("Successfully reconnected on port %s after %s seconds."%(poll_interval, time_spent))

def send_post_upload_gcode(port, baudrate):
	configure_tty(port, baudrate)
	os.system("echo 'M502' >> " + port)
	os.system("echo 'G29 A' >> " + port)
	os.system("echo 'G29 L1' >> " + port)
	os.system("echo 'M500' >> " + port)
	print("Sent post upload gcode.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("USAGE: python %s [DEV_PORT] [BAUDRATE] [FIRMWARE_PATH]"%sys.argv[0]);
    upload(sys.argv[1], sys.argv[2], sys.argv[3])
