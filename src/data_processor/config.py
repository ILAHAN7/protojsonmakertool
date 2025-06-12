from dataclasses import dataclass
from typing import Dict
import configparser
import os

@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

@dataclass
class ProcessorConfig:
    batch_size: int = 1000
    spatial_margin: float = 0.01  # 위도/경도 검색 마진
    building_precise_check: bool = True  # 건물 정밀 검사 여부
    cell_index_type: str = 'btree'  # 셀 인덱스 타입
    cache_enabled: bool = True  # 캐시 사용 여부
    cache_size: int = 1000  # 캐시 크기
    building_search: bool = False  # 빌딩 탐색 여부

class Config:
    def __init__(self, config_path: str):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # DB 설정
        self.db = DBConfig(
            host=self.config['database']['host'],
            port=int(self.config['database']['port']),
            user=self.config['database']['user'],
            password=self.config['database']['password'],
            database=self.config['database']['database']
        )
        
        # 처리 설정
        self.processor = ProcessorConfig(
            batch_size=int(self.config.get('processor', 'batch_size', fallback='1000')),
            spatial_margin=float(self.config.get('processor', 'spatial_margin', fallback='0.01')),
            building_precise_check=self.config.getboolean('processor', 'building_precise_check', fallback=True),
            cell_index_type=self.config.get('processor', 'cell_index_type', fallback='btree'),
            cache_enabled=self.config.getboolean('processor', 'cache_enabled', fallback=True),
            cache_size=int(self.config.get('processor', 'cache_size', fallback='1000')),
            building_search=self.config.getboolean('processor', 'building_search', fallback=False)
        ) 