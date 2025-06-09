import os
import functools
from io import BytesIO
from pathlib import Path
from contextlib import suppress

from flask import render_template, flash, g, redirect, url_for, request, send_file, current_app, abort
from PIL import Image, ImageDraw, ImageFont

from ...config import *
from ...util.db import fetch_one, insert_dict, delete_from
from ...util.form import Field, validate
from . import bp


def _my_badge_overlay() -> Path:
    badge_path = Path(current_app.instance_path) / 'badges'
    os.makedirs(badge_path, exist_ok=True)  # ensure save dir
    return badge_path / f'{g.uid}.png'


def _default_overlay() -> Path:
    return Path(current_app.static_folder) / 'badge' / 'default.png'


def _enlarge_overlay() -> bool:
    with suppress(Exception):
        new = Image.new("RGBA", (1575, 2362))  # 80x120mm dpi=500
        old = Image.open(_my_badge_overlay(), 'r', ('PNG',))
        old = old.crop((0, 0, min(old.width, 1200), min(old.height,800)))
        new.paste(old, (180, 750), old)  # paste to customize area
        old.close()
        new.save(_my_badge_overlay(), format="png")
        new.close()
        return True
    return False


def _generate_overlay(line1: str, line2: str) -> Image.Image | None:
    with suppress(Exception):
        text1 = Image.new("RGBA", (5000, 290))
        text2 = Image.new("RGBA", (2500, 600))
        draw1 = ImageDraw.Draw(text1)
        draw2 = ImageDraw.Draw(text2)
        font1 = ImageFont.truetype(Path(current_app.static_folder)/'badges'/'MiSans-Demibold.ttf', 250)
        font2 = ImageFont.truetype(Path(current_app.static_folder)/'badges'/'MiSans-Normal.ttf', 110)

        draw1.text((0, -45), line1, (0xff,0xff,0xff), font1)
        draw2.text((0, -20), line2, (0xe6,0xe6,0xe6), font2, spacing=32)
        bbox1 = text1.getbbox() or (0, 0, 0, 0)
        bbox2 = text2.getbbox() or (0, 0, 0, 0)
        text1 = text1.crop((bbox1[0], 0, bbox1[2], 290))
        text2 = text2.crop((bbox2[0], 0, bbox2[2], bbox2[3]))
        if text1.width > 1800:  # if line1 very long, resize to full width
            text1 = text1.resize((1200, text1.height*1200//text1.width))
        elif text1.width > 1180:  # if line1 slightly long, resize to smaller width
            text1 = text1.resize((1160, text1.height*1160//text1.width))
        if text2.width > 1200:  # if line2 too long, resize to full width
            text2 = text2.resize((1200, text2.height*1200//text2.width))
        if text2.height > 400:  # corp line2 bottom, avoid interfere with logo
            text2 = text2.crop((0, 0, text2.width, 400))

        overlay = Image.new("RGBA", (1575, 2362))  # 80x120mm dpi=500
        draw = ImageDraw.Draw(overlay)
        # draw the white line
        draw.rectangle([(182, 1121), (1392, 1130)], fill=(0xff,0xff,0xff))
        overlay.paste(text1, (180, 1110-text1.height), text1)
        overlay.paste(text2, (180, 1170), text2)
        return overlay


def badge_open(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if NOW() > BADGE_CLOSE:
            flash('定制已截止。')
            return redirect(url_for('.badge'))
        return view(*args, **kwargs)
    return wrapped


@bp.post('/badge')
@badge_open
def post_badge():
    if (file := request.files.get('overlay')) and file.filename:
        if file.filename.lower().endswith('.png'):
            file.save(_my_badge_overlay())
            if _enlarge_overlay():
                flash('上传成功，请查看效果预览！')
            else:
                with suppress(OSError):
                    os.remove(_my_badge_overlay())
                flash('图片生成失败！请调整后重试！')
        else:
            flash('文件类型错误！')
    else:
        if form := validate(
            Field('昵称', 'line1', 1, 20, str, True),
            Field('简介', 'line2', 0, 100, str, True),
        ):
            insert_dict('badge', form|{'uid': g.uid})
            if overlay := _generate_overlay(form['line1'], form['line2']):
                overlay.save(_my_badge_overlay(), 'PNG')
                overlay.close()
                flash('保存成功，请查看效果预览！')
            else:
                flash('图片生成失败！请重试！')

    return redirect(url_for('.badge'))


@bp.post('/badge/del')
@badge_open
def post_badge_del():
    with suppress(OSError):
        os.remove(_my_badge_overlay())
    delete_from('badge', {'uid': g.uid})
    flash('已清除。')
    return redirect(url_for('.badge'))


@bp.get('/badge/live')
def badge_live():
    line1 = request.args.get('line1', '')
    line2 = request.args.get('line2', '')
    if not line1 and not line2:  # on page load, no args
        if _my_badge_overlay().is_file():
            return send_file(_my_badge_overlay(), 'image/png')
        else:
            return send_file(_default_overlay(), 'image/png')
    if len(line1) > 20 or len(line2) > 100:  # check input
        abort(400)
    if overlay := _generate_overlay(line1, line2):
        png = BytesIO()  # buffer and return from memory
        overlay.save(png, format="png")
        overlay.close()
        png.seek(0)
        return send_file(png, 'image/png')
    # fallback to default if anything wrong
    return send_file(_default_overlay(), 'image/png')


@bp.get('/badge')
def badge():
    form = fetch_one('badge', {'uid': g.uid})
    file_exists = _my_badge_overlay().is_file()
    return render_template('badge.html', form=form, file_exists=file_exists)
