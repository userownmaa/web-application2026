from flask import Blueprint, render_template, request, send_file, current_app
from flask_login import current_user, login_required
from sqlalchemy import func, desc
from models import VisitLog, User
from extensions import db
from decorators import check_rights
import csv
import io
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.before_app_request
def log_visit():
    """Логирование посещений всех страниц (только для авторизованных пользователей)"""
    if request.endpoint and not request.endpoint.startswith('static'):
        if current_user.is_authenticated:
            visit_log = VisitLog(
                path=request.path,
                user_id=current_user.id
            )
            db.session.add(visit_log)
            db.session.commit()

@reports_bp.route('/visits')
@login_required
def visit_logs():
    """Журнал посещений"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    
    query = VisitLog.query.order_by(desc(VisitLog.created_at))
    
    if not current_user.role or current_user.role.name != 'Администратор':
        query = query.filter(VisitLog.user_id == current_user.id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items
    
    return render_template('reports/visit_logs.html', 
                         logs=logs, 
                         pagination=pagination,
                         title='Журнал посещений')

@reports_bp.route('/visits/by-pages')
@login_required
def visits_by_pages():
    """Статистика посещений по страницам"""
    query = db.session.query(
        VisitLog.path,
        func.count(VisitLog.id).label('visit_count')
    ).group_by(VisitLog.path).order_by(desc('visit_count'))
    
    if not current_user.role or current_user.role.name != 'Администратор':
        query = query.filter(VisitLog.user_id == current_user.id)
    
    stats = query.all()
    return render_template('reports/visits_by_pages.html', 
                         stats=stats,
                         title='Статистика по страницам')

@reports_bp.route('/visits/by-pages/export')
@login_required
def export_visits_by_pages():
    """Экспорт статистики по страницам в CSV"""
    query = db.session.query(
        VisitLog.path,
        func.count(VisitLog.id).label('visit_count')
    ).group_by(VisitLog.path).order_by(desc('visit_count'))
    
    if not current_user.role or current_user.role.name != 'Администратор':
        query = query.filter(VisitLog.user_id == current_user.id)
    
    stats = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Страница', 'Количество посещений'])
    
    for i, (path, count) in enumerate(stats, 1):
        writer.writerow([i, path, count])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8',
        as_attachment=True,
        download_name=f'visits_by_pages_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@reports_bp.route('/visits/by-users')
@login_required
def visits_by_users():
    """Статистика посещений по пользователям"""
    query = db.session.query(
        VisitLog.user_id,
        User.last_name,
        User.first_name,
        User.middle_name,
        func.count(VisitLog.id).label('visit_count')
    ).outerjoin(User, VisitLog.user_id == User.id).group_by(
        VisitLog.user_id, User.last_name, User.first_name, User.middle_name
    ).order_by(desc('visit_count'))
    
    if not current_user.role or current_user.role.name != 'Администратор':
        query = query.filter(VisitLog.user_id == current_user.id)
    
    stats = query.all()
    
    formatted_stats = []
    for i, (user_id, last_name, first_name, middle_name, count) in enumerate(stats, 1):
        if user_id is None:
            user_name = "Неаутентифицированный пользователь"
        else:
            parts = [last_name, first_name, middle_name]
            user_name = ' '.join(filter(None, parts)) or f"Пользователь #{user_id}"
        formatted_stats.append((i, user_name, count))
    
    return render_template('reports/visits_by_users.html', 
                         stats=formatted_stats,
                         title='Статистика по пользователям')

@reports_bp.route('/visits/by-users/export')
@login_required
def export_visits_by_users():
    """Экспорт статистики по пользователям в CSV"""
    query = db.session.query(
        VisitLog.user_id,
        User.last_name,
        User.first_name,
        User.middle_name,
        func.count(VisitLog.id).label('visit_count')
    ).outerjoin(User, VisitLog.user_id == User.id).group_by(
        VisitLog.user_id, User.last_name, User.first_name, User.middle_name
    ).order_by(desc('visit_count'))
    
    if not current_user.role or current_user.role.name != 'Администратор':
        query = query.filter(VisitLog.user_id == current_user.id)
    
    stats = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])
    
    for i, (user_id, last_name, first_name, middle_name, count) in enumerate(stats, 1):
        if user_id is None:
            user_name = "Неаутентифицированный пользователь"
        else:
            parts = [last_name, first_name, middle_name]
            user_name = ' '.join(filter(None, parts)) or f"Пользователь #{user_id}"
        writer.writerow([i, user_name, count])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8',
        as_attachment=True,
        download_name=f'visits_by_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )