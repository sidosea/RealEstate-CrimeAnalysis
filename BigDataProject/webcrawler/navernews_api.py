import os
import sys
import urllib.request
import datetime
import json
from dotenv import load_dotenv

load_dotenv()
#네이버 API
client_id = os.getenv("NAVER_ID")
client_secret = os.getenv("NAVER_SECRET")

#검색어
SEARCH_QUERY = "서울 치안"

#제목/본문에 필터링할 키워드
KEYWORDS = ["치안", "범죄", "안전", "강력범죄", "CCTV", "사건", "우범", "도난", "강도","마약"]

def getRequestUrl(url):
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print("[%s] Url Request Success" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e:
        print(e)
        print("[%s] Error for URL: %s" % (datetime.datetime.now(), url))
        return None

def getNaverSearch(node, srcText, start, display):
    base = "https://openapi.naver.com/v1/search"
    node = f"/{node}.json"
    parameters = f"?query={urllib.parse.quote(srcText)}&start={start}&display={display}"

    url = base + node + parameters
    responseDecode = getRequestUrl(url)

    if responseDecode is None:
        return None
    else:
        return json.loads(responseDecode)

def getPostData(post, jsonResult, cnt):
    title = post['title']
    description = post['description']

    #제목이나 본문에 키워드 포함 여부
    if not any(keyword in title or keyword in description for keyword in KEYWORDS):
        return

    org_link = post['originallink']
    link = post['link']
    pDate = datetime.datetime.strptime(post['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
    pDate = pDate.strftime('%Y-%m-%d %H:%M:%S')

    jsonResult.append({
        'cnt': cnt,
        'title': title,
        'description': description,
        'org_link': org_link,
        'link': link,
        'pDate': pDate
    })

def main():
    node = 'news'
    cnt = 0
    jsonResult = []

    print(f"[INFO] 검색어: {SEARCH_QUERY}")
    jsonResponse = getNaverSearch(node, SEARCH_QUERY, 1, 100)

    if jsonResponse is None:
        print("API 호출에 실패했습니다.")
        return

    total = jsonResponse['total']

    while jsonResponse is not None and jsonResponse['display'] != 0:
        for post in jsonResponse['items']:
            cnt += 1
            getPostData(post, jsonResult, cnt)

        start = jsonResponse['start'] + jsonResponse['display']
        if start > 1000:  # API 최대 검색 제한
            break
        jsonResponse = getNaverSearch(node, SEARCH_QUERY, start, 100)

    print(f'전체 검색 : {total} 건')
    print(f'필터링 후 저장된 데이터 : {len(jsonResult)} 건')

    filename = f"{SEARCH_QUERY}_filtered_news.json"
    with open(filename, 'w', encoding='utf-8') as outfile:
        jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(jsonFile)

    print(f'{filename} 저장 완료')

if __name__ == '__main__':
    main()


