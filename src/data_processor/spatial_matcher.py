from typing import Dict, List, Any
from .db_connector import DBConnector
from .config import ProcessorConfig
from .cell_matcher import GridCellMatcher

class SpatialMatcher:
    # 그리드 셀 상수
    ORG_MIN_X = 124.54117
    ORG_MIN_Y = 32.928463
    ORG_MAX_X = 130.57113
    ORG_MAX_Y = 42.344405
    OFFSET_5M_X = 0.0000555
    OFFSET_5M_Y = 0.0000460
    DEFAULT_LEVEL = 5  # 25m 그리드 셀

    def __init__(self, db_connector: DBConnector, config: ProcessorConfig):
        self.db = db_connector
        self.config = config
        self.cell_matcher = GridCellMatcher()
    
    def is_point_in_bbox(self, lat: float, lon: float, bbox: Dict[str, float]) -> bool:
        """점이 bbox 안에 있는지 확인"""
        return (bbox['min_x'] <= lon <= bbox['max_x'] and
                bbox['min_y'] <= lat <= bbox['max_y'])
    
    def is_point_in_polygon(self, lat: float, lon: float, building: Dict[str, Any]) -> bool:
        """점이 건물 폴리곤 내부에 있는지 확인"""
        if 'polygon' in building:
            # TODO: 폴리곤 포함 여부 검사 로직 구현
            # 현재는 BBox로 대체
            return True
        return True
    
    def match_buildings(self, lat: float, lon: float, candidates: List[Dict]) -> List[Dict]:
        """Building 매칭 - 2단계 처리"""
        matched = []
        for building in candidates:
            # 1단계: 빠른 BBox 검사
            if not self.is_point_in_bbox(lat, lon, building):
                continue
                
            # 2단계: 건물 특성에 따른 추가 검사
            if building.get('needs_precise_check', False):
                if not self.is_point_in_polygon(lat, lon, building):
                    continue
            
            matched.append(building)
        return matched

    def find_matches(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """위치에 대한 building과 cell 매칭"""
        lat, lon = location['latitude'], location['longitude']
        
        # 1. 그리드 셀 매칭
        grid_cell = self.cell_matcher.match(lat, lon)
        
        # 2. Building 매칭 (2단계 처리)
        building_candidates = self.db.get_building_candidates(
            lat, lon, self.config.spatial_margin
        )
        matched_buildings = self.match_buildings(lat, lon, building_candidates)
        
        return {
            'buildings': matched_buildings,
            'grid_cell': grid_cell
        }
    
    def create_training_record(self, location: Dict[str, Any], matches: Dict[str, List]) -> Dict[str, Any]:
        """학습 데이터 레코드 생성"""
        return {
            'input': {
                'lcellid': location.get('lcellid', '').split(',') if location.get('lcellid') else [],
                'wmac': location.get('wmac', '').split(',') if location.get('wmac') else [],
                'wrssi': [float(x) if x != 'None' else None for x in location.get('wrssi', '').split(',')] if location.get('wrssi') else [],
                'ipcikey': location.get('lpciKey', '').split(',') if location.get('lpciKey') else [],
                'location': {
                    'latitude': location['latitude'],
                    'longitude': location['longitude']
                }
            },
            'answer': {
                'grid_cell': matches['grid_cell'],
                'buildings': [
                    {
                        'uid': b['uid'],
                        'height': b['height'],
                        'hstare': b['hstare'],
                        'lstare': b['lstare']
                    } for b in matches['buildings']
                ]
            }
        } 