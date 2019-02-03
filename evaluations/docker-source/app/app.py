from flask import Flask, render_template, send_from_directory, jsonify
import traceback
import inspect
import logging
# logging.basicConfig(level=logging.DEBUG)
import os
import socket
import sys
import calc_iou

import utils
import config
import pandas as pd

from Data import Data

# calculations
import calculate

global_data = Data(config.IN_STUDY)

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def default():
    # return render_template('index.html', title='Home', user=user, posts=posts)
    return render_template('home.html')

@app.route("/iou")
def show_iou():
    iou_files = get_rel_to_root_files(config.OUT_IOU_DIR)
    return render_template('iou.html', files=iou_files)
@app.route("/calculate_iou")
def calculate_iou():
    utils.printFlaskMsg("Calculating IOUs...")
    try:
        result = calc_iou.run()
    except:
        utils.printFlaskMsg("Unexpected error:")
        errorMsg = traceback.format_exc()
        utils.printFlaskMsg(errorMsg)
        return jsonify({"success": False, "message": errorMsg})
        # raise
    utils.printFlaskMsg(result["message"])
    result["files"] = get_rel_to_root_files(config.OUT_IOU_DIR)
    result["trace"] = getTraceBack()
    return jsonify(result)

def set_tables(f, tables):
    for section in config.ALL_SECTIONS:
        # init dict
        if section not in tables:
            tables[section] = {}
        # fill tables
        if section in f:
            for statistic in config.ALL_STATISTICS:
                if statistic in f:
                    in_df = pd.read_csv(f)
                    if statistic not in tables[section]:
                        tables[section][statistic] = []
                    tables[section][statistic].append(in_df.to_html(index=False, justify="center"))

def set_plots(f, plots):
    for section in config.ALL_SECTIONS:
        # init dict
        if section not in plots:
            plots[section] = {}
        # fill plots
        if section in f:
            for pl_type in config.ALL_PLOTS:
                if pl_type in f:
                    if pl_type not in plots[section]:
                        plots[section][pl_type] = []
                    plots[section][pl_type].append(f)

# NEW
@app.route("/evals")
def show_evals():
    # FILES
    files = utils.nat_sort_list(utils.get_file_paths(config.OUT_EVALS_DIR))
    tables = {}
    if len(files) > 0:
        for f in files:
            set_tables(f, tables)

    # PLOTS
    plot_files = utils.nat_sort_list(get_rel_to_root_files(config.OUT_PLOT_DIR))
    plot_dict= {}
    if len(plot_files) > 0:
        for f in plot_files:
            set_plots(f, plot_dict)

    # utils.printFlaskMsg(str(files))
    # utils.printFlaskMsg(str(tables))
    # utils.printFlaskMsg(str(plot_dict))

    return render_template('evals.html', files=tables, plots=plot_dict)

@app.route("/calc/<string:section>")
def calc(section):
    global global_data
    result = {"success": False, "message": "No method specified!"}

    if section in config.ALL_SECTIONS:
        utils.printFlaskMsg("Calculating " + section + "...")

        try:
            global_data.create_out_dirs()
            # call corresponding function in calc
            result = getattr(calculate, section)(global_data)
            # utils.printFlaskMsg(str(result["message"]['norm']))
        except:
            utils.printFlaskMsg("Unexpected error:")
            errorMsg = traceback.format_exc()
            utils.printFlaskMsg(errorMsg)
            return jsonify({"success": False, "message": errorMsg})
            # raise

    result["trace"] = getTraceBack()
    return jsonify(result)

@app.route("/clear")
def clear_all():

    result = {"success": True, "message": "sucessfully cleared!"}

    try:
        utils.remove_dir(config.OUT_EVALS_DIR)
        utils.remove_dir(config.OUT_PLOT_DIR)
        utils.remove_dir(config.OUT_IOU_DIR)
        # call corresponding function in calc
        # result = getattr(calculate, section)(global_data)
        # utils.printFlaskMsg(str(result["message"]['norm']))
    except:
        utils.printFlaskMsg("Unexpected error:")
        errorMsg = traceback.format_exc()
        utils.printFlaskMsg(errorMsg)
        return jsonify({"success": False, "message": errorMsg})
        # raise

    result["trace"] = getTraceBack()
    return jsonify(result)


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # downloads = os.path.join(current_app.root_path, 'downloads')
    return send_from_directory(directory="downloads", filename=filename)

@app.route('/code/<path:filename>', methods=['GET', 'POST'])
def code(filename):
    # downloads = os.path.join(current_app.root_path, 'downloads')
    return send_from_directory(directory="", filename=filename)

def getTraceBack():
    traceRaw = traceback.format_stack()
    return '<br>'.join(traceRaw)

def getInspect():
    traceRaw = inspect.stack()
    formattedTrace = ""
    for fi in traceRaw:
        formattedTrace += str(fi) + "<br>"
    return formattedTrace

def get_rel_to_root_files(path):
    wd = os.getcwd()
    all_files = utils.get_file_paths(path)
    file_names = []
    for f in all_files:
        file_names.append(f.replace(wd,""))
    return file_names

if __name__ == "__main__":
    # internal port 80
    app.run(host='0.0.0.0', port=80, debug=config.DEBUG_APP)
