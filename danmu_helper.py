import time, websocket, threading
from encode import msg_encode, msg_decode
from typing import Optional
from functools import reduce


def format_str(msg: str) -> str:
    return msg.replace('@S', '/').replace('@A', '@')


def reduce_msg(pre, current) -> dict:
    if len(current) > 1:
        key = format_str(current[0])
        value = format_str(current[1])
        pre[key] = value
    return pre


def handle_msg(msg):
    decoded_msg = msg_decode(msg)
    msg_list = decoded_msg.split('/')
    msg_key_value_list = [item.split('@=') for item in msg_list]
    res = reduce(reduce_msg, msg_key_value_list, {})
    msg_type = res.get('type')
    if msg_type is None or msg_type != 'chatmsg':
        return

    room_id = res['rid']
    nickname = res['nn']
    txt = res['txt']
    level = res['level']
    pic = f"https://apic.douyucdn.cn/upload/{res['ic']}_big.jpg"
    print(f"\033[32m房间号：{room_id}， "
          f"\033[36m昵称：{nickname}， "
          f"\033[35m弹幕：{txt}， "
          f"\033[34m等级：{level}， "
          f"\033[31m头像：{pic}")


class DanMuHelper(websocket.WebSocketApp):
    def __init__(self, url: str):
        super().__init__(url,
                         on_open=self._on_ws_open,
                         on_message=self._on_ws_message,
                         on_error=self._on_ws_error,
                         on_close=self._on_ws_close
                         )
        self.room_id: Optional[str] = None

    def start(self, room_id: str) -> None:
        self.room_id = room_id
        self.run_forever()

    def _login(self):
        login_str = f'type@=loginreq/roomid@={self.room_id}/dfl@=sn@AA=107@ASss@AA=1@Ssn@AA=108@ASss@AA=1@Ssn@AA=105' \
                    f'@ASss@AA=1@Ssn@AA=110@ASss@AA=1@Ssn@AA=undefined@ASss@AA=1/username@=417406996/uid@=417406996' \
                    f'/ver@=20190610/aver@=218101901/ct@=0/ '
        self._send_ws_msg(login_str)

    def _join_group(self):
        group_str = f'type@=joingroup/rid@={self.room_id}/gid@=1/'
        self._send_ws_msg(group_str)

    def _keep_heartbeat(self):
        t = threading.Thread(target=self._on_ws_heart_beat)
        t.setDaemon(True)
        t.start()

    def _send_ws_msg(self, msg):
        msg_bytes = msg_encode(msg)
        self.send(msg_bytes)

    def _on_ws_open(self, ws):
        self._login()
        self._join_group()
        self._keep_heartbeat()

    def _on_ws_message(self, ws, msg):
        handle_msg(msg)

    def _on_ws_error(self, ws, code, res):
        print(f'{self.room_id} --- 出错 --- {code} --- {res}')

    def _on_ws_close(self, ws):
        print(f'{self.room_id} --- 被迫关闭')

    def _on_ws_heart_beat(self):
        while True:
            heart_str = 'type@=mrkl/'
            heart_byte = msg_encode(heart_str)
            self.send(heart_byte)
            time.sleep(45)
