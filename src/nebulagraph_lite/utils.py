import random
import time
import functools
import psutil

from typing import List, Type


# Thanks to https://www.learnui.design/tools/data-color-picker.html
COLORS_hex = {
    # "dark_blue": "#003f5c",
    # "blue": "#2f4b7c",
    "purple": "#665191",
    "magenta": "#a05195",
    "pink": "#d45087",
    "red": "#f95d6a",
    "orange": "#ff7c43",
    "yellow": "#ffa600",
}

COLORS_rgb = {
    # "dark_blue": "38;2;0;63;92",
    # "blue": "38;2;47;75;124",
    "purple": "38;2;102;81;145",
    "magenta": "38;2;160;81;149",
    "pink": "38;2;212;80;135",
    "red": "38;2;249;93;106",
    "orange": "38;2;255;124;67",
    "yellow": "38;2;255;166;0",
}

BANNER_ASCII = r"""
  _   _      _           _        ____                 _     
 | \ | | ___| |__  _   _| | __ _ / ___|_ __ __ _ _ __ | |__  
 |  \| |/ _ | '_ \| | | | |/ _` | |  _| '__/ _` | '_ \| '_ \ 
 | |\  |  __| |_) | |_| | | (_| | |_| | | | (_| | |_) | | | |
 |_| \_|\___|_.__/ \__,_|_|\__,_|\____|_|  \__,_| .__/|_| |_|
                                                |_|          
                                                lite version
"""


def retry(
    exceptions: List[Type[Exception]],
    tries: int = 4,
    delay: int = 1,
    backoff: int = 2,
) -> None:
    """
    A decorator for retrying a function with an exponential backoff.

    Parameters:
    exceptions: A tuple of exception types to catch and retry.
    tries: Maximum number of attempts. Default is 4.
    delay: Initial delay between retries in seconds. Default is 1 second.
    backoff: Backoff multiplier. Default is 2.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal tries, delay
            while tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Retrying in {delay} seconds...", e)
                    time.sleep(delay)
                    tries -= 1
                    delay *= backoff
            return func(*args, **kwargs)  # Last attempt without catching exceptions

        return wrapper

    return decorator


def fancy_print(text: str, color: str = "Blue") -> None:
    """
    Print a string in color from COLORS_rgb.
    """
    if color not in COLORS_rgb:
        # random color
        color = COLORS_rgb[
            list(COLORS_rgb.keys())[random.randint(0, len(COLORS_rgb) - 1)]
        ]
    else:
        color = COLORS_rgb[color]
    print(f"\033[1;3;{color}m{text}\033[0m")


def fancy_dict_print(d: dict, color: str = None) -> None:
    """
    Print a dict in color from COLORS_rgb.
    """
    color_keys = list(COLORS_rgb.keys())
    for i, (key, value) in enumerate(d.items()):
        if color is None or color not in COLORS_rgb:
            color = COLORS_rgb[color_keys[i % len(color_keys)]]
        else:
            color = COLORS_rgb[color]
        print(f"\033[1;3;{color}m{key}: {value}\033[0m")


def get_pid_by_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == "LISTEN":
            return conn.pid
    return None


def kill_process_by_pid(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Process with PID {pid} has been terminated.")
    except psutil.NoSuchProcess:
        print(f"No process with PID {pid} exists.")


@retry((Exception,), tries=3, delay=5, backoff=3)
def process_listening_on_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == "LISTEN":
            return True
    return False
