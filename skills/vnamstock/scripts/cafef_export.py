"""Read-only CafeF financial exports. Python: requests, openpyxl. No credentials."""
import os
import argparse, csv, hashlib, json, re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from openpyxl import Workbook, load_workbook

def export(symbol, root, date, exchange='hose'):
    symbol=symbol.upper()
    if not re.fullmatch(r'[A-Z0-9]{2,12}',symbol): raise ValueError('Invalid symbol')
    base=Path(root)/symbol/'CafeF'; base.mkdir(parents=True,exist_ok=True)
    runs=sorted(base.glob('*_v*/manifest.json'))
    prev=json.loads(runs[-1].read_text(encoding='utf-8')) if runs else {}
    v=1
    while (base/f'{date}_v{v:02}').exists(): v+=1
    out=base/f'{date}_v{v:02}'; out.mkdir(); (out/'raw').mkdir()
    page=f'https://cafef.vn/du-lieu/{exchange}/{symbol.lower()}-tai-chinh.chn'
    session=requests.Session(); response=session.get(page,timeout=30);response.raise_for_status()
    (out/'raw/page.html').write_text(response.text,encoding='utf-8')
    endpoints={'BCTC_Tom_Tat':('v1','GetReportSummary','ALL'),'CDKT':('v2','GetReportCDKT','ALL'),'KQKD':('v1','GetReportDetail','KQKD'),'LCTT':('v1','GetReportLCTT','ALL')}
    manifest={'symbol':symbol,'checked_date':date,'source_page':page,'previous_run':str(runs[-1]) if runs else None,'reports':{},'notes':['API values preserved without unit conversion; verify units before valuation.','CafeF latest period is not proof of latest issuer filing.','LCTT may be cumulative; do not sum quarterly-labelled columns.']}
    for kind,(version,method,rt) in endpoints.items():
        try:
            url=f'https://apiweb.cafef.vn/api/{version}/BCTC/{method}'
            r=session.get(url,params={'symbol':symbol,'pageIndex':1,'pageSize':4,'reportType':rt,'TypeTime':'QUY'},timeout=30);r.raise_for_status(); j=r.json()
            (out/'raw'/f'{kind}.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
            if not j.get('isSuccess'): raise ValueError('API did not report success')
            data=j['value']; templates=data['templace']; blocks=data['data']
            grouped=bool(templates and isinstance(templates[0].get('data'),list))
            groups=[(t.get('name',t['code']),t['data'],next((b['data'] for b in blocks if b['code']==t['code']),[])) for t in templates] if grouped else [(kind,templates,blocks)]
            wb=Workbook();wb.remove(wb.active); periods=set(); row_count=0
            for ix,(title,metrics,cols) in enumerate(groups):
                if not cols: continue
                ws=wb.create_sheet(re.sub(r'[\\/*?:\[\]]','_',title)[:27]+str(ix)); ws.append(['Code','Chỉ tiêu']+[c['time'] for c in cols]); periods.update(c['time'] for c in cols)
                maps=[{str(m['code']):m.get('value') for m in c['data']} for c in cols]
                for m in metrics:
                    ws.append([str(m['code']),m.get('name','')]+[x.get(str(m['code'])) for x in maps]);row_count+=1
                ws.freeze_panes='C2';ws.column_dimensions['A'].width=18;ws.column_dimensions['B'].width=75
                for column in ['C','D','E','F']:ws.column_dimensions[column].width=24
                for row in ws.iter_rows(min_row=2,min_col=3):
                    for cell in row:
                        if isinstance(cell.value,(int,float)):cell.number_format='#,##0.00'
            if not row_count:raise ValueError('No data rows; schema may have changed')
            info=wb.create_sheet('Source');info.append(['URL',r.url]);info.append(['Checked',date]);info.append(['Unit','Raw API values; no conversion. Money typically VND; EPS VND/share; ratios have own units. Verify.'])
            dest=out/f'{symbol}_{kind}.xlsx';wb.save(dest);check=load_workbook(dest,read_only=True);assert len(check.sheetnames)>1;check.close()
            digest=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            old=prev.get('reports',{}).get(kind,{})
            manifest['reports'][kind]={'status':'ok','url':r.url,'periods':sorted(periods),'new_periods':sorted(periods-set(old.get('periods',[]))) if old else [],'changed_since_previous':digest!=old.get('sha256') if old else None,'sha256':digest,'rows':row_count,'file':dest.name}
        except Exception as e:manifest['reports'][kind]={'status':'failed','error':str(e)}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'folder':str(out),'reports':manifest['reports']},ensure_ascii=False,indent=2))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('symbol');p.add_argument('--root',default=os.environ.get('VNAMSTOCK_ROOT',os.getcwd()));p.add_argument('--date',required=True,help='Client local date YYYY-MM-DD');p.add_argument('--exchange',choices=['hose','hnx','upcom'],default='hose');a=p.parse_args()
    export(a.symbol,a.root,a.date,a.exchange)
