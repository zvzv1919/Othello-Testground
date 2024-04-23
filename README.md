# Othello-Testground
A platform to execute and analyse Othello games between AIs (human included) \
GPL license inherited from [Edax](https://github.com/abulmo/edax-reversi)    
 

TODO: Installation guide
# Dev
Conda env: `conda activate othello_testground` \
Game generation: use edax C code to produce search results in a queue `derived_states`. Python interface should be defined in a central location (currently `bench.py` together with benching tools). \
Eval net training: consume from `derived_states`

## TODO:
1. Output game records
2. Reconstruct games from game records (check edax codebase first)

## C library dev cycle
1. Make code change in .c files, API change in .h files. Put additional APIs in pyutils.h
2. under `/edax_src`, `make build-so`
3. Rerun `main.py` to load the changes
4. Log the changes in pyutils.h for ref

## Optimization Ideas
1. Use mq (kafka) to smooth out game generation and eval net training
2. Organize C library functions into a class so that the library only needs to be load once
3. Use `cython` compilation instead of `ctypes` between python and C code
4. Use [Zobrist Hashing](https://en.wikipedia.org/wiki/Zobrist_hashing) for compact gameboard representation

## Known Issues
1. Sometimes game result has less aggregated games than total games![Wrong Game result.png](resources%2FWrong%20Game%20result.png)

# Reference
https://github.com/ianlokh/Othello/tree/master
https://github.com/abulmo/edax-reversi


