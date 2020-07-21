from argparse import ArgumentParser
import requests
from time import time, sleep
from requests.cookies import RequestsCookieJar
from json import dumps

url_danmaku = 'https://api.bilibili.com/x/v2/dm/search?oid={}&type=1&order=ctime&pn=1&ps=50'
url_cid = 'http://api.bilibili.com/x/player/pagelist?bvid={}'
url_mid = 'http://api.bilibili.com/x/member/web/account'
url_sendmsg = 'https://api.vc.bilibili.com/web_im/v1/web_im/send_msg'


class Main:
    def __init__(self, args):
        self.session = requests.session()
        self.cookies()
        self.mid = self.session.get(url_mid).json()['data']['mid']
        cid = self.session.get(url_cid.format(args.BVid)).json()['data'][0]['cid']
        history = []
        while True:
            t = time()
            mid_list = [i['mid'] for i in self.session.get(url_danmaku.format(cid)).json()['data']['result']]
            for i in mid_list:
                if not i in history:
                    self.send_msg(i)
                    history.append(i)
                    print(i)
            sleep(args.time - time() + t)

    def cookies(self):
        cookies = RequestsCookieJar()
        with open('cookies.txt', 'r') as f:
            cookies.set('SESSDATA', f.read(), domain='.bilibili.com')
        self.session.cookies = cookies

    def send_msg(self, mid):
        with open('text.txt', 'r') as f:
            self.session.post(url_sendmsg, data={
                'msg[sender_uid]': self.mid,
                'msg[receiver_id]': mid,
                'msg[receiver_type]': 1,
                'msg[msg_type]': 1,
                'msg[content]': dumps({
                    'content': f.read()
                })})


def parser():
    parser = ArgumentParser()
    parser.add_argument('BVid', type=str, help='输入您的视频的BV号')
    parser.add_argument('-t', '--time', type=int,
                        help='输入爬取的时间间隔，否则默认60s一次。'
                             '如果在间隔时间内，收到了50条以上的弹幕，则可能会遗漏发送。',
                        default=60)
    return parser.parse_args()


if __name__ == '__main__':
    Main(parser())
