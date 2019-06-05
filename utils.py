import json
import socket
import sys



def check_version():
    v = sys.version_info
    if v.major == 3 and v.minor >= 5:
        return
    print('你当前安装的Python是%d.%d.%d，请使用Python3.6及以上版本' % (v.major, v.minor, v.micro))
    exit(1)


def decode(s):
    try:
        return s.decode('utf-8')
    # except AttributeError:
    #     return s.encode('utf-8')
    except UnicodeDecodeError:
        return s.decode('gbk')


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


# 将字典转成字符串
def dict2str(d):
    s = ''
    for i in d:
        val = ''
        if d[i] is not None:
            val = d[i]
        s = s + i + ': ' + val + '\r\n'
    return s


def check_json(input_str):
    try:
        json.loads(input_str)
        return True
    except BaseException as e:
        print(e)
        return False
