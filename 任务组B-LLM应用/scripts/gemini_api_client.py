import os
import json
import time
import random
import re
from typing import List, Dict, Any, Optional


class GeminiAPIClient:
    """A simple client for Gemini API (simulated for now)."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.use_simulation = True  # Use simulation mode by default
        
    def _detect_language(self, text: str) -> str:
        """Detect language from text."""
        # Simple heuristic for language detection
        arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        german_chars = re.findall(r'[äöüßÄÖÜ]', text)
        persian_chars = re.findall(r'[\u0600-\u06FF\u0750-\u077F]', text)
        french_chars = re.findall(r'[éèêëàâôûùçÉÈÊËÀÂÔÛÙÇ]', text)
        hebrew_chars = re.findall(r'[\u0590-\u05FF]', text)
        hindi_chars = re.findall(r'[\u0900-\u097F]', text)
        
        # Count characters
        counts = {
            '阿拉伯语': len(arabic_chars),
            '中文': len(chinese_chars),
            '德语': len(german_chars),
            '英语': 0,  # Default
            '波斯语': len(persian_chars),
            '法语': len(french_chars),
            '希伯来语': len(hebrew_chars),
            '印地语': len(hindi_chars)
        }
        
        # Determine language
        max_lang = max(counts.items(), key=lambda x: x[1])
        if max_lang[1] > 0:
            return max_lang[0]
        return '英语'
        
    def _simulate_style_classification(self, text: str) -> Dict[str, Any]:
        """Simulate Gemini API response for style classification."""
        # Simple heuristic-based classification for demonstration
        text_lower = text.lower()
        
        # Check for news indicators
        news_indicators = ['记者', '报道', '消息', '今天', '昨日', '据悉', '据了解', '新华社', '人民日报', '新闻', '发布']
        # Check for novel indicators
        novel_indicators = ['他', '她', '说', '道', '想', '心里', '脸上', '眼睛', '微笑', '突然', '忽然', '然后', '接着']
        # Check for classical Chinese indicators
        classical_indicators = ['之', '乎', '者', '也', '矣', '焉', '哉', '岂', '其', '然', '虽', '而']
        # Check for literature indicators
        literature_indicators = ['作者', '著', '作品', '文学', '小说', '故事', '情节', '人物', '时代']
        
        news_score = sum(1 for indicator in news_indicators if indicator in text)
        novel_score = sum(1 for indicator in novel_indicators if indicator in text)
        classical_score = sum(1 for indicator in classical_indicators if indicator in text)
        literature_score = sum(1 for indicator in literature_indicators if indicator in text)
        
        # Also detect language
        detected_language = self._detect_language(text)
        
        # Determine predicted style - prioritize Chinese styles if Chinese chars present
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        
        if len(chinese_chars) > 0:
            # Chinese text - choose among Chinese styles
            scores = {
                '新闻': news_score,
                '小说': novel_score,
                '古文': classical_score,
                '名著': literature_score
            }
            # Also check for dishu-like text
            if len(text) < 300 and len(text.split()) < 50:
                scores['地书风格'] = 0.8
            
            # Find the highest score
            predicted_style = max(scores.items(), key=lambda x: x[1])[0]
            max_score = scores[predicted_style]
            confidence = 0.5 + (max_score / (max_score + 1)) * 0.4
        else:
            # Non-Chinese text - use detected language
            predicted_style = detected_language
            confidence = 0.6 + random.random() * 0.35
        
        # Also check for Dishu-like text (shorter, more symbolic)
        if len(text) < 200 and len(text.split()) < 30 and len(chinese_chars) > 0:
            predicted_style = '地书风格'
            confidence = 0.7
        
        return {
            'predicted_style': predicted_style,
            'confidence': confidence,
            'style_scores': {
                '新闻': news_score,
                '小说': novel_score,
                '古文': classical_score,
                '名著': literature_score,
                '阿拉伯语': 0.1 if detected_language != '阿拉伯语' else 0.9,
                '中文': 0.1 if detected_language != '中文' else 0.9,
                '德语': 0.1 if detected_language != '德语' else 0.9,
                '英语': 0.1 if detected_language != '英语' else 0.9,
                '波斯语': 0.1 if detected_language != '波斯语' else 0.9,
                '法语': 0.1 if detected_language != '法语' else 0.9,
                '希伯来语': 0.1 if detected_language != '希伯来语' else 0.9,
                '印地语': 0.1 if detected_language != '印地语' else 0.9,
                '地书风格': 0.1
            },
            'reasoning': f"基于文本特征的模拟分类结果。检测到的语言: {detected_language}, 特征数: 新闻={news_score}, 小说={novel_score}, 古文={classical_score}, 名著={literature_score}",
            'is_simulation': True
        }
    
    def _simulate_style_analysis(self, text: str) -> Dict[str, Any]:
        """Simulate Gemini API response for detailed style analysis."""
        sentences = [s.strip() for s in re.split(r'[。！？.!?]', text) if s.strip()]
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        
        return {
            'formality_score': random.uniform(0.3, 0.8),
            'emotional_intensity': random.uniform(0.2, 0.9),
            'complexity_score': min(1.0, avg_sentence_length / 50),
            'key_features': [
                '句子结构',
                '词汇选择',
                '语气语调'
            ],
            'style_description': '这是一段模拟的语体风格分析结果。',
            'is_simulation': True
        }
    
    def classify_style(self, text: str, style_categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Classify the style of a given text."""
        if style_categories is None:
            style_categories = ['新闻', '小说', '古文', '名著', '阿拉伯语', '中文', '德语', '英语', '波斯语', '法语', '希伯来语', '印地语', '地书风格', '其他']
        
        if self.use_simulation:
            return self._simulate_style_classification(text)
        
        # Real API call would go here
        raise NotImplementedError("Real API integration requires Gemini API key.")
    
    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Perform detailed style analysis on text."""
        if self.use_simulation:
            return self._simulate_style_analysis(text)
        
        # Real API call would go here
        raise NotImplementedError("Real API integration requires Gemini API key.")


def build_style_classification_prompt(text: str, categories: List[str]) -> str:
    """Build a prompt for style classification."""
    prompt = f"""请将以下文本分类为以下风格之一：{', '.join(categories)}

文本内容：
{text}

请以JSON格式返回结果，包含以下字段：
- predicted_style: 预测的风格类别
- confidence: 置信度（0-1之间的浮点数）
- reasoning: 简要说明分类理由
"""
    return prompt


def build_style_analysis_prompt(text: str) -> str:
    """Build a prompt for detailed style analysis."""
    prompt = f"""请对以下文本进行详细的语体风格分析：

文本内容：
{text}

请分析以下方面：
1. 正式程度（0-1）
2. 情感强度（0-1）
3. 语言复杂度（0-1）
4. 主要语体特征

请以JSON格式返回分析结果。
"""
    return prompt


def main():
    """Test the Gemini API client."""
    print("Testing Gemini API client (simulation mode)...")
    
    client = GeminiAPIClient()
    
    # Load some test data
    base_dir = 'd:/_College/NLP/Research'
    data_dir = os.path.join(base_dir, '任务组B-LLM应用', 'data')
    
    # Test with news sample
    news_path = os.path.join(data_dir, 'news_samples.json')
    if os.path.exists(news_path):
        with open(news_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        if news_data:
            first_news = list(news_data.values())[0][:500]  # First 500 chars
            print("\n=== Testing with news text ===")
            print(f"Text snippet: {first_news[:100]}...")
            result = client.classify_style(first_news)
            print(f"Predicted style: {result['predicted_style']}")
            print(f"Confidence: {result['confidence']:.2f}")
    
    # Test with novel sample
    novel_path = os.path.join(data_dir, 'novel_samples.json')
    if os.path.exists(novel_path):
        with open(novel_path, 'r', encoding='utf-8') as f:
            novel_data = json.load(f)
        if novel_data:
            first_novel = list(novel_data.values())[0][:500]  # First 500 chars
            print("\n=== Testing with novel text ===")
            print(f"Text snippet: {first_novel[:100]}...")
            result = client.classify_style(first_novel)
            print(f"Predicted style: {result['predicted_style']}")
            print(f"Confidence: {result['confidence']:.2f}")
    
    # Test with classical sample
    classical_path = os.path.join(data_dir, 'classical_samples.json')
    if os.path.exists(classical_path):
        with open(classical_path, 'r', encoding='utf-8') as f:
            classical_data = json.load(f)
        if classical_data:
            first_classical = list(classical_data.values())[0][:500]  # First 500 chars
            print("\n=== Testing with classical Chinese text ===")
            print(f"Text snippet: {first_classical[:100]}...")
            result = client.classify_style(first_classical)
            print(f"Predicted style: {result['predicted_style']}")
            print(f"Confidence: {result['confidence']:.2f}")
    
    # Test with Dishu glosses
    dishu_path = os.path.join(data_dir, 'dishu_samples.json')
    if os.path.exists(dishu_path):
        with open(dishu_path, 'r', encoding='utf-8') as f:
            dishu_data = json.load(f)
        if dishu_data:
            first_dishu = ' '.join(dishu_data[:10])  # First 10 glosses
            print("\n=== Testing with Dishu glosses ===")
            print(f"Text snippet: {first_dishu[:100]}...")
            result = client.classify_style(first_dishu)
            print(f"Predicted style: {result['predicted_style']}")
            print(f"Confidence: {result['confidence']:.2f}")


if __name__ == "__main__":
    main()
