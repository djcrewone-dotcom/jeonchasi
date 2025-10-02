import http.server
import socketserver
import os
import json
import pandas as pd
import glob
from urllib.parse import urlparse, parse_qs

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API 엔드포인트 처리
        if parsed_path.path == '/api/remaining-data':
            self.handle_remaining_data_api(parsed_path)
        else:
            # 기본 정적 파일 서빙
            super().do_GET()
    
    def handle_remaining_data_api(self, parsed_path):
        """잔여대수 데이터 API"""
        try:
            # data 폴더에서 최신 CSV 파일 찾기
            csv_files = glob.glob('data/*remaining car*.csv')
            if not csv_files:
                self.send_error_response(404, "CSV 파일을 찾을 수 없습니다")
                return
            
            # 가장 최신 파일 선택
            latest_file = max(csv_files, key=os.path.getctime)
            
            # CSV 파일 읽기
            df = pd.read_csv(latest_file, encoding='utf-8-sig')
            
            # 쿼리 파라미터 파싱
            query_params = parse_qs(parsed_path.query)
            vehicle_type = query_params.get('vehicle_type', [None])[0]
            region = query_params.get('region', [None])[0]
            
            # 데이터 필터링
            filtered_df = df.copy()
            if vehicle_type:
                filtered_df = filtered_df[filtered_df['구분'] == vehicle_type]
            if region:
                filtered_df = filtered_df[filtered_df['지역'] == region]
            
            # JSON으로 변환
            data = filtered_df.to_dict('records')
            
            # 응답 전송
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"API 오류: {e}")
            self.send_error_response(500, f"서버 오류: {str(e)}")
    
    def send_error_response(self, status_code, message):
        """에러 응답 전송"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        error_data = {"error": message}
        self.wfile.write(json.dumps(error_data, ensure_ascii=False).encode('utf-8'))

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"서버가 http://localhost:{PORT} 에서 실행 중입니다")
        print("브라우저에서 http://localhost:8000/index.html 을 열어주세요")
        print("API 엔드포인트: http://localhost:8000/api/remaining-data")
        httpd.serve_forever()
