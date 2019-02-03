#!/usr/bin/python
import config

import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import qqplot
import seaborn as sns
import scikit_posthocs as sp
import numpy as np
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FuncFormatter

# General plotting settings
# sns.set(style="whitegrid")
# font = {'family' : 'normal', 'weight' : 'bold','size' : 'large'}
sns.set_context("paper", rc={"axes.labelsize":"x-large", "axes.weight":'bold'})
sns.set_style("whitegrid")


def saveHistPlot(data):
    for v in VIDEO_NAMES:
        plt.hist(v)
    plt.savefig(config.OUT_PLOT_DIR + "/hist_" + config.OUT_PLOT_FILE + "." + config.OUT_PNG_EXT)
    plt.close('all')

def saveScatterPlot(data, calcBy, var_target, var_compare, path):
    # figure size settings
    plt.rcParams['figure.figsize'] = (5, 5)
    fig, ax1 = plt.subplots()
    ax1.set(ylim=(config.PLOT_RANGES[var_target][min], config.PLOT_RANGES[var_target][max]))
    ax1.set(xlim=(config.PLOT_RANGES[var_compare][min], config.PLOT_RANGES[var_compare][max]))
    window_title = str("["+ calcBy.name +"]" + "["+var_target+"-"+var_compare+"]" + " - Scatter Plot")

    ylabelName = var_target
    # if var_target in config.SUBSTITUTE_STRINGS:
    #     ylabelName = config.SUBSTITUTE_STRINGS[var_target]

    if calcBy == config.CalcByType.VIDEO:
        sns.scatterplot(x=var_compare, y=var_target, hue="video", style="video", data=data).set(ylabel=ylabelName)

    if calcBy == config.CalcByType.TOOL:
        sns.scatterplot(x=var_compare, y=var_target, hue="tool", style="tool", data=data).set(ylabel=ylabelName)

    # fig.canvas.set_window_title(window_title)
    plt.tight_layout()

    # path = config.OUT_PLOT_DIR + "/scatter_" + var_target + "_" + var_compare + "_" + calcBy.name + "_" + config.OUT_PLOT_FILE + "." + config.OUT_PNG_EXT
    plt.savefig(path)
    plt.close('all')
    return path

# dunn-test heatmap
def saveHeatMapPlot(dunnResult, path):
    plt.rcParams['figure.figsize'] = (5, 5)
    fig, ax1 = plt.subplots()
    plt.gcf().subplots_adjust(left=0.30, right=0.75)

    # 'cbar_ax_bbox': [0.80, 0.35, 0.04, 0.3]
    heatmap_args = {'linewidths': 0.25, 'linecolor': '0.5', 'clip_on': False, 'square': True, 'cbar_ax_bbox': [0.80, 0.35, 0.04, 0.3]}
    sp.sign_plot(dunnResult, **heatmap_args)
    # path = config.OUT_PLOT_DIR + "/heat_" + var + "_" + calcByString + "_" + config.OUT_PLOT_FILE + "." + config.OUT_PNG_EXT
    # fig.canvas.set_window_title(figureName + "["+config.TARGET_VAR+"] - Distribution Difference HeatMap")
    plt.savefig(path)
    plt.close('all')
    return path

# interpretation:
# https://www.wellbeingatschool.org.nz/information-sheet/understanding-and-interpreting-box-plots
def saveBoxPlot(data, calcBy, var, path):
    # figure size settings
    plt.rcParams['figure.figsize'] = (5, 5)

    # fig, (ax1, ax2) = plt.subplots(2)
    fig, ax1 = plt.subplots()
    ax1.set(ylim=(config.PLOT_RANGES[var][min], config.PLOT_RANGES[var][max]))
    window_title = str("["+ calcBy.name +"]["+ var +"] - Box Plot")

    # sns.regplot(x, y, ax=ax1)
    # sns.kdeplot(x, ax=ax2)

    ylabelName = var
    # if var in config.SUBSTITUTE_STRINGS:
    #     ylabelName = config.SUBSTITUTE_STRINGS[var]

    vid_order = [e.value for e in config.Video]

    if calcBy == config.CalcByType.VIDEO:
        sns.boxplot(x="video", y=var, order=vid_order, data=data, ax=ax1).set(ylabel=ylabelName)

    if calcBy == config.CalcByType.TOOL:
        sns.boxplot(x="tool",y=var,data=data, ax=ax1).set(ylabel=ylabelName)

    if calcBy == config.CalcByType.VIDEO_TOOL:
        sns.boxplot(x="tool",y=var, hue="video", hue_order=vid_order, data=data, ax=ax1).set(ylabel=ylabelName)

    if calcBy == "likert":
        ax1.set(ylim=(config.PLOT_RANGES["likert"][min], config.PLOT_RANGES["likert"][max]), yscale="linear")
        ax1.get_yaxis().set_major_locator(MaxNLocator(integer=True)) # only show integer numbers
        sns.boxplot(x="tool", y="vEffort", hue="video", hue_order=vid_order, data=data, ax=ax1)


    # fig.canvas.set_window_title(window_title)
    if config.PLOT_CORRECT_THRESH and calcBy != "likert":
        plt.axhline(config.CORRECT_THRESH, color='tab:red', linestyle='dashed')
    plt.tight_layout()

    # path = config.OUT_PLOT_DIR + "/box_" + var + "_" + calcBy.name + "_" + config.OUT_PLOT_FILE + "." + config.OUT_PNG_EXT
    plt.savefig(path)
    plt.close('all')
    return path

def saveQQPlot(data, calcBy, var, path):

    # figure size settings
    plt.rcParams['figure.figsize'] = (15, 5)

    fig = plt.figure()
    # fig.canvas.set_window_title("["+ calcBy.name +"]["+ var +"] - Q-Q Plots")

    if calcBy == config.CalcByType.VIDEO:
        i = 1
        for v in config.Video:
            qqSubPlot(fig, data[data.video==v.value][var].values, [2,2,i], v.value)
            i = i + 1

    if calcBy == config.CalcByType.TOOL:
        i = 1
        for t in config.Tool:
            qqSubPlot(fig, data[data.tool==t.value][var].values, [2,2,i], t.value)
            i = i + 1

    if calcBy == config.CalcByType.VIDEO_TOOL:
        i = 1
        for t in config.Tool:
            for v in config.Video:
                # works: data[data.tool == t][data.video == v][var].values
                # but results in user warning, proceed with 2 steps here
                df_tool_data = data[data.tool == t.value]
                qqSubPlot(fig, df_tool_data[df_tool_data.video == v.value][var].values, [3,3,i], t.value + "_" + v.value, True)
                i = i + 1

    if calcBy == None:
        fig = qqplot(data[var].values, line='s')
        plt.title(var)


    plt.tight_layout()
    # path = config.OUT_PLOT_DIR + "/qq_" + var + "_" + calcBy.name + "_" + config.OUT_PLOT_FILE + "." + config.OUT_PNG_EXT
    plt.savefig(path)
    plt.close('all')
    return path
### addQQPlot
# indicate normal distributions
def qqSubPlot(figure, data, layout, name, resizeLabels = False):
    ax = figure.add_subplot(layout[0], layout[1], layout[2], ymargin=0.5)
    ax.set_title(name)
    if resizeLabels:
        ax.set_xlabel(ax.get_xlabel(), fontsize=10)
        ax.set_ylabel(ax.get_ylabel(), fontsize=10)
    qqplot(data, line='s', ax=ax)
    # left = -2.7
    # top = ax.get_ylim()[1] - 0.05
    # txt = ax.text(left, top, name, verticalalignment='top')
    # txt.set_bbox(dict(facecolor='k', alpha=0.1))
