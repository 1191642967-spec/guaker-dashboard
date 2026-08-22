#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成直播间运营数据分析可视化HTML单页"""

import json

with open('data_table1.json', 'r', encoding='utf-8') as f:
    data1 = json.load(f)
with open('data_table2.json', 'r', encoding='utf-8') as f:
    data2 = json.load(f)

# 读取排版表数据
try:
    with open('data_schedule.json', 'r', encoding='utf-8') as f:
        schedule_data = json.load(f)
except:
    schedule_data = {{}}

data1_json = json.dumps(data1, ensure_ascii=False)
data2_json = json.dumps(data2, ensure_ascii=False)
schedule_json = json.dumps(schedule_data, ensure_ascii=False)

# 计算最新数据日期
latest_date = max(r['date'] for r in data1) if data1 else '2026-08-17'

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>直播间运营数据分析看板</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: linear-gradient(135deg, #f5efe6 0%, #ede4d3 30%, #e8dcc8 70%, #f0e6d6 100%);
    min-height: 100vh;
    background-attachment: fixed;
  }}
  body::before {{ content: ''; position: fixed; top:0; left:0; right:0; bottom:0; pointer-events:none; z-index:0;
    background-image: radial-gradient(circle at 20% 30%, rgba(212,165,116,0.08) 0%, transparent 50%), radial-gradient(circle at 80% 70%, rgba(0,48,135,0.05) 0%, transparent 50%);
  }}
  main {{ position: relative; z-index: 1; }}
  .glass-card {{ background: rgba(255,255,255,0.92); backdrop-filter: blur(8px); border: 1px solid rgba(212,165,116,0.25); box-shadow: 0 4px 20px rgba(0,48,135,0.08); }}
  .tab-active {{ background: linear-gradient(135deg, #003087, #003da5); color: white; box-shadow: 0 4px 12px rgba(0,48,135,0.35); }}
  .tab-inactive {{ background: rgba(255,255,255,0.85); color: #5a6c7d; }}
  .tab-inactive:hover {{ background: white; color: #003087; }}
  .sub-tab-active {{ background: linear-gradient(135deg, #003087, #003da5); color: white; box-shadow: 0 2px 8px rgba(0,48,135,0.3); }}
  .sub-tab-inactive {{ background: rgba(255,255,255,0.8); color: #5a6c7d; }}
  .sub-tab-inactive:hover {{ background: white; color: #003087; }}
  .kpi-card {{ transition: transform 0.25s, box-shadow 0.25s; background: linear-gradient(135deg, #ffffff, #faf6ee); border: 1px solid #e8dcc8; }}
  .kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 12px 28px rgba(0,48,135,0.12); border-color: #d4a574; }}
  .kpi-value {{ font-size: 22px !important; font-weight: 700 !important; }}
  .kpi-label {{ font-size: 13px !important; }}
  .kpi-sub {{ font-size: 11px !important; }}
  .chart-box {{ min-height: 320px; }}
  table {{ border-collapse: collapse; }}
  th {{ cursor: pointer; user-select: none; white-space: nowrap; background: #f5efe6; color: #003087; font-weight: 600; }}
  th:hover {{ background: #ede4d3; }}
  th .sort-icon {{ opacity: 0.4; margin-left: 4px; }}
  th.sort-asc .sort-icon, th.sort-desc .sort-icon {{ opacity: 1; color: #003087; }}
  tbody tr:hover {{ background: #faf6ee; }}
  .pagination button {{ min-width: 32px; }}
  .pagination button.active {{ background: linear-gradient(135deg, #003087, #003da5); color: white; }}
  .screenshot-btn {{ background: linear-gradient(135deg, #c8102e, #e63946); color: white; box-shadow: 0 4px 12px rgba(200,16,46,0.35); transition: all 0.2s; }}
  .screenshot-btn:hover {{ transform: translateY(-1px); box-shadow: 0 6px 16px rgba(200,16,46,0.45); }}
  .screenshot-btn:disabled {{ opacity: 0.6; cursor: not-allowed; }}
  .target-met {{ color: #16a34a; font-weight: 700; }}
  .target-not-met {{ color: #dc2626; font-weight: 700; }}
  .target-input {{ width: 60px; border: 1px solid #d4a574; border-radius: 6px; padding: 2px 6px; font-size: 12px; text-align: center; background: #fff; }}
  .target-input:focus {{ outline: none; border-color: #003087; box-shadow: 0 0 0 2px rgba(0,48,135,0.15); }}
  .analysis-box {{ background: linear-gradient(135deg, #fffef9, #f5efe6); border: 1px solid #d4a574; border-left: 4px solid #003087; }}
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-thumb {{ background: #d4a574; border-radius: 3px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  .rank-1 {{ background: linear-gradient(135deg, #fef3c7, #fde68a); }}
  .rank-2 {{ background: linear-gradient(135deg, #f1f5f9, #e2e8f0); }}
  .rank-3 {{ background: linear-gradient(135deg, #fed7aa, #fdba74); }}
</style>
</head>
<body class="min-h-screen">

<!-- 顶部标题栏 -->
<header class="sticky top-0 z-50" style="background: linear-gradient(135deg, #003087 0%, #003da5 50%, #002b6e 100%); box-shadow: 0 4px 20px rgba(0,48,135,0.3);">
  <div class="max-w-[1600px] mx-auto px-6 py-4">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: linear-gradient(135deg, #c8102e, #e63946); box-shadow: 0 4px 12px rgba(200,16,46,0.4);">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
        </div>
        <div>
          <h1 class="text-xl font-bold text-white">桂格直播间运营数据分析看板</h1>
          <p class="text-xs text-blue-200 mt-0.5">数据来源：飞书表格 · 桂格燕麦直播间</p>
        </div>
      </div>
      <div class="text-right">
        <p class="text-xs text-blue-200">数据更新至</p>
        <p class="text-sm font-semibold text-white">{latest_date}</p>
      </div>
    </div>
  </div>
</header>

<!-- Tab 切换 -->
<div class="max-w-[1600px] mx-auto px-6 pt-6">
  <div class="flex gap-2">
    <button id="tab1Btn" class="tab-active px-6 py-2.5 rounded-xl text-sm font-medium transition-all">直播间每日数据汇总</button>
    <button id="tab2Btn" class="tab-inactive px-6 py-2.5 rounded-xl text-sm font-medium transition-all">日主播数据报表</button>
  </div>
</div>

<main class="max-w-[1600px] mx-auto px-6 pb-10">

<!-- ==================== Tab 1：直播间每日数据汇总 ==================== -->
<section id="tab1" class="pt-6">

  <!-- 子Tab切换 + 截图按钮 -->
  <div class="flex items-center justify-between mb-5">
    <div class="flex gap-1 p-1 rounded-xl" style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);">
      <button id="subTabDailyBtn" class="sub-tab-active px-5 py-2 rounded-lg text-sm font-medium transition-all">日报表</button>
      <button id="subTabRangeBtn" class="sub-tab-inactive px-5 py-2 rounded-lg text-sm font-medium transition-all">区间报表</button>
    </div>
    <div class="flex items-center gap-2">
      <button id="refreshBtn" class="px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all" style="background: linear-gradient(135deg, #003087, #003da5); color: white; box-shadow: 0 2px 8px rgba(0,48,135,0.3);">
        <svg id="refreshIcon" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
        <span id="refreshText">刷新数据</span>
      </button>
      <button id="screenshotBtn" class="screenshot-btn px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        一键截图
      </button>
    </div>
  </div>

  <!-- ========== 日报表板块 ========== -->
  <div id="dailyPanel">
    <!-- 日期选择 -->
    <div class="flex items-center gap-2 mb-5">
      <button id="yesterdayBtn" class="text-xs px-3 py-1.5 rounded-lg font-medium transition-all" style="background: linear-gradient(135deg, #003087, #003da5); color: white; box-shadow: 0 2px 8px rgba(0,48,135,0.3);">昨日</button>
      <label class="text-xs text-slate-500">选择日期：</label>
      <select id="dailyDateSelect" class="border border-slate-200 rounded-xl px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none bg-white/90 shadow-sm"></select>
    </div>

    <!-- 本月经营目标（可编辑） -->
    <div class="glass-card rounded-2xl p-5 mb-5">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-xs font-semibold text-white px-2.5 py-1 rounded-md" style="background: linear-gradient(135deg, #003087, #003da5);">本月经营目标</span>
        <span id="bizMonthLabel" class="text-xs text-slate-400"></span>
        <span class="text-xs text-slate-400 ml-auto">点击目标值可编辑</span>
      </div>
      <div id="monthlyBizCards" class="grid grid-cols-1 md:grid-cols-3 gap-4"></div>
    </div>

    <!-- 当日核心数据KPI -->
    <div class="glass-card rounded-2xl p-5 mb-5">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-xs font-semibold text-white px-2.5 py-1 rounded-md" style="background: linear-gradient(135deg, #003087, #003da5);">当日核心数据</span>
        <span id="dailyKpiLabel" class="text-xs text-slate-400"></span>
      </div>
      <div id="dailyKpiCards" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"></div>
    </div>

    <!-- 当日转化漏斗 + 主播排名（左右两栏） -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
      <div class="glass-card rounded-2xl p-5">
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xs font-semibold text-white px-2.5 py-1 rounded-md" style="background: linear-gradient(135deg, #003087, #003da5);">当日转化漏斗</span>
          <span id="dailyFunnelLabel" class="text-xs text-slate-400"></span>
        </div>
        <div class="flex gap-2">
          <div id="chartDailyFunnel" style="height:380px; flex:1; min-width:0"></div>
          <div id="funnelTargets" style="width:180px; flex-shrink:0"></div>
        </div>
      </div>
      <div class="glass-card rounded-2xl p-5">
        <div class="flex items-center gap-2 mb-4">
          <span class="text-xs font-semibold text-white px-2.5 py-1 rounded-md" style="background: linear-gradient(135deg, #c8102e, #e63946);">当日主播排名</span>
          <span id="dailyAnchorLabel" class="text-xs text-slate-400"></span>
        </div>
        <div id="dailyAnchorRankList" class="space-y-3"></div>
      </div>
    </div>

    <!-- 今日+明日主播排版 -->
    <div class="grid grid-cols-2 gap-5 mt-5">
      <!-- 今日排班明细 -->
      <div class="glass-card rounded-2xl p-5 border border-amber-200/50" style="background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(254,251,235,0.95));">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background: linear-gradient(135deg, #d4a574, #c8102e);">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <h3 class="text-base font-bold" style="color: #c8102e;">今日排班明细</h3>
          <span id="todayScheduleDate" class="text-xs text-slate-400 ml-auto"></span>
        </div>
        <div id="todayScheduleContent"></div>
      </div>

      <!-- 明日主播排版 -->
      <div class="glass-card rounded-2xl p-5 border border-blue-200/50" style="background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(239,246,255,0.95));">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background: linear-gradient(135deg, #003087, #003da5);">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          </div>
          <h3 class="text-base font-bold" style="color: #003087;">明日主播排版</h3>
          <span id="tomorrowScheduleDate" class="text-xs text-slate-400 ml-auto"></span>
        </div>
        <div id="tomorrowScheduleContent"></div>
      </div>
    </div>

    <!-- 抖音运营数据分析总结 -->
    <div class="glass-card rounded-2xl p-5 mt-5 border border-amber-200/50" style="background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(253,250,245,0.95));">
      <div class="flex items-center gap-2 mb-3">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background: linear-gradient(135deg, #003087, #003da5);">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
        </div>
        <h3 class="text-base font-bold" style="color: #003087;">抖音运营数据分析</h3>
        <span id="dailyAnalysisDate" class="text-xs text-slate-400 ml-auto"></span>
      </div>
      <div id="dailyAnalysisContent" class="text-sm text-slate-600 leading-relaxed space-y-3"></div>
    </div>

  </div>

  <!-- ========== 区间报表板块 ========== -->
  <div id="rangePanel" class="hidden">
    <!-- 日期范围筛选 -->
    <div class="flex items-center gap-3 mb-5 glass-card rounded-2xl p-4 flex-wrap">
      <label class="text-sm text-slate-600 font-medium">日期范围：</label>
      <input type="date" id="dateStart" class="border border-slate-200 rounded-xl px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none bg-white/90 shadow-sm">
      <span class="text-slate-400">至</span>
      <input type="date" id="dateEnd" class="border border-slate-200 rounded-xl px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none bg-white/90 shadow-sm">
      <button id="resetDate" class="text-sm text-slate-500 hover:text-slate-700 px-3 py-1.5 rounded-lg hover:bg-slate-100 transition-colors">重置</button>
      <div class="flex items-center gap-2 ml-auto">
        <div class="flex gap-1">
          <button id="quickWeek" class="text-sm px-3 py-1.5 rounded-lg font-medium transition-all" style="background: linear-gradient(135deg, #003da5, #2563eb); color: white; box-shadow: 0 2px 8px rgba(0,61,165,0.3);">本周</button>
          <button id="quickMonth" class="text-sm px-3 py-1.5 rounded-lg font-medium transition-all" style="background: linear-gradient(135deg, #003087, #003da5); color: white; box-shadow: 0 2px 8px rgba(0,48,135,0.3);">本月</button>
          <button id="quickQuarter" class="text-sm px-3 py-1.5 rounded-lg font-medium transition-all" style="background: linear-gradient(135deg, #d4a574, #e8c99b); color: white; box-shadow: 0 2px 8px rgba(212,165,116,0.3);">本季度</button>
        </div>
        <span id="quickRangeLabel" class="text-xs text-slate-400 whitespace-nowrap"></span>
      </div>
    </div>

    <!-- 区间KPI卡片 -->
    <div id="kpiCards1" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-6"></div>

    <!-- 区间漏斗 + 小时均GMV -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
      <div class="bg-white rounded-xl shadow-sm p-4 border border-slate-100">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">流量转化漏斗（区间汇总）</h3>
        <div id="chartFunnel" class="chart-box" style="height:380px;min-height:380px"></div>
      </div>
      <div class="bg-white rounded-xl shadow-sm p-4 border border-slate-100">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">小时均GMV & 成交件数</h3>
        <div id="chartBar" class="chart-box"></div>
      </div>
    </div>

    <!-- 区间走势图 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
      <div class="bg-white rounded-xl shadow-sm p-4 border border-slate-100">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">GMV 趋势</h3>
        <div id="chartGmv" class="chart-box"></div>
      </div>
      <div class="bg-white rounded-xl shadow-sm p-4 border border-slate-100">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">ROI 趋势</h3>
        <div id="chartRoi" class="chart-box"></div>
      </div>
    </div>

    <!-- 区间关联走势图 -->
    <div class="mb-2">
      <h3 class="text-sm font-semibold text-slate-700 px-1">区间关联分析走势</h3>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
      <div class="bg-white rounded-xl shadow-sm p-4 border border-slate-100">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">GMV & ROI 走势</h3>
        <div id="chartGmvRoiRange" class="chart-box"></div>
      </div>
      <div class="bg-white rounded-xl shadow-sm p-4 border border-slate-100">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">商品曝光点击率 & ROI 走势</h3>
        <div id="chartClickRoiRange" class="chart-box"></div>
      </div>
      <div class="bg-white rounded-xl shadow-sm p-4 border border-slate-100">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">GMV & 点击成交转化率 走势</h3>
        <div id="chartGmvConvRange" class="chart-box"></div>
      </div>
      <div class="bg-white rounded-xl shadow-sm p-4 border border-slate-100">
        <h3 class="text-sm font-semibold text-slate-700 mb-2">直播间场观 & ROI 走势</h3>
        <div id="chartViewsRoiRange" class="chart-box"></div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="glass-card rounded-2xl overflow-hidden">
      <div class="p-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <h3 class="text-sm font-semibold text-slate-700">原始数据明细</h3>
        <input type="text" id="search1" placeholder="搜索日期、指标..." class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm w-56 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
      </div>
      <div class="overflow-x-auto">
        <table id="table1" class="w-full text-xs">
          <thead class="bg-slate-50 text-slate-600"></thead>
          <tbody class="text-slate-700"></tbody>
        </table>
      </div>
      <div id="pagination1" class="pagination flex items-center justify-between p-3 border-t border-slate-100 text-sm text-slate-600"></div>
    </div>

    <!-- 数据分析框 -->
    <div class="analysis-box rounded-2xl p-5 mt-5">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-xs font-semibold text-white px-2.5 py-1 rounded-md" style="background: linear-gradient(135deg, #003087, #003da5);">数据洞察分析</span>
        <span id="analysisLabel" class="text-xs text-slate-400"></span>
      </div>
      <div id="analysisContent" class="text-sm text-slate-700 leading-relaxed space-y-2"></div>
    </div>
  </div>
</section>

<!-- ==================== Tab 2：日主播数据报表 ==================== -->
<section id="tab2" class="pt-6 hidden">

  <!-- 月度主播排名 -->
  <div class="glass-card rounded-2xl p-5 mb-5">
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xs font-semibold text-white px-2.5 py-1 rounded-md" style="background: linear-gradient(135deg, #003087, #003da5);">月度排名</span>
      <span id="monthRankLabel" class="text-xs text-slate-400"></span>
    </div>
    <div id="monthRankList" class="space-y-3"></div>
  </div>

  <!-- 周度主播排名 -->
  <div class="glass-card rounded-2xl p-5 mb-5">
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xs font-semibold text-white px-2.5 py-1 rounded-md" style="background: linear-gradient(135deg, #003da5, #2563eb);">周度排名</span>
      <span id="weekRankLabel" class="text-xs text-slate-400"></span>
    </div>
    <div id="weekRankList" class="space-y-3"></div>
  </div>

  <!-- 日度主播排名 -->
  <div class="glass-card rounded-2xl p-5 mb-5">
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xs font-semibold text-white px-2.5 py-1 rounded-md" style="background: linear-gradient(135deg, #c8102e, #e63946);">日度排名</span>
      <span id="dayRankLabel" class="text-xs text-slate-400"></span>
    </div>
    <div id="dayRankList" class="space-y-3"></div>
  </div>

  <!-- 数据表格 -->
  <div class="glass-card rounded-2xl overflow-hidden">
    <div class="p-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
      <h3 class="text-sm font-semibold text-slate-700">主播数据明细</h3>
      <input type="text" id="search2" placeholder="搜索主播、日期、场控..." class="border border-slate-300 rounded-lg px-3 py-1.5 text-sm w-56 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
    </div>
    <div class="overflow-x-auto">
      <table id="table2" class="w-full text-xs">
        <thead class="bg-slate-50 text-slate-600"></thead>
        <tbody class="text-slate-700"></tbody>
      </table>
    </div>
    <div id="pagination2" class="pagination flex items-center justify-between p-3 border-t border-slate-100 text-sm text-slate-600"></div>
  </div>
</section>

</main>

<script>
// ==================== 数据 ====================
const RAW_DAILY = {data1_json};
const RAW_ANCHOR = {data2_json};
const SCHEDULE = {schedule_json};

// 数据清洗：修正异常比率值
function cleanData(arr) {{
  return arr.map(r => {{
    const row = {{...r}};
    // 比率字段：>1先除以100（视为百分比格式），超出0-1合理范围的设为null
    ['interactionRateCount','interactionRateUser','exposureToWatchRate','watchToProductRate','productClickRate','clickToBuyRate','refundRate'].forEach(k => {{
      if (row[k] !== null && row[k] !== undefined && !isNaN(row[k])) {{
        if (row[k] > 1) row[k] = row[k] / 100;
        if (row[k] > 1 || row[k] < 0) row[k] = null;
      }}
    }});
    // 极端异常ROI（正常ROI一般0-5）
    if (row.couponRoi !== null && (row.couponRoi > 10 || row.couponRoi < 0)) row.couponRoi = null;
    if (row.overallRoi !== null && (row.overallRoi > 10 || row.overallRoi < 0)) row.overallRoi = null;
    // 新增粉丝单日超过1000视为异常
    if (row.newFans !== null && row.newFans > 1000) row.newFans = null;
    // 互动人数超过场观视为异常
    if (row.interactionUsers !== null && row.views !== null && row.interactionUsers > row.views) row.interactionUsers = null;
    return row;
  }});
}}
const DAILY = cleanData(RAW_DAILY);
const ANCHOR = RAW_ANCHOR;

// ==================== 工具函数 ====================
const fmt = {{
  num: v => v === null || v === undefined || isNaN(v) ? '-' : Number(v).toLocaleString('zh-CN', {{maximumFractionDigits: 2}}),
  int: v => v === null || v === undefined || isNaN(v) ? '-' : Math.round(Number(v)).toLocaleString('zh-CN'),
  pct: v => v === null || v === undefined || isNaN(v) ? '-' : (Number(v)*100).toFixed(2) + '%',
  money: v => v === null || v === undefined || isNaN(v) ? '-' : '¥' + Number(v).toLocaleString('zh-CN', {{maximumFractionDigits: 0}}),
  date: v => v ? v : '-',
  shortDate: v => v ? v.slice(2) : '-'
}};

function sum(arr, key) {{ return arr.reduce((s,r) => s + (r[key]||0), 0); }}
function avg(arr, key) {{ const valid = arr.filter(r => r[key]!==null && r[key]!==undefined); return valid.length ? sum(valid,key)/valid.length : 0; }}

// ==================== 日期筛选 ====================
let dateStart = '', dateEnd = '';

function getFiltered(tab) {{
  const data = tab === 1 ? DAILY : ANCHOR;
  return data.filter(r => {{
    if (dateStart && r.date < dateStart) return false;
    if (dateEnd && r.date > dateEnd) return false;
    return true;
  }});
}}

function initDateFilters() {{
  const dates1 = DAILY.map(r=>r.date).sort();
  const dates2 = ANCHOR.map(r=>r.date).sort();
  const allDates = [...dates1, ...dates2].sort();
  const min = allDates[0], max = allDates[allDates.length-1];
  document.getElementById('dateStart').min = min;
  document.getElementById('dateStart').max = max;
  document.getElementById('dateEnd').min = min;
  document.getElementById('dateEnd').max = max;
  document.getElementById('dateStart').value = min;
  document.getElementById('dateEnd').value = max;
  dateStart = min; dateEnd = max;
}}

// ==================== Tab 切换 ====================
let currentTab = 1;
const charts = {{}};

function switchTab(tab) {{
  currentTab = tab;
  document.getElementById('tab1').classList.toggle('hidden', tab !== 1);
  document.getElementById('tab2').classList.toggle('hidden', tab !== 2);
  document.getElementById('tab1Btn').className = tab===1 ? 'tab-active px-6 py-2.5 rounded-t-lg text-sm font-medium transition-all' : 'tab-inactive px-6 py-2.5 rounded-t-lg text-sm font-medium transition-all';
  document.getElementById('tab2Btn').className = tab===2 ? 'tab-active px-6 py-2.5 rounded-t-lg text-sm font-medium transition-all' : 'tab-inactive px-6 py-2.5 rounded-t-lg text-sm font-medium transition-all';
  setTimeout(() => renderAll(), 50);
}}

// ==================== KPI 卡片 ====================
function renderKPI1(data) {{
  const kpis = [
    {{label:'总GMV', value: fmt.money(sum(data,'totalGmv')), sub:'区间合计', color:'text-blue-600', bg:'bg-blue-50'}},
    {{label:'投放消耗', value: fmt.money(sum(data,'adSpend')), sub:'区间合计', color:'text-orange-600', bg:'bg-orange-50'}},
    {{label:'整体ROI', value: fmt.num(avg(data,'overallRoi')), sub:'区间均值', color:'text-green-600', bg:'bg-green-50'}},
    {{label:'场观', value: fmt.int(sum(data,'views')), sub:'区间合计', color:'text-purple-600', bg:'bg-purple-50'}},
    {{label:'成交件数', value: fmt.int(sum(data,'orders')), sub:'区间合计', color:'text-pink-600', bg:'bg-pink-50'}},
    {{label:'客单价', value: fmt.num(avg(data,'avgOrderValue')), sub:'区间均值', color:'text-cyan-600', bg:'bg-cyan-50'}},
    {{label:'退款率', value: fmt.pct(avg(data,'refundRate')), sub:'区间均值', color:'text-red-600', bg:'bg-red-50'}}
  ];
  document.getElementById('kpiCards1').innerHTML = kpis.map(k => `
    <div class="kpi-card glass-card rounded-2xl p-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-slate-500">${{k.label}}</span>
        <span class="w-2 h-2 rounded-full ${{k.bg}}"></span>
      </div>
      <div class="text-lg font-bold ${{k.color}}">${{k.value}}</div>
      <div class="text-xs text-slate-400 mt-1">${{k.sub}}</div>
    </div>
  `).join('');
}}

// ==================== Tab2 主播排名 ====================
function getAnchorRank(data) {{
  const anchors = [...new Set(data.map(r=>r.anchor))];
  const list = anchors.map(a => {{
    const rows = data.filter(r=>r.anchor===a);
    const gmv = sum(rows,'gmv');
    const spend = sum(rows,'adSpend');
    const duration = sum(rows,'duration');
    const roi = spend>0 ? gmv/spend : 0;
    const hourlyGmv = duration>0 ? gmv/duration : 0;
    return {{ anchor:a, gmv, spend, roi, duration, hourlyGmv, sessions:rows.length }};
  }});
  // 综合评分：GMV 40% + 小时均GMV 30% + ROI 30%（min-max标准化）
  const norm = (arr, key) => {{
    const vals = arr.map(x=>x[key]).filter(v=>v>0);
    if (!vals.length) return arr.map(()=>0);
    const mx = Math.max(...vals), mn = Math.min(...vals);
    return arr.map(x => mx>mn ? (x[key]-mn)/(mx-mn) : 0.5);
  }};
  const nGmv = norm(list,'gmv'), nHourly = norm(list,'hourlyGmv'), nRoi = norm(list,'roi');
  list.forEach((x,i) => {{ x.score = nGmv[i]*0.4 + nHourly[i]*0.3 + nRoi[i]*0.3; }});
  return list.sort((a,b)=>b.score-a.score);
}}

function renderRankList(containerId, rankData, labelEl, labelText) {{
  const container = document.getElementById(containerId);
  document.getElementById(labelEl).textContent = labelText;
  if (!rankData.length) {{
    container.innerHTML = '<div class="text-center text-slate-400 py-6 text-sm">暂无数据</div>';
    return;
  }}
  const rankColors = ['bg-yellow-400','bg-gray-400','bg-orange-400'];
  container.innerHTML = rankData.map((item,i) => {{
    const isTop3 = i < 3;
    return `
    <div class="flex items-center gap-4 p-3 rounded-lg ${{isTop3?'bg-gradient-to-r from-slate-50 to-white border border-slate-100':'hover:bg-slate-50'}} transition-colors">
      <div class="flex-shrink-0 w-8 h-8 rounded-full ${{isTop3?rankColors[i]:'bg-slate-200'}} flex items-center justify-center text-white font-bold text-sm">${{i+1}}</div>
      <div class="flex-shrink-0 w-20 font-semibold text-slate-700">${{item.anchor}}</div>
      <div class="flex-1 grid grid-cols-2 md:grid-cols-5 gap-3">
        <div><div class="text-xs text-slate-400">GMV</div><div class="text-sm font-bold text-blue-600">${{fmt.money(item.gmv)}}</div></div>
        <div><div class="text-xs text-slate-400">小时均GMV</div><div class="text-sm font-bold text-cyan-600">${{fmt.money(item.hourlyGmv)}}</div></div>
        <div><div class="text-xs text-slate-400">ROI</div><div class="text-sm font-bold text-emerald-600">${{item.roi?item.roi.toFixed(2):'-'}}</div></div>
        <div><div class="text-xs text-slate-400">消耗</div><div class="text-sm font-medium text-orange-600">${{fmt.money(item.spend)}}</div></div>
        <div><div class="text-xs text-slate-400">时长/场次</div><div class="text-sm font-medium text-slate-600">${{item.duration?item.duration.toFixed(1):0}}h / ${{item.sessions}}场</div></div>
      </div>
    </div>`;
  }}).join('');
}}

function renderMonthRank() {{
  const now = new Date();
  const y = now.getFullYear(), m = now.getMonth()+1;
  const prefix = `${{y}}-${{String(m).padStart(2,'0')}}`;
  const data = ANCHOR.filter(r=>r.date && r.date.startsWith(prefix));
  const rank = getAnchorRank(data);
  renderRankList('monthRankList', rank, 'monthRankLabel', `${{y}}年${{m}}月（${{data.length}}场）`);
}}

function renderWeekRank() {{
  const dates = [...new Set(ANCHOR.map(r=>r.date))].sort();
  const latest = dates[dates.length-1];
  if (!latest) {{ renderRankList('weekRankList', [], 'weekRankLabel', ''); return; }}
  const weekAgo = new Date(latest);
  weekAgo.setDate(weekAgo.getDate() - 6);
  const weekStart = weekAgo.toISOString().slice(0,10);
  const data = ANCHOR.filter(r=>r.date >= weekStart && r.date <= latest);
  const rank = getAnchorRank(data);
  renderRankList('weekRankList', rank, 'weekRankLabel', `${{weekStart}} ~ ${{latest}}（${{data.length}}场）`);
}}

function renderDayRank() {{
  const dates = [...new Set(ANCHOR.map(r=>r.date))].sort();
  const latest = dates[dates.length-1];
  const data = ANCHOR.filter(r=>r.date === latest);
  const rank = getAnchorRank(data);
  renderRankList('dayRankList', rank, 'dayRankLabel', `${{latest}}（${{data.length}}场）`);
}}

// ==================== 图表 ====================
function getChart(id) {{
  if (!charts[id]) charts[id] = echarts.init(document.getElementById(id));
  return charts[id];
}}

const baseTextStyle = {{ fontSize: 11, color: '#64748b' }};

function renderGmvChart(data) {{
  const chart = getChart('chartGmv');
  chart.setOption({{
    tooltip: {{ trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#e2e8f0', textStyle: {{fontSize:12}}, formatter: p => {{
      let s = p[0].axisValue + '<br/>';
      p.forEach(item => {{ s += `${{item.marker}} ${{item.seriesName}}: ${{fmt.money(item.value)}}<br/>`; }});
      return s;
    }} }},
    legend: {{ data: ['总GMV(加优惠券)','GMV'], top: 0, textStyle: baseTextStyle }},
    grid: {{ left: 50, right: 20, top: 35, bottom: 30 }},
    xAxis: {{ type: 'category', data: data.map(r=>fmt.shortDate(r.date)), axisLabel: baseTextStyle, axisLine: {{lineStyle:{{color:'#e2e8f0'}}}} }},
    yAxis: {{ type: 'value', axisLabel: {{...baseTextStyle, formatter: v => v>=10000?(v/10000)+'万':v}}, splitLine: {{lineStyle:{{color:'#f1f5f9'}}}} }},
    series: [
      {{ name: '总GMV(加优惠券)', type: 'line', smooth: true, data: data.map(r=>r.totalGmv), itemStyle:{{color:'#2563eb'}}, areaStyle:{{color:{{type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{{offset:0,color:'rgba(37,99,235,0.2)'}},{{offset:1,color:'rgba(37,99,235,0)'}}]}}}} }},
      {{ name: 'GMV', type: 'line', smooth: true, data: data.map(r=>r.gmv), itemStyle:{{color:'#f59e0b'}}, lineStyle:{{type:'dashed'}} }}
    ]
  }});
}}

function renderRoiChart(data) {{
  const chart = getChart('chartRoi');
  chart.setOption({{
    tooltip: {{ trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#e2e8f0', textStyle: {{fontSize:12}} }},
    legend: {{ data: ['整体ROI','智能优惠券ROI'], top: 0, textStyle: baseTextStyle }},
    grid: {{ left: 45, right: 20, top: 35, bottom: 30 }},
    xAxis: {{ type: 'category', data: data.map(r=>fmt.shortDate(r.date)), axisLabel: baseTextStyle, axisLine: {{lineStyle:{{color:'#e2e8f0'}}}} }},
    yAxis: {{ type: 'value', axisLabel: baseTextStyle, splitLine: {{lineStyle:{{color:'#f1f5f9'}}}} }},
    series: [
      {{ name: '整体ROI', type: 'line', smooth: true, data: data.map(r=>r.overallRoi), itemStyle:{{color:'#10b981'}} }},
      {{ name: '智能优惠券ROI', type: 'line', smooth: true, data: data.map(r=>r.couponRoi), itemStyle:{{color:'#8b5cf6'}} }}
    ]
  }});
}}

function renderFunnelChart(data) {{
  // 优先使用绝对值字段汇总
  const hasAbs = data.some(r => r.exposureCount > 0);
  let exposure, totalViews, productExp, productClick, buyers;
  if (hasAbs) {{
    exposure = sum(data, 'exposureCount');
    totalViews = sum(data, 'watchCount');
    productExp = sum(data, 'productExposureCount');
    productClick = sum(data, 'productClickCount');
    buyers = sum(data, 'buyerCount');
    if (totalViews === 0) totalViews = sum(data, 'views');
  }} else {{
    const valid = data.filter(r => r.views > 0 && r.exposureToWatchRate !== null && r.watchToProductRate !== null && r.productClickRate !== null && r.clickToBuyRate !== null);
    totalViews = sum(valid, 'views');
    const wAvg = (key) => {{
      const v = valid.filter(r => r[key]!==null);
      if (!v.length) return 0;
      return v.reduce((s,r) => s + r.views * r[key], 0) / totalViews;
    }};
    exposure = wAvg('exposureToWatchRate') > 0 ? totalViews / wAvg('exposureToWatchRate') : totalViews;
    productExp = totalViews * wAvg('watchToProductRate');
    productClick = productExp * wAvg('productClickRate');
    buyers = productClick * wAvg('clickToBuyRate');
  }}
  const funnelData = [
    {{ value: Math.round(exposure), name: '直播间曝光' }},
    {{ value: Math.round(totalViews), name: '直播间观看' }},
    {{ value: Math.round(productExp), name: '商品曝光' }},
    {{ value: Math.round(productClick), name: '商品点击' }},
    {{ value: Math.round(buyers), name: '成交' }}
  ];
  renderSvgFunnel('chartFunnel', funnelData);
}}

function renderBarChart(data) {{
  const chart = getChart('chartBar');
  chart.setOption({{
    tooltip: {{ trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#e2e8f0', textStyle: {{fontSize:12}} }},
    legend: {{ data: ['小时均GMV','成交件数'], top: 0, textStyle: baseTextStyle }},
    grid: {{ left: 50, right: 20, top: 35, bottom: 30 }},
    xAxis: {{ type: 'category', data: data.map(r=>fmt.shortDate(r.date)), axisLabel: baseTextStyle, axisLine: {{lineStyle:{{color:'#e2e8f0'}}}} }},
    yAxis: [
      {{ type: 'value', name: '小时均GMV', axisLabel: baseTextStyle, splitLine: {{lineStyle:{{color:'#f1f5f9'}}}} }},
      {{ type: 'value', name: '成交件数', axisLabel: baseTextStyle, splitLine: {{show:false}} }}
    ],
    series: [
      {{ name: '小时均GMV', type: 'bar', data: data.map(r=>r.hourlyGmv), itemStyle:{{color:'#2563eb', borderRadius:[4,4,0,0]}} }},
      {{ name: '成交件数', type: 'line', yAxisIndex: 1, smooth: true, data: data.map(r=>r.orders), itemStyle:{{color:'#f59e0b'}} }}
    ]
  }});
}}

// 通用双轴走势图
function renderDualAxisChart(chartId, data, opt) {{
  const chart = getChart(chartId);
  chart.setOption({{
    tooltip: {{
      trigger: 'axis',
      backgroundColor: 'rgba(15,23,42,0.92)',
      borderColor: 'transparent',
      textStyle: {{ color: '#fff', fontSize: 12 }},
      formatter: (p) => {{
        let s = p[0].axisValue + '<br/>';
        p.forEach(item => {{
          if (item.value != null) {{
            const v = opt.leftSeries === item.seriesName && opt.leftFmt ? opt.leftFmt(item.value) :
                      opt.rightSeries === item.seriesName && opt.rightFmt ? opt.rightFmt(item.value) : item.value;
            s += `${{item.marker}} ${{item.seriesName}}: <b>${{v}}</b><br/>`;
          }}
        }});
        return s;
      }}
    }},
    legend: {{ data: [opt.leftSeries, opt.rightSeries], top: 0, textStyle: baseTextStyle, itemWidth: 12, itemHeight: 8 }},
    grid: {{ left: 55, right: 55, top: 35, bottom: 30 }},
    xAxis: {{ type: 'category', data: data.map(r=>fmt.shortDate(r.date)), axisLabel: baseTextStyle, axisLine: {{lineStyle:{{color:'#e2e8f0'}}}} }},
    yAxis: [
      {{ type: 'value', name: opt.leftName, nameTextStyle: {{color:'#94a3b8',fontSize:10}}, axisLabel: {{...baseTextStyle, formatter: opt.leftAxisFmt || (v=>v)}}, splitLine: {{lineStyle:{{color:'#f1f5f9'}}}} }},
      {{ type: 'value', name: opt.rightName, nameTextStyle: {{color:'#94a3b8',fontSize:10}}, axisLabel: {{...baseTextStyle, formatter: opt.rightAxisFmt || (v=>v)}}, splitLine: {{show:false}} }}
    ],
    series: [
      {{ name: opt.leftSeries, type: 'bar', data: data.map(r=>r[opt.leftKey]), itemStyle:{{color: opt.leftColor, borderRadius:[4,4,0,0]}}, barMaxWidth: 30 }},
      {{ name: opt.rightSeries, type: 'line', yAxisIndex: 1, smooth: true, data: data.map(r=>r[opt.rightKey]), itemStyle:{{color: opt.rightColor}}, lineStyle:{{width:2.5}}, symbol: 'circle', symbolSize: 5 }}
    ]
  }});
}}

// 区间报表走势图
function renderGmvRoiRangeChart(data) {{ renderDualAxisChart('chartGmvRoiRange', data, {{ leftKey:'totalGmv',leftName:'GMV',leftSeries:'总GMV',leftColor:'#2563eb',rightKey:'overallRoi',rightName:'ROI',rightSeries:'整体ROI',rightColor:'#10b981',leftFmt:v=>'¥'+v.toLocaleString(),rightFmt:v=>v.toFixed(2),leftAxisFmt:v=>v>=10000?(v/10000)+'万':v }}); }}
function renderClickRoiRangeChart(data) {{ renderDualAxisChart('chartClickRoiRange', data, {{ leftKey:'productClickRate',leftName:'点击率',leftSeries:'商品曝光点击率',leftColor:'#f59e0b',rightKey:'overallRoi',rightName:'ROI',rightSeries:'整体ROI',rightColor:'#10b981',leftFmt:v=>(v*100).toFixed(2)+'%',rightFmt:v=>v.toFixed(2),leftAxisFmt:v=>(v*100).toFixed(0)+'%' }}); }}
function renderGmvConvRangeChart(data) {{ renderDualAxisChart('chartGmvConvRange', data, {{ leftKey:'totalGmv',leftName:'GMV',leftSeries:'总GMV',leftColor:'#2563eb',rightKey:'clickToBuyRate',rightName:'转化率',rightSeries:'点击成交转化率',rightColor:'#8b5cf6',leftFmt:v=>'¥'+v.toLocaleString(),rightFmt:v=>(v*100).toFixed(2)+'%',leftAxisFmt:v=>v>=10000?(v/10000)+'万':v,rightAxisFmt:v=>(v*100).toFixed(0)+'%' }}); }}
function renderViewsRoiRangeChart(data) {{ renderDualAxisChart('chartViewsRoiRange', data, {{ leftKey:'views',leftName:'场观',leftSeries:'直播间场观',leftColor:'#06b6d4',rightKey:'overallRoi',rightName:'ROI',rightSeries:'整体ROI',rightColor:'#10b981',leftFmt:v=>v.toLocaleString(),rightFmt:v=>v.toFixed(2),leftAxisFmt:v=>v>=10000?(v/10000)+'万':v }}); }}

// ==================== 数据表格 ====================
const table1Cols = [
  {{key:'date',label:'日期',fmt:fmt.date}},
  {{key:'totalGmv',label:'总GMV',fmt:fmt.money}},
  {{key:'duration',label:'直播时长(h)',fmt:fmt.num}},
  {{key:'hourlyGmv',label:'小时均GMV',fmt:fmt.num}},
  {{key:'views',label:'场观',fmt:fmt.int}},
  {{key:'orders',label:'成交件数',fmt:fmt.int}},
  {{key:'avgOrderValue',label:'客单价',fmt:fmt.num}},
  {{key:'adSpend',label:'投放消耗',fmt:fmt.money}},
  {{key:'overallRoi',label:'整体ROI',fmt:fmt.num}},
  {{key:'couponRoi',label:'优惠券ROI',fmt:fmt.num}},
  {{key:'uvValue',label:'UV值',fmt:fmt.num}},
  {{key:'refundAmount',label:'退款金额',fmt:fmt.money}},
  {{key:'refundRate',label:'退款率',fmt:fmt.pct}},
  {{key:'interactions',label:'互动次数',fmt:fmt.int}},
  {{key:'interactionUsers',label:'互动人数',fmt:fmt.int}},
  {{key:'newFans',label:'新增粉丝',fmt:fmt.int}},
  {{key:'exposureToWatchRate',label:'曝光-观看率',fmt:fmt.pct}},
  {{key:'watchToProductRate',label:'观看-商品曝光率',fmt:fmt.pct}},
  {{key:'productClickRate',label:'商品曝光-点击率',fmt:fmt.pct}},
  {{key:'clickToBuyRate',label:'点击-成交转化率',fmt:fmt.pct}}
];

const table2Cols = [
  {{key:'anchor',label:'主播',fmt:v=>v||'-'}},
  {{key:'date',label:'日期',fmt:fmt.date}},
  {{key:'duration',label:'时长(h)',fmt:fmt.num}},
  {{key:'gmv',label:'GMV',fmt:fmt.money}},
  {{key:'adSpend',label:'投放消耗',fmt:fmt.money}},
  {{key:'paidAmount',label:'付费成交',fmt:fmt.money}},
  {{key:'couponAmount',label:'优惠券成交',fmt:fmt.money}},
  {{key:'overallRoi',label:'整体ROI',fmt:fmt.num}},
  {{key:'exposureClickRate',label:'曝光点击率',fmt:fmt.pct}},
  {{key:'clickToBuyRate',label:'点击成交率',fmt:fmt.pct}},
  {{key:'controller',label:'场控',fmt:v=>v||'-'}}
];

let tableState = {{ 1:{{page:1,pageSize:15,sortKey:null,sortDir:null,search:''}}, 2:{{page:1,pageSize:15,sortKey:null,sortDir:null,search:''}} }};

function renderTable(tab) {{
  const cols = tab===1 ? table1Cols : table2Cols;
  const state = tableState[tab];
  const tableId = tab===1 ? 'table1' : 'table2';
  const pagId = tab===1 ? 'pagination1' : 'pagination2';
  let data = getFiltered(tab);

  // 搜索
  if (state.search) {{
    const q = state.search.toLowerCase();
    data = data.filter(r => cols.some(c => String(r[c.key]||'').toLowerCase().includes(q)));
  }}
  // 排序
  if (state.sortKey) {{
    data = [...data].sort((a,b) => {{
      let va=a[state.sortKey], vb=b[state.sortKey];
      if(va===null||va===undefined) va=''; if(vb===null||vb===undefined) vb='';
      if(typeof va==='number'&&typeof vb==='number') return state.sortDir==='asc'?va-vb:vb-va;
      return state.sortDir==='asc'?String(va).localeCompare(String(vb)):String(vb).localeCompare(String(va));
    }});
  }}
  // 分页
  const total = data.length;
  const totalPages = Math.max(1, Math.ceil(total/state.pageSize));
  if (state.page > totalPages) state.page = totalPages;
  const start = (state.page-1)*state.pageSize;
  const pageData = data.slice(start, start+state.pageSize);

  // 表头
  const thead = document.querySelector(`#${{tableId}} thead`);
  thead.innerHTML = '<tr>' + cols.map(c => {{
    const sortCls = state.sortKey===c.key ? (state.sortDir==='asc'?'sort-asc':'sort-desc') : '';
    const arrow = state.sortKey===c.key ? (state.sortDir==='asc'?'▲':'▼') : '⇅';
    return `<th class="px-3 py-2 text-left font-medium border-b border-slate-200 ${{sortCls}}" data-key="${{c.key}}">${{c.label}}<span class="sort-icon">${{arrow}}</span></th>`;
  }}).join('') + '</tr>';

  // 表体
  const tbody = document.querySelector(`#${{tableId}} tbody`);
  tbody.innerHTML = pageData.length ? pageData.map(r => '<tr class="border-b border-slate-50">' + cols.map(c => `<td class="px-3 py-2 whitespace-nowrap">${{c.fmt(r[c.key])}}</td>`).join('') + '</tr>').join('') : '<tr><td colspan="'+cols.length+'" class="text-center py-8 text-slate-400">暂无数据</td></tr>';

  // 分页
  const pag = document.getElementById(pagId);
  let pageBtns = '';
  const maxBtn = 5;
  let startP = Math.max(1, state.page - 2);
  let endP = Math.min(totalPages, startP + maxBtn - 1);
  if (endP - startP < maxBtn - 1) startP = Math.max(1, endP - maxBtn + 1);
  for (let i = startP; i <= endP; i++) {{
    pageBtns += `<button class="px-2 py-1 rounded text-xs ${{i===state.page?'active':'hover:bg-slate-100'}}" data-page="${{i}}">${{i}}</button>`;
  }}
  pag.innerHTML = `
    <span>共 ${{total}} 条，第 ${{state.page}}/${{totalPages}} 页</span>
    <div class="flex gap-1 items-center">
      <button class="px-2 py-1 rounded text-xs hover:bg-slate-100 disabled:opacity-30" data-page="prev" ${{state.page<=1?'disabled':''}}>上一页</button>
      ${{pageBtns}}
      <button class="px-2 py-1 rounded text-xs hover:bg-slate-100 disabled:opacity-30" data-page="next" ${{state.page>=totalPages?'disabled':''}}>下一页</button>
    </div>
  `;

  // 绑定排序
  thead.querySelectorAll('th').forEach(th => {{
    th.onclick = () => {{
      const key = th.dataset.key;
      if (state.sortKey === key) {{
        state.sortDir = state.sortDir==='asc' ? 'desc' : (state.sortDir==='desc'?null:'asc');
        if (!state.sortDir) state.sortKey = null;
      }} else {{ state.sortKey = key; state.sortDir = 'asc'; }}
      state.page = 1;
      renderTable(tab);
    }};
  }});
  // 绑定分页
  pag.querySelectorAll('button[data-page]').forEach(btn => {{
    btn.onclick = () => {{
      const p = btn.dataset.page;
      if (p==='prev') state.page = Math.max(1, state.page-1);
      else if (p==='next') state.page = Math.min(totalPages, state.page+1);
      else state.page = parseInt(p);
      renderTable(tab);
    }};
  }});
}}

// ==================== 日数据转化率报表 ====================
let CONVERSION_TARGETS = JSON.parse(localStorage.getItem('conversionTargets') || 'null') || {{
  exposureToWatch: 0.15,
  watchToProduct: 0.92,
  productClick: 0.30,
  clickToBuy: 0.18
}};
let BIZ_TARGETS = JSON.parse(localStorage.getItem('bizTargets') || 'null') || {{
  gmv: 1000000,
  adSpend: 500000,
  roi: 2.0
}};
function saveBizTargets() {{ localStorage.setItem('bizTargets', JSON.stringify(BIZ_TARGETS)); }}

function saveTargets() {{
  localStorage.setItem('conversionTargets', JSON.stringify(CONVERSION_TARGETS));
}}

function initDailyDateSelect() {{
  const select = document.getElementById('dailyDateSelect');
  const dates = [...new Set(DAILY.map(r=>r.date))].sort().reverse();
  select.innerHTML = dates.map(d => `<option value="${{d}}">${{d}}</option>`).join('');
  if (dates.length) select.value = dates[0];
}}

function getMonthData(year, month) {{
  const prefix = `${{year}}-${{String(month).padStart(2,'0')}}`;
  return DAILY.filter(r => r.date && r.date.startsWith(prefix));
}}

function getRecent30Days(dateStr) {{
  const idx = DAILY.findIndex(r => r.date === dateStr);
  if (idx === -1) return DAILY.slice(-30);
  const start = Math.max(0, idx - 29);
  return DAILY.slice(start, idx + 1).sort((a,b) => a.date.localeCompare(b.date));
}}

// 本月经营目标卡片（GMV、消耗、ROI）
function renderMonthlyBizCards() {{
  const select = document.getElementById('dailyDateSelect');
  const selDate = select.value;
  const [year, month] = selDate ? selDate.split('-').map(Number) : [new Date().getFullYear(), new Date().getMonth()+1];
  const monthData = getMonthData(year, month);
  const container = document.getElementById('monthlyBizCards');
  document.getElementById('bizMonthLabel').textContent = `${{year}}年${{month}}月（共${{monthData.length}}天）`;

  if (!monthData.length) {{
    container.innerHTML = '<div class="col-span-full text-center text-slate-400 py-8 text-sm">本月暂无数据</div>';
    return;
  }}

  const totalGmv = sum(monthData, 'totalGmv');
  const totalSpend = sum(monthData, 'adSpend');
  const avgRoi = totalSpend > 0 ? totalGmv / totalSpend : null;
  const daysInMonth = new Date(year, month, 0).getDate();
  const timeProgress = Math.min(100, (monthData.length / daysInMonth) * 100);

  const metrics = [
    {{ key:'gmv', label:'本月GMV', actual: totalGmv, target: BIZ_TARGETS.gmv, fmt: v=>'¥'+v.toLocaleString(), bar:'bg-blue-500', text:'text-blue-600', inverse:false }},
    {{ key:'adSpend', label:'本月消耗', actual: totalSpend, target: BIZ_TARGETS.adSpend, fmt: v=>'¥'+v.toLocaleString(), bar:'bg-orange-500', text:'text-orange-600', inverse:true }},
    {{ key:'roi', label:'本月投产ROI', actual: avgRoi, target: BIZ_TARGETS.roi, fmt: v=>v!==null?v.toFixed(2):'-', bar:'bg-emerald-500', text:'text-emerald-600', inverse:false }}
  ];

  container.innerHTML = metrics.map(m => {{
    if (m.actual === null || m.actual === undefined) {{
      return `<div class="rounded-xl border border-slate-100 bg-white p-5"><div class="text-xs text-slate-400 mb-2">${{m.label}}</div><div class="text-2xl font-bold text-slate-400">-</div></div>`;
    }}
    const ratio = m.target > 0 ? m.actual / m.target : 0;
    const progress = Math.min(100, ratio*100);
    const reached = m.inverse ? m.actual <= m.target : m.actual >= m.target;
    const overBudget = m.inverse && m.actual > m.target;
    const diff = m.inverse ? (m.target - m.actual) : (m.target - m.actual);
    const aheadBy = progress - timeProgress;
    const aheadText = aheadBy >= 0 ? `超前 ${{aheadBy.toFixed(1)}}%` : `滞后 ${{Math.abs(aheadBy).toFixed(1)}}%`;
    const aheadColor = aheadBy >= 0 ? 'text-emerald-500' : 'text-red-500';
    return `
    <div class="rounded-xl border border-slate-100 bg-white p-5 hover:shadow-md transition-shadow">
      <div class="flex items-center justify-between mb-3">
        <span class="text-sm text-slate-500 font-medium">${{m.label}}</span>
        <div class="flex items-center gap-1">
          <span class="text-xs text-slate-400">目标</span>
          <input type="number" class="biz-target-input w-16 text-xs text-center border border-slate-200 rounded px-1 py-0.5 focus:ring-1 focus:ring-blue-400 outline-none" data-key="${{m.key}}" value="${{m.key==='roi'?m.target.toFixed(1):(m.target/10000).toFixed(0)}}" step="${{m.key==='roi'?'0.1':'10'}}">
          <span class="text-xs text-slate-400">${{m.key==='roi'?'':'万'}}</span>
        </div>
      </div>
      <div class="flex items-baseline gap-2 mb-3">
        <span class="text-3xl font-bold ${{m.text}}">${{m.fmt(m.actual)}}</span>
        <span class="text-sm ${{reached?'text-emerald-500':overBudget?'text-red-500':'text-slate-400'}} font-medium">${{reached?'✓ 达标':overBudget?'超预算':'差'+m.fmt(Math.abs(diff))}}</span>
      </div>
      <div class="w-full bg-slate-100 rounded-full h-2.5 mb-2 overflow-hidden relative">
        <div class="bg-slate-300 h-2.5 absolute left-0 top-0" style="width:${{timeProgress.toFixed(1)}}%"></div>
        <div class="${{overBudget?'bg-red-500':m.bar}} h-2.5 rounded-full relative transition-all duration-500" style="width:${{progress.toFixed(1)}}%"></div>
      </div>
      <div class="flex justify-between text-xs">
        <span class="text-slate-400">完成 <span class="${{overBudget?'text-red-500':m.text}} font-medium">${{progress.toFixed(1)}}%</span> · 时序 <span class="text-slate-500 font-medium">${{timeProgress.toFixed(1)}}%</span></span>
        <span class="${{aheadColor}} font-medium">${{aheadText}}</span>
      </div>
    </div>`;
  }}).join('');

  container.querySelectorAll('.biz-target-input').forEach(inp => {{
    inp.onchange = () => {{
      const key = inp.dataset.key;
      let val = parseFloat(inp.value);
      if (key !== 'roi') val = val * 10000;
      if (val > 0) {{
        BIZ_TARGETS[key] = val;
        saveBizTargets();
        renderMonthlyBizCards();
      }}
    }};
  }});
}}

// SVG漏斗图（均匀递减梯形，统一蓝色系）
function renderSvgFunnel(containerId, rawVals) {{
  const container = document.getElementById(containerId);
  if (!rawVals.length || !rawVals[0].value) {{ container.innerHTML = '<div class="text-center text-slate-400 py-12 text-sm">暂无数据</div>'; return; }}

  const W = 520, H = 380;
  const leftPad = 75, rightPad = 120;
  const funnelW = W - leftPad - rightPad;
  const n = rawVals.length;
  const gap = 8;
  const layerH = (H - 50 - gap*(n-1)) / n;
  const topY = 25;

  // 均匀递减宽度比例，保证形状规整
  const widthRatios = [1.0, 0.78, 0.60, 0.44, 0.28];
  const widths = rawVals.map((_,i) => funnelW * (widthRatios[i] || 0.28));

  // 统一蓝色系渐变（深→浅）
  const colors = ['#3b5bdb','#4263eb','#4c6ef5','#5c7cfa','#748ffc'];
  const gid = containerId.replace(/[^a-zA-Z0-9]/g, '');

  let svg = `<svg viewBox="0 0 ${{W}} ${{H}}" preserveAspectRatio="xMidYMid meet" style="width:100%;height:100%;font-family:inherit">`;
  svg += '<defs>';
  colors.forEach((c,i) => {{
    svg += `<linearGradient id="fg_${{gid}}_${{i}}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="${{c}}" stop-opacity="0.85"/><stop offset="100%" stop-color="${{c}}"/>
    </linearGradient>`;
  }});
  svg += `<marker id="arrow_${{gid}}" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
    <path d="M0,0 L7,3.5 L0,7 Z" fill="#adb5bd"/></marker>`;
  svg += '</defs>';

  // 左侧整体转化率
  const overallRate = rawVals[n-1].value / rawVals[0].value;
  svg += `<text x="${{leftPad-15}}" y="${{H/2-10}}" text-anchor="middle" fill="#1e293b" font-size="20" font-weight="bold">${{(overallRate*100).toFixed(2)}}%</text>`;
  svg += `<text x="${{leftPad-15}}" y="${{H/2+10}}" text-anchor="middle" fill="#64748b" font-size="11" font-weight="500">曝光-成交</text>`;
  svg += `<text x="${{leftPad-15}}" y="${{H/2+24}}" text-anchor="middle" fill="#64748b" font-size="11" font-weight="500">转化率(人数)</text>`;
  svg += `<path d="M${{leftPad-35}},${{topY+10}} L${{leftPad-35}},${{H-20}}" stroke="#e9ecef" stroke-width="1.5" fill="none"/>`;
  svg += `<path d="M${{leftPad-35}},${{H-20}} L${{leftPad-8}},${{H-20}}" stroke="#e9ecef" stroke-width="1.5" fill="none" marker-end="url(#arrow_${{gid}})"/>`;

  // 绘制每层
  for (let i = 0; i < n; i++) {{
    const w1 = widths[i];
    const w2 = i < n-1 ? widths[i+1] : widths[i] * 0.85;
    const y1 = topY + i*(layerH+gap);
    const y2 = y1 + layerH;
    const x1l = leftPad + (funnelW - w1)/2;
    const x1r = leftPad + (funnelW + w1)/2;
    const x2l = leftPad + (funnelW - w2)/2;
    const x2r = leftPad + (funnelW + w2)/2;

    svg += `<polygon points="${{x1l}},${{y1}} ${{x1r}},${{y1}} ${{x2r}},${{y2}} ${{x2l}},${{y2}}" fill="url(#fg_${{gid}}_${{i}})"/>`;

    // 内部文字（右对齐，贴近右侧）- 增大字号提升清晰度
    const tx = x2r - 14;
    svg += `<text x="${{tx}}" y="${{y1+layerH/2-2}}" text-anchor="end" fill="#ffffff" font-size="16" font-weight="bold">${{rawVals[i].value.toLocaleString()}}</text>`;
    svg += `<text x="${{tx}}" y="${{y1+layerH/2+15}}" text-anchor="end" fill="rgba(255,255,255,0.9)" font-size="11" font-weight="500">${{rawVals[i].name}}人数</text>`;

    // 右侧转化率 - 增大字号提升清晰度
    if (i > 0) {{
      const rate = rawVals[i].value / rawVals[i-1].value;
      const rx = leftPad + funnelW + 25;
      const ry = (y1+y2)/2;
      svg += `<text x="${{rx+28}}" y="${{ry-2}}" text-anchor="middle" fill="#1e293b" font-size="15" font-weight="bold">${{(rate*100).toFixed(2)}}%</text>`;
      svg += `<text x="${{rx+28}}" y="${{ry+13}}" text-anchor="middle" fill="#64748b" font-size="10" font-weight="500">${{rawVals[i-1].name}}-</text>`;
      svg += `<text x="${{rx+28}}" y="${{ry+25}}" text-anchor="middle" fill="#64748b" font-size="10" font-weight="500">${{rawVals[i].name}}率(人数)</text>`;
      const prevY = topY + (i-1)*(layerH+gap) + layerH;
      svg += `<line x1="${{x2r+3}}" y1="${{prevY}}" x2="${{rx+3}}" y2="${{ry-8}}" stroke="#dee2e6" stroke-width="1.2" marker-end="url(#arrow_${{gid}})"/>`;
    }}
  }}

  svg += '</svg>';
  container.innerHTML = svg;
}}

// 当日转化漏斗图
function renderDailyFunnelChart() {{
  const date = document.getElementById('dailyDateSelect').value;
  const row = DAILY.find(r => r.date === date);
  const label = document.getElementById('dailyFunnelLabel');
  if (!row) {{ label.textContent = date + ' 暂无数据'; document.getElementById('chartDailyFunnel').innerHTML=''; document.getElementById('funnelTargets').innerHTML=''; return; }}
  label.textContent = date;

  const rawVals = [
    {{ name: '直播间曝光', value: row.exposureCount||0 }},
    {{ name: '直播间观看', value: row.watchCount||0 }},
    {{ name: '商品曝光', value: row.productExposureCount||0 }},
    {{ name: '商品点击', value: row.productClickCount||0 }},
    {{ name: '成交', value: row.buyerCount||0 }}
  ];
  renderSvgFunnel('chartDailyFunnel', rawVals);

  // 转化率目标面板
  const rates = [
    {{ key:'exp2watch', name:'曝光→观看', actual: row.exposureCount? row.watchCount/row.exposureCount : 0 }},
    {{ key:'watch2prod', name:'观看→商品曝光', actual: row.watchCount? row.productExposureCount/row.watchCount : 0 }},
    {{ key:'prod2click', name:'商品曝光→点击', actual: row.productExposureCount? row.productClickCount/row.productExposureCount : 0 }},
    {{ key:'click2buy', name:'点击→成交', actual: row.productClickCount? row.buyerCount/row.productClickCount : 0 }}
  ];
  // 从localStorage读取目标
  let targets = {{}};
  try {{ targets = JSON.parse(localStorage.getItem('funnelTargets') || '{{}}'); }} catch(e) {{}}
  const defaultTargets = {{ exp2watch:15, watch2prod:80, prod2click:25, click2buy:15 }};

  const container = document.getElementById('funnelTargets');
  container.innerHTML = `
    <div class="text-xs font-semibold text-slate-600 mb-3 pb-2 border-b border-slate-200">转化率目标</div>
    ${{rates.map(r => {{
      const target = targets[r.key] !== undefined ? targets[r.key] : defaultTargets[r.key];
      const actualPct = (r.actual * 100);
      const met = actualPct >= target;
      return `
        <div class="mb-3">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs text-slate-500">${{r.name}}</span>
            <span class="text-xs font-bold ${{met?'target-met':'target-not-met'}}">${{actualPct.toFixed(2)}}%</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="text-xs text-slate-400">目标</span>
            <input type="number" class="target-input" data-key="${{r.key}}" value="${{target}}" min="0" max="100" step="0.1">
            <span class="text-xs text-slate-400">%</span>
          </div>
          <div class="w-full h-1.5 bg-slate-200 rounded-full mt-1 overflow-hidden">
            <div class="h-full rounded-full transition-all" style="width:${{Math.min(100, actualPct/target*100)}}%; background: ${{met?'linear-gradient(90deg,#16a34a,#22c55e)':'linear-gradient(90deg,#dc2626,#ef4444)'}}"></div>
          </div>
          <div class="text-xs mt-0.5 text-right ${{met?'text-green-600':'text-red-500'}}">${{met?'✓ 达标':'✗ 未达标'}}</div>
        </div>
      `;
    }}).join('')}}
  `;
  // 绑定目标输入事件
  container.querySelectorAll('.target-input').forEach(inp => {{
    inp.onchange = () => {{
      let t = {{}};
      try {{ t = JSON.parse(localStorage.getItem('funnelTargets') || '{{}}'); }} catch(e) {{}}
      t[inp.dataset.key] = parseFloat(inp.value) || 0;
      localStorage.setItem('funnelTargets', JSON.stringify(t));
      renderDailyFunnelChart();
    }};
  }});
}}

// 抖音运营数据分析总结
function renderDailyAnalysis() {{
  const date = document.getElementById('dailyDateSelect').value;
  const row = DAILY.find(r => r.date === date);
  const label = document.getElementById('dailyAnalysisDate');
  const content = document.getElementById('dailyAnalysisContent');
  if (!row) {{ label.textContent = ''; content.innerHTML = '<div class="text-slate-400 text-center py-4">暂无数据</div>'; return; }}
  label.textContent = date;

  const fmt = n => n ? n.toLocaleString('zh-CN', {{maximumFractionDigits:0}}) : '-';
  const pct = n => n ? (n*100).toFixed(1) + '%' : '-';

  // 经营概况
  const gmv = row.totalGmv || 0;
  const spend = row.adSpend || 0;
  const roi = row.overallRoi || 0;
  const views = row.views || 0;
  const orders = row.orders || 0;
  const fans = row.newFans || 0;
  const refundRate = row.refundRate || 0;

  // 流量转化
  const exp = row.exposureCount || 0;
  const watch = row.watchCount || 0;
  const prodExp = row.productExposureCount || 0;
  const prodClick = row.productClickCount || 0;
  const buyers = row.buyerCount || 0;
  const exp2watch = row.exposureToWatchRate || 0;
  const watch2prod = row.watchToProductRate || 0;
  const prod2click = row.productClickRate || 0;
  const click2buy = row.clickToBuyRate || 0;

  // 主播数据
  const anchors = ANCHOR.filter(r => r.date === date);
  const topAnchor = anchors.sort((a,b) => (b.gmv||0)-(a.gmv||0))[0];

  // 智能分析
  let roiLevel = roi >= 2.5 ? '优秀' : roi >= 2.0 ? '良好' : roi >= 1.5 ? '一般' : '偏低';
  let expLevel = exp2watch >= 0.15 ? '优秀' : exp2watch >= 0.12 ? '良好' : exp2watch >= 0.10 ? '一般' : '偏低';
  let clickLevel = prod2click >= 0.25 ? '优秀' : prod2click >= 0.20 ? '良好' : prod2click >= 0.15 ? '一般' : '偏低';
  let buyLevel = click2buy >= 0.15 ? '优秀' : click2buy >= 0.12 ? '良好' : click2buy >= 0.10 ? '一般' : '偏低';

  let html = '';

  // 经营概况
  html += `<div class="p-3 rounded-lg" style="background: rgba(0,48,135,0.05); border-left: 3px solid #003087;">
    <div class="font-semibold mb-1" style="color: #003087;">📊 当日经营概况</div>
    <div>当日GMV <b style="color:#003087;">¥${{fmt(gmv)}}</b>，投放消耗 <b style="color:#c8102e;">¥${{fmt(spend)}}</b>，整体ROI <b>${{roi.toFixed(2)}}</b>（${{roiLevel}}）。场观 ${{fmt(views)}} 人，成交 ${{fmt(orders)}} 单，客单价 ¥${{(row.avgOrderValue||0).toFixed(0)}}，新增粉丝 ${{fmt(fans)}} 人，退款率 ${{pct(refundRate)}}。</div>
  </div>`;

  // 流量转化
  html += `<div class="p-3 rounded-lg" style="background: rgba(200,16,46,0.05); border-left: 3px solid #c8102e;">
    <div class="font-semibold mb-1" style="color: #c8102e;">🔄 流量转化分析</div>
    <div>曝光 ${{fmt(exp)}} → 观看 ${{fmt(watch)}}（转化率 ${{pct(exp2watch)}}，${{expLevel}}）→ 商品曝光 ${{fmt(prodExp)}}（${{pct(watch2prod)}}）→ 商品点击 ${{fmt(prodClick)}}（${{pct(prod2click)}}，${{clickLevel}}）→ 成交 ${{fmt(buyers)}} 人（${{pct(click2buy)}}，${{buyLevel}}）。整体曝光-成交转化率 ${{(exp>0?(buyers/exp*100).toFixed(2):0)}}%。</div>
  </div>`;

  // 主播表现
  if (topAnchor) {{
    const totalAnchorGmv = anchors.reduce((s,a) => s+(a.gmv||0), 0);
    const topShare = totalAnchorGmv > 0 ? (topAnchor.gmv/totalAnchorGmv*100).toFixed(0) : 0;
    html += `<div class="p-3 rounded-lg" style="background: rgba(212,165,116,0.08); border-left: 3px solid #d4a574;">
      <div class="font-semibold mb-1" style="color: #92400e;">👥 主播表现</div>
      <div>当日共 ${{anchors.length}} 位主播开播，GMV最高为 <b>${{topAnchor.anchor}}</b>（¥${{fmt(topAnchor.gmv)}}，占比 ${{topShare}}%），ROI ${{(topAnchor.overallRoi||0).toFixed(2)}}，小时均GMV ¥${{fmt(topAnchor.hourlyGmv||0)}}。${{anchors.length >= 3 ? '主播梯队分布合理，建议保持头部主播优势的同时培养中腰部主播。' : '开播主播较少，建议增加主播排班提升全天覆盖。'}}</div>
    </div>`;
  }}

  // 运营建议
  let suggestions = [];
  if (roi < 2.0) suggestions.push('ROI偏低，建议优化投放人群定向和出价策略，降低无效消耗');
  if (exp2watch < 0.12) suggestions.push('曝光-观看转化率偏低，建议优化直播间封面、标题和开场话术提升进入率');
  if (prod2click < 0.20) suggestions.push('商品曝光-点击率偏低，建议优化商品卡主图、价格展示和讲解节奏');
  if (click2buy < 0.12) suggestions.push('点击-成交转化率偏低，建议加强逼单话术、限时优惠和信任背书');
  if (refundRate > 0.10) suggestions.push('退款率偏高，建议关注商品质量和发货时效，降低售后纠纷');
  if (fans < 50) suggestions.push('新增粉丝较少，建议增加关注引导话术和粉丝专属福利');
  if (suggestions.length === 0) suggestions.push('各项指标表现良好，建议保持当前运营节奏，持续优化细节');

  html += `<div class="p-3 rounded-lg" style="background: rgba(16,185,129,0.05); border-left: 3px solid #10b981;">
    <div class="font-semibold mb-1" style="color: #047857;">💡 运营建议</div>
    <ul class="list-disc list-inside space-y-1">
      ${{suggestions.map(s => `<li>${{s}}</li>`).join('')}}
    </ul>
  </div>`;

  content.innerHTML = html;
}}

// 当日主播排名
function renderDailyAnchorRank() {{
  const date = document.getElementById('dailyDateSelect').value;
  const data = ANCHOR.filter(r=>r.date === date);
  const rank = getAnchorRank(data);
  renderRankList('dailyAnchorRankList', rank, 'dailyAnchorLabel', date + '（' + data.length + '场）');
}}

// 今日排班明细（基于真实当前日期）
function renderTodaySchedule() {{
  const dateLabel = document.getElementById('todayScheduleDate');
  const content = document.getElementById('todayScheduleContent');

  // 真实今天
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const today = `${{y}}-${{m}}-${{day}}`;
  const weekDays = ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'];
  const weekDay = weekDays[now.getDay()];
  dateLabel.textContent = today + ' ' + weekDay;

  const schedule = SCHEDULE[today];
  if (!schedule || !schedule.slots || schedule.slots.length === 0) {{
    content.innerHTML = '<div class="text-center text-slate-400 py-6 text-sm">暂无今日排班数据</div>';
    return;
  }}

  let html = '<div class="space-y-2">';
  schedule.slots.forEach((slot, i) => {{
    const colors = ['#c8102e', '#d4a574', '#e67e22', '#f39c12', '#e74c3c'];
    const color = colors[i % colors.length];
    html += `
      <div class="flex items-center gap-3 p-3 rounded-lg" style="background: rgba(200,16,46,0.05); border-left: 3px solid ${{color}};">
        <div class="flex-shrink-0 w-24 text-sm font-semibold" style="color: ${{color}};">${{slot.time}}</div>
        <div class="flex-1">
          <span class="text-base font-bold text-slate-700">${{slot.anchor}}</span>
        </div>
        <div class="flex-shrink-0 text-sm text-slate-500">
          <span class="font-semibold" style="color: ${{color}};">${{slot.duration}}</span> 小时
        </div>
      </div>
    `;
  }});
  html += '</div>';

  if (schedule.rest) {{
    html += `
      <div class="mt-3 pt-3 border-t border-slate-200 flex items-center gap-2">
        <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <span class="text-sm text-slate-500">休息主播：</span>
        <span class="text-sm font-semibold text-amber-600">${{schedule.rest}}</span>
      </div>
    `;
  }}

  const totalHours = schedule.slots.reduce((s, slot) => s + (slot.duration || 0), 0);
  html += `
    <div class="mt-3 pt-3 border-t border-slate-200 flex justify-between items-center">
      <span class="text-xs text-slate-400">共 ${{schedule.slots.length}} 个时段</span>
      <span class="text-sm font-semibold" style="color: #c8102e;">总直播时长：${{totalHours.toFixed(1)}} 小时</span>
    </div>
  `;

  content.innerHTML = html;
}}

// 明日主播排版（基于真实当前日期）
function renderTomorrowSchedule() {{
  const dateLabel = document.getElementById('tomorrowScheduleDate');
  const content = document.getElementById('tomorrowScheduleContent');

  // 真实明天
  const now = new Date();
  now.setDate(now.getDate() + 1);
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const tomorrow = `${{y}}-${{m}}-${{day}}`;
  const weekDays = ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'];
  const weekDay = weekDays[now.getDay()];
  dateLabel.textContent = tomorrow + ' ' + weekDay;

  const schedule = SCHEDULE[tomorrow];
  if (!schedule || !schedule.slots || schedule.slots.length === 0) {{
    content.innerHTML = '<div class="text-center text-slate-400 py-6 text-sm">暂无明日排版数据</div>';
    return;
  }}

  let html = '<div class="space-y-2">';
  schedule.slots.forEach((slot, i) => {{
    const colors = ['#003087', '#003da5', '#2563eb', '#3b82f6', '#60a5fa'];
    const color = colors[i % colors.length];
    html += `
      <div class="flex items-center gap-3 p-3 rounded-lg" style="background: rgba(0,48,135,0.05); border-left: 3px solid ${{color}};">
        <div class="flex-shrink-0 w-24 text-sm font-semibold" style="color: ${{color}};">${{slot.time}}</div>
        <div class="flex-1">
          <span class="text-base font-bold text-slate-700">${{slot.anchor}}</span>
        </div>
        <div class="flex-shrink-0 text-sm text-slate-500">
          <span class="font-semibold" style="color: ${{color}};">${{slot.duration}}</span> 小时
        </div>
      </div>
    `;
  }});
  html += '</div>';

  if (schedule.rest) {{
    html += `
      <div class="mt-3 pt-3 border-t border-slate-200 flex items-center gap-2">
        <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <span class="text-sm text-slate-500">休息主播：</span>
        <span class="text-sm font-semibold text-amber-600">${{schedule.rest}}</span>
      </div>
    `;
  }}

  const totalHours = schedule.slots.reduce((s, slot) => s + (slot.duration || 0), 0);
  html += `
    <div class="mt-3 pt-3 border-t border-slate-200 flex justify-between items-center">
      <span class="text-xs text-slate-400">共 ${{schedule.slots.length}} 个时段</span>
      <span class="text-sm font-semibold" style="color: #003087;">总直播时长：${{totalHours.toFixed(1)}} 小时</span>
    </div>
  `;

  content.innerHTML = html;
}}

// 当日核心数据KPI
function renderDailyKpiCards() {{
  const select = document.getElementById('dailyDateSelect');
  const date = select.value;
  const row = DAILY.find(r => r.date === date);
  const container = document.getElementById('dailyKpiCards');
  document.getElementById('dailyKpiLabel').textContent = date || '';

  if (!row) {{
    container.innerHTML = '<div class="col-span-full text-center text-slate-400 py-8 text-sm">该日期暂无数据</div>';
    return;
  }}

  const kpis = [
    {{ label:'总GMV', value: fmt.money(row.totalGmv), sub:'加优惠券', color:'#003087' }},
    {{ label:'GMV', value: fmt.money(row.gmv), sub:'不含优惠券', color:'#003da5' }},
    {{ label:'投放消耗', value: fmt.money(row.adSpend), sub:'千川消耗', color:'#c8102e' }},
    {{ label:'整体ROI', value: row.overallRoi!==null?row.overallRoi.toFixed(2):'-', sub:'投产比', color:'#16a34a' }},
    {{ label:'直播时长', value: row.duration?row.duration+'h':'-', sub:'小时', color:'#5a6c7d' }},
    {{ label:'小时均GMV', value: fmt.money(row.hourlyGmv), sub:'每小时产出', color:'#003087' }},
    {{ label:'场观', value: row.views?row.views.toLocaleString():'-', sub:'观看人数', color:'#7c3aed' }},
    {{ label:'成交件数', value: row.orders?row.orders.toLocaleString():'-', sub:'订单量', color:'#c8102e' }},
    {{ label:'客单价', value: row.avgOrderValue?'¥'+row.avgOrderValue.toFixed(2):'-', sub:'件均金额', color:'#003da5' }},
    {{ label:'新增粉丝', value: row.newFans?row.newFans.toLocaleString():'-', sub:'涨粉数', color:'#16a34a' }},
    {{ label:'互动人数', value: row.interactionUsers?row.interactionUsers.toLocaleString():'-', sub:'参与互动', color:'#d4a574' }},
    {{ label:'退款率', value: row.refundRate!==null?(row.refundRate*100).toFixed(2)+'%':'-', sub:'退款占比', color:'#dc2626' }}
  ];

  container.innerHTML = kpis.map(k => `
    <div class="kpi-card rounded-xl p-4">
      <div class="kpi-label text-slate-500 mb-1.5">${{k.label}}</div>
      <div class="kpi-value" style="color:${{k.color}}">${{k.value}}</div>
      <div class="kpi-sub text-slate-400 mt-1">${{k.sub}}</div>
    </div>
  `).join('');
}}

// ==================== 渲染入口 ====================
let currentSubTab = 'daily'; // 'daily' | 'range'

function switchSubTab(tab) {{
  currentSubTab = tab;
  document.getElementById('subTabDailyBtn').className = tab==='daily'
    ? 'sub-tab-active px-5 py-2 rounded-lg text-sm font-medium transition-all'
    : 'sub-tab-inactive px-5 py-2 rounded-lg text-sm font-medium transition-all';
  document.getElementById('subTabRangeBtn').className = tab==='range'
    ? 'sub-tab-active px-5 py-2 rounded-lg text-sm font-medium transition-all'
    : 'sub-tab-inactive px-5 py-2 rounded-lg text-sm font-medium transition-all';
  document.getElementById('dailyPanel').classList.toggle('hidden', tab !== 'daily');
  document.getElementById('rangePanel').classList.toggle('hidden', tab !== 'range');
  renderAll();
}}

// 数据分析框
function renderAnalysis(data) {{
  const label = document.getElementById('analysisLabel');
  const content = document.getElementById('analysisContent');
  if (!data || !data.length) {{
    label.textContent = '';
    content.innerHTML = '<div class="text-slate-400 text-center py-4">所选区间暂无数据</div>';
    return;
  }}
  const start = data[0].date, end = data[data.length-1].date;
  const days = data.length;
  label.textContent = start + ' ~ ' + end + '（' + days + '天）';

  const totalGmv = data.reduce((s,r)=>s+(r.totalGmv||0),0);
  const avgGmv = totalGmv/days;
  const maxGmvRow = data.reduce((a,b)=>(a.totalGmv||0)>(b.totalGmv||0)?a:b);
  const totalSpend = data.reduce((s,r)=>s+(r.adSpend||0),0);
  const avgRoi = totalSpend>0? totalGmv/totalSpend : 0;
  const totalOrders = data.reduce((s,r)=>s+(r.orders||0),0);
  const avgViews = data.reduce((s,r)=>s+(r.views||0),0)/days;
  const totalRefund = data.reduce((s,r)=>s+(r.refundAmount||0),0);
  const refundRate = totalGmv>0? totalRefund/totalGmv : 0;

  // 转化率
  const totalExp = data.reduce((s,r)=>s+(r.exposureCount||0),0);
  const totalWatch = data.reduce((s,r)=>s+(r.watchCount||0),0);
  const totalProdExp = data.reduce((s,r)=>s+(r.productExposureCount||0),0);
  const totalClick = data.reduce((s,r)=>s+(r.productClickCount||0),0);
  const totalBuyer = data.reduce((s,r)=>s+(r.buyerCount||0),0);
  const exp2watch = totalExp? totalWatch/totalExp : 0;
  const click2buy = totalClick? totalBuyer/totalClick : 0;

  // 趋势判断
  const half = Math.floor(days/2);
  const firstHalf = data.slice(0, half).reduce((s,r)=>s+(r.totalGmv||0),0);
  const secondHalf = data.slice(half).reduce((s,r)=>s+(r.totalGmv||0),0);
  const trend = secondHalf > firstHalf*1.05 ? '上升' : secondHalf < firstHalf*0.95 ? '下降' : '平稳';

  const html = `
    <p><span class="font-semibold" style="color:#003087">【经营概况】</span>统计区间共 ${{days}} 天，总GMV <span class="font-bold" style="color:#003087">¥${{totalGmv.toLocaleString()}}</span>，日均 <span class="font-bold">¥${{avgGmv.toFixed(0)}}</span>；单日最高 ${{maxGmvRow.date}} 达 ¥${{(maxGmvRow.totalGmv||0).toLocaleString()}}。总投放消耗 ¥${{totalSpend.toLocaleString()}}，整体ROI <span class="font-bold" style="color:${{avgRoi>=2?'#16a34a':'#c8102e'}}">${{avgRoi.toFixed(2)}}</span>。</p>
    <p><span class="font-semibold" style="color:#003087">【流量转化】</span>累计曝光 ${{totalExp.toLocaleString()}} 人，观看 ${{totalWatch.toLocaleString()}} 人，曝光-观看率 <span class="font-bold">${{(exp2watch*100).toFixed(2)}}%</span>；商品点击 ${{totalClick.toLocaleString()}} 人，点击-成交转化率 <span class="font-bold">${{(click2buy*100).toFixed(2)}}%</span>；累计成交 ${{totalBuyer.toLocaleString()}} 人、${{totalOrders}} 件。</p>
    <p><span class="font-semibold" style="color:#003087">【趋势研判】</span>区间后半段GMV较前半段呈<span class="font-bold" style="color:${{trend==='上升'?'#16a34a':trend==='下降'?'#c8102e':'#d4a574'}}">${{trend}}</span>态势。场均场观 ${{avgViews.toFixed(0)}} 人，退款率 <span class="font-bold" style="color:${{refundRate<=0.05?'#16a34a':'#c8102e'}}">${{(refundRate*100).toFixed(2)}}%</span>${{refundRate>0.05?'，建议关注退款原因。':'，控制良好。'}}</p>
    <p><span class="font-semibold" style="color:#003087">【运营建议】</span>${{avgRoi<2?'当前整体ROI低于2，建议优化投放人群和素材，提升投产比。':'整体ROI表现良好，可考虑适度加大投放预算。'}} ${{exp2watch<0.15?'曝光-观看率偏低，建议优化直播间封面和标题提升吸引力。':'曝光-观看率达标。'}} ${{click2buy<0.15?'点击-成交转化率有提升空间，建议优化商品讲解和促单话术。':'点击-成交转化表现优秀。'}}</p>
  `;
  content.innerHTML = html;
}}

function renderAll() {{
  const d1 = getFiltered(1);
  const d2 = getFiltered(2);
  if (currentTab === 1) {{
    if (currentSubTab === 'daily') {{
      // 日报表
      renderMonthlyBizCards();
      renderDailyKpiCards();
      renderDailyFunnelChart();
      renderDailyAnchorRank();
      renderTodaySchedule();
      renderTomorrowSchedule();
      renderDailyAnalysis();
    }} else {{
      // 区间报表
      renderKPI1(d1);
      renderFunnelChart(d1);
      renderBarChart(d1);
      renderGmvChart(d1);
      renderRoiChart(d1);
      renderGmvRoiRangeChart(d1);
      renderClickRoiRangeChart(d1);
      renderGmvConvRangeChart(d1);
      renderViewsRoiRangeChart(d1);
      renderTable(1);
      renderAnalysis(d1);
    }}
  }} else {{
    renderMonthRank();
    renderWeekRank();
    renderDayRank();
    renderTable(2);
  }}
}}

// ==================== 事件绑定 ====================
document.getElementById('tab1Btn').onclick = () => switchTab(1);
document.getElementById('tab2Btn').onclick = () => switchTab(2);
document.getElementById('subTabDailyBtn').onclick = () => switchSubTab('daily');
document.getElementById('subTabRangeBtn').onclick = () => switchSubTab('range');
document.getElementById('dateStart').onchange = e => {{ dateStart = e.target.value; renderAll(); }};
document.getElementById('dateEnd').onchange = e => {{ dateEnd = e.target.value; renderAll(); }};
document.getElementById('resetDate').onclick = () => {{ initDateFilters(); document.getElementById('quickRangeLabel').textContent=''; renderAll(); }};
function applyQuickRange(start, end, label) {{
  dateStart = start; dateEnd = end;
  document.getElementById('dateStart').value = start;
  document.getElementById('dateEnd').value = end;
  document.getElementById('quickRangeLabel').textContent = label;
  renderAll();
}}
document.getElementById('quickWeek').onclick = () => {{
  const now = new Date();
  const day = now.getDay() || 7;
  const monday = new Date(now); monday.setDate(now.getDate() - day + 1);
  const sunday = new Date(monday); sunday.setDate(monday.getDate() + 6);
  const fmt = d => `${{d.getFullYear()}}-${{String(d.getMonth()+1).padStart(2,'0')}}-${{String(d.getDate()).padStart(2,'0')}}`;
  applyQuickRange(fmt(monday), fmt(sunday), `${{fmt(monday).slice(5)}} ~ ${{fmt(sunday).slice(5)}}`);
}};
document.getElementById('quickMonth').onclick = () => {{
  const now = new Date();
  const y = now.getFullYear(), m = now.getMonth();
  const first = `${{y}}-${{String(m+1).padStart(2,'0')}}-01`;
  const lastDay = new Date(y, m+1, 0).getDate();
  const last = `${{y}}-${{String(m+1).padStart(2,'0')}}-${{String(lastDay).padStart(2,'0')}}`;
  applyQuickRange(first, last, `${{y}}年${{m+1}}月`);
}};
document.getElementById('quickQuarter').onclick = () => {{
  const now = new Date();
  const y = now.getFullYear(), q = Math.floor(now.getMonth()/3);
  const startMonth = q*3, endMonth = q*3+2;
  const first = `${{y}}-${{String(startMonth+1).padStart(2,'0')}}-01`;
  const lastDay = new Date(y, endMonth+1, 0).getDate();
  const last = `${{y}}-${{String(endMonth+1).padStart(2,'0')}}-${{String(lastDay).padStart(2,'0')}}`;
  applyQuickRange(first, last, `${{y}}年Q${{q+1}}`);
}};
document.getElementById('search1').oninput = e => {{ tableState[1].search = e.target.value; tableState[1].page=1; renderTable(1); }};
document.getElementById('search2').oninput = e => {{ tableState[2].search = e.target.value; tableState[2].page=1; renderTable(2); }};
document.getElementById('dailyDateSelect').onchange = () => {{ renderMonthlyBizCards(); renderDailyKpiCards(); renderDailyFunnelChart(); renderDailyAnchorRank(); renderDailyAnalysis(); }};

// 刷新数据功能 - 调用本地服务从飞书拉取数据并上传云端
const LOCAL_API = 'http://127.0.0.1:8888';
let refreshPolling = false;

async function checkUpdateStatus() {{
  try {{
    const resp = await fetch(LOCAL_API + '/api/status', {{ cache: 'no-store' }});
    const data = await resp.json();
    return data;
  }} catch(e) {{
    return null;
  }}
}}

async function pollUpdateStatus() {{
  if (!refreshPolling) return;
  const status = await checkUpdateStatus();
  const text = document.getElementById('refreshText');
  
  if (!status) {{
    // 本地服务未启动
    refreshPolling = false;
    document.getElementById('refreshBtn').disabled = false;
    document.getElementById('refreshIcon').classList.remove('animate-spin');
    text.textContent = '刷新数据';
    showToast('本地更新服务未启动，请先运行 start_server.bat', 'error');
    return;
  }}
  
  if (status.running) {{
    // 还在更新中，显示最新日志
    const logs = status.log || [];
    if (logs.length > 0) {{
      const lastLog = logs[logs.length - 1];
      text.textContent = '更新中...' + (lastLog.length > 15 ? lastLog.substring(0, 15) + '...' : lastLog);
    }}
    setTimeout(pollUpdateStatus, 2000);
  }} else {{
    // 更新完成
    refreshPolling = false;
    document.getElementById('refreshBtn').disabled = false;
    document.getElementById('refreshIcon').classList.remove('animate-spin');
    text.textContent = '刷新数据';
    
    if (status.last_result === 'success') {{
      showToast('数据更新成功！正在刷新页面...', 'success');
      setTimeout(() => {{ location.reload(true); }}, 1500);
    }} else {{
      showToast('数据更新失败，请检查本地服务日志', 'error');
    }}
  }}
}}

document.getElementById('refreshBtn').onclick = async () => {{
  const btn = document.getElementById('refreshBtn');
  const icon = document.getElementById('refreshIcon');
  const text = document.getElementById('refreshText');
  
  if (refreshPolling) return;
  
  btn.disabled = true;
  icon.classList.add('animate-spin');
  text.textContent = '连接服务...';
  
  try {{
    // 先检查本地服务是否可用
    const statusCheck = await checkUpdateStatus();
    if (!statusCheck) {{
      throw new Error('本地服务未启动');
    }}
    
    // 触发更新
    const resp = await fetch(LOCAL_API + '/api/update', {{ 
      method: 'POST',
      cache: 'no-store'
    }});
    const data = await resp.json();
    
    if (data.status === 'started' || data.status === 'running') {{
      refreshPolling = true;
      text.textContent = '从飞书拉取数据...';
      setTimeout(pollUpdateStatus, 2000);
    }} else {{
      throw new Error(data.message || '触发更新失败');
    }}
  }} catch(e) {{
    btn.disabled = false;
    icon.classList.remove('animate-spin');
    text.textContent = '刷新数据';
    showToast('本地更新服务未启动！请先双击运行 start_server.bat，然后再点击刷新', 'error');
  }}
}};

// 一键截图功能
document.getElementById('screenshotBtn').onclick = async () => {{
  const btn = document.getElementById('screenshotBtn');
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> 生成中...';
  try {{
    const target = document.getElementById('dailyPanel');
    // 临时禁用Tailwind注入的style标签（含oklch，html2canvas不支持）
    const twStyles = [];
    document.querySelectorAll('style').forEach(s => {{
      if (s.textContent && s.textContent.includes('oklch')) {{
        s.disabled = true;
        twStyles.push(s);
      }}
    }});
    await new Promise(r => setTimeout(r, 50));

    const canvas = await html2canvas(target, {{
      scale: 2,
      useCORS: true,
      backgroundColor: '#f5efe6',
      logging: false,
      onclone: (clonedDoc) => {{
        clonedDoc.body.style.background = '#f5efe6';
        clonedDoc.querySelectorAll('.glass-card').forEach(el => {{
          el.style.background = '#ffffff';
          el.style.backdropFilter = 'none';
          el.style.webkitBackdropFilter = 'none';
        }});
        // 修复input值不显示问题：将所有input替换为显示value的span
        clonedDoc.querySelectorAll('input').forEach(input => {{
          const span = clonedDoc.createElement('span');
          span.textContent = input.value || '';
          span.style.cssText = input.style.cssText;
          span.style.display = 'inline-block';
          span.style.minWidth = input.offsetWidth ? input.offsetWidth + 'px' : '40px';
          span.style.padding = '2px 6px';
          span.style.border = '1px solid #e2e8f0';
          span.style.borderRadius = '4px';
          span.style.background = '#fff';
          span.style.fontSize = '12px';
          span.style.color = '#334155';
          span.style.textAlign = 'center';
          if (input.className) span.className = input.className;
          input.parentNode.replaceChild(span, input);
        }});
      }}
    }});

    // 恢复Tailwind style
    twStyles.forEach(s => s.disabled = false);

    const date = document.getElementById('dailyDateSelect').value || '日报表';

    // 1. 下载图片
    const link = document.createElement('a');
    link.download = `桂格直播间日报表_${{date}}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();

    // 2. 复制到剪贴板（支持直接粘贴）
    try {{
      canvas.toBlob(async (blob) => {{
        if (blob && navigator.clipboard && window.ClipboardItem) {{
          await navigator.clipboard.write([
            new ClipboardItem({{ 'image/png': blob }})
          ]);
          // 显示复制成功提示
          showToast('截图已复制到剪贴板，可直接粘贴');
        }} else {{
          showToast('截图已下载，当前浏览器不支持自动复制');
        }}
      }}, 'image/png');
    }} catch(err) {{
      console.warn('复制到剪贴板失败:', err);
    }}
  }} catch(e) {{
    document.querySelectorAll('style').forEach(s => {{ if(s.textContent && s.textContent.includes('oklch')) s.disabled = false; }});
    alert('截图失败：' + e.message);
  }} finally {{
    btn.disabled = false;
    btn.innerHTML = originalText;
  }}
}};

// Toast提示
function showToast(msg, type) {{
  const existing = document.getElementById('toastMsg');
  if (existing) existing.remove();
  const isError = type === 'error';
  const bgColor = isError ? 'linear-gradient(135deg,#dc2626,#ef4444)' : 'linear-gradient(135deg,#16a34a,#22c55e)';
  const icon = isError 
    ? '<svg style="display:inline-block;width:16px;height:16px;margin-right:6px;vertical-align:middle;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>'
    : '<svg style="display:inline-block;width:16px;height:16px;margin-right:6px;vertical-align:middle;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>';
  const toast = document.createElement('div');
  toast.id = 'toastMsg';
  toast.style.cssText = 'position:fixed;top:80px;left:50%;transform:translateX(-50%);background:' + bgColor + ';color:white;padding:12px 24px;border-radius:8px;font-size:14px;font-weight:500;z-index:99999;box-shadow:0 4px 12px rgba(0,0,0,0.15);animation:toastIn 0.3s ease;max-width:90%;text-align:center;';
  toast.innerHTML = icon + msg;
  document.body.appendChild(toast);
  setTimeout(() => {{ toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }}, 3500);
}}

document.getElementById('yesterdayBtn').onclick = () => {{
  const today = new Date();
  const yesterday = new Date(today.getTime() - 86400000);
  const yStr = yesterday.toISOString().slice(0,10);
  const select = document.getElementById('dailyDateSelect');
  const exists = [...select.options].some(o => o.value === yStr);
  if (exists) {{ select.value = yStr; }} else {{
    const dates = [...select.options].map(o => o.value).filter(d => d <= yStr).sort();
    if (dates.length) select.value = dates[dates.length-1];
  }}
  select.onchange();
}};
window.addEventListener('resize', () => Object.values(charts).forEach(c=>c.resize()));

// ==================== 管理模式检测 ====================
// 刷新按钮仅在管理模式下显示（URL带 ?admin=1 或 localStorage已设置）
function checkAdminMode() {{
  const urlParams = new URLSearchParams(window.location.search);
  const urlAdmin = urlParams.get('admin');
  const storedAdmin = localStorage.getItem('guaker_admin_mode');
  
  let isAdmin = false;
  if (urlAdmin === '1' || urlAdmin === 'true') {{
    isAdmin = true;
    localStorage.setItem('guaker_admin_mode', '1');
    // 清理URL参数，避免分享时泄露
    window.history.replaceState({{}}, document.title, window.location.pathname);
  }} else if (storedAdmin === '1') {{
    isAdmin = true;
  }}
  
  if (isAdmin) {{
    document.getElementById('refreshBtn').style.display = 'flex';
  }}
}}

// 双击标题切换管理模式（隐藏入口，仅管理员知道）
let titleClickCount = 0;
let titleClickTimer = null;
document.querySelector('header h1')?.addEventListener('click', () => {{
  titleClickCount++;
  clearTimeout(titleClickTimer);
  titleClickTimer = setTimeout(() => {{ titleClickCount = 0; }}, 1000);
  if (titleClickCount >= 3) {{
    titleClickCount = 0;
    const current = localStorage.getItem('guaker_admin_mode');
    if (current === '1') {{
      localStorage.removeItem('guaker_admin_mode');
      document.getElementById('refreshBtn').style.display = 'none';
      showToast('已退出管理模式', 'success');
    }} else {{
      localStorage.setItem('guaker_admin_mode', '1');
      document.getElementById('refreshBtn').style.display = 'flex';
      showToast('已进入管理模式，刷新按钮已显示', 'success');
    }}
  }}
}});

checkAdminMode();

// ==================== 初始化 ====================
initDateFilters();
initDailyDateSelect();
renderAll();
</script>
</body>
</html>'''

with open('直播间运营数据分析看板.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML已生成，大小: {len(html)} 字节")
print("文件: 直播间运营数据分析看板.html")
