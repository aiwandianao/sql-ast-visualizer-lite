# 项目目标：生成轻量版 SQL 语法树可视化工具，实现「本地输入 SQL → 解析生成 AST → 浏览器可视化」全流程
project:
  name: "sql-ast-visualizer-lite"
  description: "轻量本地工具，可视化 MySQL 语法树，辅助理解 SQL 解析原理（适合面试复习）"
  output_dir: "./sql-ast-visualizer"  # 生成代码的输出目录

# 核心文件结构（极简设计，仅保留必要文件）
files:
  - name: "input.sql"
    type: "text"
    content: |
      -- 示例 SQL，用户可修改
      SELECT id, name FROM users WHERE age > 18;

  - name: "MySqlLexer.g4"
    type: "antlr-grammar"
    source: "https://raw.githubusercontent.com/antlr/grammars-v4/master/sql/mysql/Positive-Technologies/MySqlLexer.g4"  # 复用社区成熟语法规则

  - name: "MySqlParser.g4"
    type: "antlr-grammar"
    source: "https://raw.githubusercontent.com/antlr/grammars-v4/master/sql/mysql/Positive-Technologies/MySqlParser.g4"  # 复用社区成熟语法规则

  - name: "parse.py"
    type: "python"
    purpose: "解析 input.sql，生成 AST 数据（ast.json）"
    requirements:
      - 依赖 antlr4-python3-runtime，通过 pip 安装
      - 读取 input.sql 中的 SQL 语句
      - 调用 ANTLR 生成的解析器进行词法/语法分析
      - 将解析得到的 ParseTree 转换为简化的 JSON 结构（包含节点类型、值、子节点）
      - 输出结果到 ast.json

  - name: "visualize.html"
    type: "html"
    purpose: "加载 ast.json，用 D3.js 可视化语法树"
    requirements:
      - 纯 HTML + JavaScript，无前端框架依赖
      - 内置 D3.js CDN 引用（无需本地安装）
      - 自动读取同目录下的 ast.json
      - 用树形结构展示 AST，支持：
        - 节点点击显示详情（类型、值、在 SQL 中的位置）
        - 鼠标悬停高亮节点及其父/子节点
        - 适配不同屏幕尺寸的响应式布局

  - name: "README.md"
    type: "markdown"
    content: |
      # SQL 语法树可视化工具（轻量版）
      
      本地快速查看 MySQL 语句的语法树结构，辅助理解 SQL 解析原理。
      
      ## 快速使用
      1. 安装依赖：`pip install antlr4-python3-runtime`
      2. 在 input.sql 中写入 SQL 语句
      3. 运行 `python parse.py` 生成 ast.json
      4. 用浏览器打开 visualize.html 查看可视化结果

# 技术实现约束（确保轻量性）
constraints:
  - 不使用任何后端服务框架（如 Flask/Django），仅用原生 Python 脚本
  - 不引入前端构建工具（如 Webpack），可视化页面为单文件 HTML
  - AST 转换需简化（忽略解析器内部细节，只保留用户关心的节点类型：关键字、表名、列名、条件等）
  - 兼容 Python 3.8+ 和主流浏览器（Chrome/Firefox/Edge）

# 输出检查清单
checklist:
  - 运行 `python parse.py` 后是否成功生成 ast.json
  - 打开 visualize.html 后是否正确渲染树形结构
  - 节点点击是否能显示详情
  - 示例 SQL（SELECT id, name FROM users WHERE age > 18）是否能正常解析和展示