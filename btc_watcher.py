#!/usr/bin/env python3

import time
from datetime import datetime

import requests
import beepy
import configparser
import curses
import random

import sender
import debug

# BITCOIN_API_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'
BITCOIN_API_URL = 'https://api.pro.coinbase.com/products/BTC-USD/stats'

# Get Configuration
config = configparser.ConfigParser()
config.read("config.txt")

BITCOIN_PRICE_LOW_THRESHOLD = int(config.get('tracker', 'BITCOIN_PRICE_LOW_THRESHOLD'))
BITCOIN_PRICE_HIGH_THRESHOLD = int(config.get('tracker', 'BITCOIN_PRICE_HIGH_THRESHOLD'))
TIMER_SECONDS = eval(config.get('system', 'TIMER_SECONDS'))
SOUND = int(config.get('system', 'SOUND'))
last_price = BITCOIN_PRICE_LOW_THRESHOLD


def get_latest_bitcoin_price():
    global last_price
    bold = ""
    price = 0
    str_price = ""
    result_dict = dict()

    try:
        response = requests.get(BITCOIN_API_URL)
        response_json = response.json()

        price = response_json["last"]
        price = price.split(".")[0]

        open_price = response_json["open"]
        open_price = open_price.split(".")[0]
        result_dict["open_price"] = open_price

        high_price = response_json["high"]
        high_price = high_price.split(".")[0]
        result_dict["high_price"] = high_price

        low_price = response_json["low"]
        low_price = low_price.split(".")[0]
        result_dict["low_price"] = low_price

        volume = response_json["volume"]
        volume = volume.split(".")[0]
        result_dict["volume"] = volume

        str_price = format(int(price), ',d')
        result_dict["str_price"] = str_price

        price = price.translate({ord(i): None for i in ','})
        price = int(price)

        result_dict["price"] = price

    except Exception as e:
        debug.output_error(e)

    if price > 0:
        diff = abs(price - last_price)

        if last_price > price:
            sign = "-"
        else:
            sign = "+"

        result_dict["sign"] = sign
        result_dict["diff"] = format(int(diff), ',d')

        date = datetime.utcnow()
        result_dict["date"] = date.strftime('%H:%M')

        last_price = price

        output_str = bold + str_price + " ( " + sign + " " + str(diff) + "\t)"
        # print(output_str)
        debug.output_debug(output_str)

    return result_dict


def print_price(stdscr, line_num, dict_price):
    sign = dict_price["sign"]
    price = dict_price["price"]
    str_price = dict_price["str_price"]
    diff = dict_price["diff"]

    if price < BITCOIN_PRICE_LOW_THRESHOLD:
        stdscr.attron(curses.color_pair(5))
        stdscr.attron(curses.A_BOLD)


    if price > BITCOIN_PRICE_HIGH_THRESHOLD:
        stdscr.attron(curses.color_pair(4))
        stdscr.attron(curses.A_BOLD)

    stdscr.addstr(line_num, 1, str_price)

    stdscr.attroff(curses.color_pair(4))
    stdscr.attroff(curses.color_pair(5))
    stdscr.attroff(curses.A_BOLD)

    stdscr.addstr(line_num, 8, "(")

    if sign == "+":
        stdscr.attron(curses.color_pair(4))
    elif sign == "-":
        stdscr.attron(curses.color_pair(5))

    stdscr.addstr(line_num, 10, sign)

    stdscr.attroff(curses.color_pair(4))
    stdscr.attroff(curses.color_pair(5))

    stdscr.addstr(line_num, 12, diff)
    stdscr.addstr(line_num, 17, ")")


def print_stats(stdscr, line_num, label, stat):
    stat = format(int(stat), ',d')

    stdscr.attron(curses.color_pair(6))
    stdscr.addstr(line_num, 25, label)
    stdscr.attroff(curses.color_pair(6))
    stdscr.addstr(line_num + 1, 27, stat)


def draw_menu(stdscr):
    k = 0
    price = 0

    bitcoin_history = []

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)

    while True:

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        #       BTC HERE

        dict_price = get_latest_bitcoin_price()

        if "price" in dict_price.keys():

            bitcoin_history.append(dict_price)

            price = dict_price["price"]
            sign = dict_price["sign"]
            str_price = dict_price["str_price"]
            diff = dict_price["diff"]

        else:
            dict_price = bitcoin_history[len(bitcoin_history) - 1]

        bitcoin_history_length = len(bitcoin_history)

        if bitcoin_history_length > height - 3:
            bitcoin_history_pos = bitcoin_history_length - height + 3
        else:
            bitcoin_history_pos = 0

        #        stdscr.addstr(1, 20, str(len(bitcoin_history)))
        #        stdscr.addstr(1, 25, str(bitcoin_history_pos))

        for i in range(height - 3):
            str_pos = i + 1

            if i < bitcoin_history_length:
                print_price(stdscr, str_pos, bitcoin_history[bitcoin_history_pos])

            bitcoin_history_pos += 1

        if price < BITCOIN_PRICE_LOW_THRESHOLD:
            if SOUND:
                beepy.beep(sound=1)
            sender.send_email(str_price)

        if price > BITCOIN_PRICE_HIGH_THRESHOLD:
            if SOUND:
                beepy.beep(sound=1)
            sender.send_email(str_price)

        start_pos = int((height - 8) / 2)
        print_stats(stdscr, start_pos, "Open Price", dict_price["open_price"])
        print_stats(stdscr, start_pos + 2, "Low Price", dict_price["low_price"])
        print_stats(stdscr, start_pos + 4, "High Price", dict_price["high_price"])
        print_stats(stdscr, start_pos + 6, "Volume", dict_price["volume"])

        # Render status bar
        statusbarstr = " " + str(dict_price["date"])
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height - 1, 0, " " * (width - 1))
        stdscr.addstr(height - 1, int((width / 2) - 3), statusbarstr)
        #        stdscr.addstr(height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        stdscr.move(height - 1, width - 1)
        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        # k = stdscr.getch()
        if price > 0:
            time.sleep(TIMER_SECONDS)
        else:
            time.sleep(30)


def main():
    curses.wrapper(draw_menu)


if __name__ == "__main__":
    main()

# TODO Test
