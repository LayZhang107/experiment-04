# 实验四：蓝牙降噪耳机消费者洞察引擎 v0.4

## 品牌与数据

本项目使用四个竞品品牌：索尼、Bose、Apple AirPods、华为 FreeBuds。原始数据为教学模拟数据，共402条；清洗去重后399条有效评论。

## 运行

```powershell
C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe src/consumer_insight_engine.py
C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tests/test_engine.py
```

## 输出

- `data/raw/raw_data.csv`：含缺失值、重复记录、价格格式差异、品牌缩写、日期格式差异和异常评分的原始数据
- `data/processed/clean_data.csv`：清洗去重后的数据
- `data/encoded/encoded_reviews.json`：评论语义编码和原文证据
- `outputs/pain_point_statistics.csv`：痛点计数、分母和占比
- `outputs/brand_topic_statistics.csv`：品牌-主题负面统计
- `outputs/evidence_table.csv`：重点结论的评论证据
- `outputs/inspection_10.csv`：10条人工抽检记录
- `outputs/dashboard.html`：Dashboard
- `outputs/insight_report.md`：洞察报告

GitHub Skill 来源和适配说明见 `docs/github_skill_usage.md`。
