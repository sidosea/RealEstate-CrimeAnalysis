import pandas as pd
import re

df = pd.read_excel("BigDataProject/12_04_08_E_CCTV정보.xlsx")

# 이름 추출
def extract_gu(name):
    match = re.search(r'서울(?:시|특별시)\s*(\S+?)청', name)
    return match.group(1) if match else None

# 구 컬럼 추가
df['구'] = df.iloc[:, 0].apply(extract_gu)
# 합산
result = df.groupby('구')[df.columns[1]].sum().reset_index()
result.to_csv("output.csv", index=False, encoding='utf-8-sig')


