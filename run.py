import argparse,csv,json
import numpy as np
from model import Config,Plant,pv
p=argparse.ArgumentParser(); p.add_argument('--weather',required=True,help='CSV columns ghi,ambient; ordered hourly local time starting midnight'); p.add_argument('--rate',type=float,required=True); p.add_argument('--tref',type=float,required=True); p.add_argument('--entropy',type=float,required=True); p.add_argument('--seed',type=int,default=0); p.add_argument('--width',type=float,required=True,help='assumed Gaussian load width in hours'); p.add_argument('--output',default='dispatch.csv'); a=p.parse_args()
if a.rate<0 or a.width<=0: p.error('invalid scenario parameters')
w=np.genfromtxt(a.weather,delimiter=',',names=True); rng=np.random.default_rng(a.seed); plant=Plant(Config(a.rate,a.tref,a.entropy),h=rng.uniform(.79,.81),soc=rng.uniform(.4,.6),temp=float(w['ambient'][0])); rows=[]
for j,(g,t) in enumerate(zip(w['ghi'],w['ambient'])):
    h=j%24; solar=float(pv(g,t)); load=max(0,8+10*np.exp(-.5*((h-18)/a.width)**2)+rng.normal(0,.5)); action=1 if solar>load+5 else -1 if 18<=h<22 and plant.soc>.2 else 0
    row=plant.step(action,solar,load,t); rows.append(dict(hour=j,**row))
    if row['done']: break
with open(a.output,'w') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
print(json.dumps({k:sum(r[k] for r in rows) for k in ['served','unmet','curtailment','reward']},indent=2))
