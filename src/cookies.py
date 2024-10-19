import browser_cookie3
import time
from utils import pressCombination


def getCookies():
    cookies = browser_cookie3.chrome(domain_name='.tiktok.com')
    allCookies = []

    for cookie in cookies:
        if 'developer' not in cookie.__dict__['domain']:
            ck = cookie.__dict__
            ck['secure'] = bool(ck['secure'])
            allCookies.append(ck)

    return allCookies


def initWithCookies(driver, espera):
    myCookies = getCookies()
    driver.get('https://www.tiktok.com')
    time.sleep(espera)
    for cookie in myCookies:
        driver.add_cookie(cookie)


def reloadCookies(driver):
    driver.delete_all_cookies()
    pressCombination()
    newCookies = getCookies()
    for cookie in newCookies:
        driver.add_cookie(cookie)
