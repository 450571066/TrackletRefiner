import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
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
# the unworked stack, will transfer the tracklet from this stack into confirmed_stack after process
stack = []
# recording the current tracklet in order to do the processing 
current_tracklet = None
count = 0
# if close == True, end the program
close = False
# if flag == True, end the current tracklet loop
flag = False
# max number of row to display candidate tracklets
# MAX_ROW = 5
MAX_ROW = 4

# TODO: the inpath for the video, should change to your directory
inpath_name = get_next_video("merg")
if not inpath_name:
    close = True
    
inpath, filename = inpath_name
# inpath = "Data/videosrc/circleRegion"
# filename = "circleRegion_Drone"


###
# tkinter functions
###

def show(input_list1, input_list2):
    time1 = time.time()

    window = tk.Tk()
    window.title('Merge GUI')
    # TODO: set window's size, 1920 * 1080 as default
    width = 1200
    height = 150 * (len(input_list2) + 1)
    window.geometry('{}x{}'.format(width,height))
    var = tk.StringVar()


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


    
    #TODO: default value for three buttons, could change here to fit your screen
    start_point = 100
    button_height = height-100
    b1 = tk.Button(window, text="confirm", command=same)
    b1.place(x=3 * start_point, y=button_height)
    time2 = time.time()
    print("Generate buttons: {:.5f}".format(time2-time1))
    
    window.protocol("WM_DELETE_WINDOW", on_closing)

    # img_list is to contain all the intermediate label
    img_list1 = []
    #TODO: default value for initial gap to the top, could change here to fit your screen
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
        img_list1.append(ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(input_list1[i][0],cv2.COLOR_BGR2RGB))))
        # put all the images on the window
        tk.Label(window, image=img_list1[i]).place(x=total_width, y=total_height)
        # compute the width for next image
        total_width += width

    time3 = time.time()
    print("Generate left column of images: {:.5f}".format(time3-time2))

    count = 0
    img_list2 = [[None for _ in range(5)] for _ in range(len(input_list2))]
    for j in range(len(input_list2)):
        input_list = input_list2[j]
        total_width = 600
        total_height = 20 + count * 170
        for i in range(len(input_list)):
            # record the width for the image
            width = input_list[i][1] + 50
            # create all the image labels
            img_list2[j][i] = (ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(input_list[i][0],cv2.COLOR_BGR2RGB))))
            # put all the images on the window
            tk.Label(window, image=img_list2[j][i]).place(x=total_width, y=total_height)
            # compute the width for next image
            total_width += width
        count += 1
        time4 = time.time()
        print("Generate right column {} of images lasting: {:.5f}".format(j, time4-time3))

    var_list = []
    chk_list = []
    for i in range(len(input_list2)):
        var_list.append(tk.IntVar())
        chk_list.append(ttk.Checkbutton(window, text=str(i+1), variable=var_list[i]))
        chk_list[i].grid(padx=550,pady=75)
    time5 = time.time()
    print("Generate check buttons: {:.5f}".format(time5-time4))
    window.mainloop()
  


if __name__ == '__main__':
    if not close:
        # open the MOT text and save the splitted value to a list
        f = open("splited_MOT_files/{}.txt".format(filename), "r")
        # f = open("splited_MOT_files/{}.txt".format(filename), "r")
        b = [i.split() for i in f.readlines()]

        # open a video reader
        cap = cv2.VideoCapture("{}/{}.MP4".format(inpath, filename))
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
        
        # while there is still unworked tracklet in the stack, keep the loop
        while stack:
            # when close == True, end the program
            if close:
                break
            # get the top tracklet from the unworked stack
            time1 = time.time()
            tracklet = []
            current_tracklet = stack.pop(0)
            tracklet.append(current_tracklet)
            
            if not stack:
                confirmed_stack.append(tracklet)
                break
            end = int(current_tracklet[-1][0])
            indexes = []
            for i in stack:
                start = int(i[0][0])
                if start > end:
                    indexes.append(i)
            for i in indexes:
                stack.remove(i)
            time2 =time.time()
            print("Generate all candidates: {:.5f}".format(time2-time1))

            # set the flag to False at the begining of each tracklet
            flag = False
            current_bbs = get_merge_frame_index(current_tracklet, cap)
            while indexes:
                time4 = time.time()
                if close:
                    break
                count = 0
                candidates = []
                while indexes and count < MAX_ROW:
                    candidates.append(indexes.pop())
                    count += 1
                candidate_frames = []
                for i in candidates:
                    candidate_tracklet = i
                    time_get_frame = time.time()
                    candidate_frames.append(get_merge_frame_index(candidate_tracklet, cap))
                    print("time for retrieve one set of frame from random tracklet:{:.5f} with length {}\n    Average time is {:.5f}".format(time.time()-time_get_frame, len(candidate_frames[-1]), (time.time()-time_get_frame)/len(candidate_frames[-1])))
                check_list = []
                show(current_bbs, candidate_frames)
                time3 = time.time()
                for i in range(len(candidates)):
                    if i in check_list:
                        tracklet.append(candidates[i])
                    else:
                        stack.append(candidates[i])
                print("Time for get candidates into right place: {:.5f}".format(time.time()-time3))
                print("\n---Time for one inner loop is {:.5f}---\n".format(time.time()-time4))

            confirmed_stack.append(interpolation(tracklet))
            print("\n------Time for one whole loop is {:.5f}------\n".format(time.time()-time1))
            

        # write to the current folder
        if not close:
            f = open("merged_MOT_files/{}.txt".format(filename), "w")
            output_list = []
            for i in range(len(confirmed_stack)):
                for j in range(len(confirmed_stack[i])):
                    temp = confirmed_stack[i][j]
                    temp[1] = int(i+1)
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


