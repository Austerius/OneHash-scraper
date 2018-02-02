"""
Scrapy spider for scraping dynamically generated esport betting information from web site *www.onehash.com*

This script was created for educational purposes to demonstrate how to scrape data from dynamically
generated web page using *Scrapy* and *Selenium webdriver*. Also, here you can find examples of
scrapy "Item" and "ItemLoader", as well as "How to use xpath selectors in scrapy" and "How to scroll
dynamically loading web page block with Selenium"

This script was written in Python 3.6(for scrapy 1.5), and before running it, you'll need to install:
- Scrapy (on Windows machine you'll need appropriate C++ SDK to run Twisted - check their docs);
- Selenium (with geckodriver for Windows machines);
- Firefox browser.
After installing all requirements - create Scrapy project and put this script into "spiders" folder.

"onehash.py" spider scrape information about esport events that not yet been played(or in progress).
What kind of data this script will scrape shows below(names in ' ' also are keys for Item container):
- 'date'  - date of the single event/game in timedate format converted to UTC time(or tried to);
- 'game' - name of the game(csgo, overwatch, dota2 etc);
- 'player1' - name of the first participant(or team name, like: "Misfits" or "SK Gaming" etc);
- 'player2' - name of the second participant;
- 'odds1' - bet rate on the first player(float value, like: 1.345);
- 'odds2' - bet rate on the second player(float value).

Now, for convenient purpose this script needs that :var:TIME_DIFFERENCE been set inside script to your own value.
- TIME_DIFFERENCE - represent a difference between time for event, that shows on website
                    and UTC time(check in script comments). You can set it to "0", and then all dates for events,
                    which starts 24+ hours from current time will be saved in site_time format(not UTC).
Also, if script working to slowly or scraped information not full - you can try to adjust :param:sleep_time
and :param:loop_timer inside of method "parse" of OneHash class.

To run a spider - change your location in terminal to scrapy project folder and type: scrapy crawl onehash
To save data to .json file(for example), type: scrapy crawl onehash -o yourfile.json
"""

import time
import datetime

import scrapy
from scrapy import Selector
from scrapy.loader.processors import MapCompose, Join
from scrapy.loader import ItemLoader

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# script author - Alexander Shums'kii
# https://github.com/Austerius

# put your time difference between time, that shows on site and current_utc time(use sight).
# Tip: use others esport betting site for reference (EGB.com shows events date in GMT +0). For example:
# If onehash show event start in 20min from now(your time 12:40), and on EGB this event will start at 11:00
# TIME_DIFFERENCE = (12:40 + 00:20) - 11:00 = +2 (yeh, it's work in most cases)
TIME_DIFFERENCE = +2


def get_name(name_string):
    """
    Function for getting name of the game from class name string.
    Incoming string looks like: "icon-oh cat-overwatch"
    """
    name_string = name_string.split(" ")[1]
    name_string = name_string.split("-")[1]
    return name_string


def get_odd(odd_string):
    """Function for converting odds string to a correct float value."""
    odd_string = odd_string[1:]  # firs element is char 'x' - getting rid of it
    return float(odd_string)


class Event(scrapy.Item):
    """
        Class-container for scraped data.
        Usually you put this class in separate file(but for the convenience of "one-file-example" I put it here).
    """
    game = scrapy.Field(input_processor=MapCompose(get_name))
    player1 = scrapy.Field()
    player2 = scrapy.Field()
    # So, our odds placed in several span selectors(one char of odd per 'span')
    # That's why we using 'Join' processor fist, to get all chars and form a string from em(with no separator)
    odds1 = scrapy.Field(input_processor=Join(''), output_processor=MapCompose(get_odd))
    odds2 = scrapy.Field(input_processor=Join(''), output_processor=MapCompose(get_odd))
    date = scrapy.Field()


class OneHash(scrapy.Spider):

    name = "onehash"
    allowed_domains = ['www.onehash.com']
    start_urls = ["https://www.onehash.com/category/e_sport/"]

    def __init__(self):
        self.driver = webdriver.Firefox()
        super().__init__()

    def __del__(self):
        self.driver.close()

    def parse(self, response):
        """ parsing page.
            Edit *sleep_time* and *loop_timer* before running.
            Elso, don't forgot about :var:TIME_DIFFERENCE variable.
        """
        self.driver.get(response.url)
        self.driver.maximize_window()
        sleep_time = 3  # sleep time for completely load web page(increase/decrease if needed)
        loop_timer = 10  # Timer for scrolling down to the bottom of the content(edit for your own value if needed)
        time.sleep(sleep_time)  # loading initial page
        parsed_data = Event()  # container for parsed data

        # Scrolling to the end of results/bets page
        event_box = self.driver.find_element_by_xpath('//body//main')
        try:
            event_box.click()  # needed emulate click on the element to proceed
        except:
            pass
        timer = time.time() + loop_timer
        while True:
            ActionChains(self.driver).move_to_element(event_box).send_keys(Keys.END).perform()
            if time.time() > timer:
                break

        # getting outer html:
        source = Selector(text=self.driver.page_source)

        # here we can find all juicy information about single event
        events = source.xpath('//div[@class="eventbox-container"]')

        # processing/parsing game information here
        for event in events:
            il = ItemLoader(selector=event, item=parsed_data)
            # time-date block(we will count our time in UTC and transform site time to UTC)
            current_time_utc = datetime.datetime.utcnow()
            # getting class name of first div block in "time-wrapper" block
            time_block = event.xpath('.//div[@class="time-wrapper"]/div/@class').extract_first()
            # site has 2 different time formats: actual datetime and timer to event start(like: 2h 43m)
            if time_block == 'time-left':  # if we get a timer
                time_string = event.xpath('.//div[@class="time-wrapper"]/div[@class="time-left"]/span[2]/text()').extract_first()
                try:
                    # time_string format: "2h 32m" or "34m 39s" or "12s"
                    first, second = time_string.split(' ')  # getting minutes(seconds) and hours _strings
                    hours = 0
                    minutes = 0
                    seconds = 0
                    if first[-1] == 'h':  # if we still have hour or few to the start of the event
                        hours = int(first[:-1])  # getting rid of letter(h or m) at the end of string
                        minutes = int(second[:-1])
                    elif first[-1] == 'm':
                        minutes = int(first[:-1])
                        seconds = int(second[:-1])
                    delta_time = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
                except ValueError:
                    delta_time = current_time_utc  # seconds left until event start

                # so, to get actual date in utc we'll need to add delta_time to current utc time
                game_date_utc = current_time_utc + delta_time
            elif time_block == 'datetime':  # ok, now actual fun: (( not really ((
                date_string = event.xpath('.//div[@class="time-wrapper"]/div[@class="datetime"]/span[@class="date"]/text()').extract_first()
                time_string = event.xpath('.//div[@class="time-wrapper"]/div[@class="datetime"]/span[@class="time"]/text()').extract_first()
                day, month, year = date_string.split('/')
                hour, minute = time_string.split(":")
                # now, it's most easiest and maybe worst method: you actually need to go to web site and figure out
                # a difference between current utc and site time(for me it was +2h - check TIME_DIFFERENCE variable)
                site_date = datetime.datetime(year=int(year), month=int(month), day=int(day),
                                              hour=int(hour), minute=int(minute))
                delta_time = datetime.timedelta(minutes=TIME_DIFFERENCE*60)
                game_date_utc = site_date - delta_time
            # we don't want to scrap events that already ended(or in progress):
            if current_time_utc > game_date_utc:
                continue

            # don't miss a '.' at the beginning of the selector, so we will parse only current event block
            il.add_xpath('game', './/div[@class="item"]/i/@class')
            il.add_value('date', game_date_utc)
            il.add_xpath('player1', './/section[@class="team"][1]//div[@class="eventbox-title text-ellipsis"]/text()')
            il.add_xpath('player2', './/section[@class="team"][2]//div[@class="eventbox-title text-ellipsis"]/text()')
            # this selector will get text field from multiple 'span', than, we will use Join processor(check our Item)
            il.add_xpath('odds1', './/section[@class="team"][1]//div[@class="multi-number-roller"]//span/text()')
            il.add_xpath('odds2', './/section[@class="team"][2]//div[@class="multi-number-roller"]//span/text()')
            il.load_item()
            yield parsed_data
