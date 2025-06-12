from data_processor.db_connector import DBConnector
from data_processor.config import Config

def check_data():
    config = Config('config/db_config.ini')
    db = DBConnector(config.db)
    
    # collectxy 데이터 확인
    result = db.execute_query('SELECT MIN(id) as min_id, MAX(id) as max_id, COUNT(*) as count FROM collectxy')
    print("\nCollectxy stats:")
    print(f"  Total records: {result[0]['count']}")
    print(f"  ID range: {result[0]['min_id']} - {result[0]['max_id']}")
    
    # 샘플 데이터 확인
    if result[0]['count'] > 0:
        sample = db.execute_query('SELECT * FROM collectxy LIMIT 1')
        print("\nSample record:")
        for key, value in sample[0].items():
            print(f"  {key}: {value}")
    
    # Building 데이터 확인
    result = db.execute_query('SELECT COUNT(*) as count FROM building')
    print("\nBuilding count:", result[0]['count'])
    
    # Cellidindex 데이터 확인
    result = db.execute_query('SELECT COUNT(*) as count FROM cellidindex')
    print("\nCellidindex count:", result[0]['count'])

if __name__ == '__main__':
    check_data() 