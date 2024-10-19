import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import table
from utils import convertTimestamp, isMoreRecent
from cookies import reloadCookies, initWithCookies
from candidatos import saoPaulo


esperas = {
    'video': .3,
    'foto': 1.5,
    'pagina': 2,
    'cookie-page': .5
}


# Scraping


def getVideoLinksFromUser(userUrl, driver):
    driver.get(userUrl)
    time.sleep(esperas['pagina'])
    postsDiv = driver.find_elements(By.CLASS_NAME, 'e19c29qe8')
    linkElements = [i.find_element(By.TAG_NAME, 'a') for i in postsDiv]
    linkElements = [i for i in linkElements if len(i.find_elements(By.XPATH, './div')) < 2]
    links = [i.get_attribute('href') for i in linkElements]

    return links


def updateLinksFromUser(userUrl, times, driver):
    driver.get(userUrl)
    time.sleep(esperas['pagina'])
    for _ in range(times):
        driver.execute_script("window.scrollTo(window.scrollY, document.body.scrollHeight);")
        time.sleep(esperas['pagina'])
    postsDiv = driver.find_elements(By.CLASS_NAME, 'e19c29qe8')
    links = [i.find_element(By.TAG_NAME, 'a').get_attribute('href') for i in postsDiv]

    return links


def getVideoStats(videoUrl, count, driver):
    driver.get(videoUrl)
    time.sleep(esperas['video'])
    try:
        scriptTag = json.loads(
            driver.find_element(By.ID, '__UNIVERSAL_DATA_FOR_REHYDRATION__').get_attribute('innerHTML'))
        videoInfo = scriptTag['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
        duration = videoInfo['video']['duration']
        postedDate = {
            "timestamp": videoInfo['createTime'],
            "date": convertTimestamp(videoInfo['createTime'])
        }

        if not isMoreRecent(postedDate['timestamp'], '1723766400') and count > 2:
            return {'code': 1}

        stats = videoInfo['stats']
        tags = [t['title'] for t in videoInfo['challenges']]
        metadata = {
            "author": scriptTag['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']['author'][
                'nickname'],
            "date": postedDate["date"],
            "timestamp": postedDate["timestamp"],
            "likes": stats['diggCount'],
            "comments": stats['commentCount'],
            "shares": stats['shareCount'],
            "playCount": stats['playCount'],
            "saves": stats['collectCount'],
            "duration": duration,
            "tags": tags,
            "link": videoUrl
        }

        return metadata

    except KeyError as e:
        return tryAgain(videoUrl, count, e, driver)

    except NoSuchElementException as e:
        return tryAgain(videoUrl, count, e, driver)


def getPhotoStats(photoUrl, driver):
    driver.get(photoUrl)
    time.sleep(esperas['foto'])

    likes = driver.find_element(By.CSS_SELECTOR, "[data-e2e='like-count']").text
    comments = driver.find_element(By.CSS_SELECTOR, "[data-e2e='comment-count']").text
    shares = driver.find_element(By.CSS_SELECTOR, "[data-e2e='share-count']").text
    saves = driver.find_element(By.CSS_SELECTOR, "[data-e2e='undefined-count']").text
    profileElement = driver.find_element(By.CSS_SELECTOR, "[data-e2e='browser-nickname']")
    spanInProfileElement = profileElement.find_elements(By.TAG_NAME, 'span')
    author = spanInProfileElement[0].text
    relativeDate = spanInProfileElement[-1].text
    tags = driver.find_element(By.CSS_SELECTOR, "[data-e2e='browse-video-desc']").text.replace("\n", '')
    metadata = {
        "author": author,
        "date": relativeDate,
        "timestamp": 'n/a',
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "playCount": 'n/a',
        "saves": saves,
        "duration": 'n/a',
        "tags": tags,
        "link": photoUrl
    }

    return metadata


def getPostStats(url, count, driver):
    if 'video' in url:
        info = getVideoStats(url, count, driver)

        if not info:
            info = getVideoStats(url, count, driver)
    else:
        info = getPhotoStats(url, driver)

    return info


def tryAgain(url, count, e, driver):
    print(e)
    html = driver.page_source
    with open(f'{url.split('/')[-1]}.html', 'w', encoding='utf-8') as file:
        file.write(html)
    print('Tentando de novo em ...')
    for i in range(1, 6):
        print(f"{i}...")
        time.sleep(1)

    return getVideoStats(url, count, driver)


def getPostStatsFromUser(userUrl, driver):
    links = getVideoLinksFromUser(userUrl, driver)

    if len(links) > 0:
        counter = 0
        lent = len(links)
        ts = 0

        while counter < lent:
            if counter % 5 == 0:
                reloadCookies(driver)

            info = getPostStats(links[counter], counter, driver)

            print(links[counter], ' : ', info)

            if 'code' in info:
                break

            if counter == 0:
                table.createHeader(links[counter])

            table.createRow(info)
            counter += 1

            if counter == lent:
                ts += 1
                links = updateLinksFromUser(userUrl, ts, driver)
                lent = len(links)

    else:
        print('Nenhum link encontrado!')
        initWithCookies(driver, esperas['cookie-page'])
        getPostStatsFromUser(userUrl, driver)


def getMultPostStatsFromUsers(users):
    driver = webdriver.Chrome()
    initWithCookies(driver, esperas['cookie-page'])

    for user in users:
        getPostStatsFromUser(user, driver)

    driver.quit()


sp = [cand['tiktok'] for cand in saoPaulo if cand['tiktok']]
print(sp)
# getMultPostStatsFromUsers(sp)
