#!/bin/bash

# 국어
python main.py --test_file_path data/2024_국어_공통.json --model_type gpt-4-1106-preview
python main.py --test_file_path data/2024_국어_언어와매체.json --model_type gpt-4-1106-preview
python main.py --test_file_path data/2024_국어_화법과작문.json --model_type gpt-4-1106-preview

# 수학
python main.py --test_file_path data/2024_수학_공통.json --model_type gpt-4-1106-preview
python main.py --test_file_path data/2024_수학_기하.json --model_type gpt-4-1106-preview
python main.py --test_file_path data/2024_수학_미적.json --model_type gpt-4-1106-preview
python main.py --test_file_path data/2024_수학_확통.json --model_type gpt-4-1106-preview

# 영어
python main.py --test_file_path data/2024_영어.json --model_type gpt-4-1106-preview

