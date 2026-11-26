"""New scenario implementation, not recovered original code."""
import numpy as np
from dataclasses import dataclass
@dataclass
class Config:
    rate: float # required scenario/calibrated fractional loss per second
    tref: float # Celsius
    entropy: float # pack V/K, explicit assumption
    substep: int = 60
    ea: float = .6
    knee: float = .8
    alpha: float = 5.
    weights: tuple = (.85,.05,.05,.05)

def pv(ghi, ambient): # Eq 4
    return np.maximum(0,np.asarray(ghi)/1000*100*(1-.004*np.asarray(ambient))*.9)
def acceleration(h,c): return 1+c.alpha*max(0,c.knee-h)
def loss(h,t,dt,c):
    return acceleration(h,c)*c.rate*np.exp(c.ea/8.617e-5*(1/(c.tref+273.15)-1/(t+273.15)))*dt

def thermal(t,amb,p,dt,c): # Eqs 15-16, frozen heat per substep
    i=1000*p/400
    q=i*i*.0005+i*(t+273.15)*c.entropy
    eq=amb+.1*q
    return eq+(t-eq)*np.exp(-dt/2000)

class Plant:
    def __init__(self,c,h=.8,soc=.5,temp=25,estimate=.8):
        self.c=c; self.h=h; self.h0=h; self.estimate=estimate; self.e=200*h*soc; self.temp=temp
    @property
    def soc(self): return self.e/(200*self.h)
    def step(self,a,pv,load,amb):
        if self.h<=.7: raise RuntimeError('End of service')
        eta=np.sqrt(.96); cap=200*self.h; old=self.h
        p=np.clip(a,-1,1)*50
        ch=min(max(p,0),max(pv-load,0),max(0,.9*cap-self.e)/eta)
        dis=min(max(-p,0),max(load-pv,0),max(0,self.e-.1*cap)*eta)
        self.e+=eta*ch-dis/eta
        served=min(load,pv+dis-ch); unmet=load-served; curt=pv+dis-ch-served
        assert abs(pv+dis-served-ch-curt)<1e-8
        for start in range(0,3600,self.c.substep):
            dt=min(self.c.substep,3600-start)
            self.temp=thermal(self.temp,amb,ch-dis,dt,self.c)
            self.h=max(.7,self.h-loss(self.h,self.temp,dt,self.c))
            self.estimate=max(.7,self.estimate-loss(self.estimate,self.temp,dt,self.c))
        # Explicit new convention: preserve stored energy except capacity overflow.
        spill=max(0,self.e-.9*200*self.h); self.e-=spill
        components=np.array([served*.15/5,-max(0,(self.temp-45)/30),-min(1,(old-self.h)/2e-5),-unmet/20])
        return dict(pv=pv,load=load,charge=ch,discharge=dis,served=served,unmet=unmet,curtailment=curt,temperature=self.temp,soh=self.h,estimated_soh=self.estimate,soc=self.soc,capacity_spill=spill,reward=float(components@self.c.weights),done=self.h<=.7)

def lcoe(initial,om,replacements,served,salvage=0,discount=.08):
    d=(1+discount)**np.arange(1,len(served)+1)
    return (initial+np.sum((np.asarray(om)+np.asarray(replacements))/d)-salvage/d[-1])/np.sum(np.asarray(served)/d)
