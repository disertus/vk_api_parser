import parsers.comments_parser as comments_parser
import parsers.posts_parser as posts_parser

import argparse
import datetime
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
    """Create folders where the files containing parsed data will be stored"""
    try:
        os.system("mkdir parsed_comments")
        os.system("mkdir parsed_posts_info")
    except Exception as e:
        logging.warning(f"Failed to create specified folders. Error message: {e}")
        pass


def get_request_response(url):
    """Send a get request and return its response if the request was successful. Retry upon failure."""
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
        print(f"ERROR: {e}")
        logging.error(e)
        time.sleep(2)
        get_request_response(url)


def iterate_until_required_date(latest_post_timestamp: int, community_id: int, url: str, parser, delay):
    """Repeatedly sends get requests to the API while incrementing the offset by 100 in order to reach the next
    batch of items. Interrupts once the list of items is exhausted."""
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
            time.sleep(delay)
        except Exception as e:
            print(f"An error occurred while parsing the response {response}: \n{e}")
            break


def extract_community_ids(filepath: str):
    """Get community ids from the file, extract the integers following the prefix"""
    owner_id_list = []
    with open(filepath, "r") as file:
        for line in file.readlines():
            # minus sign required since all community ids should be negative integers
            owner_id_list.append(-int(re.split("public", line)[-1]))
    return owner_id_list


def extract_item_ids(community_id: int, item_id: int):
    """Get post ids or comment ids depending on the context.
    If post_id equals 0, extract parsed post_ids. Otherwise parse comment_ids"""
    if item_id == 0:
        temp_id_list = []
        with open(
            f"{os.getcwd()}/parsed_posts_info/{abs(community_id)}.txt", "r"
        ) as file:
            for line in file.readlines():
                temp_id_list.append(json.loads(line)["post_id"])
        return temp_id_list
    else:
        pass
        # temp_id_dict = {}
        # with open(
        #     f"{os.getcwd()}/parsed_comments/{abs(community_id)}.txt", "r"
        # ) as file:
        #     for line in file.readlines():
        #         pass


def parse_arguments():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-dt", "--date",
                           help='''Date in "YYYY-MM-DD" format.
                           The parser will get all available posts and their comments from VK API starting from now 
                           and till this date. The default value is "2022-02-19".''',
                           type=str,
                           default="2022-02-19")
    argparser.add_argument("-t", "--token",
                           help="The token required to access VK API.",
                           type=str)
    argparser.add_argument("-dl", "--delay",
                           help='''Delay between requests in seconds. 
                           The lower the delay the lower are the chances of
                           getting an error for exceeding the rps limit. The default value is 1''',
                           type=float,
                           default=1)
    return argparser.parse_args()


def date_string_to_timestamp(date_string: str):
    return round(time.mktime(datetime.datetime.strptime(date_string, "%Y-%m-%d").timetuple()))


# def extract_parsed_comment_ids(community_id: int, post_id: int):
#     temp_comment_dict = {}
#     with open(f"{os.getcwd()}/parsed_posts_info/{abs(community_id)}.txt", "r") as file:
#         for line in


if __name__ == "__main__":
    create_working_folders()
    flags = parse_arguments()

    base_url = "https://api.vk.com/"
    api_version = 5.131
    end_date = date_string_to_timestamp(flags.date)
    print(f"End date argument: {flags.date}")
    if not flags.token:
        print("Please provide a token to access the API. Check the README.md file for more details.")
        exit()

    for owner_id in extract_community_ids(filepath="community_id_list.txt"):
        print(f"Parsing post data for https://vk.com/public{abs(owner_id)}")
        post_url = (
            base_url + f"method/wall.get?owner_id={owner_id}"
            f"&access_token={flags.token}"
            f"&v={api_version}&count=100"
        )
        iterate_until_required_date(
            end_date,
            abs(owner_id),
            post_url,
            posts_parser.parse_json_post_response,
            flags.delay
        )

        print(f"Extracting comments: ")
        for post_id in tqdm(extract_item_ids(owner_id, item_id=0)):
            comment_url = (
                base_url + f"method/wall.getComments?owner_id={owner_id}"
                f"&access_token={flags.token}"
                f"&v={api_version}&count=100"
                f"&post_id={post_id}&sort=desc&extended=1"
                f"&fields=sex,bdate,country,city,contacts"
                f"&thread_items_count=10"
            )
            iterate_until_required_date(
                end_date,
                abs(owner_id),
                comment_url,
                comments_parser.parse_json_comment_response,
                flags.delay
            )
