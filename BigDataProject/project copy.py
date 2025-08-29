import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#한글 폰트 설정 (matplotlib에서 한글 깨짐 방지)
plt.rcParams['font.family'] = 'Malgun Gothic' #윈도우 쓸 때
# plt.rcParams['font.family'] = 'AppleGothic' #맥북 쓸 때
plt.rcParams['axes.unicode_minus'] = False #마이너스 기호 깨짐 방지

#데이터 불러오기
#인코딩 문제와 파일 경로 문제 해결 완
try:
    cctv_df = pd.read_csv("CCTV.csv", encoding='utf-8-sig')
    print("CCTV.csv 로드 성공 (UTF-8-SIG)")
except UnicodeDecodeError:
    try:
        cctv_df = pd.read_csv("CCTV.csv", encoding='cp949')
        print("CCTV.csv 로드 성공 (CP949)")
    except UnicodeDecodeError:
        print("CCTV.csv 로드 실패 (CP949), EUC-KR로 재시도...")
        cctv_df = pd.read_csv("CCTV.csv", encoding='euc-kr')
        print("CCTV.csv 로드 성공 (EUC-KR)")
except FileNotFoundError:
    print("Error: CCTV.csv 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"CCTV.csv 로드 중 예상치 못한 오류 발생: {e}")
    exit()

try:
    crime_df = pd.read_csv("Crime.csv", encoding='utf-8-sig')
    print("Crime.csv 로드 성공 (UTF-8-SIG)")
except UnicodeDecodeError:
    try:
        crime_df = pd.read_csv("Crime.csv", encoding='cp949')
        print("Crime.csv 로드 성공 (CP949)")
    except UnicodeDecodeError:
        print("Crime.csv 로드 실패 (CP949), EUC-KR로 재시도...")
        crime_df = pd.read_csv("Crime.csv", encoding='euc-kr')
        print("Crime.csv 로드 성공 (EUC-KR)")
except FileNotFoundError:
    print("Error: Crime.csv 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"Crime.csv 로드 중 예상치 못한 오류 발생: {e}")
    exit()

try:
    estate_df = pd.read_csv("Estate.csv", encoding='utf-8-sig')
    print("Estate.csv 로드 성공 (UTF-8-SIG)")
except UnicodeDecodeError:
    try:
        estate_df = pd.read_csv("Estate.csv", encoding='cp949')
        print("Estate.csv 로드 성공 (CP949)")
    except UnicodeDecodeError:
        print("Estate.csv 로드 실패 (CP949), EUC-KR로 재시도...")
        estate_df = pd.read_csv("Estate.csv", encoding='euc-kr')
        print("Estate.csv 로드 성공 (EUC-KR)")
except FileNotFoundError:
    print("Error: Estate.csv 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"Estate.csv 로드 중 예상치 못한 오류 발생: {e}")
    exit()

try:
    person_df = pd.read_csv("Person.csv", encoding='utf-8-sig')
    print("Person.csv 로드 성공 (UTF-8-SIG)")
except UnicodeDecodeError:
    try:
        person_df = pd.read_csv("Person.csv", encoding='cp949')
        print("Person.csv 로드 성공 (CP949)")
    except UnicodeDecodeError:
        print("Person.csv 로드 실패 (CP949), EUC-KR로 재시도...")
        person_df = pd.read_csv("Person.csv", encoding='euc-kr')
        print("Person.csv 로드 성공 (EUC-KR)")
except FileNotFoundError:
    print("Error: Person.csv 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()
except Exception as e:
    print(f"Person.csv 로드 중 예상치 못한 오류 발생: {e}")
    exit()

#데이터 로드 끝

#각 데이터프레임의 상위 5행 출력 (데이터 로드 확인용)
print("\n--- CCTV DataFrame Head ---")
print(cctv_df.head())
print("\n--- Crime DataFrame Head ---")
print(crime_df.head())
print("\n--- Estate DataFrame Head ---")
print(estate_df.head())
print("\n--- Person DataFrame Head ---")
print(person_df.head())

#지역별 범죄 발생 빈도 분석

print("\n--- 5-1. 지역별 범죄 발생 빈도 분석 ---")

#범죄 전처리
if '범죄대분류' in crime_df.columns:
    #강력범죄, 절도범죄, 폭력범죄만 추출
    violent_types = ['강력범죄', '절도범죄', '폭력범죄']
    if all(v in crime_df['범죄대분류'].values for v in violent_types):
        # 범죄 데이터를 구별로 집계
        crime_selected = crime_df[crime_df['범죄대분류'].isin(violent_types)].copy()
        crime_selected = crime_selected.set_index('범죄대분류')
        crime_selected = crime_selected.T
        crime_selected = crime_selected.iloc[1:]  #첫 행이 자치구명이면, 1행부터 데이터
        crime_selected.index.name = '구'
        crime_selected = crime_selected.astype(float)
        plt.figure(figsize=(14, 7))
        crime_selected.plot(kind='bar', stacked=False, figsize=(14, 7))
        plt.title('자치구별 강력범죄, 절도범죄, 폭력범죄 발생 건수')
        plt.xlabel('자치구')
        plt.ylabel('발생 건수')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='범죄 유형')
        plt.tight_layout()
        plt.show()
    else:
        print("Error: 강력범죄, 절도범죄, 폭력범죄 중 일부가 Crime.csv의 '범죄대분류'에 없습니다.")
else:
    print("Error: '범죄대분류' 컬럼이 Crime.csv에 없습니다. 컬럼명을 확인해주세요.")
    exit()

#부동산 전처리
if '자치구명' in estate_df.columns and '물건금액(만원)' in estate_df.columns:
    #구별 평균 부동산 가격 계산
    estate_by_district = estate_df.groupby('자치구명')['물건금액(만원)'].mean().reset_index()
    estate_by_district.rename(columns={'자치구명': '구'}, inplace=True)
    print("\n--- Estate by District Head ---")
    print(estate_by_district.head())
else:
    print("Error: '자치구명' 또는 '물건금액(만원)' 컬럼이 Estate.csv에 없습니다. 컬럼명을 확인해주세요.")
    exit()

#인구 전처리
if '동별(2)' in person_df.columns and '계 (명)' in person_df.columns and '등록외국인 (명)' in person_df.columns:
    #구별 인구 데이터 추출
    person_by_district = person_df[person_df['동별(2)'] != '소계'].copy()
    person_by_district = person_by_district[person_by_district['동별(2)'] != '동별(2)'].copy()  # 헤더 행 제거
    
    #컬럼명 변경
    person_by_district.rename(columns={
        '동별(2)': '구',
        '계 (명)': '총인구',
        '등록외국인 (명)': '외국인수'
    }, inplace=True)
    
    #숫자형으로 변환
    person_by_district['총인구'] = pd.to_numeric(person_by_district['총인구'].str.replace(',', ''), errors='coerce')
    person_by_district['외국인수'] = pd.to_numeric(person_by_district['외국인수'].str.replace(',', ''), errors='coerce')
    
    #외국인 비율 계산
    person_by_district['외국인비율'] = person_by_district['외국인수'] / person_by_district['총인구'] * 100
    
    print("\n--- Person by District Head ---")
    print(person_by_district[['구', '총인구', '외국인수', '외국인비율']].head())
else:
    print("Error: 필요한 컬럼이 Person.csv에 없습니다. 컬럼명을 확인해주세요.")
    print("현재 컬럼:", person_df.columns.tolist())
    exit()

#병합
#컬럼이 각 데이터프레임에 있는지 확인
if '구' in cctv_df.columns and '구' in estate_by_district.columns and '구' in person_by_district.columns:
    merged_df = pd.merge(cctv_df, estate_by_district, on='구', how='inner')
    merged_df = pd.merge(merged_df, person_by_district[['구', '총인구', '외국인수', '외국인비율']], on='구', how='inner')
    
    # 인구 1만명당 범죄율 계산
    merged_df['인구만명당범죄율'] = merged_df['총범죄수'] / (merged_df['총인구'] / 10000)
    
    print("\n--- Merged DataFrame Head ---")
    print(merged_df.head())
    print("\n--- Merged DataFrame Columns ---")
    print(merged_df.columns)

    #시각화
    #외국인 비율과 범죄율의 관계
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=merged_df, x='외국인비율', y='인구만명당범죄율',
                    size='총인구', hue='총인구',
                    sizes=(50, 500), palette='viridis', legend=False)

    #라벨 추가
    for i in range(len(merged_df)):
        plt.text(merged_df['외국인비율'].iloc[i] + 0.1,
                 merged_df['인구만명당범죄율'].iloc[i],
                 merged_df['구'].iloc[i], fontsize=9)

    plt.title('서울 자치구별 외국인 비율과 인구 만명당 범죄율')
    plt.xlabel('외국인 비율 (%)')
    plt.ylabel('인구 만명당 범죄율')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    #외국인 비율과 CCTV 설치 수의 관계
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=merged_df, x='외국인비율', y='카메라대수',
                    size='총인구', hue='총인구',
                    sizes=(50, 500), palette='viridis', legend=False)

    #라벨 추가
    for i in range(len(merged_df)):
        plt.text(merged_df['외국인비율'].iloc[i] + 0.1,
                 merged_df['카메라대수'].iloc[i],
                 merged_df['구'].iloc[i], fontsize=9)

    plt.title('서울 자치구별 외국인 비율과 CCTV 설치 수')
    plt.xlabel('외국인 비율 (%)')
    plt.ylabel('CCTV 설치 수')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    #인구 만명당 범죄율과 CCTV 설치 수의 관계
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=merged_df, x='인구만명당범죄율', y='카메라대수',
                    size='총인구', hue='외국인비율',
                    sizes=(50, 500), palette='viridis')

    #라벨 추가
    for i in range(len(merged_df)):
        plt.text(merged_df['인구만명당범죄율'].iloc[i] + 0.1,
                 merged_df['카메라대수'].iloc[i],
                 merged_df['구'].iloc[i], fontsize=9)

    plt.title('서울 자치구별 인구 만명당 범죄율과 CCTV 설치 수')
    plt.xlabel('인구 만명당 범죄율')
    plt.ylabel('CCTV 설치 수')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    #상관관계 분석
    correlation_foreign_crime = merged_df['외국인비율'].corr(merged_df['인구만명당범죄율'])
    correlation_foreign_cctv = merged_df['외국인비율'].corr(merged_df['카메라대수'])
    correlation_crime_cctv = merged_df['인구만명당범죄율'].corr(merged_df['카메라대수'])
    
    print(f"\n외국인 비율과 인구 만명당 범죄율 간의 상관관계: {correlation_foreign_crime:.2f}")
    print(f"외국인 비율과 CCTV 설치 수 간의 상관관계: {correlation_foreign_cctv:.2f}")
    print(f"인구 만명당 범죄율과 CCTV 설치 수 간의 상관관계: {correlation_crime_cctv:.2f}")

    #외국인 비율 TOP 5
    print("\n--- 외국인 비율 상위 5개 구 ---")
    print(merged_df.sort_values('외국인비율', ascending=False)[['구', '외국인비율', '인구만명당범죄율', '카메라대수']].head())

    #인구 만명당 범죄율이 높은 구 TOP 5
    print("\n--- 인구 만명당 범죄율 상위 5개 구 ---")
    print(merged_df.sort_values('인구만명당범죄율', ascending=False)[['구', '인구만명당범죄율', '외국인비율', '카메라대수']].head())

    #CCTV 설치 수가 많은 구 TOP 5
    print("\n--- CCTV 설치 수 상위 5개 구 ---")
    print(merged_df.sort_values('카메라대수', ascending=False)[['구', '카메라대수', '인구만명당범죄율', '외국인비율']].head())

else:
    print("Error: '구' 컬럼이 모든 데이터프레임에 존재하지 않아 병합할 수 없습니다.")

#CCTV 설치 현황과 범죄율 비교
print("\n--- 5-2. CCTV 설치 현황과 범죄율 비교 ---")

#CCTV 설치 개수와 범죄 발생 간의 상관관계 분석
correlation = merged_df['카메라대수'].corr(merged_df['총범죄수'])
print(f"\nCCTV 설치 개수와 총 범죄 발생 건수 간의 상관관계: {correlation:.2f}")

plt.figure(figsize=(10, 7))
sns.regplot(data=merged_df, x='카메라대수', y='총범죄수', scatter_kws={'alpha':0.6})
#라벨 추가
for i in range(len(merged_df)):
    plt.text(merged_df['카메라대수'].iloc[i] + 50,
             merged_df['총범죄수'].iloc[i],
             merged_df['구'].iloc[i], fontsize=9)
plt.title('CCTV 설치 개수와 총 범죄 발생 건수')
plt.xlabel('CCTV 대수')
plt.ylabel('총 범죄 건수')
plt.grid(True)
plt.tight_layout()
plt.show()

#CCTV 수가 많음에도 범죄율이 높은 지역 도출
merged_df['CCTV_대비_범죄수'] = merged_df.apply(
    lambda row: row['총범죄수'] / row['카메라대수'] if row['카메라대수'] > 0 else row['총범죄수'], axis=1
)

#CCTV 수가 평균보다 많으면서 CCTV 대비 범죄수가 높은 지역
avg_cctv = merged_df['카메라대수'].mean()
high_crime_despite_cctv = merged_df[
    (merged_df['카메라대수'] > avg_cctv) &
    (merged_df['CCTV_대비_범죄수'] > merged_df['CCTV_대비_범죄수'].mean())
].sort_values(by='CCTV_대비_범죄수', ascending=False)

print("\n--- CCTV 수가 평균보다 많음에도 CCTV 대비 범죄수가 높은 지역 ---")
print(high_crime_despite_cctv[['구', '카메라대수', '총범죄수', 'CCTV_대비_범죄수']])

plt.figure(figsize=(10, 6))
sns.barplot(x='구', y='CCTV_대비_범죄수', data=high_crime_despite_cctv, palette='coolwarm')
plt.title('CCTV가 많지만 CCTV 대비 범죄수가 높은 지역')
plt.xlabel('자치구')
plt.ylabel('CCTV 대수 대비 범죄수')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

#부동산 실거래가 분석
print("\n--- 5-3. 부동산 실거래가 분석 ---")

#지역별 아파트 중간 값 매매 가격 분석
#물건금액(만원)과 자치구명 컬럼이 estate_df에 있는지 확인
if '물건금액(만원)' not in estate_df.columns or '자치구명' not in estate_df.columns:
    print("Error: Estate DataFrame에 '물건금액(만원)' 또는 '자치구명' 컬럼이 없습니다. 컬럼명을 확인해주세요.")
    exit()

#물건금액(만원) 컬럼을 숫자형으로 변환
#데이터가 문자열로 되어 있고 쉼표가 포함된 경우를 대비
estate_df['물건금액(만원)'] = pd.to_numeric(estate_df['물건금액(만원)'].astype(str).str.replace(',', ''), errors='coerce')
estate_df.dropna(subset=['물건금액(만원)'], inplace=True) # 변환 실패(NaN) 값 제거

estate_median_price = estate_df.groupby('자치구명')['물건금액(만원)'].median().reset_index()
estate_median_price.columns = ['구', '아파트_중간매매가']
estate_median_price = estate_median_price.sort_values(by='아파트_중간매매가', ascending=False)

print("\n--- 지역별 아파트 중간 값 매매 가격 ---")
print(estate_median_price.head())

plt.figure(figsize=(12, 7))
sns.barplot(x='구', y='아파트_중간매매가', data=estate_median_price, palette='GnBu')
plt.title('서울 자치구별 아파트 중간 값 매매 가격')
plt.xlabel('자치구')
plt.ylabel('중간 매매 가격 (만원)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

#안전지표(범죄율, 교통사고)와의 상관관계 확인
#아파트 중간 매매가와 총 범죄수 간의 상관관계
if '아파트_중간매매가' in merged_df.columns and '총범죄수' in merged_df.columns:
    correlation_estate_crime = merged_df['아파트_중간매매가'].corr(merged_df['총범죄수'])
    print(f"\n아파트 중간 매매 가격과 총 범죄 건수 간의 상관관계: {correlation_estate_crime:.2f}")

    plt.figure(figsize=(10, 7))
    sns.regplot(data=merged_df, x='아파트_중간매매가', y='총범죄수', scatter_kws={'alpha':0.6})
    #라벨 추가
    for i in range(len(merged_df)):
        plt.text(merged_df['아파트_중간매매가'].iloc[i] * 1.01, # 약간 우측으로
                 merged_df['총범죄수'].iloc[i],
                 merged_df['구'].iloc[i], fontsize=9)
    plt.title('아파트 중간 매매 가격과 총 범죄 건수 관계')
    plt.xlabel('아파트 중간 매매 가격 (만원)')
    plt.ylabel('총 범죄 건수')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("Error: '아파트_중간매매가' 또는 '총범죄수' 컬럼이 최종 병합 데이터프레임에 없습니다. 상관관계 분석 불가.")


print("\n--- 데이터 분석 완료 ---")
