import requests

class DataFetcher:

    def __init__(self,api_key= "6f424346616d736a383371627a5a55",base_url = None):
        self.api_key = api_key
        self.base_url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/bikeList/1/1000/"
        self.raw_data = None

    #서울시 공공데이터 받아오는 함수
    def get_data(self):
            '''
            response = requests.get(self.base_url,timeout=5)
            self.raw_data = response.json()
            return self.raw_data
            '''

            all_rows = []
        
        # 1부터 3000까지 1000개씩 구간을 나누어 반복
            for start in range(1, 3001, 1000):
                end = start + 999
            # 기존에 정의된 base_url의 '1/1000' 부분을 현재 구간 숫자로 교체
                target_url = self.base_url.replace("1/1000", f"{start}/{end}")
            
                try:
                    response = requests.get(target_url, timeout=5)
                    res_json = response.json()
                    rows = res_json.get("rentBikeStatus", {}).get("row", [])
                    if rows:
                        all_rows.extend(rows)
                    else:
                        break
                except Exception as e:
                    print(f"데이터 조회 중 에러 발생: {e}")
                    break
                
            self.raw_data = {"rentBikeStatus": {"row": all_rows}}
            return self.raw_data

    #API 상태 점검 / 예외처리 
    def check_api(self):
        pass




#공공데이터 제대로 받아오는지 테스트
fetcher = DataFetcher()
data = fetcher.get_data()


if data:
     list=data.get("rentBikeStatus",{}).get("row",[])
     print(f"대여소 총 개수:{len(list)}")
     if len(list)>0:
        print("첫번째 대여소 샘플:",list[0])
else:
     print("데이터 받아오지 못함")


