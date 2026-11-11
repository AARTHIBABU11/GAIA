# modules/fraud_detector.py
import re
import random
from datetime import datetime
from collections import Counter


class FraudDetector:
    """Detect fake environmental reports - Enhanced for Indian context"""

    def __init__(self):
        # Industry benchmarks (Indian context)
        self.industry_benchmarks = {
            'textile': {'co2_range': (500, 5000), 'water_range': (10000, 50000)},
            'chemical': {'co2_range': (1000, 10000), 'water_range': (20000, 100000)},
            'steel': {'co2_range': (5000, 50000), 'water_range': (5000, 30000)},
            'pharma': {'co2_range': (200, 2000), 'water_range': (5000, 25000)},
            'automobile': {'co2_range': (1000, 8000), 'water_range': (10000, 40000)},
            'food_processing': {'co2_range': (200, 3000), 'water_range': (5000, 20000)},
            'power': {'co2_range': (10000, 100000), 'water_range': (10000, 50000)}
        }

        # AI-generated text patterns
        self.ai_patterns = [
            r'\bas an ai\b',
            r'\bas a language model\b',
            r"\bi don't have access\b",
            r'\bbased on my training\b',
            r'\bplease note that\b',
            r'\bit is important to note\b',
            r'\bin conclusion\b',
            r'\bfurthermore\b',
            r'\badditionally\b',
            r'\bhowever\b',
            r'\btherefore\b',
            r'\bhere are some\b',
            r'\bhere is a\b',
            r'\blet me provide\b'
        ]

        # Suspicious generic phrases
        self.generic_phrases = [
            'committed to sustainability',
            'dedicated to environmental protection',
            'strive to reduce',
            'aim to achieve',
            'work towards',
            'in line with our policy',
            'as per guidelines'
        ]

    # --------------------------------------------------
    # Consistency Checks
    # --------------------------------------------------
    def check_consistency(self, metrics):
        red_flags = []

        critical_fields = ['co2_emissions', 'water_usage']
        for field in critical_fields:
            if metrics.get(field) is None:
                red_flags.append(
                    f"⚠️ Missing critical field: {field.replace('_', ' ').title()}")

        co2_value = metrics.get('co2_emissions')
        water_value = metrics.get('water_usage')

        if co2_value is not None:
            if co2_value > 100000:
                red_flags.append(
                    f"⚠️ Extremely high emissions ({co2_value:,.0f} tons) - verify data")
            elif co2_value == 0:
                red_flags.append(
                    "⚠️ Zero emissions reported - unusual for industrial facility")

        if co2_value is not None and water_value is not None:
            if co2_value == 0 and water_value > 0:
                red_flags.append(
                    "⚠️ Zero emissions but water usage present - inconsistent data")

        renewable_value = metrics.get('renewable_percent')
        if co2_value is not None and renewable_value is not None:
            if renewable_value > 50 and co2_value > 5000:
                red_flags.append(
                    f"⚠️ High renewable ({renewable_value}%) but high emissions ({co2_value:,.0f}) - inconsistent")

        return red_flags

    # --------------------------------------------------
    # Industry Benchmark Checks
    # --------------------------------------------------
    def check_industry_benchmarks(self, metrics, industry=None):
        flags = []

        if industry and industry in self.industry_benchmarks:
            benchmarks = self.industry_benchmarks[industry]

            co2_value = metrics.get('co2_emissions')
            if co2_value is not None:
                co2_min, co2_max = benchmarks['co2_range']
                if co2_value < co2_min * 0.5:
                    flags.append(
                        f"⚠️ Unusually low emissions for {industry} industry - verify methodology")
                elif co2_value > co2_max * 1.5:
                    flags.append(
                        f"⚠️ Unusually high emissions for {industry} industry - verify data")

            water_value = metrics.get('water_usage')
            if water_value is not None:
                water_min, water_max = benchmarks['water_range']
                if water_value < water_min * 0.5:
                    flags.append(
                        f"⚠️ Unusually low water usage for {industry} industry")
                elif water_value > water_max * 1.5:
                    flags.append(
                        f"⚠️ Unusually high water usage for {industry} industry")

        return flags

    # --------------------------------------------------
    # Rounding Pattern Detection
    # --------------------------------------------------
    def detect_rounding_patterns(self, text):
        suspicious = []

        numbers = re.findall(r'\b\d+(?:,\d+)?(?:\.\d+)?\b', text)

        if numbers:
            round_numbers = []
            for n in numbers:
                n_clean = n.replace(',', '')
                if n_clean.endswith(('00', '000', '0000')):
                    round_numbers.append(n)

            if round_numbers:
                round_percent = len(round_numbers) / len(numbers) * 100
                if round_percent > 40:
                    suspicious.append(
                        f"⚠️ {len(round_numbers)} round numbers detected ({round_percent:.0f}%) - possible fabricated data")
                elif round_percent > 25:
                    suspicious.append(
                        "⚠️ Unusual number of round numbers detected")

            number_counts = Counter(numbers)
            for num, count in number_counts.items():
                if count > 3 and len(numbers) > 10:
                    suspicious.append(
                        f"⚠️ Number '{num}' repeated {count} times - suspicious")

        return suspicious

    # --------------------------------------------------
    # Template / AI Pattern Detection
    # --------------------------------------------------
    def detect_template_patterns(self, text):
        suspicious = []
        text_lower = text.lower()

        ai_matches = []
        for pattern in self.ai_patterns:
            if re.search(pattern, text_lower):
                ai_matches.append(pattern)

        if len(ai_matches) > 2:
            suspicious.append(
                f"⚠️ AI-generated language patterns detected ({len(ai_matches)} matches)")

        generic_matches = []
        for phrase in self.generic_phrases:
            if phrase in text_lower:
                generic_matches.append(phrase)

        if len(generic_matches) > 3:
            suspicious.append(
                f"⚠️ Too many generic phrases ({len(generic_matches)}) - possible template report")

        sentences = re.split(r'[.!?।]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        unique_sentences = set(sentences)

        if len(sentences) > 5 and len(unique_sentences) < len(sentences) * 0.5:
            suspicious.append(
                f"⚠️ High content repetition ({len(sentences)} sentences, {len(unique_sentences)} unique)")

        return suspicious

    # --------------------------------------------------
    # Unit Consistency
    # --------------------------------------------------
    def detect_inconsistent_units(self, text, metrics):
        suspicious = []
        text_lower = text.lower()

        if metrics.get('co2_emissions') is not None:
            if 'kilograms' in text_lower and metrics['co2_emissions'] > 1000:
                suspicious.append(
                    "⚠️ CO₂ reported in kg but value suggests tons - possible unit confusion")

        if metrics.get('water_usage') is not None:
            if 'liters' in text_lower and metrics['water_usage'] > 10000:
                suspicious.append(
                    "⚠️ Water reported in liters but value suggests million liters - possible unit confusion")

        return suspicious

    # --------------------------------------------------
    # Anomaly Detection
    # --------------------------------------------------
    def detect_anomalous_combinations(self, metrics):
        suspicious = []

        co2 = metrics.get('co2_emissions')
        water = metrics.get('water_usage')
        renewable = metrics.get('renewable_percent')
        waste = metrics.get('waste_generated')

        if co2 is not None and water is not None:
            if co2 < 100 and water > 10000:
                suspicious.append(
                    "⚠️ Extremely low emissions but high water usage")

        if co2 is not None and renewable is not None:
            if renewable > 80 and co2 > 5000:
                suspicious.append(
                    "⚠️ High renewable percentage but still high emissions")

        if co2 is not None and waste is not None:
            if waste == 0 and co2 > 100:
                suspicious.append(
                    "⚠️ Zero waste reported but emissions present")

        return suspicious

    # --------------------------------------------------
    # Main Fraud Detection
    # --------------------------------------------------
    def detect(self, text, metrics, industry=None):
        fraud_score = 0
        reasons = []

        consistency_flags = self.check_consistency(metrics)
        if consistency_flags:
            fraud_score += 0.25
            reasons.extend(consistency_flags)

        if industry:
            benchmark_flags = self.check_industry_benchmarks(metrics, industry)
            if benchmark_flags:
                fraud_score += 0.20
                reasons.extend(benchmark_flags)

        if text:
            rounding_flags = self.detect_rounding_patterns(text)
            if rounding_flags:
                fraud_score += 0.15
                reasons.extend(rounding_flags)

            template_flags = self.detect_template_patterns(text)
            if template_flags:
                fraud_score += 0.20
                reasons.extend(template_flags)

            unit_flags = self.detect_inconsistent_units(text, metrics)
            if unit_flags:
                fraud_score += 0.10
                reasons.extend(unit_flags)

        anomaly_flags = self.detect_anomalous_combinations(metrics)
        if anomaly_flags:
            fraud_score += 0.15
            reasons.extend(anomaly_flags)

        fraud_score = min(fraud_score, 1.0)

        if fraud_score > 0.7:
            severity = "HIGH"
            severity_icon = "🔴"
        elif fraud_score > 0.4:
            severity = "MEDIUM"
            severity_icon = "🟡"
        else:
            severity = "LOW"
            severity_icon = "🟢"

        reasons = list(dict.fromkeys(reasons))

        return {
            'is_fake': fraud_score >= 0.5,
            'fraud_score': round(fraud_score, 2),
            'reasons': reasons if reasons else ["✅ No fraud indicators detected."],
            'severity': severity,
            'severity_icon': severity_icon
        }


# Create instance
fraud_detector = FraudDetector()