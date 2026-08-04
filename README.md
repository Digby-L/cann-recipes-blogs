# cann-recipes-docs
本仓库是 **[CANN Recipes Blog](https://gitcode.com/cann/cann-recipes-blogs) 的内容来源仓库**，聚合了从各 recipe 代码仓（infer / train / embodied-ai）迁出的**模型优化文档**与**CANN 原子特性文档**。
> CANN Recipes 技术文档中心 —— 独立于代码仓库的统一文档库

[![Blog](https://img.shields.io/badge/Blog-CANN%20Recipes-orange)](https://gitcode.com/cann/cann-recipes-blogs)   [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)


---

## 🗂️ 内容分类

本仓库独立于代码仓库，是CANN Recipes 技术文档中心，按 **应用场景** 组织文档，对应 blog 的四大领域分类：

| 领域 | 目录 | 内容概要 | 代码仓库 |
|------|------|----------|--------|
| **推理** | [infer/](infer/) | 大语言模型、多模态生成、推荐系统的推理优化文档 | [cann-recipes-infer](https://gitcode.com/cann/cann-recipes-infer) |
| **训练** | [train/](train/) | 预训练、强化学习训练优化文档 | [cann-recipes-train](https://gitcode.com/cann/cann-recipes-train) |
| **具身智能** | [embodied/](embodied/) | 3D视觉、机械臂操作、导航、世界模型优化文档 | [cann-recipes-embodied-ai](https://gitcode.com/cann/cann-recipes-embodied-ai) |
| **CANN 原子特性** | [cann_features/](cann_features/) | NPU graph优化等跨场景公共能力文档 | - |

---

## 📚 样例列表

### 推理优化 (infer/)

#### 大语言模型 (llm/)
- **DeepSeek-R1** - decode/prefill 阶段优化方案
- **DeepSeek-V3.2** - 推理指南 + AscendC/PyPTO/TileLang 算子开发
- **DeepSeek-V4** - 推理优化实践文档 + AscendC/PyPTO/TileLang 算子开发
- **Qwen 系列** - Qwen3-MoE、Qwen3-Next 等模型优化
- **Kimi-K2-Thinking** - 推理部署指南
- **LongCat-Flash** - 长文本模型优化
- **GPT-OSS** - 开源 GPT 模型优化

#### 多模态生成 (multimodal/)
- **Hunyuan-Image 3.0** - 混元图像生成优化
- **Hunyuan-Video** - 混元视频生成优化
- **WAN 2.2** - 图生视频优化
- **SANA-Video** - 视频生成优化

#### 推荐系统 (recommendation/)
- **HSTU** - 推荐模型优化

---

### 训练优化 (train/)

#### 预训练 (pretrain/)
- **DeepSeek-V3.2** - 大模型预训练优化方案

#### 强化学习 (rl/)
- **DeepSeek-RL** - 强化学习训练优化
- **Qwen3-235B** - 长序列 RL 训练优化（32k context）
- **SAM Decoding** - 推测解码优化

---

### 具身智能 (embodied/)

#### 3D 视觉 (3d_vision/)
- **Hunyuan3D** - 3D 生成模型优化
- **Gaussian Splatting** - 高斯泼溅渲染优化（alpha blending、culling、load balance、精确相交）
- **VGGT** - 视觉几何模型优化与精度评估

#### 机械臂操作 (manipulation/)
- **GR00T N1.6** - 机械臂控制模型优化
- **Pi0** - 策略模型推理优化（Torch/OM 两种部署方式）

#### 导航 (navigation/)
- **Alpamayo-R1** - 机器人导航模型优化

#### 世界模型 (world_model/)
- **Cosmos** - 世界模型优化

---

### CANN 原子特性 (cann_features/)

- **NPU Graph Optimization** - NPU 计算图优化原理与实践
- **其他原子特性** - 算子融合、内存优化等（待补充）

> CANN 原子特性文档直接平铺在 `cann_features/` 目录下，无子分类层级。

---

## 🚀 如何贡献文档

### 1. 添加新文档

按照四级目录结构放置文档：

```bash
# 示例1：添加新的 LLM 优化文档
cann-recipes-docs/
└── infer/
    └── llm/
        └── your_model/              # 模型名（小写+下划线）
            ├── your_model_optimization.md
            └── figures/             # 文档配图
                ├── arch.png
                └── perf.png

# 示例2：添加 CANN 原子特性文档
cann-recipes-docs/   #（在blog中设计成特性矩阵，然后再点入每个文件中）
└── cann_features/
    ├── npu_graph_optimization.md    # 直接平铺，无子目录
    └── figures/
        └── graph_opt.png
```

### 2. 命名规范

- **目录名**：全部小写，单词用下划线 `_` 分隔
  - ✅ `deepseek_v3_2_exp`
  - ❌ `DeepSeek-V3.2-Exp`
  
- **文件名**：`{model}_{scenario}_optimization.md` 或 `{model}_{scenario}_guide.md`
  - ✅ `qwen3_moe_optimization.md`
  - ❌ `README.md`（禁止使用，无法直观展示内容）

- **图片**：放在同级 `figures/` 目录，文档内用相对路径引用
  ```markdown
  ![架构图](figures/arch.png)
  ```

### 3. 自动上线流程

```
提交文档到本仓 → 触发 CI → blog 自动重建 → 新文档上线
```

无需改动 blog 代码，本仓库会自动扫描新增文档并生成导航。


> 注：推理、训练文档迁移进行中，统计数据持续更新。

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

## ❓ FAQ

**Q: 原代码仓的文档链接会失效吗？**  
A: 不会。代码仓会保留 stub 文件，指向 blog 新地址。

**Q: 我需要修改某篇文档，改哪里？**  
A: 直接在本仓对应目录修改并提交，blog 会自动同步。

**Q: 框架设计、使用指南类文档在哪？**  
A: 保留在各代码仓的 `docs/design`、`docs/common` 等目录，因为它们需要代码上下文才能理解。

---
