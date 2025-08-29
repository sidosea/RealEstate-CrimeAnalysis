import pandas as pd

# CSV 읽기
df = pd.read_csv("BigDataProject/경찰청_범죄 발생 지역별 통계_20231231.csv", encoding="cp949")

# 컬럼명 서울 제거
df.columns = [col.replace('서울', '') if col != df.columns[0] else col for col in df.columns]
df = df.rename(columns={df.columns[0]: '범죄대분류'})

# 동일한 구 합산
grouped = df.groupby('범죄대분류').sum(numeric_only=True)
grouped.to_csv("addedCrime.csv", encoding='cp949')

