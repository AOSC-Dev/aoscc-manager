from contextlib import suppress

import requests

from ..config import *
from ..secret import BOT_TOKEN


def send_telegram(uid: int, msg: str) -> bool:
    with suppress(Exception):
        r = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={
            'chat_id': uid,
            'text': msg,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }, timeout=10)
        if r.json()['ok']:
            return True
    return False


########## ABOVE: Flask Synch Part ##########
########## BELOW: TGBot Async Part ##########

from telegram import Update
from telegram.ext import filters, Application, ContextTypes, MessageHandler, CommandHandler

from .verify import sign_msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"""
{update.effective_user.first_name} 您好，欢迎注册 {TITLE} ！请点击以下链接登入会议注册系统，链接有效期 {LOGIN_TOKEN_EXPIRY} 分钟，您可随时发送 /start 获取登入链接。

如需更多协助，您可在此机器人会话留言，或邮件联系 aoscc@aosc.io 。

{URL_BASE}/login/{sign_msg('telegram', str(update.effective_user.id), LOGIN_TOKEN_EXPIRY*60)}
""", disable_web_page_preview=True)


async def private_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    fwded = await msg.forward(MGMT_ID)
    await fwded.reply_text(f'REPLY ME FOR USER {update.effective_user.id}')
    await msg.reply_text('您的消息已经转送至会务组，我们将尽快回复。')


async def reply_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    reply = msg.reply_to_message
    if not reply or reply.from_user.id != context.bot.id:
        return
    if not reply.text.startswith('REPLY ME FOR USER'):
        return
    try:
        uid = int(reply.text.removeprefix('REPLY ME FOR USER '))
    except ValueError:
        return
    await msg.copy(uid)
    await msg.reply_text('回复已经转送至用户。')


def bot_main():
    bot = Application.builder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler('start', start, filters.ChatType.PRIVATE))
    bot.add_handler(MessageHandler(filters.ChatType.PRIVATE, private_msg))
    bot.add_handler(MessageHandler(filters.Chat(MGMT_ID), reply_msg))

    bot.run_polling()


if __name__ == '__main__':
    bot_main()