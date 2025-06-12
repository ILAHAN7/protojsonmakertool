from data_processor.db_connector import DBConnector
from data_processor.config import Config

def check_table_structure():
    config = Config('config/db_config.ini')
    db = DBConnector(config.db)
    
    # 테이블 목록 조회
    tables = db.execute_query('SHOW TABLES')
    print("\nAvailable tables:", [table[f'Tables_in_{config.db.database}'] for table in tables])
    
    # 각 테이블의 구조 확인
    for table in tables:
        table_name = table[f'Tables_in_{config.db.database}']
        print(f"\nStructure of {table_name}:")
        columns = db.execute_query(f'DESCRIBE {table_name}')
        for col in columns:
            print(f"  {col['Field']}: {col['Type']}")

if __name__ == '__main__':
    check_table_structure() 