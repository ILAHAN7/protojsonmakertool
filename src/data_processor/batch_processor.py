import json
import time
from typing import Dict, Any, Iterator, List
from .config import Config
from .db_connector import DBConnector
from .spatial_matcher import SpatialMatcher
import os

def float_repr(o):
    """부동소수점 숫자를 문자열로 변환 (지수 표기법 방지)"""
    if isinstance(o, float):
        return format(o, 'f').rstrip('0').rstrip('.')
    return repr(o)

class BatchProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.db = DBConnector(config.db)
        self.matcher = SpatialMatcher(self.db, config.processor)
        self.stats = {
            'db_read_time': 0,
            'building_match_time': 0,
            'total_records': 0
        }
    
    def process_range(self, start_id: int, end_id: int) -> Iterator[Dict[str, Any]]:
        """지정된 범위의 데이터를 배치 단위로 처리"""
        for batch_start in range(start_id, end_id, self.config.processor.batch_size):
            batch_end = min(batch_start + self.config.processor.batch_size, end_id)
            
            # 1. Collectxy 배치 데이터 로드 (그리드 셀 계산 포함)
            db_start = time.time()
            locations = self.db.get_collectxy_batch(batch_start, batch_end)
            self.stats['db_read_time'] += time.time() - db_start
            
            if not locations:
                continue
            
            # 2. 각 위치에 대해 처리
            for location in locations:
                self.stats['total_records'] += 1
                
                # 기본 응답 구조 생성 (location 정보는 제외)
                result = {
                    'input': {
                        'lcellid': location['lcellid'].split(',') if location['lcellid'] else [],
                        'wmac': location['wmac'].split(',') if location['wmac'] else [],
                        'wrssi': [float(x) for x in location['wrssi'].split(',')] if location['wrssi'] else [],
                        'ipcikey': location['ipcikey'].split(',') if location['ipcikey'] else []
                    },
                    'answer': {
                        'grid_cell': location['grid_cell']
                    }
                }
                
                # 빌딩 탐색이 활성화된 경우에만 수행
                if self.config.processor.building_search:
                    match_start = time.time()
                    matches = self.matcher.find_matches(location)
                    self.stats['building_match_time'] += time.time() - match_start
                    result['answer']['buildings'] = matches.get('buildings', [])
                
                yield result
    
    def process_to_file(self, start_id: int, end_id: int, output_path: str):
        """처리 결과를 파일로 저장"""
        total_start = time.time()
        
        # 출력 디렉토리가 없으면 생성
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # traindata 파일 경로 생성
        base_name = os.path.splitext(output_path)[0]
        train_path = f"{base_name}_traindata.jsonl"
        
        # 두 파일 동시에 처리
        with open(output_path, 'w', encoding='utf-8') as f_out, \
             open(train_path, 'w', encoding='utf-8') as f_train:
            
            for record in self.process_range(start_id, end_id):
                # 원본 형식으로 저장
                json.dump(record, f_out, ensure_ascii=False, default=float_repr)
                f_out.write('\n')
                
                wmac_str = ','.join(record['input']['wmac']) if record['input']['wmac'] else ""
                wrssi_str = ','.join([str(x) for x in record['input']['wrssi']]) if record['input']['wrssi'] else ""
                lcellid_str = ','.join(record['input']['lcellid']) if record['input']['lcellid'] else ""
                ipcikey_str = ','.join(record['input']['ipcikey']) if record['input']['ipcikey'] else ""
                
                prompt_str = f"wmac={wmac_str} wrssi={wrssi_str} lcellid={lcellid_str} ipcikey={ipcikey_str}"
                completion_str = f"x_id={record['answer']['grid_cell']['x_id']},y_id={record['answer']['grid_cell']['y_id']}"
                
                train_record = {
                    "prompt": prompt_str,
                    "completion": completion_str
                }
                
                json.dump(train_record, f_train, ensure_ascii=False)
                f_train.write('\n')
        
        total_time = time.time() - total_start
        print("\n성능 통계:")
        print(f"총 처리 시간: {total_time:.2f}초")
        print(f"총 레코드 수: {self.stats['total_records']}")
        print(f"레코드당 평균 처리 시간: {(total_time/self.stats['total_records'])*1000:.2f}ms")
        print(f"DB 읽기 시간: {self.stats['db_read_time']:.2f}초 ({(self.stats['db_read_time']/total_time)*100:.1f}%)")
        if self.config.processor.building_search:
            print(f"건물 매칭 시간: {self.stats['building_match_time']:.2f}초 ({(self.stats['building_match_time']/total_time)*100:.1f}%)")
        print(f"초당 처리 레코드: {self.stats['total_records']/total_time:.1f}개")
        print(f"처리 완료:")
        print(f"- 원본 결과: {output_path}")
        print(f"- 학습 데이터: {train_path}")