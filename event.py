import os

import lark_oapi as lark
from flask import Flask
from lark_oapi.adapter.flask import *

from client import ENCRYPT_KEY, VERIFICATION_TOKEN
from config import Config, Person, Debt
from main import send_task_card, get_morning_card_content, get_evening_card_content

config_dir = "config"

config = Config.from_json_file(os.path.join(config_dir, "config.json"))

app = Flask(__name__)


# TODO: 注册事件回调

def find_people_by_open_id(open_id: str) -> Person:
    for people in config.people_list:
        if people.open_id == open_id:
            return people
    raise ValueError(f"Unknown open_id: {open_id}")


def do_interactive_card(data: lark.Card):
    config.update()
    if data.action.tag == "button":
        # 如果不是本人更改/管理员更改，返回报错
        action_people = find_people_by_open_id(data.open_id)
        if action_people.name != config.last_people and not action_people.is_admin:
            return 403, "无权限"

        # 如果已经完成，直接返回
        if config.is_finished:
            return 200, "已经标记完成"

        # 标记完成 -> 更新卡片信息 -> 保存配置 -> 返回卡片
        config.is_finished = True
        card_dict = config.last_card_content
        card_dict["data"]["template_variable"]["finish_button_text"] = "已完成"

        # send_task_card(card_dict)
        config.save_to_json()
        return lark.JSON.marshal(card_dict)
    elif data.action.tag == "select_person":
        # 如果不是本人更改/管理员更改，返回报错
        action_people = find_people_by_open_id(data.open_id)
        if action_people.name != config.last_people and not action_people.is_admin:
            return 403, "无权限"

        # 如果已经完成，直接返回
        if config.is_finished:
            return 200, "已经标记完成"

        # 添加负债信息 -> 更新当前值班人&卡片内容 -> 根据 is_first 分情况发送卡片 -> 保存当前配置
        creditor = find_people_by_open_id(data.action.option)
        debtor = find_people_by_open_id(data.open_id)

        config.debt.append(Debt(creditor.name, debtor.name))
        config.last_people = creditor.name
        if config.is_first:
            card_content = get_morning_card_content(creditor.name)
        else:
            card_content = get_evening_card_content(creditor.name)
        config.last_card_content = card_content
        send_task_card(card_content, creditor.name)
        config.save_to_json()
    else:
        raise ValueError(f"Unknown tag: {data.action.tag}")


# 注册卡片回调
card_handler = lark.CardActionHandler.builder(ENCRYPT_KEY, VERIFICATION_TOKEN, lark.LogLevel.DEBUG) \
    .register(do_interactive_card) \
    .build()


@app.route("/card", methods=["POST"])
def card():
    resp = card_handler.do(parse_req())
    return parse_resp(resp)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7777)
