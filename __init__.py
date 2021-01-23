# -*- coding: utf-8 -*-

"""
m3u8ToMp4
~~~~~~~~~~~~

Basic usage:

import m3u8ToMp4
m3u8ToMp4.download("https://xxx.com/20200620/abcdefg/index.m3u8", "E:\movies_save\", "Marvel's The Avengers")
    
... or input params by console:

m3u8ToMp4.download_console()

python Console[
    m3u8_address:  https://xxx.com/20200620/abcdefg/index.m3u8
    
    restore_path:  E:\movies_save\
    
    video_name:    Marvel's The Avengers
]
    
"""

from .api import download, download_console
from .process import Crawler
from .session import request_get
from .utils import progress_bar, check_dir_file_valid
from .exceptions import (
    RequestError, ResponseStatusError, NameInvalidError, NameRepeatedError
)

__author__ = "VioletYFD"
__version__ = "0.2.2"

__all__ = (
    "download",
    "download_console",
    "Crawler",
    "request_get",
    "progress_bar",
    "check_dir_file_valid",
    "RequestError",
    "ResponseStatusError",
    "NameInvalidError",
    "NameRepeatedError"
)
