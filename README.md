# protojsonmakertool

## Overview

**protojsonmakertool** is a Python tool for batch extracting and processing spatial (location) data from a MySQL database, converting it into JSONL format suitable for machine learning training. It efficiently handles large-scale data, supports grid cell and building matching, and provides dual output formats for both raw and ML-ready data.

---

## Project Structure

```
soxmodulerprto/
├── config/                  # Configuration files
│   └── db_config.ini        # DB and processor settings
├── output/                  # Output files
│   ├── result.jsonl         # Original results
│   └── result_traindata.jsonl  # ML training data
├── sampleDBdata/            # Sample DB data
│   ├── building_*.csv
│   ├── cellidindex_*.csv
│   └── collectxy_*.csv
├── src/
│   └── data_processor/      # Core processing modules
│       ├── __main__.py
│       ├── batch_processor.py
│       ├── cell_matcher.py
│       ├── check_data.py
│       ├── check_tables.py
│       ├── config.py
│       ├── db_connector.py
│       └── spatial_matcher.py
├── requirements.txt         # Python dependencies
├── run.bat                  # Windows run script
├── run.py                   # Simple run wrapper
└── README.md                # Documentation
```

---

## Features
- **Batch Processing**: Efficiently processes data in user-defined batch sizes
- **Grid Cell & Building Matching**: Supports spatial matching of coordinates and buildings
- **Performance Statistics**: Outputs detailed stats (processing time, DB read time, etc.)
- **Dual Output**: Generates both original JSONL and ML training JSONL formats

---

## Requirements
- Python 3.11+
- MySQL database
- Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration
Edit `config/db_config.ini` to set DB connection, batch size, and matching options:

```
[database]
host = localhost
user = youruser
password = yourpassword
database = yourdb

[processor]
batch_size = 100
building_search = true
grid_size = 0.001
```

---

## Usage

### 1. Run with `run.py`

```bash
python run.py <start_id> <end_id>
```
Example:
```bash
python run.py 53749 53849
```

### 2. Run as a module

```bash
python -m src.data_processor --config config/db_config.ini --start-id 53749 --end-id 53849 --output output/result.jsonl
```

---

## Output Example

### Original JSONL (`result.jsonl`)
```json
{
  "input": {
    "lcellid": ["123,456", "789,012"],
    "wmac": ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"],
    "wrssi": [-75, -82],
    "ipcikey": ["key1", "key2"]
  },
  "answer": {
    "grid_cell": {"x_id": 123, "y_id": 456},
    "buildings": [
      {"id": 789, "name": "Example Building", "distance": 25.3}
    ]
  }
}
```

### ML Training JSONL (`result_traindata.jsonl`)
```json
{
  "prompt": "wmac=AA:BB:CC:DD:EE:FF,11:22:33:44:55:66 wrssi=-75,-82 lcellid=123,456,789,012 ipcikey=key1,key2",
  "completion": "x_id=123,y_id=456"
}
```

---

## Performance Statistics
- Outputs total processing time, record count, DB read/match time, throughput, and more after each run.

---
