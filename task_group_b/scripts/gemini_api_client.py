import os
import json
import time
import random
from typing import List, Dict, Any, Optional


class GeminiAPIClient:
    """A simple client for Gemini API (simulated for now)."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.use_simulation = True  # Use simulation mode by default
        
    def _simulate_style_classification(self, text: str) -> Dict[str, Any]:
        """Simulate Gemini API response for style classification."""
        # Simple heuristic-based classification for demonstration
        text_lower = text.lower()
        
        # Check for news indicators
        news_indicators = ['记者', '报道', '消息', '今天', '昨日', '据悉', '据了解', '新华社', '人民日报']
        # Check for novel indicators
        novel_indicators = ['他', '她', '说', '道', '想', '心里', '脸上', '眼睛', '微笑', '突然', '忽然']
        
        news_score = sum(1 for indicator in news_indicators if indicator in text)
        novel_score = sum(1 for indicator in novel_indicators if indicator in text)
        
        # Determine predicted style
        if news_score > novel_score:
            predicted_style = '新闻'
            confidence = 0.5 + (news_score / (news_score + novel_score + 1)) * 0.5
        elif novel_score > news_score:
            predicted_style = '小说'
            confidence = 0.5 + (novel_score / (news_score + novel_score + 1)) * 0.5
        else:
            # Equal or no indicators, random choice
            predicted_style = random.choice(['新闻', '小说'])
            confidence = 0.5
        
        # Also check for Dishu-like text (shorter, more symbolic)
        if len(text) < 200 and len(text.split()) < 30:
            dishu_confidence = 0.4
        else:
            dishu_confidence = 0.2
        
        return {
            'predicted_style': predicted_style,
            'confidence': confidence,
            'style_scores': {
                '新闻': news_score,
                '小说': novel_score,
                '地书风格': dishu_confidence
            },
            'reasoning': f"基于文本特征的模拟分类结果。新闻特征数: {news_score}, 小说特征数: {novel_score}",
            'is_simulation': True
        }
    
    def _simulate_style_analysis(self, text: str) -> Dict[str, Any]:
        """Simulate Gemini API response for detailed style analysis."""
        sentences = [s.strip() for s in text.split('。') if s.strip()]
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
            style_categories = ['新闻', '小说', '地书风格', '其他']
        
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
    data_dir = os.path.join(base_dir, 'task_group_b', 'data')
    
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
    
    # Test with Dishu glosses
    dishu_path = os.path.join(data_dir, 'dishu_glosses.json')
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
