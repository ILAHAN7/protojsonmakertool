import os
import sys
from data_processor.batch_processor import BatchProcessor
from data_processor.config import Config

def main():
    # 기본값 설정
    config_path = 'config/db_config.ini'
    output_dir = 'output'
    output_file = 'result.jsonl'
    
    # 명령줄 인자 처리
    if len(sys.argv) != 3:
        print("사용법: python run.py <시작_ID> <종료_ID>")
        print("예시: python run.py 53749 53849")
        sys.exit(1)
    
    try:
        start_id = int(sys.argv[1])
        end_id = int(sys.argv[2])
    except ValueError:
        print("오류: ID는 숫자여야 합니다.")
        sys.exit(1)
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    
    # 설정 로드 및 처리 실행
    config = Config(config_path)
    processor = BatchProcessor(config)
    
    print(f"처리 시작: ID {start_id} ~ {end_id}")
    processor.process_to_file(start_id, end_id, output_path)
    print(f"처리 완료: 결과가 {output_path}에 저장되었습니다.")

if __name__ == '__main__':
    main() 