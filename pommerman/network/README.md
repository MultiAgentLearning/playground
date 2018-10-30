## IonPlayer (Pommerman network module)
## Running:
Run the command `ion_client` for running the client and `ion_server` for running the server
## How does this work:
```
Match-making pseudo-code:
Client:
1. Run wrapper on client which handles network + environment
2. Connect to Server and send a "match" request
Server:
1. Receive match request and look for other users who have sent a match request as well
2. If amount of players is equal to 4 and amount of matches running in parallel aren't more than a specified amount then send an "ready" request to the 4 players and wait
Client:
3. Respond to "ready" request with another "ready"
Server:
3A. If ready was not received from a user: Remove user from active players list and go back to step 1 (Look for another pair)
3B. If ready was received from everyone: Delegate a process to that match
```
```
Match-processing loop pseudo-code:
Server:
1. Send observation to all players with timeout
Client:
1. Send single action integer to server
Server:
2A. If action was received within timeout then parse it
2B. If action wasn't received or was received after timeout then issue a STOP action
```
```
Security considerations:
1. Isolated channels must be kept for each and every player as to prevent cheating by reading other messages on a single channel
2. In addition to 1 everything should also work on a single port
Both of these can be easily handled using WebSocket (https://en.wikipedia.org/wiki/WebSocket)
```
## The network code originated from the following repositories:
* ionclient - https://github.com/PixelyIon/ionplayer-client
* ionserver - https://github.com/PixelyIon/ionplayer-server