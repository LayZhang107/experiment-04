# Prompt 与 AI 解释模板

请把每条评论编码为 JSON，保留 review_id，并从原文中摘录 evidence。允许的主题包括：价格、音质、降噪、佩戴舒适、续航、配送、包装、通话、连接稳定、外观。允许的情绪包括 positive、neutral、negative、mixed、unknown。

约束：
1. 不从评分单独推断痛点。
2. evidence 必须是 review_text 的原文子串。
3. 无法判断时使用 unknown 或 none。
4. Python 负责计数、分组、排序和占比，AI只负责语义编码和解释。
5. 解释必须分为事实、推断和建议，并引用 review_id。

本次本地运行保留相同 JSON 契约，以便后续替换为大模型编码器后复用统计程序。
