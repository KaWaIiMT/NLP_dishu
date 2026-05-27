数字标注是类似这种格式的json文件：{
    "project": "《地书》图形语言 vs 自然语言：计算语言学与自然语言处理多层标注配置",
    "config_snapshot": {
      "project": "《地书》图形语言 vs 自然语言：计算语言学与自然语言处理多层标注配置",
      "version": "dishu_cl_nlp_full_v2",
      "tasks": [
        {
          "task_id": "literal_gloss",
          "task_name": "[Text] 字面对应词 / Literal Gloss",
          "mode": "text",
          "applies_to": "both",
          "placeholder": "输入该图形或图形组最直接、最字面的自然语言对应词或短语",
          "help_text": "记录你一眼看上去最直接想到的词或短语，不必追求上下文最准确，只写“字面上像什么”。例如一个奔跑小人可写“跑步”“逃跑”。这相当于把图形先译成最表层的词。"
        },
        {
          "task_id": "free_translation",
          "task_name": "[Text] 自由翻译 / Free Translation",
          "mode": "text",
          "applies_to": "group",
          "placeholder": "输入该图形组在自然语言中的通顺表达",
          "help_text": "把整个图形组用自然、通顺的话表达出来，不必逐个对应。重点是“整组想说什么”。例如多个图形组合后，可直接写成“他因为害怕而逃走了”。"
        },
        {
          "task_id": "pragmatic_meaning",
          "task_name": "[Text] 语境实际含义 / Pragmatic Meaning",
          "mode": "text",
          "applies_to": "both",
          "placeholder": "输入该图形在当前上下文中的实际表达意图",
          "help_text": "有些图形字面意思和实际想表达的不一样，这里记录“在当前上下文中真正想说什么”。例如笑脸在某处可能不是“开心”，而是“礼貌”或“缓和气氛”。"
        },
        {
          "task_id": "event_description",
          "task_name": "[Text] 事件描述 / Event Description",
          "mode": "text",
          "applies_to": "group",
          "placeholder": "输入该图形组描述的事件或场景",
          "help_text": "把这个图形组当作一个事件或场景来概括：谁在做什么、发生了什么、结果怎样。适合较完整的组合，不要求逐字翻译，而是写成简洁事件描述。"
        },
        {
          "task_id": "context_note",
          "task_name": "[Text] 研究备注 / Annotation Note",
          "mode": "text",
          "applies_to": "both",
          "placeholder": "记录任何难点、歧义、判断依据或特殊现象",
          "help_text": "这里不是正式标注结果，而是补充说明。可记录你为什么这样判断、哪里不确定、是否依赖上下文、是否像某种固定符号等，方便后续复核。"
        },
        {
          "task_id": "semantic_role_core",
          "task_name": "[Single] 核心语义角色 / Core Semantic Role",
          "mode": "single",
          "applies_to": "both",
          "options": [
            "施事 / Agent",
            "受事 / Patient",
            "体验者 / Experiencer",
            "工具 / Instrument",
            "处所 / Location",
            "时间 / Time",
            "方式 / Manner",
            "结果 / Result",
            "核心谓词 / Predicate",
            "无明显语义角色 / None"
          ],
          "help_text": "判断该对象在一个事件里主要扮演什么角色。比如“人”可能是施事，“被打的人”是受事，“跑”本身可看作核心谓词。若它不像事件成分，就选“无明显语义角色”。"
        },，其中有这些类型[Text] 字面对应词 / Literal Gloss
                                                                                                                                                                                                             
  [Text] 自由翻译 / Free Translation
                                                                                                                                                                                                             
  [Text] 语境实际含义 / Pragmatic Meaning
                                                                                                                                                                                                             
  [Text] 事件描述 / Event Description
                                                                                                                                                                                                             
  [Text] 研究备注 / Annotation Note
                                                                                                                                                                                                             
  [Single] 核心语义角色 / Core Semantic Role
                                                                                                                                                                                                             
  [Single] 对中心成分关系 / Dependency to Head
                                                                                                                                                                                                             
  [Single] 与前一组的篇章关系 / Discourse Relation
                                                                                                                                                                                                             
  [Single] 主要言语行为 / Primary Speech Act
                                                                                                                                                                                                             
  [Single] 指称类型 / Reference Type
                                                                                                                                                                                                             
  [Multi] 词性/符号性质 / POS-like Category
                                                                                                                                                                                                             
  [Multi] 类形态特征 / Morphological-like Features
                                                                                                                                                                                                             
  [Multi] 语义基元 / Semantic Primitives
                                                                                                                                                                                                             
  [Multi] 视觉提示特征 / Visual Cues
                                                                                                                                                                                                             
  [Multi] 交际功能 / Communicative Functions
                                                                                                                                                                                                             
  [Multi] 歧义来源 / Sources of Ambiguity
                                                                                                                                                                                                             
  [Multi-Text] 可能词义候选 / WSD Candidates
                                                                                                                                                                                                             
  [Multi-Text] 多种自然语言译法 / Possible Translations
                                                                                                                                                                                                             
  [Multi-Text] 框架/隐喻映射 / Frame or Metaphor Mapping
                                                                                                                                                                                                             
  [Multi-Text] 联想搭配词 / Collocational Associations
                                                                                                                                                                                                             
                                                                                                                                                                                                             
                                                                                                                                                                                                             
  [Multi-Text] 跨语言近似对应 / Cross-linguistic Equivalents
                                                                                                                                                                                                             
  [Scale] 认知-语言学核心量表 / Cognitive-Linguistic Metrics
                                                                                                                                                                                                             
  [Scale] 句法-语义适配度 / Syntactic-Semantic Fitness
                                                                                                                                                                                                             
  [Scale] 标注信心与一致性评估 / Confidence & Consistency，