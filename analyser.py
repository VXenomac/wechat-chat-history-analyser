# -*- coding: utf-8 -*-
'''
@File    :   analyser.py
@Time    :   2022/01/08 15:00:25
@Author  :   VXenomac
'''

# import lib
import re
import json
import pkuseg
import pandas as pd
from rich.console import Console
from pathlib import Path
from datetime import datetime
from dateutil.parser import parse
from collections import Counter
from rich.table import Table


def js2excel(path):
    with open(path, 'r') as f:
        load_dict = json.loads(f.read().replace('var data = ', ''))
    message = pd.DataFrame(load_dict['message']).rename(columns={'m_nsFromUsr': '发送人', 'm_uiCreateTime': '发送时间', 'm_nsContent': '消息内容'})
    message['发送时间'] = message['发送时间'].apply(lambda timestamp: datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %T'))
    ORDER = ['发送人', '发送时间', '消息内容']
    message = message[ORDER]
    return message


class WeChatMessageAnalyser():

    def __init__(self, message):
        self.message = message

    def 计算成为好友的天数(self):
        # 根据本地聊天记录计算与目标用户第一次聊天迄今为止的天数。如果换过手机等原因造成聊天记录缺失等的情况会导致数据不准确
        date = self.message.loc[0, '发送时间'][:10].split('-')
        date = f'{date[0]}年{date[1]}月{date[2]}日'
        return {
            '成为好友的日期': date,
            '成为好友的天数': (datetime.now() - parse(self.message.loc[0, '发送时间'])).days
        }
    
    def 计算聊天的情况(self):
        self.message['发送日期'] = self.message['发送时间'].apply(lambda x: x[:10])
        # 计算成为好友迄今为止当天至少发送过一条消息的天数
        unique_day = list(set(self.message['发送日期']))
        day_counter = Counter(day[:4] for day in unique_day)
        result = {f'{k} 年聊天的天数': v for k, v in day_counter.items()}
        result['总计聊天的天数'] = len(unique_day)
        # 计算成为好友迄今为止当天发送消息数量最多的日期
        message_day = self.message['发送日期'].to_list()
        frequent_day = Counter(message_day).most_common(1)[0]
        result['聊天最频繁的日期'] = {
            '日期': frequent_day[0],
            '消息数量': frequent_day[1]
        }
        # 计算一天 24 小时内聊天最频繁的时间段
        message_day_time = self.message['发送时间'].apply(lambda x: x[11:13]).to_list()
        frequent_day_time = Counter(message_day_time).most_common(1)[0]
        result['聊天最频繁的时间'] = {
            '时间': frequent_day_time[0],
            '消息数量': frequent_day_time[1]
        }
        # 聊天到最晚
        self.message['与 5 点相差的时间'] = self.message['发送时间'].apply(lambda x: (parse('05:00:00') - parse(x[11:])).seconds / 60)
        index = self.message['与 5 点相差的时间'].idxmin()
        result['聊天最晚的时间'] = {
            '日期': self.message.loc[index, '发送日期'],
            '发送时间': self.message.loc[index, '发送时间'][11:],
            '发送内容': self.message.loc[index, '消息内容']
        }
        return result
        
    
    def 计算消息量(self):
        return {
            '总共消息': self.message.shape[0],
            '收到消息': self.message[self.message['发送人'].notnull()].shape[0],
            '发送消息': self.message[self.message['发送人'].isnull()].shape[0]
        }


    def 计算关键词(self):
        content = ''
        for _, row in self.message.iterrows():
            pattern = re.compile(r'[A-Za-z]', re.S)
            if res := re.findall(pattern, row['消息内容']):
                continue
            else:
                content = f'{content} {row["消息内容"]}'
        # 设置停用词
        stop_words = [' ', '的', '了', '我', '是', '你', '好', '也', '就', '不', '吗', '个', '有', '还', '一', '都', '这', '在', '啊', '没', '要', '去', '太', '会', '那', '看', '哦', '说', '这个', '给', '很', '人', '天', '那个', '两', '他', '还是', '应该', '跟', '什么', ']', '她', '吧', '能', '对', '想', '然后', '[', '用', '做', '上', '时候', '！', '，', '得', '大', '但是', '自己', '下', '这样', '能', '着', '挺', '写', '一下', '？', '已经', '因为', '找', '小', '次', '和', '打', '呢', '好像', '可能', '呀', '感觉', '来', '没有', '嘛', '过', '行', '多', '啦', '把', '到', '再', '过', '柴]', '觉得', '这么', '先', '发']
        # 设置用户字典
        lexicon = ['笑死', '妹妹', '甜妹', '渣男', '预训练', '臭宝', '宝贝', '宝', '好滴', '牛蛙', '牛哇']
        seg = pkuseg.pkuseg(user_dict=lexicon, model_name='web')
        seg_list = seg.cut(content)
        seg_list = [word for word in seg_list if word not in stop_words]

        counter = Counter(seg_list)
        return {
            '关键词': counter.most_common(25)
        }


if __name__ == '__main__':
    console = Console()
    folder = '' # 替换为导出联系人的文件夹名称
    path = Path(folder) / 'js/message.js'
    message = js2excel(path)
    message.to_excel('消息.xlsx', index=False)
    message = pd.read_excel('消息.xlsx')
    analyser = WeChatMessageAnalyser(message)
    好友天数 = analyser.计算成为好友的天数()
    聊天情况 = analyser.计算聊天的情况()
    消息量 = analyser.计算消息量()
    关键词 = analyser.计算关键词()

    用户名 = '@一个轮子' # 替换为相应的用户名

    text_1 = f"你于[bold cyan]{好友天数['成为好友的日期']}[/bold cyan]与[bold red]{用户名}[/bold red]成为微信好友，迄今已过[bold green]{好友天数['成为好友的天数']}[/bold green]天，约[bold purple]{(好友天数['成为好友的天数'] / 365):.2f}[/bold purple]年。"
    text_2 = f"在你们成为微信好友的[bold blue]{好友天数['成为好友的天数']}[/bold blue]天中，你们共有[bold green]{聊天情况['总计聊天的天数']}[/bold green]天有过交流。在2021年你们聊得更加频繁了，共计[bold yellow]{聊天情况['2021 年聊天的天数']}[/bold yellow]天，一年约[bold cyan]{聊天情况['2021 年聊天的天数'] / 365 * 100:.0f}%[/bold cyan]的时间都有交流。"
    text_3 = f"你们互相共发了{消息量['总共消息']}条消息，其中你发给{用户名}{消息量['收到消息']} 条消息。"
    text_4 = f"你们在[bold cyan]{聊天情况['聊天最频繁的日期']['日期']}[/bold cyan]看起来有非常多的话想要说，相互发送共计{聊天情况['聊天最频繁的日期']['消息数量']}条消息。"
    text_5 = f"你们最常在[bold cyan]{int(聊天情况['聊天最频繁的时间']['时间'])}~{int(聊天情况['聊天最频繁的时间']['时间']) + 1}[/bold cyan]点聊天，其中有{聊天情况['聊天最频繁的时间']['消息数量']}条消息在这个时间段被发送，约占所有消息的[bold purple]{聊天情况['聊天最频繁的时间']['消息数量'] / 消息量['总共消息'] * 100:.2f}%[/bold purple]。"
    text_6 = f"在[bold cyan]{聊天情况['聊天最晚的时间']['日期']}[/bold cyan]这天，你们深夜{聊天情况['聊天最晚的时间']['发送时间'][:5]}还在聊天。你说：「{聊天情况['聊天最晚的时间']['发送内容']}」。"
    table = Table(show_header=True, header_style='bold magenta')
    table.add_column('关键词', style='dim', width=12)
    table.add_column('词频', justify='right')
    for key, value in 关键词['关键词']:
        table.add_row(key, str(value))
    print('\n')
    console.print(text_1 + '\n')
    console.print(text_2 + '\n')
    console.print(text_3 + '\n')
    console.print(text_4 + '\n')
    console.print(text_5 + '\n')
    console.print(text_6 + '\n')
    print('你们聊天时候经常提及：')
    console.print(table)
