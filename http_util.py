import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib import parse
import log_util
import main
import utils
from xshell_key import generate_key  # 指定导入包下的函数
from content_type import judge_type  # 指定导入包下的函数

# 获取到当前执行文件目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.close_connection = True

    def send_http_header(self, content_type='application/json;charset=utf-8'):
        origin = self.headers['Origin']
        self.send_response(200)
        self.send_header('Content-Type', content_type)
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

    def parse_request(self):
        accept = self.headers["Accept"].split(";")[0]
        if accept.find("image") != -1:
            self.send_http_header(judge_type(self.path) + ';charset=utf-8')
        else:
            self.send_http_header(self.headers["Accept"].split(",")[0] + ';charset=utf-8')

        if self.path == '/':
            self.send_http_body(utils.get_html("index.html"))

        elif self.path != "/" and self.path.find("static") != -1:
            self.send_http_body(utils.get_static(self.path))

        else:
            return self.send_error(404)

    def do_post(self):

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
        except BaseException as e:
            self.send_http_body({'code': 500, 'msg': utils.decode(e.output)})

    # 根据url路由返回请求
    def url_request(self, path):
        # 如果不是静态文件
        if not os.path.isfile(BASE_DIR + path) and path not in main.urlpatterns:
            self.send_error(HTTPStatus.NOT_FOUND, '请求地址错误')
            # log_util.log_error("code %d, message %s", HTTPStatus.NOT_FOUND, '未找到')
            # self.log_error("code %d, message %s", HTTPStatus.NOT_FOUND, '未找到')
        elif path in main.urlpatterns:
            # 动态调用函数并传参
            result = eval(main.urlpatterns[path])(self)
            if result.find(".html") != -1:
                self.url_request(result)
                return

            # 动态导入模块
            # m = __import__("root.main")
            if utils.check_json(result):
                self.response_head['Content-Type'] = 'application/json;charset=utf-8'
            else:
                self.response_head['Content-Type'] = 'text/html;charset=utf-8'

            self.send_http_body = result
            self.response_head['Set-Cookie'] = self.Cookie
        # 是静态文件
        else:
            path = BASE_DIR + path
            # 扩展名,只提供制定类型的静态文件
            self.response_head['Content-Type'] = judge_type(path)
            extension_name = os.path.splitext(path)[1]
            extension_set = {'.css', '.html', '.js'}
            if extension_name in extension_set:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fd:
                    data = fd.read()
                self.send_http_body = data
            # 其他文件返回
            else:
                self.requestline = HTTPStatus.OK
                with open(path, 'rb') as fd:
                    data = fd.read()
                self.send_http_body = data
