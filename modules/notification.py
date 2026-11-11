from datetime import datetime, timedelta
import streamlit as st # type: ignore

class NotificationSystem:
    """Send automated notifications with multilingual support"""

    def __init__(self):
        self.sent_notifications = []
        self.pending_reminders = []

    def _translate_notification(self, text, language='en'):
        """Translate notification to regional languages (simplified)"""
        if language == 'hi':
            return text + "\n\n[हिंदी में जानकारी के लिए कृपया अधिकारी से संपर्क करें]"
        elif language == 'ta':
            return text + "\n\n[தகவல்கள் தமிழில்: அதிகாரியை தொடர்பு கொள்ளவும்]"
        return text

    def generate_warning(self, factory_name, score, suggestions, is_fake=False, language='en'):
        """Generate warning message with severity levels"""

        if score >= 80:
            severity = "EXCELLENT"
        elif score >= 60:
            severity = "GOOD"
        elif score >= 40:
            severity = "POOR"
        else:
            severity = "CRITICAL"

        # FRAUD ALERT
        if is_fake:
            notification = {
                'type': 'FRAUD_ALERT',
                'severity': 'HIGH',
                'icon': '🚨',
                'subject': f'URGENT: Fake Report Detected - {factory_name}',
                'body': f"""
🚨 FRAUD ALERT - {factory_name}

Gaia Score: {score}/100 (FLAGGED)
Severity: HIGH
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Issues Detected:
{chr(10).join(['- ' + s for s in suggestions[:5]])}

Submit Corrected Report within 48 hours.
Provide documents within 7 days.
""",
                'deadline_days': 7,
                'deadline_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'action_required': True,
                'escalation_level': 1
            }

        # CRITICAL WARNING
        elif score < 40:
            notification = {
                'type': 'SEAL_WARNING',
                'severity': 'CRITICAL',
                'icon': '🔴',
                'subject': f'FINAL WARNING: Sealing Threat - {factory_name}',
                'body': f"""
FINAL WARNING - SEALING THREAT

Factory: {factory_name}
Gaia Score: {score}/100

Violations:
{chr(10).join(['- ' + s for s in suggestions[:4]])}

Deadline: 30 days
""",
                'deadline_days': 30,
                'deadline_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'action_required': True,
                'escalation_level': 3
            }

        # IMPROVEMENT NOTICE
        elif score < 60:
            notification = {
                'type': 'IMPROVEMENT_NOTICE',
                'severity': 'MEDIUM',
                'icon': '🟡',
                'subject': f'Improvement Notice - {factory_name}',
                'body': f"""
IMPROVEMENT NOTICE

Factory: {factory_name}
Gaia Score: {score}/100

Areas to Improve:
{chr(10).join(['- ' + s for s in suggestions[:3]])}

Submit improvement plan within 15 days.
""",
                'deadline_days': 60,
                'deadline_date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
                'action_required': True,
                'escalation_level': 1
            }

        # GOOD / EXCELLENT
        else:
            notification = {
                'type': 'ACKNOWLEDGMENT',
                'severity': 'LOW',
                'icon': '✅',
                'subject': f'Report Acknowledged - {factory_name}',
                'body': f"""
REPORT ACKNOWLEDGED

Factory: {factory_name}
Gaia Score: {score}/100 ({severity})

Thank you for maintaining compliance.
""",
                'deadline_days': None,
                'deadline_date': None,
                'action_required': False,
                'escalation_level': 0
            }

        notification['score'] = score
        notification['factory_name'] = factory_name
        notification['timestamp'] = datetime.now().isoformat()
        notification['language'] = language

        if language != 'en':
            notification['body_translated'] = self._translate_notification(notification['body'], language)

        return notification

    def send(self, to, notification):
        """Send notification"""

        notification_data = {
            'to': to,
            'type': notification['type'],
            'severity': notification.get('severity', 'MEDIUM'),
            'subject': notification.get('subject', 'GAIA Notification'),
            'body': notification.get('body_translated', notification.get('body', '')),
            'timestamp': datetime.now(),
            'status': 'sent',
            'channel': 'email'
        }

        self.sent_notifications.append(notification_data)

        # Store reminder
        if notification.get('deadline_days') is not None and notification.get('action_required'):
            self.pending_reminders.append({
                'notification': notification,
                'to': to,
                'deadline': datetime.now() + timedelta(days=notification['deadline_days']),
                'sent_date': datetime.now()
            })

        # Streamlit UI (safe)
        try:
            with st.chat_message("assistant"):
                st.markdown(f"""
📧 Notification Sent  
To: {to}  
Type: {notification['type']}  
Severity: {notification.get('severity')}  
Subject: {notification.get('subject')}  
""")
        except:
            pass

        print(f"[NOTIFICATION SENT] To: {to} | Type: {notification['type']}")
        return True

    def get_pending_reminders(self):
        """Get reminders near deadline"""
        today = datetime.now()
        pending = []

        for reminder in self.pending_reminders:
            days_remaining = (reminder['deadline'] - today).days
            if 0 < days_remaining <= 7:
                pending.append({
                    'to': reminder['to'],
                    'notification': reminder['notification'],
                    'days_remaining': days_remaining
                })

        return pending

    def generate_reminder(self, original_notification, days_remaining):
        """Generate reminder for pending action"""
        factory_name = original_notification.get('factory_name', 'Facility')
        notif_type = original_notification.get('type', 'NOTICE')
        score = original_notification.get('score', 0)

        return {
            'type': f'REMINDER_{notif_type}',
            'severity': original_notification.get('severity', 'HIGH'),
            'icon': '⏰',
            'subject': f'REMINDER: Action Required within {days_remaining} days - {factory_name}',
            'body': f"""
REMINDER: Action Required within {days_remaining} days

Factory: {factory_name}
Original Notice: {notif_type}
Current Score: {score}/100
Days Remaining: {days_remaining}

Please ensure the required corrective actions or documentation are submitted before the deadline.
""",
            'deadline_days': days_remaining,
            'deadline_date': original_notification.get('deadline_date'),
            'action_required': True,
            'escalation_level': original_notification.get('escalation_level', 1) + 1,
            'factory_name': factory_name,
            'score': score
        }

    def send_due_reminders(self):
        pending = self.get_pending_reminders()
        for p in pending:
            reminder = self.generate_reminder(p['notification'], p['days_remaining'])
            self.send(p['to'], reminder)
        return len(pending)

# Create instance
notification_system = NotificationSystem()