import os
import sys
import urllib.request
import datetime
import time
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
ServiceKey = os.getenv("SERVICE_KEY")

def getRequestUrl(url):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print("[%s] Url Request Success" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e:
        print(e)
        print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))
        return None

def getTourismStatsItem(yyyymm, national_code, ed_cd):
    service_url = 'http://openapi.tour.go.kr/openapi/service/EdrcntTourismStatsService/getEdrcntTourismStatsList'

    parameters = "?_type=json&serviceKey=" + ServiceKey  #인증키
    parameters += "&YM=" + yyyymm
    parameters += "&NAT_CD=" + national_code
    parameters += "&ED_CD=" + ed_cd

    url = service_url + parameters
    print(url)  #액세스 거부 여부 확인용 출력
    retData = getRequestUrl(url) 

    if retData == None:
        return None
    else:
        return json.loads(retData)
def getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear):
    jsonResult = []
    result = []
    for year in range(nStartYear, nEndYear + 1):
        for month in range(1, 13):
            yyyymm = '{0}{1:0>2}'.format(str(year), str(month))
            jsonData = getTourismStatsItem(yyyymm, nat_cd, ed_cd)
            if jsonData['response']['header']['resultMsg'] == 'OK':
                if jsonData['response']['body']['items'] == '':
                    dataEND = '{0}{1:0>2}'.format(str(year), str(month - 1))
                    print("데이터 없음... \n제공되는 통계 데이터는 %s년 %s월까지입니다." %
                          (str(year), str(month - 1)))
                    break
                print(json.dumps(jsonData, indent=4, sort_keys=True, ensure_ascii=False))
                natName = jsonData['response']['body']['items']['item']['natKorNm']
                natName = natName.replace(' ', '')
                num = jsonData['response']['body']['items']['item']['num']
                ed = jsonData['response']['body']['items']['item']['ed']
                print('[%s_%s : %s]' % (natName, yyyymm, num))
                print('----------------------------------------')
                jsonResult.append({'nat_name': natName, 'nat_cd': nat_cd,
                                   'yyyymm': yyyymm, 'visit_cnt': num,
                                   'ed': ed})
        result.append((natName, nat_cd, yyyymm, num))
    return (jsonResult, result, natName, ed, dataEND)

def main():
    jsonResult = []
    result = []

    print("<< 국내 입국한 외국인의 통계 데이터를 수집합니다. >>")
    nat_cd = input("국가 코드를 입력해주세요(중국: 112 / 일본: 130 / 미국: 275): ")
    nStartYear = int(input("몇 년부터?: "))
    nEndYear = int(input("몇 년까지?: "))
    ed_cd = "E"  #E: 방한외래관광객, D: 해외 출국

    jsonResult, result, natName, ed, dataEND = getTourismStatsService(
        nat_cd, ed_cd, nStartYear, nEndYear
    )

    #JSON
    with open('./%s_%s_%d_%s.json' % (natName, ed, nStartYear, dataEND),
              'w', encoding='utf8') as outfile:
        jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(jsonFile)

    #CSV
    columns = ['입국자국가', '국가코드', '입국연월', '입국자 수']
    result_df = pd.DataFrame(result, columns=columns)
    result_df.to_csv('./%s_%s_%d_%s.csv' % (natName, ed, nStartYear, dataEND),
                     index=False, encoding='cp949')

if __name__ == '__main__':
    main()
