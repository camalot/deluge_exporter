import datetime
import json
import math
import random
import re
import string
import typing

import requests


def dict_get(dictionary, key, default_value=None) -> typing.Any:
    if key in dictionary.keys():
        return dictionary[key] or default_value
    else:
        return default_value


def get_scalar_result(conn, sql, default_value=None, *args) -> typing.Any:
    cursor = conn.cursor()
    try:
        cursor.execute(sql, args)
        return cursor.fetchone()[0]
    except Exception as ex:
        return default_value


def str2bool(v) -> bool:
    return v.lower() in ("yes", "true", "yup", "1", "t", "y", "on")


def chunk_list(lst, size):
    # looping till length l
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def get_random_string(length: int = 10) -> str:
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def get_random_name(noun_count=1, adjective_count=1) -> str:
    fallback_nouns = [
        "Aardvark",
        "Albatross",
        "Alligator",
        "Alpaca",
    ]
    fallback_adjectives = [
        "Able",
        "Acidic",
        "Adorable",
        "Aggressive",
    ]
    try:
        adjectives = load_from_gist("adjectives", adjective_count)
        nouns = load_from_gist("nouns", noun_count)
        results = adjectives + nouns
        return " ".join(w.title() for w in results)
    except Exception as ex:
        try:
            nouns = requests.get(f"https://random-word-form.herokuapp.com/random/noun?count={str(noun_count)}").json()
            adjectives = requests.get(
                f"https://random-word-form.herokuapp.com/random/adjective?count={str(adjective_count)}"
            ).json()
            results = adjectives + nouns
            return " ".join(w.title() for w in results)
        except Exception as ex:
            try:
                results = requests.get(
                    f"https://random-word-api.herokuapp.com/word?number={str(noun_count + adjective_count)}&swear=0"
                ).json()
                return " ".join(w.title() for w in results)
            except Exception as ex:
                return " ".join(
                    random.sample(fallback_adjectives, adjective_count) + random.sample(fallback_nouns, noun_count)
                )

def to_timestamp(date, tz: typing.Optional[datetime.timezone] = None) -> float:
    date = date.replace(tzinfo=tz)
    return (date - datetime.datetime(1970, 1, 1, tzinfo=tz)).total_seconds()


def from_timestamp(timestamp: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


def get_timestamp() -> float:
    return to_timestamp(datetime.datetime.utcnow())


def load_from_gist(type, count) -> typing.List[str]:
    types = [ "adjectives", "nouns", "verbs" ]
    if type not in types:
        type = "nouns"
    if count <= 0:
        count = 1
    elif count > 10:
        count = 10
    data = requests.get(f"https://gist.githubusercontent.com/camalot/8d2af3796ac86083e873995eab98190d/raw/b39de3a6ba03205380caf5d58e0cae8a869ac36d/{type}.js").text
    data = re.sub(r"(var\s(adjectives|nouns|verbs)\s=\s)|;$","", data)
    jdata = json.loads(data)
    return random.sample(jdata, count)


def get_args_dict(func, args, kwargs) -> dict:
    args_names = func.__code__.co_varnames[:func.__code__.co_argcount]
    return {**dict(zip(args_names, args)), **kwargs}


def str_replace(input_string: str, *args, **kwargs) -> str:
    xargs = get_args_dict(str_replace, args, kwargs)
    result = input_string
    for a in xargs:
        result = result.replace(f"{{{{{a}}}}}", str(kwargs[a]))
    return result

def get_last_section_in_url(name) -> str:
    if "/" in name:
        # if the name has a slash in it, then it is a url. Remove everything before and including the slash
        name_split = name.rsplit("/", 1)
        if len(name_split) > 1:
            name = name_split[1]
    return name

def convert_size_to_bytes(size: str) -> float:
    size = size.upper().replace(",", "").replace(" ", "")
    if size.endswith("KB"):
        return float(size[:-2]) * 1024
    if size.endswith("MB"):
        return float(size[:-2]) * 1024 ** 2
    if size.endswith("GB"):
        return float(size[:-2]) * 1024 ** 3
    if size.endswith("TB"):
        return float(size[:-2]) * 1024 ** 4
    if size.endswith("PB"):
        return float(size[:-2]) * 1024 ** 5
    if size.endswith("EB"):
        return float(size[:-2]) * 1024 ** 6
    if size.endswith("ZB"):
        return float(size[:-2]) * 1024 ** 7
    if size.endswith("YB"):
        return float(size[:-2]) * 1024 ** 8
    return float(size)

def convert_size_to_string(size_bytes) -> str:
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
