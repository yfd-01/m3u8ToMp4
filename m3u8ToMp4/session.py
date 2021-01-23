# -*- coding: utf-8 -*-

"""
m3u8ToMp4.session
~~~~~~~~~~~~~~~~~

this module provides a way to get/post request HTTP which has a number of retries
"""

import requests
from .exceptions import RequestError


def request_get(url, tries, **kwargs):
    return request_("get", url, tries, **kwargs)


def request_post(url, tries, **kwargs):
    return request_("post", url, tries, **kwargs)


def request_(method, url, tries, headers=None, data=None, timeout=60, proxies=None, verify=False):
    index = 0

    while index < tries:
        try:
            rsp = requests.get(url, headers=headers, timeout=timeout, proxies=proxies, verify=verify) if method == "get"\
                else requests.post(url, headers=headers, data=data, timeout=timeout, proxies=proxies, verify=verify)

            return rsp
        except Exception:
            timeout += 2
            index += 1

    raise RequestError(url)
