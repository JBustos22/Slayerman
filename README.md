# DFBot
A Discord bot for Quake III DeFRaG.

# Environment

Python>=3.8.5 required

Conda environment not necessary, but suggested: https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html

To install requirements, simply do:

`pip install -r requirements.txt`

# Setting up local Database

1. Download PostgreSQL: https://www.postgresqltutorial.com/install-postgresql/
    * port 5432
    * username postgres
    * password of your choice
    
2. Download pgAdmin4: https://www.pgadmin.org/download/

3. Open up pgAdmin4

4. Right click on Servers, create Server.

5. Name your server whatever you'd like.

6. Click on the connection tab, enter:
    * Host: localhost
    * Port: 5432
    * Username: postgres
    * Password: password chosen at step 1
    * Save

7. Inside your server, right click Databases, create Database.
    * Name this database "Defrag"
    * Save

8. Right click the Defrag database, Restore...

9. Navigate to this repo's folder, select df.db **(Note: you may have to select 'Format: all files' for this file to be visible)**
     * Click Restore

10. Once finished, confirm success by checking that there is an table named 'discord_ids' under Defrag -> Schemas -> Tables

11. If success, store your database password in keyring by running `python` in the project's environment and doing:
    ```
    >>> import keyring
    >>> keyring.set_password("db_password", "postgres", "<your password from step 1>")
    ```

# Running the bot

1. Create an account/log in to: 

    https://discord.com/developers/applications

2. Create a new app.

3. Navigate to the Bots tab.

4. Add a new bot, customize as desired.

5. Copy token.

6. Run `python` in the project's environment and do:
    ```
    >>> import keyring
    >>> keyring.set_password("bot_token", "dfbot", "<your token goes here>")
    ```

7. Navigate back to General Information in discord developers portal.

8. Copy the Client ID.

9. Invite bot to your server using the Client ID in this link:
  
    https://discord.com/oauth2/authorize?client_id={Client_ID}&scope=bot
  
    Note: To invite the bot to a server that is not yours,, give this link with your client ID to the server owner instead.
  
10. Finally, run the bot with 
  
    `python dfbot.py` in the proper environment

    You should see a message such as 

     `We have logged in as DFBot#xxxx`

    And the bot's status should be 'online'.
