import parsers.comments_parser as comments_parser
import parsers.posts_parser as posts_parser

import json
import logging
import os
import re
import time
from tqdm import tqdm

import requests


logging.basicConfig(
    filename="Logs.log", format="%(asctime)s %(message)s", level=logging.WARNING
)


def create_working_folders():
    try:
        os.system("mkdir parsed_comments")
        os.system("mkdir parsed_posts_info")
    except Exception as e:
        logging.warning(f"Failed to create specified folders. Error message: {e}")
        pass


def get_request_response(url):
    attempts = 0
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error")
            logging.error(
                f"Encountered an error while sending a request, ending the process. Status code {response.status_code}"
            )
    except Exception as e:
        print("ERROR: " + e)
        time.sleep(2)
        attempts += 1
        get_request_response(url)


def iterate_until_required_date(
    latest_post_timestamp: int, community_id: int, url: str, parser
):
    offset = 0
    reached_latest_timestamp = False
    while 1:
        offset_param = f"&offset={offset}"
        response = get_request_response(url + offset_param)
        try:
            for response_item in response["response"]["items"]:  # [1:]:
                if response_item["date"] >= latest_post_timestamp:
                    parser(response_item, community_id, response)
                elif response_item["date"] < latest_post_timestamp:
                    reached_latest_timestamp = True
                    break
            if reached_latest_timestamp:
                break
            if len(response["response"]["items"]) < 100:
                break
            offset += 100
            time.sleep(1)
        except Exception as e:
            print(f"An error occurred while parsing the response {response}: \n{e}")
            break


def extract_community_ids(filepath: str):
    owner_id_list = []
    with open(filepath, "r") as file:
        for line in file.readlines():
            # minus sign required since all community ids should be negative integers
            owner_id_list.append(-int(re.split("public", line)[-1]))
    return owner_id_list


def extract_item_ids(community_id: int, post_id: int):
    # if post_id equals 0, extract parsed post_ids. otherwise parse comment_ids
    if post_id == 0:
        temp_id_list = []
        with open(
            f"{os.getcwd()}/parsed_posts_info/{abs(community_id)}.txt", "r"
        ) as file:
            for line in file.readlines():
                temp_id_list.append(json.loads(line)["post_id"])
        return temp_id_list
    else:
        temp_id_dict = {}
        with open(
            f"{os.getcwd()}/parsed_comments/{abs(community_id)}.txt", "r"
        ) as file:
            for line in file.readlines():
                pass


# def extract_parsed_comment_ids(community_id: int, post_id: int):
#     temp_comment_dict = {}
#     with open(f"{os.getcwd()}/parsed_posts_info/{abs(community_id)}.txt", "r") as file:
#         for line in


if __name__ == "__main__":
    create_working_folders()
    base_url = "https://api.vk.com/"
    service_token = "TOKEN"
    api_version = 5.131
    before_war_time = 1645270728

    for owner_id in extract_community_ids(filepath="community_id_list.txt"):
        print(f"Parsing post data for https://vk.com/public{abs(owner_id)}")
        post_url = (
            base_url + f"method/wall.get?owner_id={owner_id}"
            f"&access_token={service_token}"
            f"&v={api_version}&count=100"
        )
        iterate_until_required_date(
            before_war_time,
            abs(owner_id),
            post_url,
            posts_parser.parse_json_post_response,
        )

        print(f"Extracting comments: ")
        for post_id in tqdm(extract_item_ids(owner_id, post_id=0)):
            comment_url = (
                base_url + f"method/wall.getComments?owner_id={owner_id}"
                f"&access_token={service_token}"
                f"&v={api_version}&count=100"
                f"&post_id={post_id}&sort=desc&extended=1"
                f"&fields=sex,bdate,country,city,contacts"
                f"&thread_items_count=10"
            )
            iterate_until_required_date(
                before_war_time,
                abs(owner_id),
                comment_url,
                comments_parser.parse_json_comment_response,
            )
