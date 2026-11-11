# modules/score_calculator.py

class ScoreCalculator:

    """Calculate Gaia Score (0-100) - Enhanced for Indian context"""

 

    def __init__(self):

        # Domain weights for comprehensive sustainability assessment

        self.weights = {

            'emissions': 0.25,      # Carbon footprint

            'water': 0.20,          # Water conservation

            'waste': 0.15,          # Waste management

            'energy': 0.15,         # Renewable energy

            'compliance': 0.15,     # Regulatory compliance

            'social': 0.10          # Community impact (tree plantation, etc.)

        }

 

        # Industry-specific benchmarks (tons/ML/year)

        self.industry_benchmarks = {

            'textile': {'co2_good': 500, 'co2_critical': 5000, 'water_good': 10000, 'water_critical': 50000},

            'chemical': {'co2_good': 1000, 'co2_critical': 10000, 'water_good': 20000, 'water_critical': 100000},

            'steel': {'co2_good': 5000, 'co2_critical': 50000, 'water_good': 5000, 'water_critical': 30000},

            'pharma': {'co2_good': 200, 'co2_critical': 2000, 'water_good': 5000, 'water_critical': 25000},

            'automobile': {'co2_good': 1000, 'co2_critical': 8000, 'water_good': 10000, 'water_critical': 40000},

            'default': {'co2_good': 1000, 'co2_critical': 10000, 'water_good': 10000, 'water_critical': 50000}

        }

 

    def _calculate_metric_score(self, value, good_threshold, critical_threshold, lower_is_better=True):

        """

        Convert metric value to score (0-100)

 

        Args:

            value: The metric value

            good_threshold: Value considered "good" (score 80)

            critical_threshold: Value considered "critical" (score 20)

            lower_is_better: True if lower values are better (emissions, water)

        """

        if value is None:

            return 50  # Default if no data

 

        if lower_is_better:

            if value <= good_threshold:

                return 90

            elif value >= critical_threshold:

                return 20

            else:

                # Linear interpolation

                range_val = critical_threshold - good_threshold

                if range_val > 0:

                    score = 90 - ((value - good_threshold) / range_val) * 70

                    return max(20, min(90, score))

                return 55

        else:

            # Higher is better (renewable percentage)

            if value >= good_threshold:

                return 90

            elif value <= critical_threshold:

                return 20

            else:

                range_val = good_threshold - critical_threshold

                if range_val > 0:

                    score = 20 + ((value - critical_threshold) / range_val) * 70

                    return max(20, min(90, score))

                return 55

 

    def _get_industry_benchmarks(self, industry=None):

        """Get benchmarks for specific industry"""

        if industry and industry.lower() in self.industry_benchmarks:

            return self.industry_benchmarks[industry.lower()]

        return self.industry_benchmarks['default']

 

    def calculate_domain_scores(self, metrics, industry=None):

        """Calculate individual domain scores"""

        benchmarks = self._get_industry_benchmarks(industry)

 

        scores = {

            'emissions': 50,

            'water': 50,

            'waste': 50,

            'energy': 50,

            'compliance': 50,

            'social': 50

        }

 

        # 1. Emissions Score (CO2)

        co2_value = metrics.get('co2_emissions')

        if co2_value is not None:

            scores['emissions'] = self._calculate_metric_score(

                co2_value,

                benchmarks['co2_good'],

                benchmarks['co2_critical'],

                lower_is_better=True

            )

 

        # 2. Water Score

        water_value = metrics.get('water_usage')

        if water_value is not None:

            scores['water'] = self._calculate_metric_score(

                water_value,

                benchmarks['water_good'],

                benchmarks['water_critical'],

                lower_is_better=True

            )

 

        # 3. Waste Score

        waste_value = metrics.get('waste_generated')

        if waste_value is not None:

            # Waste benchmark: <50 tons = good, >500 tons = critical

            scores['waste'] = self._calculate_metric_score(

                waste_value,

                good_threshold=50,

                critical_threshold=500,

                lower_is_better=True

            )

 

        # 4. Energy/Renewable Score

        renewable_value = metrics.get('renewable_percent')

        if renewable_value is not None:

            # Higher renewable = better

            scores['energy'] = self._calculate_metric_score(

                renewable_value,

                good_threshold=50,      # 50% renewable = good

                critical_threshold=10,   # 10% renewable = critical

                lower_is_better=False

            )

 

        # 5. Compliance Score (from sentiment)

        sentiment = metrics.get('sentiment_score', 50)

        if sentiment is not None:

            scores['compliance'] = sentiment

 

        # 6. Social Score (tree plantation, community impact)

        tree_value = metrics.get('tree_planted')

        if tree_value is not None:

            if tree_value >= 1000:

                scores['social'] = 95

            elif tree_value >= 500:

                scores['social'] = 85

            elif tree_value >= 100:

                scores['social'] = 70

            elif tree_value >= 50:

                scores['social'] = 55

            else:

                scores['social'] = 40

 

        return scores

 

    def calculate(self, metrics, sentiment_score=50, industry=None):

        """

        Calculate Gaia Score

 

        Args:

            metrics: Dictionary of sustainability metrics

            sentiment_score: Score from text analysis (0-100)

            industry: Industry type for benchmarking

 

        Returns:

            float: Gaia Score (0-100)

        """

        # Add sentiment to metrics

        metrics_with_sentiment = metrics.copy()

        metrics_with_sentiment['sentiment_score'] = sentiment_score

 

        # Calculate domain scores

        domain_scores = self.calculate_domain_scores(metrics_with_sentiment, industry)

 

        # Weighted average

        total_score = 0

        for domain, weight in self.weights.items():

            total_score += domain_scores.get(domain, 50) * weight

 

        # Apply penalty for missing critical data

        missing_critical = 0

        critical_fields = ['co2_emissions', 'water_usage']

        for field in critical_fields:

            if metrics.get(field) is None:

                missing_critical += 1

 

        if missing_critical >= 2:

            total_score *= 0.85  # 15% penalty for missing both

        elif missing_critical >= 1:

            total_score *= 0.95  # 5% penalty for missing one

 

        # Ensure within 0-100 range

        final_score = max(0, min(100, total_score))

 

        return round(final_score, 1)

 

    def get_status(self, score):

        """Get detailed status based on score"""

        if score >= 80:

            return {

                'status': 'EXCELLENT',

                'color': 'green',

                'icon': '🎉',

                'message': 'Excellent sustainability performance. You are a leader in environmental stewardship.',

                'action': 'Maintain current practices and share as case study.',

                'deadline': 'Next review in 12 months',

                'bg_color': '#e8f5e9',

                'border_color': '#4caf50'

            }

        elif score >= 60:

            return {

                'status': 'GOOD',

                'color': 'blue',

                'icon': '👍',

                'message': 'Good performance. Minor improvements recommended to reach excellence.',

                'action': 'Focus on lowest-scoring domains identified in analysis.',

                'deadline': 'Submit improvement plan within 60 days',

                'bg_color': '#e3f2fd',

                'border_color': '#2196f3'

            }

        elif score >= 40:

            return {

                'status': 'POOR',

                'color': 'orange',

                'icon': '⚠️',

                'message': 'Poor performance. Significant improvements required.',

                'action': 'Implement corrective actions. Submit progress report in 30 days.',

                'deadline': 'Compliance required within 60 days',

                'bg_color': '#fff3e0',

                'border_color': '#ff9800'

            }

        else:

            return {

                'status': 'CRITICAL',

                'color': 'red',

                'icon': '🚨',

                'message': 'CRITICAL CONDITION. Severe violations detected.',

                'action': 'IMMEDIATE ACTION REQUIRED. Sealing threat if not addressed within 30 days.',

                'deadline': 'Final warning: 30 days',

                'bg_color': '#ffebee',

                'border_color': '#f44336'

            }

 

    def get_domain_breakdown(self, metrics, industry=None):

        """Get detailed breakdown by domain"""

        metrics_with_sentiment = metrics.copy()

        metrics_with_sentiment['sentiment_score'] = 70  # Default for breakdown

 

        domain_scores = self.calculate_domain_scores(metrics_with_sentiment, industry)

 

        breakdown = []

        for domain, score in domain_scores.items():

            if score < 40:

                status = "🔴 CRITICAL"

            elif score < 60:

                status = "🟡 NEEDS IMPROVEMENT"

            elif score < 80:

                status = "🟢 GOOD"

            else:

                status = "🌟 EXCELLENT"

 

            breakdown.append({

                'domain': domain.upper(),

                'score': round(score, 1),

                'status': status,

                'weight': self.weights.get(domain, 0) * 100

            })

 

        return breakdown

 

    def get_recommendation_priority(self, domain_scores):

        """Get prioritized recommendations based on domain scores"""

        priorities = []

 

        for domain, score in domain_scores.items():

            if score < 40:

                priority = "HIGH"

                urgency = "Immediate action required"

            elif score < 60:

                priority = "MEDIUM"

                urgency = "Address within 60 days"

            else:

                priority = "LOW"

                urgency = "Monitor and maintain"

 

            priorities.append({

                'domain': domain.upper(),

                'score': round(score, 1),

                'priority': priority,

                'urgency': urgency

            })

 

        # Sort by score (lowest first)

        priorities.sort(key=lambda x: x['score'])

 

        return priorities

# Create instance

score_calculator = ScoreCalculator()
