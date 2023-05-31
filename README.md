# cli-status
Get the status, latency, and HTTP response codes of multiple hosts in the terminal.

### How to use
1) Add hosts you would like to get the status of in any .txt file (do not add http:// or https://, this will be already added in the requests)
2) Then, run the script with argument -f or --file with the name of the text file (hosts.txt in this example)
3) The table will generate however pretty slowly.

### Sidenotes
- This is pretty buggy, the table generates slow and it isn't dynamic
- It is hardcoded to ping the hosts 2 times, and when calculating packet loss it only divides by 2

### To-do
- Dynamic updating table
- Try to always run this in the background
- More statistics
