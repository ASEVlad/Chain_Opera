import os
import time

import requests
import platform
import threading

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


message_lock = threading.Lock()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ProfileManager:
    def __init__(self, profile_id: str, anty_type: str):
        self.profile_id = profile_id
        self.anty_type = anty_type.upper()

    def open_profile(self):
        if self.anty_type == "ADSPOWER":
            self.driver = self.open_ads_power_profile()
        elif self.anty_type == "DOLPHIN":
            self.driver = self.open_dolphin_profile()
        self.driver.set_page_load_timeout(40)

        return self.driver

    def open_ads_power_profile(self):
        start_url = f"http://127.0.0.1:50325/api/v1/browser/start?user_id={self.profile_id}"
        response = requests.get(start_url).json()
        ws_url = response["data"]["ws"]["selenium"]

        options = webdriver.ChromeOptions()
        options.debugger_address = ws_url.replace("ws://", "").replace("/devtools/browser/", "")

        geckodriver_path = self.get_geckodriver_path()
        service = Service(geckodriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def open_dolphin_profile(self):
        start_url = f"http://localhost:3001/v1.0/browser_profiles/{self.profile_id}/start?automation=1"
        response = requests.get(start_url).json()
        port = response["automation"]["port"]

        options = Options()
        options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')

        geckodriver_path = self.get_geckodriver_path()
        service = Service(geckodriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def close_profile(self):
        if self.driver:
            self.driver.close()
            self.driver.quit()

        if self.anty_type == "ADSPOWER":
            stop_url = f"http://127.0.0.1:50325/api/v1/browser/stop?user_id={self.profile_id}"
        elif self.anty_type == "DOLPHIN":
            stop_url = f"http://localhost:3001/v1.0/browser_profiles/{self.profile_id}/stop"

        for _ in range(3):
            requests.get(stop_url)
            time.sleep(5)

        self.driver = None

    def get_geckodriver_path(self):
        system = platform.system()
        architecture = platform.machine()
        driver_path = self.select_driver_executable(system, architecture)

        return driver_path

    def select_driver_executable(self, system: str, architecture: str):

        if system == 'Windows':
            executable_name = 'chromedriver.exe' if '64' in architecture else 'chromedriver_x86.exe'
        elif system == 'Darwin' or (system == 'Linux' and '64' in architecture):
            executable_name = 'chromedriver'
        else:
            raise ValueError("Unsupported operating system or architecture")

        executable_path = os.path.abspath(os.path.join(BASE_DIR, "..", "data", executable_name))

        if system != 'Windows':
            os.chmod(executable_path, 0o755)

        return executable_path