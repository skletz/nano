import config
import utils
import csv
import pandas as pd
pd.options.display.float_format = '{:3.3f}'.format
import plots
import sys
import numpy as np
import scipy

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html
from scipy.stats import shapiro     # shapiro wilk
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html
from scipy.stats import kruskal     # kruskal wallis (non-parametric n-sample ANOVA alternative )
import scikit_posthocs as sp
# https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.spearmanr.html
from scipy.stats import spearmanr # spearmans ranked rank coefficient (non-parametric correlation betw. 2 continuous vars)
from scipy.stats import friedmanchisquare
import pingouin as pg


def create_plot(data, type, var, plot_func, path_prefix):
    typeString = type.name if type != None else "None"
    if (isinstance(var, list)):
        path = path_prefix + "_" + var[0] + "_" + var[1] + "_" + typeString + "_" + config.OUT_PLOT_FILE + "." + config.OUT_PNG_EXT
        return plot_func(data.df, type, var[0], var[1], path)
    else:
        path = path_prefix + "_" + var + "_" + typeString + "_" + config.OUT_PLOT_FILE + "." + config.OUT_PNG_EXT
        return plot_func(data.df, type, var, path)

def create_stat(data, type, var, func, path_prefix, file_type):
    typeString = type.name if type != None else "None"
    stat_df = None
    if (isinstance(var, list)):
        stat_df = data.calc_dual_stat(type, var[0], var[1], func, ["coef","p"])
    else:
        stat_df = data.calc_single_stat(type, var, func, ["s", "p"])
    out_var_path = path_prefix + typeString + "_" + var + "_" + file_type + "." + config.OUT_CSV_EXT
    stat_df.to_csv(out_var_path, index=False)
    return stat_df

def create_var_stats(data, var_list, type, test_func, out_prefix, force_unique=True, plot_dunn=True):
    out_csv = config.OUT_EVALS_DIR + "/" + out_prefix
    out_png = config.OUT_PLOT_DIR + "/" + out_prefix

    res = {}
    stat = ['s', 'p']
    res_posthoc = None
    plot_list = []
    statistics_dct = {}
    statistics_idx_col = "var"
    statistics_dct[statistics_idx_col] = []
    statistics_dct['n'] = []
    column_names = [statistics_idx_col, 'n'] + stat

    for var in var_list:
        res[var] = {}
        dct = data.to_single_type_dict(type, var, force_unique)
        lst = data.to_single_type_list(type, var, force_unique)

        # statistic test
        res[var][stat[0]], res[var][stat[1]] = test_func(*lst) # '*' splits list into list of arguments
        if 'n' not in res[var]:
            res[var]['n'] = len(lst[0])

        statistics_dct[statistics_idx_col].append(var)
        statistics_dct['n'].append(len(lst[0]))
        for st in stat:
            if st not in statistics_dct:
                statistics_dct[st] = []
            val = utils.format_number(res[var][st],config.PRINT_PRECISION)
            statistics_dct[st].append(val)

        # dunn
        if plot_dunn:
            frame = pd.DataFrame.from_dict(dct)
            frame = frame.melt(var_name='groups', value_name='values')
            res_posthoc = sp.posthoc_dunn(frame, val_col='values', group_col='groups', p_adjust='bonferroni')
            path = out_png + "heat_" + var + "_" + sp.posthoc_dunn.__name__ + "." + config.OUT_PNG_EXT
            plot_list.append(plots.saveHeatMapPlot(res_posthoc, path))

    # statistics to df
    statistics_df = pd.DataFrame(statistics_dct, columns=column_names)
    statistics_df.set_index(statistics_idx_col)
    out_var_path = out_csv + "question_groups_" + type.name + "_" + test_func.__name__ + "." + config.OUT_CSV_EXT
    statistics_df.to_csv(out_var_path, index=False)

    return res, plot_list


def subjective(data):
    # out paths
    func_name = sys._getframe().f_code.co_name
    out_prefix = func_name + "_"

    # Friedmann/Kruskal and Dunn
    types = [config.CalcByType.VIDEO, config.CalcByType.TOOL]
    questions = [config.QuestionVideo, config.QuestionTool]
    tests = [friedmanchisquare, kruskal]

    plot_list = []
    stat_dict = {}
    for i in range(len(types)):
        q_list = list(map(lambda c: c.value, questions[i]))
        res, plots = create_var_stats(data, q_list, types[i], tests[i], out_prefix)
        plot_list += plots
        stat_dict[types[i].name] = res

    return {"success": True, "message": {"sub_groups": str(stat_dict), "plots": str(plot_list)}}


def efficiency(data):
    # out paths
    func_name = sys._getframe().f_code.co_name
    out_prefix = func_name + "_"
    out_csv = config.OUT_EVALS_DIR + "/" + out_prefix
    out_png = config.OUT_PLOT_DIR + "/" + out_prefix

    plot_list = []
    norm_time_dict = {}
    var = "time"
    for c in config.CalcByType:
        # box plots
        plot_list.append(create_plot(data, c, var, plots.saveBoxPlot, out_png + "box"))
        # statistics + out
        norm_time_dict[c.name] = create_stat(data, c, var, shapiro, out_csv, config.OUT_NORM_FILE)
        # qq plots
        plot_list.append(create_plot(data, c, var, plots.saveQQPlot, out_png + "qq"))


    # var by no calctype
    norm_time_dict["None"] = create_stat(data, None, var, shapiro, out_csv, config.OUT_NORM_FILE)
    plot_list.append(create_plot(data, None, var, plots.saveQQPlot, out_png + "qq"))

    # ONE WAY ANOVA w repeated measurements
    out_one_way_anova = out_csv + var + "_" + config.OUT_ONE_WAY_ANOVA_FILE + "." + config.OUT_CSV_EXT
    data_log = data.deep_copy();
    data_log[var] = np.log10(data_log[var])
    # Remove outliers
    q = data_log['time'].quantile(0.96)
    data_log = data_log[data_log["time"] < q]
    one_way_anova_aov = pg.rm_anova(dv=var, data=data_log, subject='user', within='video', detailed=True)
    one_way_anova_aov.to_csv(out_one_way_anova, index=False)

    # Pairwise T-test
    out_ttest= out_csv + var + "_" + config.OUT_TTEST_FILE + "." + config.OUT_CSV_EXT
    ttest_result = pg.pairwise_ttests(dv=var, within='video', subject='user', data=data_log, padjust='bonferroni', effsize='hedges', tail='one-sided', return_desc=True)
    ttest_result.to_csv(out_ttest, index=False)

    # MIXED_ANOVA
    out_mixed_anova = out_csv + var + "_" + config.OUT_MIXED_ANOVA_FILE + "." + config.OUT_CSV_EXT
    m_anova = pg.mixed_anova(dv=var, within='video', between='tool', subject='user', data=data.df)
    m_anova.to_csv(out_mixed_anova, index=False)

    # Friedmann/Kruskal and Dunn
    types = [config.CalcByType.VIDEO, config.CalcByType.TOOL]
    tests = [friedmanchisquare, kruskal]
    pfx = [config.OUT_FRIEDMAN_FILE, config.OUT_KRUSKAL_FILE]
    stat_dict = {}
    for i in range(len(types)):
        res, plt = create_var_stats(data, [var], types[i], tests[i], out_prefix + pfx[i], False)
        plot_list += plt
        stat_dict[types[i].name] = res

    return {"success": True, "message": {'norm': str(norm_time_dict), 'stats': str(stat_dict), 'one_way_anova': str(one_way_anova_aov), 'plots': str(plot_list) }}

def effectiveness(data):
    # out paths
    func_name = sys._getframe().f_code.co_name
    out_prefix = func_name + "_"
    out_csv = config.OUT_EVALS_DIR + "/" + out_prefix
    out_png = config.OUT_PLOT_DIR + "/" + out_prefix

    plot_list = []
    norm_iou_dict = {}
    var = "iou"
    for c in config.CalcByType:
        # box plots
        plot_list.append(create_plot(data, c, var, plots.saveBoxPlot, out_png + "box"))
        # norm + out + plot
        norm_iou_dict[c.name] = create_stat(data, c, var, shapiro, out_csv, config.OUT_NORM_FILE)
        plot_list.append(create_plot(data, c, var, plots.saveQQPlot, out_png + "qq"))

    # var by no calctype
    norm_iou_dict["None"] = create_stat(data, None, var, shapiro, out_csv, config.OUT_NORM_FILE)
    plot_list.append(create_plot(data, None, var, plots.saveQQPlot, out_png + "qq"))

    # Friedmann/Kruskal and Dunn
    types = [config.CalcByType.VIDEO, config.CalcByType.TOOL]
    tests = [friedmanchisquare, kruskal]
    pfx = [config.OUT_FRIEDMAN_FILE, config.OUT_KRUSKAL_FILE]
    stat_dict = {}
    for i in range(len(types)):
        res, plt = create_var_stats(data, [var], types[i], tests[i], out_prefix + pfx[i], False)
        plot_list += plt
        stat_dict[types[i].name] = res

    return {"success": True, "message": {'norm': str(norm_iou_dict), 'stats': str(stat_dict), 'plots': str(plot_list) }}

def correlations(data):
    # out paths
    func_name = sys._getframe().f_code.co_name
    out_prefix = func_name + "_"
    out_csv = config.OUT_EVALS_DIR + "/" + out_prefix
    out_png = config.OUT_PLOT_DIR + "/" + out_prefix

    plot_list = []
    spearman_dict = {}
    var_target = "iou"
    var_compare = "time"
    for c in config.CalcByType:
        # spearman + out
        spearman_dict[c.name] = data.calc_dual_stat(c, var_target, var_compare, spearmanr, ['coef', 'p'])
        out_spear = out_csv + c.name + "_" + var_target + "_" +  var_compare + "_" + config.OUT_SPEAR_FILE + "." + config.OUT_CSV_EXT
        spearman_dict[c.name].to_csv(out_spear, index=False)
        # scatter plots
        if c != config.CalcByType.VIDEO_TOOL:
            plot_list.append(create_plot(data, c, [var_target, var_compare], plots.saveScatterPlot, out_png + "scatter"))


    return {"success": True, "message": {'spear': str(spearman_dict), 'plots': str(plot_list) }}
