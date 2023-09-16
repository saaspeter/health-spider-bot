抓取来自drugs.com的药品
   drugs.com站点的药品是按照字母顺序排列的，因此决定先用一个爬虫把从A到Z的药品名称及其连接抓去下来，保存到db中，然后启动新爬虫，
读取这个药品的列表，一个一个药物来爬取，存入db，这样如果第二个爬取具体药品信息的爬虫中断了，也知道从哪条记录继续爬取，不需要所有药品从头再来
全部爬取。因此需要两个爬虫：药品名称爬虫(druglist_drugscom)和药品Detail爬虫(drugdetail_drugscom)。另外drugs中的每种药物有两个文章，
一个是Patient Info，针对普通患者阅读的，另一个是：Professional Monographs，具体而详细的药物说明书，两种说明我都想获取，但在app上仅展示Patient Info。
    
1. drugslist爬虫：drugs站点的药品列表的入口格式为：https://www.drugs.com/alpha/{从a-z的小写字母}.html ，如https://www.drugs.com/alpha/d.html， 进入这个字母后又是一个list页面，
   这个页面又是一个二级字母的列表，如：https://www.drugs.com/alpha/dd.html ，因此先从第一个首字母链接爬取，从该页面中找到第二个字母索引的链接，
   然后在读取的页面中抓取该页面中的药品列表名称及链接，存入DB。前面是Patient Info的链接格式，如果是 Professional Monographs页面，则链接后加上?pro=1，
   如：https://www.drugs.com/alpha/d.html?pro=1 ， https://www.drugs.com/alpha/da.html?pro=1 。
   Professional Monographs其实就是FDA PI的药物。执行的结果是将爬取的药物数据存入DB。
   初始的开始url配置见：json配置文件中的 start_requests配置节点，二级页面中的配置见：rules.py中的配置。
2. 针对DB中的药物列表，然后抓去每个具体药物信息，存入DB。例如：https://www.drugs.com/cons/ddavp.html

有一个大job来协调这两步，每个job包含了step1和step2, step1必须一次完成，不支持中断后续爬，step2可以支持中断爬取，中断后只需找到还未爬取的药品，
从那里开始爬取即可。step1和step2爬取成功后，可以清空爬取记录，等待下次爬取，也可以保留爬取记录，仅仅消除爬取状态，查缺补漏。

可以写一个主python脚本协调并启动这两步。


-------------------------------------------------------------------------------------------------------
---------- json config file 配置 ----------
-------------------------------------------------------------------------------------------------------
1. 在“item”->"attrs"下的配置字段中，“xpath”方法将字段的值提取出来后，如果想要继续处理则没有什么好办法了，因为loader.add_xpath
   方法是原有的方法，如果想要继续进一步处理的话，则需要修改loader类方法，过于麻烦。原来的设计应该是尽量用xpath,css等把值从html node
   中解析出来，所以直接用loader中提供的原有方法就可以，但是有时候需要更复杂的二次处理，写自己的方法。所以我添加了一个属性，对一个字段
   可以添加两个或多个方法，如果加上"after_load": "1", 说明这个方法是等loader.load_item()被调用生成了Item后再对这个属性进行
   指定新方法的调用。参见medicine_detail_drugs.json中的name_temp字段的extractNameTemp的配置。
2. 

