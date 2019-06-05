import http_util
import os
import sys
import socketserver
from http.server import HTTPServer
import utils




# def get_html(html):
#     filename = os.path.join(BASE_DIR, "templates", html)
#     with open(filename, 'r', encoding='utf-8', errors='ignore') as fd:
#         data = fd.read()
#     return data
#
#
# def get_static(file):
#     length = len(file)
#     if file.find("?") != -1:
#         length = file.find("?")
#
#     filename = os.path.join(BASE_DIR, os.path.normcase(file[1:length]))
#     # with open(filename, 'rb', encoding='utf-8', errors='ignore') as fd:
#     with open(filename, 'rb') as fd:
#         data = fd.read()
#     return data


class ThreadingHttpServer(socketserver.ThreadingMixIn, HTTPServer):
    pass


def main(port):
    httpd = ThreadingHttpServer(('', port), http_util.HTTPRequest)
    print('启动服务成功 http://%s:%d' % (utils.get_host_ip(), port))
    httpd.serve_forever()


def argvs():
    if len(sys.argv) < 2:
        return 9999
    # return string.atoi(sys.argv[1])
    return int(sys.argv[1])


if __name__ == '__main__':
    utils.check_version()
    main(argvs())
