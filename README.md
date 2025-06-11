# AOSCC 会务管理系统

从 AOSCC 2025 起使用的信息化注册和各项服务管理系统。

## 部署方式

下载和配置环境：

```
git clone https://github.com/AOSC-Dev/aoscc-manager.git
cd aoscc-manager/
python3 -m venv venv
. venv/bin/activate
pip install -e .
```

编辑配置文件 `aoscc/config.py` 和 `aoscc/secret.py` 后启动测试服务器：

```
aoscc
```

启动 Telegram 机器人：

```
aoscc tgbot
```

生产环境请用 NGINX 反代 Gunicorn ：

```
gunicorn -w 4 --reload aoscc:make_app()
```

NGINX 推荐设置：

```
location / {
    proxy_pass http://127.0.0.1:6000;
    proxy_http_version 1.1;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 目录结构

本项目的顶层为 Python 包配置文件，将 `aoscc` 配置为一个包，并采用可编辑就地安装的方式运行，其各个子目录大概功能如下。

- `user/` 用户视图
    - `services/` 注册后服务，如签到、志愿者招募、胸牌定制、住宿预订、PGP 签名等
    - `templates/index.html` 用户视图公共模板
    - 其他注册前服务，如用户登录、会议注册、联络信息、纪念品订购、账单等
- `admin/` 管理后台视图
- `util/` 功能性组件，数据库、权限管理、邮件和 Telegram 发送、凭据签名、敏感信息加密、表单验证、模板渲染、缓存策略等
- `static/` 各类静态资源
    - `common.css` 公共主样式表
- `templates/`
    - `base.html` 基础页面模板
    - `contact.html` 联系信息页面
- `__init__.py` Flask 应用对象工厂
- `config.py` 各类运行性设定
- `secret.py` 各类凭据，自行按照样例文件创建
- `schema.sql` 数据库表定义

## 许可协议

为了能让与会者了解其信息的管理方式，本项目源代码开放供阅读和审计。

考虑到除了我们自己恐怕没人用得上这东西，因此未添加许可证，如有需要请 issue 联系。
