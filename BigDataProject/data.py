import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import json
import requests

#한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """데이터 로드 및 전처리 함수"""
    try:
        #CCTV
        try:
            cctv_df = pd.read_csv("CCTV.csv", encoding='utf-8-sig')
            print("CCTV.csv 로드 성공 (UTF-8-SIG)")
        except UnicodeDecodeError:
            try:
                cctv_df = pd.read_csv("CCTV.csv", encoding='cp949')
                print("CCTV.csv 로드 성공 (CP949)")
            except UnicodeDecodeError:
                cctv_df = pd.read_csv("CCTV.csv", encoding='euc-kr')
                print("CCTV.csv 로드 성공 (EUC-KR)")
    
        #범죄
        try:
            crime_df = pd.read_csv("Crime.csv", encoding='utf-8-sig')
            print("Crime.csv 로드 성공 (UTF-8-SIG)")
        except UnicodeDecodeError:
            try:
                crime_df = pd.read_csv("Crime.csv", encoding='cp949')
                print("Crime.csv 로드 성공 (CP949)")
            except UnicodeDecodeError:
                crime_df = pd.read_csv("Crime.csv", encoding='euc-kr')
                print("Crime.csv 로드 성공 (EUC-KR)")
        
        #부동산
        try:
            estate_df = pd.read_csv("Estate.csv", encoding='utf-8-sig')
            print("Estate.csv 로드 성공 (UTF-8-SIG)")
        except UnicodeDecodeError:
            try:
                estate_df = pd.read_csv("Estate.csv", encoding='cp949')
                print("Estate.csv 로드 성공 (CP949)")
            except UnicodeDecodeError:
                estate_df = pd.read_csv("Estate.csv", encoding='euc-kr')
                print("Estate.csv 로드 성공 (EUC-KR)")
        
        # 인구
        try:
            person_df = pd.read_csv("Person.csv", encoding='utf-8-sig')
            print("Person.csv 로드 성공 (UTF-8-SIG)")
        except UnicodeDecodeError:
            try:
                person_df = pd.read_csv("Person.csv", encoding='cp949')
                print("Person.csv 로드 성공 (CP949)")
            except UnicodeDecodeError:
                person_df = pd.read_csv("Person.csv", encoding='euc-kr')
                print("Person.csv 로드 성공 (EUC-KR)")
        
        return cctv_df, crime_df, estate_df, person_df
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
        return None, None, None, None

def analyze_cctv_per_capita(cctv_df, person_df):
    """인구 1,000명당 CCTV 비율 분석"""
    #인구 전처리
    person_by_district = person_df[person_df['동별(2)'] != '소계'].copy()
    person_by_district = person_by_district[person_by_district['동별(2)'] != '동별(2)'].copy()
    person_by_district.rename(columns={'동별(2)': '구', '계 (명)': '총인구'}, inplace=True)
    person_by_district['총인구'] = pd.to_numeric(person_by_district['총인구'].str.replace(',', ''), errors='coerce')
    
    #CCTV와 인구 병합
    cctv_population = pd.merge(cctv_df, person_by_district[['구', '총인구']], on='구', how='inner')
    
    #인구 1000명당 CCTV 비율
    cctv_population['인구천명당CCTV'] = (cctv_population['카메라대수'] / (cctv_population['총인구'] / 1000)).round(2)
    
    #결과 시각화
    plt.figure(figsize=(12, 6))
    sns.barplot(data=cctv_population.sort_values('인구천명당CCTV', ascending=False),
                x='구', y='인구천명당CCTV', palette='viridis')
    plt.title('서울 자치구별 인구 1,000명당 CCTV 설치 수')
    plt.xlabel('자치구')
    plt.ylabel('인구 1,000명당 CCTV 수')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
    return cctv_population

def analyze_estate_prices(estate_df):
    """부동산 실거래가 분석"""
    #부동산 가격 전처리
    estate_df['물건금액(만원)'] = pd.to_numeric(estate_df['물건금액(만원)'].astype(str).str.replace(',', ''), errors='coerce')
    
    #구별 평균가와 중위가 계산
    estate_analysis = estate_df.groupby('자치구명').agg({
        '물건금액(만원)': ['mean', 'median']
    }).round(0)
    
    estate_analysis.columns = ['평균가', '중위가']
    estate_analysis = estate_analysis.sort_values('중위가', ascending=False)
    
    #결과 시각화
    plt.figure(figsize=(12, 6))
    estate_analysis.plot(kind='bar', figsize=(12, 6))
    plt.title('서울 자치구별 아파트 평균가/중위가')
    plt.xlabel('자치구')
    plt.ylabel('가격 (만원)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(['평균가', '중위가'])
    plt.tight_layout()
    plt.show()
    
    return estate_analysis

def analyze_crime_by_type(crime_df, person_df):
    """범죄 유형별 분석"""
    #범죄 전처리
    crime_by_district = crime_df.set_index('범죄대분류').T
    crime_by_district.reset_index(inplace=True)
    crime_by_district.rename(columns={'index': '구'}, inplace=True)
    
    #범죄 유형별 총계 계산
    crime_types = crime_by_district.columns[1:]  # '구' 컬럼 제외
    crime_summary = crime_by_district[crime_types].sum().sort_values(ascending=False)
    
    #각 구의 총 범죄수 계산
    crime_by_district['총범죄수'] = crime_by_district[crime_types].sum(axis=1)
    
    #인구 데이터 전처리
    person_by_district = person_df[person_df['동별(2)'] != '소계'].copy()
    person_by_district = person_by_district[person_by_district['동별(2)'] != '동별(2)'].copy()
    person_by_district.rename(columns={'동별(2)': '구', '계 (명)': '총인구'}, inplace=True)
    person_by_district['총인구'] = pd.to_numeric(person_by_district['총인구'].str.replace(',', ''), errors='coerce')
    
    #범죄 데이터와 인구 데이터 병합
    crime_population = pd.merge(crime_by_district, person_by_district[['구', '총인구']], on='구', how='inner')
    
    #인구 1000명당 범죄율 계산
    crime_population['인구천명당범죄수'] = (crime_population['총범죄수'] / (crime_population['총인구'] / 1000)).round(2)
    
    #결과 시각화
    plt.figure(figsize=(12, 6))
    crime_summary.plot(kind='bar')
    plt.title('범죄 유형별 발생 건수')
    plt.xlabel('범죄 유형')
    plt.ylabel('발생 건수')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
    #구별 총 범죄수 시각화
    plt.figure(figsize=(12, 6))
    crime_by_district.sort_values('총범죄수', ascending=False).plot(
        x='구', y='총범죄수', kind='bar'
    )
    plt.title('자치구별 총 범죄 발생 건수')
    plt.xlabel('자치구')
    plt.ylabel('총 범죄 건수')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
    #인구 1000명당 범죄율 시각화
    plt.figure(figsize=(12, 6))
    crime_population.sort_values('인구천명당범죄수', ascending=False).plot(
        x='구', y='인구천명당범죄수', kind='bar'
    )
    plt.title('자치구별 인구 1,000명당 범죄 발생 건수')
    plt.xlabel('자치구')
    plt.ylabel('인구 1,000명당 범죄 건수')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
    return crime_population

def analyze_foreigner_ratio(person_df):
    """외국인 비율 분석"""
    #인구 데이터 전처리
    person_by_district = person_df[person_df['동별(2)'] != '소계'].copy()
    person_by_district = person_by_district[person_by_district['동별(2)'] != '동별(2)'].copy()
    
    #컬럼명 변경, 숫자형 변환
    person_by_district.rename(columns={
        '동별(2)': '구',
        '계 (명)': '총인구',
        '등록외국인 (명)': '외국인수'
    }, inplace=True)
    
    person_by_district['총인구'] = pd.to_numeric(person_by_district['총인구'].str.replace(',', ''), errors='coerce')
    person_by_district['외국인수'] = pd.to_numeric(person_by_district['외국인수'].str.replace(',', ''), errors='coerce')
    
    #외국인 비율 계산
    person_by_district['외국인비율'] = (person_by_district['외국인수'] / person_by_district['총인구'] * 100).round(2)
    
    #결과 시각화
    plt.figure(figsize=(12, 6))
    sns.barplot(data=person_by_district.sort_values('외국인비율', ascending=False),
                x='구', y='외국인비율', palette='viridis')
    plt.title('서울 자치구별 외국인 비율')
    plt.xlabel('자치구')
    plt.ylabel('외국인 비율 (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
    return person_by_district

def analyze_all_indicators(cctv_df, crime_df, estate_df, person_df):
    """모든 지표를 비교하는 히트맵 분석"""
    #CCTV 전처리
    cctv_by_district = cctv_df.copy()
    
    # 범죄 전처리
    crime_by_district = crime_df.set_index('범죄대분류').T
    crime_by_district.reset_index(inplace=True)
    crime_by_district.rename(columns={'index': '구'}, inplace=True)
    crime_types = crime_by_district.columns[1:]
    crime_by_district['총범죄수'] = crime_by_district[crime_types].sum(axis=1)
    
    # 부동산 전처리
    estate_df['물건금액(만원)'] = pd.to_numeric(estate_df['물건금액(만원)'].astype(str).str.replace(',', ''), errors='coerce')
    estate_by_district = estate_df.groupby('자치구명')['물건금액(만원)'].mean().reset_index()
    estate_by_district.rename(columns={'자치구명': '구'}, inplace=True)
    
    # 인구 전처리
    person_by_district = person_df[person_df['동별(2)'] != '소계'].copy()
    person_by_district = person_by_district[person_by_district['동별(2)'] != '동별(2)'].copy()
    person_by_district.rename(columns={
        '동별(2)': '구',
        '계 (명)': '총인구',
        '등록외국인 (명)': '외국인수'
    }, inplace=True)
    person_by_district['총인구'] = pd.to_numeric(person_by_district['총인구'].str.replace(',', ''), errors='coerce')
    person_by_district['외국인수'] = pd.to_numeric(person_by_district['외국인수'].str.replace(',', ''), errors='coerce')
    person_by_district['외국인비율'] = (person_by_district['외국인수'] / person_by_district['총인구'] * 100).round(2)
    
    #모든 데이터 병합
    merged_data = pd.merge(cctv_by_district, crime_by_district[['구', '총범죄수']], on='구', how='inner')
    merged_data = pd.merge(merged_data, estate_by_district, on='구', how='inner')
    merged_data = pd.merge(merged_data, person_by_district[['구', '총인구', '외국인비율']], on='구', how='inner')
    
    #인구 1000명당 지표 계산
    merged_data['인구천명당CCTV'] = (merged_data['카메라대수'] / (merged_data['총인구'] / 1000)).round(2)
    merged_data['인구천명당범죄수'] = (merged_data['총범죄수'] / (merged_data['총인구'] / 1000)).round(2)
    
    #범죄율과 부동산 가격의 산점도
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=merged_data, 
                   x='물건금액(만원)', 
                   y='인구천명당범죄수',
                   s=100)
    
    #구 이름 라벨 추가
    for i in range(len(merged_data)):
        plt.text(merged_data['물건금액(만원)'].iloc[i] * 1.01,
                merged_data['인구천명당범죄수'].iloc[i],
                merged_data['구'].iloc[i],
                fontsize=9)
    
    plt.title('서울시 자치구별 범죄율과 부동산 가격의 관계')
    plt.xlabel('평균 부동산 가격 (만원)')
    plt.ylabel('인구 1,000명당 범죄 발생 건수')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    return merged_data

def get_district_centers():
    """서울시 자치구 중심 좌표 반환"""
    #서울시 자치구 중심 좌표 (위도, 경도)
    district_centers = {
        '강남구': [37.517305, 127.047502],
        '강동구': [37.549207, 127.145482],
        '강북구': [37.639604, 127.025653],
        '강서구': [37.550966, 126.849532],
        '관악구': [37.478406, 126.951613],
        '광진구': [37.538484, 127.082293],
        '구로구': [37.495485, 126.887369],
        '금천구': [37.456455, 126.895310],
        '노원구': [37.654359, 127.056473],
        '도봉구': [37.668773, 127.047152],
        '동대문구': [37.574397, 127.039550],
        '동작구': [37.512402, 126.939252],
        '마포구': [37.563341, 126.908287],
        '서대문구': [37.579116, 126.936778],
        '서초구': [37.483664, 127.032411],
        '성동구': [37.563341, 127.036848],
        '성북구': [37.589116, 127.016778],
        '송파구': [37.514402, 127.106252],
        '양천구': [37.517305, 126.866502],
        '영등포구': [37.526402, 126.896252],
        '용산구': [37.538484, 126.977293],
        '은평구': [37.602484, 126.929293],
        '종로구': [37.572484, 126.977293],
        '중구': [37.564484, 126.997293],
        '중랑구': [37.606484, 127.092293]
    }
    return district_centers

def visualize_crime_cctv_map(crime_df, cctv_df, person_df):
    """범죄 다발 지역과 외국인 비율을 지도에 시각화"""
    #범죄 데이터 전처리
    crime_by_district = crime_df.set_index('범죄대분류').T
    crime_by_district.reset_index(inplace=True)
    crime_by_district.rename(columns={'index': '구'}, inplace=True)
    crime_types = crime_by_district.columns[1:]
    crime_by_district['총범죄수'] = crime_by_district[crime_types].sum(axis=1)
    
    #인구 데이터 전처리
    person_by_district = person_df[person_df['동별(2)'] != '소계'].copy()
    person_by_district = person_by_district[person_by_district['동별(2)'] != '동별(2)'].copy()
    person_by_district.rename(columns={
        '동별(2)': '구',
        '계 (명)': '총인구',
        '등록외국인 (명)': '외국인수'
    }, inplace=True)
    person_by_district['총인구'] = pd.to_numeric(person_by_district['총인구'].str.replace(',', ''), errors='coerce')
    person_by_district['외국인수'] = pd.to_numeric(person_by_district['외국인수'].str.replace(',', ''), errors='coerce')
    person_by_district['외국인비율'] = (person_by_district['외국인수'] / person_by_district['총인구'] * 100).round(2)
    
    #범죄율 계산
    crime_rate = pd.merge(crime_by_district[['구', '총범죄수']], 
                         person_by_district[['구', '총인구', '외국인비율']], 
                         on='구', 
                         how='inner')
    crime_rate['인구천명당범죄수'] = (crime_rate['총범죄수'] / (crime_rate['총인구'] / 1000)).round(2)
    
    #자치구 중심 좌표 가져오기
    district_centers = get_district_centers()
    
    #서울시 중심 좌표로 지도 생성
    seoul_map = folium.Map(location=[37.5665, 126.9780], 
                          zoom_start=11,
                          tiles='CartoDB positron')
    
    # 범죄율에 따른 히트맵 데이터 생성
    heat_data = []
    for _, row in crime_rate.iterrows():
        if row['구'] in district_centers:
            lat, lon = district_centers[row['구']]
            # 범죄율을 가중치로 사용
            weight = row['인구천명당범죄수']
            heat_data.append([lat, lon, weight])
    
    #히트맵 레이어 추가 (투명도)
    HeatMap(heat_data,
            radius=20,  # 반경 증가
            blur=15,    # 블러 증가
            max_zoom=1,
            min_opacity=0.6,  # 최소 투명도 증가
            max_opacity=1.0,  # 최대 투명도 증가
            gradient={0.3: 'blue', 0.5: 'lime', 0.7: 'yellow', 1: 'red'}).add_to(seoul_map)
    
    #외국인 비율 정보를 팝업으로 표시
    for _, row in crime_rate.iterrows():
        if row['구'] in district_centers:
            lat, lon = district_centers[row['구']]
            #외국인 비율에 따라 원의 크기 조정
            circle_radius = 5 + (row['외국인비율'] * 2)  # 외국인 비율이 높을수록 원이 커짐
            
            folium.Popup(
                f"{row['구']}<br>"
                f"총 범죄수: {row['총범죄수']}건<br>"
                f"인구 1,000명당 범죄수: {row['인구천명당범죄수']}건<br>"
                f"외국인 비율: {row['외국인비율']}%",
                max_width=300
            ).add_to(folium.CircleMarker(
                location=[lat, lon],
                radius=circle_radius,
                color='purple',
                fill=False,  # 색 채우기 제거
                weight=2     # 테두리 두께 증가
            ).add_to(seoul_map))
    
    # 범례 추가
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white;
                padding: 10px;
                ">
    <p><strong>범례</strong></p>
    <p><span style="color: red;">■</span> 범죄 발생 (색이 진할수록 범죄율 높음)</p>
    <p><span style="color: purple;">○</span> 외국인 비율 (원이 클수록 외국인 비율 높음)</p>
    </div>
    '''
    seoul_map.get_root().html.add_child(folium.Element(legend_html))
    
    seoul_map.save('seoul_crime_foreigner_map.html')
    print("\n지도가 'seoul_crime_foreigner_map.html' 파일로 저장되었습니다.")

def main():
    """메인 함수"""
    cctv_df, crime_df, estate_df, person_df = load_data()
    
    if any(df is None for df in [cctv_df, crime_df, estate_df, person_df]):
        print("일부 데이터를 로드하지 못했습니다. 프로그램을 종료합니다.")
        return
    
    print("\n=== 범죄율과 부동산 가격의 관계 분석 ===")
    all_indicators = analyze_all_indicators(cctv_df, crime_df, estate_df, person_df)
    print("\n범죄율과 부동산 가격의 관계를 산점도로 확인했습니다.")
    
    print("\n=== 범죄 다발 지역과 외국인 비율을 지도에 시각화 ===")
    visualize_crime_cctv_map(crime_df, cctv_df, person_df)

if __name__ == "__main__":
    main()

