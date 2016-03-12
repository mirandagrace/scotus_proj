#!/bin/bash

python trial.py

for i in `seq 1990 2014`;
do
   scrapy crawl -a term=$i oyez
done 
