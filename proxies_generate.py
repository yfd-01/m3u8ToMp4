# -*- coding: utf-8 -*-

#TODO - 

import requests
import subprocess as sp
import re
import threading
from bs4 import BeautifulSoup
from .utils import progress_bar

https_xici = "https://www.xicidaili.com/wn/"
http_xici = "https://www.xicidaili.com/wt/"

recv = re.compile(u"已接收 = (\d+)", re.IGNORECASE)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'
}

ret_ls = []
expected_type = ""
expected_num = 0

class _ProxiesGenerationTypeError(TypeError):
    def __str__(self):
        return "parameter is not appropriate"

def get_proxies_ip(type_, num):
    """
    Get a number of proxies ip

    :param type_: specify the proxy ip is http or https (str)
    :param num:  the number of needed proxies ip        (int)
    :return:    list of proxies ip      (list)
    """
    if type_ != "https" and type_ != "http" or num < 1:
        raise _ProxiesGenerationTypeError

    t_ls = []

    global expected_type, expected_num
    expected_type = type_
    expected_num = num

    index = 1

    while len(ret_ls) < num:
        rsp = requests.get(https_xici + str(index), headers=headers)
        soup = BeautifulSoup(rsp.text, "lxml")

        for item in soup.select("#ip_list tr[class]"):
            i = item.select("td:nth-child(2)")[0].text
            p = item.select("td:nth-child(3)")[0].text

            t = threading.Thread(target=__ip_survival, args=(i, p, ))
            t_ls.append(t)

        for t in t_ls:
            t.setDaemon(True)
            t.start()

        for t in t_ls:
            t.join()

        t_ls.clear()
        index += 1

    return ret_ls

def __ip_survival(ip, port):
    """
    To get the survived ip into ret_ls

    :param ip:  to checked ip
    :param port:   to checked port
    """
    cmd = "ping %s"

    p = sp.Popen(cmd % ip, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)

    out = p.stdout.read().decode("gbk")

    if int(recv.findall(out)[0]) > 1:
        ret_ls.append({expected_type: expected_type + "://" + ip + ':' + port})

        if len(ret_ls) <= expected_num:
            progress_bar(len(ret_ls), expected_num,
                        prefix="ip代理池", suffix="准备中...", completed_suffix="IP代理池准备完毕!")
