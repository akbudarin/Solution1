import logging
import sys
import time
import traceback
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
    price = '{} - {}'.format(r_data['low'], r_data['high'])
    return price


def get_info_for_one_signal(ticker: str):
    pattern_url = "http://fincloudlabs.com/api/signal/"
    r = requests.get(pattern_url + ticker,
                     headers={'apiaccesskey': 'ABwdI6XOb9eq5Ica1CgV'},
                     timeout=10)
    try:
        r_data = json.loads(r.text)
        dict_of_emoji = {'HOLD': "🟡", "BUY": "🔴", "SELL": "🟢"}
        r_data["signal"] = r_data["signal"] + dict_of_emoji[r_data["signal"]]
    except KeyError:
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
    # requests.post(
    #     'https://api.telegram.org/bot{key_bot}/sendMessage?chat_id=-1001572163167&'
    #     'text={some_text}'.format(key_bot=telegram_key, some_text=some_text))
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
    print("Current time is " + str(datetime.datetime.now().time())[:-7])
    start_time = datetime.time(hour=6, minute=0)
    finish_time = datetime.time(hour=23, minute=0)

    list_of_tickers = get_list_of_tickers()
    print("Started loop")
    text_to_send = "Ticker: %23{ticker}\n" \
                   "Signal: {signal}\n" \
                   "Price: {price}"
    while True:
        # example other solution: (datetime.datetime.now() + datetime.timedelta(hours=10))
        if start_time < datetime.datetime.now(tz=tzoffset("UTC+0", 0)).time() < finish_time and \
                datetime.datetime.now(tz=tzoffset("UTC+0", 0)).weekday() < 5:
            data_tickers = []
            start_time_11 = time.time()

            for ticker in list_of_tickers:
                try:
                    signal_info = get_info_for_one_signal(ticker)
                    if signal_info == '':
                        continue
                    else:
                        data_tickers.append(text_to_send.format(
                            ticker=signal_info['ticker'],
                            signal=signal_info["signal"],
                            price=get_current_price(ticker)))
                except Exception as ex:
                    logging.info("Error in loop!" + str(ex))
                    logging.info(str(traceback.format_exc()))
                    send_message_about_error(str(ex) + str(traceback.format_exc()))
            print("--- %s seconds ---" % (time.time() - start_time_11))
            for count, i in enumerate(data_tickers):
                # time.sleep(1)
                # send_message_to_channel(i)
                print(count)
            time.sleep(300-60-60)
        else:
            time.sleep(300-60-60)


if __name__ == "__main__":
    main()
