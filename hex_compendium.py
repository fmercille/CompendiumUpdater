import json
import urllib.parse
import urllib.request
import os
import sys
import traceback

class HexCompendium:
    API_URL = 'https://hexcompendium.com/api.php'
    USER = os.environ['COMPENDIUM_USER']
    PASSWORD = os.environ['COMPENDIUM_PASS']
    LOG_FILES = { 'created': 'log_created.txt', 'error': 'log_error.txt' }
    edit_token = None

    def __init__(self):
        cookieProcessor = urllib.request.HTTPCookieProcessor()
        self.opener = urllib.request.build_opener(cookieProcessor)
        self.login()

    def login(self):
        # Fetch login token
        login_token_data = {
            'action':   'query',
            'meta':     'tokens',
            'type':     'login'
            }

        login_token = self.call_api(login_token_data)['query']['tokens']['logintoken']

        # Login
        login_data = {
            'action':       'login',
            'lgname':       self.USER,
            'lgpassword':   self.PASSWORD,
            'lgtoken':      login_token
            }

        login = self.call_api(login_data)
        self.token = login['login']['lgtoken']
        print("Login result:\n" + str(login))

    def call_api(self, data):
        data['format'] = 'json'
        encoded_data = urllib.parse.urlencode(data).encode()
        headers = { 'User-Agent': 'HexCompendium Bot' }
        req = urllib.request.Request(self.API_URL, data=encoded_data, headers=headers)
        response = self.opener.open(req)
        return json.loads(response.read().decode('utf-8'))

    def page_exists(self, name):
        check_data = {
            'action': 'query',
            'titles': name,
            'prop': 'info',
            'inprop': 'url'
        }
        response = self.call_api(check_data)
        pageid = response['query']['pages']

        return list(response['query']['pages'].keys())[0] != '-1'

    def delete_page(self, pageid):
        # Fetch edit token
        if self.edit_token is None:
            edit_token_data = {
                'action': 'query',
                'meta': 'tokens',
            }

            self.edit_token = self.call_api(edit_token_data)['query']['tokens']['csrftoken']
            

        delete_page_data = {
            'action': 'delete',
            'pageid': pageid,
            'token': self.edit_token
        }

        response = self.call_api(delete_page_data)
        print(response)

    def create_page(self, name, text, retry=False):
        response = None
        try:
            # Fetch edit token
            if self.edit_token is None:
                edit_token_data = {
                    'action': 'query',
                    'meta': 'tokens',
                }

                self.edit_token = self.call_api(edit_token_data)['query']['tokens']['csrftoken']

            create_data = {
                'action': 'edit',
                'title': name,
                'text': text,
                'createonly': True,
                'token': self.edit_token
            }

            response = self.call_api(create_data)

            if 'error' in response and response['error']['code'] in ('badtoken', 'permissiondenied') and retry == False:
                self.edit_token = None
                self.token = None
                self.login()
                return self.create_page(name, text, retry=True)

            pageid = response['edit']['pageid']
            print(response)
            print()
            print("Created {0}".format(name))

            info_data = {
                'action': 'query',
                'prop': 'info',
                'pageids': pageid,
                'inprop': 'url'
            }
            response = self.call_api(info_data)
            print(response)
            f = open(self.LOG_FILES['created'], 'a')
            f.write(str(pageid) + "\t" + response['query']['pages'][str(pageid)]['fullurl'] + "\n")
            f.close()
            return True
        except:
            f = open(self.LOG_FILES['error'], 'a')
            f.write("Card {0} generated an error:\n".format(name))
            f.write(str(response))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            f.write("-------\n")
            traceback.print_tb(exc_traceback, limit=1, file=f)
            f.write("-------\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=f)
            f.write("======================\n")
            f.close()
            return False

