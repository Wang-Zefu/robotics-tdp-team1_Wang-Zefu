# Alpha 参数小规模测试报告

## 环境信息
- Python: `3.12.12`
- Platform: `Linux-6.12.47-x86_64-with-glibc2.39`
- Git commit: `f99bbf0`
- 测试时间(UTC): `2026-03-04 17:02:45`

## 安装依赖
- `python -m pip install setuptools wheel`
- `python -m pip install numpy scipy pyrusgeom coloredlogs humanfriendly matplotlib pytest`

## 测试命令
- `cd Pyrus2D && python run_alpha_comparison.py --alphas 0.2 0.8 --matches 2 --duration 60 --workers 2 --no-falls --output alpha_results_smoke`

## 结果汇总

| 配置 | 场次 | 蓝队总进球 | 红队总进球 | 蓝胜 | 红胜 | 平局 |
|---|---:|---:|---:|---:|---:|---:|
| a0p20_vs_a0p20 | 2 | 0 | 0 | 0 | 0 | 2 |
| a0p20_vs_a0p80 | 2 | 0 | 0 | 0 | 0 | 2 |
| a0p80_vs_a0p20 | 2 | 0 | 0 | 0 | 0 | 2 |
| a0p80_vs_a0p80 | 2 | 0 | 0 | 0 | 0 | 2 |

- 原始结果文件数: `8`（目录：`Pyrus2D/alpha_results_smoke/`）
- 说明：本次仅为 smoke test（小规模连通性验证），用于确认 α 参数测试流程可运行。
