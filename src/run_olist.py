"""兼容 Kaggle 原始 Olist 文件名并生成真实分析输出。"""
from pathlib import Path
import shutil
from analysis import run

root=Path(__file__).resolve().parents[1]
raw=root/'data/raw'
source_names={
    'olist_orders_dataset.csv':'orders.csv', 'olist_customers_dataset.csv':'customers.csv',
    'olist_order_items_dataset.csv':'order_items.csv', 'olist_order_payments_dataset.csv':'payments.csv',
    'olist_order_reviews_dataset.csv':'reviews.csv', 'olist_products_dataset.csv':'products.csv',
}
has_kaggle_raw=any((raw/source).exists() for source in source_names)
if not has_kaggle_raw and (raw/'DATA_MODE.txt').exists() and (raw/'DATA_MODE.txt').read_text(encoding='utf-8').strip() == 'SIMULATED_DEMO':
    raise RuntimeError('检测到模拟数据。请先放入 Kaggle Olist 原始 CSV，再执行真实数据入口。')
for source, target in source_names.items():
    if (raw/source).exists(): shutil.copyfile(raw/source,raw/target)
required=['orders.csv','customers.csv','order_items.csv','payments.csv','reviews.csv','products.csv']
missing=[target for target in required if not (raw/target).exists()]
if missing: raise FileNotFoundError(f'缺少 Olist 必需文件: {missing}')
(raw/'DATA_MODE.txt').write_text('OLIST_ACTUAL\n', encoding='utf-8')
print(run(raw,root/'dashboard/data',data_mode='OLIST_ACTUAL'))
