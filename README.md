# DFBot
A Discord bot for Quake III DeFRaG

# Environment

Python>=3.8.5 required

To install requirements, simply do:

`pip install -r requirements.txt`

# Running the bot

1. Create an account/log in to: 

    https://discord.com/developers/applications

2. Create a new app.

3. Navigate to the Bots tab.

4. Add a new bot, customize as desired.

5. Copy token.

6. Paste token into `CLIENT_TOKEN` dfbot.py.

7. Navigate back to General Information in discord developers portal.

8. Copy the Client ID.

9. Invite bot to your server using the Client ID in this link:
  
    https://discord.com/oauth2/authorize?client_id={Client ID}&scope=bot
  
    Note: To invite the bot to a server that is not yours,, give this link with your client ID to the server owner instead.
  
10. Finally, run the bot with 
  
    `python dfbot.py`

    You should see a message such as 

     `We have logged in as DFBot#xxxx`

    And the bot's status should be 'online'.
