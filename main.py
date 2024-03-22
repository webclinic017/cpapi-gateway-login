from selenium.webdriver.common.by import By
from selenium import webdriver
import threading
import requests
import argparse
import urllib3
import time
import os


def start_gateway(gateway_root_dir: str):
    os.chdir(gateway_root_dir)
    os.system(".\\bin\\run.bat .\\root\\conf.yaml")


def get_auth_status(port: int = 5000):
    # Don't show SSL warnings in console
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(
        f"https://localhost:{port}/v1/api/iserver/auth/status", verify=False
    )
    return response.json()


def authenticate_user(
    username: str,
    password: str,
    gateway_port: int = 5000,
    headless: bool = True,
):
    webdriver_options = webdriver.EdgeOptions()
    # Gateway uses self-signed certs, ignore warnings related to it
    webdriver_options.add_argument("--ignore-certificate-errors")
    webdriver_options.add_argument("--ignore-ssl-errors")
    webdriver_options.add_argument("--log-level=3")
    if headless:
        webdriver_options.add_argument("--headless")
    with webdriver.Edge(options=webdriver_options) as chrome_driver:
        login_page = f"https://localhost:{gateway_port}"
        chrome_driver.get(login_page)
        # User is redirected to login page on first visit
        while chrome_driver.current_url == login_page:
            time.sleep(0.25)
        current_url = chrome_driver.current_url
        print(f"Logging in as {username}...")
        username_input = chrome_driver.find_element(By.ID, "xyz-field-username")
        username_input.send_keys(username)
        password_input = chrome_driver.find_element(By.ID, "xyz-field-password")
        password_input.send_keys(password)
        submit_button = chrome_driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        # Wait until user is redirected to the login confirmation page
        while chrome_driver.current_url == current_url:
            time.sleep(0.25)
        print("Login successful!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "username",
        help="username for the user to be authenticated",
        type=str,
    )
    parser.add_argument(
        "password",
        help="password for the user to be authenticated",
        type=str,
    )
    parser.add_argument(
        "--path",
        help="relative path to the root gateway directory",
        type=str,
        default=".",
    )
    parser.add_argument(
        "--port",
        help="port on which the gateway is running",
        type=int,
        default=8080,
    )
    parser.add_argument(
        "--headless",
        help="don't open browser window when authenticating the user",
        action="store_true",
        default=False,
    )
    parsed_args = parser.parse_args()
    gateway_thread = threading.Thread(target=start_gateway, args=(parsed_args.path,))
    gateway_thread.start()
    NUM_SECONDS_TO_WAIT_UNTIL_GATEWAY_START = 5
    time.sleep(NUM_SECONDS_TO_WAIT_UNTIL_GATEWAY_START)
    authenticate_user(
        parsed_args.username,
        parsed_args.password,
        parsed_args.port,
        parsed_args.headless,
    )
    auth_status = get_auth_status(port=parsed_args.port)
    print(auth_status)


if __name__ == "__main__":
    main()
