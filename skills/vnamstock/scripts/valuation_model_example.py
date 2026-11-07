"""KDH conditional valuation 28/10/2026. Inputs: CafeF raw JSON (VND) + KDH disclosures. Units: ty dong unless noted."""
import json,glob,os
B=os.environ.get('VNAMSTOCK_ROOT','.')+'/KDH/CafeF/2026-10-28_v01/raw/'
def load(fn,code_filter=None):
    v=json.load(open(B+fn,encoding='utf-8'))['value']; T=v['templace']; D=v['data']
    if isinstance(T[0].get('data'),list): T=T[0]['data']; D=next(b['data'] for b in v['data'] if b['code']==v['templace'][0]['code'])
    return {c['time']:{str(d['code']):(d.get('value') or 0)/1e9 for d in c['data']} for c in D}
Q={}
for f in ['KQKD.json','history/kqkd_p2.json','history/kqkd_p3.json']: Q.update(load(f))
print('== Quy: DT thuan | LN gop | CPBH+CPQL | LN HD cot loi (gop-BH-QL) | LN me | YoY DT | YoY LN me | YoY cot loi')
def core(q): return Q[q]['20']-Q[q]['25']-Q[q]['26']
for q,p in [('Q3-2025','Q3-2024'),('Q4-2025','Q4-2024'),('Q1-2026','Q1-2025'),('Q2-2026','Q2-2025')]:
    a,b=Q[q],Q[p]
    yo=lambda x,y: f'{(x/y-1)*100:+.1f}%' if y>0 and x>0 else f'{x:.1f} vs {y:.1f}'
    print(q,f"{a['10']:.1f} | {a['20']:.1f} | {a['25']+a['26']:.1f} | {core(q):.1f} (cung ky {core(p):.1f}) | {a['61']:.1f} | {yo(a['10'],b['10'])} | {yo(a['61'],b['61'])} | {yo(core(q),core(p))}")
# ---- share & price basis
P=14250; SH=1245.297704  # trieu cp, sau co tuc 10% + ESOP (CV 160/2026 ngay 21/10/2026)
ESOP_CASH=10.864*12000/1000  # ty dong
TSNH=35453.468; NNH=3524.662; NPT=19497.023; NCI=1367.550; VCSH=19973.730; CASH=2605.261; STI=284.502; DEBT=2223.420+14435.537
EQ_ME=VCSH-NCI+ESOP_CASH
print(f'\nESOP cash {ESOP_CASH:.1f}; VCSH me pro-forma {EQ_ME:.1f}; BVPS {EQ_ME/SH*1000:,.0f} d; P/B {P/(EQ_ME/SH*1000):.2f}')
NWC=TSNH-NNH+ESOP_CASH; NCAV=TSNH-NPT-NCI+ESOP_CASH
print(f'NWC {NWC:,.1f} -> {NWC/SH*1000:,.0f} d/cp | NCAV {NCAV:,.1f} -> {NCAV/SH*1000:,.0f} d/cp, 2/3={NCAV/SH*1000*2/3:,.0f}')
for name,hi,hr in [('Than trong',.30,.20),('Trung gian',.15,.10),('So sach',0,0)]:
    n=NCAV-29488.131*hi-2978.496*hr; print(f'  NCAV {name}: {n/SH*1000:,.0f} d/cp, 2/3 {n/SH*1000*2/3:,.0f}')
print(f'No vay {DEBT:,.1f}; tien+DTNH {CASH+STI:,.1f}; no vay rong/VCSH me {(DEBT-CASH-STI)/EQ_ME*100:.1f}%')
# ---- P/E, PEG
ttm=sum(Q[q]['61'] for q in ['Q3-2025','Q4-2025','Q1-2026','Q2-2026'])
oneoff=896.334+285.177   # lai thoai von BTM + lai mua re An Lap, truoc thue (BCTC soat xet 6T2026 tr.32)
eps=ttm/SH*1000; epsc=(ttm-oneoff)/SH*1000
print(f'\nLN me TTM {ttm:,.1f}; EPS TTM {eps:,.0f}; P/E {P/eps:.1f}x | loai one-off (xap xi, chua phan bo thue/NCI): LN {ttm-oneoff:,.1f}, EPS {epsc:,.0f}, P/E {P/epsc:.1f}x')
ann={'2021':1202.5,'2022':1103.0,'2023':715.7,'2024':810.4,'2025':1045.5}
norm=sum(ann.values())/5
print(f'LN me binh quan 2021-2025 {norm:,.1f} -> {norm/SH*1000:,.0f} d/cp, P/E chuan hoa {P/(norm/SH*1000):.1f}x')
plan=1500; print(f'KH 2026 LN {plan}: EPS fwd {plan/SH*1000:,.0f}, P/E fwd {P/(plan/SH*1000):.1f}x, tang {(plan/1045.5-1)*100:.1f}% vs 2025 -> PEG {P/(plan/SH*1000)/((plan/1045.5-1)*100):.2f} (bi lam dep boi one-off)')
# ---- DCF FCFE 10 nam co dieu kien
def path(cf0,g1,g2): 
    out=[];cf=cf0
    for t in range(1,11): cf*=1+(g1 if t<=5 else g2); out.append(cf)
    return out
def dcf(cf0,g1,g2,r,gt):
    fl=path(cf0,g1,g2); pv=sum(c/(1+r)**t for t,c in enumerate(fl,1)); tv=fl[-1]*(1+gt)/(r-gt); pvtv=tv/(1+r)**10
    return pv,pvtv,pv+pvtv,fl
def payback(cf0ps,g1,g2,r,price,disc):
    cum=0;cf=cf0ps
    for t in range(1,31):
        cf*=1+((g1 if t<=5 else g2) if (g1 or g2) else 0); x=cf/(1+r)**t if disc else cf
        if cum+x>=price: return f'{t-1+(price-cum)/x:.1f}'
        cum+=x
        if t==10 and disc: return 'chua hoan von 10 nam'
    return '>30'
scen=[('Bi quan',0.40,.03,.03,.15,.03),('Co so',0.65,.08,.05,.14,.04),('Lac quan',0.85,.12,.07,.13,.04)]
print('\n== DCF FCFE (gia dinh: FCFE chuan hoa = ty le chuyen doi x LN me binh quan 2021-25)')
res={}
for n,conv,g1,g2,r,gt in scen:
    cf0=norm*conv; pv,pvtv,v,fl=dcf(cf0,g1,g2,r,gt); vps=v/SH*1000; res[n]=vps
    cfps=cf0/SH*1000
    print(f'{n}: CF0 {cf0:,.0f} ty ({cfps:,.0f} d/cp), g {g1:.0%}/{g2:.0%}, r {r:.0%}, gT {gt:.0%} | PV10 {pv:,.0f}, PV TV {pvtv:,.0f} ({pvtv/v:.0%}), V {v:,.0f} ty = {vps:,.0f} d/cp | upside {vps/P-1:+.1%}, MOS {1-P/vps:+.1%} | mua MOS15/25/30/50: {", ".join(f"{vps*(1-m):,.0f}" for m in (.15,.25,.3,.5))}')
    print(f'   payback: 0% {P/cfps:.1f} nam | tang truong {payback(cfps,g1,g2,r,P,False)} | chiet khau {payback(cfps,g1,g2,r,P,True)}')
# reverse DCF: CF0 can de V=P voi tham so co so
lo,hi=1,5000
for _ in range(60):
    m=(lo+hi)/2; v=dcf(m,.08,.05,.14,.04)[2]/SH*1000; lo,hi=(m,hi) if v<P else (lo,m)
print(f'\nDinh gia nguoc (g 8%/5%, r 14%, gT 4%): FCFE nam dau can ~{m:,.0f} ty/nam ({m/SH*1000:,.0f} d/cp) = {m/norm:.0%} LN me binh quan; thuc te CFO-capex 2025 am')
print('\n== Do nhay gia tri/cp kich ban co so theo r va gT')
for r in (.12,.13,.14,.15,.16): print(f' r {r:.0%}: '+' | '.join(f'gT {gt:.0%}: {dcf(norm*.65,.08,.05,r,gt)[2]/SH*1000:,.0f}' for gt in (.03,.04,.05)))
# ---- Owner earnings: LN chuan hoa + D&A - capex duy tri - bo sung quy dat duy tri
DA=13.3
print('\n== Owner Earnings (bo sung quy dat duy tri la gia dinh, khong co thuyet minh)')
for n,land,g1,g2,r,gt in [('Bi quan',.55,.03,.03,.15,.03),('Co so',.35,.08,.05,.14,.04),('Lac quan',.20,.12,.07,.13,.04)]:
    oe=norm+DA-DA-norm*land; pv,pvtv,v,_=dcf(oe,g1,g2,r,gt); vps=v/SH*1000; ops=oe/SH*1000
    print(f'{n}: OE {oe:,.0f} ty ({ops:,.0f} d/cp; tai dau tu dat {land:.0%}) -> {vps:,.0f} d/cp, TV {pvtv/v:.0%}, MOS {1-P/vps:+.1%} | payback 0% {P/ops:.1f}, tang truong {payback(ops,g1,g2,r,P,False)}, chiet khau {payback(ops,g1,g2,r,P,True)}')
# self-tests
assert abs(dcf(100,0,0,.1,0)[2]-1000)<1e-6, 'perpetuity check'
f=path(100,.05,.05); assert abs(sum(f)-100*1.05*((1.05**10-1)/.05))<1e-6
print('\nself-tests ok')
