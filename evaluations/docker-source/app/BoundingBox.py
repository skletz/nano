#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import config


class BoundingBox:
    """Bounding box class - Format: upperLeftPoint = x, lowerRightPoint = y"""

    def __init__(self, input_line, toolName, lineNumber=-1):

        # init bbox for invalid frames (aibu format for no bbx frames)
        # upper left coordinate
        self.x0 = float(-1)
        self.x1 = float(-1)
        # lower right coordinate
        self.y0 = self.x0 + float(1)
        self.y1 = self.x1 + float(1)
        # frame number
        self.frame = lineNumber

        if input_line == "":
            return

        if toolName == config.Tool.DARKLABEL:
            self.init_from_darklabel(input_line)
        if toolName == config.Tool.VATIC:
            self.init_from_vatic(input_line)
        if toolName == config.Tool.AIBU:
            self.init_from_aibu(input_line)

    # format(leftCorner): frameNumber,numBoxes,x,y,w,h
    def init_from_darklabel(self, input_line):
        parts = input_line.split(",")
        self.frame = int(parts[0])
        # self.numBoxes = parts[1]
        self.x0 = float(parts[2])
        self.x1 = float(parts[3])
        # calc lower right point
        self.y0 = self.x0 + float(parts[4])
        self.y1 = self.x1 + float(parts[5])

    # format(leftCorner): x,y,w,h
    def init_from_aibu(self, input_line):
        parts = input_line.split(",")
        self.x0 = float(parts[0])
        self.x1 = float(parts[1])
        # calc lower right point
        self.y0 = self.x0 + float(parts[2])
        self.y1 = self.x1 + float(parts[3])

    # format(XML: time,upperLeft,lowerLeft,lowerRight,upperRight):
    # tags: t=time, pt=point, x=xCoord, y=yCoord, l=isGroundTruth (0/1) -> keyframe for interpolation
    # e.g:
    # <polygon>
    #   <!-- time -->
    #   <t>0</t>
    #   <!-- upperLeft -->
    #   <pt>
    #       <x>576</x><y>78</y><l>1</l>
    #   </pt>
    #   ...
    # </polygon>
    def init_from_vatic(self, input_line):
        root = ET.fromstring(input_line)
        self.frame = int(root[0].text)
        self.x0 = float(root[1][0].text)
        self.x1 = float(root[1][1].text)
        # self.isKeyFrame = float(root[1][2].text)
        self.y0 = float(root[3][0].text)
        self.y1 = float(root[3][1].text)

    # originally from: https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
    # improved an corrected: https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc

    def iou(self, bbox):
        # determine the coordinates of the intersection rectangle: upper_left(xA,yA), lower_right(xB,yB)
        xA = max(self.x0, bbox.x0)
        yA = max(self.x1, bbox.x1)
        xB = min(self.y0, bbox.y0)
        yB = min(self.y1, bbox.y1)

        # compute the area of intersection rectangle: lengthX(xB-xA) * lengthY(yB-yA)
        # Adding one simply prevents the iou numerator from being zero
        interArea = abs(max((xB - xA), 0) * max((yB - yA), 0))
        if interArea == 0:
            return 0

        # compute the area of both the prediction and ground-truth rectangles
        boxAArea = abs((self.y0 - self.x0) * (self.y1 - self.x1))
        boxBArea = abs((bbox.y0 - bbox.x0) * (bbox.y1 - bbox.x1))

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        iou = interArea / float(boxAArea + boxBArea - interArea)

        # return the intersection over union value
        return iou

    def print_out(self):
        print("--- BBox ---")
        print("frame", self.frame)
        print("p1", self.x0, self.x1)
        print("p2", self.y0,  self.y1)
        print("------------")
