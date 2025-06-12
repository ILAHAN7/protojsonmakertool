@echo off
set PYTHONPATH=src
python -m data_processor --config config/db_config.ini --start-id %1 --end-id %2 --output output/result.jsonl 