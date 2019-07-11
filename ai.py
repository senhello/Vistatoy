import requests
from bson import ObjectId
from uuid import uuid4
from setting import SPEECH, MONGODB, VOICE, CHAT_PATH, TULING_URL, TULING_DATA
import os

def get_file_content(filePath):
    os.system(f"ffmpeg -y -i {filePath}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {filePath}.pcm")
    with open(f"{filePath}.pcm", 'rb') as fp:
        return fp.read()

def audio2text(filePath):
    res = SPEECH.asr(get_file_content(filePath), 'pcm', 16000, {
        'dev_pid': 1536,
    })

    text = res.get("result")[0]
    print(text)

    return text


def text2audio(text):
    result = SPEECH.synthesis(text, 'zh', 1, VOICE)
    filename = f"{uuid4()}.mp3"
    file_path = os.path.join(CHAT_PATH,filename)
    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        # print(result)
        with open(file_path, 'wb') as f:
            f.write(result)

    return filename

def to_tuling(text, uid):
    TULING_DATA["perception"]["inputText"]["text"] = text
    TULING_DATA["userInfo"]["userId"] = uid
    res = requests.post(TULING_URL, json=TULING_DATA)
    res_json = res.json()
    text = res_json.get("results")[0].get("values").get("text")
    print(text)
    return text


def my_nlp_lowB(text,uid):
    # text = "我要给爸爸发消息"
    if "发消息" in text:
        toy_info = MONGODB.toys.find_one({"_id":ObjectId(uid)})
        for friend in toy_info.get("friend_list"):
            if friend.get("friend_nick") in text or friend.get("friend_remark") in text:
                filename = text2audio(f"可以给{friend.get('friend_remark')}发消息了")
                return {"from_user":friend.get("friend_id"),"chat":filename,"friend_type":friend.get('friend_type')}

    if "播放" in text or "我要听" in text or "唱一首" in text :
        content_list = MONGODB.content.find({})
        for content in content_list:
            if content.get("title") in text :
                return {"from_user": "ai", "music": content.get("music")}


    res = to_tuling(text,uid)
    filename = text2audio(res)
    return {"from_user": "ai", "chat": filename}


# print(text2audio("消息发送成功"))