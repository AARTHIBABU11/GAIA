# modules/text_analyzer.py

import re
import streamlit as st  # pyright: ignore[reportMissingImports]
from transformers import pipeline  # pyright: ignore[reportMissingImports]


class TextAnalyzer:
    """Analyze sustainability reports using DistilBERT - Green AI optimized"""

    def __init__(self):
        self.classifier = None
        self.model_loaded = False
        self._load_model()

    def _load_model(self):
        """Load lightweight DistilBERT model (66MB) - CPU efficient"""
        try:
            with st.spinner("📝 Loading DistilBERT model (66MB)..."):
                self.classifier = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1
                )
                self.model_loaded = True
                print("[OK] DistilBERT model loaded successfully")
        except Exception as e:
            print(f"[WARN] Model load failed: {e}")
            print("Text analysis will use keyword-based fallback")
            self.classifier = None
            self.model_loaded = False

    # ✅ FIXED: moved outside _load_model
    def analyze(self, text):
        """Main analysis function combining metrics + sentiment"""

        metrics = self.extract_metrics(text)
        sentiment = self.analyze_sentiment(text)

        score = 50

        if metrics['renewable_percent']:
            score += min(metrics['renewable_percent'] * 0.3, 20)

        if metrics['co2_emissions']:
            if metrics['co2_emissions'] < 1000:
                score += 10
            else:
                score -= 10

        if metrics['waste_generated']:
            if metrics['waste_generated'] < 500:
                score += 5
            else:
                score -= 5

        if sentiment['label'] == 'POSITIVE':
            score += 10
        elif sentiment['label'] == 'NEGATIVE':
            score -= 10

        score = max(0, min(100, int(score)))

        suggestions = []

        if not metrics['renewable_percent']:
            suggestions.append("Increase renewable energy usage")

        if metrics['co2_emissions'] and metrics['co2_emissions'] > 1000:
            suggestions.append("Reduce carbon emissions urgently")

        if metrics['waste_generated'] and metrics['waste_generated'] > 500:
            suggestions.append("Improve waste management system")

        if sentiment['label'] == 'NEGATIVE':
            suggestions.append("Overall sustainability performance needs improvement")

        if not suggestions:
            suggestions.append("Maintain current sustainability practices")

        return {
            "gaia_score": score,
            "metrics": metrics,
            "sentiment": sentiment,
            "suggestions": suggestions
        }

    # ⚠️ Make sure this exists (you accidentally removed earlier)
    def extract_metrics(self, text):
        text_lower = text.lower()

        metrics = {
            'co2_emissions': None,
            'water_usage': None,
            'waste_generated': None,
            'renewable_percent': None,
            'energy_consumption': None,
            'effluent_treated': None,
            'tree_planted': None
        }

        co2_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:tons?|tonnes?)\s*(?:co2|carbon)', text_lower)
        if co2_match:
            metrics['co2_emissions'] = float(co2_match.group(1).replace(',', ''))

        renewable_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text_lower)
        if renewable_match:
            metrics['renewable_percent'] = float(renewable_match.group(1))

        waste_match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:tons?|tonnes?)\s*waste', text_lower)
        if waste_match:
            metrics['waste_generated'] = float(waste_match.group(1).replace(',', ''))

        return metrics

    def analyze_sentiment(self, text):
        if self.classifier is None:
            return self._keyword_sentiment(text)

        sample = text[:500]

        try:
            result = self.classifier(sample)[0]
            return {'score': result['score'], 'label': result['label']}
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return self._keyword_sentiment(text)

    def _keyword_sentiment(self, text):
        text_lower = text.lower()

        positive_keywords = ['reduced', 'improved', 'green', 'sustainable']
        negative_keywords = ['pollution', 'waste', 'violation']

        pos = sum(1 for kw in positive_keywords if kw in text_lower)
        neg = sum(1 for kw in negative_keywords if kw in text_lower)

        if pos + neg == 0:
            return {'score': 0.5, 'label': 'NEUTRAL'}

        score = pos / (pos + neg)
        label = 'POSITIVE' if score > 0.5 else 'NEGATIVE'

        return {'score': score, 'label': label}

    def is_model_loaded(self):
        return self.model_loaded


# Create instance
text_analyzer = TextAnalyzer()