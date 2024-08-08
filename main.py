import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    ElementClickInterceptedException,
)

import secret

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_experimental_option("detach", True)


class Browser:
    browser, service = None, None

    def __init__(self, driver: str):
        self.service = Service(driver)
        self.browser = webdriver.Chrome(service=self.service, options=chrome_options)

    def open_page(self, url: str):
        self.browser.get(url)
        time.sleep(2)

    def close_browser(self):
        self.browser.quit()

    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((by, value))
        )
        button.click()

    def login(self, username: str, password: str):
        self.add_input(
            by=By.XPATH, value="/html/body/div[3]/form/div[1]/input", text=username
        )
        self.add_input(
            by=By.XPATH, value="/html/body/div[3]/form/div[2]/input", text=password
        )
        self.click_button(by=By.XPATH, value="/html/body/div[3]/form/div[3]/button")
        self.click_button(
            by=By.XPATH, value="/html/body/div[2]/div/div[3]/div/div[1]/div/span[1]/a"
        )

    def click_button_repeatedly(self):
        for _ in range(100000):
            try:
                button1 = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[2]/div[3]/table/tbody/tr[32]/td[6]/form/button[1]",
                        )
                    )
                )

                if button1.is_enabled():
                    print("Successfully clicked DS")
                    button1.click()
                    time.sleep(1)
                else:
                    self.browser.refresh()
                    time.sleep(1.5)
            except ElementClickInterceptedException:
                print("Element click intercepted. Trying again...")
                time.sleep(1)
                continue
            except WebDriverException as e:
                if "ERR_CONNECTION_REFUSED" in str(
                    e
                ) or "ERR_INTERNET_DISCONNECTED" in str(e):
                    print("Connection error detected. Waiting and trying again...")
                    self.close_browser()
                    return False
                print(f"Error clicking button: {e}")
                self.close_browser()
                return False
        return True


if __name__ == "__main__":
    driver_path = "drivers/chromedriver"
    login_url = "http://reg.exam.dtu.ac.in/student/login"

    while True:
        browser = Browser(driver_path)
        try:
            browser.open_page(login_url)
            browser.login(secret.username, secret.password)
            if not browser.click_button_repeatedly():
                print("Restarting the script due to connection error...")
                time.sleep(5)
                continue
        except WebDriverException as e:
            if "ERR_CONNECTION_REFUSED" in str(e) or "ERR_INTERNET_DISCONNECTED" in str(
                e
            ):
                print(
                    "Connection error detected during login. Waiting and trying again..."
                )
                time.sleep(5)
                continue
            print(f"Unexpected error: {e}")
        finally:
            browser.close_browser()
        break
