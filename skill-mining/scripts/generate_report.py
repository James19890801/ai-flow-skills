"""
generate_report.py - 生成 Skill 挖掘 HTML 可视化报告
用法: python generate_report.py <报告JSON文件路径>
JSON格式见下方 EXAMPLE_DATA
"""

import sys
import json
import os
from datetime import datetime

EXAMPLE_DATA = {
    "process_name": "示例采购审批流程",
    "total_nodes": 8,
    "nodes": [
        {
            "id": 1,
            "name": "需求收集与汇总",
            "description": "各部门提交采购需求，汇总到表格",
            "skill_score": 88,
            "priority": "high",
            "reasons": ["重复度极高", "有明确输入输出", "AI可自动汇总分类"],
            "skill_idea": "需求汇总 Skill：自动聚合多部门需求邮件，结构化输出采购清单",
            "difficulty": "低",
            "status": "立即可做"
        },
        {
            "id": 2,
            "name": "供应商资质审核",
            "description": "人工核查供应商资质文件",
            "skill_score": 75,
            "priority": "high",
            "reasons": ["耗时长", "规则明确", "AI可辅助比对关键指标"],
            "skill_idea": "资质审核 Skill：上传供应商文件，AI自动提取关键资质并对照标准输出审核意见",
            "difficulty": "中",
            "status": "立即可做"
        },
        {
            "id": 3,
            "name": "价格比对分析",
            "description": "对比多家供应商报价，形成比价表",
            "skill_score": 92,
            "priority": "high",
            "reasons": ["高重复", "数据驱动", "AI擅长结构化对比"],
            "skill_idea": "比价分析 Skill：输入多份报价单，自动生成对比矩阵并推荐最优选择",
            "difficulty": "低",
            "status": "立即可做"
        },
        {
            "id": 4,
            "name": "合同起草",
            "description": "基于模板起草采购合同",
            "skill_score": 70,
            "priority": "medium",
            "reasons": ["有模板可依", "需要定制化", "AI可生成初稿"],
            "skill_idea": "合同起草 Skill：输入关键条款信息，自动生成标准合同初稿",
            "difficulty": "中",
            "status": "需更多信息"
        },
        {
            "id": 5,
            "name": "多级审批流转",
            "description": "逐级提交审批，等待各级签字",
            "skill_score": 30,
            "priority": "low",
            "reasons": ["依赖人工决策", "线下签字环节无法替代"],
            "skill_idea": "审批提醒 Skill：自动推送审批通知，催办超期节点",
            "difficulty": "高",
            "status": "需系统集成"
        }
    ]
}


def get_priority_color(priority):
    return {"high": "#10b981", "medium": "#f59e0b", "low": "#6b7280"}.get(priority, "#6b7280")

def get_status_badge(status):
    colors = {
        "立即可做": ("bg-green-100 text-green-800", "✅"),
        "需更多信息": ("bg-yellow-100 text-yellow-800", "⚡"),
        "需系统集成": ("bg-blue-100 text-blue-800", "🔧"),
        "复杂需拆分": ("bg-red-100 text-red-800", "⚠️"),
    }
    cls, icon = colors.get(status, ("bg-gray-100 text-gray-800", "❓"))
    return f'<span class="px-2 py-1 rounded-full text-xs font-medium {cls}">{icon} {status}</span>'

def score_bar(score):
    color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
    return f'''
        <div class="flex items-center gap-2">
            <div class="flex-1 bg-gray-100 rounded-full h-2">
                <div class="h-2 rounded-full transition-all" style="width:{score}%;background:{color}"></div>
            </div>
            <span class="text-sm font-bold" style="color:{color}">{score}</span>
        </div>'''

def generate_html(data):
    nodes = data.get("nodes", [])
    process_name = data.get("process_name", "未命名流程")
    total_nodes = data.get("total_nodes", len(nodes))
    high_count = sum(1 for n in nodes if n.get("priority") == "high")
    medium_count = sum(1 for n in nodes if n.get("priority") == "medium")
    top3 = sorted(nodes, key=lambda x: x.get("skill_score", 0), reverse=True)[:3]
    now = datetime.now().strftime("%Y年%m月%d日 %H:%M")

    nodes_html = ""
    for node in nodes:
        reasons_html = "".join(f'<span class="inline-block bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded mr-1 mb-1">{r}</span>' for r in node.get("reasons", []))
        nodes_html += f'''
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start mb-3">
                <div class="flex items-center gap-3">
                    <span class="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-sm font-bold">{node.get("id","")}</span>
                    <div>
                        <h3 class="font-semibold text-gray-900">{node.get("name","")}</h3>
                        <p class="text-xs text-gray-500 mt-0.5">{node.get("description","")}</p>
                    </div>
                </div>
                {get_status_badge(node.get("status",""))}
            </div>
            <div class="mb-3">{score_bar(node.get("skill_score", 0))}</div>
            <div class="mb-3">{reasons_html}</div>
            <div class="bg-indigo-50 rounded-xl p-3">
                <p class="text-xs text-indigo-500 font-medium mb-1">💡 Skill 构想</p>
                <p class="text-sm text-indigo-800">{node.get("skill_idea","")}</p>
            </div>
            <div class="mt-2 flex justify-between text-xs text-gray-400">
                <span>实现难度：{node.get("difficulty","")}</span>
            </div>
        </div>'''

    top3_html = ""
    medals = ["🥇", "🥈", "🥉"]
    for i, node in enumerate(top3):
        top3_html += f'''
        <div class="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100">
            <span class="text-2xl">{medals[i]}</span>
            <div class="flex-1">
                <p class="font-semibold text-gray-900 text-sm">{node.get("name","")}</p>
                <p class="text-xs text-gray-500">{node.get("skill_idea","")[:40]}...</p>
            </div>
            <span class="text-lg font-bold text-indigo-600">{node.get("skill_score",0)}</span>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skill 挖掘报告 · {process_name}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
  .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
  .card-hover:hover {{ transform: translateY(-2px); }}
</style>
</head>
<body class="bg-gray-50 min-h-screen">

  <!-- Header -->
  <div class="gradient-bg text-white py-12 px-6">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-center gap-2 text-white/70 text-sm mb-4">
        <span>🔍</span><span>Skill 挖掘报告</span><span>·</span><span>{now}</span>
      </div>
      <h1 class="text-3xl font-bold mb-2">{process_name}</h1>
      <p class="text-white/80">已完成智能分析，识别出 Skill 建设机会</p>
      
      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4 mt-8">
        <div class="bg-white/20 backdrop-blur rounded-2xl p-4 text-center">
          <div class="text-3xl font-bold">{total_nodes}</div>
          <div class="text-white/80 text-sm mt-1">流程节点总数</div>
        </div>
        <div class="bg-white/20 backdrop-blur rounded-2xl p-4 text-center">
          <div class="text-3xl font-bold text-green-300">{high_count}</div>
          <div class="text-white/80 text-sm mt-1">高优先级 Skill 机会</div>
        </div>
        <div class="bg-white/20 backdrop-blur rounded-2xl p-4 text-center">
          <div class="text-3xl font-bold text-yellow-300">{medium_count}</div>
          <div class="text-white/80 text-sm mt-1">中优先级机会</div>
        </div>
      </div>
    </div>
  </div>

  <div class="max-w-4xl mx-auto px-6 py-10">

    <!-- Top 3 -->
    <div class="mb-10">
      <h2 class="text-xl font-bold text-gray-900 mb-4">🏆 最推荐优先实施</h2>
      <div class="space-y-3">
        {top3_html}
      </div>
    </div>

    <!-- 分割线 -->
    <div class="border-t border-gray-200 my-8"></div>

    <!-- 所有节点分析 -->
    <div>
      <h2 class="text-xl font-bold text-gray-900 mb-2">📋 全节点 Skill 分析</h2>
      <p class="text-sm text-gray-500 mb-6">以下为流程中每个节点的 Skill 适合度评估（满分100分）</p>
      <div class="grid gap-4">
        {nodes_html}
      </div>
    </div>

    <!-- 图例 -->
    <div class="mt-10 bg-white rounded-2xl p-6 border border-gray-100">
      <h3 class="font-semibold text-gray-700 mb-3">📌 评分说明</h3>
      <div class="grid grid-cols-2 gap-3 text-sm text-gray-600">
        <div>• <strong>80-100分</strong>：强烈建议立即构建</div>
        <div>• <strong>60-79分</strong>：有机会，需补充信息</div>
        <div>• <strong>40-59分</strong>：可做但需配合其他手段</div>
        <div>• <strong>40分以下</strong>：暂缓，条件不成熟</div>
      </div>
    </div>

    <div class="text-center text-gray-400 text-xs mt-8">
      由 Qoder Skill 挖掘专家 自动生成 · {now}
    </div>
  </div>

</body>
</html>'''


def main():
    if len(sys.argv) < 2:
        # 无参数时使用示例数据演示
        data = EXAMPLE_DATA
        print("[提示] 未提供数据文件，使用示例数据生成演示报告")
    else:
        json_path = sys.argv[1]
        if not os.path.exists(json_path):
            print(f"[错误] 文件不存在: {json_path}")
            sys.exit(1)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    html = generate_html(data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"D:\\skill_mining_report_{timestamp}.html"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[成功] 报告已生成: {output_path}")
    
    # 自动打开浏览器预览
    import subprocess
    subprocess.Popen(["powershell", "-Command", f"Start-Process '{output_path}'"])
    print("[成功] 已自动打开浏览器预览")
    
    return output_path


if __name__ == "__main__":
    main()
