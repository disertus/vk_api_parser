import parsers.comments_parser as comments_parser
import os


def parse_json_post_response(post_item, community_id, full_response):
    temp_dict = {}
    temp_dict["owner_id"] = abs(community_id)
    temp_dict["post_id"] = post_item["id"]
    temp_dict["publication_timestamp"] = post_item["date"]
    temp_dict["post_text"] = post_item["text"]
    try:
        temp_dict["attachment_type"] = post_item["attachments"][0]["type"]
    except KeyError:
        temp_dict["attachment_type"] = None
    temp_dict["comments_count"] = post_item["comments"]["count"]
    temp_dict["likes_count"] = post_item["likes"]["count"]
    temp_dict["views_count"] = post_item["views"]["count"]
    comments_parser.append_dict_contents(
        temp_dict, f"{os.getcwd()}/parsed_posts_info/{abs(community_id)}.txt"
    )
