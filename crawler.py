import argparse
import logging
import os
import queue
import time
from functools import lru_cache

import bs4
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

TARGET_URL = "https://example.com"
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(format="%(process)d-%(levelname)s-%(message)s", level=logging.INFO)


def session():
    s = requests.session()
    retry_strategy = Retry(
        total=2,
        connect=2,
        status_forcelist=None,
        allowed_methods=False,
        backoff_factor=1,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    s.mount("http://", adapter)
    return s


def arguments():
    parser = argparse.ArgumentParser(
        description="This is crawler CLI utilite",
        prog="python crawler.py --target-url=https://example.com",
        add_help=False
    )

    parser.add_argument("--target-url", dest="url", default=TARGET_URL, type=str)
    parser.add_argument("-h", "--help", "-help", action="help", help="Help message")

    return parser.parse_args()


@lru_cache(maxsize=128)
def get_links(url: str) -> set:
    logging.info(f"Request for URL={url}")
    time.sleep(0.1)
    r = session().get(url, timeout=5)
    if r.ok:
        soup = bs4.BeautifulSoup(r.text, "lxml")
        link_list = [elem["href"] for elem in soup.find_all("a", href=True)]
        return set(link_list)
    else:
        logging.warning(f"Request on URL={url} has status={r.status_code}")


def save_to_txt(input_set: set):
    report_path = f"{CURRENT_PATH}/report"
    if not os.path.exists(report_path):
        os.makedirs(report_path)
    with open(f"{report_path}/report.txt", "w") as f:
        for elem in input_set:
            f.write(str(elem) + "\n")


def bypass_links():
    url = q.get()
    result_set.add(url)
    link_list = get_links(url)
    for link in link_list:
        if (
            link.startswith("/")
            and f"{args.url}{link}" not in q.queue
            and f"{args.url}{link}" not in result_set
        ):
            q.put(f"{args.url}{link}")
        elif (
            link.startswith(args.url)
            and link != f"{args.url}/"
            and link not in q.queue
            and link not in result_set
        ):
            q.put(link)


if __name__ == "__main__":
    q = queue.Queue()
    result_set = set()
    args = arguments()
    q.put(args.url)
    while not q.empty():
        bypass_links()
        logging.info(f"In queue {len(q.queue)} links, pass {len(result_set)}")
    save_to_txt(result_set)
    logging.info(f"Bypass queue finished, overall {len(result_set)} links")
