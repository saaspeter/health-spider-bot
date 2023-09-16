抓取来自drugs.com的疾病
   drugs.com站点的疾病是按照字母顺序排列的，因此决定先用一个爬虫把从A到Z的疾病名称及其连接抓去下来，保存到db中，然后启动新爬虫，
读取这个疾病的列表，一个一个药物来爬取，存入db，这样如果第二个爬取具体疾病信息的爬虫中断了，也知道从哪条记录继续爬取，不需要所有疾病从头再来
全部爬取。因此需要两个爬虫：疾病名称爬虫(diseaselist_drugscom)和疾病Detail爬虫(diseasedetail_drugscom)。
   另外drugs.com 中的每种疾病有四个文章来源，如下。因为都是基础性的科普文章，我会先抓取：Mayo Clinic和Harvard health。 
   a) Browser By Conditions:  https://www.drugs.com,tag:conditions, 入口地址：https://www.drugs.com/alpha/condition
   b) IBM CareNotes:  https://www.drugs.com,tag:CareNotes, 入口地址：https://www.drugs.com/care_notes.html
   c) Mayo Clinic：https://www.drugs.com,tag:MayoClinic，入口处为：https://www.drugs.com/mcd/
   d) Harvard health, https://www.drugs.com,tag:HarvardHealth，入口处为： https://www.drugs.com/health-guide/

以下是Mayo Clinic的抓取设置：
1. drugslist爬虫：drugs站点的疾病列表的入口格式为：https://www.drugs.com/mcd/ ，参见json配置文件的 start_urls配置， 
   然后在这个页面中进入各疾病字母列表，再从单个字母页面中提取出疾病目录信息，参见rules.py中disease_list_drugs_mayo配置。
   抓取具体疾病目录，然后存入DB。
2. 针对DB中的疾病列表，然后抓去每个具体疾病信息，存入DB。例如：https://www.drugs.com/cons/ddavp.html

有一个大job来协调这两步，每个job包含了step1和step2, step1必须一次完成，不支持中断后续爬，step2可以支持中断爬取，中断后只需找到还未爬取的药品，
从那里开始爬取即可。step1和step2爬取成功后，可以清空爬取记录，等待下次爬取，也可以保留爬取记录，仅仅消除爬取状态，查缺补漏。

