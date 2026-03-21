"""
build_skill.py - 根据挖掘结果自动封装生成 Skill 文件
用法: python build_skill.py <skill_info.json>

JSON格式:
{
  "skill_name": "比价分析",
  "skill_id": "price-comparison-analysis",
  "node_description": "对比多家供应商报价，形成比价表",
  "trigger_scenes": ["用户说帮我比价", "上传了多份报价单"],
  "input_format": "多份供应商报价文件（PDF/Excel/文字）",
  "output_format": "结构化比价矩阵 + 推荐意见",
  "key_steps": ["解析各份报价单", "提取关键价格项", "横向对比", "生成推荐"],
  "install_path": "personal"
}
"""

import sys
import json
import os
from datetime import datetime

SKILL_TEMPLATE = '''---
name: {skill_id}
description: {description_line}
---

# {skill_name}

## 核心任务
{node_description}

## 触发场景
{trigger_scenes}

## 执行步骤

### 第一步：获取输入
接收用户提供的 {input_format}

### 第二步：处理分析
{steps_detail}

### 第三步：输出结果
按以下格式输出：{output_format}

## 输出规范

- 结构清晰，有标题层级
- 关键数据高亮标注
- 末尾给出明确结论或建议
- 若信息不足，主动追问关键缺失项

## 注意事项
- 保持客观中立，数据说话
- 遇到模糊信息主动确认，不猜测
- 输出前做逻辑自检
'''


def build_skill(data):
    skill_name = data.get("skill_name", "未命名Skill")
    skill_id = data.get("skill_id", "unnamed-skill")
    node_description = data.get("node_description", "")
    trigger_scenes = data.get("trigger_scenes", [])
    input_format = data.get("input_format", "用户输入")
    output_format = data.get("output_format", "结构化文本")
    key_steps = data.get("key_steps", [])
    install_path = data.get("install_path", "personal")

    # 生成 description 一行（用于 YAML frontmatter）
    triggers_text = "、".join(f'"{t}"' for t in trigger_scenes[:3])
    description_line = f"{skill_name}：{node_description[:50]}。当用户说{triggers_text}时触发。"

    # 触发场景列表
    trigger_scenes_md = "\n".join(f"- {s}" for s in trigger_scenes)

    # 步骤详情
    steps_detail = "\n".join(f"{i+1}. {step}" for i, step in enumerate(key_steps))

    skill_content = SKILL_TEMPLATE.format(
        skill_id=skill_id,
        skill_name=skill_name,
        description_line=description_line,
        node_description=node_description,
        trigger_scenes=trigger_scenes_md,
        input_format=input_format,
        output_format=output_format,
        steps_detail=steps_detail,
    )

    # 确定安装目录
    if install_path == "personal":
        base_dir = os.path.join(os.path.expanduser("~"), ".qoder", "skills")
    else:
        base_dir = os.path.join(".qoder", "skills")

    skill_dir = os.path.join(base_dir, skill_id)
    os.makedirs(skill_dir, exist_ok=True)

    skill_file = os.path.join(skill_dir, "SKILL.md")
    with open(skill_file, 'w', encoding='utf-8') as f:
        f.write(skill_content)

    print(f"\n{'='*50}")
    print(f"✅ Skill 封装完成！")
    print(f"{'='*50}")
    print(f"📁 Skill 目录: {skill_dir}")
    print(f"📄 Skill 文件: {skill_file}")
    print(f"\n--- Skill 预览 ---\n")
    print(skill_content)
    print(f"\n{'='*50}")
    print(f"💡 在 Qoder 中说 '{trigger_scenes[0] if trigger_scenes else skill_name}' 即可调用此 Skill！")
    print(f"{'='*50}\n")

    return skill_file


def main():
    if len(sys.argv) < 2:
        print("[提示] 用法: python build_skill.py <skill_info.json>")
        print("[提示] 使用示例数据演示...")
        data = {
            "skill_name": "供应商比价分析",
            "skill_id": "supplier-price-comparison",
            "node_description": "对比多家供应商报价，识别最优选项，输出比价矩阵",
            "trigger_scenes": ["帮我比价", "分析这几份报价单", "哪家供应商更合适"],
            "input_format": "多份供应商报价文件或报价数据",
            "output_format": "比价对比表 + 综合评分 + 推荐意见",
            "key_steps": [
                "解析各供应商报价文件，提取关键价格项和条款",
                "建立统一比较维度（单价、交期、付款条件、售后等）",
                "横向对比，生成结构化比价矩阵",
                "综合评分，标注最优/次优选项",
                "输出推荐意见及风险提示"
            ],
            "install_path": "personal"
        }
    else:
        json_path = sys.argv[1]
        if not os.path.exists(json_path):
            print(f"[错误] 文件不存在: {json_path}")
            sys.exit(1)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    build_skill(data)


if __name__ == "__main__":
    main()
