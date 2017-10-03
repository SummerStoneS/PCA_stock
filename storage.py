import os
import json
import pandas as pd


class Storage:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            # 创建文件夹 叫path
            os.mkdir(path)

    # 保存 key是保存成什么文件名
    def store(self, key, data, fmt="csv"):
        assert fmt in ("csv", "json", "npy")
        file_path = os.path.join(self.path, "%s.%s" % (key, fmt))
        if fmt == "csv":
            if not isinstance(data, (pd.Series, pd.DataFrame)):
                raise TypeError("File must be of DataFrame or Series format to be stored as csv")
            data.to_csv(file_path)
        elif fmt == "npy":
            import numpy as np
            np.save(file_path, data)
        elif fmt == "json":
            if not isinstance(data, dict):
                raise TypeError("data must be of dict format to be stored as json")
            with open(file_path, "w") as f:
                json.dump(data, f)

    def load(self, key, fmt="csv", parse_dates=True):
        assert fmt in ("csv", "json")
        file_path = os.path.join(self.path, "%s.%s" % (key, fmt))
        if fmt == "csv":
            return pd.read_csv(file_path, index_col=0, parse_dates=parse_dates)
        else:
            return json.load(file_path)

    def wrapper(self, keys, fmts=None):
        fmts = fmts or "csv"
        if not isinstance(fmts, (tuple, list)):
            fmts = [fmts] * len(keys)

        def wrapper_inside(fn):
            def inside(*args, **kwargs):
                rtn_values = fn(*args, **kwargs)
                if not isinstance(rtn_values, tuple):
                    rtn_values = (rtn_values, )
                assert len(rtn_values) == len(keys), "length of `keys` must be the same as returned values"
                pairs = zip(keys, rtn_values, fmts)
                for key, data, fmt in pairs:
                    self.store(key, data, fmt=fmt)
                if len(rtn_values) == 1:
                    rtn_values = rtn_values[0]
                return rtn_values
            return inside
        return wrapper_inside

