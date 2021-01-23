# -*- coding: utf-8 -*-

"""
m3u8ToMp4.exceptions
~~~~~~~~~~~~~~~~~~~~

this module is a exception set, which has been used through the while process
"""


class Error(Exception):
    pass


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
    pass


class NameRepeatedError(Error):
    pass

