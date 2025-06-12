import argparse
import os
from .config import Config
from .batch_processor import BatchProcessor

def main():
    # 1. 인자 파싱
    parser = argparse.ArgumentParser(description='DB 데이터로 학습 데이터셋 생성')
    parser.add_argument('--config', type=str, required=True, help='설정 파일 경로')
    parser.add_argument('--start-id', type=int, required=True, help='시작 ID')
    parser.add_argument('--end-id', type=int, required=True, help='종료 ID')
    parser.add_argument('--output', type=str, required=True, help='출력 파일 경로')
    args = parser.parse_args()
    
    # 2. 출력 디렉토리 생성
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # 3. 설정 로드
    config = Config(args.config)
    
    # 4. 처리 실행
    processor = BatchProcessor(config)
    processor.process_to_file(args.start_id, args.end_id, args.output)

if __name__ == '__main__':
    main() 