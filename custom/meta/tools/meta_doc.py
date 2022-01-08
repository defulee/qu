#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import argparse
import os
import sys

import pymysql
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from custom.meta.lib.model_doc import persist_model_meta
from custom.meta.lib.dict_doc import persist_dict_meta


def get_config_file():
    parser = argparse.ArgumentParser()
    parser.description = '参数解析'
    parser.add_argument('-c', '--config_file', required=True, help='配置文件')
    args = parser.parse_args()
    return args.config_file


def get_config_data(yaml_file):
    # 打开yaml文件
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()

    # 将字符串转化为字典或列表
    return yaml.full_load(file_data)


if __name__ == "__main__":
    # 获取配置
    config_file = get_config_file()
    # config_file = "/Users/defu/dev/github/defulee/toolbox/custom/meta/lib/config.yml"
    config_data = get_config_data(config_file)
    print(config_data)

    # 连接数据库
    mysql_password = input("请输入MYSQL_PASSWORD: ")
    db = pymysql.connect(host=config_data["mysql"]["mysql_host"], port=config_data["mysql"]["mysql_port"],
                         db=config_data["mysql"]["mysql_database"], user=config_data["mysql"]["mysql_username"],
                         password=mysql_password)
    db.autocommit(True)
    cursor = db.cursor()

    # 打开文件
    fo = open(os.getcwd() + "/meta_doc.md", "w")

    # 持久化模型原信息
    all_dict_list = []
    if len(config_data["models"]) > 0:
        fo.write("## 模型信息\n\n")
        for model in config_data["models"]:
            field_desc = None
            if model["name"] in config_data["model_field_desc"]:
                field_desc = config_data["model_field_desc"][model["name"]]
            dict_list = persist_model_meta(cursor, model, field_desc, fo)
            all_dict_list.extend(dict_list)

    # 持久化字典原信息
    if len(all_dict_list) > 0:
        fo.write("## 字典信息\n\n")
        for dict_key in all_dict_list:
            persist_dict_meta(cursor, dict_key, fo)

    # 文档生成完成
    print("文档已生成，地址：", os.getcwd() + "/meta_doc.md")
    # 关闭数据库 & 文件连接
    cursor.close()
    db.close()
    fo.close()
