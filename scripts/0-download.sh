#!/bin/sh
# Downloads the COUGH dataset (CC BY-NC-SA 4.0, research and education use) into work/.
# Pinned to one commit so the numbers stay reproducible.
set -e
C=c6689b90757df3e0d1ae226044c79f50ac4f38ce
mkdir -p work && cd work
for f in FAQ_Bank_eval.csv User_Query_Bank.csv Annotated_Relevance_Set.csv; do
  curl -sSfL -o "$f" "https://raw.githubusercontent.com/sunlab-osu/covid-faq/$C/data/$f"
done
curl -sSfL -o List_of_websites.txt "https://raw.githubusercontent.com/sunlab-osu/covid-faq/$C/List_of_websites.txt"
echo "Downloaded to work/"
