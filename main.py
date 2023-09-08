import os
import time
import urllib3
import argparse
import requests
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By


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
    webdriver_options = webdriver.ChromeOptions()
    webdriver_options.add_argument("--ignore-certificate-errors")
    webdriver_options.add_argument("--ignore-ssl-errors")
    webdriver_options.add_argument("--log-level=3")
    if headless:
        webdriver_options.add_argument("--headless")
    with webdriver.Chrome(options=webdriver_options) as chrome_driver:
        login_page = f"https://localhost:{gateway_port}"
        chrome_driver.get(login_page)
        # User is redirected to login page on first visit
        while chrome_driver.current_url == login_page:
            time.sleep(0.25)
        current_url = chrome_driver.current_url
        username_input = chrome_driver.find_element(By.ID, "xyz-field-username")
        username_input.send_keys(username)
        password_input = chrome_driver.find_element(By.ID, "xyz-field-password")
        password_input.send_keys(password)
        submit_button = chrome_driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        # Wait until user is redirected to the login confirmation page
        while chrome_driver.current_url == current_url:
            time.sleep(0.25)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "username",
        help="username for authentication",
        type=str,
    )
    parser.add_argument(
        "password",
        help="password for authentication",
        type=str,
    )
    parser.add_argument(
        "path",
        help="relative path to the root gateway directory",
        type=str,
        default=".",
    )
    parser.add_argument(
        "--port",
        help="port for authentication",
        type=int,
        default=5000,
    )
    parser.add_argument(
        "--headless",
        help="run in headless mode",
        action="store_true",
        default=False,
    )
    gateway_thread = threading.Thread(
        target=start_gateway, args=(parser.parse_args().path,)
    )
    gateway_thread.start()
    NUM_SECONDS_TO_WAIT_UNTIL_GATEWAY_START = 5
    time.sleep(NUM_SECONDS_TO_WAIT_UNTIL_GATEWAY_START)
    authenticate_user(
        parser.parse_args().username,
        parser.parse_args().password,
        parser.parse_args().port,
        parser.parse_args().headless,
    )
    auth_status = get_auth_status()
    print(auth_status)
    gateway_thread.join()


if __name__ == "__main__":
    main()
