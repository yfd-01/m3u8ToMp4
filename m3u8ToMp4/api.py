# -*- coding: utf-8 -*-

"""
m3u8ToMp4.api
~~~~~~~~~~~~~

this module implements the M3U8ToMp4 API
"""

from . import process


def download_console():
    """
    Constructs and start to download video, the params received by console
    """

    with process.Crawler() as crawler:
        crawler.download_video_from_m3u8_c()

def download(m3u8, download_base_path, name, **kwargs):
    """
    Constructs and start to download video, the param received by calling

    :param m3u8:                the target m3u8 address: str
    :param download_base_path:  the video saved path: str
    :param name:                the video name: str
    :param \*\*kwargs:          Optional arguments that ``Crawler`` takes
    """

    with process.Crawler(**kwargs) as crawler:
        crawler.download_video_from_m3u8_p(m3u8, download_base_path, name)