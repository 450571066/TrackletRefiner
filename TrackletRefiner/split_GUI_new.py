import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time
from operator import itemgetter
from utils import *

###
# global variables
###

row = 15
length = row * 4
sel = 0
show_list = []
# the confirmed stack contains all processed tracklets
confirmed_stack = []
# the unworked stack, will transfer the tracklet from this stack into confirmed_stack after process
stack = []
# recording the current tracklet in order to do the processing 
current_tracklet = None
count = 0
# if close == True, end the program
close = False
# if flag == True, end the current tracklet loop
flag = False

# TODO: the inpath for the video, should change to your directory
inpath_name = get_next_video("split")
if not inpath_name:
    close = True
inpath, filename = inpath_name


# inpath = "C:/Users/pv/Desktop/MobaXterm Downloads/Merge"
# filename = "shopFrontGate_Drone2"

###
# tkinter functions
###


def show(input_list):
    ###
    # input_list = [[image, width, height, MOT_info(frame, tag, ...)],...]
    ###
    global row
    window = tk.Tk()
    window.title("{}->{}".format(",".join(input_list[0][-1][:2]), ",".join(input_list[-1][-1][:2])))
    # TODO: set window's size, 1920 * 1080 as default
    width = 1600
    height = 900
    # width = 1000
    # height = 600
    window.geometry('{}x{}'.format(width, height))
    var = tk.StringVar()

    # the click on method for selection buttons, set the selected value to "sel"
    def selection():
        global sel
        sel = int(var.get())

    # the click on method for exit "X" button, will end the program directly
    def on_closing():
        global close
        close = True
        window.destroy()

    # the click on method for confirm, will submit "sel" to the backend system and break the tracklet
    def confirm():
        global sel
        global count
        global stack
        global confirmed_stack
        global current_tracklet
        global flag

        # if no selection here
        if sel == 0:
            # call next methods to continue on this tracklet
            all_correct()
            return

        # count here is to track the length for visited part in this tracklet
        # put the second part of tracklet back into the unworked stack
        if sel + count >= len(current_tracklet):
            print(sel, count, len(current_tracklet))
            print("ERROR: SEL COUNT WRONG")
        stack.insert(0, current_tracklet[sel + count:])
        # put the first part of tracklet into the confirmed stack
        confirmed_stack.append(current_tracklet[:sel + count])
        # when flag == True, end the current tracklet loop and continue the unworked stack loop
        flag = True
        # clear the count here, because we will choose a new tracklet
        count = 0
        sel = 0
        # we will build a new window for next few images
        window.destroy()

    # the click on method for all correct, will continue on this tracklet
    def all_correct():
        global count
        global sel
        if m == current_tracklet[-1]:
            # if this is the last part for the tracklet, we will add this whole tracklet into confirmed stack and
            # continue loop on unworked stack
            confirmed_stack.append(current_tracklet)
            count = 0
        sel = 0
        window.destroy()

    # the click on method for trash, will ignore this tracklet since it may contain images that we do not want to keep
    def trash():
        global sel
        global flag
        global show_list
        # set flag to True to end this tracklet and continue on unworked stack
        if sel:
            print(sel)
            stack.insert(0, current_tracklet[sel:])
            sel = 0
        show_list = []
        flag = True
        window.destroy()

    time1 = time.time()
    check_input_list = []
    # TODO: default value for initial gap to the top, could change here to fit your screen
    # the global setting for image position
    # total_height is to decide the height for each row
    # max_height is the max size for the prev row and the next row position will depend on it
    total_height = -20
    max_height = 0

    # create all selection buttons
    for i in range(len(input_list) - 1):
        if i % row == 0:
            # when filled one row, reset all variables
            # the first selection will show after the first image of the row
            total_width = input_list[i][1] + 10
            # 20 here is the initial gap to the top
            total_height += max_height + 20
            max_height = 0
        # 50 here is global gap for all the images
        width = input_list[i][1] + 50
        # update for the max height
        max_height = max(input_list[i][2], max_height)
        # create all the selection button labels
        check_input_list.append(tk.Radiobutton(window, text=str(i + 1), variable=var, value=i + 1, command=selection))
        # put all the selection buttons
        check_input_list[i].place(x=total_width, y=total_height)
        total_width += width

    # TODO: default value for three buttons, could change here to fit your screen
    start_point = 100
    # button_height = height-50
    button_height = height - 180
    # b1 = tk.Button(window, text="All Correct", command=all_correct)
    # b1.place(x=3 * start_point, y=button_height)
    b2 = tk.Button(window, text="Confirm", command=confirm)
    b2.place(x=2 * start_point, y=button_height)
    b3 = tk.Button(window, text="Trash", command=trash)
    b3.place(x=start_point, y=button_height)
    window.protocol("WM_DELETE_WINDOW", on_closing)

    time2 = time.time()
    print("Generate all buttons: {:.5f}".format(time2 - time1))

    # img_list is to contain all the intermediate label
    img_list = []
    # TODO: default value for initial gap to the top, could change here to fit your screen
    # all constants here could be changed
    total_height = 20
    max_height = 0
    total_width = 0
    for i in range(len(input_list)):
        # record the width for the image
        width = input_list[i][1] + 50
        # find the max_height for next row
        max_height = max(input_list[i][2], max_height)
        # create all the image labels
        img_list.append(ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(input_list[i][0], cv2.COLOR_BGR2RGB))))
        if i % row == 0 and i != 0:
            # when filled the row, reset all the variables
            # for end of each row, put the first image for next line on it to compare them easily
            tk.Label(window, image=img_list[i]).place(x=total_width, y=total_height)
            total_width = 0
            total_height += max_height + 20
        # put all the images on the window
        tk.Label(window, image=img_list[i]).place(x=total_width, y=total_height)
        # compute the width for next image
        total_width += width
    # clear the show_list for next loop

    time3 = time.time()
    print("Generate all images: {:.5f}".format(time3 - time2))

    show_list.clear()
    window.mainloop()


if __name__ == '__main__':
    if not close:
        time1 = time.time()
        # open the MOT text and save the splitted value to a list
        f = open("{}/{}.txt".format(inpath, filename), "r")
        b = [i.split() for i in f.readlines()]

        # open a video reader
        cap = cv2.VideoCapture("{}/{}.mp4".format(inpath, filename))
        # get total frame numbers
        frame_num = int(cap.get(7))

        id_dict = {}

        # here use a dictionary to save all same tag image in the same list
        for n in b:
            # n[1] is the tag for the image
            index = n[1]
            if n[1] not in id_dict:
                id_dict[index] = []
            id_dict[index].append(n)

        # put all the temporary tracklet into unworked stack waiting for process
        for i in id_dict:
            stack.append(id_dict[i])

        # split all tracklet with missing frame
        cur = 0
        prev = 0
        while stack:
            flag = 0
            current_tracklet = stack.pop(0)

            prev = int(current_tracklet[0][0])
            for i in range(1, len(current_tracklet)):
                if int(current_tracklet[i][0]) - prev != 1:
                    print(current_tracklet[i], current_tracklet[i - 1])
                    confirmed_stack.append(current_tracklet[:i])
                    stack.insert(0, current_tracklet[i:])
                    flag = 1
                    break
                prev = int(current_tracklet[i][0])
            if not flag:
                confirmed_stack.append(current_tracklet)
        stack = confirmed_stack[:]
        confirmed_stack = []

        # Clean out wrong bounding box items
        while stack:
            flag = 0
            current_tracklet = stack.pop(0)
            if not current_tracklet:
                continue
            # print(current_tracklet)
            for i in range(0, len(current_tracklet)):
                m = current_tracklet[i]
                if not int(float(m[5])) > int(float(m[3])) or not int(float(m[4])) > int(float(m[2])):
                    if i != 0:
                        confirmed_stack.append(current_tracklet[:i])
                    stack.insert(0, current_tracklet[i + 1:])
                    flag = 1
                    break
            if not flag:
                confirmed_stack.append(current_tracklet)

        stack = confirmed_stack[:]
        confirmed_stack = []

        time2 = time.time()
        print("Load bounding box info to the stack and clean: {:.5f}".format(time2 - time1))

        time3 = time.time()
        # while there is still unworked tracklet in the stack, keep the loop
        while stack:
            # when close == True, end the program
            if close:
                break
            # get the top tracklet from the unworked stack
            tracklet = stack.pop(0)

            # dismiss the empty tracklet
            if not tracklet:
                continue
            current_tracklet = tracklet

            # set the flag to False at the begining of each tracklet
            flag = False

            # record the start position for the tracklet to get the frames list
            start = int(tracklet[0][0])

            # get the frames list and record the end postion for this list
            time_get_frame = time.time()
            end, frames = get_frames(start, length, cap)
            get_frame = time.time()
            print("Retrieve needed frames: {:.5f}".format(get_frame - time_get_frame))

            # loop each element in the tracklet
            for m in tracklet:
                # check if need to end the loop or program
                if flag or close:
                    # if flag == True, reset count and end this tracklet
                    count = 0
                    break

                # if this image is not in the frames list, then get a new set of frames
                if int(m[0]) > end:
                    # print(start)
                    start = int(m[0])
                    time_get_frame = time.time()
                    end, frames = get_frames(start, length, cap)
                    get_frame = time.time()
                    print("Retrieve needed frames: {:.5f}".format(get_frame - time_get_frame))

                # print the current MOT information 
                # print(m)

                # get the current frame, it will depends on which frame the video reader began to read
                if not frames:
                    print("ERROR: NOT FRAME")
                    print(m)
                    break
                frame = frames[int(m[0]) - start]
                # get the image in the bounding box
                if int(float(m[5])) > int(float(m[3])):
                    down = int(float(m[5]))
                    up = int(float(m[3]))
                else:
                    print("ERROR: WRONG BOUNDING BOX -- height")
                    print(m)
                    break

                if int(float(m[4])) > int(float(m[2])):
                    right = int(float(m[4]))
                    left = int(float(m[2]))
                else:
                    print("ERROR: WRONG BOUNDING BOX -- width")
                    print(m)
                    break

                bb = frame[up:down, left:right]
                # TODO: here width and height could be changed depended on your image feature
                width = 50
                height = 150
                # if you don't want to resize the image, here is the image's width and height
                # width = int(m[4]) - int(m[2])
                # height = int(m[5]) - int(m[3])

                # resize it to the give size
                bb = cv2.resize(bb, dsize=(width, height), interpolation=cv2.INTER_AREA)

                # add the image in to the show_list with its width and height
                show_list.append([bb, width, height, m])

                # when meet the end of the tracklet, call the show fucntion directly
                if m == tracklet[-1]:
                    # call the show function and dispaly all the images in the list
                    print(count)
                    time_for_GUI = time.time()
                    print("Time for intercept bounding box: {:.5f}".format(time_for_GUI - get_frame))
                    show(show_list)

                    time4 = time.time()
                    print("Time for display GUI: {:.5f}".format(time4 - time_for_GUI))
                    print("---Time for this epoch: {:.5f}---\n".format(time4 - time3))
                    time3 = time.time()

                    show_list = []
                    count = 0
                # if the length of show_list meet the preset length
                elif len(show_list) == length:
                    # call the show_list function and dispaly all the images in the list
                    print(count)
                    time_for_GUI = time.time()
                    print("Time for intercept bounding box: {:.5f}".format(time_for_GUI - get_frame))
                    show(show_list)

                    time4 = time.time()
                    print("Time for display GUI: {:.5f}".format(time4 - time_for_GUI))
                    print("---Time for this epoch: {:.5f}---\n".format(time4 - time3))
                    time3 = time.time()

                    show_list = [[bb, width, height, m]]
                    if m == current_tracklet[-1]:
                        show_list = []
                    if flag or close:
                        show_list = []
                    # update count for next loop
                    count += length - 1

            if show_list and len(show_list) > 1:
                print("?")
                print(count)
                time_for_GUI = time.time()
                print("Time for intercept bounding box: {:.5f}".format(time_for_GUI - get_frame))
                show(show_list)

                time4 = time.time()
                print("Time for display GUI: {:.5f}".format(time4 - time_for_GUI))
                print("---Time for this epoch: {:.5f}---\n".format(time4 - time3))
                time3 = time.time()

                show_list = []
                count = 0

        # write to the current folder
        # if not close:
        f = open("{}/splited_{}.txt".format(inpath, filename), "r")
        output_list = []
        for i in range(len(confirmed_stack)):
            for j in range(len(confirmed_stack[i])):
                temp = confirmed_stack[i][j]
                temp[1] = int(i + 1)
                temp[0] = int(temp[0])
                output_list.append(temp)
        output_list.sort()
        for i in output_list:
            i[0] = str(i[0])
            i[1] = str(i[1])
            f.write(" ".join(i))
            f.write("\n")
        f.close()
        print("Finished the txt file")
