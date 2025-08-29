import os
import sys
import urllib.request
import datetime
import time
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
ServiceKey = os.getenv("JAYWALK_KEY")

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

#API 호출
def getPedestrianAccidentData(searchYearCd, siDo, guGun, numOfRows, pageNo, dataType="json"):
    #무단횡단 교통사고 API
    service_url = 'http://apis.data.go.kr/B552061/jaywalking/getRestJaywalking'

    parameters = "?type=" + dataType + "&serviceKey=" + ServiceKey
    parameters += "&searchYearCd=" + str(searchYearCd)
    parameters += "&siDo=" + str(siDo)
    parameters += "&guGun=" + str(guGun)
    parameters += "&numOfRows=" + str(numOfRows)
    parameters += "&pageNo=" + str(pageNo)

    url = service_url + parameters
    print(url)  # 액세스 여부 확인
    retData = getRequestUrl(url)  

    if retData is None:
        return None
    else:
        try:
            return json.loads(retData)
        except json.JSONDecodeError as e:
            print(f"[{datetime.datetime.now()}] JSON 디코딩 오류 발생:")
            print(f"오류 메시지: {e}")
            print(f"수신된 데이터 (일부): {retData[:500]}...") # 처음 500자만 출력 확인
            print("데이터가 JSON 형식이 아니거나 비어있습니다.")
            return None

def main():
    jsonResult = []
    
    print("<< 한국도로교통공단_무단횡단 교통사고 다발지역 정보를 수집합니다. >>")
    searchYearCd = int(input("조회하고자 하는 연도를 입력해주세요 (예: 2015): "))
    siDo_input = input("시도 코드를 입력해주세요 (서울: 11 / 부산: 26 등, '서울' 입력 시 모든 구 조회): ")

    if siDo_input == "11" or siDo_input.lower() == "서울":
        siDo = "11"
        target_guguns = SEOUL_GUGUN_CODES.values() 
        print(f"서울특별시의 모든 구에 대한 데이터를 수집합니다.")
    else:
        siDo = siDo_input
        guGun = input("시군구 코드를 입력해주세요 (해당 시도의 시군구 코드 입력): ")
        target_guguns = [guGun] 

    numOfRows = 100 
    
    for guGun_code in target_guguns:
        print(f"\n--- {siDo} 시도 코드, {guGun_code} 시군구 코드 데이터 수집 중 ---")
        pageNo = 1      

        while True:
            jsonData = getPedestrianAccidentData(searchYearCd, siDo, guGun_code, numOfRows, pageNo)
            
            if jsonData is None:
                print("데이터를 가져오는 중 오류가 발생했습니다. 다음 구로 넘어갑니다.")
                break
            if 'response' in jsonData and 'header' in jsonData['response'] and 'body' in jsonData['response']:
                header = jsonData['response']['header']
                body = jsonData['response']['body']

                resultCode = header.get('resultCode')
                resultMsg = header.get('resultMsg')

                if resultCode == '0000': #API 호출 성공 (데이터가 있을 수도 있고 없을 수도 있음)
                    #totalCount가 0이거나 items.item이 비어있는지 먼저 확인
                    if body.get('totalCount', 0) == 0 or not (body.get('items') and body['items'].get('item')):
                        print(f"{guGun_code} 구에 해당 연도의 데이터가 없습니다.")
                        break #현재 구에 대한 데이터 수집 중단하고 다음 구로 넘어감
                    else:
                        items = body['items']['item']
                        if isinstance(items, dict):
                            items = [items]

                        for item in items:
                            jsonResult.append(item)
                            print(f"지점명: {item.get('spot_nm')}, 발생건수: {item.get('occrrnc_cnt')}, 사상자수: {item.get('caslt_cnt')}")

                        totalCount = body.get('totalCount', 0)
                        if (pageNo * numOfRows) < totalCount:
                            pageNo += 1
                            time.sleep(1)
                        else:
                            print(f"{guGun_code} 구의 모든 데이터를 가져왔습니다.")
                            break
                else: #resultCode가 0000이 아님
                    print(f"API 호출 실패 for {guGun_code} 구: [{resultCode}] {resultMsg}")
                    break
            else:
                print(f"예상치 못한 API 응답 구조입니다 for {guGun_code} 구.")
                print(json.dumps(jsonData, indent=4, ensure_ascii=False))
                break

    if jsonResult:
        filename_json = f'./무단횡단교통사고다발지역_{searchYearCd}_{siDo_input}_전체구.json'
        with open(filename_json, 'w', encoding='utf8') as outfile:
            jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
            outfile.write(jsonFile)
        print(f"\nJSON 파일 저장 완료: {filename_json}")

        columns = [
            'geom_json', 'afos_fid', 'afos_id', 'bjd_cd', 'spot_cd', 
            'sido_sgg_nm', 'spot_nm', 'occrrnc_cnt', 'caslt_cnt', 
            'dth_dnv_cnt', 'se_dnv_cnt', 'sl_dnv_cnt', 'wnd_dnv_cnt', 
            'lo_crd', 'la_crd'
        ]
        result_df = pd.DataFrame(jsonResult)
        result_df = result_df[[col for col in columns if col in result_df.columns]]
        
        filename_csv = f'./무단횡단교통사고다발지역_{searchYearCd}_{siDo_input}_전체구.csv'
        result_df.to_csv(filename_csv, index=False, encoding='cp949')
        print(f"CSV 파일 저장 완료: {filename_csv}")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == '__main__':

    main()
