from typing import Dict, Any, List
import numpy as np

class GridCellMatcher:
    """그리드 기반 셀 매칭 클래스"""
    # 그리드 셀 상수
    ORG_MIN_X = 124.54117
    ORG_MIN_Y = 32.928463
    ORG_MAX_X = 130.57113
    ORG_MAX_Y = 42.344405
    OFFSET_5M_X = 0.0000555
    OFFSET_5M_Y = 0.0000460
    DEFAULT_LEVEL = 5  # 25m 그리드 셀

    def match(self, lat: float, lon: float) -> Dict[str, Any]:
        """단일 위치에 대한 그리드 셀 ID 계산"""
        x_id = int((lon - self.ORG_MIN_X) / (self.OFFSET_5M_X * self.DEFAULT_LEVEL)) + 1
        y_id = int((lat - self.ORG_MIN_Y) / (self.OFFSET_5M_Y * self.DEFAULT_LEVEL)) + 1
        return {
            'x_id': x_id,
            'y_id': y_id
        }

    def match_batch(self, lats: List[float], lons: List[float]) -> List[Dict[str, Any]]:
        """여러 위치에 대한 그리드 셀 ID 일괄 계산"""
        # NumPy 배열로 변환
        lats_arr = np.array(lats)
        lons_arr = np.array(lons)
        
        # 벡터화된 계산
        x_ids = ((lons_arr - self.ORG_MIN_X) / (self.OFFSET_5M_X * self.DEFAULT_LEVEL)).astype(int) + 1
        y_ids = ((lats_arr - self.ORG_MIN_Y) / (self.OFFSET_5M_Y * self.DEFAULT_LEVEL)).astype(int) + 1
        
        # 결과를 딕셔너리 리스트로 변환
        return [{'x_id': x, 'y_id': y} for x, y in zip(x_ids, y_ids)] 