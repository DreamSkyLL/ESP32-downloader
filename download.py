#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ESP32 smartpump firmware downloader by kontornl

# import esptool
import json, os

ADDR_EEPROM = 0x3ff000
ADDR_FW = 0x10000
CONFIG_PATH = 'config.json'
EEPROM_PATH = 'eeprom.bin'
FW_PUMP_PATH = 'pump.bin'
FW_TANK_PATH = 'tank.bin'
PPID_CELL_MIN = 1
PPID_CELL_MAX = 254

download_config:dict = {
    "serial_port": "COM6",
    "serial_speed": 1500000,
    "gen_ppid": True,
    "ppid_start": [1, 1, 1, 1],
    "server_addr": "47.104.141.250",
    "server_port": 9991
}
class download_args():
    def __init__(self, addr_filename=[(ADDR_EEPROM, None), (ADDR_FW, None)], port=download_config['serial_port'], baud=download_config['serial_speed']):
        self.port=port
        self.baud=baud
        self.addr_filename=addr_filename
        # self.flash_freq='40m'
        # self.flash_mode='qio'
        # self.flash_size='8MB'
        self.ucIsHspi=False
        self.ucIsLegacy=False
        self.no_progress=False
        self.no_stub=True
        self.verify=True
        self.compress=None
        self.no_compress=False

# download_args:dict = {
#     'port': download_config['serial_port'],
#     'baud': download_config['serial_speed'],
#     'addr_filename': [(ADDR_EEPROM, None), (ADDR_FW, None)],
#     'flash_freq': '40m',
#     'flash_mode': 'qio',
#     'flash_size': '4MB',
#     'ucIsHspi': False,
#     'ucIsLegacy': False,
#     'no_progress': False,
#     'verify': True,
#     'compress': None,
#     'no_compress': False
# }
ppid_current:list = [PPID_CELL_MIN, PPID_CELL_MIN, PPID_CELL_MIN, PPID_CELL_MIN]

def load_config():
    global download_config, ppid_current
    try:
        with open(CONFIG_PATH, 'r') as f:
            download_config = json.loads(f.read())
        ppid_current = download_config['ppid_start']
    except:
        return None

def gen_ppid():
    ppid = b''
    for cell in download_config['ppid_start']:
        if cell < PPID_CELL_MIN: cell = PPID_CELL_MIN
        if cell > PPID_CELL_MAX: cell = PPID_CELL_MAX
        ppid += int(cell).to_bytes(1, byteorder='little')
    if ppid == b'i6\x82\x85': 
        download_config['ppid_start'][3] += 1
        ppid = b'i6\x82\x86'
    download_config['ppid_start'][3] += 1
    if download_config['ppid_start'][3] > PPID_CELL_MAX:
        download_config['ppid_start'][3] = 0
        download_config['ppid_start'][2] += 1
    if download_config['ppid_start'][2] > PPID_CELL_MAX:
        download_config['ppid_start'][2] = 0
        download_config['ppid_start'][1] += 1
    if download_config['ppid_start'][1] > PPID_CELL_MAX:
        download_config['ppid_start'][1] = 0
        download_config['ppid_start'][0] += 1
    if download_config['ppid_start'][0] > PPID_CELL_MAX:
        download_config['ppid_start'] == [PPID_CELL_MIN, PPID_CELL_MIN, PPID_CELL_MIN, PPID_CELL_MIN]
    return ppid

if __name__ == '__main__':
    load_config()
    # with open('eeprom_init.bin', 'rb') as f:
    #     eeprom_init = bytearray(f.read())
    # eeprom_head = eeprom_init[0:0x200]
    # eeprom_tail = eeprom_init[0x400:0x41f]
    # del eeprom_init
    try:
        while True:
            print('Generating virtual EEPROM.')
            if download_config['gen_ppid']: ppid = gen_ppid()
            else:
                ppid_str = input('Give one PPID in heximal format XXXX-XXXX, e.g. 6936-8285: ')
                # TODO: manually input PPID
            eeprom_cache:bytearray = b'H' # b'H\0\0\0\0\0lh\00047.104.141.250\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x07\x27'
            eeprom_cache += ppid
            eeprom_cache += b'\0lmh\0eSUP\0O\x80'
            eeprom_cache += download_config['server_port'].to_bytes(2, 'little')
            eeprom_cache += bytearray(download_config['server_addr'], encoding='utf-8')
            eeprom_cache += b'\0'*(65-len(download_config['server_addr']))
            # once server_addr contains non-ascii code, this length could be invalid
            with open('eeprom.bin', 'wb+') as f:
                # f.write(eeprom_head)
                # f.seek(0x300)
                f.write(eeprom_cache)
                # f.seek(0x400)
                # f.write(eeprom_tail)
            print('The device ID will be %02x%02x-%02x%02x' % (eeprom_cache[1], eeprom_cache[2], eeprom_cache[3], eeprom_cache[4]))
            input('Plug one PUMP device in and press ENTER to continue, or Ctrl-C to quit: ')
            while os.system('python.exe .\\esptool.py -p %s -b %d write_flash 0x0 boot.bin 0x%x %s 0xa000 ota.bin 0x%x %s' % (
                download_config['serial_port'], download_config['serial_speed'], ADDR_EEPROM, EEPROM_PATH, ADDR_FW, FW_PUMP_PATH
            )):
                try:
                    input('Download failed! Press ENTER to continue, or Ctrl-C to skip: ')
                except KeyboardInterrupt:
                    print('cancelled.')
                    break
            ''' download by invoking esptool methods
            with open(EEPROM_PATH, 'rb') as f_eeprom, open(FW_PUMP_PATH, 'rb') as f_fw:
                args = download_args([(ADDR_EEPROM, f_eeprom), (ADDR_FW, f_fw)])
                # esp = esptool.ESPLoader.detect_chip(args.port, 115200, 'default_reset')
                esp = esptool.ESP32ROM(download_config['serial_port'], 115200)
                esp.connect()
                esp.run_stub()
                esp.change_baud(download_config['serial_speed'])
                esp.flash_spi_attach(args.ucIsHspi,args.ucIsLegacy)
                esptool.detect_flash_size(esp, args)
                esp.flash_set_parameters(esptool.flash_size_bytes(args.flash_size))
                esptool.write_flash(esp, args)
            '''
            input('Plug one TANK device in and press ENTER to continue, or Ctrl-C to quit: ')
            while os.system('python.exe .\\esptool.py -p %s -b %d write_flash 0x0 boot.bin 0x%x %s 0xa000 ota.bin 0x%x %s' % (
                download_config['serial_port'], download_config['serial_speed'], ADDR_EEPROM, EEPROM_PATH, ADDR_FW, FW_TANK_PATH
            )):
                try:
                    input('Download failed! Press ENTER to continue, or Ctrl-C to skip: ')
                except KeyboardInterrupt:
                    print('cancelled.')
                    break

            ''' download by invoking esptool methods
            with open(EEPROM_PATH, 'rb') as f_eeprom, open(FW_PUMP_PATH, 'rb') as f_fw:
                args = download_args([(ADDR_EEPROM, f_eeprom), (ADDR_FW, f_fw)])
                esp = esptool.ESP32ROM(download_config['serial_port'], 115200)
                esp.connect()
                esp.run_stub()
                esp.change_baud(download_config['serial_speed'])
                esp.flash_spi_attach(args.ucIsHspi,args.ucIsLegacy)
                esptool.detect_flash_size(esp, args)
                esp.flash_set_parameters(esptool.flash_size_bytes(args.flash_size))
                esptool.write_flash(esp, args)
            '''
            input('Press ENTER to continue, or Ctrl-C to quit.')
    except KeyboardInterrupt:
        print('cancelled.')
        print('Quit downloader.')
