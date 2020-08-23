# Uno
A server and a client for the UNO card game.  
Since card amount is showing all the time, you don't need to call UNO when you have one card left ;)  
  
It works on local for both the server and the client.  
To make it listen to the public internet, server.py need to add argument 'host = 0.0.0.0' to app.run(). Then client.py need to change SERVER_URL according to the actual server's IP address.   
