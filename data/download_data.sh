# Run this script to download data
for symbol in btt kbtt shib kshib sos ksos
do
    python get_data.py $symbol
done
