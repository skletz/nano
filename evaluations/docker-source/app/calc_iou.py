#!/usr/bin/env python3
import os
import sys
import utils
import csv
import collections
from BoundingBox import BoundingBox
from User import User
import config

def get_tool_from_file(fileName):
    if "_gt.txt" in fileName:
        return config.Tool.DARKLABEL
    if "output_" in fileName:
        return config.Tool.VATIC
    if "groundtruth.txt" in fileName:
        return config.Tool.AIBU
    return "None"


def get_bb(fp, frame, toolName):
    undo_pos = fp.tell()
    line = fp.readline()

    # create default invalid bbox (aibu format for no bbx frames)
    no_annot_bb = BoundingBox("", "", frame)

    # aibu
    if toolName == config.Tool.AIBU:
        # no need for line check
        return BoundingBox(line, toolName, frame)

    # darklabel
    if toolName == config.Tool.DARKLABEL:
        parts = line.split(",")
        if parts[0] == str(frame):
            return BoundingBox(line, toolName)

    # vatic
    if toolName == config.Tool.VATIC:
        if "<annotation>" in line:
            undo_pos = fp.tell()
            line = fp.readline()
        if "<object>" in line:
            undo_pos = fp.tell()
            line = fp.readline()
        if "<t>" + str(frame) + "</t>" in line:
            return BoundingBox(line, toolName)
    # wrong framenumber or other error
    fp.seek(undo_pos)  # undo last read
    return no_annot_bb


def is_skip_frame(video, frameNr):
    rangeList = config.OBJECT_INVISIBLE_RANGES[video]
    for i in range(0, len(rangeList), 2):
        if frameNr >= rangeList[i] and frameNr <= rangeList[i + 1]:
            return True


def print_user(user):
    print("------------- USER " + str(user_id) + " --------------")
    for video in config.Video:
        print("%s: #ious %d, avg %.3f" % (video.value,
                                          len(user.iouList[video]),
                                          user.calc_avg(video)))
    print("------------------------------------")


def get_user_score(gtFiles, userFiles, user_id):
    user = User(user_id)

    for gt_file in gtFiles:
        gtToolName = get_tool_from_file(gt_file)
        if gtToolName not in config.Tool:
            # skip invalid files
            return
        for uFile in userFiles:
            uToolName = get_tool_from_file(uFile)
            if uToolName not in config.Tool:
                # skip invalid files
                continue
            for video in config.Video:
                video_string = video.value
                if video_string in gt_file and video_string in uFile:
                    gtFileObject = utils.open_file_reading(gt_file)
                    uFileObject = utils.open_file_reading(uFile)
                    user.set_tool(uToolName)
                    # interrupted frame by frame reading for all possible frame numbers
                    for i in range(0, config.VIDEO_FRAME_MAP[video]):
                        if (is_skip_frame(video, i)):
                            # skip frame: object totally occluded, out of view
                            continue
                        gtBB = get_bb(gtFileObject, i, gtToolName)
                        uBB = get_bb(uFileObject, i, user.tool)
                        iou = gtBB.iou(uBB)
                        user.add_iou(iou, video)
                    gtFileObject.close()
                    uFileObject.close()
    return user


# main
def run():
    # read input
    gt_root = config.IN_ANNOTATIONS + "/gt"
    user_root = config.IN_ANNOTATIONS + "/users"
    gt_file_paths = utils.get_file_paths(gt_root)
    user_tool_paths = utils.get_immediate_subdirs(user_root)
    if len(list(gt_file_paths)) < 1 or len(list(user_tool_paths)) < 1:
        return {"success": False, "message": "missing inputs"}

    tool_userpaths = {}  # all user folders per tool
    for path in user_tool_paths:
        tool_userpaths[utils.get_last_subdir(path)] = utils.get_immediate_subdirs(path)

    if len(tool_userpaths) < 1:
        return {"success": False, "message": "Could not fetch user data"}

    # calculate user IoU scores
    users = []
    for tool_label, user_folders in tool_userpaths.items():
        for folder in user_folders:
            user_id = utils.get_last_subdir(folder)
            userFiles = utils.get_file_paths(folder)
            users.append(get_user_score(gt_file_paths, userFiles, user_id))
            # print_user(users[len(users) - 1])  # print current user

    if len(users) < 1:
        return {"success": False, "message": "Failed calculating IOUs."}

    # write IoU score output files
    # sort users according to id
    users.sort(key=lambda x: int(x.id), reverse=False)
    # open out file
    utils.make_dir(config.OUT_IOU_DIR)
    outfile = config.OUT_IOU_DIR + "/" + config.OUT_IOU_FILE + "." + config.OUT_CSV_EXT
    fp = utils.open_file_writing(outfile, True)
    # write csv header
    fp.write("user,tool")
    for video in config.Video:
        fp.write("," + video.value)
    fp.write("\n")

    # write csv lines & finish
    for user in users:
        fp.write(str(user.id) + "," + user.tool.value)
        for video in config.Video:
            fp.write("," + str(user.calc_avg(video)))
        fp.write("\n")
    fp.close()
    return {"success": True, "message": "Wrote " + outfile}
# main
