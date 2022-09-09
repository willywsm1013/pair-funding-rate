# Run this script to download data
for symbol in btt kbtt shib kshib sos ksos lunc klunc
do
    python get_data.py $symbol
done
