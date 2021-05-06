import cv2
from tkinter import messagebox
import os
from PIL import Image
import math

# get frames for displaying according to the start position, display size and the video reader
def get_frames(start, length, cap):
    ###
    # start: start position for the video
    # length: the length for frames
    # cap: the video reader
    ###
    cap.set(cv2.CAP_PROP_POS_FRAMES, float(start-1))
    frames = []
    ret, frame = cap.read()
    count = 0
    while ret:
        # when read enough images, break the loop and return
        if count == length:
            break
        count += 1
        
        
        frames.append(frame)
        ret, frame = cap.read()
    # return end positon and the list of frames
    return start+count-1, frames

# a cache liked function, will select next unsplit or unmerged MOT file
def get_next_video(function):
    video_inpath = "Data/videosrc"
    # TODO: filed in working on files name
    # work_on = ["example1", "example2"]

    cache = "{}ed_MOT_files".format(function)
    cache_list = [i.split(".")[0] for i in os.listdir(cache)]
    folders = [i for i in os.listdir(video_inpath)]
    
    for folder in folders:
        if not folder:
            continue
        newInPath = video_inpath + "/" + folder
        for i,j,k in os.walk(newInPath):
            for file in k:
                name, _ = file.split(".")
                if name not in cache_list:# and name in work_on:
                    return newInPath, name

    messagebox.showinfo("Message", "All tracklets are {}ed, Thank you!".format(function))
    return None

def get_merge_frame_index(input_list, cap):
    length = min(5, len(input_list))
    frames = []
    
    index_list = [len(input_list) * i // length for i in range(length)]
    
    for i in index_list:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(input_list[i][0])-1)
        ret, frame = cap.read()
        m = input_list[i]
        if int(m[5]) > int(m[3]):
            up = int(m[5])
            down = int(m[3])
        else:
            continue

        if int(m[4]) > int(m[2]):
            right = int(m[4])
            left = int(m[2])
        else:
            continue
        
        bb = frame[down:up, left:right]
        # TODO: here width and height could be changed depended on your image feature
        width = 50
        height = 150
        # if you don't want to resize the image, here is the image's width and height
        # width = int(m[4]) - int(m[2])
        # height = int(m[5]) - int(m[3])

        #resize it to the give size
        bb = cv2.resize(bb, dsize=(width, height), interpolation = cv2.INTER_AREA)
        
        # add the image in to the show_list with its width and height
        frames.append([bb,width,height]) 

    return frames


def create_avi(file_inpath, video_inpath, filename):
    colors = [(255 - 20 * i, 20 * i, 20 * i) for i in range(10)]
    f = open("{}/{}.txt".format(file_inpath, filename), "r")
    print("{}/{}.mp4".format(video_inpath, filename))
    cap = cv2.VideoCapture("{}/{}.mp4".format(video_inpath, filename))
    # f = open("origin_MOT_files/circleRegion_Drone.txt", "r")
    # cap = cv2.VideoCapture("Data/videosrc/circleRegion/circleRegion_Drone.MP4")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    fps = cap.get(cv2.CAP_PROP_FPS)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    videoWriter = cv2.VideoWriter('{}/{}.avi'.format(file_inpath, filename), fourcc, fps, size)
    # videoWriter = cv2.VideoWriter('test.avi', fourcc, fps, size)
    b = [i.split() for i in f.readlines()]
    pre_frame = -1
    frame = None
    for bb in b:
        print(bb)
        pt1 = (int(bb[2]),int(bb[3]))
        pt2 = (int(bb[4]),int(bb[5]))
        cur_frame = int(bb[0])
        if cur_frame != pre_frame:
            if pre_frame != -1:
                videoWriter.write(frame)
                # print(frame.shape)
                # print out current image
                # filename = 'savedImage{bb[1]}.jpg'
                # cv2.imwrite(filename, frame)
                # break
            pre_frame = cur_frame
            ret, frame = cap.read()
            # print(ret)



        # Blue color in BGR
        color = (255, 0, 0)
        
        # Line thickness of 2 px
        thickness = 2
        
        # Using cv2.rectangle() method
        # Draw a rectangle with blue line borders of thickness of 2 px
        frame = cv2.rectangle(frame, pt1, pt2, colors[int(bb[1]) % 10], thickness)
        cv2.putText(frame, '{}'.format(bb[1]), (pt1[0], pt1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        # Displaying the image 
    videoWriter.write(frame)  
    
    # Using cv2.imwrite() method
    # Saving the image
        
        # frame = cv2.rectangle(frame,pt1,pt2,(255, 0, 0) )

def interpolation(input_lists):
    input_lists.sort(key=lambda x: int(x[0][0]))
    while len(input_lists) > 1:
        current_tracklet = input_lists.pop(0)
        candidate_tracklet = input_lists.pop(0)
        gap = int(candidate_tracklet[0][0]) - int(current_tracklet[-1][0])
        start_index = int(current_tracklet[-1][0]) + 1 
        start_bb = current_tracklet[-1][2:6]
        end_bb = candidate_tracklet[0][2:6]
        interpolate = []
        for j in range(gap-1):
            cur_index = start_index + j
            interpolate.append([str(cur_index), str(-1), 
                                str(int((1-(j+1)/gap)*int(start_bb[0])+(j+1)/gap*int(end_bb[0]))), 
                                str(int((1-(j+1)/gap)*int(start_bb[1])+(j+1)/gap*int(end_bb[1]))), 
                                str(int((1-(j+1)/gap)*int(start_bb[2])+(j+1)/gap*int(end_bb[2]))), 
                                str(int((1-(j+1)/gap)*int(start_bb[3])+(j+1)/gap*int(end_bb[3]))),
                                str(-1), str(-1), str(-1), str(-1)])
        current_tracklet += interpolate
        current_tracklet += candidate_tracklet
        
        input_lists.insert(0,current_tracklet)
    return input_lists[0]
    
# create_avi("merged_MOT_files", "Data/videosrc/circleRegion", "circleRegion_Drone")