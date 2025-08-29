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
    exit() #파일이 없으면 프로그램 종료
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

#각 데이터프레임의 상위 5행 출력 (데이터 로드 확인용)
print("\n--- CCTV DataFrame Head ---")
print(cctv_df.head())
print("\n--- Crime DataFrame Head ---")
print(crime_df.head())
print("\n--- Estate DataFrame Head ---")
print(estate_df.head())

#부동산 평균 집계
if '물건금액(만원)' in estate_df.columns and '자치구명' in estate_df.columns:
    estate_grouped = estate_df.groupby('자치구명')['물건금액(만원)'].mean().reset_index()
    estate_grouped.columns = ['구', '평균부동산금액']
    print("\n--- Estate Grouped Head ---")
    print(estate_grouped.head())
else:
    print("Error: '물건금액(만원)' 또는 '자치구명' 컬럼이 Estate.csv에 없습니다. 컬럼명을 확인해주세요.")
    exit()


#범죄 전처리
if '범죄대분류' in crime_df.columns:
    # 범죄 데이터를 구별로 집계
    crime_by_district = crime_df.set_index('범죄대분류').T
    crime_by_district['총범죄수'] = crime_by_district.sum(axis=1)
    crime_by_district.reset_index(inplace=True)
    crime_by_district.rename(columns={'index': '구'}, inplace=True)
    print("\n--- Crime by District Head ---")
    print(crime_by_district.head())
else:
    print("Error: '범죄대분류' 컬럼이 Crime.csv에 없습니다. 컬럼명을 확인해주세요.")
    exit()


#병합
#컬럼이 각 데이터프레임에 있는지 확인
if '구' in cctv_df.columns and '구' in crime_by_district.columns and '자치구명' in estate_df.columns:
    # Estate 데이터의 컬럼명을 '구'로 변경
    estate_df = estate_df.rename(columns={'자치구명': '구'})
    merged_df = pd.merge(cctv_df, crime_by_district[['구', '총범죄수']], on='구', how='inner')
    merged_df = pd.merge(merged_df, estate_df[['구', '물건금액(만원)']], on='구', how='inner')
    print("\n--- Merged DataFrame Head ---")
    print(merged_df.head())
    print("\n--- Merged DataFrame Columns ---")
    print(merged_df.columns)

    #시각화
    #카메라대수,총범죄수,물건금액(만원) 컬럼이 병합된 데이터프레임에 있는지 확인
    if '카메라대수' in merged_df.columns and '총범죄수' in merged_df.columns and '물건금액(만원)' in merged_df.columns:
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=merged_df, x='카메라대수', y='총범죄수',
                        size='물건금액(만원)', hue='물건금액(만원)',
                        sizes=(50, 500), palette='viridis', legend=False)
        #라벨 추가 시 '구' 컬럼이 있어야 함
        if '구' in merged_df.columns:
            for i in range(len(merged_df)):
                plt.text(merged_df['카메라대수'].iloc[i] + 100,
                         merged_df['총범죄수'].iloc[i],
                         merged_df['구'].iloc[i], fontsize=9)
        else:
            print("Error: '구' 컬럼이 병합된 데이터프레임에 없어 라벨을 추가할 수 없습니다.")

        plt.title('서울 자치구별 CCTV 수와 범죄수 (부동산 평균가 크기)')
        plt.xlabel('CCTV 대수')
        plt.ylabel('총 범죄 건수')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        print("Error: 시각화에 필요한 '카메라대수', '총범죄수', '물건금액(만원)' 컬럼 중 일부가 병합된 데이터프레임에 없습니다.")
        print("병합된 데이터프레임 컬럼: ", merged_df.columns.tolist())
else:

    print("Error: '구' 컬럼이 모든 데이터프레임에 존재하지 않아 병합할 수 없습니다.")

