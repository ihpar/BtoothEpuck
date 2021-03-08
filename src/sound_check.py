import numpy as np
import sounddevice
import time


def file_to_sound(file_path):
    lst = []
    with open(file_path) as src:
        lines = src.read().splitlines()
        cnt = 0
        for line in lines:
            if not line.startswith('.hword'):
                continue
            hexa = line.split(' ')[1]
            num = int(hexa, 16)
            lst.append(num)
    lst = np.array(lst)
    print(np.min(lst), np.max(lst))
    lst = (lst / np.max(lst)) * 0.5
    lst = (lst * 32768).astype(np.int16)
    sounddevice.play(lst, 7200)
    time.sleep(5)


def np_sound_to_file(np_src, tar_file):
    res = (np_src + 1) * (2 ** 13)
    res = np.concatenate((res, np.zeros(8000)), axis=None)
    res = res.astype(int)
    # print(np.min(res), np.max(res))
    with open(tar_file, 'w') as f:
        f.write('.section .sound_samples,code\n')
        f.write('.global e_sound_sample\n')
        f.write('.palign 2\n')
        f.write('e_sound_sample:\n')
        for el in res:
            hexa = '.hword 0x' + '{:04X}'.format(el)
            f.write(hexa + '\n')


def make_sound_one():
    fs = 8000  # Hz
    T = 1.0  # second
    freqs = [440, 880]
    t = np.arange(0, T, 1 / fs)
    x = np.sin(2 * np.pi * freqs[0] * t)
    y = np.sin(2 * np.pi * freqs[1] * t)

    res = np.concatenate((x, y), axis=None)

    # sounddevice.play(res, fs)
    # time.sleep(2)

    np_sound_to_file(res, 'one.s')


def ex_one():
    fs = 8000  # Hz
    T = 1.  # second
    freq = 880
    t = np.arange(0, T, 1 / fs)
    x = 0.5 * np.sin(2 * np.pi * freq * t)  # 0.5 is arbitrary to avoid clipping sound card DAC
    x = (x * 32768).astype(np.int16)  # scale to int16 for sound card
    print(np.max(x))
    sounddevice.play(x, fs)  # releases GIL
    time.sleep(1)  # NOTE: Since sound playback is async, allow sound playback to finish before Python exits


def main():
    file_to_sound('C:/Users/istir/Desktop/e_const_sound - Copy.s')
    # ex_one()
    # make_sound_one()


if __name__ == '__main__':
    main()
