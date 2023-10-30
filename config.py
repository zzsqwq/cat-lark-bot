import json
import shutil
from typing import *


class Debt:
    def __init__(self, creditor: str, debtor: str) -> None:
        self.creditor = creditor
        self.debtor = debtor


class Person:
    def __init__(self, name: str, open_id: str, is_admin: Optional[bool] = False) -> None:
        self.name = name
        self.open_id = open_id
        self.is_admin: Optional[bool] = is_admin

    def at(self, id_type: str = "id") -> str:
        return f'<at {id_type}="{self.open_id}"></at>'


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs) -> 'Config':
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, json_data: dict = None) -> None:
        if json_data:
            self.debt = [Debt(item['creditor'], item['debtor']) for item in json_data['debt']]
            self.is_first = json_data['is_first']
            self.last_people = json_data['last_people']
            self.is_finished = json_data['is_finished']
            self.actual_people = json_data['actual_people']
            self.last_card_content = json_data['last_card_content']
            self.people_list = [Person(item['name'], item['open_id'], item.get("is_admin")) for item in
                                json_data['people_list']]
            self.chat_id = json_data['chat_id']

    # Update config from json file
    def update(self, filename: str = None) -> None:
        """
        Update the config instance from the specified JSON file.
        If no filename is provided, use the previously stored filename.
        """
        if filename:
            Config.filename = filename
        if not hasattr(self, "filename"):
            raise Exception('No filename has been specified previously. Provide a filename to update from.')

        with open(self.filename, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        self.debt = [Debt(item['creditor'], item['debtor']) for item in json_data['debt']]
        self.is_first = json_data['is_first']
        self.last_people = json_data['last_people']
        self.is_finished = json_data['is_finished']
        self.actual_people = json_data['actual_people']
        self.last_card_content = json_data['last_card_content']
        self.people_list = [Person(item['name'], item['open_id'], item.get("is_admin")) for item in
                            json_data['people_list']]
        self.chat_id = json_data['chat_id']

    @classmethod
    def from_json_file(cls, filename: str) -> 'Config':
        with open(filename, 'r', encoding='utf-8') as f:
            cls.filename = filename
            json_data = json.load(f)
        return cls(json_data)

    def save_to_json(self) -> None:
        if self.filename:
            # 存 filename 之前对应对应的文件为 config.last.json
            shutil.copyfile(self.filename, self.filename.replace('.json', '.last.json'))
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self, f, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)
        else:
            raise Exception('filename is None')
