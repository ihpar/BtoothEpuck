from robot import Robot
from threading import Thread, Lock, Event
import random

idle_robots, listener_robots, speaker_robots = [], [], []
previous_listeners = [-1, -1]
thanos_snap = False
num_complete_tasks = 0
num_robots = 0
num_connected_robots = 0

thread_lock = Lock()
iteration_completed = Event()
all_robots_connected = Event()

robot_main_loop_permits = []


def choose_speaker(iteration, is_random=False):
    global num_robots
    if is_random:
        speaker_index = random.randint(0, num_robots - 1)
    else:
        speaker_index = iteration % num_robots
    return [speaker_index]


def choose_listeners(iteration, is_random=False, is_balanced=False):
    global num_robots, previous_listeners
    result = []
    if is_random:
        if is_balanced:

            while True:
                listener_one = random.randint(0, num_robots - 1)
                if (listener_one not in speaker_robots) and (listener_one not in previous_listeners):
                    result.append(listener_one)
                    break

            while True:
                listener_two = random.randint(0, num_robots - 1)
                if (listener_two not in speaker_robots) and (listener_two not in previous_listeners) and (listener_two not in result):
                    result.append(listener_two)
                    break
            previous_listeners[0] = result[0]
            previous_listeners[1] = result[1]
        else:
            listener_one = speaker_robots[0]
            while listener_one in speaker_robots:
                listener_one = random.randint(0, num_robots - 1)
            result.append(listener_one)

            listener_two = speaker_robots[0]
            while (listener_two in speaker_robots) or (listener_two == listener_one):
                listener_two = random.randint(0, num_robots - 1)
            result.append(listener_two)
    else:
        listener_one = (iteration + 1) % num_robots
        listener_two = (iteration - 1) % num_robots
        result.append(listener_one)
        result.append(listener_two)
    # return result
    return [listener_one]


def choose_idles(iteration, is_random=False):
    result = []
    if is_random:
        for i in range(num_robots):
            if (i in listener_robots) or (i in speaker_robots):
                continue
            result.append(i)
    else:
        idle_index_one = (iteration + 2) % num_robots
        idle_index_two = (iteration + 3) % num_robots
        idle_index_three = (iteration + 4) % num_robots
        result.append(idle_index_one)
        result.append(idle_index_two)
        result.append(idle_index_three)
    # return result
    return [-1]


def manage_robot(robot, robot_index):
    global num_complete_tasks, num_robots, num_connected_robots
    robot.set_q_loc(robot_index)
    robot.connect()

    # initial acknowledgement
    robot.send_message("T")
    print(robot.get_message())

    # robot.set_status('i')
    # msg = ''
    # while 'X' not in msg:
    #    msg = robot.get_message()

    # sending random seed
    robot.send_message(f"r{random.randint(1, 999)}T")
    msg = ''
    while 'X' not in msg:
        msg = robot.get_message()
    print(msg)

    # initial sync
    thread_lock.acquire()
    num_connected_robots += 1
    if num_connected_robots == num_robots:
        all_robots_connected.set()
    thread_lock.release()

    all_robots_connected.wait()

    i = 0
    while True:
        robot_main_loop_permits[robot_index].wait()
        if thanos_snap:
            break

        msg = f'Pass {i}\n'

        if robot_index in idle_robots:
            robot.set_status('iT')
        elif robot_index in listener_robots:
            robot.set_status('lT')
        elif robot_index in speaker_robots:
            robot.set_status('sT')

        while 'X' not in msg:
            msg += robot.get_message()
        robot.add_message_log_entry(msg + "\n")
        print('========================')
        print(f'{robot.get_name()}')
        print(msg)

        thread_lock.acquire()

        robot_main_loop_permits[robot_index].clear()
        num_complete_tasks += 1
        if num_complete_tasks == num_robots:
            iteration_completed.set()

        thread_lock.release()
        i += 1

    robot.dump_message_log()
    robot.disconnect()


def init_threads(robots):
    robot_threads = []
    for i, robot in enumerate(robots):
        robot_threads.append(Thread(target=manage_robot, args=(robot, i,)))

    return robot_threads


def start_iteration():
    global num_complete_tasks
    thread_lock.acquire()
    num_complete_tasks = 0
    thread_lock.release()

    iteration_completed.clear()
    for permit in robot_main_loop_permits:
        permit.set()


def main():
    global idle_robots, listener_robots, speaker_robots, num_robots, robot_main_loop_permits, thanos_snap

    robots = [
        Robot('10:00:E8:C5:61:7E', 'e_3228'),  # 4
        Robot('10:00:E8:C5:62:03', 'e_3120')  # 5
        # Robot('10:00:E8:C5:64:34', 'e_3121'),  # 8
        # Robot('10:00:E8:C5:61:8C', 'e_3311'),  # 10
        # Robot('10:00:E8:C5:64:73', 'e_2870'),  # 11
        # Robot('10:00:E8:C5:64:75', 'e_2858')  # 14
    ]

    curr_iteration = 0
    target_iteration = 2
    num_robots = len(robots)

    for i in range(num_robots):
        robot_main_loop_permits.append(Event())
        robot_main_loop_permits[i].clear()

    all_robots_connected.clear()

    robot_threads = init_threads(robots)
    for thread in robot_threads:
        thread.start()

    while curr_iteration < (target_iteration * num_robots):
        print(f'++++++++++ Loop No {round(100 * curr_iteration / num_robots) / 100} ++++++++++')

        speaker_robots = choose_speaker(curr_iteration)
        listener_robots = choose_listeners(curr_iteration, is_random=False, is_balanced=False)
        idle_robots = choose_idles(curr_iteration, is_random=False)

        start_iteration()
        iteration_completed.wait()
        curr_iteration += 1

    for permit in robot_main_loop_permits:
        permit.set()

    thanos_snap = True

    for thread in robot_threads:
        thread.join()

    print('Exiting main...')


if __name__ == '__main__':
    main()
