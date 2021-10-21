import logging
import time
import traceback
from passwords import telegram_key
import requests
import json
import datetime

logging.basicConfig(
    filename="logs.txt", level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def get_info_for_one_signal(ticker: str):
    pattern_url = "http://fincloudlabs.com/api/signal/"
    r = requests.get(pattern_url + ticker)
    r_data = json.loads(r.text)
    dict_of_emoji = {'HOLD': "🟡", "BUY": "🔴", "SELL": "🟢"}
    r_data["signal"] = r_data["signal"] + dict_of_emoji[r_data["signal"]]
    print()
    return r_data


def get_list_of_tickers():
    url = "https://fincloudlabs.com/api/ticker"
    r = requests.get(url)
    r_data = json.loads(r.text)
    list_with_names_of_tickers = list(r_data.keys())
    print()
    return list_with_names_of_tickers


def send_message_to_channel(some_text):
    requests.post(
        'https://api.telegram.org/bot{key_bot}/sendMessage?chat_id=-1001572163167&'
        'text={some_text}'.format(key_bot=telegram_key, some_text=some_text))

    # for "Signals" channel
    requests.post(
        'https://api.telegram.org/bot{key_bot}/sendMessage?chat_id=-1001680841952&'
        'text={some_text}'.format(key_bot=telegram_key, some_text=some_text))


def send_message_about_error(text_error):
    """ Send message about any error to the owner """
    new_text_error = "Time error is {}. The error is ".format(
        str(datetime.datetime.now().time())[:-7]) + text_error
    requests.post(
        'https://api.telegram.org/bot{key_bot}/sendMessage?chat_id=46691361&'
        'text={some_text}'.format(key_bot=telegram_key, some_text=new_text_error))


def main():
    print(datetime.datetime.now().time())
    start_time = datetime.time(hour=9, minute=0)
    finish_time = datetime.time(hour=23, minute=0)
    list_of_tickers = get_list_of_tickers()
    while True:
        if start_time < datetime.datetime.now().time() < finish_time and \
                datetime.datetime.today().weekday() < 5:
            for ticker in list_of_tickers:
                try:
                    signal_info = get_info_for_one_signal(ticker)
                    text_to_send = \
                        "Тикер: {ticker}, сигнал: {signal}".format(
                        ticker=signal_info['ticker'], signal=signal_info['signal'])
                    send_message_to_channel(text_to_send)
                except Exception as ex:
                    logging.info("Error in loop!" + str(ex))
                    logging.info(str(traceback.format_exc()))
                    send_message_about_error(str(ex))
                    send_message_about_error(str(traceback.format_exc()))
                time.sleep(6)
        else:
            time.sleep(6)


if __name__ == "__main__":
    main()

