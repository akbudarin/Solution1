import logging
import time
import traceback
from passwords import telegram_key
import requests
import json
import datetime

logging.basicConfig(
    filename="logs_Signals.txt", level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def get_info_for_one_signal(ticker: str):
    pattern_url = "http://fincloudlabs.com/api/signal/"
    r = requests.get(pattern_url + ticker)
    r_data = json.loads(r.text)
    dict_of_emoji = {'HOLD': "🟡", "BUY": "🔴", "SELL": "🟢"}
    r_data["signal"] = r_data["signal"] + dict_of_emoji[r_data["signal"]]
    return r_data


def get_list_of_tickers():
    url = "https://fincloudlabs.com/api/ticker"
    r = requests.get(url)
    r_data = json.loads(r.text)
    list_with_names_of_tickers = list(r_data.keys())
    return list_with_names_of_tickers


def send_message_to_channel(some_text):
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


def get_current_status_of_signals(list_of_tickers):
    """ Return dict which key is ticker name and value is list with two elements.
        First element is signal data. Second is flag for stoppage """

    status_dict = {}
    for ticker in list_of_tickers:
        status_dict[ticker] = [get_info_for_one_signal(ticker)['signal'], False]
    return status_dict


def main():
    print("Current time is " + str(datetime.datetime.now().time())[:-7])
    start_time = datetime.time(hour=9, minute=0)
    finish_time = datetime.time(hour=23, minute=59)
    list_of_tickers = ['F', 'TWTR']
    dict_previous_status = get_current_status_of_signals(list_of_tickers)
    print("Started loop")
    while True:
        if start_time < datetime.datetime.now().time() < finish_time and \
                datetime.datetime.today().weekday() < 5:
            for ticker in list_of_tickers:
                try:
                    signal_info = get_info_for_one_signal(ticker)
                    text_to_send = "Ticker: {ticker}, signal: {signal}"

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
                        dict_previous_status[ticker][1] = False   # Снимаем блокировку, если она есть
                        text_to_send = text_to_send.format(
                            ticker=signal_info['ticker'],
                            signal=signal_info['signal'])
                        send_message_to_channel(text_to_send)
                        dict_previous_status[ticker][0] = signal_info['signal']

                except Exception as ex:
                    logging.info("Error in loop!" + str(ex))
                    logging.info(str(traceback.format_exc()))
                    send_message_about_error(str(ex))
                    send_message_about_error(str(traceback.format_exc()))
                time.sleep(30)
        else:
            time.sleep(30)


if __name__ == "__main__":
    main()
