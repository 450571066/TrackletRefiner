import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
import time
from operator import itemgetter
from utils import *
import math

###
# global variables
###
length = 5
sel = 0
merge = False
show_list = []
# the confirmed stack contains all processed tracklets
confirmed_stack = []
# recording the current tracklet in order to do the processing
current_tracklet = None
count = 0
# if close == True, end the program
close = False
# if flag == True, end the current tracklet loop
flag = False
# TODO: the number of frame of time interval to process, 500 as default
time_interval = 500
# TODO: the number of frame of time overlap between adjacent time interval, 100 as default
time_overlap = 100

# TODO: the inpath for the video, should change to your directory

# inpath_name = get_next_video("merg")
# if not inpath_name:
# close = True
# inpath, filename = inpath_name

inpath = "C:/Users/pv/Desktop/MobaXterm Downloads/Merge/splited_MOT_files"
filename = "shopSideSquare_Drone"


###
# tkinter functions
###

def show(input_list1, input_list2):
    time1: float = time.time()

    window = tk.Tk()
    window.title('Merge GUI')
    # TODO: set window's size, 1920 * 1080 as default
    width = 1200
    height = 150 * (len(input_list2) + 1) + 100
    window.geometry('{}x{}'.format(width, height))

    window.resizable(True, True)


    canvas = Canvas(window, width=1400, height=1400, scrollregion=(0, 0, width, height+100))
    scrollbar = Scrollbar(window, orient=VERTICAL)

    scrollbar.pack(side=RIGHT, fill=Y)
    scrollbar.config(command=canvas.yview)

    frame_1 = Frame(canvas)
    frame_1.pack(side=LEFT, fill=BOTH, expand=False)
    frame_2 = Frame(canvas)
    frame_2.pack(side=RIGHT, padx=0, expand=True)

    canvas.pack(expand=True, fill=BOTH)
    canvas.config(yscrollcommand=scrollbar.set)

    canvas.create_window(0, 0, window=frame_2, anchor=NW)

    # the click on method for exit "X" button, will end the program directly
    def on_closing():
        global close
        close = True
        window.destroy()

    # the click on method for confirm, will submit "sel" to the backend system and break the tracklet
    def same():
        global check_list
        for i in range(len(var_list)):
            if var_list[i].get():
                check_list.append(i)
        # we will build a new window for next few images
        window.destroy()

    time2 = time.time()
    print("Generate buttons: {:.5f}".format(time2 - time1))
    tk.Button(canvas, text="confirm", command=same).pack(side=LEFT, padx=260)
    window.protocol("WM_DELETE_WINDOW", on_closing)

    # img_list is to contain all the intermediate label
    img_list1 = []
    # TODO: default value for initial gap to the top, could change here to fit your screen
    # all constants here could be changed
    total_height = 20
    max_height = 0
    total_width = 0
    width = 0
    for i in range(len(input_list1)):
        # record the width for the image
        width = input_list1[i][1] + 50
        max_height = max(max_height, input_list1[i][2])
        # create all the image labels
        img_list1.append(ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(input_list1[i][0], cv2.COLOR_BGR2RGB))))
        # put all the images on the window
        tk.Label(canvas, image=img_list1[i]).place(x=total_width, y=total_height)
        # compute the width for next image
        total_width += width

    time3 = time.time()
    print("Generate left column of images: {:.5f}".format(time3 - time2))

    count = 0
    img_list2 = [[None for _ in range(20)] for _ in range(len(input_list2))]
    for j in range(len(input_list2)):
        input_list = input_list2[j]
        total_width = 600
        total_height = 20 + count * 170
        for i in range(len(input_list)):
            # record the width for the image
            width = input_list[i][1] + 50
            # create all the image labels
            img_list2[j][i] = (
                ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(input_list[i][0], cv2.COLOR_BGR2RGB))))
            # put all the images on the window
            tk.Label(frame_2, image=img_list2[j][i]).place(x=total_width, y=total_height)
            # compute the width for next image
            total_width += width
        count += 1
        time4 = time.time()
        print("Generate right column {} of images lasting: {:.5f}".format(j, time4 - time3))

    var_list = []
    chk_list = []
    for i in range(len(input_list2)):
        var_list.append(tk.IntVar())
        chk_list.append(ttk.Checkbutton(frame_2, text=str(i + 1), variable=var_list[i]))
        chk_list[i].grid(padx=550, pady=75)
    time5 = time.time()
    print("Generate check buttons: {:.5f}".format(time5 - time4))
    window.mainloop()


if __name__ == '__main__':
    if not close:
        # open the MOT text and save the splitted value to a list
        f = open("{}/{}.txt".format(inpath, filename), "r")
        # f = open("splited_MOT_files/{}.txt".format(filename), "r")
        b = [i.split() for i in f.readlines()]

        # open a video reader
        cap = cv2.VideoCapture("{}/{}.mp4".format(inpath, filename))
        # get total frame numbers
        current_time = time_interval
        frame_num = 100  # int(cap.get(7))
        id_dict = {}
        frame_dict = {}
        MAX = 0

        # here use a dictionary to save all same tag image in the same list
        for n in b:
            # n[1] is the tag for the image
            index = n[1]
            if int(index) > MAX:
                MAX = int(index)
            if n[1] not in id_dict:
                id_dict[index] = []
            id_dict[index].append(n)

        while True:
            # initialize the start time and end time for the current time interval
            start = current_time - time_interval
            end = current_time - time_interval + time_overlap
            stack = []
            # when close == True, end the program
            if close:
                print("The GUI has been manually stopped")
                break
            # put unworked tracklets into the stack when the program is not in the last iteration
            elif current_time < frame_num:
                for i in id_dict:
                    if int(id_dict[i][-1][0]) < current_time or int(id_dict[i][0][0]) < current_time:
                        stack.append(id_dict[i])
                    else:
                        break
            # put unworked tracklets into the stack when the program is in the last iteration
            elif current_time - frame_num < time_interval:
                if id_dict:
                    for i in id_dict:
                        stack.append(id_dict[i])
                else:
                    break
            else:
                break

            # remove tracklets that will be processed from the id_dict
            for item in stack:
                del id_dict[item[0][1]]

            print("The time interval you are processing is from {} to {}".format(current_time - time_interval,
                                                                                 min(current_time, frame_num)))
            # while there is still unworked tracklet in the stack, keep the loop
            while stack:
                # when close == True, end the program
                if close:
                    break
                # get the top tracklet from the unworked stack
                time1 = time.time()
                tracklet = []
                current_tracklet = stack.pop(0)
                print("CURRENT PROGRESS: {}/{}".format(current_tracklet[0][1], MAX))
                tracklet.append(current_tracklet)
                # when the confrimed stack is empty, the current tracklet will be directly appended to confirmed stack
                if not confirmed_stack:
                    confirmed_stack.append(current_tracklet)
                    continue
                indexes = []
                index = []
                # take out tracklets within the time interval to process
                for ind, i in enumerate(confirmed_stack):
                    if current_time > time_interval:
                        for bb in i:
                            if int(bb[0]) > start or int(bb[0]) < end:
                                indexes.append(i)
                                index.append(ind)
                                break
                    else:
                        indexes.append(i)
                        index.append(ind)

                # remove tracklet that to be processed from confirmed stack
                for i in indexes:
                    for ind, j in enumerate(confirmed_stack):
                        if i == j:
                            del confirmed_stack[ind]
                time2 = time.time()
                print("Generate all candidates: {:.5f}".format(time2 - time1))

                # set the flag to False at the begining of each tracklet
                flag = False
                current_bbs = get_merge_frame_index(current_tracklet, cap)
                # when tracklets within the time interval exist
                while indexes:
                    time4 = time.time()
                    if close:
                        break
                    count = 0
                    candidates = []
                    # generate all candidate tracklets to be merged
                    while indexes:
                        candidates.append(indexes.pop())
                        count += 1
                    candidate_frames = []
                    # generate displayed trackelts and show them on GUI
                    for i in candidates:
                        candidate_tracklet = i
                        time_get_frame = time.time()
                        candidate_frames.append(get_merge_frame_index(candidate_tracklet, cap))
                        print(
                            "time for retrieve one set of frame from random tracklet:{:.5f} with length {}\n    "
                            "Average time is {:.5f}".format(
                                time.time() - time_get_frame, len(candidate_frames[-1]),
                                (time.time() - time_get_frame) / len(candidate_frames[-1])))
                    check_list = []
                    show(current_bbs, candidate_frames)
                    time3 = time.time()
                    for i in range(len(candidates)):
                        if i in check_list:
                            tracklet.append(candidates[i])
                        else:
                            confirmed_stack.append(candidates[i])
                    if check_list:
                        for remaining_tracklet in indexes:
                            confirmed_stack.append(remaining_tracklet)
                        break
                    print("Time for get candidates into right place: {:.5f}".format(time.time() - time3))
                    print("\n---Time for one inner loop is {:.5f}---\n".format(time.time() - time4))

                confirmed_stack.append(elimination(interpolation(tracklet)))
                print("\n------Time for one whole loop is {:.5f}------\n".format(time.time() - time1))

                if not stack:
                    current_time += time_interval - time_overlap
                    break

        # write to the current folder
        if not close:
            f = open("C:/Users/pv/Desktop/MobaXterm Downloads/Merge/merged_MOT_files/{}.txt".format(filename), "w")
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
