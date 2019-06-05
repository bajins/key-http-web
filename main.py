import json

from xshell_key import generate_key

urlpatterns = {"": "main.index", "/": "main.index", "/login": "main.login", "/login-page": "main.login_page",
               "/getKey": "main.get_key"}


def index(request):
    return "/index.html"


def login_page(request):
    return "/login.html"


def login(request):
    if request.Method != "POST":
        return json.dumps({'code': 401, 'msg': "请求方式错误"})
    name = request.request_data.get("name", "")
    if name.strip() == '':
        return json.dumps({'code': 300, 'msg': "请输入名称"})
    password = request.request_dataget("password", "")
    if password.strip() == '':
        return json.dumps({'code': 300, 'msg': "请输入密码"})

    request.process_session().set_cookie('name', '123')
    request.process_session().write_xml()
    return json.dumps({'code': 200, 'msg': "登录成功"})

    # if request.process_session().get_cookie('name') is not None:
    #     return 'hello, ' + request.process_session().get_cookie('name')
    # with open('root/login.html', 'r') as f:
    #     data = f.read()
    # return data


def get_key(request):
    # 判断是否是post请求
    if request.Method != 'POST':
        return json.dumps({'code': 401, 'msg': "请求方式错误"})

    app = request.request_data.get('app', "")
    if app.strip() == '':
        return json.dumps({'code': 300, 'msg': "请选择产品"})

    version = request.request_data.get('version', "")
    if version.strip() == '':
        return json.dumps({'code': 300, 'msg': "请选择版本"})

    key = generate_key(app.replace("+", " "), version)
    # 返回给用户  模版中使用到的users就是这里传递进去的
    return json.dumps({'code': 200, 'msg': "请求成功", 'key': key})
