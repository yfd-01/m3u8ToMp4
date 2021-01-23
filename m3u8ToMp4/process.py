# -*- coding: utf-8 -*-

"""
m3u8ToMp4.process
~~~~~~~~~~~~~~~~~

this module is the implementation core, it contains class `Crawler` detail
"""

import os
import re
import time
import shutil
import threading
import subprocess
from Crypto.Cipher import AES
from urllib3 import disable_warnings
from . import utils, proxies_generate
from .session import request_get

from .exceptions import *

disable_warnings()


def analyze_url(url):
    """
    对URL格式进行解析
    """

    analyzed_data = {"protocol": None, "host": None, "resource_prefix": None}

    _reg1 = r"(http|https)://(\S+?)/"
    _reg2 = r".+/+"

    try:
        analyzed_data["protocol"] = re.findall(_reg1, url)[0][0]
        analyzed_data["host"] = re.findall(_reg1, url)[0][1]
        analyzed_data["resource_prefix"] = re.findall(_reg2, url)[0]
    except IndexError:
        print("Check the url format")
        return None

    return analyzed_data


def find_out_current_suffix(m3u8_text):
    """
    得到新的后缀
    """

    tmp_reg = r"#EXTINF:.+?,"
    tmp_ls = re.findall(tmp_reg, m3u8_text)

    pos1 = m3u8_text.find(tmp_ls[0])
    pos1_ = pos1 + len(tmp_ls[0])

    pos2_ = m3u8_text.find(tmp_ls[1], pos1_)

    str_ = m3u8_text[pos1_ + 1: pos2_]

    return str_[str_.rfind('.') + 1: len(str_) - 1]


def assemble_new_request(row, protocol, host, prefix):
    """
    拼接出新的请求地址
    """
    if row[0] == '/':
        return protocol + "://" + host + row
    else:
        return prefix + row


def get_speed_displayed(start_time, download_end_time, end_time, file_path, name):
    """
    对运行时间和下载速度进行显示（非进度条）
    """
    precise = "{0:.2f}"

    total_time = precise.format(end_time - start_time)
    total_download_time = precise.format(
        os.path.getsize(os.path.join(file_path, name+".mp4")) / (download_end_time - start_time) / 1024)

    print("【INFO】 视频下载成功！ 一共耗时：%ss  平均下载速度：%sKB/s" % (total_time, total_download_time))


class Crawler:
    _UNREACHABLE_STOP = False  # 资源完全重试后仍不可达退出标志

    __attrs__ = ["m3u8_reg", "m3u8_flag", "ts_reg", "tries", "download_base_path", "name", "folder_need", "ts_suffix",
                 "encrypt_method", "encrypt_file", "encrypt_key", "download_queue_length", "completed_queue_length",
                 "has_more_clip", "detect_queue_time", "total_clips", "current_clips", "merge_total",
                 "single_delete_length", "start_time", "download_end_time", "end_time",
                 "use_ip_proxy_pool", "crypt_ls", "auto_bitrate", "auto_bitrate_level"]

    def __init__(self, folder_need=None, download_queue_length=None, detect_queue_time=None,
                 single_delete_length=None, auto_bitrate=None, auto_bitrate_level=None):

        #assign default vaules to params which have not assigned
        folder_need = True if folder_need is None else folder_need
        download_queue_length = 200 if download_queue_length is None else download_queue_length
        detect_queue_time = 10 if detect_queue_time is None else detect_queue_time
        single_delete_length = 100 if single_delete_length is None else single_delete_length
        auto_bitrate = False if auto_bitrate is None else auto_bitrate
        auto_bitrate_level = "HIGHER" if auto_bitrate_level is None else auto_bitrate_level

        # m3u8文件判断正则表达式
        self.m3u8_reg = r".*\.m3u8.*"
        # 是否为新的m3u8文件
        self.m3u8_flag = False

        # ts文件判断正则表达式
        self.ts_reg = r".*\.ts.*"

        # 请求资源失败重试次数
        self.tries = 20

        # 导出路径
        self.download_base_path = ""
        # 文件夹和最终导出视频文件名
        self.name = ""
        # 是否视频需要放在文件夹中
        self.folder_need = folder_need

        # ts文件后缀（应对修改后缀）
        self.ts_suffix = "ts"

        # 加密方法
        self.encrypt_method = None
        # 服务器端加密文件名
        self.encrypt_file = None
        # 读取的加密密钥（对称加密）
        self.encrypt_key = None
        # 解密对象集合
        self.crypt_ls = {"AES-128": AES}

        # 执行请求的线程数
        self.download_queue_length = download_queue_length
        # 在一个时间片内完成的线程数
        self.completed_queue_length = 0
        # 是否还有未下载切片
        self.has_more_clip = True
        # 补充线程冷却时间
        self.detect_queue_time = detect_queue_time
        # 一共需下载的切片数
        self.total_clips = 0
        # 当前下载完成的切片数
        self.current_clips = 0
        # 当前已合成的切片数
        self.merge_total = 0
        # 单次删除切片数
        self.single_delete_length = single_delete_length

        # 标记开始时间
        self.start_time = None
        # 标记下载结束时间
        self.download_end_time = None
        # 标记最终结束时间
        self.end_time = None

        # 是否使用代理IP池
        self.use_ip_proxy_pool = False

        # 是否自动选择比特率
        self.auto_bitrate = auto_bitrate
        # 自动比特率的默认选择
        self.auto_bitrate_level = auto_bitrate_level
        
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass    

    def download_video_from_m3u8_c(self):
        """ 下载m3u8-控制台版 """

        m3u8 = self.prepare_download()

        self.start_time = time.time()
        m3u8 = m3u8.strip(' ')
        file_path, ts_name_ls = self.download_ts_files(self.get_ts_list(m3u8))

        self.merge_and_delete_ts_set(file_path, ts_name_ls)

    def download_video_from_m3u8_p(self, m3u8, download_base_path, name):
        """ 下载m3u8-调用参数版 """

        if not utils.check_dir_file_valid(name):
            raise NameInvalidError
        else:
            file_path = os.path.join(download_base_path, name)
            if os.path.exists(file_path):
                raise NameRepeatedError(name)
            else:
                if re.match("^[a-zA-Z]:(\\\\[^\\/:\*\?\"<>\|]+)*\\\\?$", file_path) is None:
                    raise PathNotADirectoryError(file_path)
                
                if self.auto_bitrate and self.auto_bitrate_level != "HIGHEST" and self.auto_bitrate_level != "LOWEST":
                    raise BitrateLevelInvalidError(self.auto_bitrate_level)
                
                self.download_base_path = download_base_path
                self.name = name

                os.makedirs(file_path)

        self.start_time = time.time()
        m3u8 = m3u8.strip(' ')
        file_path, ts_name_ls = self.download_ts_files(self.get_ts_list(m3u8))

        self.merge_and_delete_ts_set(file_path, ts_name_ls)

        if not self.folder_need:
            self.move_video_higher(file_path)

    def prepare_download(self):
        """ 接收存储名，创建存储目录 """

        while True:
            m3u8 = input("m3u8_address: ")
            download_base_path = input("restore_path: ")
            name = input("video_name: ")
            file_path = os.path.join(download_base_path, name)

            if utils.check_dir_file_valid(name):
                if not os.path.exists(file_path):
                    try:
                        os.makedirs(file_path)
                        self.download_base_path = download_base_path
                        self.name = name

                        break
                    except NotADirectoryError:
                        print("【Error】 无效路径")
                else:
                    print("【Error】 视频名字已存在")
            else:
                print("【ERROR】 文件名不能包含特殊字符")

        return m3u8

    def get_ts_list(self, m3u8):
        """ 得到需要下载的ts列表 """

        while True:
            ls = self.handle_m3u8(m3u8)

            if not self.m3u8_flag:
                ts_ls = ls
                break
            else:
                m3u8 = ls

        return ts_ls

    def handle_m3u8(self, m3u8):
        """ 对m3u8文件进行一系列处理 """

        url_ = analyze_url(m3u8)

        protocol = url_["protocol"]
        host = url_["host"]
        prefix = url_["resource_prefix"]

        try:
            print("【INFO】 正在请求m3u8文件...")
            rsp = request_get(m3u8, self.tries, timeout=5)

            if rsp.status_code == 200:
                res = self._m3u8_has_more_judge(rsp, protocol, host, prefix)
                if self.m3u8_flag:
                    return res

                self._ts_is_encrypted_judge(rsp, prefix)

                return self._collect_ts_files(rsp, protocol, host, prefix)
            else:
                raise ResponseStatusError
        except ResponseStatusError as e:
            print("\n【ERROR】 m3u8文件获取异常，下载失败")
            print(e)
            exit(-62)
        except RequestError as e:
            print("\n【ERROR】 服务器不稳定，m3u8文件无法获取，下载失败")
            print(e)
            exit(-61)

    def _m3u8_has_more_judge(self, rsp, protocol, host, prefix):
        """ 判断请求的m3u8文件是否指向新的m3u8文件地址 """

        print("【INFO】 m3u8文件获取成功，正在判断是否为新的m3u8地址...")

        if rsp.text.find(".m3u8") != -1:
            print("【INFO】 判断为新的m3u8地址")
            print("--------------------------------------------")

            self.m3u8_flag = True

            m3u8_ls = re.findall(self.m3u8_reg, rsp.text)
            if len(m3u8_ls) == 1:
                return assemble_new_request(m3u8_ls[0], protocol, host, prefix)
            else:
                print("【INFO】 检测到有多个m3u8文件: ")
                if self.auto_bitrate:
                    choice = len(m3u8_ls) if self.auto_bitrate_level == "HIGHEST" else 1
                    print("【INFO】 已做比特率自动选择")
                else:
                    for index, item in enumerate(m3u8_ls):
                        print("  " + str(index + 1) + " --- " + item)

                    while True:
                        choice_str = input("请选择: ")
                        choice = int(choice_str)
                        if choice <= len(m3u8_ls):
                            break

                return assemble_new_request(m3u8_ls[choice - 1], protocol, host, prefix)

        self.m3u8_flag = False

        return rsp

    def _ts_is_encrypted_judge(self, rsp, prefix):
        """ 判断ts文件是否被加密 """

        print("【INFO】 判断ts文件是否被加密...")

        if rsp.text.find("EXT-X-KEY") != -1:
            pos1 = rsp.text.find("METHOD=")
            pos2 = rsp.text.find(',', pos1)

            pos3 = rsp.text.find("URI=" + '"')
            pos4 = rsp.text.find('"', pos3 + len("URI=" + '"'))
            self.encrypt_method = rsp.text[pos1 + len("METHOD="): pos2]
            self.encrypt_file = rsp.text[pos3 + len("URI=" + '"'): pos4]

            print("【INFO】 ts文件已被加密  加密算法: " + self.encrypt_method + "  加密文件名: " + self.encrypt_file)
            self.download_encrypt_file_handler(prefix + self.encrypt_file)

    def _collect_ts_files(self, rsp, protocol, host, prefix):
        """ 获取ts列表集合 """

        print("【INFO】 正在获取ts文件列表...")
        self.m3u8_flag = False
        ts_ls = re.findall(self.ts_reg, rsp.text)

        if len(ts_ls) == 0:
            suffix = find_out_current_suffix(rsp.text)

            print("【INFO】 检测到ts后缀名已被修改为." + suffix)
            self.ts_reg = r".*\." + suffix + ".*"
            self.ts_suffix = suffix
            ts_ls = re.findall(self.ts_reg, rsp.text)

        for index, item in enumerate(ts_ls):
            ts_ls[index] = assemble_new_request(ts_ls[index], protocol, host, prefix)

        return ts_ls

    def download_ts_files(self, ts_ls):
        """ 下载所有的ts文件 """

        self.total_clips = len(ts_ls)

        file_path = os.path.join(os.path.join(self.download_base_path, self.name))

        # IP代理池
        self.use_ip_proxy_pool = False  # TODO
        if self.use_ip_proxy_pool:
            print("【INFO】 IP代理准备中...")
            type_ = ts_ls[0][:ts_ls[0].find(':')]
            proxies_ip = proxies_generate.get_proxies_ip(type_, self.total_clips)
            print("【INFO】 IP代理准备完成,已待命IP代理数为: " + str(len(proxies_ip)))

        utils.progress_bar(0, len(ts_ls), prefix="ts文件集", suffix="下载中...", completed_suffix="ts文件集下载成功!")

        download_queue = []

        index = -self.download_queue_length + 1  # 这个1不可省略，因为下面的判断为 <self.completed_queue_length，不+1会导致有一个切片一直无法请求

        proxies_ip_index = 0
        ts_it = iter(ts_ls)
        ts_name_ls = []

        while self.current_clips < self.total_clips:
            while index < self.completed_queue_length:
                try:
                    item = next(ts_it)
                except StopIteration:
                    self.has_more_clip = False
                    break

                ts_name = item[item.rfind('/') + 1: item.rfind(self.ts_suffix)] + "ts"

                ts_req = threading.Thread(args=(item, file_path, ts_name,
                                                proxies_ip[proxies_ip_index] if self.use_ip_proxy_pool is True else None
                                                ), target=self.download_ts_handler)

                download_queue.append(ts_req)
                index += 1
                proxies_ip_index += 1
                ts_name_ls.append(ts_name)

            self.completed_queue_length = 0

            for ts_req in download_queue:
                ts_req.setDaemon(True)
                ts_req.start()

            if self._UNREACHABLE_STOP:
                exit(-71)

            if self.has_more_clip:
                time.sleep(self.detect_queue_time)

            index = 0
            download_queue.clear()

        return file_path, ts_name_ls
    

    def download_encrypt_file_handler(self, encrypt_url):
        """ 密钥文件下载处理器 """

        try:
            self.encrypt_key = request_get(encrypt_url, self.tries, timeout=5).text
            print("【INFO】 获取到加密密钥")
        except RequestError:
            print("\n【ERROR】 服务器不稳定，密钥文件无法获取，下载失败")
            exit(-73)

    def download_ts_handler(self, ts_url, file_path, file_name, proxy_ip=None):
        """ ts目标文件下载处理器 """

        try:
            if self.use_ip_proxy_pool:
                rsp = request_get(ts_url, self.tries, timeout=5, proxy_ip=proxy_ip)
            else:
                rsp = request_get(ts_url, self.tries, timeout=5)

            with open(os.path.join(file_path, file_name), 'wb') as file:
                if self.encrypt_method is None:
                    file.write(rsp.content)
                else:
                    crypt_obj = self.crypt_ls[self.encrypt_method]
                    cryptor = crypt_obj.new(self.encrypt_key.encode("utf-8"), crypt_obj.MODE_CBC)
                    file.write(cryptor.decrypt(rsp.content))

            self.current_clips += 1
            self.completed_queue_length += 1

            utils.progress_bar(self.current_clips, self.total_clips, decimals=2, prefix="ts文件集", suffix="下载中..."
                              , completed_suffix="ts文件集下载成功")

        except RequestError:
            print("\n【ERROR】 服务器不稳定，部分ts文件无法获取，下载失败")
            self._UNREACHABLE_STOP = True
        except OSError:
            print("【ERROR】 请检查是否磁盘空间不足")
            self._UNREACHABLE_STOP = True
        except KeyError:
            print("【ERROR】 请添加密钥对象")
            self._UNREACHABLE_STOP = True

    def merge_and_delete_ts_set(self, file_path, ts_name_ls):
        """ ts文件集的合并、删除，生成最终的目标视频文件 """

        self.download_end_time = time.time()

        self._merge_set(file_path, ts_name_ls)
        self._delete_set(file_path, ts_name_ls)
        self.end_time = time.time()

        get_speed_displayed(self.start_time, self.download_end_time, self.end_time, file_path, self.name)

    def _merge_set(self, file_path, ts_name_ls):
        """ 存入ts文件名称顺序，并用ffmpeg进行视频文件合成 """

        for item in ts_name_ls:
            with open(os.path.join(file_path, "ts_ls.txt"), "a+") as file:
                file.write("file '" + os.path.join(file_path, item) + "'")
                file.write('\n')

        merge_cmd = "ffmpeg.exe -y -f concat -safe 0 -i " + '"' + os.path.join(file_path, "ts_ls.txt") + '"' + " -c copy " \
                    + '"' + os.path.join(file_path, self.name + ".mp4") + '"'

        p = subprocess.Popen(merge_cmd, shell=True, cwd=os.path.abspath(os.path.dirname(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("【INFO】 合并ts文件中...")
        p.communicate()

    def _delete_set(self, file_path, ts_name_ls):
        """ 清理所有ts文件和顺序文件 """

        print("【INFO】 开始清理ts文件...")
        index = 0
        delete_total = 0
        del_cmd = "del /a /f /q "

        while delete_total < len(ts_name_ls):
            while index < self.single_delete_length:
                try:
                    del_cmd += ts_name_ls[delete_total] + ' '
                    index += 1
                    delete_total += 1
                except IndexError:
                    break

            p = subprocess.Popen(del_cmd, shell=True, cwd=file_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            utils.progress_bar(delete_total, len(ts_name_ls), decimals=2, prefix="删除ts文件", suffix="删除中..."
                              , completed_suffix="切片删除完成!")
            p.communicate()

            index = 0
            del_cmd = "del /a /f /q "

        del_cmd = "del /a /f /q ts_ls.txt"
        subprocess.call(del_cmd, shell=True, cwd=file_path)

    def move_video_higher(self, file_path):
        shutil.move(os.path.join(file_path, self.name + ".mp4"), os.path.join(self.download_base_path, self.name + ".mp4"))
        shutil.rmtree(file_path)