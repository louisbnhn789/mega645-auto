import os,csv,json,datetime,itertools,collections,urllib.request,pathlib,html
root=pathlib.Path(__file__).parent
data=root/'data'; docs=root/'docs'
data.mkdir(exist_ok=True);docs.mkdir(exist_ok=True)
path=data/'all.csv'
url=os.getenv('MEGA645_CSV_URL','').strip()
if not url:
    url='https://raw.githubusercontent.com/NhanAZ-Data/vietlott-data-research/main/datasets/draws/mega645/all.csv'
try:
    req=urllib.request.Request(url,headers={'User-Agent':'Mega645-Research/1.0'})
    raw=urllib.request.urlopen(req,timeout=30).read()
    import io
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    if len(rows)<100 or not {'draw_date','result_json'}.issubset(rows[0]):
        raise ValueError('Invalid source schema')
    if not path.exists() or len(rows)>=len(list(csv.DictReader(path.open(encoding='utf-8-sig')))):
        path.write_bytes(raw)
except Exception as exc:
    print('Source unavailable:',exc)
if not path.exists():
    (docs/'index.html').write_text('<h1>Mega645: No verified data yet</h1><p>Set MEGA645_CSV_URL and run workflow.</p>',encoding='utf8')
    raise SystemExit(0)
draws={}
for row in csv.DictReader(path.open(encoding='utf-8-sig')):
    if row.get('product','mega645')!='mega645' or row.get('draw_status','confirmed')!='confirmed':continue
    try:
        day=datetime.date.fromisoformat(row['draw_date'])
        nums=tuple(sorted(map(int,json.loads(row['result_json'])['numbers'])))
        if len(nums)==6 and len(set(nums))==6 and 1<=min(nums) and max(nums)<=45:
            draws[(day,nums)]=(day,nums)
    except (ValueError,TypeError,KeyError):pass
history=sorted(draws.values())
if not history:raise ValueError('No valid draws')
today=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).date()
target=max(today,history[-1][0]+datetime.timedelta(days=1))
while target.weekday() not in (2,4,6):target+=datetime.timedelta(days=1)
same=[n for d,n in history if d.weekday()==target.weekday()]
recent=[n for d,n in history[-150:]]
count=lambda sets:collections.Counter(p for nums in sets for p in itertools.combinations(nums,2))
a,b,c=count(n for d,n in history),count(same),count(recent)
baseline=15/990
def score(pair):
    return .7*(b[pair]+100*baseline)/(len(same)+100)+.3*(c[pair]+50*baseline)/(len(recent)+50)
pairs=sorted(itertools.combinations(range(1,46),2),key=lambda p:(-score(p),p))
def quality(nums):return sum(score(p) for p in itertools.combinations(sorted(nums),2))
candidates=set()
for seed in pairs[:120]:
    nums=list(seed)
    while len(nums)<6:
        choice=max((n for n in range(1,46) if n not in nums),key=lambda n:(quality(nums+[n]),-n))
        nums.append(choice)
    candidates.add(tuple(sorted(nums)))
sets=sorted(candidates,key=lambda s:(-quality(s),s))[:10]
fmt=lambda nums:'-'.join(f'{n:02}' for n in nums)
result={'last_draw':str(history[-1][0]),'target_date':str(target),'stale_days':(today-history[-1][0]).days,'draws':len(history),'weekday_draws':len(same),'source':url,'top_pairs':[{'pair':fmt(p),'all':a[p],'weekday':b[p],'recent':c[p],'historical_score_pct':round(score(p)*100,3)} for p in pairs[:30]],'top_sets':[{'numbers':fmt(s),'score':round(quality(s),5)} for s in sets]}
(docs/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
rows=''.join('<tr><td>'+str(i)+'</td><td>'+x['pair']+'</td><td>'+str(x['all'])+'</td><td>'+str(x['weekday'])+'</td><td>'+str(x['recent'])+'</td><td>'+str(x['historical_score_pct'])+'%</td></tr>' for i,x in enumerate(result['top_pairs'],1))
sets_html=''.join('<tr><td>'+str(i)+'</td><td>'+x['numbers']+'</td><td>'+str(x['score'])+'</td></tr>' for i,x in enumerate(result['top_sets'],1))
warning='WARNING: history is '+str(result['stale_days'])+' days old. Rankings are NOT current.' if result['stale_days']>5 else 'Source recency should still be verified.'
page=f"""<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mega645 Auto</title><style>body{{font:16px system-ui;max-width:1000px;margin:30px auto;padding:16px;background:#f5f7fb;color:#152338}}section{{background:white;border-radius:14px;padding:20px;margin:18px 0}}table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}.scroll{{overflow:auto}}.alert{{color:#a33}}h1{{color:#1855a0}}</style><h1>Mega 6/45 – Historical analysis</h1><section><h2>Next draw: {target}</h2><p>Last verified draw: {history[-1][0]} | {len(history)} draws | {len(same)} matching weekday draws</p><p class="alert">{html.escape(warning)}</p><h2>Top ranked six-number set: {fmt(sets[0])}</h2><p>This is a historical ranking, not a higher proven probability of winning.</p></section><section class="scroll"><h2>Top 30 pairs</h2><table><tr><th>#</th><th>Pair</th><th>All</th><th>Same weekday</th><th>Last 150</th><th>Historical score</th></tr>{rows}</table></section><section class="scroll"><h2>Top 10 sets</h2><table><tr><th>#</th><th>Numbers</th><th>Score</th></tr>{sets_html}</table></section><section>Score = 70% weekday-smoothed pair frequency + 30% recent-150-smoothed frequency. The six-number sets are heuristic candidates, not proven global optima. Check source freshness before use.</section></html>"""
(docs/'index.html').write_text(page,encoding='utf8')
print('Updated',result['last_draw'],result['target_date'],result['draws'])
