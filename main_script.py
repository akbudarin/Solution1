import time
from passwords import telegram_key
import requests
import json
import datetime


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


def main():
    print(datetime.datetime.now().time())
    start_time = datetime.time(hour=9, minute=0)
    finish_time = datetime.time(hour=23, minute=0)
    list_of_tickers = get_list_of_tickers()
    while True:
        if start_time < datetime.datetime.now().time() < finish_time and \
                datetime.datetime.today().weekday() < 5:
            for ticker in list_of_tickers:
                signal_info = get_info_for_one_signal(ticker)
                text_to_send = \
                    "Тикер: {ticker}, сигнал: {signal}".format(
                    ticker=signal_info['ticker'], signal=signal_info['signal'])
                send_message_to_channel(text_to_send)
                time.sleep(6)
        else:
            time.sleep(6)


if __name__ == "__main__":
    main()
