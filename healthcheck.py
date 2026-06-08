import functools
import signal
import threading
import requests
import time
from colorama import Fore, Style, init

init(autoreset=True)

endpoints = [
    {"name": "Gateway", "url": "https://sociounido-gateway.onrender.com/ping"},
    {"name": "MS Club", "url": "https://microservicio-club.onrender.com/ping"},
]

colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

name_to_color = {endpoint["name"]: colors[i % len(colors)] for i, endpoint in enumerate(endpoints)}

def post_to_endpoints(sigterm, name, url):
    """
    Continuously sends POST requests to the given endpoint until the sigterm flag is set.
    """
    color = name_to_color[name]  # Get the color for this name
    while not sigterm.is_set():
        try:
            response = requests.post(url, timeout=5)  # 5-second timeout
            if response.status_code >= 200 and response.status_code < 300:
                print(f"{color}[{name}] | URL: {url} - Status Code: {Fore.GREEN}{response.status_code}")
                time.sleep(30)  
            else: 
                print(f"{color}[{name}] | URL: {url} - Status Code: {Fore.RED}{response.status_code}")
        except requests.RequestException as e:
            print(f"{color}[{name}] | URL: {url} - Failed with error: {e}")
        # sleep to prevent spamming
        time.sleep(10)  

def sigterm_handler(sigterm):
    """
    Signal handler to set the sigterm event.
    """
    print(Fore.RED + "SIGTERM received, stopping threads...")
    sigterm.set()

def main():
    sigterm = threading.Event()
    signal.signal(signal.SIGTERM, functools.partial(sigterm_handler, sigterm=sigterm))

    threads = []
    for endpoint in endpoints:
        thread = threading.Thread(
            target=post_to_endpoints, args=(sigterm, endpoint["name"], endpoint["url"])
        )
        threads.append(thread)
        thread.start()

    try:
        # Keep the main thread alive to catch SIGTERM
        while not sigterm.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "KeyboardInterrupt received, stopping threads...")
        sigterm.set()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()