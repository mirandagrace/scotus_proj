# scotus_proj
The repository is for my statistical learning class project. It will contain code to generate the datasets, and then apply several machine learning algorithms to it.

## The Data

### Supreme Court Database
The first data set that I will be using for this project is [The Supreme Court Database](http://supremecourtdatabase.org/index.php). They provide several different formats of the data for download but what I really need is the data in an relational database. So I have written functions to parse the csv files and store them in a relational database.

### Argument Transcripts
The second data set I will be using for this project is argument transcripts scraped from [Oyez](http://oyez.org). To this end I have written a webcrawler using scrapy to crawl the site and add the data to the relational database.

### Opininons
TODO: Make a database of opinions.

## Utility Functions and Classes
There are a variety of utilities that I have written as part of this project.

### Build
Because populating my relational database takes some time I have created a build class that allows me to incrementally build up my database without reprocessing data unnecessarily.

## Algorithms
I will eventually attempt to use this data to train machine learning algorithms to automatically summarize the opinions, among other things as data completeness and time permit.
