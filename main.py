"""
cli-status: developed by @epiclyblu

A dynamically rendering CLI tool to monitor the status of multiple servers from
either a file or a list of servers provided by yourself.
"""

# python main.py -f hosts.txt
# python main.py -s google.com cloudflare.com 1.1.1.1

from threading import Thread
import argparse
import os
import time

from rich import print
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from icmplib import ping
from icmplib.exceptions import NameLookupError, TimeoutExceeded
import requests


def get_ping(server_url: str, count, interval, timeout):
    """
    Get the ping of a server; supported hostname formats: IPv4, IPv6, FQDN (domain)

    Arguments: server_url: str
    Returns: ping (float), packet_loss (float)
    """

    try:
        response = ping(server_url, count=count, interval=interval, timeout=timeout,
                        privileged=False)

        average = response.avg_rtt.__round__(1)

        if float(average) <= 50.0:
            average = f"[bright_green]{average}[/bright_green]"
        elif float(average) <= 100.0:
            average = f"[bright_yellow]{average}[/bright_yellow]"
        elif float(average) >= 100.0:
            average = f"[bright_red]{average}[/bright_red]"
        elif float(average) == 0.0:
            average = f"[bright_red]{average}[/bright_red]"

        packet_loss = int(response.packets_received)
        if packet_loss / 2 == 0:
            packet_loss = f"[bright_red]{packet_loss}/{response.packets_sent}[/bright_red]"
        elif packet_loss / 2 == 0.5:
            packet_loss = f"[bright_yellow]{packet_loss}/{response.packets_sent}[/bright_yellow]"
        elif packet_loss / 2 == 1:
            packet_loss = f"[bright_green]{packet_loss}/{response.packets_sent}[/bright_green]"

        return [average, packet_loss]
    except NameLookupError:
        return [None, None]
    except TimeoutExceeded:
        return [None, None]
    except requests.exceptions.RequestException:
        return [None, None]


def get_http(server_url):
    """
    Get the HTTP response code of a server

    Arguments: url (string)
    Returns: HTTP response code (integer)
    """

    try:
        response = requests.get(f"https://{server_url}", timeout=1)
        http = response.status_code

        if http in [200, 201, 204, 206]:
            http = f"[bright_green]{http}[/bright_green]"
        elif http in [400, 401, 403, 405, 408, 429]:
            http = f"[bright_yellow]{http}[/bright_yellow]"
        elif http in [404, 500, 502, 503, 504, 509]:
            http = f"[bright_red]{http}[/bright_red]"

        return http
    except requests.exceptions.RequestException:
        return None


def monitor_server(row, count, interval, timeout, cooldown):
    """
    Asynchronous function to monitor servers

    Arguments: server (list)
    Outputs: to the table in the monitor() function
    """

    server = row[0]
    timer_start = row[4]

    while True:
        elapsed_time = time.time() - timer_start
        remaining_time = max(cooldown - elapsed_time, 0)

        if remaining_time <= 0:
            latency = get_ping(server, count, interval, timeout)
            http = get_http(server)

            ping_val = f"{latency[0]} ms" if latency and latency[0] else "Error" if latency else "Processing"
            packet_loss = f"{latency[1]}" if latency and latency[1] else "Error" if latency else "Processing"
            status_code = str(http) if http else "Error"

            row[1] = ping_val
            row[2] = packet_loss
            row[3] = status_code
            row[4] = time.time()

        time.sleep(cooldown)


def monitor(servers, count, interval, timeout, cooldown):
    """
    Monitor the status of multiple servers

    Arguments: servers (list)
    Outputs: table (rich.Table)
    """

    table = Table(title="Host Status", show_header=True, header_style="blue")
    table.add_column("Hostname", justify="center", style="bright_cyan")
    table.add_column("Ping", justify="center", width=12)
    table.add_column("Result", justify="center", width=12)
    table.add_column("HTTP", justify="center", width=12)
    table.add_column("Next Update", justify="center", width=18)

    with Live(table, refresh_per_second=1) as live:
        rows = []

        for server in servers:
            rows.append([server, Spinner("dots"), Spinner("dots"), Spinner("dots"), 0])

        threads = []
        for row in rows:
            t = Thread(target=monitor_server, args=(row, count, interval, timeout, cooldown))
            threads.append(t)
            t.start()

        while any(t.is_alive() for t in threads):
            new_table = Table(title="Host Status", show_header=True, header_style="blue")
            new_table.add_column("Hostname", justify="center", style="bright_cyan")
            new_table.add_column("Ping", justify="center", width=12)
            new_table.add_column("Result", justify="center", width=12)
            new_table.add_column("HTTP", justify="center", width=12)
            new_table.add_column("Next Update", justify="center", width=18)

            for row in rows:
                hostname = row[0]
                ping_val = row[1]
                packet_loss = row[2]
                status_code = row[3]
                timer_start = row[4]

                elapsed_time = time.time() - timer_start
                remaining_time = max(cooldown - elapsed_time, 0)
                remaining_text = f"{int(remaining_time)}s" if remaining_time > 0 else Spinner("dots")

                new_table.add_row(hostname, ping_val, packet_loss, status_code, remaining_text)

            live.update(new_table)
            time.sleep(0.1)


def main():
    """
    Main function to parse arguments and call the monitor function
    """
    parser = argparse.ArgumentParser(description="cli status")
    group = parser.add_mutually_exclusive_group(required=True)

    # You can choose any file you want to monitor.
    group.add_argument("-f", "--file", help="Path to the hostname file")
    group.add_argument("-s", "--server", nargs="+", help="Hostname to monitor")
    parser.add_argument("-c", "--count", help="Number of pings to send", default=2)
    parser.add_argument("-i", "--interval", help="Interval between pings", default=0.1)
    parser.add_argument("-t", "--timeout", help="Timeout for each ping", default=1)
    parser.add_argument("-d", "--cooldown", help="Cooldown between each update", default=15)

    args = parser.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            servers = f.read().splitlines()
        if os.stat(args.file).st_size == 0:
            print(":warning: ", "[bold red]No servers found in hosts.txt. "
                                "Please add servers line by line[/bold red]")
            return
    elif args.server:
        servers = args.server

    try:
        monitor(servers, count=args.count, interval=args.interval, timeout=args.timeout,
                cooldown=args.cooldown)
    except KeyboardInterrupt:
        exit(0)


if __name__ == "__main__":
    console = Console()
    main()
