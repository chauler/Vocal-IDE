# This file is a modified version of the "copilot api" project by B00TK1D, which can be found at https://github.com/B00TK1D/copilot-api
# The original project created an HTTP server for the copilot API,
# and I have modified it to be used as a module that could be imported, with a single class
# that wraps the original functionality.
# The original project comes with the following license:
# MIT License

# Copyright (c) 2024 B00TK1D

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import speech_recognition as sr
import requests
import json
import time
from server import send_message

class CopilotAuthenticator:
    def __init__(self):
        self.callbacks = []
        self.token = None
        # self.setup()

    def setup(self):
        resp = requests.post('https://github.com/login/device/code', headers={
            'accept': 'application/json',
            'editor-version': 'Neovim/0.6.1',
            'editor-plugin-version': 'copilot.vim/1.16.0',
            'content-type': 'application/json',
            'user-agent': 'GithubCopilot/1.155.0',
            'accept-encoding': 'gzip,deflate,br'
        }, data='{"client_id":"Iv1.b507a08c87ecfe98","scope":"read:user"}')

        # Parse the response json, isolating the device_code, user_code, and verification_uri
        resp_json = resp.json()
        device_code = resp_json.get('device_code')
        user_code = resp_json.get('user_code')
        verification_uri = resp_json.get('verification_uri')

        send_message({
            "route": "auth",
            "data": {
                "uri": verification_uri,
                "code": user_code
            }
        })

        while True:
            time.sleep(5)
            resp = requests.post('https://github.com/login/oauth/access_token', headers={
                'accept': 'application/json',
                'editor-version': 'Neovim/0.6.1',
                'editor-plugin-version': 'copilot.vim/1.16.0',
                'content-type': 'application/json',
                'user-agent': 'GithubCopilot/1.155.0',
                'accept-encoding': 'gzip,deflate,br'
            }, data=f'{{"client_id":"Iv1.b507a08c87ecfe98","device_code":"{device_code}","grant_type":"urn:ietf:params:oauth:grant-type:device_code"}}')

            # Parse the response json, isolating the access_token
            resp_json = resp.json()
            access_token = resp_json.get('access_token')

            if access_token:
                break

        # Save the access token to a file
        with open('.copilot_token', 'w') as f:
            f.write(access_token)

        print('Authentication success!')
        self.notify_authentication()

    # Check if the token is invalid through the exp field
    def is_token_invalid(self, token):
        if token is None or 'exp' not in token or self.extract_exp_value(token) <= time.time():
            return True
        return False

    def extract_exp_value(self, token):
        pairs = token.split(';')
        for pair in pairs:
            key, value = pair.split('=')
            if key.strip() == 'exp':
                return int(value.strip())
        return None

    def authenticate(self):
        # Check if the .copilot_token file exists
        while True:
            try:
                with open('.copilot_token', 'r') as f:
                    access_token = f.read()
                    break
            except FileNotFoundError:
                self.setup()
        # Get a session with the access token
        resp = requests.get('https://api.github.com/copilot_internal/v2/token', headers={
            'authorization': f'token {access_token}',
            'editor-version': 'Neovim/0.6.1',
            'editor-plugin-version': 'copilot.vim/1.16.0',
            'user-agent': 'GithubCopilot/1.155.0'
        })

        # Parse the response json, isolating the token
        resp_json = resp.json()
        self.token = resp_json.get('token')
        self.notify_authentication()

    def token_thread(self):
        while True:
            self.authenticate()
            time.sleep(25 * 60)

    def is_authenticated(self):
        return self.token is not None and not self.is_token_invalid(self.token)

    def watch_authentication(self, callback):
        self.callbacks.append(callback)
        return callback

    def notify_authentication(self):
        for callback in self.callbacks:
            callback()
        self.callbacks = []


authenticator = CopilotAuthenticator()


def copilot(prompt, language='python'):
    # If the token is None, get a new one
    if not authenticator.is_authenticated():
        authenticator.authenticate()

    try:
        resp = requests.post('https://copilot-proxy.githubusercontent.com/v1/engines/copilot-codex/completions', headers={'authorization': f'Bearer {authenticator.token}'}, json={
            'prompt': prompt,
            'suffix': '',
            'max_tokens': 1000,
            'temperature': 0,
            'top_p': 1,
            'n': 1,
            'stop': ['\n'],
            'nwo': 'github/copilot.vim',
            'stream': True,
            'extra': {
                'language': language
            }
        })
    except requests.exceptions.ConnectionError:
        return ''

    result = ''

    # Parse the response text, splitting it by newlines
    resp_text = resp.text.split('\n')
    for line in resp_text:
        # If the line contains a completion, print it
        if line.startswith('data: {'):
            # Parse the completion from the line as json
            json_completion = json.loads(line[6:])
            completion = json_completion.get('choices')[0].get('text')
            if completion:
                result += completion
            else:
                result += '\n'

    return result


def HandleInput(prompt, language='python'):
    # Get the completion from the copilot function
    completion = copilot(f"#{prompt}\n\n", language)
    return completion


def authenticate():
    authenticator.authenticate()


def watch_authentication(callback):
    authenticator.watch_authentication(callback)


def copilot_listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        input = ""
        while True:
            # Grab initial input
            r.adjust_for_ambient_noise(source, duration=2)
            send_message({"route": "message",
                          "data": {"message": 'Say something! Say "Exit" to stop.'}})
            audio = r.listen(source, timeout=7, phrase_time_limit=5)
            try:
                input = r.recognize_google(audio, language="en-US")
            except sr.UnknownValueError:
                print("Could not understand audio", file=sys.stderr)

            if input == "exit":
                print("Exiting...", flush=True)
                break

            prompt = input
            while True:
                # Continue existing prompt
                print(prompt, flush=True)
                completion = HandleInput(prompt)
                prompt += completion
                #print(f"Data:{{{completion}\n}}", flush=True)
                send_message({"route": "data",
                              "data": {"message": completion}})
                send_message({"route": "message",
                              "data": {"message": 'Continue? ("Yes"/"No")'}})
                while True:
                    try:
                        audio = r.listen(source, timeout=10,
                                         phrase_time_limit=3)
                        input = r.recognize_google(audio, language="en-US")
                    except sr.UnknownValueError:
                        print("Could not understand audio", file=sys.stderr)
                        continue
                    if input == "yes" or input == "no":
                        break
                if input == "no":
                    break


def main():
    # Every 25 minutes, get a new token
    authenticator.authenticate()
    prompt = "# create a simple loop to print 100 random numbers\n\n"
    while True:
        completion = HandleInput(prompt)
        if completion == '\n':
            break
        else:
            prompt += completion
    return prompt


if __name__ == '__main__':
    print(__name__, flush=True)
    main()
