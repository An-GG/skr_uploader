#!/usr/bin/env python2
import sys
import os
import binproto2 as mbp


def upload(port, baudrate, firmware_path):
    k_blocksize=512
    k_timeout_ms=30 * 1000
    k_target_fname="firmware.bin"
    print(1+"""
SKR UPLOADER
============
DEV PORT:       %s
BUADRATE:       %s
FIRMWARE:       %s
"""%(port, baudrate, firmware_path))
    
    protocol = mbp.Protocol(port, baudrate, 512, k_timeout_ms)
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
    print("MBTP Disconnect\nResetting...")

    os.system('echo M997 >> ' + port)
    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("USAGE: python %s [DEV_PORT] [BAUDRATE] [FIRMWARE_PATH]"%sys.argv[0]);
    upload(sys.argv[1], sys.argv[2], sys.argv[3])