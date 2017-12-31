# coding: utf-8
import os
import time
import math
from PIL import Image
from PIL import ImageDraw

IMAGE_PATH = "./1.png"

STEP_LENGTH = 3


def pull_screenshot():
    os.system('adb shell screencap -p /sdcard/1.png')
    os.system('adb pull /sdcard/1.png .')


def backup_screenshot(ts):
    if not os.path.exists("screenshot_backups"):
        os.system('mkdir screenshot_backups ')
    # 为了方便失败的时候 debug
    os.system('cp 1.png screenshot_backups/{}.png'.format(ts))


def jump(distance):
    press_time = distance * 1.393
    press_time = max(press_time, 200)
    press_time = int(press_time)
    # TODO: 坐标根据截图的 size 来计算
    cmd = 'adb shell input swipe 500 1600 500 1601 ' + str(press_time)
    print cmd
    os.system(cmd)


def find_piece_and_board(im):
    w, h = im.size

    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0
    board_x = 0
    board_y = 0

    for i in range(int(h * 0.5), int(h * 0.7), STEP_LENGTH):
        for j in range(int(w * 0.06), int(w * 0.94), STEP_LENGTH):
            pixel = im.getpixel((j, i))
            # 根据棋子的最低行的颜色判断，找最后一行那些点的平均值
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                piece_x_sum += j
                piece_x_c += 1
                piece_y_max = max(i, piece_y_max)

    if not all((piece_x_sum, piece_x_c)):
        return 0, 0, 0, 0
    piece_x = piece_x_sum / piece_x_c
    piece_y = piece_y_max - 20  # 上移棋子底盘高度的一半

    draw = ImageDraw.Draw(im)
    pixelBg = im.getpixel((board_x, int(h * 0.3)))
    print("pixelBg:", pixelBg[0], pixelBg[1], pixelBg[2])
    # 255, 247, 170

    board_x, board_y = getboard(w, h, piece_x, pixelBg, draw, im)

    for x in range(piece_x - 7, piece_x + 7):
        for y in range(piece_y - 7, piece_y + 7):
            draw.point((x, y), '#ff0000')

    for x in range(board_x - 7, board_x + 7):
        for y in range(board_y - 7, board_y + 7):
            draw.point((x, y), '#00ff00')
    # im.show()
    im.save("./1.png")

    if not all((board_x, board_y)):
        return 0, 0, 0, 0

    return piece_x, piece_y, board_x, board_y


def getboard(w, h, piece_x, pixelBg, draw, im):
    for y in range(int(h * 0.3), int(h * 0.8), STEP_LENGTH):
        for x in range(0, w, STEP_LENGTH):
            if x in range(piece_x - 40, piece_x + 40):
                if y in range(int(h * 0.3), int(h * 0.8), STEP_LENGTH):
                    draw.line((x, int(h * 0.3), x, int(h * 0.8)), pixelBg, STEP_LENGTH)
                continue
            pixel = im.getpixel((x, y))
            if abs(pixelBg[0] - pixel[0]) > 10 or abs(pixelBg[1] - pixel[1]) > 10 or abs(pixelBg[2] - pixel[2]) > 15:
                # draw.line((0, i, w, i), '#000000', 1)
                print(x, y, pixel[0], pixel[1], pixel[2])
                board_y = y + 30
                board_x = x
                return board_x, board_y
    return 0, 0


def main():
    while True:
        pull_screenshot()
        im = Image.open(IMAGE_PATH)
        # 获取棋子和 board 的位置
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
        ts = int(time.time())
        print("result:", ts, piece_x, piece_y, board_x, board_y)
        jump(math.sqrt(abs(board_x - piece_x) ** 2 + abs(board_y - piece_y) ** 2))
        backup_screenshot(ts)
        time.sleep(2.4)  # 为了保证截图的时候应落稳了，多延迟一会儿


def test():
    im = Image.open("./error1.png")
    # 获取棋子和 board 的位置
    piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
    print("test result:", piece_x, piece_y, board_x, board_y)


if __name__ == '__main__':
    main()
    # test()
