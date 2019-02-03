#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import utils
import config


class User:
    """User class"""

    def __init__(self, id):
        self.id = id
        self.iouList = {}
        for val in config.Video:
            self.iouList[val] = []

        self.tool = None

    def set_tool(self, toolName):
        self.tool = toolName

    def add_iou(self, value, video):
        self.iouList[video].append(value)

    def calc_avg(self, video):
        return utils.safe_div(sum(self.iouList[video]), len(self.iouList[video]))
