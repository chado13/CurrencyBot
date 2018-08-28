import requests
from bs4 import BeautifulSoup as bs
from apscheduler.schedulers.blocking import BlockingScheduler
import telegram
import pytz
from datetime import datetime
import os
from prettytable import PrettyTable
import pandas as pd
import json
 
  #수정 후 아래 명령어 실행                  
  # heroku ps:scale clock=1 
  # git push heroku master

SEOUL_TZ = pytz.timezone('Asia/Seoul')
today_index = datetime.now(SEOUL_TZ).weekday()

sched = BlockingScheduler()


def telebot(message):
    """
    텔레그램 봇에 메세지 전송 명령 메소드
    """
    with open('secret.json') as f:
        token = json.loads(f.read())['token']
    bot = telegram.Bot(token=token)
    chat_id = bot.getUpdates()[-1].message.chat.id
    bot.sendMessage(chat_id=chat_id, text= message)
# @sched.scheduled_job('interval', seconds=3)
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=10)
def parse():
    """
    네이버 증권 내 환율 정보를 파싱하는 메소드
    """
    url = "https://finance.naver.com/marketindex/exchangeList.nhn"
    req = requests.get(url).text
    soup =bs(req, "lxml")
    tbody = soup.find('tbody')
    tbody = '<table>'+str(tbody)+'</table>'
    df = pd.read_html(tbody)[0]
    df = df.iloc[:4,[0,1,2]]
    df.columns=['통화','매매기준율','살때']
    temp_dict=df.to_dict('split')

    t = PrettyTable()
    column = temp_dict['columns']
    t.field_names = column
    lens = len(temp_dict['data'])
    for i in range(lens):
        t.add_row(temp_dict['data'][i])

    text = str(t)

    telebot(text)

sched.start()


