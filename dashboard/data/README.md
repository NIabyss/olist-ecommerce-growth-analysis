# 仪表盘数据输出

这个目录下的文件是我跑 `src/run_demo.py` 或 `src/run_olist.py` 后自动生成的,不是手工整理的。`order_fact.csv` 是订单级明细,体积比较大、内容也接近原始数据,我把它加进了 `.gitignore`;其余的聚合 CSV 都可以直接拿去 Power BI / Tableau 里导入用。

上传 GitHub 之前,我都会再确认一遍 `summary.json` 里的 `data_mode` 是不是和 README、报告里写的说法一致——模拟跑出来的数据绝不能被标成真实的 Olist 结果,这是我对这个项目的底线。
