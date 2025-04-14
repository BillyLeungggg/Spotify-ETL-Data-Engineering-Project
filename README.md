# Spotify-ETL-Data-Engineering-Project

### 
I built an ETL pipeline by using the Spotify API on AWS. The pipeline will automaically retreive the data from the Spotify API, then transform the data into designated format. After that, the reformed data will be loaded into AWS data store.

##
Architecture 
![Architecture Diagram](https://github.com/BillyLeungggg/Spotify-ETL-Data-Engineering-Project/blob/main/Data%20pipeline%20architecture.png)

###
Service used on AWS

- S3 (Simple Storage Service) : Store and retrieve data on the Web
- Lambda : Run the code wihout managing servers
- Cloud Watch : To collect and track metrics, monitor log files and set alarm
- Glue crawler : Automatically crawl the data source, identifies data format and infers schemas to create an AWS Glue Data Catalog.
- 
