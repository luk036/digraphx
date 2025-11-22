# digraphx 项目上下文

## 项目概述

`digraphx` 是一个用 Python 编写的有向图（Directed Graph）优化库，专注于网络优化问题。该项目基于 PyScaffold 4.5 创建，旨在提供一个轻量级且高效的有向图操作和分析工具。

主要特性包括：
- 负环检测（Negative Cycle Detection）
- 最小环比率计算（Minimum Cycle Ratio Calculation）
- 参数化优化算法
- 高效的图数据结构实现（TinyDiGraph）

## 依赖关系

- [luk036/mywheel](https://github.com/luk036/mywheel) - 自定义数据结构库
- networkx - 图论算法库
- decorator
- numpy

## 核心模块

### 1. TinyDiGraph (`tiny_digraph.py`)
一个轻量级的有向图实现，优化了性能和内存效率。通过继承自 NetworkX 的 DiGraph 类，并使用自定义的 MapAdapter 作为底层存储结构。

### 2. 负环检测 (`neg_cycle.py`)
实现了基于 Howard 方法的负环检测算法，使用 Bellman-Ford 算法进行边的松弛操作。

### 3. 最小环比率求解器 (`min_cycle_ratio.py`)
提供最小环比率问题的求解，使用参数化方法结合最大参数化求解器。

### 4. 其他模块
- `min_parmetric_q.py` - 参数化 Q 优化
- `neg_cycle_q.py` - 负环 Q 检测
- `parametric.py` - 参数化算法接口

## 构建和测试

该项目使用标准的 Python 包管理工具：

安装依赖：
```bash
pip install -r requirements/default.txt
pip install -r requirements/test.txt
```

运行测试：
```bash
pytest tests/
```

代码覆盖率测试：
```bash
pytest --cov digraphx --cov-report term-missing
```

## 开发规范

- 代码使用 Python 3.9+ 编写
- 遵循 PEP 8 代码风格
- 使用 type hints 提供类型信息
- 测试使用 pytest 框架

## 项目结构

```
src/digraphx/ - 源代码目录
├── __init__.py
├── tiny_digraph.py - 轻量级有向图实现
├── neg_cycle.py - 负环检测算法
├── min_cycle_ratio.py - 最小环比率求解器
├── parametric.py - 参数化算法接口
├── neg_cycle_q.py - 负环 Q 检测
├── min_parmetric_q.py - 参数化 Q 优化
└── py.typed - 类型提示标记文件

tests/ - 测试目录
├── test_cycle_ratio.py - 环比率相关测试
├── test_neg_cycle.py - 负环检测测试
├── test_tiny_digraph.py - TinyDiGraph 测试
└── 其他测试文件
```

## 使用示例

从 TinyDiGraph 的文档可以看出，基本用法如下：

```python
from digraphx.tiny_digraph import TinyDiGraph

gr = TinyDiGraph()
gr.init_nodes(1000)  # 初始化 1000 个节点
gr.add_edge(2, 1)    # 添加从节点 2 到节点 1 的边
```

## 项目状态

根据 setup.cfg 中的分类器，该项目处于 Beta 开发阶段，使用 MIT 许可证。

## 备注

- 该项目专注于网络优化算法，特别是负环检测和最小环比率问题
- 使用了自定义的高效数据结构以优化性能
- 与 NetworkX 集成，利用其丰富的图算法功能