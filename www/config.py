import config_default

class Dict(dict):
    '''
    Simple dict but support access as x.y style.
    '''
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        # $ Dict = dict(zip(['a','b'],['1','2']))
        # {'a':1, 'b':2}
        for k, v in zip(names, values):
            self[k] = v

    # 当使用点号获取实例属性时，如果属性不存在就自动调用__getattr__方法
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    # 当设置类实例属性时自动调用，如j.name=5 就会调用__setattr__方法  self.[name]=5
    def __setattr__(self, key, value):
        self[key] = value

# 覆盖
def merge(defaults, override):
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

# 添加一种取值方式dict.key，相当于dict['key']
def toDict(d):
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D

configs = config_default.configs

try:
    import config_override
    # 用来覆盖默认设置
    configs = merge(configs, config_override.configs)
except ImportError:
    pass

configs = toDict(configs)

