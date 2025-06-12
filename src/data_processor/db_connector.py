import mysql.connector
from mysql.connector import pooling
from typing import List, Dict, Any, Optional
from decimal import Decimal
from .config import Config, DBConfig
import psycopg2

class DBConnector:
    # 그리드 셀 상수
    ORG_MIN_X = 124.54117
    ORG_MIN_Y = 32.928463
    OFFSET_5M_X = 0.0000555
    OFFSET_5M_Y = 0.0000460
    DEFAULT_LEVEL = 5

    def __init__(self, config: DBConfig):
        self.config = config
        self.pool_config = {
            'pool_name': 'mypool',
            'pool_size': 5,
            'host': config.host,
            'port': config.port,
            'user': config.user,
            'password': config.password,
            'database': config.database
        }
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**self.pool_config)
        self.conn = None
        self.connect()
    
    def connect(self):
        """데이터베이스 연결"""
        if not self.conn or self.conn.closed:
            self.conn = mysql.connector.connect(
                host=self.pool_config['host'],
                port=self.pool_config['port'],
                database=self.pool_config['database'],
                user=self.pool_config['user'],
                password=self.pool_config['password']
            )

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """쿼리 실행 및 결과 반환"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Decimal 타입을 문자열로 변환
            for row in results:
                for key, value in row.items():
                    if isinstance(value, Decimal):
                        row[key] = str(value)
            
            return results
        finally:
            cursor.close()
            connection.close()
    
    def get_collectxy_batch(self, start_id: int, end_id: int) -> List[Dict[str, Any]]:
        """Collectxy 테이블에서 배치 데이터 조회 및 그리드 셀 계산"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    id,
                    latitude, 
                    longtitude,
                    lcellid,
                    wmac,
                    wrssi,
                    lpciKey,
                    FLOOR(((longtitude - %s) / (%s * %s)) + 1) as x_id,
                    FLOOR(((latitude - %s) / (%s * %s)) + 1) as y_id
                FROM collectxy 
                WHERE id BETWEEN %s AND %s
                ORDER BY id
            """, (
                self.ORG_MIN_X, self.OFFSET_5M_X, self.DEFAULT_LEVEL,
                self.ORG_MIN_Y, self.OFFSET_5M_Y, self.DEFAULT_LEVEL,
                start_id, end_id
            ))
            
            results = []
            for row in cursor.fetchall():
                # Decimal 타입을 float로 변환
                lat = float(row['latitude']) if isinstance(row['latitude'], Decimal) else row['latitude']
                lon = float(row['longtitude']) if isinstance(row['longtitude'], Decimal) else row['longtitude']
                
                results.append({
                    'id': row['id'],
                    'latitude': lat,
                    'longitude': lon,  # API 응답은 'longitude'로 통일
                    'lcellid': row['lcellid'],
                    'wmac': row['wmac'],
                    'wrssi': row['wrssi'],
                    'ipcikey': row['lpciKey'],  # DB는 lpciKey, API는 ipcikey로 통일
                    'grid_cell': {
                        'x_id': int(row['x_id']),
                        'y_id': int(row['y_id'])
                    }
                })
            return results
            
        finally:
            cursor.close()
            connection.close()

    def get_building_candidates(self, lat: float, lon: float, margin: float) -> List[Dict[str, Any]]:
        """Building 후보군 조회"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
            SELECT 
                uid, height, hstare, lstare,
                minX, maxX, minY, maxY
            FROM building
            WHERE minX <= %s AND maxX >= %s
              AND minY <= %s AND maxY >= %s
            """, (
                lon + margin, lon - margin,
                lat + margin, lat - margin
            ))
            
            results = cursor.fetchall()
            # Decimal 타입을 float로 변환
            for row in results:
                if isinstance(row['height'], Decimal):
                    row['height'] = float(row['height'])
            return results
            
        finally:
            cursor.close()
            connection.close()
    
    def get_cellindex_candidates(self, lat: float, lon: float, margin: float) -> List[Dict[str, Any]]:
        """Cellindex 후보군 조회 - 단순 인덱스 활용"""
        query = """
        SELECT lcellids, minX as min_x, maxX as max_x, minY as min_y, maxY as max_y
        FROM cellidindex
        WHERE minX <= %s AND maxX >= %s
          AND minY <= %s AND maxY >= %s
        """
        return self.execute_query(query, (
            lon + margin, lon - margin,
            lat + margin, lat - margin
        ))
    
    def ensure_spatial_indexes(self):
        """공간 인덱스 존재 확인 및 생성"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()
        
        try:
            # Building bbox 인덱스
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_building_bbox 
            ON building (minX, maxX, minY, maxY)
            """)
            
            # Cell bbox 인덱스
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cell_bbox 
            ON cellidindex (minX, maxX, minY, maxY)
            """)
            
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close() 