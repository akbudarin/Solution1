import logging
import sys
import time
import traceback
import schedule as schedule
from multiprocessing import Process, Manager
from passwords import telegram_key
import requests
import json
import datetime
from dateutil.tz import tzoffset

logging.basicConfig(
    filename="logs_main.txt", level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def get_current_price(ticker: str):
    r = requests.get(
        'http://fincloudlabs.com/api/candle/{}'.format(ticker),
        headers={'apiaccesskey': 'ABwdI6XOb9eq5Ica1CgV'})
    r_data = json.loads(r.text)
    r_data_low = "%.2f" % float(r_data['low'])
    r_data_high = "%.2f" % float(r_data['high'])
    price = '{} - {}'.format(r_data_low, r_data_high)
    return price


def get_info_for_one_signal(ticker: str):
    pattern_url = "http://fincloudlabs.com/api/signal/"
    try:
        r = requests.get(pattern_url + ticker,
                         headers={'apiaccesskey': 'ABwdI6XOb9eq5Ica1CgV'},
                         timeout=10)
        r_data = json.loads(r.text)
        dict_of_emoji = {'HOLD': "🟡", "BUY": "🔴", "SELL": "🟢"}
        r_data["signal"] = r_data["signal"] + dict_of_emoji[r_data["signal"]]
    except KeyError:
        send_message_about_error(r.url + r.text +
                                 str(traceback.format_exc()))
        print(r.url + r.text)
        return ''
    except Exception as ex:
        send_message_about_error(r.url + r.text +
                                 str(traceback.format_exc()))
        print(r.url + r.text)
        return ''
    return r_data


def get_list_of_tickers():
    url = "https://fincloudlabs.com/api/market"
    r = requests.get(url, headers={'apiaccesskey': 'ABwdI6XOb9eq5Ica1CgV'},
                     timeout=10)
    try:
        r_data = json.loads(r.text)
        list_with_names_of_tickers = list(r_data.keys())
    except Exception as ex:
        sys.exit("Страница {} недоступна!\n"
                 "{}".format(url, r.status_code))
    return list_with_names_of_tickers


def send_message_to_channel(some_text):
    requests.post(
        'https://api.telegram.org/bot{key_bot}/sendMessage?chat_id=-1001572163167&'
        'text={some_text}'.format(key_bot=telegram_key, some_text=some_text))
    # requests.post(
    #     'https://api.telegram.org/bot{key_bot}/sendMessage?chat_id=-1001680841952&'
    #     'text={some_text}'.format(key_bot=telegram_key, some_text=some_text))


def send_message_about_error(text_error):
    """ Send message about any error to the owner """
    new_text_error = "Time error is {}. The error is ".format(
        str(datetime.datetime.now().time())[:-7]) + text_error
    requests.post(
        'https://api.telegram.org/bot{key_bot}/sendMessage?chat_id=46691361&'
        'text={some_text}'.format(key_bot=telegram_key, some_text=new_text_error))


def append_ticker_to_list(ticker, return_list):
    text_to_send = "Ticker: %23{ticker}\n" \
                   "Signal: {signal}\n" \
                   "Price: {price}\n\n"
    try:
        signal_info = get_info_for_one_signal(ticker)
        return_list.append(text_to_send.format(
            ticker=signal_info['ticker'],
            signal=signal_info["signal"],
            price=get_current_price(ticker)))
    except Exception as ex:
        logging.info("Error!" + str(ex))
        logging.info(str(traceback.format_exc()))


def get_info_for_tickers(list_of_tickers):
    procs = []
    manager = Manager()
    return_list = manager.list()

    for ticker in list_of_tickers:
        proc = Process(target=append_ticker_to_list, args=(ticker, return_list))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    return list(return_list)


def main():
    try:
        start_time = datetime.time(hour=6, minute=0)
        finish_time = datetime.time(hour=23, minute=0)
        list_of_tickers = get_list_of_tickers()
        if start_time < datetime.datetime.now(tz=tzoffset("UTC+0", 0)).time() < finish_time \
                and datetime.datetime.now(tz=tzoffset("UTC+0", 0)).weekday() < 5:
            data_tickers = get_info_for_tickers(list_of_tickers)
            five_tickers = ''
            for count, i in enumerate(data_tickers, 1):
                five_tickers += i
                if count % 5 == 0:
                    send_message_to_channel(five_tickers)
                    five_tickers = ''
    except Exception as ex:
        send_message_about_error(str(ex))


if __name__ == "__main__":
    schedule.every().hour.at(":00").do(main)
    schedule.every().hour.at(":05").do(main)
    schedule.every().hour.at(":10").do(main)
    schedule.every().hour.at(":15").do(main)
    schedule.every().hour.at(":20").do(main)
    schedule.every().hour.at(":25").do(main)
    schedule.every().hour.at(":30").do(main)
    schedule.every().hour.at(":35").do(main)
    schedule.every().hour.at(":40").do(main)
    schedule.every().hour.at(":45").do(main)
    schedule.every().hour.at(":50").do(main)
    schedule.every().hour.at(":55").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
    #main()
