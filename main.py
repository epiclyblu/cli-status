# python main.py -f hosts.txt
# python main.py -s google.com cloudflare.com 1.1.1.1

import argparse
import os
from rich import print
from rich.console import Console
from rich.live import Live
from rich.table import Table
from icmplib import ping
import requests


def get_ping(server_url: str):
    """
    Get the ping of a server; supported hostname formats: IPv4, IPv6, FQDN (domain)

    Arguments: server_url: str

    """

    try:
        response = ping(server_url, count=2, interval=0.1, timeout=1, privileged=False)

        average = response.avg_rtt

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


def monitor(servers):
    """
    Monitor the status of multiple servers
    """

    table = Table(title="Host Status", show_header=True, header_style="blue")
    table.add_column("🌐 Hostname", justify="center", style="cyan", width=24)
    table.add_column("📶 Ping", justify="center", width=12)
    table.add_column("📉 Result", justify="center", width=12)
    table.add_column("⛵ HTTP", justify="center", width=12)

    with Live(table, refresh_per_second=4, console=console):
        for server in servers:
            latency = get_ping(server)
            http = get_http(server)

            ping_val = f"{latency[0]}" + " ms" if f"{latency[0]}" else "Error"
            packet_loss = f"{latency[1]}" if f"{latency[1]}" else "Error"
            status_code = str(http) if http is not None else "Error"

            table.add_row(server, ping_val, packet_loss, status_code)


def main():
    """
    Main function to parse arguments and call the monitor function
    """
    parser = argparse.ArgumentParser(description="cli status")
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-f", "--file", help="Path to the hostname file")
    group.add_argument("-s", "--server", nargs="+", help="Hostname to monitor")

    # You can choose any file you want to monitor.
    args = parser.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            servers = f.read().splitlines()
        if os.stat(args.file).st_size == 0:
            print(":warning:", "[bold red]No servers found in hosts.txt."
                            "Please add servers line by line[/bold red]")
            return
    elif args.server:
        servers = args.server
    monitor(servers)


if __name__ == "__main__":
    console = Console()
    main()
    