"""一键生成模拟数据并执行完整分析。"""
from pathlib import Path
from generate_demo_data import generate
from analysis import run
from validate_outputs import validate

root=Path(__file__).resolve().parents[1]
generate(root/'data/raw')
demo_output=root/'dashboard'/'demo_data'
print(run(root/'data/raw',demo_output,data_mode='SIMULATED_DEMO'))
validate(root,demo_output)
