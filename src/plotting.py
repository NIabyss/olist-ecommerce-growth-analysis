"""输出报告可复用图表。"""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def make_figures(data_dir: Path, figure_dir: Path) -> None:
    figure_dir.mkdir(parents=True,exist_ok=True)
    m=pd.read_csv(data_dir/'monthly_kpis.csv'); r=pd.read_csv(data_dir/'rfm_summary.csv')
    plt.style.use('seaborn-v0_8-whitegrid')
    fig,ax=plt.subplots(figsize=(9,4)); ax.plot(m.purchase_month,m.gmv,marker='o'); ax.set(title='Monthly GMV',xlabel='Month',ylabel='GMV'); ax.tick_params(axis='x',rotation=45); fig.tight_layout(); fig.savefig(figure_dir/'monthly_gmv.png',dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4)); ax.bar(r.segment.map({'高价值':'High value','潜力':'Potential','需唤回':'Win-back','沉睡':'Dormant'}),r.revenue); ax.set(title='RFM revenue contribution',xlabel='Segment',ylabel='GMV'); fig.tight_layout(); fig.savefig(figure_dir/'rfm_revenue.png',dpi=160); plt.close(fig)

if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]; make_figures(root/'dashboard/data',root/'reports/figures')
