def msg_encode(msg):
    # 数据体 以  \0 结尾
    msg = f'{msg}\0'

    # 数据体 字节类型
    msg_bytes = msg.encode('utf-8')

    # 整体的长度 等于 数据体 + 消息头(8个字节）
    msg_len = len(msg_bytes) + 8

    # 整体长度转 字节（占4个字节， 小端整数）
    msg_bytes_len = int.to_bytes(msg_len, 4, byteorder='little')

    # 消息类型转字节（占2个字节，小端整数）
    type_bytes = int.to_bytes(689, 2, byteorder='little')

    # 加密字段 和 保留字段。一样。都是0（占1个字节，小端整数）
    encode_bytes = int.to_bytes(0, 1, byteorder='little')

    #  整体分三个 部分  长度 + 头  +  数据体
    byte1 = msg_bytes_len
    byte2 = msg_bytes_len + type_bytes + encode_bytes + encode_bytes
    byte3 = msg_bytes

    return byte1 + byte2 + byte3


def msg_decode(msg_bytes):
    msg = ''
    # 分段获取 消息
    while len(msg_bytes) > 0:
        #  前 4  位表示 当前消息的长度
        content_length = int.from_bytes(msg_bytes[0: 4], byteorder='little')

        # 因为包含三部分 长度 + (头 + 消息)
        current_msg_bytes_len = 4 + content_length

        current_msg_bytes = msg_bytes[0: current_msg_bytes_len]

        msg_bytes = msg_bytes[current_msg_bytes_len: -1]

        # 长度 +  头  = 4 + 8 = 12
        content = current_msg_bytes[12: -1].decode('utf-8', 'ignore')
        msg += content

    return msg
