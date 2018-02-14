# OneHash-scraper
<h3>onehash.py</h3>
Scrapy spider for scraping dynamically generated esport betting information from web site www.onehash.com

This script was created for educational purposes to demonstrate how to scrape data from dynamically
generated web page using **Scrapy** and **Selenium webdriver**. Also, here you can find examples of
scrapy *"Item"* and *"ItemLoader"*, as well as *"How to use xpath selectors in scrapy"* and *"How to scroll
dynamically loading web page block with Selenium"*

This script was written in Python 3.6(for scrapy 1.5), and before running it, you'll need to install:
- Scrapy (on Windows machine you'll need appropriate C++ SDK to run Twisted - check their docs);
- Selenium (with geckodriver for Windows machines);
- Firefox browser.
After installing all requirements - <b>create Scrapy project</b> and put this script into "spiders" folder.

"<i>onehash.py</i>" spider scrape information about esport events that not yet been played(or in progress).
What kind of data this script will scrape shows below(names in ' ' also are keys for Item container):
- '<i>date</i>'  - date of the single event/game in timedate format converted to UTC time(or tried to);
- '<i>game</i>' - name of the game(csgo, overwatch, dota2 etc);
- '<i>player1</i>' - name of the first participant(or team name, like: "Misfits" or "SK Gaming" etc);
- '<i>player2</i>' - name of the second participant;
- '<i>odds1</i>' - bet rate on the first player(float value, like: 1.345);
- '<i>odds2</i>' - bet rate on the second player(float value).

Now, for convenient purpose this script needs that variable <b>TIME_DIFFERENCE</b> been set inside script to your own value.
- <i>TIME_DIFFERENCE</i> - represent a difference between time for event, that shows on website
                    and UTC time(check in script comments). You can set it to "0", and then all dates for events,
                    which starts 24+ hours from current time will be saved in site_time format(not UTC).</br>

Also, if script works to slowly or scraped information not full - you can try to adjust parameters '<i>sleep_time</i>'
and '<i>loop_timer</i>' inside of method "parse" of OneHash class.

To <b>run a spider</b> - change your location in terminal to scrapy project folder and type:</br> 
```scrapy crawl onehash```</br>
To save data to .json file(for example), type:</br> 
```scrapy crawl onehash -o yourfile.json```
