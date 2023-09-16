# health-spider-bot

web spider drugs and disease articles from different websites, 
using an enhanced python scrapy framework, you can only need json config file to grab from different website source,
and store articles into db, and support spider jobs and can rerun the job

Features:
1. support grab data from different websites, only need to write json config files for that website.
2. the spider process support schedule job to run, and rerun job from db record, so the spider can be divided into serval times incase the items are too much, also can escape the possible rate limit for bot from the website.
3. the data will be stored into the mysql db
4. if you want to load the data into a vector db, you can refer to my another project: https://github.com/saaspeter/vectorDB-data-convert , so the data can be grabbed from different websites and stored into Chroma DB smoothly.
5. the config file in this project support to grab data from drugs.com which include: Mayo Clinic and Harvard health.

How the process works:
Since I checked some website's articles, the structure is similar, there is one drugs/diseases list, the click the item can see the detail,
so I use the two phrases for each website source, the drugs tasks are: "spider_medicine_list" and "spider_medicine_details", for the disease, 
the tasks are "spider_disease_list" and "spider_disease_detail". By doing this we can schedule a spider job easily and we can grab a website's data in different process and support re-run, 
we can see the progressing in the db table: kh_spider_job(a total planning record number and how many finished and how many are left), 
we can see all the article items brief info in table: kh_spider_job_items (name, site, url)
For details see: /docs

How to Run: 
1. config your db connection in setting.py
2. run the list process phrase: e.g: python3 run.py disease_list_drugs ("disease_list_drugs" is the name of json file in folder configs),
   which will grab all the drugs/disease item name into db table: kh_spider_job
3. run the detail process phrase: e.g: python3 run.py disease_detail_drugs. If you just want to get each detail item content, please skip step2 list step.
4. about the log file, you can set the log file path in the pycharm IDE, e.g: /health-spider-bot/spider_run.log, and the console will also print the progress information.
5. for more details, see: docs/runSpiderJob.md

for more details, please see the docs folder in the project, since I am a Chinese, so my notes are in Chinese, you can translate them.

Notes:
    parts of the project's dependency is in docs/requirements.md, but some may not be included in it, e.g: Chroma dependency. 
The project log is in spider_running.log 