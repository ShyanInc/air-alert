import requests
import time

from enum import Enum
from fake_useragent import UserAgent

link = "https://vadimklimenko.com/map/statuses.json?t="
header = {
    "User-Agent": UserAgent().random
}


class Alert(Enum):
    ALERT = True
    NO_ALERT = False


async def get_status():
    current_time = str(round(time.time_ns() / 1000000))

    response = requests.get(link + current_time, headers=header)
    json = response.json()

    regions = json["states"]

    region = regions["Житомирська область"]
    # region = regions["Житомирська область"]
    region_name = "Житомирська область"
    # region_name = "Житомирська область"
    region_alert = region["enabled"]

    if region_alert:
        return "Alert"
    elif not region_alert:
        return "No_Alert"

