import config
import utils
import pandas as pd

class Data:
    def __init__(self, path):
        # read input data
        self.df = pd.read_csv(path)

    def create_out_dirs(self):
        # create results folders if not exist
        utils.make_dir(config.OUT_EVALS_DIR)
        utils.make_dir(config.OUT_PLOT_DIR)

    def get_single_col(self, col):
        return self.df[col].values

    def get_single_col_dict(self, col):
        res = {}
        res[col] = self.df[col].values
        return res

    def get_unique_df(self, type):
        if type == config.CalcByType.VIDEO_TOOL:
            return self.df.drop_duplicates(subset=['user','tool','video'])
        else:
            return self.df.drop_duplicates(subset=['user', type.name.lower()])

    def to_single_type_list(self, type, var):
        lst = []
        df_unique = self.get_unique_df(type)

        if type == config.CalcByType.VIDEO:
            for v in config.Video:
                values = df_unique[df_unique.video == v.value][var].values
                lst.append(values)

        if type == config.CalcByType.TOOL:
            for t in config.Tool:
                values = df_unique[df_unique.tool == t.value][var].values
                lst.append(values)

        if type == config.CalcByType.VIDEO_TOOL:
            for t in config.Tool:
                for v in config.Video:
                    # works: self.df[self.df.tool == t.value][self.df.video == v.value][var].values
                    # but results in user warning, proceed with 2 steps here
                    df_tool_data = self.df[self.df.tool == t.value]
                    values = df_tool_data[df_tool_data.video == v.value][var].values
                    lst.append(values)
        return lst

    def to_single_type_dict(self, type, var):
        dct = {}
        df_unique = self.get_unique_df(type)

        if type == config.CalcByType.VIDEO:
            for v in config.Video:
                values = df_unique[df_unique.video == v.value][var].values
                dct[v.value] = values

        if type == config.CalcByType.TOOL:
            for t in config.Tool:
                values = df_unique[df_unique.tool == t.value][var].values
                dct[t.value] = values

        if type == config.CalcByType.VIDEO_TOOL:
            for t in config.Tool:
                for v in config.Video:
                    # works: self.df[self.df.tool == t.value][self.df.video == v.value][var].values
                    # but results in user warning, proceed with 2 steps here
                    df_tool_data = self.df[self.df.tool == t.value]
                    values = df_tool_data[df_tool_data.video == v.value][var].values
                    dct[t.value + "_"+ v.value] = values
        return dct

    def calc_single_stat(self, type, var, func, stat = ['p']):
        dct = {}
        idx_col = type.name if type != None else "VAR"
        dct[idx_col] = []
        df_col = "df"
        column_names = [idx_col, df_col] + stat # merge with stat list
        res = {'p': None, 's': None}

        if type == config.CalcByType.VIDEO:
            for v in config.Video:
                values = self.df[self.df.video==v.value][var].values
                dct[df_col] = len(values)
                res['s'], res['p'] = func(values)
                dct[idx_col].append(v.value)
                for st in stat:
                    if st not in dct:
                        dct[st] = []
                    dct[st].append(utils.format_number(res[st],config.PRINT_PRECISION))

        if type == config.CalcByType.TOOL:
            for t in config.Tool:
                values = self.df[self.df.tool==t.value][var].values
                dct[df_col] = len(values)
                res['s'], res['p'] = func(values)
                dct[idx_col].append(t.value)
                for st in stat:
                    if st not in dct:
                        dct[st] = []
                    dct[st].append(utils.format_number(res[st],config.PRINT_PRECISION))

        if type == config.CalcByType.VIDEO_TOOL:
            for t in config.Tool:
                dct[idx_col].append(t.value)
                for v in config.Video:
                    # works: self.df[self.df.tool == t.value][self.df.video == v.value][var].values
                    # but results in user warning, proceed with 2 steps here
                    df_tool_data = self.df[self.df.tool == t.value]
                    values = df_tool_data[df_tool_data.video == v.value][var].values
                    res['s'], res['p'] = func(values)
                    if v.value not in dct:
                        dct[v.value] = []
                    add_vals = df_col + ": " + str(len(values))
                    add_vals += ", " + stat[0] + ": " + str(utils.format_number(res[stat[0]], config.PRINT_PRECISION))
                    if len(stat) > 1:
                        add_vals = add_vals + ", " + stat[1] + ": " + str(utils.format_number(res[stat[1]], config.PRINT_PRECISION))
                    dct[v.value].append(add_vals)
            # copy video names (don't just assign -- changes original list on altering later)
            column_names = [e.value for e in config.Video]
            column_names.insert(0, type.name)

        # calc stat for var only
        if type == None:
            values = self.df[var]
            dct[df_col] = len(values)
            res['s'], res['p'] = func(values)
            dct[idx_col].append(var)
            for st in stat:
                if st not in dct:
                    dct[st] = []
                dct[st].append(utils.format_number(res[st],config.PRINT_PRECISION))

        # results as df
        df = pd.DataFrame(dct, columns=column_names)
        df.set_index(idx_col)

        return df


    def calc_dual_stat(self, type, var_target, var_compare, func, stat = ['p']):
        dct = {}
        idx_col = type.name if type != None else "VAR"
        dct[idx_col] = []
        df_col = "df"
        column_names = [idx_col, df_col] + stat # merge with stat list
        res = {'p': None, 'coef': None}

        if type == config.CalcByType.VIDEO:
            for v in config.Video:
                df = self.df[self.df.video==v.value]
                res['coef'], res['p'] = func(df[var_target].values, df[var_compare].values)
                dct[df_col] = len(df[var_target].values)
                dct[idx_col].append(v.value)
                for st in stat:
                    if st not in dct:
                        dct[st] = []
                    dct[st].append(utils.format_number(res[st],config.PRINT_PRECISION))

        if type == config.CalcByType.TOOL:
            for t in config.Tool:
                df = self.df[self.df.tool==t.value]
                res['coef'], res['p'] = func(df[var_target].values, df[var_compare].values)
                dct[df_col] = len(df[var_target].values)
                dct[idx_col].append(t.value)
                for st in stat:
                    if st not in dct:
                        dct[st] = []
                    dct[st].append(utils.format_number(res[st],config.PRINT_PRECISION))

        if type == config.CalcByType.VIDEO_TOOL:
            for t in config.Tool:
                dct[idx_col].append(t.value)
                for v in config.Video:
                    # works: self.df[self.df.tool == t.value][self.df.video == v.value][var].values
                    # but results in user warning, proceed with 2 steps here
                    df_tool_data = self.df[self.df.tool == t.value]
                    df = df_tool_data[df_tool_data.video == v.value]
                    res['coef'], res['p'] = func(df[var_target].values, df[var_compare].values)
                    if v.value not in dct:
                        dct[v.value] = []
                    add_vals = df_col + ": " + str(len(df[var_target].values))
                    add_vals += ", " + stat[0] + ": " + str(utils.format_number(res[stat[0]], config.PRINT_PRECISION))
                    if len(stat) > 1:
                        add_vals = add_vals + ", " + stat[1] + ": " + str(utils.format_number(res[stat[1]], config.PRINT_PRECISION))
                    dct[v.value].append(add_vals)
            # copy video names (don't just assign -- changes original list on altering later)
            column_names = [e.value for e in config.Video]
            column_names.insert(0, type.name)

        # calc stat for var1 and var2 only
        if type == None:
            dct[idx_col].append(var_target)
            res['coef'], res['p'] = func(self.df[var_target].values, self.df[var_compare].values)
            dct[var_compare] = []
            add_vals = df_col + ": " + str(len(self.df[var_target].values))
            add_vals += ", " + stat[0] + ": " + str(utils.format_number(res[stat[0]], config.PRINT_PRECISION))
            if len(stat) > 1:
                add_vals = add_vals + ", " + stat[1] + ": " + str(utils.format_number(res[stat[1]], config.PRINT_PRECISION))
            dct[var_compare].append(add_vals)

        # results as df
        df = pd.DataFrame(dct, columns=column_names)
        df.set_index(idx_col)

        return df

    def deep_copy(self):
        return self.df.copy(deep=True)
