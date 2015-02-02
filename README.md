# amazon-echo-cheddar

Moves items from your Amazon Echo Shopping list to your lists in Cheddar. 

# Usage

`$ python get_tasks.py`

# Configuration

Move `config.sample` to `config.txt`. Add your Amazon account email/username and your Cheddar OAuth token and list ID. (details below)

# How to set up Cheddar (get your token and list ID)

First, go register an application:

<https://cheddarapp.com/developer/apps/new>

View your application to get the Client ID and Secret: (substitute your app ID)

<https://cheddarapp.com/developer/apps/123>

On that page, you'll find an access token. Use the token to get your lists:

`curl -i "https://api.cheddarapp.com/v1/lists" -H "Authorization: Bearer <access_token>"`

Find your list in the response and note its "id" parameter. Use that ID to add items to your list:

`curl -i "https://api.cheddarapp.com/v1/lists/<list_id>/tasks" -X POST -d "task[text]=<URL escaped task text>" -H "Authorization: Bearer <access_token>"`