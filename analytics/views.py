from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import date
import json

from .models import ScreenTimeLog, CATEGORY_CHOICES
from .services import AnalyticsService, ProductivityService, ReportService, ImportService
from .forms import ScreenTimeLogForm


def dashboard(request):
    """Home dashboard with overview metrics."""
    service = AnalyticsService()
    prod_service = ProductivityService()

    today = date.today()
    total_today = service.get_total_screen_time(today)
    most_used = service.get_most_used_app(today)
    productivity_score = service.calculate_productivity_score(today)
    focus_data = service.get_focus_vs_distraction(today)

    # Weekly bar chart data
    weekly_trend = service.get_weekly_trend()
    weekly_labels = list(weekly_trend.keys())
    weekly_data = list(weekly_trend.values())

    # Category pie chart data
    category_breakdown = service.get_category_breakdown()
    category_labels = list(category_breakdown.keys())
    category_data = list(category_breakdown.values())

    context = {
        'total_today': total_today,
        'most_used': most_used,
        'productivity_score': productivity_score,
        'focus_data': focus_data,
        'weekly_labels': json.dumps(weekly_labels),
        'weekly_data': json.dumps(weekly_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'today': today,
    }
    return render(request, 'analytics/dashboard.html', context)


def add_log(request):
    """Add a new screen time log entry."""
    if request.method == 'POST':
        form = ScreenTimeLogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Screen time log added successfully!')
            return redirect('dashboard')
    else:
        form = ScreenTimeLogForm()

    return render(request, 'analytics/add_log.html', {'form': form})


def analytics_page(request):
    """Deep analytics with multiple charts."""
    service = AnalyticsService()
    prod_service = ProductivityService()

    # Weekly trend bar chart
    weekly_trend = service.get_weekly_trend()
    weekly_labels = list(weekly_trend.keys())
    weekly_data = list(weekly_trend.values())

    # Category pie chart (all time)
    category_breakdown = service.get_category_breakdown()
    category_labels = list(category_breakdown.keys())
    category_data = list(category_breakdown.values())

    # Productivity line chart
    weekly_scores = prod_service.get_weekly_scores()
    score_labels = list(weekly_scores.keys())
    score_data = list(weekly_scores.values())

    # Focus vs distraction donut
    focus_data = service.get_focus_vs_distraction()
    total_focus = focus_data['focus'] + focus_data['distraction']
    focus_ratio = round((focus_data['focus'] / total_focus) * 100, 1) if total_focus else 0
    distraction_ratio = round((focus_data['distraction'] / total_focus) * 100, 1) if total_focus else 0
    today_score = service.calculate_productivity_score()

    donut_labels = ['Focus', 'Distraction']
    donut_data = [focus_data['focus'], focus_data['distraction']]

    # Insights and summary data for readability
    report_service = ReportService()
    insights = report_service.get_insights()
    total_all_time = sum(category_breakdown.values())
    top_category = ''
    top_percent = 0
    if category_breakdown:
        top_category, top_total = max(category_breakdown.items(), key=lambda item: item[1])
        top_percent = round((top_total / total_all_time) * 100, 1) if total_all_time else 0

    if today_score >= 70:
        score_level = 'Excellent'
        score_color = '#2EE59D'
    elif today_score >= 40:
        score_level = 'Average'
        score_color = '#FFC857'
    else:
        score_level = 'Needs Improvement'
        score_color = '#FF5C5C'

    context = {
        'weekly_labels': json.dumps(weekly_labels),
        'weekly_data': json.dumps(weekly_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'score_labels': json.dumps(score_labels),
        'score_data': json.dumps(score_data),
        'donut_labels': json.dumps(donut_labels),
        'donut_data': json.dumps(donut_data),
        'focus_data': focus_data,
        'focus_ratio': focus_ratio,
        'distraction_ratio': distraction_ratio,
        'today_score': today_score,
        'score_level': score_level,
        'score_color': score_color,
        'insights': insights,
        'total_all_time': total_all_time,
        'top_category': top_category,
        'top_percent': top_percent,
    }
    return render(request, 'analytics/analytics.html', context)


def activity_logs(request):
    """Paginated table of all logs with search and filter."""
    logs = ScreenTimeLog.objects.all()

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        logs = logs.filter(app_name__icontains=search_query)

    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        logs = logs.filter(category=category_filter)

    # Sort
    sort_by = request.GET.get('sort', '-date')
    logs = logs.order_by(sort_by)

    # Pagination
    paginator = Paginator(logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': CATEGORY_CHOICES,
        'search_query': search_query,
        'category_filter': category_filter,
        'sort_by': sort_by,
    }
    return render(request, 'analytics/activity_logs.html', context)


def productivity_score_page(request):
    """Productivity score breakdown page."""
    prod_service = ProductivityService()
    analytics_service = AnalyticsService()

    today_score = analytics_service.calculate_productivity_score()
    weekly_avg = prod_service.get_weekly_average()
    best_day = prod_service.get_best_day()
    worst_day = prod_service.get_worst_day()
    weekly_scores = prod_service.get_weekly_scores()

    score_labels = list(weekly_scores.keys())
    score_data = list(weekly_scores.values())

    # Determine score level
    if today_score >= 70:
        score_level = 'Excellent'
        score_color = '#2EE59D'
    elif today_score >= 40:
        score_level = 'Average'
        score_color = '#FFC857'
    else:
        score_level = 'Low'
        score_color = '#FF5C5C'

    context = {
        'today_score': today_score,
        'weekly_avg': weekly_avg,
        'best_day': best_day,
        'worst_day': worst_day,
        'score_labels': json.dumps(score_labels),
        'score_data': json.dumps(score_data),
        'score_level': score_level,
        'score_color': score_color,
    }
    return render(request, 'analytics/productivity.html', context)


def reports_page(request):
    """Reports and AI insights page."""
    report_service = ReportService()
    analytics_service = AnalyticsService()

    weekly_summary = report_service.get_weekly_summary()
    insights = report_service.get_insights()
    category_breakdown = analytics_service.get_category_breakdown()

    # Format minutes to hours/minutes
    def format_time(minutes):
        h = minutes // 60
        m = minutes % 60
        return f"{h}h {m}m"

    formatted_trend = {
        day: format_time(mins)
        for day, mins in weekly_summary['trend'].items()
    }

    context = {
        'weekly_summary': weekly_summary,
        'insights': insights,
        'category_breakdown': category_breakdown,
        'formatted_trend': formatted_trend,
        'format_total': format_time(weekly_summary['total_week_minutes']),
        'format_avg': format_time(int(weekly_summary['avg_daily_minutes'])),
    }
    return render(request, 'analytics/reports.html', context)


def import_data(request):
    """Upload CSV and import screen time logs."""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('import_file')
        if not uploaded_file:
            messages.error(request, 'Please choose a CSV file to upload.')
            return redirect('import_data')

        service = ImportService()
        rows, errors = service.read_file(uploaded_file)
        created = 0
        if rows:
            created = service.save_to_database(rows)

        if created:
            messages.success(request, f'Imported {created} valid rows.')
        if errors:
            messages.warning(request, f'Skipped {len(errors)} invalid rows.')
            for error in errors[:5]:
                messages.info(request, error)

        return redirect('dashboard')

    return render(request, 'analytics/import.html')


def delete_log(request, pk):
    """Delete a log entry."""
    log = get_object_or_404(ScreenTimeLog, pk=pk)
    if request.method == 'POST':
        log.delete()
        messages.success(request, '🗑️ Log deleted.')
    return redirect('activity_logs')