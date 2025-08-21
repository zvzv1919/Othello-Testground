pushd ..
# DATA_DIR=data/5_100k_20240510
# EMPTIES=5
# time(data_validation/val-search $DATA_DIR/obf > $DATA_DIR/eval_${EMPTIES}_validate.txt)
# real    0m3.520s
# user    0m3.200s
# sys     0m0.307s
# time(bin/mEdax -solve $DATA_DIR/obf -l $EMPTIES -verbose 1 > $DATA_DIR/eval_${EMPTIES}.txt)
# real    22m2.854s
# user    17m50.721s
# sys     0m13.238s

DATA_DIR=data/test
EMPTIES=8
time(data_validation/val-search $DATA_DIR/obf)
# real    0m3.520s
# user    0m3.200s
# sys     0m0.307s
# time(bin/mEdax -solve $DATA_DIR/obf -l $EMPTIES -verbose 1 > $DATA_DIR/eval_${EMPTIES}.txt)
# real    22m2.854s
# user    17m50.721s
# sys     0m13.238s

popd