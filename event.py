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
        # Tag finish
        if config.is_finished:
            return 200, "已经标记完成"

        config.is_finished = True
        card_dict = config.last_card_content
        # TODO: is_finished to button_text
        card_dict["data"]["template_variable"]["is_finished"] = "已完成"

        send_task_card(card_dict)
        config.save_to_json()
    elif data.action.tag == "select_person":
        # Tag select_person
        if config.is_finished:
            return 200, "已经标记完成"

        creditor = find_people_by_open_id(data.action.option)
        debtor = find_people_by_open_id(data.open_id)

        config.debt.append(Debt(creditor.name, debtor.name))
        config.last_people = creditor.name
        if config.is_first:
            card_content = get_morning_card_content(creditor.name)
        else:
            card_content = get_evening_card_content(creditor.name)
        config.last_card_content = card_content
        send_task_card(card_content)
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
    app.run(port=7777)
