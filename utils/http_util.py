import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib import request
from utils import log_util, util
import main
from utils.content_type import judge_type  # 指定导入包下的函数

DEFAULT_ERROR_HTML = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <title>Error response</title>
</head>
<body>
<div style="width: 100%;text-align:center;">
    <h1>404 Not Found</h1>
</div>
</body>
<html>
"""

# 获取到当前执行文件目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = 'static'
CookieDir = 'cookie/'


class HTTPRequest(BaseHTTPRequestHandler):
    Method = None
    Url = None
    Protocol = None
    Host = None
    Port = None
    Connection = None
    CacheControl = None
    UserAgent = None
    Accept = None
    ContentType = None
    AcceptEncoding = None
    AcceptLanguage = None
    Cookie = None
    csrf_token = None
    session = None
    request_line = None
    request_data = dict()
    response_line = ''
    response_head = dict()
    response_body = ''

    # 解析请求体
    def resolve_headers(self):
        # 解析请求方法、url、协议
        self.request_line = self.requestline
        request_line = self.requestline.split(' ')
        self.Method = request_line[0].upper()
        # 请求地址和参数分割
        mpath, margs = request.splitquery(self.path)  # ?分割
        self.Url = mpath
        self.Protocol = request_line[2]
        # 如果有携带参数，并且请求方式为GET
        if util.not_empty(margs) and self.Method == "GET":
            parameters = margs.split('&')
            for parameter in parameters:
                if util.not_empty(parameter):
                    key, val = parameter.split('=', 1)
                    self.request_data[key] = val

        # 头部信息
        for header in self.headers:
            key = header.lower()
            val = self.headers[header]
            if key == "Host".lower():
                self.Host = val
            elif key == "Connection".lower():
                self.Connection = val
            elif key == "Cache-Control".lower():
                self.CacheControl = val
            elif key == "User-Agent".lower():
                self.UserAgent = val
            elif key == "Accept".lower():
                self.Accept = val
            elif key == "Content-Type".lower():
                self.ContentType = val
            elif key == "Accept-Encoding".lower():
                self.AcceptEncoding = val
            elif key == "Accept-Language".lower():
                self.AcceptLanguage = val
            elif key == "Cookie".lower():
                ck = val.split('; ')
                for k in ck:
                    if k.lower() == "csrftoken":
                        self.csrf_token = k.split("=")[0]
                    else:
                        self.Cookie = k
            # self.head[key] = val

        # 解析参数，并且请求方式为POST
        if util.not_empty(self.headers['Content-length']) and self.Method == "POST":
            body = self.rfile.read(int(self.headers['Content-length'])).decode('utf-8')
            if body.find("Content-Disposition") != -1:
                hd = body[body.find("\r\n"):len(body)].replace('\r\n\r\n', '')
                form = hd.split('\r\n')
                for content in form:
                    if content.find("form-data") != -1:
                        param = content.split('"')
                        self.request_data[param[1]] = param[2]
            else:
                params = body.split("&")
                if util.not_empty(params[0]):
                    for param in params:
                        k, v = param.split("=", 1)
                        self.request_data[k] = v

    # 设置响应头
    def send_http_header(self, content_type='application/json;charset=utf-8'):
        # 设置响应状态码
        self.send_response(HTTPStatus.OK)
        # 设置响应类型
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
        self.send_header('Access-Control-Allow-Methods', 'GET,POST')
        self.send_header('Access-Control-Max-Age', '86400')

    # 设置响应内容
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

    def do_GET(self):
        self.do_POST()

    def do_POST(self):
        self.resolve_headers()
        self.url_request(self.Url)

    # 根据url路由返回请求
    def url_request(self, path):

        file_path = get_file_path(path)
        self.send_http_header(judge_type(file_path))

        # 如果不是静态文件
        if not os.path.isfile(file_path) and path not in main.urlpatterns:
            self.response_line = HTTPStatus.NOT_FOUND
            self.send_http_header('text/html')
            self.end_headers()
            self.response_body = DEFAULT_ERROR_HTML.encode("utf-8")
            log_util.log_error("%s code %d, message %s", path, HTTPStatus.NOT_FOUND, '未找到')

        # 在路由中存在
        elif path in main.urlpatterns:
            # 动态调用函数并传参
            result = eval(main.urlpatterns[path])(self)
            # 如果返回的值是文件
            if os.path.isfile(get_file_path(result)):
                self.url_request(result)
                return

            # 动态导入模块
            # m = __import__("root.main")
            if util.check_json(result):
                self.send_http_header('application/json;charset=utf-8')
            else:
                self.send_http_header('text/html;charset=utf-8')

            self.send_header('Set-Cookie', self.Cookie)

            self.end_headers()

            self.send_http_body(result)
        # 是静态文件
        else:
            # if file_path.find("/public") != -1:
            #     filename = os.path.basename(file_path)
            #     self.send_header("Content-Disposition", "attachment; filename=" + filename)

            self.end_headers()

            # 扩展名,只提供制定类型的静态文件
            extension_name = os.path.splitext(file_path)[1]
            extension_set = {'.css', '.html', '.js'}
            if extension_name in extension_set:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as fd:
                    data = fd.read()
                self.send_http_body(data)
            # 其他文件返回
            else:
                with open(file_path, 'rb') as fd:
                    data = fd.read()
                self.send_http_body(data)


def get_file_path(path):
    if path.find(STATIC_DIR) == -1:
        file_path = STATIC_DIR + path
    elif path.find("/" + STATIC_DIR) != -1:
        file_path = path[path.find(STATIC_DIR):len(path)]

    return file_path
