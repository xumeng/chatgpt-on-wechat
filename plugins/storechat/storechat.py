from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from plugins import *
import plugins
import requests
import json


@plugins.register(name="StoreChat", desc="Store chat messages", version="0.1", author="amonxu.com", desire_priority=-1)
class StoreChat(Plugin):

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[StoreChat] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [ContextType.TEXT, ContextType.JOIN_GROUP, ContextType.PATPAT, ContextType.EXIT_GROUP]:
            return
        msg: ChatMessage = e_context["context"]["msg"]
        reply = Reply()
        reply.type = ReplyType.TEXT
        judge_content = self.judge_content_for_post(msg.content)
        if judge_content and judge_content["type"] == "post":
            topicId = judge_content["topicId"]
            reply.content = f"🫡收到, 已同步至♾️️区平台 https://qu.gegegugu.com/t/{topicId}"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
        else:
            e_context.action = EventAction.CONTINUE

    def judge_content_for_post(self, text: str):
        text = text.split(" ", 1)[1] if " " in text else text
        url = "http://localhost:8000/api/ai/gen/topic"
        payload = json.dumps({"content": text})
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            logger.info(f"[StoreChat] judge_content_for_post error, {response.status_code}, {response.text}")
            return None
