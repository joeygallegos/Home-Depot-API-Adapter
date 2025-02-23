#!/usr/bin/env python3
import pprint
import requests
import json
import re
from datetime import datetime
from re import sub
from decimal import Decimal
from collections import defaultdict

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"

item_links = [
    "https://www.homedepot.com/p/Deckmate-2-in-Green-Exterior-Self-Starting-Star-Flat-Head-Wood-Deck-Screws-8-1-lb-126-Pieces-2DMG1/305418731",
    "https://www.homedepot.com/p/Nexgrill-29-in-Barrel-Charcoal-Grill-Smoker-in-Black-810-0029/306148311",
    "https://www.homedepot.com/p/Everbilt-3-4-in-FHT-x-3-4-in-FIP-Brass-Adapter-Fitting-801659/300096153",
    "https://www.homedepot.com/p/Milwaukee-M12-12V-Lithium-Ion-Cordless-Drill-Driver-Impact-Driver-Combo-Kit-w-Two-1-5Ah-Batteries-Charger-Tool-Bag-2-Tool-2494-22/203111686",
]

stores = [534, 618, 6561]
API_URL = "https://apionline.homedepot.com/federation-gateway/graphql?opname=productClientOnlyProduct"


class bot:
    session = None


def setup(obj):
    obj.session = requests.Session()
    obj.session.cookies.update({})
    obj.session.headers.update({})
    return obj


print("Setting up worker bot")
worker = setup(bot())


def get_graphql_query():
    ql_query = None
    with open("query.dat", "r") as file:
        # read without newline character
        ql_query = file.read().splitlines(False)

    # return single string instead of a list<str>
    ql_query = "".join([str(line) for line in ql_query])
    return ql_query


# using graph query and JSON payload, make POST to hydration API to get the data for an item
def get_item_payload(
    store=0, item=00000, zipcode=00000, write_request=False, write_response=False
):
    query = get_graphql_query()
    if query == None or query == "":
        print("ERROR: Query not present. Cannot continue.")

    payload = json.dumps(
        {
            "operationName": "productClientOnlyProduct",
            "variables": {
                "isBrandPricingPolicyCompliant": True,
                "skipSpecificationGroup": False,
                "skipSubscribeAndSave": False,
                "skipKPF": False,
                "skipPaintDetails": True,
                "itemId": item,
                "storeId": store,
                "zipcode": zipcode,
            },
            "query": str(query),
        }
    )

    # TODO: Extract the _abck cookie
    # Looks like content split with a ~
    # If any part of this changes, the whole request is rejected
    headers = {
        "authority": "apionline.homedepot.com",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://www.homedepot.com",
        "pragma": "no-cache",
        "user-agent": user_agent,
        "x-experience-name": "general-merchandise",
        "accept-encoding": "gzip, deflate, br",
        "x-debug": "true",
        "cookie": "_abck=4782389E885CF9BA38B25AB02FEB7BF5~0~YAAQ0SXAF3zV8PyUAQAAZxMDMg3HHOvcIt4lyXrSP/u6aTP10AreCjolvkHWNt/IXlVW+O2PgXG3dA7rx4FaBCqC5hhI8Wda0HwUH0L0j9zle1/kQau2mttBeK77BjOUKA01KukprjJeRsFbhiWpaayRdibapYVZKU5zHGMTsNUEaBSbV2Peefpdn8yZf5eqNnqpazphOzxQV181HkVwrTFw8G3SvJKWuXG9Q4nDxJNeI8GbDxuHJcod9WDow/Y7Th1S560H8BzRPZQtoBi7fTN8FQN5YPhO8i0pjmBa6wJkOYdNm4ijHTX3Tr/+LQdE+9q9plapNwn6+v9pCe6sRifM/6NEJk/CMIyThRoeuNUMgidlvLYCYR1Cb4nWzKvsPrIdimZUwg5P7jS1fpIDdNa1JYiZrQT/ksxnEzVBjCQlFOdiNN0m7WJWRIZ0pQ6l5tybMw/zkTlJG0UPbEluygu+KYIU6YeUdkBUF61tLW1xzV3IQhwNUX1rTVKigZ1nNFlrRWic9e2+XeuZTWldPr5LUpiE7nCjemAyqKNMqX1qNQ1cIeQyERtGlvG9sxLTR853ShMztM/ZcZ+k09tXMLMpLZcWaboshnCDuEkDOq1FFgwX/Tp4XC/p1mTI5dqcgME17FdZFK5sLVKQhhRCGsnrK7rfuxhSh/TBNA==~-1~-1~-1;"
    }
    if write_request:
        nonce = str(int(datetime.now().timestamp()))
        with open(
            nonce + "_request.json",
            "a+",
            encoding="utf-8",
        ) as f:
            f.writelines(
                [str(payload), "=======================================", str(headers)]
            )
            f.close()

    # execute POST
    result = requests.post(
        API_URL,
        data=payload,
        headers=headers,
    )

    if write_response:
        nonce = str(int(datetime.now().timestamp()))
        with open(
            nonce + "_response.json",
            "a+",
            encoding="utf-8",
        ) as f:
            f.write(result.text)
            f.close()

    return json.loads(result.text)


# Get item price from payload data
def get_price(response_json):
    if response_json.get("data"):
        if response_json["data"].get("product"):
            if response_json["data"]["product"].get("pricing"):
                price = response_json["data"]["product"]["pricing"].get("value")
                if price is not None:
                    print(f"Price found: {price}")
                    return price
                else:
                    print("Pricing value is None.")
            else:
                print("No pricing data found.")
        else:
            print("No product data found.")
    else:
        print("No data section found.")
    return None



# get item name from payload
def get_name(response_json):
    if response_json.get("data"):
        if response_json.get("data").get("product"):
            name = (
                response_json.get("data")
                .get("product")
                .get("identifiers")
                .get("productLabel")
            )
            return name
    return None


# get item id from store link
def get_item_id_from_url(url):
    return int(re.search(r"(\d+)(/*)$", url).group(0))


def get_best_price_nearby_stores():
    item_price_dict = {}

    # Check links for best price
    for link in item_links:
        item_id = get_item_id_from_url(link)

        # If the item_id is not in the dictionary, add it with default values
        if item_id not in item_price_dict:
            item_price_dict[item_id] = {"best_price": None, "best_store": None}

        # Loop through each store
        for store_id in stores:
            payload = get_item_payload(store_id, item_id, 77449, True, True)
            current_store_price = get_price(payload)

            # If the best price is not set or the current store has a cheaper price
            if (
                item_price_dict[item_id]["best_price"] is None
                or item_price_dict[item_id]["best_price"] > current_store_price
            ):
                item_price_dict[item_id]["best_price"] = current_store_price
                item_price_dict[item_id]["best_store"] = store_id

    for item_id, item_data in item_price_dict.items():
        print(
            "Item {}".format(
                get_name(
                    get_item_payload(
                        item_data["best_store"], item_id, 77449, True, True
                    )
                )
            )
        )
        print(
            " - Store # {} - Price: ${}".format(
                item_data["best_store"], item_data["best_price"]
            )
        )


# examples
get_best_price_nearby_stores()
