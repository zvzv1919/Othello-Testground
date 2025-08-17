1. in search, get moves gets called duplicatively (in is_game_over and main body), can optimize
2. board can be passed by ref.
3. benchmarking: `time(./val-search ../data/5_100k_20240510/obf > ../data/5_100k_20240510/eval_5_validate.txt)`