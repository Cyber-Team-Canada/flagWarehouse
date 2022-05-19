# flagWarehouse
Flag submission system for Attack/Defense CTFs.

![Web interface](img/server.png)

* [Server](#server)
    * [Installation](#installation)
    * [Configuration](#configuration)
    * [Usage](#usage)
    * [Deployment (optional)](#deployment-optional)
* [Client](#client)

## Server
The server is a Flask web application that uses SQLite as its database engine. It stores flags and sends them
periodically to the verification server of the competition. It also provides an easy to use interface that shows some
stats and makes it possible to explore the database.

### Installation
```
git clone https://github.com/Cyber-Team-Canada/flagWarehouse.git
cd flagWarehouse/server
pip3 install -r requirements.txt
```
### Configuration
Obtain a `.env` file for the competition, or copy the `.env.template` file and modify. If the situation calls for it, modify the config.py for parameters that do not use `os.getenv()`.

Edit the parameters in [.env](server/application/.env)

- `FW_WEB_PASSWORD`: the password to access the web interface
- `FW_API_TOKEN`: the token for the flagWarehouse API
- `FW_TEAM_ID`: your team ID in the competition
- `FW_VM_SUBNET`: the subnet in which your vulnbox resides (10.FW_VM_SUBNET.FW_TEAM_ID.1)
- `FW_TEAM_TOKEN`: your team's token
- `FW_ROUND_DURATION`: the duration of a round (or *tick*) in seconds
- `FW_SUB_LIMIT`: number of flags that can be sent to the organizers' server each `FW_SUB_INTERVAL`
- `FW_SUB_INTERVAL`: interval in seconds for the submission; if the submission round takes more than the number of seconds
- `FW_SUB_HOST`: the domain name or IP address of the submission server
- `FW_SUB_PORT`: the port number of the submission server
- `FW_SUB_ENDPOINT`: the endpoint of the submission server (only used in HTTP submissions)
- `FW_SUB_USE_HTTP`: whether or not flag submission uses an HTTP connection (if false, use TCP)
- `FW_SUB_ACCEPTED`: the string used to verify whether the verification server accepted the flag

Edit the parameters in [config.py](server/config.py)

- `FLAG_FORMAT`: string containing the regex format of the flags
- `YOUR_TEAM`: the ip address of your team
- `TEAMS`: the ip addresses of the teams in the competition
- `FLAG_ALIVE`: the number of seconds a flag can be considered valid
- `SUB_URL`: the url used for the verification of the flags (only for HTTP submission)

There is also the environment variable `FLASK_DEBUG` in [run.sh](server/run.sh): if set, any edit to the source files
(including the configuration file) while the server is running will trigger a restart with the new parameters.
Take note that **the submission loop will not be restarted automatically**, even in debug mode, so if you need to change
parameters that influence its behaviour, please restart the server manually.

### Usage
```
chmod +x run.sh
./run.sh
```
The web interface can be accessed on port 5000. To log in, use any username and the password you set.

If the password is wrong, the server logger will display a warning containing the username and the password used, as
well as the IP from which the request came from.

### Deployment (optional)
Given that most CTFs only last some hours and teams are usually not *that* big, the quickest and least painful approach
would be to self host the application and to use [ngrok](https://ngrok.com/).

If for any reason this approach doesn't suit you, you will need to make some modifications to the source code yourself;
for example, running this app *as is* on [Heroku](https://heroku.com) would probably be a bad idea since it uses SQLite
([here's why](https://devcenter.heroku.com/articles/sqlite3)), so you'll need to use `psycopg2` instead of `sqlite3` in
[db.py](server/application/db.py) (all the queries *should* be compatible, though).

For any other modifications, follow the guidelines for Flask deployment of your platform of choice.

## Client
The client is a simple Python script that runs all the programs (both scripts and binaries) in a specific directory.
The programs *need* to run only one time on one target (the target IP address is passed via argv by the client). For a
basic template, please refer to [example.py](client/exploits/example.py).

When it starts, the client automatically fetches the configuration from the server (targets, round duration etc.). When 
the exploits print something on the standard output, the client reads the output in real time and extracts the flags
using the regex fetched from the server; as soon as the flags are found, they are sent (along with other data like the
username and the timestamp) to the [flagWarehouse server](server).

Right now, the module `requests` is still needed and listed in [requirements.txt](client/requirements.txt). In the
future, I might use `urllib` in order to avoid external dependencies.

For a list and explanation of the possible options, please refer to the CLI help.