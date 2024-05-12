DATA_DIR=data/21_100k_20240512
EMPTIES=21

bin/mEdax -solve $DATA_DIR/obf -l 0 -verbose 1 > $DATA_DIR/eval_0.txt
#bin/mEdax -solve $DATA_DIR/obf -l 0 -verbose 3 > $DATA_DIR/eval_ref.txt
bin/mEdax -solve $DATA_DIR/obf -l $EMPTIES -verbose 1 > $DATA_DIR/eval_$EMPTIES.txt
