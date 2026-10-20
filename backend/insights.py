"""Readable, computed explanations. No acquisition fixture is accessible here."""
import numpy as np
from . import mechanisms as m


def explain(cloud,weights,losses,noise_multiplier=1.,rates=None,observation_minute=None):
    channels=[]
    for channel,spec in m.CHANNELS.items():
        minute=cloud.cutoff if observation_minute is None else observation_minute
        values=m.sensor_prediction(cloud,channel,minute)
        noise=spec['noise']*noise_multiplier
        families=[]
        # Predictive ranges include measurement noise, not only particle variability.
        nodes,nw=np.polynomial.hermite.hermgauss(21);nw=nw/np.sqrt(np.pi)
        for i,f in enumerate(m.FAMILIES):
            sl=slice(i*m.N,(i+1)*m.N);fw=weights[sl]
            fw=fw/fw.sum() if fw.sum()>1e-250 else np.full(m.N,1/m.N)
            outcomes=(values[sl,None]+np.sqrt(2)*nodes*noise).ravel()
            ow=(fw[:,None]*nw).ravel()
            intervals=[round(m.weighted_quantile(outcomes,ow,q),3) for q in [.1,.5,.9]]
            families.append({'id':f['id'],'label':f['label'],'range':intervals,'weight':round(float(weights[sl].sum()),4)})
        experiments=[]
        for q in [.15,.5,.85]:
            value=m.weighted_quantile(values,weights,q)
            # A hypothetical delayed result is evaluated at its observation time,
            # never released into the current evidence ledger.
            likelihood=-.5*((values-value)/noise)**2
            post=m.normalize(np.log(np.maximum(weights,1e-300))+likelihood)
            choice=int(np.argmin(post@losses))
            experiments.append({'value':round(value,3),'family_weights':m.family_mass(post).round(4).tolist(),
                'scenario_index':choice,'rate_ml_h':rates[choice] if rates else None})
        channels.append({'channel':channel,'label':spec['label'],'unit':spec['unit'],'families':families,
            'possible_results':experiments,'observation_minute':minute,'noise_sd':noise,
            'interpretation':'Authored predictive observation ranges, not validated device distributions'})
    return channels
