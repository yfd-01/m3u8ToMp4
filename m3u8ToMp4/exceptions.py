# -*- coding: utf-8 -*-

"""
m3u8ToMp4.exceptions
~~~~~~~~~~~~~~~~~~~~

this module is a exception set, which has been used through the while process
"""


class Error(Exception):
    def __init__(self, *args):
        self.args = args


class RequestError(Error):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return "RequestError: url - " + repr(self.url)


class ResponseStatusError(RequestError):
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return "ResponseStatusError: status_code - " + repr(self.status_code)


class NameInvalidError(Error):
    def __str__(self):
        return '文件名包含特殊字符 - 注意是否有 \ / : * ? " < > |'


class NameRepeatedError(Error):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "名字已存在 - " + repr(self.name)


class BitrateLevelInvalidError(Error):
    def __init__(self, Level):
        self.Level = Level

    def __str__(self):
        return "无效的自动比特率等级 - " + repr(self.Level)


class PathNotADirectoryError(Error):
    def __init__(self, path):
        self.path = path
        
    def __str__(self):
        return "不是一个可使用路径 - " + repr(self.path)


