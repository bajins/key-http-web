#!/usr/bin/env python
# -*- coding: utf-8 -*-
import imghdr
import os, sys, subprocess, json, socketserver
import socket
import string
from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler
# import xshellkey as xshellkey  # 导入包下的模块并取别名
from xshellkey import generate_key  # 指定导入包下的函数
from contenttype import judge_type  # 指定导入包下的函数

# 获取到当前执行文件目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_html(html):
    filename = os.path.join(BASE_DIR, "templates", html)
    with open(filename, 'r', encoding='utf-8', errors='ignore') as fd:
        data = fd.read()
    return data


def get_static(file):
    length = len(file)
    if file.find("?") != -1:
        length = file.find("?")

    filename = os.path.join(BASE_DIR, os.path.normcase(file[1:length]))
    # with open(filename, 'rb', encoding='utf-8', errors='ignore') as fd:
    with open(filename, 'rb') as fd:
        data = fd.read()
    return data


class LearningHTTPRequestHandler(BaseHTTPRequestHandler):
    def send_http_header(self, contentType='application/json;charset=utf-8'):
        origin = self.headers['Origin']
        self.send_response(200)
        self.send_header('Content-Type', contentType)
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'GET,POST')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def send_http_body(self, data):
        # 判断是否为bytes
        if isinstance(data, bytes):
            body = data
        # 判断是否为str
        elif isinstance(data, str):
            body = data.encode('utf-8', errors='ignore')
        else:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8', errors='ignore')
        self.wfile.write(body)

    def do_get(self):
        # self.close_connection = True
        accept = self.headers["Accept"].split(";")[0]
        if accept.find("image") != -1:
            self.send_http_header(judge_type(self.path) + ';charset=utf-8')
        else:
            self.send_http_header(self.headers["Accept"].split(",")[0] + ';charset=utf-8')

        if self.path == '/':
            self.send_http_body(get_html("index.html"))

        elif self.path != "/" and self.path.find("static") != -1:
            self.send_http_body(get_static(self.path))

        else:
            return self.send_error(404)

    def do_post(self):
        # self.close_connection = True

        if self.path != '/getKey':
            # return self.send_error(400)
            return self.send_http_body({'code': 400, 'msg': "请求路径不存在"})

        body = self.rfile.read(int(self.headers['Content-length']))
        qs = parse.parse_qs(body.decode('utf-8'))

        self.send_http_header()

        if 'app' not in qs.keys():
            return self.send_http_body({'code': 300, 'msg': "请选择产品"})
        if 'version' not in qs.keys():
            return self.send_http_body({'code': 300, 'msg': "请选择版本"})

        product = qs['app'][0]
        version = qs['version'][0]

        try:
            self.send_http_body({'code': 200, 'msg': "请求成功", 'key': generate_key(product, version)})
        except ValueError as e:
            self.send_http_body({'code': 500, 'msg': decode(e.output)})
        except subprocess.CalledProcessError as e:
            self.send_http_body({'code': 500, 'msg': decode(e.output)})
        except subprocess.TimeoutExpired as e:
            self.send_http_body({'code': 500, 'msg': decode(e.output)})
        except subprocess.CalledProcessError as e:
            self.send_http_body({'code': 500, 'msg': decode(e.output)})


class ThreadingHttpServer(socketserver.ThreadingMixIn, HTTPServer):
    pass


def main(port):
    httpd = ThreadingHttpServer(('', port), LearningHTTPRequestHandler)
    print('启动服务成功 http://' + get_host_ip() + ":%d" % port)
    print('按 Ctrl + C 结束...')
    httpd.serve_forever()


# functions ###################################################################


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


# check #######################################################################
def check_version():
    v = sys.version_info
    if v.major == 3 and v.minor >= 5:
        return
    print('你当前安装的Python是%d.%d.%d，请使用Python3.6及以上版本' % (v.major, v.minor, v.micro))
    exit(1)


def argvs():
    if len(sys.argv) < 2:
        return 3000
    # return string.atoi(sys.argv[1])
    return int(sys.argv[1])


if __name__ == '__main__':
    check_version()
    main(argvs())
