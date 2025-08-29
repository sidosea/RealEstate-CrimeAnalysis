import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import Pipeline

#한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """데이터 로드 및 전처리 함수"""
    try:
        #CCTV 데이터 로드
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
        
        #범죄 데이터 로드
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
        
        #부동산 데이터 로드
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
        
        #인구 데이터 로드
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

def prepare_data(cctv_df, crime_df, estate_df, person_df):
    """회귀 분석을 위한 데이터 준비"""
    #범죄 전처리
    crime_by_district = crime_df.set_index('범죄대분류').T
    crime_by_district.reset_index(inplace=True)
    crime_by_district.rename(columns={'index': '구'}, inplace=True)
    crime_types = crime_by_district.columns[1:]
    crime_by_district['총범죄수'] = crime_by_district[crime_types].sum(axis=1)
    
    #인구 전처리
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
    
    #부동산 전처리
    estate_df['물건금액(만원)'] = pd.to_numeric(estate_df['물건금액(만원)'].astype(str).str.replace(',', ''), errors='coerce')
    estate_by_district = estate_df.groupby('자치구명')['물건금액(만원)'].mean().reset_index()
    estate_by_district.rename(columns={'자치구명': '구'}, inplace=True)
    
    #모든 데이터 병합
    merged_data = pd.merge(cctv_df[['구', '카메라대수']], crime_by_district[['구', '총범죄수']], on='구', how='inner')
    merged_data = pd.merge(merged_data, estate_by_district, on='구', how='inner')
    merged_data = pd.merge(merged_data, person_by_district[['구', '외국인비율']], on='구', how='inner')
    
    return merged_data

def analyze_regression(data):
    """회귀 분석 수행"""
    #특성과 타겟 분리
    features = ['총범죄수', '외국인비율', '카메라대수']
    X = data[features]
    y = data['물건금액(만원)']
    
    #파이프라인
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', LinearRegression())
    ])
    
    #학습/테스트 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    #모델 학습
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    #모델 평가
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print("\n=== 전체 구 회귀 분석 결과 ===")
    print(f"평균 제곱 오차 (MSE): {mse:,.2f}")
    print(f"평균 절대 오차 (MAE): {mae:,.2f}")
    print(f"결정 계수 (R²): {r2:.4f}")
    
    #특성 중요도 시각화
    plt.figure(figsize=(10, 6))
    feature_importance = pd.DataFrame({
        '특성': features,
        '계수': pipeline.named_steps['regressor'].coef_
    })
    sns.barplot(data=feature_importance.sort_values('계수', ascending=False),
                x='계수', y='특성')
    plt.title('특성별 회귀 계수 (전체 구)')
    plt.xlabel('회귀 계수')
    plt.ylabel('특성')
    plt.tight_layout()
    plt.show()
    
    #실제값 vs 예측값
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.title('실제값 vs 예측값 (전체 구)')
    plt.xlabel('실제 아파트 가격 (만원)')
    plt.ylabel('예측 아파트 가격 (만원)')
    plt.tight_layout()
    plt.show()
    
    return pipeline

def main():
    """메인 함수"""
    cctv_df, crime_df, estate_df, person_df = load_data()
    
    #존재 여부 확인
    if any(df is None for df in [cctv_df, crime_df, estate_df, person_df]):
        print("일부 데이터를 로드하지 못했습니다. 프로그램을 종료합니다.")
        return
    
    print("\n=== 데이터 준비 중... ===")
    merged_data = prepare_data(cctv_df, crime_df, estate_df, person_df)
    
    print("\n=== 회귀 분석 수행 중... ===")
    model = analyze_regression(merged_data)
    
    print("\n=== 변수 간 상관관계 분석 ===")
    correlation = merged_data[['총범죄수', '외국인비율', '카메라대수', '물건금액(만원)']].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation, 
                annot=True, 
                cmap='coolwarm', 
                vmin=-1, 
                vmax=1,
                fmt='.2f')
    plt.title('변수 간 상관관계')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

