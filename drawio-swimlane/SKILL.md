---

name: drawio-swimlane

description: 绘制流程图、泳道图、跨部门流程图。当用户说"画流程图"、"画个流程图"、"帮我画流程"、"泳道图"、"跨部门流程图"、"SOP流程图"、"业务流程图"、"角色-活动矩阵图"时，必须优先使用此 skill，禁止调用 canvas-design 或 frontend-design。输出标准 draw.io XML 文件，并通过嵌入式 iframe 在浏览器中直接渲染和编辑，无需安装任何软件。

---


# Draw.io 跨部门泳道图绘制最佳实践



用户提供流程步骤数据（角色、活动、时序、分支逻辑），生成可直接在浏览器**预览 + 在线编辑**的专业泳道图。



---



## 零、强制执行原则（最高优先级）

> **这些规则凌驾于所有其他描述之上，违反即重做。**

1. **必须用 Python 脚本生成 XML**，禁止手写 XML —— 手写 XML 无法保证坐标唯一性
2. **活动节点 value 只写活动名称**，禁止写备注、说明、时间、解释性文字 —— 备注会导致字体爆大
3. **每个活动必须占据唯一的 X 坐标槽位**，用代码 `slot` 机制分配，禁止凭感觉写坐标
4. **脚本内置坐标冲突检查**，生成 XML 前必须断言所有节点 X 坐标唯一，有冲突则抛出异常
5. **自动打开预览**，py 脚本最后一行必须是 `subprocess.Popen(['start', html_path], shell=True)`

### 鲁棒性强制规范

6. **Python 脚本必须包含异常捕获**：所有文件写入、XML 生成操作用 `try/except` 包裹，失败时打印清晰错误信息
7. **XML 合法性验证前置**：写入文件前必须用 `xml.etree.ElementTree.fromstring()` 验证 XML 合法，解析报错则中止并提示修复
8. **HTML 预览打开失败容错**：若 `subprocess.Popen` 报错（如文件不存在），捕获异常并打印文件绝对路径，提示用户手动打开
9. **字段值转义保护**：所有写入 XML `value` 属性的字符串必须转义 `&`→`&amp;`、`<`→`&lt;`、`>`→`&gt;`、`"`→`&quot;`，防止 XML 结构损坏
10. **JS 模板字符串转义三件套**：XML 写入 HTML JS 模板字符串前必须转义 `` ` ``→`` \` ``，`$`→`\$`，`\`→`\\`，缺一不可

---



## 交付规范

必须同时输出两个文件，并**自动打开预览**：

1. **`流程名.drawio`** — 标准 draw.io XML，可下载后在 draw.io 网页版/桌面版编辑
2. **`流程名.html`** — 嵌入 draw.io 全功能编辑器的页面，浏览器直接打开即可**查看 + 拖拽编辑**，无需任何安装
3. **自动打开预览** — 使用终端命令自动打开 HTML 文件，用户无需手动查找文件位置

> **核心要求**：
> - HTML 必须使用「可编辑模式」，用户可以直接在 draw.io 面板中移动节点、修改文字、添加/删除连线
> - **必须自动打开预览**，确保用户能立即看到效果，无需手动寻找文件



---



## 一、draw.io XML 结构规范



### 1. 泳道容器（pool）



**强制使用 `shape=pool` + `childLayout=stackLayout`**，禁止使用 `shape=table` 或 `childLayout=tableLayout`（会产生冗余竖线）。

> **标题独立规则（强制）**：pool 的 `value` 必须为空字符串，`startSize=0`；流程标题必须单独放一个 `text` 类型节点，置于 pool 上方画布顶部居中，`parent="1"`（属于根节点，不属于 pool），确保标题与活动节点/连线完全分离，不产生重叠。

```python
# 标题节点（独立于 pool 之外）
TITLE_H = 40
POOL_Y  = 20 + TITLE_H + 10   # pool 从标题下方 10px 开始
title_x = 20 + (total_w - 300) // 2

title_cell = f'''<mxCell id="title" value="流程名称"
  style="text;html=1;strokeColor=none;fillColor=none;align=center;
         verticalAlign=middle;whiteSpace=wrap;fontStyle=1;fontSize=15;fontColor=#333333;"
  vertex="1" parent="1">
  <mxGeometry x="{title_x}" y="20" width="300" height="{TITLE_H}" as="geometry"/>
</mxCell>'''

# pool value 清空，startSize=0
pool_cell = f'''<mxCell id="pool" value=""
  style="shape=pool;html=1;startSize=0;horizontal=1;
         childLayout=stackLayout;horizontalStack=0;
         resizeParent=1;resizeLast=1;collapsible=0;
         fillColor=#f5f5f5;strokeColor=#555555;"
  vertex="1" parent="1">
  <mxGeometry x="20" y="{POOL_Y}" width="{total_w}" height="{len(lanes)*LANE_H}" as="geometry"/>
</mxCell>'''
```


```xml

<mxCell id="pool" value="流程标题"

  style="shape=pool;html=1;startSize=30;horizontal=1;

         childLayout=stackLayout;horizontalStack=0;

         resizeParent=1;resizeLast=1;collapsible=0;

         fillColor=#f5f5f5;strokeColor=#555555;

         fontStyle=1;fontSize=14;fontColor=#333333;align=center;"

  vertex="1" parent="1">

  <mxGeometry x="20" y="20" width="[总宽]" height="[总高]" as="geometry"/>

</mxCell>

```



### 2. 泳道（lane）

- `horizontal=0`：泳道标题在左侧竖排
- `startSize=40`：左侧标题宽度
- **高度自适应规则（强制）**：
  - **单行活动（无返工）**：`height="100"`
  - **含返工节点**：`height="180"`（主流程 y=20~80，返工节点 y=110）
- 各泳道使用不同浅色填充，配套深色边框
- **返工节点必须放在同泳道内，禁止跨泳道返工线**



```xml

<mxCell id="lane1" value="角色名称"

  style="swimlane;html=1;startSize=40;swimlaneBody=1;swimlaneHead=1;swimlaneLine=1;

         fontStyle=1;align=center;fontSize=12;horizontal=0;

         fillColor=#dae8fc;strokeColor=#6c8ebf;"

  vertex="1" parent="pool">

  <mxGeometry y="[偏移]" width="[同 pool 宽]" height="[按内容定]" as="geometry"/>

</mxCell>

```



> **强制要求**：泳道 style 中**禁止设置** `swimlaneBody=0` 或 `swimlaneHead=0`，这两个属性会导致泳道分隔线与边框消失，必须保持为 `1` 或直接省略（默认为 1）。



**推荐配色方案（5 泳道）：**



| 角色 | fillColor | strokeColor |

|------|-----------|-------------|

| 业务 HR | `#dae8fc` | `#6c8ebf` |

| 候选人/客户 | `#fff2cc` | `#d6b656` |

| 系统/自动化 | `#d5e8d4` | `#82b366` |

| 共享服务/运营 | `#ffe6cc` | `#d79b00` |

| 行政/IT/支持 | `#e1d5e7` | `#9673a6` |



### 3. 节点类型



**开始/结束节点（必须）：**

```xml

<!-- 开始：黑底白字椭圆，放在第一条泳道最左侧 -->

<mxCell id="start" value="开始"

  style="ellipse;whiteSpace=wrap;html=1;

         fillColor=#1a1a1a;strokeColor=#1a1a1a;

         fontColor=#ffffff;fontStyle=1;fontSize=12;"

  vertex="1" parent="lane1">

  <mxGeometry x="80" y="[垂直居中]" width="80" height="40" as="geometry"/>

</mxCell>



<!-- 结束：同样黑底白字椭圆，放在最后一个活动泳道最右侧 -->

<mxCell id="end" value="结束" style="[同上]" vertex="1" parent="[最后活动所在 lane]">

  <mxGeometry x="[最右]" y="[垂直居中]" width="80" height="40" as="geometry"/>

</mxCell>

```



**普通活动节点（必须带编号，只写活动名称，禁止写备注）：**

> **活动编号规范（强制）**：
> - **顺序执行的活动**：使用连续阿拉伯数字编号（1.0、2.0、3.0...）
> - **同步协同的活动**：使用相同编号（如 7.0 表示申请人、采购部、财务部同时参与验收）
> - **决策点**：不编号（如"超限额？"）
> - **开始/结束节点**：不编号

```xml
<!-- value 必须包含活动编号，格式：X.0 活动名称 -->
<mxCell id="n1" value="1.0 提交采购申请"
  style="rounded=1;whiteSpace=wrap;html=1;
         fillColor=[泳道色];strokeColor=[泳道边框色];
         fontSize=11;arcSize=8;"
  vertex="1" parent="[所在 lane]">
  <mxGeometry x="[slot_x(n)]" y="[垂直居中]" width="120" height="40" as="geometry"/>
</mxCell>

<!-- 同步协同示例：同一编号 7.0 出现在多个泳道 -->
<mxCell id="n8" value="7.0 参与验收" parent="lane0">...</mxCell>
<mxCell id="n9" value="7.0 资产验收入库" parent="lane2">...</mxCell>
<mxCell id="n10" value="7.0 参与验收" parent="lane3">...</mxCell>
```




**KCP 关键控制点（蓝色加粗边框，value 只写活动名称）：**

```xml
<!-- KCP节点也只写活动名称，不加备注 -->
<mxCell id="n4" value="活动名称"
  style="rounded=1;whiteSpace=wrap;html=1;
         fillColor=[泳道色];strokeColor=#1677ff;strokeWidth=2;
         fontSize=11;arcSize=8;"
  vertex="1" parent="[lane]">
  <mxGeometry x="[slot_x(n)]" y="[垂直居中]" width="120" height="40" as="geometry"/>
</mxCell>
```



**决策节点（菱形）：**

```xml
<mxCell id="d1" value="判断条件？"
  style="rhombus;whiteSpace=wrap;html=1;
         fillColor=#fff0cc;strokeColor=#d6b656;
         fontSize=11;fontStyle=1;"
  vertex="1" parent="[lane]">
  <mxGeometry x="[X]" y="10" width="100" height="80" as="geometry"/>
</mxCell>
```

**返工节点（同泳道内闭环）：**

```xml
<!-- 返工节点：放在主流程下方，y=110，高度 50 -->
<mxCell id="n3_return" value="&lt;b&gt;3a&lt;/b&gt; 返回修改完善"
  style="rounded=1;whiteSpace=wrap;html=1;
         fillColor=[泳道色];strokeColor=[泳道边框色];
         fontSize=11;arcSize=10;"
  vertex="1" parent="[lane]">
  <mxGeometry x="400" y="110" width="140" height="50" as="geometry"/>
</mxCell>

<!-- 返工回线：使用泳道左侧通道，避免交叉 -->
<mxCell id="e_return_back" style="edgeStyle=orthogonalEdgeStyle;html=1;rounded=1;arcSize=10;
  exitX=0;exitY=0.5;entryX=0;entryY=0.5;
  strokeColor=#cf1322;strokeWidth=1.5;dashed=1;"
  edge="1" parent="[lane]" source="n3_return" target="n3">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="180" y="135"/>  <!-- 左侧通道 -->
      <mxPoint x="180" y="50"/>
    </Array>
  </mxGeometry>
</mxCell>
```



### 4. 连线规范（核心原则）

**优先级1：连接点标准**
- **正向流程**：左进右出（`entryX=0, exitX=1`）
- **返工流程**：上出上进（`exitY=0, entryY=0`）或下出下进（`exitY=1, entryY=1`）
- 返工线绝不使用左右连接点

**优先级2：禁止穿过活动框**
- 返工线必须计算路径，从所有活动框的上方或下方绕行
- 宁可走高/走低，绝不穿过活动实体

**优先级3：禁止线交叉**
- 返工线高度必须避开所有正向连线
- 通过坐标计算确定最优高度

**优先级4：最短路径**
- 在满足以上条件后，选择最短路径

**返工线计算方法：**
```
1. 确定源节点和目标节点的X坐标
2. 计算路径上所有活动框的Y范围（y到y+height）
3. 选择返工线高度：min(所有活动框的y) - 20 或 max(所有活动框的y+height) + 20
4. 绘制：上出→横向→上进（┐形）或下出→横向→下进（┌形）
```

**所有连线统一使用圆角折线风格：**

```xml
<!-- 同泳道内实线连线（按泳道配色） -->
<mxCell id="e12" style="edgeStyle=orthogonalEdgeStyle;html=1;rounded=1;arcSize=10;
  exitX=1;exitY=0.5;entryX=0;entryY=0.5;
  strokeColor=#6c8ebf;strokeWidth=1.5;"
  edge="1" source="n1" target="n2" parent="lane1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>

<!-- 跨泳道连线：parent 设为 pool -->
<mxCell id="e45" style="edgeStyle=orthogonalEdgeStyle;html=1;rounded=1;arcSize=10;
  exitX=1;exitY=0.5;entryX=0;entryY=0.5;
  strokeColor=#d6b656;strokeWidth=1.5;"
  edge="1" source="n4" target="n5" parent="pool">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="[转折 X]" y="[源节点中心 Y]"/>
      <mxPoint x="[转折 X]" y="[目标节点中心 Y]"/>
    </Array>
  </mxGeometry>
</mxCell>

<!-- 返工线示例：上出上进，从活动上方绕行 -->
<mxCell id="e_return" value="否" style="edgeStyle=orthogonalEdgeStyle;html=1;rounded=1;arcSize=10;
  exitX=0.5;exitY=0;entryX=0.5;entryY=0;
  strokeColor=#cf1322;strokeWidth=1.5;dashed=1;
  fontColor=#cf1322;fontStyle=1;fontSize=10;"
  edge="1" source="d2" target="n3" parent="lane2">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="[源节点中心X]" y="[计算后的高度，确保在活动上方]"/>
      <mxPoint x="[目标节点中心X]" y="[计算后的高度]"/>
    </Array>
  </mxGeometry>
</mxCell>
```

**连线着色规则：**
- 实线主流程：与源节点所在泳道颜色一致
- 跨泳道触发（虚线）：使用目标泳道颜色
- 并行触发（虚线）：紫色 `#9673a6`
- 分支「是」：绿色 `#389e0d`，分支「否」：红色 `#cf1322`
- 返工线：红色 `#cf1322`，虚线



---



## 二、布局规划原则



### X 坐标（时间轴）- 强制原则

**核心原则：每个活动必须占据唯一的 X 槽位，用代码分配，禁止手工填写坐标**

**标准做法：slot 机制（强制）**

```python
# ① 先列出所有活动，按时间顺序分配槽位
# 格式：(slot编号, 活动id, 所在泳道id, 活动名称)
# slot 从 1 开始，每个活动独占一个 slot，真正并行的活动共享同一 slot

activities = [
    (1,  'n1',  'lane2', '需求初筛'),
    (2,  'n2',  'lane1', '意向确认'),
    (3,  'n3',  'lane3', '项目立项'),
    (4,  'n4',  'lane4', '深度诊断'),   # slot4
    (4,  'n5',  'lane1', '配合诊断'),   # slot4，与n4真正并行，共享slot
    (5,  'n6',  'lane4', '方案设计'),
    # ...以此类推
]

# ② 坐标计算函数
NODE_W   = 120   # 节点宽度
NODE_H   = 40    # 节点高度
SLOT_GAP = 60    # 槽间距
X_START  = 160   # 第一个活动的起始X（留给开始节点）

def slot_x(slot: int) -> int:
    return X_START + (slot - 1) * (NODE_W + SLOT_GAP)

# ③ 生成节点时调用
for slot, nid, lane, name in activities:
    x = slot_x(slot)
    # 生成 <mxCell ...> XML

# ④ 坐标冲突检查（生成XML前执行，有冲突直接抛出异常）
def check_x_unique(activities):
    from collections import defaultdict
    slot_lanes = defaultdict(list)
    for slot, nid, lane, name in activities:
        slot_lanes[slot].append((lane, nid, name))
    for slot, items in slot_lanes.items():
        lanes = [item[0] for item in items]
        if len(lanes) != len(set(lanes)):
            raise ValueError(f"Slot {slot} 中同一泳道出现多个节点: {items}")
    print("✓ 坐标检查通过，无冲突")

check_x_unique(activities)

# ⑤ 生成XML前验证合法性（鲁棒性保障，必须执行）
def validate_xml(xml_str):
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(xml_str)
        print("✓ XML 合法性验证通过")
        return True
    except ET.ParseError as e:
        print(f"✗ XML 解析失败：{e}")
        print("  请检查 value 属性中是否含有未转义的 & < > \" 字符")
        return False

# ⑥ 字段值安全转义函数（写入 XML value 前必须调用）
def xml_escape(text: str) -> str:
    return (str(text)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;'))

# ⑦ 安全写入文件（带异常捕获）
def safe_write(path, content, encoding='utf-8'):
    import os
    try:
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        print(f"✓ 文件已写入：{os.path.abspath(path)}")
        return True
    except OSError as e:
        print(f"✗ 文件写入失败：{e}")
        print(f"  请检查目录是否存在或是否有写入权限：{os.path.dirname(os.path.abspath(path))}")
        return False

# ⑧ 安全打开预览（带异常捕获）
def safe_open_preview(html_path):
    import subprocess, os
    abs_path = os.path.abspath(html_path)
    if not os.path.exists(abs_path):
        print(f"✗ 预览文件不存在：{abs_path}")
        return
    try:
        subprocess.Popen(['start', abs_path], shell=True)
        print(f"✓ 预览已自动打开：{abs_path}")
    except Exception as e:
        print(f"✗ 自动打开失败：{e}")
        print(f"  请手动打开文件：{abs_path}")
```

**检查清单（代码执行前必须过一遍）：**
```
□ activities 列表中，非并行活动的 slot 是否全部唯一？
□ 共享同一 slot 的活动，是否确实在业务上同时进行？
□ check_x_unique() 是否通过（无异常）？
```




### Y 坐标（泳道内）

- 单行活动：y = (泳道高度 - 节点高度) / 2（垂直居中）

- 多行活动（含决策分支）：从 y=40 开始，行间距约 100px

- 确保所有节点 bottom < 泳道高度（严禁溢出）



### 泳道高度参考

| 内容 | 建议高度 |

|------|---------|

| 单行活动（1-3 个） | 120px |

| 含决策分支（上下 2 行） | 250-300px |

| 含多分支（3 行） | 380-420px |

| 含多个纵向活动（4+） | 按实际计算 |



### 泳道宽度：动态适配规则（重要）



**禁止固定宽度**，必须根据最右侧节点自动计算：



```

泳道宽度 = max(所有节点的 x + width) + 60px 右留白

```



用 Python 生成 XML 前先扫描最大右边界：



```python

import xml.etree.ElementTree as ET



tree = ET.fromstring(xml_content)

max_right = 0

for cell in tree.iter('mxCell'):

    if cell.get('vertex') != '1':

        continue

    style = cell.get('style', '')

    if 'pool' in style or 'childLayout' in style or 'swimlane' in style:

        continue

    geo = cell.find('mxGeometry')

    if geo is not None:

        right = float(geo.get('x', 0)) + float(geo.get('width', 0))

        max_right = max(max_right, right)



lane_width = int(max_right) + 60  # 60px 右留白



# 将 lane_width 应用到 swim_container 和所有 lane_*

```



- `swim_container` 的 `width` = `lane_width`

- 每条 `lane_*` 的 `width` = `lane_width`

- 生成后用 ET 验证 XML 合法性再写入文件



---



## 三、HTML 可编辑嵌入页模板



### 方案：embed.diagrams.net 全功能编辑器模式



`embed.diagrams.net` 支持两种模式：

- **只读预览**（旧方案）：URL 带 `noSaveBtn=1&noExitBtn=1`，用户无法编辑

- **全功能编辑**（新方案）：URL 带 `&edit=1`，去掉禁用按钮参数，用户可直接在面板上拖拽编辑



```python

# 用 Python 生成 HTML，处理 XML 中的特殊字符转义

with open('流程图.drawio', 'r', encoding='utf-8') as f:

    raw = f.read().strip()



# JS 模板字符串安全转义（3 个字符）

xml_js = raw.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')



html = f"""<!DOCTYPE html>

<html lang="zh-CN">

<head>

<meta charset="UTF-8">

<title>流程图标题</title>

<style>

*  margin:0;padding:0;box-sizing:border-box; 

html,body  width:100%;height:100%;overflow:hidden; 

#header {{

  height:44px;background:#fff;border-bottom:1px solid #e8e8e8;

  display:flex;align-items:center;padding:0 16px;gap:12px;

  font-family:"Microsoft YaHei",sans-serif;font-size=14px;

}}

#header span  flex:1;font-weight:500; 

#header button {{

  padding:5px 14px;border-radius:4px;font-size:13px;cursor:pointer;

  border:1px solid #d9d9d9;background:#fff;

}}

#frame-wrap  width:100%;height:calc(100vh - 44px); 

iframe  width:100%;height:100%;border:none; 

</style>

</head>

<body>

<div id="header">

  <span>📋 流程图标题</span>

  <button onclick="dl()">⬇ 下载 .drawio 文件</button>

</div>

<div id="frame-wrap">

  <!-- 关键：使用 edit=1 开启全功能编辑器，去掉 noSaveBtn 和 noExitBtn -->

  <iframe id="drawio"

    src="https://embed.diagrams.net/?embed=1&spin=1&proto=json&ui=default&edit=1">

  </iframe>

</div>

<script>

const XML = `{xml_js}`;

const iframe = document.getElementById('drawio');



function sendXml() {{

  iframe.contentWindow.postMessage(

    JSON.stringify({ action: 'load', xml: XML, autosave: 1 }), '*'

  );

}}



// 双重保险：load 事件 + init 消息，都触发加载

iframe.addEventListener('load', () => setTimeout(sendXml, 1500));

window.addEventListener('message', (e) => {{

  try {{

    const msg = JSON.parse(e.data);

    if (msg.event === 'init') sendXml();

    // 用户在编辑器内保存时，autosave 会回传修改后的 XML

    if (msg.event === 'autosave' || msg.event === 'save') {{

      console.log('已保存 XML:', msg.xml);

    }}

  }} catch(err) {{}}

}});



function dl() {{

  const blob = new Blob([XML], {{type:'application/xml'}});

  const a = document.createElement('a');

  a.href = URL.createObjectURL(blob);

  a.download = '流程图.drawio';

  a.click();

}}

</script>

</body>

</html>"""

# 写入文件
with open('d:/流程图.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 自动打开本地HTML预览
import subprocess
subprocess.Popen(['start', 'd:/流程图.html'], shell=True)

print('✓ 文件生成成功并已自动打开预览！')
print('  drawio: d:/流程图.drawio')
print('  HTML:   d:/流程图.html')

```



### 关键参数说明



| 参数 | 旧（只读）| 新（可编辑）| 说明 |

|------|----------|------------|------|

| `ui` | `min` | `default` | 显示完整工具栏和面板 |

| `edit` | 无 | `1` | 开启编辑模式 |

| `noSaveBtn` | `1` | **去掉** | 保留保存按钮 |

| `noExitBtn` | `1` | **去掉** | 保留退出按钮 |

| `autosave`（postMessage）| `0` | `1` | 编辑时回传 XML |



**注意事项：**

- XML 写入 JS 模板字符串前必须转义 3 个字符：`` ` `` → `` \` ``，`$` → `\$`，`\` → `\\`

- iframe 的 `load` 事件 + `init` postMessage 双重监听，解决不同网络环境下加载时机不一致

- 延迟 1500ms 发送 XML，确保 draw.io 引擎初始化完成

- **严禁** 在 `window.onload` 中用 `window.location.href` 跳转，会导致预览页闪退变空白

- `ui=default` 才会显示左侧图形面板、右侧属性面板、顶部菜单栏，缺少这些面板用户无法在页面内编辑



---



## 四、流程逻辑强制规范

1. **主干从左到右**：严格按时间/事件顺序，不允许回头箭头破坏主干方向
2. **开始/结束必有**：开始椭圆在第一条泳道最左，结束椭圆在最后活动所在泳道最右，均为黑底白字
3. **跨泳道连线**：`parent="pool"`，使用折点（`Array as="points"`）明确转折路径
4. **决策分支**：「是」向下继续主干，「否」向下到返工节点；两条分支最终必须合流
5. **返工闭环约束（新增）**：
   - **返工节点必须放在同泳道内**，y=110，禁止跨泳道
   - **返工回线使用泳道左侧通道**（x=180/380/580…），避免与主流程交叉
   - **返工节点编号**：使用子编号（如 3a、7a、9a）
   - **返工线样式**：`dashed=1`，红色 `#cf1322`
6. **触发/并行**：用虚线 `dashed=1;dashPattern=8 4` 区分，并标注文字说明
7. **活动编号**：全部使用阿拉伯数字（1、2、3…），禁止字母（A、B、C）
8. **无孤立节点**：每个活动节点至少有一条入线和一条出线（开始/结束节点除外）



---



## 五、常见问题与解决方案



| 问题 | 原因 | 解决方案 |

|------|------|---------|

| 泳道内出现冗余竖线 | 使用了 `childLayout=tableLayout` | 改为 `shape=pool` + `childLayout=stackLayout` |

| **泳道分隔线/边框线不显示** | 泳道 style 含 `swimlaneBody=0` 或 `swimlaneHead=0` | 必须设为 `swimlaneBody=1;swimlaneHead=1`（或删除该参数，默认为 1）|

| 预览页空白/闪退 | `window.location.href` 自动跳转 | 删除自动跳转，改为手动点击按钮 |

| 打开 HTML 无法编辑节点 | iframe URL 使用了 `noSaveBtn=1`/`ui=min` | 改用 `ui=default&edit=1`，去掉禁用参数 |

| **XML 属性值含裸双引号报错** | `value="...文字"...文字"..."` 属性内含 `"` | 属性值内所有 `"` 必须转义为 `&quot;` |

| 跨泳道连线跑偏 | 坐标系混用（lane 坐标 vs pool 坐标） | 跨泳道连线一律 `parent="pool"`，坐标用 pool 绝对坐标 |

| **泳道右侧截断，活动溢出** | 泳道 `width` 固定值不够 | 动态计算：`max(节点 x+width) + 60` 作为泳道宽度 |

| 活动节点溢出泳道（垂直）| Y 坐标超过泳道高度 | 计算每个节点 bottom = y + height < 泳道 height |

| XML 在 JS 中解析报错 | 特殊字符未转义 | 替换 3 个字符：`` ` ``、`$`、`\` |

| draw.io 加载后显示空白 | init 事件未捕获/发送时机太早 | 同时监听 `load`(+1500ms delay) 和 `init` postMessage |

| **Python 脚本运行报 UnicodeEncodeError** | Windows 终端默认 GBK，打印中文报错 | 脚本顶部加 `import sys; sys.stdout.reconfigure(encoding='utf-8')` 或用 `os.environ['PYTHONIOENCODING']='utf-8'` |

| **XML 写入后文件为空** | open() 写入异常被静默忽略 | 使用 `safe_write()` 函数包裹，捕获 OSError |

| **draw.io 显示 "Invalid XML"** | 活动名称含 `&`、`<`、`>` 字符 | 所有 value 属性值必须调用 `xml_escape()` 函数 |

| **脚本报 FileNotFoundError 写 drawio** | 目标目录不存在 | 脚本开头加 `os.makedirs(os.path.dirname(path), exist_ok=True)` |

---

## 六、完整工作流程示例（含鲁棒性增强）

以下是一个标准的泳道图生成工作流程，包含自动打开预览和所有容错机制：

```python
import os, sys, subprocess
import xml.etree.ElementTree as ET

# 兼容 Windows 终端中文输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ===== 工具函数 =====

def xml_escape(text: str) -> str:
    """写入 XML value 属性前必须调用"""
    return (str(text)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;'))

def validate_xml(xml_str: str) -> bool:
    """写入文件前验证 XML 合法性"""
    try:
        ET.fromstring(xml_str)
        print("✓ XML 合法性验证通过")
        return True
    except ET.ParseError as e:
        print(f"✗ XML 解析失败：{e}")
        print("  请检查 value 属性中是否含有未转义的 & < > \" 字符")
        return False

def safe_write(path: str, content: str, encoding='utf-8') -> bool:
    """安全写入文件，目录不存在时自动创建"""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        print(f"✓ 文件已写入：{os.path.abspath(path)}")
        return True
    except OSError as e:
        print(f"✗ 文件写入失败：{e}")
        return False

def safe_open_preview(html_path: str):
    """安全打开预览，失败时提示手动打开"""
    abs_path = os.path.abspath(html_path)
    if not os.path.exists(abs_path):
        print(f"✗ 预览文件不存在：{abs_path}")
        return
    try:
        subprocess.Popen(['start', abs_path], shell=True)
        print(f"✓ 预览已自动打开：{abs_path}")
    except Exception as e:
        print(f"✗ 自动打开失败：{e}")
        print(f"  请手动打开文件：{abs_path}")

# ===== 主流程 =====

# 1. 生成 draw.io XML（所有活动名称先经过 xml_escape）
# xml_content = ... 根据 activities 列表生成 ...

# 2. 验证 XML 合法性，失败则中止
if not validate_xml(xml_content):
    raise SystemExit("XML 验证失败，请修复后重试")

# 3. 安全写入 .drawio 文件
drawio_path = 'd:/流程名.drawio'
if not safe_write(drawio_path, xml_content):
    raise SystemExit("drawio 文件写入失败，请检查权限")

# 4. 生成 HTML：XML 写入 JS 模板字符串前必须转义三件套
xml_js = xml_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
... HTML 模板内容 ...
const XML = `{xml_js}`;
... 其余 HTML ...
"""

# 5. 安全写入 HTML
html_path = 'd:/流程名.html'
if not safe_write(html_path, html_content):
    print("  HTML 写入失败，但 .drawio 文件已保存，请用 draw.io 桌面版打开")

# 6. 自动打开预览（安全版）
safe_open_preview(html_path)
```

**关键要点**：
- 文件生成后**必须立即自动打开预览**
- 用户无需手动查找文件位置
- 确保用户能第一时间看到流程图效果
- 如果预览有问题，可以立即诊断修复
- **所有步骤均有容错处理，单步失败不影响其他步骤**
