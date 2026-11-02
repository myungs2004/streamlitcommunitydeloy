import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from DataFetcher import DataFetcher
from DataProcessor import DataProcessor
from StationFilter import StationFilter

class DashboardUI:
    def __init__(self):
        self.df = pd.DataFrame()
        self.summary = {}
        self.filtered_df = pd.DataFrame()

    #검색 사이드바
    def render_sidebar(self): 
        st.sidebar.header("🔍 대여소 검색 및 필터")
        search_keyword = st.sidebar.text_input("대여소 이름 검색", placeholder="예: 광운대역")
        min_bikes = st.sidebar.slider("최소 잔여 자전거 수", 0, 20, 0)
        status_filter = st.sidebar.selectbox("혼잡도 상태", ["전체", "여유", "보통", "부족"])
        return search_keyword, min_bikes, status_filter

    #통계영역
    #todo - 더미 데이터라 api 받아오면 삭제
    def show_metrics(self,summary): 
        col1, col2, col3= st.columns(3)
        with col1:
            
            st.metric(label="전체 대여소 수", value=f"{summary.get('전체 대여소 수', 0):,}개")
        with col2:
            st.metric(label="총 가동 자전거", value=f"{summary.get('총 자전거 수', 0):,}대")
        with col3:
            st.metric(label="평균 거치율", value=f"{summary.get('평균 거치율', 0.0)}%")

    #지도영역
    #todo - Folium map으로 개선 가능
    #todo - 더미 데이터라 api 받아오면 삭제
    def show_map(self,filtered_df):      
        '''
        st.subheader("서울시 대여소 현황 지도 (Prototype)")
        map_data = pd.DataFrame(
            np.random.randn(50, 2) / [50, 50] + [37.5665, 126.9780],
            columns=['lat', 'lon']
        )
        st.map(map_data)
        '''

        st.subheader("서울시 대여소 위치")
        if not filtered_df.empty and '위도' in filtered_df.columns and '경도' in filtered_df.columns:
            map_df = filtered_df.rename(columns={'위도': 'lat', '경도': 'lon'})
            st.map(map_df[['lat', 'lon']], zoom=11)
        else:
            st.info("표출할 지도 데이터가 없습니다.")
        

    # 테이블영역
    #todo - 더미 데이터라 api 받아오면 삭제
    def show_table(self,filtered_df): 
        '''
        st.subheader("대여소 상세 정보 목록")
        dummy_df = pd.DataFrame({
            "대여소 ID": [101, 102, 103, 104, 105],
            "대여소명": ["광운대역 3번출구", "석계역 1번출구", "월계이마트", "공릉역 2번출구", "태릉입구역"],
            "거치대 수": [15, 20, 10, 25, 15],
            "현재 자전거": [2, 14, 1, 18, 5],
            "상태": ["부족", "여유", "부족", "여유", "보통"]
        })
        st.dataframe(dummy_df, use_container_width=True)
        '''
        st.subheader("대여소 상세 정보 목록")
        if not filtered_df.empty:
            display_df = filtered_df[[
                '대여소ID', '대여소이름', '거치대개수', '자전거주차총건수', '거치율', '상태'
            ]].rename(columns={
                '대여소ID': '대여소 ID',
                '대여소이름': '대여소명',
                '거치대개수': '거치대 수',
                '자전거주차총건수': '현재 자전거'
            })
            st.dataframe(display_df, use_container_width=True, height=450)
        else:
            st.warning("조건에 일치하는 대여소가 없습니다.")


    #차트영역
    #todo - api 연동되면 더미데이터 삭제
    def show_chart(self,df):
        '''
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("⚠️ 자전거 부족 대여소 TOP 10")
            
            top_shortage_df = pd.DataFrame({
                "stationName": ["광운대역 2번출구", "공릉역 1번출구", "월계역 3번출구", "석계역 2번출구", "태릉입구역 4번출구"],
                "parkingBikeTotCnt": [1, 2, 2, 3, 4]
            })

            fig_bar = px.bar(
                top_shortage_df,
                x="parkingBikeTotCnt",
                y="stationName",
                orientation="h",
                labels={"parkingBikeTotCnt": "잔여 자전거 수", "stationName": "대여소명"},
                template="plotly_white",
            )
            fig_bar.update_traces(marker_color="#ef4444") 
            fig_bar.update_layout(
                bargap=0.4,
                margin=dict(l=10, r=10, t=20, b=20),
                yaxis=dict(autorange="reversed") 
            )
            st.plotly_chart(fig_bar, width="stretch")

        with col_right:
            st.subheader("📊 대여소 혼잡도 상태 비율")

            status_df = pd.DataFrame({
                "status": ["여유", "보통", "부족"],
                "count": [45, 35, 20]
            })

            fig_pie = px.pie(
                status_df,
                names="status",
                values="count",
                hole=0.5, 
                template="plotly_white",
                color="status",
                color_discrete_map={
                    "여유": "#10b981", 
                    "보통": "#f59e0b", 
                    "부족": "#ef4444"
                }
            )
            fig_pie.update_layout(
                margin=dict(l=10, r=10, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, width="stretch")
        '''
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("⚠️ 자전거 부족 대여소 TOP 10")
            
            sf_chart = StationFilter(df)
            top_shortage_df = sf_chart.top_shortage(10)

            if not top_shortage_df.empty:
                fig_bar = px.bar(
                    top_shortage_df,
                    x="자전거주차총건수",
                    y="대여소이름",
                    orientation="h",
                    labels={"자전거주차총건수": "잔여 자전거 수", "대여소이름": "대여소명"},
                    template="plotly_white",
                )
                fig_bar.update_traces(marker_color="#ef4444") 
                fig_bar.update_layout(
                    bargap=0.4,
                    margin=dict(l=10, r=10, t=20, b=20),
                    yaxis=dict(autorange="reversed") 
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("데이터가 없습니다.")

        with col_right:
            st.subheader("📊 대여소 혼잡도 상태 비율")

            if not df.empty and '상태' in df.columns:
                status_counts = df['상태'].value_counts().reset_index()
                status_counts.columns = ['status', 'count']

                fig_pie = px.pie(
                    status_counts,
                    names="status",
                    values="count",
                    hole=0.5, 
                    template="plotly_white",
                    color="status",
                    color_discrete_map={
                        "여유": "#10b981", 
                        "보통": "#f59e0b", 
                        "부족": "#ef4444"
                    }
                )
                fig_pie.update_layout(
                    margin=dict(l=10, r=10, t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("데이터가 없습니다.")

    def run(self):
        '''
        # 페이지 기본 설정
        st.set_page_config(
            page_title="서울시 따릉이 대여정보 대시보드",
            page_icon="🚲",
            layout="wide"
        )
        
        st.title("🚲 서울시 공공자전거 따릉이 대여정보 대시보드")
        st.markdown("---")

        # 각 메서드 호출 실행
        self.render_sidebar()
        self.show_metrics()
        st.markdown("---")

        # todo - 도표나 그래프 추가!
        tab1, tab2, tab3 = st.tabs(["🗺️ 대여소 지도", "📊 데이터 테이블", "📈 차트"])
        with tab1:
            self.show_map()
        with tab2:
            self.show_table()
        with tab3:
            self.show_chart()
        '''

        st.set_page_config(
            page_title="서울시 따릉이 대여정보 대시보드",
            page_icon="🚲",
            layout="wide"
        )
        
        st.title("🚲 서울시 공공자전거 따릉이 대여정보 대시보드")
        st.markdown("---")

        # 1. API 데이터 가져오기 및 전처리 파이프라인 실행
        with st.spinner("🔄 서울시 전체 따릉이 데이터를 불러오는 중입니다..."):
            fetcher = DataFetcher()
            raw_data = fetcher.get_data()

        if not raw_data:
            st.error("❌ 데이터를 받아오지 못했습니다. API 상태를 확인해주세요.")
            return

        row_list = raw_data.get("rentBikeStatus", {}).get("row", [])
        if not row_list:
            st.warning("⚠️ 대여소 데이터가 비어 있습니다.")
            return

        processor = DataProcessor(row_list)
        df = processor.clean()
        df = processor.add_rate()
        summary = processor.get_summary()

        # 2. 사이드바 입력값 처리
        search_keyword, min_bikes, status_filter = self.render_sidebar()

        # 3. StationFilter로 실시간 필터 적용
        sf = StationFilter(df)
        if search_keyword:
            sf.search(search_keyword)
        if min_bikes > 0:
            sf.bike_count(min_bikes)
        if status_filter != "전체":
            sf.by_status(status_filter)
        
        filtered_df = sf.filtered_df

        # 4. 통계 영역 표시
        self.show_metrics(summary)
        st.markdown("---")

        # 5. 탭 구성 (지도, 테이블, 차트)
        tab1, tab2, tab3 = st.tabs(["🗺️ 대여소 지도", "📊 데이터 테이블", "📈 차트"])
        with tab1:
            self.show_map(filtered_df)
        with tab2:
            self.show_table(filtered_df)
        with tab3:
            self.show_chart(df)

if __name__ == "__main__":
    ui = DashboardUI()
    ui.run()
