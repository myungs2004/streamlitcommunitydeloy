import pandas as pd
from DataFetcher import DataFetcher

class DataProcessor:

    #입력:raw_data
    #출력:df
    def __init__(self,raw_data):
        self.raw_data = raw_data
        self.df = None
        self.summary_stats = {}

    #데이터 타입 변환 함수
    # Pandas DataFrame으로 변환 
    def clean(self):
        if not self.raw_data:
            self.df = pd.DataFrame()
            return self.df
        self.df = pd.DataFrame(self.raw_data)
        column_mapping = {
            'stationId': '대여소ID',
            'stationName': '대여소이름',
            'rackTotCnt': '거치대개수',
            'parkingBikeTotCnt': '자전거주차총건수',
            'shared': '거치율',
            'stationLatitude': '위도',
            'stationLongitude': '경도'
        }
        self.df = self.df.rename(columns={k: v for k, v in column_mapping.items() if k in self.df.columns})

        numeric_cols = ['거치대개수', '자전거주차총건수', '거치율', '위도', '경도']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                
        return self.df
    
    #자전거 대여 혼잡 상태 판단(여유,보통,부족)
    def add_rate(self): 
        if self.df is None or self.df.empty:
            return self.df
            
        # 거치율(shared) 또는 자전거 주차 건수를 기준으로 상태 판단
        def judge_status(row):
            shared = row.get('거치율', 50)
            if pd.isna(shared):
                return '보통'
            
            # 기준 예시: 거치율 20 미만 '부족', 20~60 '보통', 60 초과 '여유'
            if shared < 20:
                return '부족'
            elif shared <= 60:
                return '보통'
            else:
                return '여유'

        # '상태' 컬럼 새로 생성
        self.df['상태'] = self.df.apply(judge_status, axis=1)
        return self.df

    #요약 통계 생성(전체 대여소, 총 자전거 수 같은 거 딕셔너리 이용해서 정리)
    def get_summary(self): 
        if self.df is None or self.df.empty:
            return {}
            
        self.summary_stats = {
            "전체 대여소 수": len(self.df),
            "총 자전거 수": int(self.df['자전거주차총건수'].sum()) if '자전거주차총건수' in self.df.columns else 0,
            "평균 거치율": round(self.df['거치율'].mean(), 1) if '거치율' in self.df.columns else 0.0
        }
        return self.summary_stats


#api로 받아오는 정보
#거치대개수
#대여소이름
#자전거주차총건수
#거치율
#위도
#경도
#대여소ID
#대여시간

