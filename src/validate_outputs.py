"""轻量回归校验：每次重跑后确认口径恒等式和关键输出完整。"""
from pathlib import Path
import json
import pandas as pd
from typing import Optional

def validate(root: Path, data: Optional[Path] = None) -> None:
    data=data or root/'dashboard'/'data'
    monthly=pd.read_csv(data/'monthly_kpis.csv')
    quality=pd.read_csv(data/'data_quality.csv')
    summary=json.loads((data/'summary.json').read_text(encoding='utf-8'))
    assert (monthly['identity_gap'].abs() < 1e-6).all(), 'GMV 三因子恒等式不成立'
    assert summary['valid_orders'] > 0 and summary['valid_users'] > 0, '有效订单或用户为空'
    assert not quality.empty, '未输出数据质量检查'
    assert (data/'ab_simulation.json').exists(), '缺少统计检验输出'
    print('validation passed: identity, volume, quality, statistical output')

if __name__ == '__main__': validate(Path(__file__).resolve().parents[1])
