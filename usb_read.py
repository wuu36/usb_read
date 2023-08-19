'''
pip install pyserial is needed
'''
import click
import serial
from serial.tools import list_ports
from msvcrt import getch
import threading
from collections import deque

'''
defination:
baudrate,parity,stopbits
'''

BAUDRATE    = 115200
PARITY      = 'N'
STOPBITS    = 1


def run(port, baudrate, parity='N', stopbits=1):
    try:
        device = serial.Serial(port=port,
                                baudrate=baudrate,
                                bytesize=8,
                                parity=parity,
                                stopbits=stopbits,
                                timeout=0.1)
    except:
        print('--- Failed to open {} ---'.format(port))
        return 0
    print('--- {} is connected. Press Ctrl+C to quit ---'.format(port))
    queue = deque()
    def read_input(): 
        while device.is_open:
            ch = getch()
            # print(ch)
            if ch == b'\x03':
                break
            else:
                queue.append(ch)

    thread = threading.Thread(target=read_input)
    thread.start()
    while thread.is_alive():
        #if disconnected from usb, break, use try except
        try:
            line = device.readline()
            if line:
                print(line.decode(),end='', flush=True)
        except IOError:
            print('--- {} is disconnected ---'.format(port))
            break
        # print("tread running")
        # line = device.readline()
        # if line:
        #     # print(line)
        #     # print(line.decode(), end='')
        #     print(line.decode(errors='replace'), end='',flush=True)  

    device.close()
    print('--- {} is closed ---'.format(port)) 
    if thread.is_alive():
        print('--- Press R to reconnect the device, otherwise to exit ---')
        thread.join()
        # print(queue[-1])
        if queue[-1] in (b'r', b'R'):
            return 1
        # # print(queue[0])
        # if getch() == b'r' or b'R':
        #     return 1

    return 0

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-p', '--port', default=None, help='serial port name')
@click.option('-b', '--baudrate', default=BAUDRATE, help='set baud reate')
@click.option('--parity', default=PARITY, type=click.Choice(['N', 'E', 'O', 'S', 'M']), help='set parity')
@click.option('-s', '--stopbits', default=STOPBITS, help='set stop bits')
@click.option('-l', is_flag=True, help='list serial ports')
def main(port, baudrate, parity, stopbits, l):
    if port is None:
        ports = list_ports.comports()
        if not ports:
            print('--- No serial port available ---')
            return
        if len(ports) == 1:
            port = ports[0][0]
            # print(type(ports))
            # print(port)
            print('--- One Ports ----')
        else:
            print('--- Available Ports ----')
            for i, v in enumerate(ports):
                print('---  {}: {} {}'.format(i, v[0], v[2]))
            if l:
                return
            raw = input('--- Select port index: ')
            try:
                n = int(raw)
                port = ports[n][0]
            except:
                return
        while run(port, baudrate, parity, stopbits):
            pass

        # print(port)
        # print(baudrate)
        # print(ports)


if __name__ == "__main__":
    # print(123)
    main()