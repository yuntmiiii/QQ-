# -*- coding: utf-8 -*-
import asyncio
import os
import time
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message
from openai import OpenAI
import httpx
import http.client
import json
import shutil
import requests
import json
import weibo

message_history = [{"role": "system",
             "content": "你叫cheems，是一只小狗，同时也是个很有帮助的小助手，你被放置到一个聊天群里回答问题，你的回答要尽可能简短. 碰到政治问题，你就回答‘这是cheems碰都不能碰的话题’"}
]# 实现gpt3群内的记忆功能
masterID = ''
apikey3 = '' # chatgpt3的key
apikey4 = '' # chatgpt4的key
appid = '' # 机器人id
secret = '' # 机器人的密钥
class reply:
    def __init__(self, message):
        self.message = message
        self.question = str(message.content)
        self.content = None
    def answer(self):
        global message_history
        if self.question.startswith(' /4'):
            client = OpenAI(
                base_url="https://api.xty.app/v1",
                api_key=apikey4,
                http_client=httpx.Client(
                    base_url="https://api.xty.app/v1", #代理
                    follow_redirects=True,
                ),
            )
            completion = client.chat.completions.create(
              model="gpt-4",
              messages=[
                {"role": "system", "content": "你叫cheems，是一只小狗，同时也是个很有帮助的小助手，你被放置到一个聊天群里回答问题。你的回答要尽可能简短."},
                {"role": "user", "content": self.question}
              ]
            )
            print(completion)
            return(completion.choices[0].message.content)
        elif (self.question.startswith(' /微博热搜')):
            return weibo.weibo()
        else:
            client = OpenAI(
                base_url="https://api.xty.app/v1",
                api_key=apikey3,
                http_client=httpx.Client(
                    base_url="https://api.xty.app/v1",
                    follow_redirects=True,
                ),
            )
            if len(message_history)>21: # 最多有20条记忆
                me = message_history
                message_history = [{"role": "system",
         "content": "你叫cheems，是一只小狗，同时也是个很有帮助的小助手，你的主人是陈宣衡，你被放置到一个聊天群里回答问题，这个群最强的人是凝神。你的回答要尽可能简短. 碰到政治问题，你就回答‘这是cheems碰都不能碰的话题’"}
                ]
                message_history = message_history + me[3:-1]
            message_history.append({"role": "user", "content": self.question})
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message_history
            )
            r = completion.choices[0].message.content
            message_history.append({"role": "assistant", "content": r})
            print(message_history)
            return (r)
          
_log = logging.get_logger()
class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")
    async def on_group_at_message_create(self, message: GroupMessage):
        print(message)
        print(message.content)
        if '/图片254543' in message.content:
            print('tupian')
            file_url = picture(message.content.replace('/图片', ''))
            if file_url:
                print(file_url)
            # file_url = 'https://midjourncy.com/mj/image/1721441107206180'
                try:
                    uploadMedia = await message._api.post_group_file(
                        group_openid=message.group_openid,
                        file_type=1,
                        url=file_url
                    )
                    await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=7,
                        msg_id=message.id,
                        media=uploadMedia
                    )
                except:
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        content=reply('图片g了'))
                    _log.info(messageResult)
            else:
                messageResult = await message._api.post_group_message(
                group_openid=message.group_openid,
                  msg_type=0,
                  msg_id=message.id,
                  content=reply('图片g了'))
                _log.info(messageResult)
        else:
            reply1 = reply(message)
            if message.author.member_openid == masterID:
                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    msg_id=message.id,
                    content=reply1.answer_master())
                _log.info(messageResult)
            else:

                messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                      msg_type=0,
                      msg_id=message.id,
                      content=reply1.answer())
                _log.info(messageResult)

if __name__ == "__main__":

    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=appid, secret=secret)
