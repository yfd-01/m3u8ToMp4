# -*- coding: utf-8 -*-

"""
m3u8ToMp4.utils
~~~~~~~~~~~~~~~

this module implements a few applicable tools
"""

import sys


def progress_bar(current, totals, decimals=1, prefix='Progress', suffix='complete', completed_suffix='completed'
                , bar_length=50):
    """
        Call in a loop to create a terminal progress bar

        :param current: current iteration (Int)
        :param totals: total iterations (Int)
        :param decimals: (optional) positive number of decimals in percent complete (Int)
        :param prefix: (optional) prefix string (Str)
        :param suffix: (optional) suffix string (Str)
        :param completed_suffix: (optional) suffix string after completed(Str)
        :param bar_length: (optional) character length of bar (Int)
    """

    percent_format = "{0:." + str(decimals) + "f}"
    percent = percent_format.format(100 * (current / totals))

    filled_length = round(bar_length * current / totals)

    bar = '#' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write("\r%s: |%s| %s%s %s" % (prefix, bar, '%', percent, suffix))

    if current == totals:
        sys.stdout.write("\r%s: |%s| %s%s %s" % (prefix, bar, '%', percent, completed_suffix))
        sys.stdout.write('\n')

    sys.stdout.flush()


def check_dir_file_valid(name):
    """
        Check out the name is valid for director or file or not

        :param name: the name to check (Str)
        :return: ret (Bool)
    """
    if name.strip() == '':
        return False

    banned_ls = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    for ch in banned_ls:
        if name.find(ch) != -1:
            return False

    return True






