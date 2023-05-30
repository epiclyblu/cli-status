import argparse
import os
import time
from urllib.parse import urlparse
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import progress
from icmplib import ping
import requests


def get_ping(server_url: str):
    """
    Get the ping of a server; supported hostname formats: IPv4, IPv6, FQDN (domain)

    Arguments: server_url: str

    """

    parsed_url = urlparse(server_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return None, None

    try:
        response = ping(server_url, count=4, interval=1, privileged=False)
        if response.is_alive:
            return response.avg_rtt, response.packet_loss
        else:
            return None, None
    except requests.exceptions.RequestException:
        return None, None


def get_http(server_url):
    """
    Get the HTTP response code of a server

    Arguments: url (string)
    Returns: HTTP response code (integer)
    """

    parsed_url = urlparse(server_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return None

    try:
        response = requests.get(f"{server_url}", timeout=1)
        return response.status_code
    except requests.exceptions.RequestException:
        return None


def monitor(file):
    """
    Monitor the status of multiple servers
    """

    with open(file, encoding="utf-8") as f:
        servers = f.read().splitlines()

    if os.stat(file).st_size == 0:
        print(":warning:", "[bold red]No servers found in hosts.txt[/bold red]")
        return
    
    table = Table(title="CLI Status", show_header=True, header_style="bold green")
    table.add_column("🌐 Hostname", justify="center", style="cyan", width=30)
    table.add_column("📶 Ping", justify="center", style="green", width=12)
    table.add_column("📉 Packet Loss", justify="center", style="red", width=12)
    table.add_column("🕸️ HTTP", justify="center", style="yellow", width=12)
    
    for server in servers:
        # add async support
        latency = get_ping(server)
        http = get_http(server)

        ping_val = str(latency['ping']) + " ms" if 'ping' in latency and latency['ping'] else "Error"
        packet_loss = str(latency['packet_loss']) + "%" if 'packet_loss' in latency and latency['packet_loss'] else "Error"
        status_code = str(http) if http is not None else "Error"

        table.add_row(server, ping_val, packet_loss, status_code)

        console.print(table)

def main():
    parser = argparse.ArgumentParser(description="cli status v1")
    parser.add_argument("-f", "--file", help="Path to the hostname file")

    args = parser.parse_args()
    monitor(args.file)

if __name__ == "__main__":
    console = Console()
    main()
