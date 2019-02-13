#!/usr/bin/python
import numpy as np
from enum import Enum

### GENERAL (check_distribution & evaluate_iou)

DEBUG_APP = False

## enums

class Tool(Enum):
    AIBU = "AIBU"
    DARKLABEL = "DarkLabel"
    VATIC = "VATIC"

class Video(Enum):
    MEDICAL = "medical"
    GAMEPLAY = "gameplay"
    PEDESTRIAN = "pedestrian"

class QuestionVideo(Enum):
    LIKE = "vLike"
    EFFORT = "vEffort"
    MOTION = "vMotion"

class QuestionTool(Enum):
    USAGE = "tUsage"
    BOXCREATION = "tBoxCreation"
    BOXMANIPULATION = "tBoxManipulation"
    tBoxPropagation = "tBoxPropagation"

class CalcByType(Enum):
    TOOL = 0
    VIDEO = 1
    VIDEO_TOOL = 2


# plotting
SHOW_QQ_PLOT = True
SHOW_BOX_PLOT = True
SHOW_SCATTER_PLOT = True
SHOW_POSTHOC_HETMAP = True
SHOW_LIKERT_PLOT = False
NUM_GTS = 1  # all GTs: -1
# default IOU correctness threshold
CORRECT_THRESH = 0.5
PLOT_CORRECT_THRESH = True


# printing
PRINT_PRECISION = 3
np.set_printoptions(suppress = True)
np.set_printoptions(precision = PRINT_PRECISION)
# np.set_printoptions(suppress=True, formatter={'float_kind':'{:0.4f}'.format})

# eval targets
TARGET_VAR = 'iou'
COMPARE_VAR = 'time'
PLOT_RANGES = {'iou': {min: 0, max: 1.0},
               'time': {min: 0, max: 400},
               'likert': {min: 1, max: 5}}

# Calculating IOU

# mapping "videoName" => number of frames
# (we start counting frames from 0, as do all 3 tools)
VIDEO_FRAME_MAP = {Video.MEDICAL: 128,
                   Video.GAMEPLAY: 125,
                   Video.PEDESTRIAN: 128}

# ranges for frames in which video-specific tracked objects are invisible
# "videoName" => [list of ranges] (pattern: [startFrame,toFrame,startFrame,toFrame,...])
OBJECT_INVISIBLE_RANGES = {Video.MEDICAL: [106, VIDEO_FRAME_MAP[Video.MEDICAL] - 1],
                           Video.GAMEPLAY: [108, 111],
                           Video.PEDESTRIAN: []}
## paths
# IN
IN_ANNOTATIONS = "./data/annotations"
IN_STUDY = "./downloads/study_data/results_tool_x_video.csv"
# OUT GENERAL
OUT_CSV_EXT = "csv"
OUT_PNG_EXT = "png"
# OUT IOU
OUT_IOU_DIR = "./downloads/iou"
OUT_IOU_FILE = "iou_avgs"
# OUT EVALS
OUT_EVALS_DIR = "./downloads/evals"
OUT_NORM_FILE = "norm"
OUT_SPEAR_FILE = "spear"
OUT_KRUSKAL_FILE = "kruskal"
OUT_ONE_WAY_ANOVA_FILE = "one_way_anova"
OUT_TTEST_FILE = "ttest"
OUT_MIXED_ANOVA_FILE = "mixed_anova"
OUT_FRIEDMAN_FILE = "friedmanchisquare"
OUT_DUNN_FILE = "posthoc_dunn"
# OUT PLOTS
OUT_PLOT_DIR = "./downloads/plot"
OUT_PLOT_FILE = "plot"

ALL_SECTIONS = ["subjective", "efficiency", "effectiveness", "correlations"]
ALL_STATISTICS = [OUT_NORM_FILE, OUT_SPEAR_FILE, OUT_KRUSKAL_FILE, OUT_ONE_WAY_ANOVA_FILE, OUT_TTEST_FILE, OUT_MIXED_ANOVA_FILE, OUT_FRIEDMAN_FILE, OUT_DUNN_FILE]
ALL_PLOTS = ["qq", "box", "scatter", "heat"]
