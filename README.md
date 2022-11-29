# Eastmoney_Guba_Forum_Comment_Web_Crawler
Instruction for revised version of Guba web-crawler
2022-07-27
Prepared by Zhenghai Chi
Content
1. Introduction	1
2. Background Information	1
3. Technical Details	2
4. Descriptive Statistics	5
Appendix	5

1. Introduction
This file is an instruction for the use of revised version of Guba Web-crawler, which is a crawler to scrape data from Guba forum. We collect data since 2017.01.01 based on the list of the Chinese listed firms according to the task requirements. We scrape the “下载时间yyyymmdd”, “阅读量”, “评论量”, “标题”, “作者”, “作者ID”, “帖子链接” and “发帖时间yyyymmdd” of each comment.
I suggest that we can collect data every month and each collection will finish in 10 hours.
Please clear the content in the relevant file or text (“error”, “cache”,“count”,“error”, “crawls”, “final_data”, “preliminary_data”, “repair_data” and “temporary_data”) instead of the files themselves. After finishing the steps in instruction, the final data will be saved in “revised version for Guba web-crawler\sharespider\final_data” directory.
The execution of this web-crawler is somewhat complex. This is because I design a second-time check mechanism, which is used to tackle the anti-crawler. However, if there is a time limitation, I suggest that we can ignore the second-time check mechanism and generate the final data directly (this may cause more erroneous data). The detail will be mentioned in section 3.
2. Background Information
1. Data Source: Eastmoney – Guba forum
2. Source Website: http://guba.eastmoney.com/list,000001,f.html (sample: 平安银行 - 000001) 000001 is the stock symbol，f. indicates the website comments are sorted by the post time.
3. Starting cut-off date for the crawling: 2017.01.01 for Eastmoney Guba forum
4. Ending cut-off date for the crawling: 2022.07.21 for Eastmoney Guba forum
5. Variable Definitions (there is only one sheet in each csv file):

Table 1
Variable	Definition
下载时间yyyymmdd	Download time (yyyymmdd)
阅读	The number of readings
评论	The number of comments
标题	Title of comment. Returning the blank if there is no title
作者	Author name. Returning the blank if there is no author name
作者ID	Author’s ID
帖子链接	Http of post
发帖时间yyyymmdd	Post time (yyyymmddhhmm)
3. Technical Details
Before running the code, please check if your environment has installed some packages. Or you can install these packages in the command interface in advance:
pip install xlrd == 1.2.0
pip install Scrapy

The idea of this program:
I divide the web crawler into four parts to scrape data.
1. I scrape the preliminary data of all listed firms from Guba.
2. Because there is no mark of year in Guba, I use the "add_year for preliminary data.py" to add the year mark.
3. Due to the anti-crawler, I write the "repair.py" code for further confirmation of files that the end date is at least early than 2017.1.1, and the "repair" will check if the data is enough and scrape the missing data again.
4. Finally, I use the "dele_tail" to delete data that is early than 2017.1.1 and finish this project.

Note:
1. The comment will be recorded as below if it uses some emoji. E.g.,
 
The comment will be recorded as “[怒] [怒] [怒]” in our final dataset.
2. There may appear that the ID is blank because of the account cancellation like “此账号已注销”, where we will record it as the blank.
3. The reason that some lacks appear is because of the different time points of web-crawler and second-time check (Some posts may be deleted, and the later check regards them as poison data and deletes the primal collection)

The detail of use of the code
1. firstly, typing “D:” in cmd (WIN+R to open the cmd, and confirm after typing “cmd”) interface (if you save the “revised version for Guba web-crawler” in D drive)
e.g., D:
 
 
Changing your directory to sharespider (please copy the directory and paste in cmd interface)
e.g., cd D:\revised version for Guba web-crawler\sharespider
 
Finally, typing “scrapy crawl guba -s JOBDIR=crawls/guba-1” in cmd interface, and it will store the cache in crawls file. If the program is interrupted, please typing the “scrapy crawl guba -s JOBDIR=crawls/guba-1” again, and the program will request the comment under the prior cache. It will spend 5 days to scrape three years’ comments via one computer.
2. Using the “add_year for preliminary data.py” to add a year for the preliminary data, where you can run the python code directly.
3. Using the “dele_tail.py”, which can detect the potential lack.
4. Before the fourth step, please opening the “pipelines.py” in “revised version for Guba web-crawler\sharespider\sharespider” directory and replacing the "preliminary_data/{}" with "repair_data/{}" in line 15. The detail is shown below:
 
 
Finishing all above, please running the “repair,py” in “revised version for Guba web-crawler\sharespider\sharespider\spiders” directory, which is similar to the use of “Guba.py”.
typing “D:” in cmd (WIN+R to open the cmd, and confirm after typing “cmd”) interface (if you save the “revised version for Guba web-crawler” in D drive)
e.g., D:
 
 
Changing your directory to sharespider (please copy the directory and paste in cmd interface)
e.g., cd D:\revised version for Guba web-crawler\sharespider
typing “scrapy crawl repair -s JOBDIR=crawls/repair-1”. Also, please typing the “scrapy crawl repair -s JOBDIR=crawls/repair-1” again and it will restart under the extant cache.
5. Then, use the “add_year for repair data.py” (about 3 hours)
6. Then, Running the “del_duplicate.py” (about 3 minutes)
7. Running the “dele_tail.py” (about 20 minutes)
8. Finally, replacing the “temporary_data” directory in “dele_duplicate.py” with “final_data”. Running the “dele_duplicate.py” again.
 
 
Finished. And the data will be saved in the “final_data” file.
Note: After step 2 above, the data has been scrapped already. If it is available to bear little wrong data (about 0.0003%), you can replace “preliminary_data” with “temporary_data” in line 4 of “dele_tail.py”. And then, running “dele_tail.py” directly, which can generate the data we need in “final_data” directory.

When you run code in cmd, it will be like this:
 
4. Descriptive Statistics
The number of stocks: 4984
Duplication: 1 (600018, 上港集箱/上港集团)
The number that we scrape: 4983
Appendix
This part is used to help you scrape any time span according to your demand (now is 2017.01.01).
Step 1: change the target time (stop time) at line 35 in “guba.py” (now, the stop time is 2017.1.1, please use YYMMDD format).
 
Step 2: change the target time (stop time) at line 82 in “repair.py” (same as step 1).
 
Step 3: add new year to the list according to your target time (stop time) at line 102 in “add_year for preliminary data.py” (now, the list includes 2017-2021 because our target time is 2017).
 
Step 4: add new year to the list according to your target time (stop time) at line 102 in “add_year for repair data.py” (same with step 3).
 
Step 5: add new year to list according to your target time (stop time) at line 12 in “dele_tail.py”.
 
And then, you can scrape data with any time span as you want.
