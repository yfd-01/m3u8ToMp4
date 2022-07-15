# m3u8ToMp4 (DEPRECATED)
~~download video by m3u8 url~~ <br/>
**Here is a substitute that supported asynchronous way**</br>
**<a href='https://github.com/yfd-01/aiom3u8'>aiom3u8</a>**

## Installing m3u8ToMp4 and Supported Versions:
m3u8ToMp4 is available on PyPI:
```python
$ python -m pip install m3u8ToMp4

# Using a mirror
$ python -m pip install m3u8ToMp4 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Basic Usage:

```python
import m3u8ToMp4

m3u8ToMp4.download("https://demo.com/demo/demo.m3u8", "C:\\videos", "video_name")  #using default config

m3u8ToMp4.download("https://demo.com/demo/demo.m3u8", "C:\\videos", "video_name",
              folder_need=False, download_queue_length=500, detect_queue_time=5,
              single_delete_length=200, auto_bitrate=True, auto_bitrate_level="HIGHEST")  #using adjustment params
```

**OR**

```python
import m3u8ToMp4

m3u8ToMp4.download_console()
#Then type params by console
```

## Adjustment Parameter Description:
* ```folder_need```: bool   &emsp;&emsp;&emsp;&emsp;&emsp;  - Whether you need a folder to contain the target video
* ```download_queue_length```: int   &emsp;&thinsp;   - The number of threads to download the video
* ```detect_queue_time```： int   &emsp;&emsp;&nbsp;   - The cooldown of replenishing the new threads to replace the threads that have completed the target in seconds
* ```single_delete_length```: int   &emsp;&thinsp;&thinsp;&thinsp;   - The number of slices merged at one time
* ```auto_bitrate```: bool    &emsp;&emsp;&emsp;&emsp;&nbsp;&thinsp;  - Whether you need a automatic selection if it has several options in video quality
* ```auto_bitrate_level```: str  &emsp;&emsp;&nbsp;&nbsp;    - The video quality in automatic selection, "HIGHEST" and "LOWEST" only 

```auto_bitrate``` and ```auto_bitrate_level``` need to be used together

## Module Supported:
### Supported Features:
* Find new m3u8 url automatically
* Find new ts file suffix if it is changed
* User select the video quality if it has several options - (called by download_console or setting auto_bitrate = False in download)
* Video quality automatic selection - (effected by setting auto_bitrate and auto_bitrate_level)
* AES-128-CBC Decrypt
* Multi-threading
### TODO 
* Random Proxies - reduce the odds of detecting
