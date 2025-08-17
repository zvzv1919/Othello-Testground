DATA_DIR=data/16_130k_wthor19772023
EMPTIES=16

bin/mEdax -solve $DATA_DIR/obf -l 0 -verbose 1 > $DATA_DIR/eval_0.txt
bin/mEdax -solve $DATA_DIR/obf -l 0 -verbose 3 > $DATA_DIR/eval_ref.txt
bin/mEdax -solve $DATA_DIR/obf -l $EMPTIES -verbose 1 > $DATA_DIR/eval_$EMPTIES.txt
