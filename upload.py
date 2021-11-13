#!/usr/bin/env python2
import sys
import os
import time
import binproto2 as mbp


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
    
    protocol = mbp.Protocol(port, baudrate, k_blocksize, k_timeout_ms)
    # INIT SD CARD
    protocol.send_ascii("M21") 

    # DELETE OLD .BIN FILE
    print("""Removing existing '%s'..."""%k_target_fname)
    protocol.send_ascii("M30 "+k_target_fname)
    # STOP AUTO TEMP REPORTING
    protocol.send_ascii("M155 S0")
    print("""Done. Preparing transfer session...""")

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
    print("Done.")

def reset(port, baudrate):
    os.system('stty -F ' + port + ' speed ' + str(baudrate) + ' -echo > /dev/null')
    print("Device tty configured.")
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



if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("USAGE: python %s [DEV_PORT] [BAUDRATE] [FIRMWARE_PATH]"%sys.argv[0]);
    upload(sys.argv[1], sys.argv[2], sys.argv[3])
    wait_for_reconnect(sys.argv[1], sys.argv[2])