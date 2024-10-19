import browser_cookie3


def getCookies():
    keyFile = 'C:\\Users\\Ronald\\AppData\\Local\\Google\\Chrome\\User Data\\Local State'
    cookies = browser_cookie3.chrome(domain_name='.tiktok.com', key_file=keyFile)  # Ou browser_cookie3.firefox(), etc., dependendo do navegador
    allCookies = []

    for cookie in cookies:
        if 'developer' not in cookie.__dict__['domain']:
            ck = cookie.__dict__
            ck['secure'] = bool(ck['secure'])
            allCookies.append(ck)

    return allCookies


print(getCookies())