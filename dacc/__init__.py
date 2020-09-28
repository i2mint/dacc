__author__ = 'thor'

from typing import Iterable


def has_non_callable_attr(obj, attr):
    return hasattr(obj, attr) and not hasattr(getattr(obj, attr), '__call__')


def ascertain_list(x):
    """
    ascertain_list(x) blah blah returns [x] if x is not already a list, and x itself if it's already a list
    Use: This is useful when a function expects a list, but you want to also input a single element without putting this
    this element in a list
    """
    if not isinstance(x, list):
        ## The "all but where it's a problem approach"
        if isinstance(x, Iterable) and not isinstance(x, dict):
            x = list(x)
        else:
            x = [x]
            ## The (less safe) "just force what you want to do differently in those cases only" approach
            # if isinstance(x, np.ndarray):
            #     x = list(x)
            # else:
            #     x = [x]
    return x


def get_subdict_and_remainder(d, list_of_keys):
    """
    :param d: dict
    :param subset_of_keys: list of keys
    :return: the subset of key:value pairs of d where key is in list_of_keys
    """
    keys_in = set(d.keys()).intersection(list_of_keys)
    keys_not_in = set(d.keys()).difference(list_of_keys)
    return (dict([(i, d[i]) for i in keys_in]), dict([(i, d[i]) for i in keys_not_in]))


class DataFlow(object):
    """
    DataFlow is a framework to pipeline data processes.
    """

    def __init__(self, **kwargs):
        kwargs = dict({'verbose_level': 0}, **kwargs)
        [setattr(self, k, v) for k, v in kwargs.items()]

        if not hasattr(self, 'data_dependencies'):
            self.data_dependencies = dict()
        if not hasattr(self, 'data_makers'):
            self.data_makers = dict()
        if not hasattr(self, 'data_storers'):
            self.data_storers = dict()

        self.mk_data_flow()

    def mk_data_flow(self):
        # make sure values of data_dependencies are lists
        self.data_dependencies = {k: ascertain_list(v) for k, v in self.data_dependencies.items()}
        # default data_makers to functions of the same name as data_dependencies
        missing_data_makers = set(self.data_dependencies.keys()).difference(list(self.data_makers.keys()))
        bundles = list()
        for k in missing_data_makers:
            if hasattr(self, k):
                self.data_makers[k] = getattr(self, k)
            else:
                bundles.append(k)
        if not hasattr(self, 'verbose_level'):
            setattr(self, 'verbose_level', 1)
        if bundles:
            print("Bundles:")
            for k in bundles:
                print(("  {}: \n    {}").format(k, ', '.join(self.data_dependencies[k])))

    def put_in_store(self, name, data):
        self.print_progress('  Storing {} in store'.format(name))
        self.store.put(name, data)

    def put_in_attr(self, name, data):
        self.print_progress('  Storing {} in attribute'.format(name))
        setattr(self, name, data)

    def put_in_data_dict(self, name, data):
        self.print_progress('  Storing {} in data_dict attribute'.format(name))
        try:
            setattr(self, 'data_dict', self.data_dict.update({'name': data}))
        except AttributeError:
            self.data_dict = {'name': data}

    def get_data(self, data_name, **kwargs):
        # if data_name not in self.data_dependencies.keys():
        #    raise ValueError("I have no data_dependencies for %s" % data_name)
        if hasattr(self,
                   'store') and data_name in self.store:  # if no data is input and the data exists in the store...
            # return the stored data
            self.print_progress(2, '  Getting {} from store'.format(data_name))
            return self.store[data_name]
        elif has_non_callable_attr(self, data_name):
            return getattr(self, data_name)
        else:
            # determine what the data part of kwargs is
            input_data, kwargs = get_subdict_and_remainder(kwargs, self.data_dependencies[data_name])
            # determine what data we don't have
            missing_data_names = set(self.data_dependencies[data_name]).difference(list(input_data.keys()))
            # get the data we don't have
            if missing_data_names:
                self.print_progress(3, "  --> {} requires {}".format(data_name, ', '.join(missing_data_names)))
                for missing_dependency in missing_data_names:
                    input_data[missing_dependency] = \
                        self.get_data(data_name=missing_dependency, **kwargs)
        # make the data
        if data_name in list(self.data_makers.keys()):
            # here the data needs to be made from data
            self.print_progress(1, '  Making {}'.format(data_name))
            kwargs = dict(input_data, **kwargs)
            made_data = self.data_makers[data_name](**kwargs)
            # store it if necessary
            if data_name in list(self.data_storers.keys()) and self.data_storers[data_name] is not None:
                self.data_storers[data_name](data_name, made_data)
            return made_data
        else:
            # here all you want is the input_data
            return input_data

    def get_data_lite_and_broad(self, data_name, **kwargs):
        # determine what the data part of kwargs is
        input_data = {k: v for k, v in kwargs.items() if k in self.data_dependencies[data_name]}
        # input_data, kwargs = get_subdict_and_remainder(kwargs, self.data_dependencies[data_name])
        # determine what data we don't have
        missing_data_names = set(self.data_dependencies[data_name]).difference(list(input_data.keys()))
        # get the data we don't have
        if missing_data_names:
            for missing_dependency in missing_data_names:
                input_data[missing_dependency] = \
                    self.get_data_lite_and_broad(data_name=missing_dependency, **kwargs)
        # make the data
        if data_name in list(self.data_makers.keys()):
            # here the data needs to be made from data
            kwargs = dict(input_data, **kwargs)
            made_data = self.data_makers[data_name](**kwargs)
            # store it if necessary
            if data_name in list(self.data_storers.keys()) and self.data_storers[data_name] is not None:
                self.data_storers[data_name](data_name, made_data)
            return made_data
        else:
            # here all you want is the input_data
            return input_data

    def print_progress(self, min_level, msg='', verbose_level=None):
        verbose_level = verbose_level or self.verbose_level
        if verbose_level >= min_level:
            msg = 2 * min_level * ' ' + msg
            self.print_progress(msg)

    @staticmethod
    def verbose(kwargs, min_level=1):
        return ('verbose' in list(kwargs.keys())) and (kwargs['verbose'] >= min_level)
