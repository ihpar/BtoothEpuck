from robot import Robot


def main():
    robot = Robot('10:00:E8:C5:61:7E', 'e_3228')
    robot.connect()
    words = ['r63', 'i', 's', 'l',  'em ipsum dolor sit amet', 'i', 's', 'l']

    robot.send_message("T")
    print(robot.get_message())

    for ch in words:
        robot.send_message(f"{ch}T")
        msg = ""
        while "X" not in msg:
            msg += robot.get_message()
        print(msg)


if __name__ == "__main__":
    main()
