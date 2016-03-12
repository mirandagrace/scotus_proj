#!/bin/bash
for i in `seq 1990 1999`;
do
   scrapy crawl -a term=$i oyez
done 
