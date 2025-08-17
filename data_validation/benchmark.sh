pushd ..
DATA_DIR=data/5_100k_20240510
EMPTIES=5

time(data_validation/val-search $DATA_DIR/obf > $DATA_DIR/eval_${EMPTIES}_validate.txt)
time(bin/mEdax -solve $DATA_DIR/obf -l $EMPTIES -verbose 1 > $DATA_DIR/eval_${EMPTIES}.txt)

popd