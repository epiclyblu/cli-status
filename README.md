
# 🕸️cli-status
cli-status is a Python command line app to get the ping, packet loss, and HTTP response code of a host in the terminal.

### Notes
- Uses the **rich** module for generating the table and the color coding in the terminal
- Updates **dynamically**; get updates in real time
- Color coded latency, packet loss, and HTTP response codes

### Instructions

1) You can do one of the following:

- Add hosts to a file line by line, excluding the http:// or https:// at the beginning
  #### hosts.txt
  ```
  google.com
  1.1.1.1
  8.8.8.8
  ```

 - Or, specify the hosts you would like to ping in your command line argument using -s

2) Run the script in your terminal
```
python main.py -f {FILE}.txt
```
or
```
python main.py -s cloudflare.com google.com 1.1.1.1
```

3) Wait for the table to generate; at the end, you should see a table with the ping and other stats

### To-do
- Auto-save settings
- Command line arguments for packet count, timeouts, etc.
