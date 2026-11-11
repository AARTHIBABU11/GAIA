# modules/database.py

import sqlite3

import json

import pandas as pd # type: ignore

from datetime import datetime, timedelta

import os

import streamlit as st # type: ignore

class DatabaseManager:

    """Manage SQLite database for GAIA - Enhanced with search and analytics"""

 

    def __init__(self, db_path="data/gaia.db"):

        self.db_path = db_path

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self._init_db()

 

    def _get_connection(self):

        """Get database connection with row factory for dict results"""

        conn = sqlite3.connect(self.db_path)

        conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        return conn

 

    def _init_db(self):

        """Initialize database tables with enhanced schema"""

        conn = self._get_connection()

        cursor = conn.cursor()

 

        # Reports table with additional fields

        cursor.execute('''

            CREATE TABLE IF NOT EXISTS reports (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                factory_name TEXT NOT NULL,

                report_text TEXT,

                gaia_score REAL,

                status TEXT,

                is_fake BOOLEAN DEFAULT 0,

                fraud_score REAL,

                industry TEXT,

                created_at TIMESTAMP,

                updated_at TIMESTAMP

            )

        ''')

 

        # Citizen complaints table with tracking

        cursor.execute('''

            CREATE TABLE IF NOT EXISTS complaints (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                tracking_id TEXT UNIQUE NOT NULL,

                complaint_type TEXT,

                location TEXT,

                description TEXT,

                severity TEXT DEFAULT 'MEDIUM',

                status TEXT DEFAULT 'PENDING',

                officer_assigned TEXT,

                inspection_date TEXT,

                resolution_date TEXT,

                created_at TIMESTAMP,

                updated_at TIMESTAMP

            )

        ''')

 

        # Notifications table

        cursor.execute('''

            CREATE TABLE IF NOT EXISTS notifications (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                recipient TEXT,

                notification_type TEXT,

                severity TEXT,

                subject TEXT,

                content TEXT,

                is_read BOOLEAN DEFAULT 0,

                sent_at TIMESTAMP

            )

        ''')

 

        # Analytics cache table for faster queries

        cursor.execute('''

            CREATE TABLE IF NOT EXISTS analytics_cache (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                metric_name TEXT UNIQUE,

                metric_value TEXT,

                calculated_at TIMESTAMP

            )

        ''')

 

        # Create indexes for faster queries

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_score ON reports(gaia_score)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_tracking ON complaints(tracking_id)')

 

        conn.commit()

        conn.close()

        print("[OK] Database initialized successfully")

 

    # ============ Report Functions ============

 

    def save_report(self, factory_name, report_text, gaia_score, is_fake, fraud_score, industry=None, status=None):

        """Save analyzed report"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            # Determine status if not provided

            if status is None:

                if gaia_score >= 80:

                    status = "EXCELLENT"

                elif gaia_score >= 60:

                    status = "GOOD"

                elif gaia_score >= 40:

                    status = "POOR"

                else:

                    status = "CRITICAL"

 

            cursor.execute('''

                INSERT INTO reports

                (factory_name, report_text, gaia_score, status, is_fake, fraud_score, industry, created_at, updated_at)

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            ''', (factory_name, report_text[:500], gaia_score, status, is_fake, fraud_score, industry,

                  datetime.now(), datetime.now()))

 

            conn.commit()

            report_id = cursor.lastrowid

            conn.close()

 

            return report_id

 

        except Exception as e:

            print(f"Error saving report: {e}")

            return None

 

    def get_reports(self, limit=10, offset=0, status=None, min_score=None, max_score=None):

        """Get recent reports with filters"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            query = "SELECT * FROM reports WHERE 1=1"

            params = []

 

            if status:

                query += " AND status = ?"

                params.append(status)

 

            if min_score is not None:

                query += " AND gaia_score >= ?"

                params.append(min_score)

 

            if max_score is not None:

                query += " AND gaia_score <= ?"

                params.append(max_score)

 

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"

            params.extend([limit, offset])

 

            cursor.execute(query, params)

            results = cursor.fetchall()

            conn.close()

 

            return [dict(row) for row in results]

 

        except Exception as e:

            print(f"Error getting reports: {e}")

            return []

 

    def get_report_by_id(self, report_id):

        """Get single report by ID"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

            cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))

            result = cursor.fetchone()

            conn.close()

            return dict(result) if result else None

        except Exception as e:

            print(f"Error getting report: {e}")

            return None

 

    def update_report_status(self, report_id, status):

        """Update report status"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

            cursor.execute('''

                UPDATE reports SET status = ?, updated_at = ? WHERE id = ?

            ''', (status, datetime.now(), report_id))

            conn.commit()

            conn.close()

            return True

        except Exception as e:

            print(f"Error updating report: {e}")

            return False

 

    # ============ Complaint Functions ============

 

    def save_complaint(self, tracking_id, complaint_type, location, description=None, severity="MEDIUM"):

        """Save citizen complaint"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            cursor.execute('''

                INSERT INTO complaints

                (tracking_id, complaint_type, location, description, severity, status, created_at, updated_at)

                VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            ''', (tracking_id, complaint_type, location, description, severity, 'PENDING',

                  datetime.now(), datetime.now()))

 

            conn.commit()

            complaint_id = cursor.lastrowid

            conn.close()

 

            return complaint_id

 

        except Exception as e:

            print(f"Error saving complaint: {e}")

            return None

 

    def get_complaints(self, limit=10, status=None):

        """Get recent complaints"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            if status:

                cursor.execute('''

                    SELECT * FROM complaints WHERE status = ? ORDER BY created_at DESC LIMIT ?

                ''', (status, limit))

            else:

                cursor.execute('''

                    SELECT * FROM complaints ORDER BY created_at DESC LIMIT ?

                ''', (limit,))

 

            results = cursor.fetchall()

            conn.close()

 

            return [dict(row) for row in results]

 

        except Exception as e:

            print(f"Error getting complaints: {e}")

            return []

 

    def get_complaint_by_tracking_id(self, tracking_id):

        """Get complaint by tracking ID"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

            cursor.execute("SELECT * FROM complaints WHERE tracking_id = ?", (tracking_id,))

            result = cursor.fetchone()

            conn.close()

            return dict(result) if result else None

        except Exception as e:

            print(f"Error getting complaint: {e}")

            return None

 

    def update_complaint_status(self, tracking_id, status, officer_assigned=None, inspection_date=None):

        """Update complaint status and assignment"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            updates = ["status = ?", "updated_at = ?"]

            params = [status, datetime.now()]

 

            if officer_assigned:

                updates.append("officer_assigned = ?")

                params.append(officer_assigned)

 

            if inspection_date:

                updates.append("inspection_date = ?")

                params.append(inspection_date)

 

            if status == "RESOLVED":

                updates.append("resolution_date = ?")

                params.append(datetime.now())

 

            query = f"UPDATE complaints SET {', '.join(updates)} WHERE tracking_id = ?"

            params.append(tracking_id)

 

            cursor.execute(query, params)

            conn.commit()

            conn.close()

            return True

 

        except Exception as e:

            print(f"Error updating complaint: {e}")

            return False

 

    # ============ Notification Functions ============

 

    def save_notification(self, recipient, notification_type, severity, subject, content):

        """Save notification record"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            cursor.execute('''

                INSERT INTO notifications (recipient, notification_type, severity, subject, content, sent_at)

                VALUES (?, ?, ?, ?, ?, ?)

            ''', (recipient, notification_type, severity, subject, content, datetime.now()))

 

            conn.commit()

            notification_id = cursor.lastrowid

            conn.close()

 

            return notification_id

 

        except Exception as e:

            print(f"Error saving notification: {e}")

            return None

 

    def get_notifications(self, limit=20, is_read=None):

        """Get notifications"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            if is_read is not None:

                cursor.execute('''

                    SELECT * FROM notifications WHERE is_read = ? ORDER BY sent_at DESC LIMIT ?

                ''', (is_read, limit))

            else:

                cursor.execute('''

                    SELECT * FROM notifications ORDER BY sent_at DESC LIMIT ?

                ''', (limit,))

 

            results = cursor.fetchall()

            conn.close()

 

            return [dict(row) for row in results]

 

        except Exception as e:

            print(f"Error getting notifications: {e}")

            return []

 

    def mark_notification_read(self, notification_id):

        """Mark notification as read"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

            cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))

            conn.commit()

            conn.close()

            return True

        except Exception as e:

            print(f"Error marking notification: {e}")

            return False

 

    # ============ Analytics Functions ============

 

    def get_statistics(self):

        """Get comprehensive statistics"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            stats = {}

 

            # Report statistics

            cursor.execute("SELECT COUNT(*) FROM reports")

            stats['total_reports'] = cursor.fetchone()[0]

 

            cursor.execute("SELECT AVG(gaia_score) FROM reports")

            stats['avg_gaia_score'] = round(cursor.fetchone()[0] or 0, 1)

 

            cursor.execute("SELECT COUNT(*) FROM reports WHERE is_fake = 1")

            stats['fake_reports'] = cursor.fetchone()[0]

 

            cursor.execute("""

                SELECT status, COUNT(*) FROM reports GROUP BY status

            """)

            stats['reports_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}

 

            # Complaint statistics

            cursor.execute("SELECT COUNT(*) FROM complaints")

            stats['total_complaints'] = cursor.fetchone()[0]

 

            cursor.execute("""

                SELECT status, COUNT(*) FROM complaints GROUP BY status

            """)

            stats['complaints_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}

 

            cursor.execute("""

                SELECT complaint_type, COUNT(*) FROM complaints GROUP BY complaint_type

            """)

            stats['complaints_by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

 

            # Recent activity

            seven_days_ago = datetime.now() - timedelta(days=7)

            cursor.execute("""

                SELECT COUNT(*) FROM reports WHERE created_at > ?

            """, (seven_days_ago,))

            stats['reports_last_7_days'] = cursor.fetchone()[0]

 

            cursor.execute("""

                SELECT COUNT(*) FROM complaints WHERE created_at > ?

            """, (seven_days_ago,))

            stats['complaints_last_7_days'] = cursor.fetchone()[0]

 

            conn.close()

            return stats

 

        except Exception as e:

            print(f"Error getting statistics: {e}")

            return {}

 

    def export_to_csv(self, table_name, output_path=None):

        """Export table to CSV"""

        try:

            conn = self._get_connection()

            query = f"SELECT * FROM {table_name}"

            df = pd.read_sql_query(query, conn)

            conn.close()

 

            if output_path is None:

                output_path = f"data/{table_name}_export_{datetime.now().strftime('%Y%m%d')}.csv"

 

            df.to_csv(output_path, index=False)

            return output_path

 

        except Exception as e:

            print(f"Error exporting to CSV: {e}")

            return None

 

    def search_reports(self, keyword):

        """Search reports by keyword"""

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

            cursor.execute('''

                SELECT * FROM reports

                WHERE factory_name LIKE ? OR report_text LIKE ?

                ORDER BY created_at DESC

            ''', (f'%{keyword}%', f'%{keyword}%'))

 

            results = cursor.fetchall()

            conn.close()

 

            return [dict(row) for row in results]

 

        except Exception as e:

            print(f"Error searching reports: {e}")

            return []

 

    def get_performance_summary(self):

        """Get performance summary for dashboard"""

        stats = self.get_statistics()

 

        return {

            'total_reports': stats.get('total_reports', 0),

            'avg_score': stats.get('avg_gaia_score', 0),

            'fraud_rate': round((stats.get('fake_reports', 0) / max(stats.get('total_reports', 1), 1)) * 100, 1),

            'complaints_pending': stats.get('complaints_by_status', {}).get('PENDING', 0),

            'complaints_resolved': stats.get('complaints_by_status', {}).get('RESOLVED', 0),

            'active_cases': stats.get('complaints_by_status', {}).get('IN_PROGRESS', 0),

            'recent_activity': stats.get('reports_last_7_days', 0) + stats.get('complaints_last_7_days', 0)

        }

 

    def clear_all_data(self, confirm=False):

        """Clear all data (for testing only)"""

        if not confirm:

            return False

 

        try:

            conn = self._get_connection()

            cursor = conn.cursor()

 

            cursor.execute("DELETE FROM reports")

            cursor.execute("DELETE FROM complaints")

            cursor.execute("DELETE FROM notifications")

            cursor.execute("DELETE FROM analytics_cache")

 

            conn.commit()

            conn.close()

 

            print("[OK] All data cleared")

            return True

 

        except Exception as e:

            print(f"Error clearing data: {e}")

            return False

# Create instance

db = DatabaseManager()
