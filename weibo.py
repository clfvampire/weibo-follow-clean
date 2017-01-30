#!/usr/bin/python
# -*- coding: utf-8 -*-
'''weibo'''

import time
import json
import requests
from bs4 import BeautifulSoup

URL = 'http://weibo.com/{0}/fans?'
UNURL = 'http://weibo.com/aj/f/remove?ajwvr=6&__rnd={t}'

COOKIES = {
    'SUB': '',
}

HEADERS = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': URL,
    'Connection': 'keep-alive',
}

PARAMS = {
    'pids':'Pl_Official_RelationFans__88',
    'cfs':'600',
    'relate':'fans',
    't':1,
    'f':1,
    'Pl_Official_RelationFans__88_page':'1',
    'ajaxpagelet':'1',
    'ajaxpagelet_v6':'1',
    '__ref':'/{0}/fans?topnav=1&wvr=6&mod=message&need_filter=1&is_search=1',
    '_t':'FM_{t}'.format(t=time.time())
}

def remove(nick, uid):
    """移除粉丝"""
    fandata = {
        'uid': uid,
        'fnick': nick,
        '_t': 0
    }
    tmp = requests.post(
        url=UNURL.format(t=time.time()), data=fandata, headers=HEADERS, cookies=COOKIES).json()
    if tmp.get('code') == "100000":
        # 安全起见留个档，起码你知道误删了谁 _(:з)∠)_
        with open('delete.txt', 'a', encoding='utf-8') as file:
            file.write(u"移除粉丝 {0} 成功\n".format(nick))
        print(u"移除粉丝 {0} 成功".format(nick))
    else:
        print(u"移除粉丝 {0} 失败，请尝试重新获取cookies".format(nick))

def main():
    """主程序"""
    print(PARAMS['Pl_Official_RelationFans__88_page'])
    resp = requests.get(url=URL, headers=HEADERS, cookies=COOKIES, params=PARAMS)
    resp = resp.text.replace('<script>parent.FM.view(', '').replace(')</script>', '')
    resp = json.loads(resp)
    fanlist = BeautifulSoup(resp.get('html'), "lxml")
    for fan in fanlist.select("div[class=info_name\\ W_fb\\ W_f14]"):
        name = fan.text.replace('\n', '')
        wid = fan.a.attrs.get('usercard').split('&')[0][3:]
        data = fan.find_next_sibling('div').text
        data = data.replace(' ', '').strip('\n').split('\n')
        data[0] = float(data[0].replace('关注', ''))
        data[1] = float(data[1].replace('粉丝', ''))
        data[2] = float(data[2].replace('微博', ''))
        # 负责的‘神奇’逻辑
        # 粉丝小于10 且 关注大于50 且 微博小于10 --> 辣鸡粉丝（会误伤）
        if data[1] < 10 and data[0] > 50 and data[2] < 10:
            remove(name, wid)
        # 从来没发过微博
        elif data[2] == 0:
            remove(name, wid)
        else:
            pass


if __name__ == '__main__':
    # 从后往前清理避免遗漏
    print(u'脚本需要手动粘贴cookie，请复制cookie中的SUB字段（=后的部分）粘贴后回车')
    COOKIES['SUB'] = input('cookie-->')
    print(u'脚本需要账号数字ID，输入你自己微博的数字ID后回车')
    WID = input('ID-->')
    URL = 'http://weibo.com/{0}/fans?'.format(WID)
    PARAMS['__ref'] = PARAMS['__ref'].format(WID)
    for pn in range(10, 0, -1):
        PARAMS['Pl_Official_RelationFans__88_page'] = pn
        main()
