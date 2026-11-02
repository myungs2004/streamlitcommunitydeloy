import pandas as pd
from DataFetcher import DataFetcher
from DataProcessor import DataProcessor


class StationFilter:

    #입력:df
    #출력:filtered_df
    def __init__(self,df):
        self.df = df
        self.filtered_df = df

    #대여소 이름/키워드 필터링
    def search(self,keyword):
        if not keyword:
            return self.filtered_df
        if "대여소이름" in self.filtered_df.columns:
            self.filtered_df = self.filtered_df[
                self.filtered_df["대여소이름"].astype(str).str.contains(keyword, case=False, na=False)
            ]
        return self.filtered_df

    #혼잡도 상태 필터링(부족/보통/여유)
    def by_status(self,status): 
        if not status or status =="전체":
            return self.filtered_df
        if "상태" in self.filtered_df.columns:
            self.filtered_df =self.filtered_df[self.filtered_df["상태"] == status]
        return self.filtered_df    

    #최소 자전거 수 필터링
    def bike_count(self,min_bikes): 
    
        if "자전거주차총건수" in self.filtered_df.columns:
            self.filtered_df = self.filtered_df[
                self.filtered_df["자전거주차총건수"] >= min_bikes
            ]
        return self.filtered_df
    
    #자전거 부족 대여소 추출
    def top_shortage(self,n):
       
        if "자전거주차총건수" in self.filtered_df.columns:
            return self.filtered_df.sort_values(by="자전거주차총건수", ascending=True).head(n)
        return self.filtered_df

    # 자전거 과잉(포화) 대여소 TOP 추출 (거치율이 가장 높은 순서)
    def top_excess(self, n):
        if "거치율" in self.filtered_df.columns and "자전거주차총건수" in self.filtered_df.columns:
            sorted_df = self.filtered_df.sort_values(
                by=["거치율", "자전거주차총건수"], 
                ascending=[False, False]
            )
            return sorted_df.head(n)
        return self.filtered_df
        
        
#api로 받아오는 정보
#거치대개수
#대여소이름
#자전거주차총건수
#거치율
#위도
#경도
#대여소ID
#대여시간

if __name__ == "__main__":
    print("🚀 [1단계] 서울시 전체 API 호출 및 전처리 파이프라인 실행...")
    fetcher = DataFetcher()
    raw_data = fetcher.get_data()

    if raw_data:
        row_list = raw_data.get("rentBikeStatus", {}).get("row", [])
        if len(row_list) > 0:
            # 1. 전처리기로 실제 데이터프레임 완성
            processor = DataProcessor(row_list)
            df = processor.clean()
            df = processor.add_rate()
            
            # 요약 통계 확인
            summary = processor.get_summary()
            print(f"\n📊 [전체 요약 통계]")
            for k, v in summary.items():
                print(f" - {k}: {v:,}개" if isinstance(v, int) else f" - {k}: {v}")
            print(f"\n✅ 전처리 완료! (총 {len(df)}개 대여소)\n")

            print("🔍 [2단계] StationFilter에서 실제 전체 데이터로 필터링 테스트 시작")
            
            # 테스트 1: 대여소 이름 검색 ("노원")
            keyword = "노원"
            sf1 = StationFilter(df)
            search_result = sf1.search(keyword)
            print(f"--- 1. '{keyword}' 검색 결과 (총 {len(search_result)}개) ---")
            if not search_result.empty:
                print(search_result[["대여소이름", "자전거주차총건수", "거치율", "상태"]].head(3))
            else:
                print(f"'{keyword}' 검색 결과가 없습니다.")

            # 테스트 2: 혼잡도 상태 필터링 ('부족')
            sf2 = StationFilter(df)
            status_result = sf2.by_status("부족")
            print(f"\n--- 2. 혼잡도 '부족' 대여소 필터 결과 (총 {len(status_result)}개) ---")
            if not status_result.empty:
                print(status_result[["대여소이름", "자전거주차총건수", "거치율", "상태"]].head(3))

            # 테스트 3: 자전거 부족 대여소 TOP 3 정밀 추출 (0개 동률 개선 반영)
            sf3 = StationFilter(df)
            top3_shortage = sf3.top_shortage(3)
            print(f"\n--- 3. 자전거 부족 TOP 3 정밀 추출 결과 ---")
            print(top3_shortage[["대여소이름", "거치대개수", "자전거주차총건수", "거치율", "상태"]])

            # 테스트 4: 자전거 과잉(포화) 대여소 TOP 3 추출 (신규 추가)
            sf4 = StationFilter(df)
            top3_excess = sf4.top_excess(3)
            print(f"\n--- 4. 자전거 과잉(포화) TOP 3 추출 결과 ---")
            print(top3_excess[["대여소이름", "거치대개수", "자전거주차총건수", "거치율", "상태"]])

            print("\n🎉 서울시 전체 데이터 연동 및 필터 테스트 성공!")
        else:
            print("⚠️ 대여소 리스트가 비어 있습니다.")
    else:
        print("❌ 데이터를 받아오지 못했습니다.")