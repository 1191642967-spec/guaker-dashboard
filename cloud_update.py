# -*- coding: utf-8 -*-
"""
桂格直播间数据看板 - 云端自动更新脚本（GitHub Actions专用）
功能：
1. 用飞书API读取最新数据（表1+表2+排版表）
2. 处理数据并生成HTML看板
3. 提交到GitHub仓库，触发Pages更新
"""
import json
import csv
import io
import re
import os
import sys
import base64
import urllib.request
import urllib.error
from datetime import datetime, date as date_cls, timedelta

# ========== 配置 ==========
SHEET_TOKEN = 'XdvLsRTPFhUK3DtZiNccUCU9ntd'
SHEET1_ID = 'bAEjmk'
SHEET2_ID = 'eqD8Nj'
SHEET3_ID = 'vJ8OVY'

# 从环境变量读取飞书凭证
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')

# 从环境变量读取GitHub凭证
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', '1191642967-spec/guaker-dashboard')

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(WORK_DIR)

def log(msg):
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}')

# ========== 飞书API ==========
def get_tenant_access_token():
    """获取飞书tenant_access_token"""
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    data = json.dumps({
        'app_id': FEISHU_APP_ID,
        'app_secret': FEISHU_APP_SECRET
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get('code') == 0:
                return result.get('tenant_access_token')
            else:
                log(f'获取token失败: {result}')
                return None
    except Exception as e:
        log(f'获取token异常: {e}')
        return None

def feishu_api_get(url, token):
    """飞书API GET请求"""
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        log(f'飞书API请求异常: {e}')
        return None

def read_sheet_range(token, sheet_id, range_str):
    """读取飞书表格指定范围"""
    url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{SHEET_TOKEN}/values/{sheet_id}!{range_str}'
    result = feishu_api_get(url, token)
    if result and result.get('code') == 0:
        return result.get('data', {}).get('valueRange', {}).get('values', [])
    return None

# ========== 数据处理函数 ==========
def parse_num(s):
    if s is None: return None
    s = str(s).strip().replace(',', '').replace('，', '')
    if not s or s in ('#DIV/0!', '#N/A', '#REF!', '#VALUE!', '-', '--', 'N/A'): return None
    if s.endswith('%'):
        try:
            v = float(s[:-1]) / 100
            return v if 0 <= v <= 1 else None
        except: return None
    try: return float(s)
    except: return None

def parse_date(s):
    if not s: return None
    s = str(s).strip()
    m = re.match(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', s)
    if m: return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r'(\d{1,2})月(\d{1,2})日?', s)
    if m:
        month = int(m.group(1))
        year = 2025 if month >= 11 else 2026
        return f"{year}-{month:02d}-{int(m.group(2)):02d}"
    return None

# ========== 读取并处理表1 ==========
def fetch_table1(token):
    log('读取表1（每日数据汇总）...')
    rows = read_sheet_range(token, SHEET1_ID, 'A1:AC1050')
    if not rows:
        log('表1读取失败')
        return None
    log(f'表1原始行数: {len(rows)}')

    # 找到所有"日期"表头行的索引
    header_indices = []
    for i, row in enumerate(rows):
        if len(row) > 1 and str(row[1]).strip() == '日期':
            header_indices.append(i)
    log(f'找到 {len(header_indices)} 个数据分段')

    # 用字典按日期存储，后面的分段覆盖前面的
    record_dict = {}
    for header_idx in header_indices:
        for i in range(header_idx + 1, len(rows)):
            row = rows[i]
            if len(row) < 3 or not str(row[1]).strip():
                break
            if str(row[1]).strip() == '日期':
                break
            date = parse_date(row[1])
            if not date:
                continue
            rec = {
                'year': 2026 if date.startswith('2026') else 2025,
                'date': date,
                'totalGmv': parse_num(row[2]) if len(row) > 2 else None,
                'gmv': parse_num(row[3]) if len(row) > 3 else None,
                'duration': parse_num(row[4]) if len(row) > 4 else None,
                'hourlyGmv': parse_num(row[5]) if len(row) > 5 else None,
                'views': parse_num(row[6]) if len(row) > 6 else None,
                'orders': parse_num(row[7]) if len(row) > 7 else None,
                'avgOrderValue': parse_num(row[8]) if len(row) > 8 else None,
                'adSpend': parse_num(row[9]) if len(row) > 9 else None,
                'overallRoi': parse_num(row[10]) if len(row) > 10 else None,
                'couponRoi': None,
                'uvValue': parse_num(row[11]) if len(row) > 11 else None,
                'refundAmount': parse_num(row[12]) if len(row) > 12 else None,
                'refundRate': parse_num(row[13]) if len(row) > 13 else None,
                'interactions': parse_num(row[14]) if len(row) > 14 else None,
                'interactionRateCount': parse_num(row[15]) if len(row) > 15 else None,
                'interactionUsers': parse_num(row[16]) if len(row) > 16 else None,
                'interactionRateUser': parse_num(row[17]) if len(row) > 17 else None,
                'newFans': parse_num(row[18]) if len(row) > 18 else None,
                'exposureCount': parse_num(row[19]) if len(row) > 19 else None,
                'watchCount': parse_num(row[20]) if len(row) > 20 else None,
                'productExposureCount': parse_num(row[21]) if len(row) > 21 else None,
                'productClickCount': parse_num(row[22]) if len(row) > 22 else None,
                'buyerCount': parse_num(row[23]) if len(row) > 23 else None,
                'exposureToWatchRate': parse_num(row[24]) if len(row) > 24 else None,
                'watchToProductRate': parse_num(row[25]) if len(row) > 25 else None,
                'productClickRate': parse_num(row[26]) if len(row) > 26 else None,
                'clickToBuyRate': parse_num(row[27]) if len(row) > 27 else None,
            }
            # 数据清洗
            if rec['refundRate'] is not None and rec['refundRate'] > 1:
                rec['refundRate'] = rec['refundRate'] / 100
            int_fields = ['views', 'orders', 'interactions', 'interactionUsers', 'newFans',
                          'exposureCount', 'watchCount', 'productExposureCount',
                          'productClickCount', 'buyerCount']
            for f in int_fields:
                v = rec.get(f)
                if v is not None:
                    if v <= 0: rec[f] = None
                    elif v != int(v): rec[f] = round(v)
            rate_fields = ['refundRate', 'interactionRateCount', 'interactionRateUser',
                           'exposureToWatchRate', 'watchToProductRate',
                           'productClickRate', 'clickToBuyRate']
            for f in rate_fields:
                v = rec.get(f)
                if v is not None and (v < 0 or v > 1): rec[f] = None
            if rec['newFans'] is not None and rec['newFans'] > 10000:
                rec['newFans'] = None
            if (rec.get('totalGmv') or 0) > 0 or (rec.get('adSpend') or 0) > 0:
                record_dict[date] = rec

    records = sorted(record_dict.values(), key=lambda x: x['date'])
    # 只保留最近30天
    today = date_cls.today()
    today_str = today.strftime('%Y-%m-%d')
    thirty_days_ago = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    records = [r for r in records if r['date'] <= today_str and r['date'] >= thirty_days_ago]

    log(f'表1处理完成: {len(records)} 条记录（近30天）')
    return records

# ========== 读取并处理表2 ==========
def fetch_table2(token):
    log('读取表2（日主播数据报表）...')
    rows1 = read_sheet_range(token, SHEET2_ID, 'A1:BS500') or []
    rows2 = read_sheet_range(token, SHEET2_ID, 'A501:BS932') or []
    all_rows = rows1 + rows2
    log(f'表2原始行数: {len(all_rows)}')

    BLOCK_STARTS = [0, 13, 26, 39, 52]

    # 扫描分段
    segments = []
    for i, row in enumerate(all_rows):
        names = {}
        for bs in BLOCK_STARTS:
            if bs < len(row):
                val = str(row[bs]).strip()
                if val and re.match(r'^[\u4e00-\u9fa5]{2,4}$', val) and val not in ('日期', '时长', '消耗'):
                    names[bs] = val
        if names and i+1 < len(all_rows):
            next_row = all_rows[i+1]
            has_fields = any('时长' in str(next_row[bs+1] if bs+1 < len(next_row) else '') or
                           '日期' in str(next_row[bs] if bs < len(next_row) else '')
                           for bs in BLOCK_STARTS if bs < len(next_row))
            if has_fields:
                segments.append({'header_row': i, 'names': names})

    log(f'共找到 {len(segments)} 个分段')

    # 处理每个分段
    raw_records = []
    for seg_idx, seg in enumerate(segments):
        header_row = seg['header_row']
        names = seg['names']
        field_row = header_row + 1
        end_row = segments[seg_idx+1]['header_row'] if seg_idx+1 < len(segments) else len(all_rows)

        for r in range(field_row + 1, end_row):
            row = all_rows[r]
            if not any(str(cell).strip() for cell in row if cell): continue

            for bs, anchor in names.items():
                if bs + 1 >= len(row): continue
                date_val = str(row[bs]).strip() if bs < len(row) else ''
                date = parse_date(date_val)
                if not date: continue

                duration = parse_num(row[bs+1]) if bs+1 < len(row) else None
                adSpend = parse_num(row[bs+2]) if bs+2 < len(row) else None
                gmv = parse_num(row[bs+3]) if bs+3 < len(row) else None
                overallRoi = parse_num(row[bs+4]) if bs+4 < len(row) else None
                hourlyGmv = parse_num(row[bs+5]) if bs+5 < len(row) else None
                views = parse_num(row[bs+6]) if bs+6 < len(row) else None
                orders = parse_num(row[bs+7]) if bs+7 < len(row) else None
                avgOrderValue = parse_num(row[bs+8]) if bs+8 < len(row) else None
                newFans = parse_num(row[bs+9]) if bs+9 < len(row) else None

                rec = {
                    'date': date,
                    'anchor': anchor,
                    'duration': duration,
                    'adSpend': adSpend,
                    'gmv': gmv,
                    'overallRoi': overallRoi,
                    'hourlyGmv': hourlyGmv,
                    'views': views,
                    'orders': orders,
                    'avgOrderValue': avgOrderValue,
                    'newFans': newFans,
                    '_seg': seg_idx,
                    '_has_row': True,
                }
                raw_records.append(rec)

    log(f'原始记录数: {len(raw_records)}')

    # 去重：同一日期同一主播，取最后一个分段的数据
    date_anchors_latest = {}
    for r in raw_records:
        d = r['date']
        a = r['anchor']
        if d not in date_anchors_latest:
            date_anchors_latest[d] = {}
        if a not in date_anchors_latest[d] or r['_seg'] > date_anchors_latest[d][a]:
            date_anchors_latest[d][a] = r['_seg']

    filtered = []
    for r in raw_records:
        d = r['date']
        if r['anchor'] != '朱吴琪' and d in date_anchors_latest:
            if r['anchor'] not in date_anchors_latest[d]: continue
        filtered.append(r)

    # 清理数据
    cleaned = []
    for r in filtered:
        if r['gmv'] is not None and r['gmv'] < 0: r['gmv'] = None
        if r['adSpend'] is not None and r['adSpend'] < 0: r['adSpend'] = None
        if r['gmv'] is not None and r['adSpend'] is not None and r['adSpend'] > 0:
            calc_roi = r['gmv'] / r['adSpend']
            if r['overallRoi'] is None or r['overallRoi'] < 0.5 or r['overallRoi'] > 10:
                r['overallRoi'] = round(calc_roi, 2)
        if r['overallRoi'] is not None and (r['overallRoi'] > 10 or r['overallRoi'] < 0):
            r['overallRoi'] = None
        if r['duration'] is not None and (r['duration'] > 24 or r['duration'] <= 0):
            r['duration'] = None
        if r['gmv'] is None and r['duration'] is None: continue
        if r['gmv'] in (0, None) and r['adSpend'] in (0, None): continue
        for k in ('_seg', '_has_row'):
            r.pop(k, None)
        cleaned.append(r)

    # 只保留最近30天
    today = date_cls.today()
    today_str = today.strftime('%Y-%m-%d')
    thirty_days_ago = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    cleaned = [r for r in cleaned if r['date'] and r['date'] <= today_str and r['date'] >= thirty_days_ago]

    log(f'表2处理完成: {len(cleaned)} 条记录（近30天）')
    return cleaned

# ========== 读取排版表 ==========
def fetch_schedule(token):
    log('读取排版表（明日主播排班）...')
    rows = read_sheet_range(token, SHEET3_ID, 'A1:E200')
    if not rows:
        log('排版表读取失败')
        return None

    schedule = {}
    current_date = None
    current_rest = None
    for row in rows[2:]:
        if len(row) < 4: continue
        date_str = str(row[0]).strip() if len(row) > 0 else ''
        time_str = str(row[1]).strip() if len(row) > 1 else ''
        anchor = str(row[2]).strip() if len(row) > 2 else ''
        duration = str(row[3]).strip() if len(row) > 3 else ''
        rest = str(row[4]).strip() if len(row) > 4 else ''

        if date_str:
            m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
            if m:
                current_date = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
                current_rest = rest if rest else None
                if current_date not in schedule:
                    schedule[current_date] = {'slots': [], 'rest': current_rest}

        if current_date and time_str and anchor:
            schedule[current_date]['slots'].append({
                'time': time_str,
                'anchor': anchor,
                'duration': float(duration) if duration else 0,
            })
        if current_date and rest:
            schedule[current_date]['rest'] = rest

    log(f'排版表处理完成: {len(schedule)} 天')
    return schedule

# ========== GitHub API ==========
def github_api(method, path, data=None):
    url = f'https://api.github.com{path}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'guaker-dashboard'
    }
    if data:
        headers['Content-Type'] = 'application/json'
        body = json.dumps(data).encode('utf-8')
    else:
        body = None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        log(f'GitHub API错误: {e.code} {e.reason}')
        return None
    except Exception as e:
        log(f'GitHub API异常: {e}')
        return None

def upload_to_github(html_content):
    """上传HTML到GitHub仓库"""
    log('上传HTML到GitHub...')
    content_b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')

    # 获取文件SHA
    file_info = github_api('GET', f'/repos/{GITHUB_REPO}/contents/index.html?ref=main')
    sha = file_info.get('sha') if file_info else None

    # 上传文件
    data = {
        'message': f'自动更新数据 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        'content': content_b64,
        'branch': 'main'
    }
    if sha:
        data['sha'] = sha

    result = github_api('PUT', f'/repos/{GITHUB_REPO}/contents/index.html', data)
    if result:
        log('✅ GitHub上传成功')
        return True
    return False

# ========== 主流程 ==========
def main():
    log('='*50)
    log('开始云端自动更新数据看板')
    log('='*50)

    # 1. 获取飞书token
    token = get_tenant_access_token()
    if not token:
        log('获取飞书token失败，终止')
        sys.exit(1)
    log('飞书token获取成功')

    # 2. 读取表1
    table1 = fetch_table1(token)
    if table1:
        with open('data_table1.json', 'w', encoding='utf-8') as f:
            json.dump(table1, f, ensure_ascii=False, indent=1)
        log('表1数据已保存')

    # 3. 读取表2
    table2 = fetch_table2(token)
    if table2:
        with open('data_table2.json', 'w', encoding='utf-8') as f:
            json.dump(table2, f, ensure_ascii=False, indent=1)
        log('表2数据已保存')

    # 4. 读取排版表
    schedule = fetch_schedule(token)
    if schedule:
        with open('data_schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=1)
        log('排版表数据已保存')

    # 5. 生成HTML
    log('生成HTML看板...')
    result = os.system(f'{sys.executable} gen_html.py')
    if result != 0:
        log('HTML生成失败，终止')
        sys.exit(1)
    log('HTML生成完成')

    # 6. 读取HTML并上传到GitHub
    html_path = os.path.join(WORK_DIR, '直播间运营数据分析看板.html')
    if not os.path.exists(html_path):
        log('HTML文件不存在，终止')
        sys.exit(1)

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    success = upload_to_github(html_content)
    if not success:
        log('GitHub上传失败')
        sys.exit(1)

    # 7. 保存更新记录
    record = {
        'updateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'success',
        'table1Count': len(table1) if table1 else 0,
        'table2Count': len(table2) if table2 else 0,
        'scheduleCount': len(schedule) if schedule else 0,
    }
    with open('update_record.json', 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    log('='*50)
    log('✅ 云端自动更新完成！')
    log(f'固定链接: https://{GITHUB_REPO.split("/")[0]}.github.io/{GITHUB_REPO.split("/")[1]}/')
    log('='*50)

if __name__ == '__main__':
    main()
