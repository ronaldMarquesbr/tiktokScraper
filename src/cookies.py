import browser_cookie3
import time


def getCookies():
    cookies = browser_cookie3.chrome(domain_name='.tiktok.com')
    allCookies = []

    for cookie in cookies:
        if 'developer' not in cookie.__dict__['domain']:
            ck = cookie.__dict__
            ck['secure'] = bool(ck['secure'])
            allCookies.append(ck)

    return allCookies


def initWithCookies(driver, waitingTime):
    myCookies = getCookies()
    driver.get('https://www.tiktok.com')
    time.sleep(waitingTime)
    for cookie in myCookies:
        driver.add_cookie(cookie)
