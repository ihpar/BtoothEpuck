from bluetooth import *
import numpy as np
import matplotlib.pyplot as plt, mpld3
import threading

mutex = threading.Lock()

thread_list = []
data_dict = {}
it = 0


def find_devs():
    print("performing inquiry...")

    nearby_devices = discover_devices(lookup_names=True)

    print("found %d devices" % len(nearby_devices))

    for name, addr in nearby_devices:
        print("%s - %s" % (addr, name))


def read_from(listener_addr):
    started = False
    d_list = []
    with open('mic_data', 'w') as f:
        print('Creating sock...')
        server_socket = BluetoothSocket(RFCOMM)
        server_socket.connect((listener_addr, 1))
        server_socket.settimeout(15)

        i = 0
        while i < 500:
            data = server_socket.recv(4096)
            d_list.append(data.decode('ascii'))
            i += 1
            if not started:
                print('Started')
                started = True

        server_socket.close()

        for d in d_list:
            f.write(d)

        print('Done')


def read_states(listener_addr):
    d_list = []
    with open('state_data', 'w') as f:
        print('Creating sock...')
        server_socket = BluetoothSocket(RFCOMM)
        server_socket.connect((listener_addr, 1))
        server_socket.settimeout(30)

        while True:
            data = server_socket.recv(64)
            d = data.decode('ascii')
            print('data:', d)
            d_list.append(d)
            print(d)
            if 'FIN' in d:
                break

        server_socket.close()

        for d in d_list:
            f.write(d)

        print('Done')


def show_data():
    mic_vals = []
    with open('mic_data', 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            vals = line.split(',')
            for val in vals:
                mic_vals.append(int(val))

    plt.plot(mic_vals[945:975])
    plt.title('Mics')
    plt.ylabel('Mic 0')

    plt.show()


def show_states():
    states = []
    dur = 0
    with open('state_data_0', 'r') as f:
        lines = f.read().splitlines()
        i = -1
        for line in lines:
            if 'C:' in line:
                i += 1
                states.append([])
                dur = 0
            elif 'done' in line or 'M:' in line:
                continue
            else:
                vals = line.split(',')
                dur += int(vals[1])
                states[i].append({'d': dur, 's': int(vals[0])})

    plot_cnt = len(states)
    i = 0
    plt.figure(figsize=(18, plot_cnt * 3))
    for e in states:
        print(e)
        i += 1
        chart = np.zeros(e[-1]['d'])
        start, end = 0, 0
        for ds in e:
            if ds['s'] == 1:
                start = ds['d']
            else:
                end = ds['d']
                chart[start:end] = 1

        plt.subplot(plot_cnt, 1, i)
        plt.plot(chart)
        plt.title('Sample ' + str(i))
        plt.ylabel('State')

    mpld3.show()


def test_truth(curr_letter, codes, by_latter=False):
    true_cnt, false_cnt = 0, 0
    if not by_latter:
        (k, v), = codes[curr_letter].items()
    else:
        for e in codes:
            (k, v), = e.items()
            if k == curr_letter:
                break
    msg = 'M: ' + ', '.join(str(x) for x in v)
    with open('code_' + str(curr_letter), 'r') as f:
        lines = f.read().splitlines()

        for line in lines:
            if not line.startswith('M:'):
                continue
            if line == msg:
                true_cnt += 1
            else:
                false_cnt += 1
                print(line)
        print(true_cnt, false_cnt)
    return true_cnt, false_cnt


def listen_dev(addr):
    global it
    data_dict[addr] = []

    server_socket = BluetoothSocket(RFCOMM)
    server_socket.connect((addr, 1))
    server_socket.settimeout(30)

    while True:
        data = server_socket.recv(64)
        d = data.decode('ascii')
        mutex.acquire(True)
        try:
            data_dict[addr].append(d)
            print(str(it), d)
            it += 1
        finally:
            mutex.release()
        if 'F' in d:
            break

    server_socket.close()


def listen_devs(addr_lst, curr_letter):
    for addr in addr_lst:
        thread = threading.Thread(target=listen_dev, args=(addr,))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

    return False
    with open('new_code_noise_20_' + str(curr_letter), 'w') as f:
        for addr in addr_lst:
            f.write('ADD:' + addr + '\n')
            for data in data_dict[addr]:
                f.write(data)


def main():
    # find_devs()
    e_3120 = '10:00:E8:C5:62:03'
    e_3228 = '10:00:E8:C5:61:7E'

    codes = [
        {'A': [1, 2, -1, -1, -1, -1]},
        {'B': [2, 1, 1, 1, -1, -1]},
        {'C': [2, 1, 2, 1, -1, -1]},
        {'D': [2, 1, 1, -1, -1, -1]},
        {'E': [1, -1, -1, -1, -1, -1]},
        {'F': [1, 1, 2, 1, -1, -1]},
        {'G': [2, 2, 1, -1, -1, -1]},
        {'H': [1, 1, 1, 1, -1, -1]},
        {'I': [1, 1, -1, -1, -1, -1]},
        {'J': [1, 2, 2, 2, -1, -1]},
        {'K': [2, 1, 2, -1, -1, -1]},
        {'L': [1, 2, 1, 1, -1, -1]},
        {'M': [2, 2, -1, -1, -1, -1]},
        {'N': [2, 1, -1, -1, -1, -1]},
        {'O': [2, 2, 2, -1, -1, -1]},
        {'P': [1, 2, 2, 1, -1, -1]},
        {'Q': [2, 2, 1, 2, -1, -1]},
        {'R': [1, 2, 1, -1, -1, -1]},
        {'S': [1, 1, 1, -1, -1, -1]},
        {'T': [2, -1, -1, -1, -1, -1]},
        {'U': [1, 1, 2, -1, -1, -1]},
        {'V': [1, 1, 1, 2, -1, -1]},
        {'W': [1, 2, 2, -1, -1, -1]},
        {'X': [2, 1, 1, 2, -1, -1]},
        {'Y': [2, 1, 2, 2, -1, -1]},
        {'Z': [2, 2, 1, 1, -1, -1]}
    ]

    curr_letter = 'T'
    listen_devs([e_3120, e_3228], curr_letter)
    # test_truth(curr_letter, codes, True)
    '''
    for i, e in enumerate(codes):
        t, f = test_truth(i, codes)
        (letter, durs), = e.items()
        print(letter, t, f)

    '''
    # read_from('10:00:E8:C5:61:7E')  # 3228
    # show_data()
    # read_states('10:00:E8:C5:61:7E')
    # show_states()


if __name__ == '__main__':
    main()
