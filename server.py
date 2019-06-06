import sys
import socketserver
from http.server import HTTPServer
from utils import util, http_util


class ThreadingHttpServer(socketserver.ThreadingMixIn, HTTPServer):
    pass


def main(port):
    httpd = ThreadingHttpServer(('', port), http_util.HTTPRequest)
    print('启动服务成功 http://%s:%d' % (util.get_host_ip(), port))
    httpd.serve_forever()


def argvs():
    if len(sys.argv) < 2:
        return 9999
    # return string.atoi(sys.argv[1])
    return int(sys.argv[1])


if __name__ == '__main__':
    util.check_version()
    main(argvs())
