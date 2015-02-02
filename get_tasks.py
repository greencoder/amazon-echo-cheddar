import arrow
import BeautifulSoup
import ConfigParser
import json
import requests
import sys
import urllib

class AmazonManager():

    def __init__(self, email, password, token, list_id):

        self.email = email
        self.password = password
        self.cheddar_access_token = token
        self.cheddar_list_id = list_id

        self.session = requests.Session()

        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.13) '\
                + 'Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13',
            'Charset': 'utf-8',
            'Origin': 'http://echo.amazon.com',
            'Referer': 'http://echo.amazon.com/spa/index.html',
        }

        self.session.headers.update(self.default_headers)
        self.login()

    def __del__(self):
        self.logout()

    def add_item_to_cheddar(self, item):

        # The Cheddar API URL for adding a task to a list
        url = "https://api.cheddarapp.com/v1/lists/%s/tasks" % self.cheddar_list_id

        # The body is the item to add
        data = {
            "task[text]": urllib.quote_plus(item['text']),
        }

        # Put the OAuth info into the headers
        headers = {
            "Authorization": "Bearer %s" % self.cheddar_access_token,
        }

        # Make the request
        cheddar_request = requests.post(url, data=data, headers=headers)

    def find_csrf_cookie(self):
        for cookie in self.session.cookies:
            if cookie.name == "csrf":
                return cookie.value
        return None

    def delete_shopping_items(self, items):

        # This PUT request needs special headers
        headers = {
            'Content-type': 'application/json',
            'csrf': self.find_csrf_cookie(),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        }

        # Loop through the items and delete each one
        for item in items:
            id = urllib.quote_plus(item['itemId'])
            item['deleted'] = True
            url = 'https://pitangui.amazon.com/api/todos/%s' % id
            delete_request = self.session.put(url, data=json.dumps(item), headers=headers)

    def fetch_shopping_items(self):

        # Request the shopping list todo API
        url = 'https://pitangui.amazon.com/api/todos?type=SHOPPING_ITEM&size=100&completed=false'
        shopping_request = self.session.get(url)

        data = shopping_request.json()

        # Find all the items
        items = []
        if data.has_key('values'):
            for value in data['values']:
                items.append(value)

        # Return our list of item objects
        return items

    def logout(self):
        self.session.headers.update({ 'Referer': 'http://echo.amazon.com/spa/index.html' })
        url = 'https://pitangui.amazon.com/logout'
        self.session.get(url)

    def login(self):

        # Request the login page
        login_url = 'https://pitangui.amazon.com'
        login_request = self.session.get(login_url)

        # Turn the login page into a soup object
        login_soup = BeautifulSoup.BeautifulSoup(login_request.text)

        # Find the <form> tag and the action from the login page
        form_el = login_soup.find('form')
        action_attr = form_el.get('action')

        # Set up the parameters we will pass to the signin
        parameters = {
            'email': self.email,
            'password': self.password,
            'create': 0,
        }

        # Find all the hidden form elements and stick them in the params
        for hidden_el in form_el.findAll(type="hidden"):
            parameters[hidden_el['name']] = hidden_el['value']

        # Update the session with the new referer
        self.session.headers.update({ 'Referer': login_url })

        # Post to the login page
        login_request = self.session.post(action_attr, data=parameters)

        # Make sure it was successful
        if login_request.status_code != 200:
            sys.exit("Error logging in! Got status %d" % login.status_code)


if __name__ == "__main__":

    # Load the config info from the config.txt file
    config = ConfigParser.ConfigParser()
    config.read("config.txt")

    print "%s\tChecking Amazon Shopping List" % arrow.now()

    # Make sure we have the items in the config
    try:
        email = config.get('Amazon', 'email')
        password = config.get('Amazon', 'password')
        token = config.get('Cheddar', 'Token')
        list_id = config.get('Cheddar', 'ListID')
    except Exception, e:
        sys.exit("Invalid or missing config.txt file.")

    # Instantiate the manager
    manager = AmazonManager(email, password, token, list_id)

    # Get all the items on your shopping list
    items = manager.fetch_shopping_items()

    for item in items:
        print "%s\tFound Item: %s" % (arrow.now(), item['text'])
        manager.add_item_to_cheddar(item)
        manager.delete_shopping_items(items)
