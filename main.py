# coding: utf-8

import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart
import msgResponse

# standard app engine imports
from google.appengine.api import urlfetch
import webapp2

#project lib
from model import *

TOKEN = '487504665:AAExpqQkIV6arYE38jH8L6DzFJyI4eReRg4'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

# ================================
# http://localhost:8080/msg?msg=btc
class MsgHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        msg = self.request.get('msg')
        if msg:
            (state, res) = msgResponse.process_msg(msg)
            response_msg = u'msg = {0} <p> res> <p> {1}'.format(msg, res)
            self.response.write(response_msg)


class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(
                json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class NewsHandler(webapp2.RequestHandler):
    def get(self):

        def send_msg(chat_id, text, reply_to=None, no_preview=True, keyboard=None):
            # send_msg: 메시지 발송
            # chat_id: (integer) 메시지를 보낼 채팅 ID
            # text: (string) 메시지 내용
            # reply_to: (integer) ~메시지에 대한 답장
            # no_preview: (boolean) URL 자동 링크(미리보기) 끄기
            # keyboard: (list) 커스텀 키보드 지정
            #

            params = {
                'chat_id': str(chat_id),
                'text': text.encode('utf-8'),
            }
            if reply_to:
                params['reply_to_message_id'] = reply_to
            if no_preview:
                params['disable_web_page_preview'] = no_preview
            if keyboard:
                reply_markup = json.dumps({
                    'keyboard': keyboard,
                    'resize_keyboard': True,
                    'one_time_keyboard': False,
                    'selective': (reply_to != None),
                })
                params['reply_markup'] = reply_markup

            try:
                urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params)).read()
            except Exception as e:
                logging.exception(e)

        def broadcast(text):
            # broadcast: 봇이 켜져 있는 모든 채팅에 메시지 발송
            # text: (string) 메시지 내용

            for chat in get_enabled_chats():
                send_msg(chat.key.string_id(), text)

        urlfetch.set_default_fetch_deadline(60)
        (state, msg) = msgResponse.process_msg('btc')
        broadcast(msg)


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                                                    ('photo', 'image.jpg', img),
                                                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)

            elif text == '/account':
                reply(str(chat_id) + u' class = ' + str(getClass(chat_id)))

            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base + i * j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            else:
                reply('What command?')

            return

        # CUSTOMIZE FROM HERE

        (state, res) = msgResponse.process_msg(text)

        if state is 1:
            reply(res)
        else:
            if getEnabled(chat_id):
                reply(u'질문에 답할 수 없어요')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))
        # elif 'who are you' in text:
        #     reply('telebot starter kit, created by yukuku: https://github.com/yukuku/telebot')
        # elif 'what time' in text:
        #     reply('look at the corner of your screen!')
        # else:
        #     if getEnabled(chat_id):
        #         reply('I got your message! (but I do not know how to answer)')
        #     else:
        #         logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/msg', MsgHandler),
    ('/broadcast-news', NewsHandler),

], debug=True)
