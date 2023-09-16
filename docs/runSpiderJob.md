一、运行List Job的过程:
1. 运行run.py，后面跟一个参数：配置json文件的名称，例如：disease_list_drugs_mayo
2. 运行的时候会重新插入一条记录到kh_spider_job表中，同时把旧的job记录删除，包括kh_spider_job_items中的具体记录。
3. 从制定的list页面抓取记录，存储在kh_spider_job_items表中。


二、运行Detail Job的过程：

1. 在运行完list job后在kh_spider_job中就会有条记录，对应的在kh_spider_job_items中会有跟多的需要爬取的药物或疾病记录。
2. 运行run.py，参数是json文件的名字，例如：medicine_detail_drugs
3. 查看运行结果，log记录在spider_run.log中
4. 查看db的记录：

   a) kh_spider_job中的status_detail应该为3，同时total_detail_finished的值应该和total_number_list的值一样，
   代表成功抓取detail article的数目和list job中获取的数据一样。
       select * from kh_spider_job where job_id=3;
   
   b) 检查kh_spider_job_items中本次job_id的记录中status是否都是3，如果有不是3的记录，代表失败的记录。
       select * from kh_spider_job_items where job_id=3 and status!=3;

5. 如果上述两步骤中有错误的记录，查看错误原因，并修复程序或数据。然后用下面的语句来设置未成功进行的记录：

   -- 查询detail job中失败的item在文章表中是否有残留记录：kh_medicine_article，如果有不完成记录需要先删除，然后重新运行detail job。
   select * from kh_medicine_article where source_url in(select source_url from kh_spider_job_items where status!=3 and job_id=?);
      -- 查询disease的记录
   select * from kh_disease_article where source_url in(select source_url from kh_spider_job_items where status!=3 and job_id=?);

   -- 如果kh_disease表或kh_medicine表中有不完成的记录，可以删除
   select * from kh_disease where spider_job_id=?

   -- 修复kh_spider_job_items中失败记录的状态，设为1代表还未开始
   update kh_spider_job_items set status=1,spider_time=null,spider_end_time=null where job_id=3 and status=2;
   update kh_spider_job set status_detail=1,end_time_detail=null,total_detail_finished=0 where job_id=3;

6. 如果成功了一部分，失败了一部分记录，例如被限流：
   -- a) 查询kh_disease_article中已经成功的记录是否和kh_disease_article_detail表中的记录相同，如果detail中记录缺失，需要把kh_disease_article中的记录也删除。
   
   -- b) 查询kh_spider_job_items表中失败的记录，并把不正确的状态(2,4) 改为‘未开始’
   select * from kh_spider_job_items where job_id=? and status not in(1,3); -- 3: success
   update kh_spider_job_items set status=1,spider_time=null,spider_end_time=null where job_id=? and status in(2,4);

   -- c) 更改job的状态 
   update kh_spider_job set status_detail=1,end_time_detail=null where job_id=?;
   



