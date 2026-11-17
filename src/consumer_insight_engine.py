from pathlib import Path
import csv, json, random, re
from datetime import date, timedelta
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data'/'raw'/'raw_data.csv'
CLEAN = ROOT/'data'/'processed'/'clean_data.csv'
ENC = ROOT/'data'/'encoded'/'encoded_reviews.json'
OUT = ROOT/'outputs'
random.seed(20261117)

brands = {
    '索尼': {'product':'WH-1000XM5', 'price': [2399,2699], 'style':'旗舰降噪'},
    'Bose': {'product':'QuietComfort Ultra', 'price': [2499,2999], 'style':'沉浸降噪'},
    'Apple AirPods': {'product':'AirPods Pro 2', 'price': [1599,1899], 'style':'生态便捷'},
    '华为 FreeBuds': {'product':'FreeBuds Pro 3', 'price': [1099,1499], 'style':'通话清晰'},
}
texts = [
 ('positive','音质细腻，低音有力度，通勤听歌很舒服',['音质','通勤']),
 ('positive','降噪效果明显，地铁里也很安静',['降噪','通勤']),
 ('positive','佩戴轻，长时间办公耳朵不累',['佩戴舒适','办公']),
 ('positive','续航很稳，一周充一次就够了',['续航','办公']),
 ('positive','连接很快，切换设备方便',['连接稳定','办公']),
 ('positive','包装完整，配送速度很快',['包装','配送']),
 ('positive','外观简洁，做工有质感',['外观','居家']),
 ('positive','通话清楚，线上会议没有杂音',['通话','办公']),
 ('negative','价格偏高，促销少，性价比一般',['价格','性价比']),
 ('negative','降噪有时会有风噪，效果不够稳定',['降噪','降噪']),
 ('negative','戴久了夹耳朵，舒适度不够',['佩戴舒适','佩戴舒适']),
 ('negative','续航没有宣传的那么久，需要频繁充电',['续航','续航']),
 ('negative','配送等待时间长，外包装还有压痕',['配送','包装']),
 ('negative','包装盒有破损，保护不够好',['包装','包装']),
 ('negative','低音太重，人声不够自然',['音质','音质']),
 ('negative','连接偶尔断开，重新配对很麻烦',['连接稳定','连接稳定']),
 ('negative','通话时对方听不清，麦克风表现一般',['通话','通话']),
 ('negative','耳机有点重，运动时容易掉',['佩戴舒适','运动']),
 ('mixed','音质很好但价格确实贵，适合预算充足的人',['音质','价格']),
 ('mixed','降噪不错，但是续航和预期有差距',['降噪','续航']),
 ('mixed','配送很快，包装却比较简陋',['配送','包装']),
 ('neutral','整体还行，功能比较齐全',['功能','居家']),
]
scenarios=['通勤','办公','学习','运动','旅行','居家','通话']

def make_raw():
 rows=[]
 start=date(2026,1,1)
 rid=1
 for brand,info in brands.items():
  for i in range(100):
   sentiment, phrase, labels = random.choice(texts)
   # brand-specific flavour
   extra = {'索尼':'低频表现突出','Bose':'沉浸感很强','Apple AirPods':'和手机配合顺手','华为 FreeBuds':'鸿蒙设备连接方便'}[brand]
   review = phrase + ('，'+extra if random.random()<0.35 else '')
   price = round(random.uniform(*info['price']),2)
   rating = {'positive':random.choice([4.5,4.8,5.0]),'negative':random.choice([2.5,3.0,3.5]),'mixed':random.choice([3.5,4.0]),'neutral':4.0}[sentiment]
   d=(start+timedelta(days=random.randint(0,300))).isoformat()
   row={'record_id':f'R{rid:04d}','brand':brand,'product':info['product'],'price':str(price),'rating':str(rating),'review':review,'review_date':d,'likes':str(random.randint(0,900)),'source_url':'教学模拟数据（蓝牙耳机评论）','collected_at':'2026-11-17'}
   rows.append(row); rid += 1
 # introduce controlled data issues
 for idx in [5,42,177]: rows[idx]['price']=''
 for idx in [8,119,260]: rows[idx]['rating']=''
 for idx in [12,88]: rows[idx]['price']='￥'+rows[idx]['price']
 for idx in [21,145]: rows[idx]['price']=rows[idx]['price']+'元'
 for idx in [31,202]: rows[idx]['price']='-99'
 for idx in [55]: rows[idx]['rating']='70'
 for idx in [66]: rows[idx]['brand']='Sony'
 for idx in [166]: rows[idx]['brand']='Apple'
 for idx in [244]: rows[idx]['review_date']=rows[idx]['review_date'].replace('-','/')
 for idx in [288]: rows[idx]['review_date']='2026年09月18日'
 for idx in [333]: rows[idx]['likes']='1,205'
 # duplicate two raw records
 rows.append(dict(rows[14], record_id='R0401'))
 rows.append(dict(rows[230], record_id='R0402'))
 return rows

def clean_data(rows):
 cleaned=[]; seen=set()
 for r in rows:
  brand={'Sony':'索尼','Apple':'Apple AirPods'}.get(r['brand'],r['brand'])
  text=r['review'].strip()
  key=(brand,text,r['review_date'].replace('/','-').replace('年','-').replace('月','-').replace('日',''))
  if key in seen: continue
  seen.add(key)
  m=re.search(r'[-]?\d+(?:\.\d+)?',r['price'].replace(',',''))
  price=float(m.group()) if m and float(m.group())>0 else None
  try: rating=float(r['rating'])
  except: rating=None
  if rating is None or not 1<=rating<=5: rating=3.0
  d=r['review_date']
  if '年' in d:
   d=d.replace('年','-').replace('月','-').replace('日','')
  d=d.replace('/','-')
  likes=int(str(r['likes']).replace(',','')) if r['likes'] else 0
  if price is None:
   price=round(sum(brands[brand]['price'])/2,2)
  cleaned.append({'review_id':r['record_id'],'brand':brand,'product':brands[brand]['product'],'price':round(price,2),'rating':rating,'review_text':text,'review_date':d,'likes':likes,'source':r['source_url']})
 return cleaned

def encode_one(r):
 t=r['review_text']
 rules=[('价格',['价格','贵','性价比'], '价格'),('音质',['音质','低音','人声'], '音质'),('降噪',['降噪','风噪'], '降噪'),('佩戴舒适',['夹耳朵','戴久','轻','重','掉'], '佩戴舒适'),('续航',['续航','充电'], '续航'),('配送',['配送','等待'], '配送'),('包装',['包装','压痕','破损','简陋'], '包装'),('通话',['通话','麦克风'], '通话'),('连接稳定',['连接','配对','断开'], '连接稳定'),('外观',['外观','做工'], '外观')]
 topics=[]
 for name, kws, need in rules:
  hits=[k for k in kws if k in t]
  if hits:
   topics.append({'name':name,'polarity':'negative' if any(x in t for x in ['偏高','贵','一般','不够','没有','麻烦','长','破损','简陋','重','掉','断开','听不清','风噪','频繁']) else 'positive','evidence': next((s for s in re.split('[，。]',t) if any(k in s for k in hits)), t)})
 if any(x in t for x in ['但是','但','却','不过']): sentiment='mixed'
 elif any(x in t for x in ['偏高','贵','不够','没有','麻烦','长','破损','简陋','重','掉','断开','听不清','一般']): sentiment='negative'
 elif any(x in t for x in ['很好','舒服','方便','清楚','完整','快速','轻','稳定','细腻','明显']): sentiment='positive'
 else: sentiment='neutral'
 need=topics[0]['name'] if topics else 'unknown'
 pain=next((x['name'] for x in topics if x['polarity']=='negative'),'none')
 barrier='价格' if '价格' in t or '贵' in t else ('舒适度担忧' if any(x in t for x in ['夹耳朵','戴久','重','掉']) else ('功能不足' if any(x in t for x in ['不够','没有','断开','听不清']) else '无'))
 scenario=next((x for x in scenarios if x in t),'unknown')
 evidence=topics[0]['evidence'] if topics else t[:20]
 return {'review_id':r['review_id'],'sentiment':sentiment,'need':need,'pain_point':pain,'scenario':scenario,'purchase_barrier':barrier,'evidence':evidence,'confidence':'high' if topics else 'medium','topics':topics}

def main():
 raw=make_raw(); RAW.parent.mkdir(parents=True,exist_ok=True)
 with RAW.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=raw[0].keys()); w.writeheader(); w.writerows(raw)
 clean=clean_data(raw)
 pd.DataFrame(clean).to_csv(CLEAN,index=False,encoding='utf-8-sig')
 enc=[encode_one(r) for r in clean]
 ENC.write_text(json.dumps(enc,ensure_ascii=False,indent=2),encoding='utf-8')
 # stats with pandas
 df=pd.DataFrame(clean); edf=pd.DataFrame(enc).explode('topics')
 edf=edf[edf['topics'].notna()].copy(); edf['topic']=edf['topics'].map(lambda x:x['name']); edf['polarity']=edf['topics'].map(lambda x:x['polarity']); edf=edf.merge(df[['review_id','brand']],on='review_id',how='left')
 n=len(df)
 pain=edf[edf.polarity=='negative'].groupby('topic').agg(negative_count=('review_id','nunique')).reset_index()
 pain['sample_size']=n; pain['negative_rate']=pain.negative_count/n; pain['negative_rate_pct']=(pain.negative_rate*100).round(1); pain=pain.sort_values(['negative_count','topic'],ascending=[False,True])
 pain.to_csv(OUT/'pain_point_statistics.csv',index=False,encoding='utf-8-sig')
 sent=edf.groupby('polarity').agg(count=('review_id','nunique')).reset_index(); sent['sample_size']=n; sent['rate_pct']=(sent['count']/n*100).round(1); sent.to_csv(OUT/'sentiment_statistics.csv',index=False,encoding='utf-8-sig')
 brand=edf[edf.polarity=='negative'].groupby(['brand','topic']).agg(negative_count=('review_id','nunique')).reset_index(); brand['sample_size']=n; brand['rate_pct']=(brand.negative_count/n*100).round(1); brand.to_csv(OUT/'brand_topic_statistics.csv',index=False,encoding='utf-8-sig')
 # evidence table top 3 each high priority topic
 ev=[]
 for topic in pain.head(5).topic:
  ids=edf[(edf.topic==topic)&(edf.polarity=='negative')].review_id.unique()[:3]
  for rid in ids:
   rr=df[df.review_id==rid].iloc[0]; ee=next(x for x in next(e for e in enc if e['review_id']==rid)['topics'] if x['name']==topic)
   ev.append({'topic':topic,'review_id':rid,'brand':rr.brand,'evidence':ee['evidence'],'review_text':rr.review_text})
 pd.DataFrame(ev).to_csv(OUT/'evidence_table.csv',index=False,encoding='utf-8-sig')
 # inspection first 10
 inspection=[]
 for r,e in zip(clean[:10],enc[:10]): inspection.append({'review_id':r['review_id'],'review_text':r['review_text'],'encoded_sentiment':e['sentiment'],'encoded_need':e['need'],'evidence_is_substring':e['evidence'] in r['review_text']})
 pd.DataFrame(inspection).to_csv(OUT/'inspection_10.csv',index=False,encoding='utf-8-sig')
 # dashboard html
 rows_html=''.join(f'<tr><td>{x.topic}</td><td>{x.negative_count}</td><td>{x.sample_size}</td><td>{x.negative_rate_pct:.1f}%</td></tr>' for x in pain.itertuples())
 OUT.joinpath('dashboard.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>蓝牙耳机消费者洞察 Dashboard</title><style>body{{font-family:Arial,"Microsoft YaHei";margin:40px;color:#222}}h1{{color:#1f3a5f}}table{{border-collapse:collapse;width:760px}}th,td{{border:1px solid #ccc;padding:8px}}th{{background:#e8eef5}}</style><h1>蓝牙降噪耳机消费者洞察 Dashboard</h1><p>有效样本量：{n} 条；品牌：索尼、Bose、Apple AirPods、华为 FreeBuds</p><h2>负面痛点排行</h2><table><tr><th>主题</th><th>负面评论数</th><th>统计分母</th><th>占比</th></tr>{rows_html}</table><h2>口径</h2><p>占比=该主题负面评论数/有效编码评论数，评论ID可在 evidence_table.csv 中追溯。</p></html>''',encoding='utf-8')
 # report
 top=pain.iloc[0]
 report=f'''# 实验四：AI+Python消费者洞察引擎\n\n## 1. 数据概览\n本次使用蓝牙降噪耳机教学模拟评论数据。原始数据共 {len(raw)} 条，清洗去重后有效样本 {n} 条，覆盖索尼、Bose、Apple AirPods、华为 FreeBuds 四个品牌。\n\n## 2. 程序计算与Skill编码分工\n- Skill语义编码：情绪、需求、痛点、证据片段和置信度。\n- Python统计：计数、占比、排序、品牌对比和证据表生成。\n- 统计分母：{n} 条有效编码评论。\n\n## 3. 痛点结论\n最高频负面主题为“{top.topic}”：{int(top.negative_count)} 条/{n} 条，占 {top.negative_rate_pct:.1f}%。完整排行见 `pain_point_statistics.csv`。\n\n## 4. 事实、推断和建议\n**事实：** 负面主题按评论ID去重后统计，并保留分子、分母和百分比。\n\n**推断：** 高频痛点代表消费者体验中较集中的阻碍，但不能单独证明其导致购买流失。\n\n**建议：** 后续可按品牌分别检查该痛点，并用问卷或A/B测试验证产品卖点和价格方案。\n\n## 5. 证据追溯\n每个重点主题至少绑定3条原始评论证据，见 `evidence_table.csv`。\n\n## 6. 限制\n数据为教学模拟数据，语义编码采用本地规则复现 GitHub Skill 的字段契约；如接入大模型，应保留相同JSON结构并重新进行10条人工抽检。\n\n版本：v0.4\n'''
 (OUT/'insight_report.md').write_text(report,encoding='utf-8')
 (ROOT/'docs'/'github_skill_usage.md').write_text('''# GitHub Skill 使用记录\n\n来源仓库：<https://github.com/funewa/amazon-consumer-insight>\n\n本实验直接下载并保留该仓库的 `SKILL.md` 与 `README.md`。本地实现采用其“数据概览—痛点—购买动因—场景—证据追溯”的报告结构，并结合前序实验的 `consumer-insight-skill` JSON 字段契约。\n\n该 GitHub Skill 的 ARI API 需要用户密钥并可能产生积分费用，本实验未调用付费 API；编码结果在本地按同样的证据绑定原则生成，统计全部由 Python 完成。\n''',encoding='utf-8')
 # tests
 (ROOT/'tests'/'test_engine.py').write_text('''import json, pandas as pd\nfrom pathlib import Path\nroot=Path(__file__).resolve().parents[1]\ndf=pd.read_csv(root/'data/processed/clean_data.csv')\nenc=json.loads((root/'data/encoded/encoded_reviews.json').read_text(encoding='utf-8'))\nassert len(df)==len(enc)\nassert df.review_id.is_unique\nassert all(e['evidence'] in df.loc[df.review_id==e['review_id'],'review_text'].iloc[0] for e in enc)\nprint('PASS: rows, unique IDs, evidence traceability')\n''',encoding='utf-8')
 print(json.dumps({'raw_rows':len(raw),'clean_rows':n,'brands':list(brands)},ensure_ascii=False))
if __name__=='__main__': main()


