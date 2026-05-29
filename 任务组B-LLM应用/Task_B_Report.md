# 任务组B：地书与自然语言的语体特征分析报告

**生成时间**: 2026-05-29 02:48:02

---

## 1. 执行摘要

本报告总结了任务组B的工作，包括：
- 自然语言数据（新闻、小说）与地书数据的加载和采样
- 多维度语体特征提取
- 基于Gemini API的零样本风格分类（当前为模拟模式）

---

## 2. 数据概览

### 2.1 数据集统计

| 语料类型 | 样本数 | 总字符数 | 来源 |
|---------|--------|----------|------|
| 新闻 | 3 | ~30,000 | THUcNews |
| 小说 | 9 | ~450,000 | 小说数据集 |
| 地书注释 | 1 | ~28,000 | 地书标注数据 |

---

## 3. 语体特征分析

### 3.1 关键语体特征对比

| corpus | num_sentences | avg_sentence_length_chars | std_sentence_length_chars | median_sentence_length_chars | min_sentence_length_chars | max_sentence_length_chars | avg_sentence_length_words | char_count | word_count | unique_words | ttr | rttr | zipf_slope | zipf_r_squared | entropy | normalized_entropy | lexical_density | punct_period_count | punct_period_ratio | punct_exclamation_count | punct_exclamation_ratio | punct_question_count | punct_question_ratio | punct_comma_count | punct_comma_ratio | punct_semicolon_count | punct_semicolon_ratio | punct_colon_count | punct_colon_ratio | punct_quote_count | punct_quote_ratio | punct_dash_count | punct_dash_ratio | punct_ellipsis_count | punct_ellipsis_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dishu | 837.000 | 33.803 | 60.703 | 24.000 | 4.000 | 1599.000 | 4.508 | 29993.000 | 3773.000 | 2485.000 | 0.659 | 40.456 | -0.426 | 0.854 | 10.815 | 0.959 | 0.083 | 797.000 | 0.027 | 39.000 | 0.001 | 3.000 | 0.000 | 1360.000 | 0.045 | 52.000 | 0.002 | 55.000 | 0.002 | 24.000 | 0.001 | 8.000 | 0.000 | 69.000 | 0.002 |
| news | 214.333 | 47.021 | 33.482 | 37.500 | 1.667 | 195.333 | 4.998 | 10000.000 | 1050.000 | 881.667 | 0.844 | 27.243 | -0.241 | 0.587 | 9.573 | 0.979 | 0.088 | 186.333 | 0.019 | 4.667 | 0.000 | 22.333 | 0.002 | 420.667 | 0.042 | 3.667 | 0.000 | 47.000 | 0.005 | 0.000 | 0.000 | 19.000 | 0.002 | 4.667 | 0.000 |
| novel | 1720.111 | 29.902 | 22.119 | 24.667 | 1.111 | 174.556 | 3.131 | 50000.000 | 4988.000 | 4682.222 | 0.939 | 66.268 | -0.110 | 0.346 | 12.087 | 0.992 | 0.094 | 1213.333 | 0.024 | 245.778 | 0.005 | 301.000 | 0.006 | 2733.889 | 0.055 | 4.444 | 0.000 | 225.444 | 0.005 | 355.889 | 0.007 | 91.444 | 0.002 | 349.000 | 0.007 |


### 3.2 主要发现

**新闻语料特征**：
- 平均句长: 47.0 字符
- 平均类型-标记比(TTR): 0.844
- 平均词汇密度: 0.088

**小说语料特征**：
- 平均句长: 29.9 字符
- 平均类型-标记比(TTR): 0.939
- 平均词汇密度: 0.094

**地书语料特征**：
- 平均句长: 33.8 字符
- 平均类型-标记比(TTR): 0.659
- 平均词汇密度: 0.083

---

## 4. 零样本风格分类结果


### 4.3 详细分类结果

| corpus | true_style | predicted_style | confidence |
| --- | --- | --- | --- |
| news | 新闻 | 小说 | 0.929 |
| news | 新闻 | 小说 | 0.750 |
| news | 新闻 | 小说 | 0.875 |
| novel | 小说 | 小说 | 0.917 |
| novel | 小说 | 小说 | 0.929 |
| novel | 小说 | 小说 | 0.800 |
| dishu | 地书风格 | 小说 | 0.500 |


---

## 5. 方法说明

### 5.1 特征提取方法

我们从文本中提取了以下类型的语体特征：

1. **句子层面特征**：句子数量、平均句长、句长标准差等
2. **词汇层面特征**：词汇量、类型-标记比(TTR)、Zipf定律拟合参数、信息熵等
3. **标点符号特征**：各类型标点的使用频率

### 5.2 Gemini API集成

当前实现使用模拟模式，实际应用时需要：
1. 配置有效的Gemini API密钥
2. 使用真实的API调用替换模拟方法
3. 优化Prompt设计以提高分类准确率

---

## 6. 结论与建议

1. **语体差异**：新闻、小说和地书注释在语体特征上存在可观测的差异
2. **API集成**：当前使用模拟模式，未来可集成真实的Gemini API以获得更好的分类效果
3. **数据扩展**：可考虑增加更多语料类型（如古文、维基百科等）进行对比分析
4. **模型训练**：未来可考虑基于提取的特征训练专用的风格分类模型

---

## 附录

### 目录结构

```
task_group_b/
├── data/
│   ├── news_samples.json
│   ├── novel_samples.json
│   └── dishu_glosses.json
├── results/
│   ├── style_features.csv
│   ├── style_feature_summary.csv
│   ├── zero_shot_classification_results.csv
│   └── classification_summary.json
└── scripts/
    ├── data_loader.py
    ├── style_feature_extractor.py
    ├── gemini_api_client.py
    ├── zero_shot_classification.py
    └── generate_report.py
```
