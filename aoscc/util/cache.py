import re

from flask import Response, request, current_app

from ..config import *
from . import bp


class _against_regex:
    def __init__(self, s: str):
        self.s = s
    def __eq__(self, pattern: str):
        return re.fullmatch(pattern, self.s) is not None

@bp.after_app_request
def cache_policy(response: Response):
    cache = response.cache_control
    cache.clear()
    if request.endpoint != 'static':
        cache.no_store = True
        cache.no_cache = True
        return response

    url = request.path.removeprefix(current_app.static_url_path+'/')
    cache.public = True
    match _against_regex(url):
        case 'normalize.css' | 'aosc.png':
            cache.max_age = 60*60*24*30
        case r'tshirt25/.+' | r'badge/.+':
            cache.max_age = 60*60
        case 'alipay.jpg' | 'wechat.jpg':
            cache.max_age = 60*20
        case 'common.css':
            cache.max_age = 60*5
        case _:
            cache.no_cache = True

    if cache.max_age and cache.max_age <= 60*60:
        cache.must_revalidate = True
    return response