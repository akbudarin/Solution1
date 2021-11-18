import logging
import sys
import time
import traceback
from passwords import telegram_key
import requests
import json
from scrapy.selector import Selector
import datetime

logging.basicConfig(
    filename="logs_main.txt", level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def get_current_price(ticker: str):
    ticker_investing_pair = {'AMD': "adv-micro-device", 'F': "ford-motor-co",
                             'T': "at-t", 'NFLX': "netflix,-inc.",
                             'PYPL': "paypal-holdings-inc",
                             'NVDA': "nvidia-corp",
                             'TSLA': "tesla-motors",
                             'AAL': "american-airlines-group",
                             'NKE': "nike", 'SHOP': "shopify-inc",
                             'GE': "general-electric", 'TWTR': "twitter-inc",
                             'PFE': "pfizer", 'BAC': "bank-of-america",
                             'DIS': "disney", 'GOOG': "google-inc-c",
                             'JNJ': "johnson-johnson", 'FB': "facebook-inc",
                             'UAL': "united-continenta", 'V': "visa-inc",
                             'MA': "mastercard-cl-a", 'MRK': "merck---co",
                             'AMZN': "amazon-com-inc", 'SNAP': "snap-inc",
                             'SPOT': "spotify-technology",
                             'XOM': "exxon-mobil",
                             'HAL': "halliburton-co", 'BABA': "alibaba",
                             'C': "citigroup", 'MSFT': "microsoft-corp",
                             'IBM': "ibm", 'SQ': "square-inc",
                             'UBER': "uber-technologies-inc",
                             'JPM': "jp-morgan-chase",
                             'AAPL': "apple-computer-inc",
                             'ARNC': "arconic-inc",
                             'BA': "boeing-co", 'BBY': "best-buy",
                             'CMCSA': "comcast-corp-new",
                             'COIN': "coinbase-global",
                             'CSCO': "cisco-sys-inc", 'CVX': "chevron",
                             'GS': "goldman-sachs-group", 'INTC': "intel-corp",
                             'KO': "coca-cola-co", 'LMT': "lockheed-martin",
                             'TXN': "texas-instru",
                             'VZ': "verizon-communications",
                             'WFC': "wells-fargo", 'GOOGL': "google-inc"}
    r = requests.get('https://ru.investing.com/equities/{}'.format(
        ticker_investing_pair[ticker]))
    price = Selector(text=r.text).xpath('//*[@data-test="instrument-price-last"]/text()').get()
    if price.count(',') == 2:
        price = price.replace(',', '', 1)
    price = float(price.replace(',', '.'))
    price = '{} - {}'.format(round(0.997*price, 2), round(1.003*price, 2))
    return price


def get_info_for_one_signal(ticker: str):
    pattern_url = "http://fincloudlabs.com/api/signal/"
    r = requests.get(pattern_url + ticker)
    r_data = json.loads(r.text)
    dict_of_emoji = {'HOLD': "🟡", "BUY": "🔴", "SELL": "🟢"}
    r_data["signal"] = r_data["signal"] + dict_of_emoji[r_data["signal"]]
    return r_data


def get_list_of_tickers():
    url = "https://fincloudlabs.com/api/market"
    r = requests.get(url)
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


def send_message_about_error(text_error):
    """ Send message about any error to the owner """
    new_text_error = "Time error is {}. The error is ".format(
        str(datetime.datetime.now().time())[:-7]) + text_error
    requests.post(
        'https://api.telegram.org/bot{key_bot}/sendMessage?chat_id=46691361&'
        'text={some_text}'.format(key_bot=telegram_key, some_text=new_text_error))


def get_current_status_of_signals(list_of_tickers):
    """ Return dict which key is ticker name and value is list with two elements.
        First element is signal data. Second is flag for stoppage """

    status_dict = {}
    for ticker in list_of_tickers:
        status_dict[ticker] = [get_info_for_one_signal(ticker)['signal'], False, 0, 0] # 3-ее значиение отвечает за кол-во buy, 4-ое за sell
    return status_dict


def main():
    print("Current time is " + str(datetime.datetime.now().time())[:-7])
    start_time = datetime.time(hour=6, minute=0)
    finish_time = datetime.time(hour=23, minute=0)
    from dateutil.tz import tzoffset
    list_of_tickers = get_list_of_tickers()
    dict_previous_status = get_current_status_of_signals(list_of_tickers)
    print("Started loop")
    while True:
        # example other solution: (datetime.datetime.now() + datetime.timedelta(hours=10))
        if start_time < datetime.datetime.now(tz=tzoffset("UTC+0", 0)).time() < finish_time and \
                datetime.datetime.now(tz=tzoffset("UTC+0", 0)).weekday() < 5:
            for ticker in list_of_tickers:
                try:
                    signal_info = get_info_for_one_signal(ticker)
                    text_to_send = "Ticker: %23{ticker}\n" \
                                   "Signal: {signal}"
                    # Если ещё не на удержании и получили "HOLD" сигнал
                    if dict_previous_status[ticker][1] is False and signal_info['signal'] == "HOLD🟡":
                        dict_previous_status[ticker][1] = True    # Ставим на удержание (блокировку)
                        if dict_previous_status[ticker][0] == "SELL🟢":
                            text_signal = "WAIT"
                        if dict_previous_status[ticker][0] == "BUY🔴" or \
                                dict_previous_status[ticker][0] == "HOLD🟡":
                            text_signal = "HOLD🟡"
                        text_to_send = text_to_send.format(
                                ticker=signal_info['ticker'],
                                signal=text_signal)
                        send_message_to_channel(text_to_send)
                    elif signal_info['signal'] != "HOLD🟡":
                        dict_previous_status[ticker][1] = False  # Снимаем блокировку, если она есть
                        text_to_send = "Ticker: %23{ticker}\n" \
                                       "Signal: {signal}\n" \
                                       "Price: {price}"
                        text_to_send = text_to_send.format(
                            ticker=signal_info['ticker'],
                            signal=signal_info['signal'],
                            price=get_current_price(signal_info['ticker'])
                        )

                        if signal_info['signal'] == "BUY🔴":
                            dict_previous_status[ticker][3] = 0
                            if dict_previous_status[ticker][2] < 3:
                                if dict_previous_status[ticker][2] == 0:
                                    send_message_to_channel(text_to_send)
                                dict_previous_status[ticker][2] += 1
                            elif dict_previous_status[ticker][2] >= 3:
                                dict_previous_status[ticker][2] = -2
                                send_message_to_channel(text_to_send)

                        if signal_info['signal'] == "SELL🟢":
                            dict_previous_status[ticker][2] = 0
                            if dict_previous_status[ticker][3] < 3:
                                if dict_previous_status[ticker][3] == 0:
                                    send_message_to_channel(text_to_send)
                                dict_previous_status[ticker][3] += 1
                            elif dict_previous_status[ticker][3] >= 3:
                                dict_previous_status[ticker][3] = -2
                                send_message_to_channel(text_to_send)

                        dict_previous_status[ticker][0] = signal_info['signal']

                except Exception as ex:
                    logging.info("Error in loop!" + str(ex))
                    logging.info(str(traceback.format_exc()))
                    send_message_about_error(str(ex) + str(traceback.format_exc()))
                time.sleep(6)
        else:
            time.sleep(6)


if __name__ == "__main__":
    main()
