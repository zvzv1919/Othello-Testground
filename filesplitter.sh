#!/bin/bash

# Check if the file path is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file_path>"
    exit 1
fi

# Input file path
FILE=$1

# Count the total number of lines in the file
TOTAL_LINES=$(wc -l < "$FILE")
echo $TOTAL_LINES

# Calculate the line to split at; using awk to round up if odd
MID_LINE=$(( (TOTAL_LINES + 1) / 2 ))
echo $MID_LINE

# Split the file into two halves
sed -n "1,${MID_LINE}p" "$FILE" > test_obf_16_1M_20240509_3.txt
sed -n "$((MID_LINE + 1)),${TOTAL_LINES}p" "$FILE" > test_obf_16_1M_20240509_4.txt

echo "The file has been split into 'first_half.txt' and 'second_half.txt'."
