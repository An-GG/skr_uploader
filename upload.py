#!/usr/bin/env python2
import sys
import os
import binproto2 as mbp


def upload(port, baudrate, firmware_path):
    k_blocksize=512
    k_timeout_ms=30 * 1000
    k_target_fname="firmware.bin"
    #
    protocol = mbp.Protocol(port, baudrate, 512, k_timeout_ms)
    
    # INIT SD CARD
    protocol.send_ascii("M21") 
    # DELETE OLD .BIN FILE
    protocol.send_ascii("M30 "+k_target_fname)
    # STOP AUTO TEMP REPORTING
    protocol.send_ascii("M155 S0")

    protocol.connect()
    transfer_session = mbp.FileTransferProtocol(protocol)
    transfer_session.copy(firmware_path, k_target_fname, True, False)
    protocol.disconnect()

    os.system('echo M997 >> ' + port)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("USAGE: python %s [DEV_PORT] [BAUDRATE] [FIRMWARE_PATH]"%sys.argv[0]);
    upload(sys.argv[1], sys.argv[2], sys.argv[3])