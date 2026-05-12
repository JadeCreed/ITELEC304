import csv
import io
from datetime import timedelta, date, datetime

from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import ScreenTimeLog


class AnalyticsService:
    """
    Handles all screen time analytics calculations.
    Logic lives here, NOT in views.
    """

    def __init__(self, queryset=None):
        self.queryset = queryset or ScreenTimeLog.objects.all()

    def get_total_screen_time(self, target_date=None):
        """Returns total screen time in minutes for a given date (default: today)."""
        if target_date is None:
            target_date = date.today()
        result = self.queryset.filter(date=target_date).aggregate(
            total=Sum('duration_minutes')
        )
        return result['total'] or 0

    def get_most_used_app(self, target_date=None):
        """Returns the app with most usage for a given date."""
        if target_date is None:
            target_date = date.today()
        entry = self.queryset.filter(date=target_date).order_by('-duration_minutes').first()
        return entry.app_name if entry else "No data"

    def get_category_breakdown(self, target_date=None):
        """Returns dict of category -> total minutes for pie chart."""
        qs = self.queryset
        if target_date:
            qs = qs.filter(date=target_date)
        breakdown = qs.values('category').annotate(
            total=Sum('duration_minutes')
        ).order_by('-total')
        return {item['category']: item['total'] for item in breakdown}

    def get_weekly_trend(self):
        """Returns last 7 days of screen time for bar chart."""
        today = date.today()
        trend = {}
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            total = self.queryset.filter(date=day).aggregate(
                total=Sum('duration_minutes')
            )['total'] or 0
            trend[day.strftime('%a %d')] = total
        return trend

    def calculate_productivity_score(self, target_date=None):
        """
        Calculates productivity score (0-100).
        Study/Work = positive, Social/Gaming = negative.
        """
        if target_date is None:
            target_date = date.today()

        entries = self.queryset.filter(date=target_date)
        if not entries.exists():
            return 0

        total_minutes = entries.aggregate(total=Sum('duration_minutes'))['total'] or 1

        score_weights = {
            'Study': 2.0,
            'Work': 1.5,
            'Entertainment': 0.0,
            'Social': -1.0,
            'Gaming': -1.5,
        }

        weighted_score = 0
        for entry in entries:
            weight = score_weights.get(entry.category, 0)
            weighted_score += (entry.duration_minutes / total_minutes) * weight

        # Normalize to 0-100
        max_weight = 2.0
        min_weight = -1.5
        normalized = (weighted_score - min_weight) / (max_weight - min_weight) * 100
        return round(max(0, min(100, normalized)), 1)

    def get_focus_vs_distraction(self, target_date=None):
        """Returns focus (Study+Work) vs distraction (Social+Gaming) minutes."""
        if target_date is None:
            target_date = date.today()
        entries = self.queryset.filter(date=target_date)

        focus_cats = ['Study', 'Work']
        distract_cats = ['Social', 'Gaming']

        focus = entries.filter(category__in=focus_cats).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0

        distraction = entries.filter(category__in=distract_cats).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0

        return {'focus': focus, 'distraction': distraction}


class ProductivityService:
    """Handles productivity score history and trends."""

    def __init__(self):
        self.analytics = AnalyticsService()

    def get_weekly_scores(self):
        """Returns productivity scores for last 7 days."""
        today = date.today()
        scores = {}
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            score = self.analytics.calculate_productivity_score(target_date=day)
            scores[day.strftime('%a %d')] = score
        return scores

    def get_best_day(self):
        """Returns the most productive day this week."""
        scores = self.get_weekly_scores()
        if not scores:
            return "No data"
        return max(scores, key=scores.get)

    def get_worst_day(self):
        """Returns the least productive day this week."""
        scores = self.get_weekly_scores()
        if not scores:
            return "No data"
        return min(scores, key=scores.get)

    def get_weekly_average(self):
        """Returns average productivity score for the week."""
        scores = self.get_weekly_scores()
        if not scores:
            return 0
        return round(sum(scores.values()) / len(scores), 1)


class ReportService:
    """Generates summary reports and AI-style insights."""

    def __init__(self):
        self.analytics = AnalyticsService()

    def get_weekly_summary(self):
        """Returns a full weekly summary dict."""
        trend = self.analytics.get_weekly_trend()
        total_week = sum(trend.values())
        avg_daily = round(total_week / 7, 1)

        return {
            'total_week_minutes': total_week,
            'avg_daily_minutes': avg_daily,
            'trend': trend,
        }

    def get_insights(self):
        """Generates smart text insights based on data."""
        insights = []
        breakdown = self.analytics.get_category_breakdown()
        total = sum(breakdown.values()) or 1

        for category, minutes in breakdown.items():
            percent = round((minutes / total) * 100, 1)
            if category == 'Social' and percent > 30:
                insights.append(
                    f"⚠️ You spend {percent}% of your time on Social apps. Consider reducing it!"
                )
            elif category == 'Study' and percent > 40:
                insights.append(
                    f"🎉 Great job! {percent}% of your time is spent on Study apps."
                )
            elif category == 'Gaming' and percent > 20:
                insights.append(
                    f"🎮 Gaming takes up {percent}% of your time. Balance it with productive tasks."
                )
            elif category == 'Work' and percent > 30:
                insights.append(
                    f"💼 You're spending {percent}% on Work apps. Make sure to rest!"
                )

        score = self.analytics.calculate_productivity_score()
        if score >= 70:
            insights.append("🌟 Excellent productivity today! Keep it up.")
        elif score >= 40:
            insights.append("📈 Decent productivity. Try to squeeze in more study time.")
        else:
            insights.append("💡 Low productivity score today. Focus on Study or Work apps tomorrow.")

        return insights if insights else ["📊 Add more data to generate personalized insights."]


class ImportService:
    REQUIRED_COLUMNS = ['app_name', 'category', 'duration', 'date']

    def read_file(self, uploaded_file):
        raw_data = uploaded_file.read().decode('utf-8-sig')
        return self.parse_csv(raw_data)

    def parse_csv(self, data):
        text_stream = io.StringIO(data)
        reader = csv.DictReader(text_stream)
        if not reader.fieldnames:
            return [], ['CSV header row is missing.']

        header_map = {name.strip().lower(): name for name in reader.fieldnames if name}
        missing = [col for col in self.REQUIRED_COLUMNS if col not in header_map]
        if missing:
            return [], [f"Missing required columns: {', '.join(missing)}."]

        valid_rows = []
        errors = []
        for line_number, raw_row in enumerate(reader, start=2):
            normalized = {
                key.strip().lower(): (value or '').strip()
                for key, value in raw_row.items() if key
            }
            row_result, error = self.validate_row(normalized, line_number)
            if error:
                errors.append(error)
            else:
                valid_rows.append(row_result)

        return valid_rows, errors

    def validate_row(self, row, line_number):
        app_name = row.get('app_name', '')
        category = row.get('category', '')
        duration_text = row.get('duration', '')
        date_text = row.get('date', '')
        notes = row.get('notes', '')

        if not app_name:
            return None, f"Row {line_number}: missing app_name."
        if not category:
            return None, f"Row {line_number}: missing category."
        if not duration_text:
            return None, f"Row {line_number}: missing duration."
        if not date_text:
            return None, f"Row {line_number}: missing date."

        try:
            duration_value = float(duration_text)
            duration_minutes = int(round(duration_value))
        except ValueError:
            return None, f"Row {line_number}: invalid duration '{duration_text}'."
        if duration_minutes <= 0:
            return None, f"Row {line_number}: duration must be greater than zero."

        try:
            parsed_date = datetime.strptime(date_text, '%d/%m/%Y').date()
        except ValueError:
            return None, f"Row {line_number}: invalid date '{date_text}'. Use DD/MM/YYYY."

        return {
            'app_name': app_name,
            'category': category,
            'duration_minutes': duration_minutes,
            'date': parsed_date,
            'notes': notes,
        }, None

    def save_to_database(self, rows):
        created = 0
        for row in rows:
            ScreenTimeLog.objects.create(**row)
            created += 1
        return created
