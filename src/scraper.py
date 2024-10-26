import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import JavascriptException
import json
from utils import convertTimestamp, isMoreRecent
from table import createTableFromDict
import threading
import queue
from candidatos import candidatos


esperas = {
    'video': .3,
    'foto': .55,
    'pagina': 3,
    'cookie-page': .5
}


# Scraping

def createOptimizedChromeDriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--mute-audio")
    driver = webdriver.Chrome(options=chrome_options)

    return driver


def getPostedDateFromPost(postUrl, driver):
    previousDriver = driver.current_window_handle
    driver.execute_script("window.open('https://www.google.com', '_blank');")
    allWindows = driver.window_handles
    driver.switch_to.window(allWindows[1])
    print(f"Buscando data da postagem {postUrl}")
    postInfo = getVideoItemStruct(postUrl, driver) if 'video' in postUrl else getPhotoItemStruct(postUrl, driver)
    driver.close()
    driver.switch_to.window(previousDriver)
    postedTimestamp = postInfo['createTime']
    print(f"Data da postagem {postUrl}: {convertTimestamp(postedTimestamp)}")

    return postedTimestamp


def getNonPinnedPosts(driver):
    allPostDivs = driver.find_elements(By.CLASS_NAME, 'e19c29qe17')
    linkElements = [i.find_element(By.TAG_NAME, 'a') for i in allPostDivs]
    linkElements = [i for i in linkElements if len(i.find_elements(By.XPATH, './div')) < 2]
    links = [i.get_attribute('href') for i in linkElements]

    return links


def getPostsLinksFromUser(userUrl, driver):
    print(f'Buscando postagens de {userUrl}')

    driver.get(userUrl)
    time.sleep(esperas['pagina'])
    links = getNonPinnedPosts(driver)
    linksAmount = len(links)
    print(f"{linksAmount} nao filtrados encontrados")

    if len(links) > 0:
        while isMoreRecent(getPostedDateFromPost(links[-1], driver), '1723766400'):
            driver.execute_script("window.scrollTo(window.scrollY, document.body.scrollHeight);")
            time.sleep(1.25)
            driver.execute_script("window.scrollTo(window.scrollY, document.body.scrollHeight);")
            time.sleep(1.25)
            driver.execute_script("window.scrollTo(window.scrollY, window.scrollY - 100);")
            driver.execute_script("window.scrollTo(window.scrollY, document.body.scrollHeight);")
            time.sleep(1.25)
            links = getNonPinnedPosts(driver)

            if len(links) == linksAmount:
                print("Todas as postagens desse usuario sao mais recentes que o timestamp definido")
                break

            linksAmount = len(links)
            print(f"{linksAmount} nao filtrados encontrados")

    return links


def getPostInfoFromItemStruct(itemStruct):
    postInfo = {
        "date": convertTimestamp(itemStruct["createTime"]),
        "timestamp": str(itemStruct["createTime"]),
        "likes": itemStruct['statsV2']['diggCount'],
        "comments": itemStruct['statsV2']['commentCount'],
        "shares": itemStruct['statsV2']['shareCount'],
        "playCount": itemStruct['statsV2']['playCount'],
        "saves": itemStruct['statsV2']['collectCount'],
        "duration": str(itemStruct['video']['duration']),
        "tags": [tag['title'] for tag in itemStruct.setdefault('challenges', [])],
    }

    return postInfo


def getVideoItemStruct(videoUrl, driver):
    print(f"Buscando video {videoUrl}")
    driver.get(videoUrl)
    time.sleep(esperas['video'])
    try:
        scriptTag = json.loads(
            driver.find_element(By.ID, '__UNIVERSAL_DATA_FOR_REHYDRATION__').get_attribute('innerHTML')
        )
        videoInfo = scriptTag['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
    except KeyError:
        print(f"Objeto de informacoes da postagem nao encontrado no html da url: {videoUrl}")
        print("Tentando novamente...")
        videoInfo = getVideoItemStruct(videoUrl, driver)

    return videoInfo


def getPhotoItemStruct(photoUrl, driver):
    print(f"Buscando foto {photoUrl}")
    driver.get(photoUrl)
    time.sleep(esperas['foto'])

    try:
        photoInfoUrl = driver.execute_script("return performance.getEntriesByType('resource')"
                                             ".filter(a => a.name.includes('detail'))[0].name;")
        photoInfo = driver.execute_script("return fetch(arguments[0]).then(response => response.json())"
                                          ".then(data => data['itemInfo']['itemStruct']);", photoInfoUrl)

    except JavascriptException:
        print(f"Erro ao tentar obter as infos da foto {photoUrl}")
        photoInfo = getPhotoItemStruct(photoUrl, driver)

    return photoInfo


def getPostStats(postUrl, driver):
    if 'video' in postUrl:
        info = getVideoItemStruct(postUrl, driver)

    else:
        info = getPhotoItemStruct(postUrl, driver)

    essentialInfo = getPostInfoFromItemStruct(info)
    essentialInfo['link'] = postUrl

    return essentialInfo


def getStatsFromUserThreaded(tiktokProfileUrl, cookies):
    driver = createOptimizedChromeDriver()
    driver.get('https://tiktok.com')
    time.sleep(.75)
    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.get(tiktokProfileUrl)

    postsLinks = getPostsLinksFromUser(tiktokProfileUrl, driver)

    newCookies = driver.get_cookies()
    driver.quit()

    midIndex = len(postsLinks) // 2
    outputQueue = queue.Queue()

    postsLinks1 = postsLinks[:midIndex]
    postsLinks2 = postsLinks[midIndex:]

    thread1 = threading.Thread(target=getPostsStatsFromUser, args=(postsLinks1, cookies, outputQueue))
    thread2 = threading.Thread(target=getPostsStatsFromUser, args=(postsLinks2, cookies, outputQueue))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    posts = []

    while not outputQueue.empty():
        posts.append(outputQueue.get())

    sortedData = sorted(posts[0] + posts[1], key=lambda x: int(x['timestamp']), reverse=True)
    print(f"\n/----------------------/\nO perfil {tiktokProfileUrl.split('/')[-1]} possui {len(sortedData)} postagens\n"
          f"e a mais antiga eh da data: {sortedData[-1]['date']} e a mais recente eh da data: {sortedData[0]['date']}")
    print("\n/----------------------/\n")
    return {'posts': sortedData, 'cookies': newCookies}


def getPostsStatsFromUser(postsLinks, cookies, output):
    driver = createOptimizedChromeDriver()
    driver.get('https://www.tiktok.com')
    time.sleep(.75)
    for cookie in cookies:
        driver.add_cookie(cookie)

    postsStats = []
    counter = 1

    for link in postsLinks:
        post = getPostStats(link, driver)
        if not isMoreRecent(post['timestamp'], 1723766400):
            break

        postsStats.append(post)
        print(counter, ' - ', post)
        counter += 1

    output.put(postsStats)

    driver.quit()


meuDriver = webdriver.Chrome()
meuDriver.get('https://www.tiktok.com/@guilhermeboulos')
input('calma')
meusCookies = meuDriver.get_cookies()
meuDriver.quit()

for candidato in [c for c in candidatos['goiania'] if c['tiktok']]:
    retornoCandidato = getStatsFromUserThreaded(candidato['tiktok'], meusCookies)
    postCandidato = retornoCandidato['posts']
    novosCookies = retornoCandidato['cookies']
    meusCookies = novosCookies
    createTableFromDict(candidato['nome'], postCandidato)
