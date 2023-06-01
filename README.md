
# 🕸️cli-status
cli-status is a Python command line app to get the ping, packet loss, and HTTP response code of a host in the terminal.

#### NOTE: This app does not render dynamically, therefore it may look laggy when the table renders.

### Notes
- Uses the **rich** module for generating the table and the color coding in the terminal
- Color coded latency, packet loss, and HTTP response codes

### Instructions

1) Add hosts to a .txt file; a file named hosts.txt is already provided for you

#### hosts.txt
```
google.com
1.1.1.1
8.8.8.8
```

2) Run the script in your terminal
```
python main.py -f {FILE}.txt
```

3) Wait for the table to generate; at the end, you should see a table with the ping and other stats
