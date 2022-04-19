import json
import os


def append_dict_contents(dict, path):
    with open(path, "a+") as file:
        json.dump(dict, file)
        file.write("\n")


def parse_json_comment_response(comment_item, community_id, full_response):
    temp_dict = {}
    temp_dict["owner_id"] = community_id
    try:
        temp_dict["post_id"] = comment_item["post_id"]
    except KeyError:
        temp_dict["post_id"] = None
    temp_dict["comment_id"] = comment_item["id"]
    temp_dict["author_id"] = comment_item["from_id"]
    temp_dict["publication_timestamp"] = comment_item["date"]
    temp_dict["comment_text"] = comment_item["text"]
    try:
        temp_dict["attachment_type"] = comment_item["attachments"][0]["type"]
    except KeyError:
        temp_dict["attachment_type"] = None
    try:
        temp_dict["likes_count"] = comment_item["likes"]["count"]
        temp_dict["can_like"] = comment_item["likes"]["can_like"]
    except KeyError:
        temp_dict["likes_count"] = 0
        temp_dict["can_like"] = 0
    temp_dict["reply_relations"] = comment_item["parents_stack"]
    try:
        temp_dict["replies_count"] = comment_item["thread"]["count"]
        temp_dict["can_reply"] = comment_item["thread"]["can_post"]
        if temp_dict["replies_count"] > 0:
            for reply in comment_item["thread"]["items"]:
                parse_json_comment_response(reply, community_id, full_response)
    except KeyError:
        temp_dict["replies_count"] = 0
        temp_dict["can_reply"] = 0
    for profile in full_response["response"]["profiles"]:
        if profile["id"] == temp_dict["author_id"]:
            temp_dict["author_first_name"] = profile["first_name"]
            temp_dict["author_last_name"] = profile["last_name"]
            # author_sex value: 1 = woman, 2 = man, 0 = unknown
            temp_dict["author_sex"] = profile["sex"]
            try:
                temp_dict["author_birth_date"] = profile["bdate"]
            except KeyError:
                temp_dict["author_birth_date"] = None
            try:
                temp_dict["author_country"] = profile["country"]
            except KeyError:
                temp_dict["author_country"] = None
            try:
                temp_dict["author_city"] = profile["city"]
            except KeyError:
                temp_dict["author_city"] = None
    append_dict_contents(
        temp_dict, f"{os.getcwd()}/parsed_comments/{abs(community_id)}.txt"
    )
