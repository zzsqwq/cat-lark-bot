import argparse
import datetime
import json
import logging
import os

from lark_oapi.api.im.v1 import *

from client import client
from config import Config

config_dir = "config"
log_dir = "log"

config = Config.from_json_file(os.path.join(config_dir, "config.json"))

people_name_list = [people.name for people in config.people_list]
people_alternate_dict = {people_name_list[i]: people_name_list[(i + 1) % len(people_name_list)] for i in
                         range(len(people_name_list))}

weekday_name_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

logger = logging.getLogger(__name__)


def get_next_people(name: str) -> str:
    return people_alternate_dict[name]


def get_morning_card_content(name: str) -> dict:
    now = datetime.datetime.now()
    people_id_list = [{"value": people.open_id} for people in config.people_list]
    people = config.people_list[people_name_list.index(name)]
    card_content = {
        "type": "template",
        "data": {
            "template_id": "ctp_AA8KL9dtGDNL",
            "template_variable": {
                "peoples": people_id_list,
                "week_day": weekday_name_list[now.weekday()],
                "today_people": people.at("id")
            }
        }
    }
    return card_content


def get_evening_card_content(name: str) -> dict:
    now = datetime.datetime.now()
    people_id_list = [{"value": people.open_id} for people in config.people_list]
    people = config.people_list[people_name_list.index(name)]
    card_content = {
        "type": "template",
        "data": {
            "template_id": "ctp_AA8KPds6qTEq",
            "template_variable": {
                "peoples": people_id_list,
                "week_day": weekday_name_list[now.weekday()],
                "today_people": people.at("id"),
                "finish_button_text": "标记完成"
            }
        }
    }
    return card_content


def send_task_card(card_content: dict, name: str):

    people = config.people_list[people_name_list.index(name)]

    request = CreateMessageRequest().builder().receive_id_type("chat_id").request_body(
        CreateMessageRequestBody().builder().msg_type("interactive").receive_id(
            config.chat_id).content(
            json.dumps(card_content)).build()).build()

    response = client.im.v1.message.create(request)

    if not response.success():
        raise Exception(
            f"client.im.v1.chat.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
    message_id = response.data.message_id
    print("Message created, message_id: %s" % message_id)

    request = UrgentSmsMessageRequest.builder() \
        .message_id(message_id) \
        .user_id_type("open_id") \
        .request_body(UrgentReceivers.builder()
                      .user_id_list([people.open_id])
                      .build()) \
        .build()

    response = client.im.v1.message.urgent_sms(request)
    if not response.success():
        raise Exception(
            f"client.im.v1.message.urgent_sms failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")

    config.last_card_content = card_content


def send_morning_card():
    if config.is_finished:
        today_people = get_next_people(config.actual_people)
        config.actual_people = today_people
    else:
        today_people = config.last_people

    # check if is a creditor
    for index, debt in enumerate(config.debt):
        if debt.creditor == today_people:
            today_people = debt.debtor
            config.debt.pop(index)

    send_task_card(get_morning_card_content(today_people), today_people)

    config.is_finished = False
    config.last_people = today_people
    config.is_first = False
    config.save_to_json()


def send_evening_card():
    if config.is_finished:
        raise Exception("You have already finished your task today!")

    today_people = config.last_people

    send_task_card(get_evening_card_content(today_people), today_people)

    config.is_first = True
    config.save_to_json()


def main():
    parser = argparse.ArgumentParser(description="A lark bot that reminds somebody to shovel shit for cat.")
    parser.add_argument("--log_path", type=str, default=".", help="log file location")
    parser.add_argument("--debug", action="store_true", help="enable debug mode")

    args = parser.parse_args()

    # 第二天早上
    if config.is_first:
        send_morning_card()
    else:
        send_evening_card()


if __name__ == "__main__":
    main()
