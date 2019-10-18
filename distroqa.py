#!/usr/bin/env python3

# Copyright © 2019 Collabora Ltd.
#
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import argparse
import datetime
import time
import math
import os
import sys
import oyaml as yaml
import random
from pyscreeze import ImageNotFoundException
from timeit import default_timer as timeit_timer

from fabric.api import *
env.hosts = "localhost"
env.port = "2222"
# Update username and password if you plan to use `.sh` action in `.yaml` file.
env.user = "username"
env.password = "password"

os.environ['DISPLAY'] = ":1.0"
hostname = os.getenv('HOSTNAME')

import pyautogui

opts = argparse.ArgumentParser()
opts.add_argument('--taskfile', action="store", dest="task_file", type=str, required=True)
opts.add_argument("--no_verbose", dest="no_verbose", default=False, action="store_true")

# parse the command line
args = opts.parse_args()

TASK_FILE = args.task_file
NO_VERBOSE = args.no_verbose
RESULT_DIR = "/testresults/" + hostname + "/" + TASK_FILE.split('.')[0] + "/"
RETRY = 10
RETRY_WAIT_SECONDS = 60
TEST_STATUS = "/testresults/" + hostname + "/" + "test_failed"
wait_time = 0


def run_script(fn, timer=1):
        with settings(host_string=env.hosts, warn_only=True):
            put(fn, "/tmp/", use_sudo=True)
            fn = os.path.basename(fn)
            run("chmod +x /tmp/"+fn)
            run("/tmp/"+fn)

def abort_tests(img):
        with open(TEST_STATUS, 'w') as fd:
            content = "Unable to locate image: " + img + " listed on " + TASK_FILE
            fd.write(content)
        time.sleep(1)


def status_ok():
        if (os.path.exists(TEST_STATUS)):
            print("Abort test due to previous errors")
            return False
        return True


def findimage_and_click(img, timer=1, use_grayscale=True, retry=RETRY):
    try:
        perform_click = True
        image_status = True
        global wait_time

        if timer < 0:
             perform_click = False
             timer = abs(timer)
             # Wait 'n' seconds before checking for image
             countdown(timer)
        elif timer == 0:
             # search for an image for 1 hour mins at 5min interval.
             perform_click = False
             retry = RETRY
             if wait_time == 0:
                wait_time = timeit_timer()
                time_taken = 0
             else:
                cur_time = timeit_timer()
                time_taken = math.floor(cur_time) - math.floor(wait_time)
             if time_taken > 3600:
                print("Unable to Locate image %s in last %d secr, %d %d abort" % (img, time_taken, cur_time, wait_time))
                retry = 0 # quit after 1 hr
                wait_time = 0
             else:
                print("Unable to Locate image %s in last %d seconds" % (img,time_taken))

        if retry > 0:
            if use_grayscale:
                pos = pyautogui.locateOnScreen(img, grayscale=True, confidence=0.7)
            else:
                pos = pyautogui.locateOnScreen(img, confidence=0.7)

            if pos is None:
                raise ImageNotFoundException

            b = pyautogui.center(pos)
            x, y = b
            if perform_click is True:
                pyautogui.click(x, y)
                countdown(timer)
                return image_status
            else:
                pyautogui.moveTo(x, y, 2)
                return image_status
        else:
            image_status = False
            return image_status

    except ImageNotFoundException as err:
        if timer != 0:
            print("Locate image %s Retry attempt:%d" % (img, retry))
            countdown(RETRY_WAIT_SECONDS)
        else:
            countdown(0)

        retry = retry - 1
        return findimage_and_click(img, timer, use_grayscale, retry)

def countdown(timer=1):
    '''Sleep for given time. Also:
       1. Every 30 seconds move mouse when its idle.
       2. Every 300 seconds refresh remove-viewer'''
    move_mouse_cnt = 0
    time_based_search = False

    if timer == 0: # Handle special case
        timer = 300
        time_based_search = True

    for i in range(timer, 0, -1):
        if NO_VERBOSE is False:
            sys.stdout.write("\r")
            sys.stdout.write('Next action will start in ' + str(i) + ' seconds ')
            sys.stdout.flush()
        else:
            if move_mouse_cnt == 0:
                sys.stdout.write('Next action will start in ' + str(i) + ' seconds ')
        time.sleep(1)

        move_mouse_cnt = move_mouse_cnt + 1
        if move_mouse_cnt % 30 == 0:
                xcur, ycur = pyautogui.position()
                xpos = random.randint(0, 200)
                ypos = random.randint(0, 200)
                pyautogui.moveTo(xpos, ypos, duration=1)
                pyautogui.moveTo(xcur, ycur, duration=1)

        if move_mouse_cnt % 300 == 0 and time_based_search is True: # ugly workaround until we find proper way to disable timeout
                rv_img1 = "/images/baseimage/refresh_viewer/rv_sendkey_button.png"
                rv_img2 = "/images/baseimage/refresh_viewer/rv_sendkey_ctrl_alt_f5.png"
                findimage_and_click(rv_img1, 10)
                findimage_and_click(rv_img2, 10)

def run_command(fn, timer=1):
    with open(fn, 'r') as fd:
        cmds = fd.readlines()
    for cmd in cmds:
        cmd = cmd.strip("\n")
        pyautogui.typewrite(cmd, interval=0.5)
        time.sleep(1)
        pyautogui.press('enter')
    countdown(timer)

def type_script(fn, timer=1):
    with open(fn, 'r') as fd:
        cmds = fd.read().split()
    for cmd in cmds:
        if cmd.endswith(".key"):
            hit_keyboard(cmd)
        else:
            pyautogui.typewrite(cmd, interval=0.5)
        time.sleep(1)
    countdown(timer)

def type_txt(txt,timer):
    pyautogui.typewrite(txt, interval=0.2)
    time.sleep(1)
    countdown(timer)

def take_scrnshot(fname):
    pyautogui.screenshot(RESULT_DIR+fname)

def pyinstruction(ins,timer):
    ins = ins.split(".ins")[0]
    if ins == "wait" or ins == "sleep":
        countdown(timer)

def hit_keyboard(key):
    key = key.split(".key")[0]
    if "+" in key:
        if key.count("+") == 1:
            key1, key2 = key.split("+")
            pyautogui.hotkey(key1, key2)
        elif key.count("+") == 2:
            key1, key2, key3 = key.split("+")
            pyautogui.hotkey(key1, key2, key3)
        else:
            print("Unsupported Key combination")
            return False
    else:
        pyautogui.press(key)
        return True

def hit_mouse(mouse_action):
    mouse_action = mouse_action.split(".mouse")[0]

    if mouse_action == "left_double":
        pyautogui.click(clicks=2, interval=0.1, button='left')
    elif mouse_action == "right":
        pyautogui.click(clicks=1, interval=0.1, button='right')
    elif mouse_action == "right_double":
        pyautogui.click(clicks=2, interval=0.1, button='right')
    else:
        print("Unsupported Mouse event combination")
        return False

    return True

def setup_dirs():
    if not (os.path.exists("/images")):
        os.system("ln -s /test/images/ /images")

    if not (os.path.exists("/testresults")):
        os.system("ln -s /test/results/ /testresults")

def screen_recorder(action):
    os.system("mkdir -p " + RESULT_DIR)
    os.system("screen_recorder " + action + " " + TASK_FILE.split('.')[0])


def process_item(kvpair,f):
    ret = True
    start_timer = timeit_timer()
    global wait_time

    if ':' in kvpair:
        item = kvpair.split(':')[0]
        timer = int(kvpair.split(':')[1])
    else:
        item = kvpair
        timer = 0

    if item.endswith(".png"):
        ret = findimage_and_click(os.path.dirname(f) + "/" + item, timer)
        wait_time = 0
    elif item.endswith(".txt"):
        run_command(os.path.dirname(f) + "/" + item, timer)
    elif item.endswith(".type"):
        # type_script(os.path.dirname(f) + "/" + item, timer)
        type_txt(item.split(".type")[0],timer)
    elif item.endswith(".sh"):
        run_script(os.path.dirname(f) + "/" + item, timer)
    elif item.endswith(".csv"):
        mkb.replay(os.path.dirname(f) + "/" + item)
        time.sleep(timer)
    elif item.endswith(".key"):
        ret = hit_keyboard(item)
        countdown(timer)
    elif item.endswith(".mouse"):
        ret = hit_mouse(item)
        countdown(timer)
    elif item.endswith(".ins"):
        pyinstruction(item,timer)
    else:
        print("\n Unknown entry:%s" % (item))
        ret = False

    end_timer = timeit_timer()
    time_taken = math.floor(end_timer) - math.floor(start_timer)

    if ret == True:
       print(u'\r \N{check mark} %-50s : took %d seconds\n' % (item, time_taken))
    else:
       print(u'\r \N{cross mark} %-50s : took %d seconds  \n' % (item, time_taken))

    return ret
def start_gui_test():
    try:
        TASK_FILE_PATH="/test/tasks/"+TASK_FILE

        with open(TASK_FILE_PATH, 'r') as fd:
            files = fd.readlines()

        for f in files:
            if not status_ok():
                break

            f = f.strip("\n")
            f = f.rstrip(" ")
            f = "/" + f  #points to /images dir inside container
            time.sleep(0.5)
            with open(f, 'r') as stream:
                out = yaml.safe_load(stream)
                for k, v in out.items():
                    lt = v
                    print("\n")
                    print('*' * (len(str(k)) + 4))
                    # print(str(k))
                    print('* {a:<{b}} *'.format(a=str(k), b=len(str(k))))
                    print('* {a:<{b}} : {c} *'.format(a=str(k), b=len(str(k)), c=str(datetime.datetime.now()).split('.')[0]))
                    print('*' * (len(str(k)) + 4))

                    for kvpair in lt:
                        if type(kvpair) is list:  # Handle set of images
                            for img in range(len(kvpair)):
                                ret = process_item(kvpair[img], f)
                                if ret is True:
                                    print("Skip rest of the images")
                                    break
                        else:
                           ret = process_item(kvpair, f)

                        if ret is False:
                            abort_tests(str(kvpair))
                            raise Exception('Cant find Image..abort')

            take_scrnshot(os.path.basename(f)+str('.png'))
    except Exception as err:
        print(err)


def main():
    '''
      Start the GUI tests
    '''
    if not status_ok():
       return -1
    setup_dirs()
    screen_recorder("start")
    start_gui_test()
    print("Processing video please wait...")
    screen_recorder("stop")
    take_scrnshot('result.png')
    countdown(10)
    screen_recorder("speedup")
    countdown(10)
    print("\r See %s dir for test status   " % (RESULT_DIR))


if __name__ == '__main__':
    main()
