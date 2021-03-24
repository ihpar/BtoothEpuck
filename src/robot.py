from bluetooth import *


class Robot:
    def __init__(self, mac_addr, name):
        self._mac_addr = mac_addr
        self._name = name
        self._sock = None
        self._status = None
        self._message_log = []
        self._queue_loc = 0

    def get_name(self):
        return f'{self._name}'

    def set_q_loc(self, no):
        self._queue_loc = no

    def connect(self):
        self._sock = BluetoothSocket(RFCOMM)
        self._sock.connect((self._mac_addr, 1))
        self._sock.settimeout(60)
        print(f'{self.get_name()} connected')

    def send_message(self, message):
        self._sock.send(f'{message}\n')

    def get_message(self):
        data = self._sock.recv(1024 * 1024)
        data = data.decode('ascii')
        return data

    def add_message_log_entry(self, msg):
        self._message_log.append(msg)

    def set_status(self, status):
        self._status = status
        self.send_message(status)

    def get_status(self):
        return self._status

    def dump_message_log(self):
        with open('log_' + self.get_name() + '.txt', 'w') as log_file:
            log_file.write(f'I am {self.get_name()}' + '\n')
            log_file.write(f'I am no {self._queue_loc} at the queue' + '\n\n')

            for message in self._message_log:
                log_file.write(message + '\n')

    def disconnect(self):
        self._sock.close()
        print(f'{self.get_name()} disconnected')
