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

启动通知 daemon ：

```
aoscc notify
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

授权后台管理员：

```
aoscc admin
```

## 目录结构

本项目的顶层为 Python 包配置文件，将 `aoscc` 配置为一个包，并采用可编辑就地安装的方式运行，部分主要目录和文件大致功能如下。

- `user/` 用户视图：联络信息、参会注册、纪念品、账单
- `service/` 参会服务：如签到、志愿者招募、胸牌定制、住宿预订、PGP 签名、抽票投奖
- `admin/` 管理后台视图：用户列表、支付管理、住宿管理、通知管理、签到、抽票投奖、数据库和权限管理
- `util/` 功能性组件：数据库、权限管理、用户登录、邮件和 Telegram 发送、凭据签名、敏感信息加密、表单验证、模板渲染、缓存策略、错误页面等
- `templates/` 视图模板
    - `user/`, `service/`, `admin/` 为对应模块的对应模板
        - `index.html` 或 `base.html` 索引和导航模板 
    - `base.html` 为基底模板
    - `contact.html` 联系信息页面
    - `login.html` 用户登录页面
    - `error.html` 错误页面模板
- `static/` 各类静态资源
    - `badges/` 胸牌定制底板、模板、字体等
    - `vote/` 投票用图标
    - `common.css` 公共主样式表
- `__init__.py` Flask 应用对象工厂
- `config.py` 各类运行性设定
- `secret.py` 各类凭据，自行按照样例文件创建
- `schema.sql` 数据库表定义

## 许可协议

© 安同开源社区 2011 - 2025，保留一切权利。

为了能让与会者了解其信息的管理方式，本项目源代码开放供阅读和审计。

考虑到除了我们自己恐怕没人用得上这东西，因此未添加许可证，如有需要请 issue 联系。

### 第三方权利内容

- `static/badge/MiSans-*.ttf`
    - [MiSans 系列字体](https://hyperos.mi.com/font/zh/)版权属于小米公司
    - 该系列字体[允许嵌入软件使用](https://hyperos.mi.com/font/zh/faq/)
- `static/{wechat,alipay}.jpg`
    - 「微信支付」和「支付宝」商标权利属于其对应公司
- `static/normalize.css`
    - Copyright © Nicolas Gallagher and Jonathan Neal
    - 以 [MIT License](https://github.com/necolas/normalize.css/blob/master/LICENSE.md) 授权
- `static/xibao.jpg`
    - 作者不详，现作为一张模因图片广泛流传于互联网
