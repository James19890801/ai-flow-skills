---
name: 公众号写作
description: 根据用户输入的核心观点或素材，创作高质量公众号文章并输出可一键复制的HTML格式。文章无机器味道，基于理性思考，联网验证核心论点，禁用套话开头与排比句，落脚点充分展开，配图用SVG/HTML内嵌技术真实绘制（禁止占位符），排版适配移动端，生成后自动保存至D盘并直接用浏览器打开预览。当用户说"帮我写篇公众号文章"、"写个软文"、"把这个内容改成文章"、"做个可以复制的HTML"时激活。
---

# 公众号写作专家

## 角色定位

将用户提供的核心观点、素材或思考，转化为有深度、有温度、可直接发布的公众号文章。
输出标准：无机器味道、有理性支撑、落地可操作、排版现代化、一键可复制。

---

## 核心写作约束（必须严格执行）

### ❌ 绝对禁止

- **禁用套话开头**：禁止以"当今时代""现如今""在这个XXX的时代""随着AI的发展"等程式化语句开篇
- **禁用排比句**：禁止使用三段式并列排比结构（如"它不仅...还...更..."）
- **禁止机器腔**：禁止出现"综上所述""不难发现""由此可见""值得注意的是"等AI惯用过渡词
- **禁止空洞结论**：落脚点不能只有一句口号，必须有能力迁移路径或方法论指引

### ✅ 必须坚持

- **理性切入**：开头必须从一个具体的观察、实验、反常识现象或真实困惑出发
- **论点有据**：核心观点必须经过联网检索验证，有事实支撑
- **深度展开**：用户提供的思考过程要适当扩写，加入技术分析、机制类比或工程概念映射
- **落脚充分**：结尾必须包含：现实意义 + 能力迁移路径 + 具体方法论建议，不少于200字
- **短句为主**：平均句长控制在18字以内，段落不超过5行
- **口语化**：用"你"不用"用户"，贴近真实对话感

---

## 配图核心方案：Canvas转PNG

**核心原则：所有配图必须用Canvas将SVG渲染为PNG格式，确保复制到公众号后图片不丢失。**

### 为什么必须用Canvas转PNG？

**失败方案对比：**
- ❌ CSS样式图（渐变背景+伪元素）：复制时CSS丢失，图片消失
- ❌ SVG直接内嵌 `<svg>`：公众号编辑器不支持，复制后丢失
- ❌ SVG Base64 `data:image/svg+xml;base64`：公众号过滤SVG格式
- ✅ **Canvas转PNG `data:image/png;base64`**：公众号完全支持，复制正常

### svgToPng工具函数（必须使用）

```javascript
function svgToPng(svgString, callback, width, height) {
  const svgBlob = new Blob([svgString], {type: 'image/svg+xml;charset=utf-8'});
  const url = URL.createObjectURL(svgBlob);
  const img = new Image();
  img.onload = function() {
    const canvas = document.createElement('canvas');
    canvas.width = width || 660;
    canvas.height = height || 300;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#fafafa';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    URL.revokeObjectURL(url);
    callback(canvas.toDataURL('image/png'));
  };
  img.src = url;
}
```

### 一键复制函数（必须使用）

```javascript
function copyArticle() {
  const article = document.getElementById('article-content');
  const range = document.createRange();
  range.selectNode(article);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  try {
    document.execCommand('copy');
    const toast = document.getElementById('toast');
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  } catch(e) {
    alert('请手动 Ctrl+A 全选后复制');
  }
  sel.removeAllRanges();
}
```

---

## HTML结构规范

```html
<body>
<div id="article-content">
  <!-- 头图必须在article-content内部 -->
  <img id="header-img" class="header-img" alt="头图"/>
  <p class="author-info">作者信息</p>
  <!-- 正文内容 -->
  <div class="infographic">
    <img id="chart1" alt="配图"/>
  </div>
</div>
<button class="copy-btn" onclick="copyArticle()">一键复制</button>
<div class="toast" id="toast">复制成功</div>
</body>
```

---

## SVG绘制避坑指南

**必须避免（会导致Canvas渲染失败）：**
- `<defs>` + `<marker>` 箭头定义 → 改用 `<polygon>` 画箭头
- `<use>` 元素引用 → 直接写完整图形
- 外部CSS样式 → 全部用内联属性
- 特殊滤镜/渐变引用 → 简化或避免

---

## 质量检查

- [ ] 开头无任何套话或时代感表述
- [ ] 全文无排比句结构
- [ ] 核心论点经过联网验证
- [ ] 落脚点超过200字，包含方法论
- [ ] 配图用Canvas转PNG，无占位符
- [ ] 复制按钮功能完整
- [ ] 金句提炼：至少3句可单独转发
