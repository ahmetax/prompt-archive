import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, flash, current_app, send_from_directory, abort
)
from sqlalchemy import func, desc

from models import db, Prompt, Tag, PromptStats, prompt_tags  # prompt_tags eklendi
from utils.helpers import allowed_file

# Blueprint tanımı
prompt_bp = Blueprint('prompt', __name__)

@prompt_bp.route('/')
def index():
    """Ana sayfa."""
    return render_template('index.html')

# prompt_routes.py dosyasında, prompt_list fonksiyonu içinde şu kısmı bulup değiştirin:

@prompt_bp.route('/prompts')
def prompt_list():
    """Prompt listesi sayfası. Filtreleme ve sıralama özellikleri içerir."""
    page = request.args.get('page', 1, type=int)
    
    # Filtreleme parametrelerini al
    filters = {}
    for field in ['language', 'generator_ai', 'from_type', 'to_type']:
        values = request.args.getlist(field)
        if values:
            filters[field] = values
    
    # Etiket filtresi
    tag_filter = request.args.getlist('tag')
    
    # Arama terimi
    search_term = request.args.get('search', '')
    
    # Sıralama parametreleri
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Temel sorgu
    query = Prompt.query
    
    # Filtreleri uygula
    for field, values in filters.items():
        query = query.filter(getattr(Prompt, field).in_(values))
    
    # Etiket filtresi uygula
    if tag_filter:
        for tag_name in tag_filter:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                query = query.filter(Prompt.tags.contains(tag))
    
    # Arama terimini uygula
    if search_term:
        search_term = f"%{search_term}%"
        query = query.filter(
            db.or_(
                Prompt.description.ilike(search_term),
                Prompt.prompt.ilike(search_term),
                Prompt.notes.ilike(search_term)
            )
        )
    
    # Sıralamayı uygula
    order_func = desc if sort_order == 'desc' else lambda x: x
    query = query.order_by(order_func(getattr(Prompt, sort_by)))
    
    # Sayfalama
    per_page = current_app.config['ITEMS_PER_PAGE']
    # Burada paginate fonksiyonu düzeltildi
    pagination = query.paginate(page=page, per_page=per_page)
    
    # Filtre seçeneklerini hazırla
    filter_options = {
        'language': db.session.query(Prompt.language).distinct().all(),
        'generator_ai': db.session.query(Prompt.generator_ai).distinct().all(),
        'from_type': db.session.query(Prompt.from_type).distinct().all(),
        'to_type': db.session.query(Prompt.to_type).distinct().all(),
        'tags': Tag.query.order_by(Tag.name).all()
    }
    
    return render_template(
        'prompt_list.html', 
        prompts=pagination,
        filters=filters,
        tag_filter=tag_filter,
        search_term=search_term,
        sort_by=sort_by,
        sort_order=sort_order,
        filter_options=filter_options
    )

@prompt_bp.route('/prompts/<int:id>')
def prompt_detail(id):
    """Prompt detay sayfası."""
    prompt = Prompt.query.get_or_404(id)
    
    # Varsa bu promptun diğer versiyonlarını al
    versions = []
    if prompt.parent_id:
        # Bu bir alt versiyon, ana promptu ve diğer versiyonları al
        parent = prompt.parent
        versions = parent.versions.all()
    else:
        # Bu bir ana prompt, tüm alt versiyonları al
        versions = prompt.versions.all()
    
    return render_template('prompt_detail.html', prompt=prompt, versions=versions)

@prompt_bp.route('/prompts/new', methods=['GET', 'POST'])
def prompt_new():
    """Yeni prompt ekleme sayfası."""
    if request.method == 'POST':
        # Form verilerini al
        data = {
            'description': request.form.get('description'),
            'language': request.form.get('language'),
            'generator_ai': request.form.get('generator_ai'),
            'from_type': request.form.get('from_type'),
            'to_type': request.form.get('to_type'),
            'prompt': request.form.get('prompt'),
            'source': request.form.get('source'),
            'notes': request.form.get('notes'),
            'success_rating': request.form.get('success_rating', type=int, default=0),
            'parent_id': request.form.get('parent_id', type=int),
            'ai_parameters': request.form.get('ai_parameters'),
            'api_usage': request.form.get('api_usage')
        }
        
        # Yeni prompt oluştur
        new_prompt = Prompt(**data)
        
        # Etiketleri işle
        tag_names = request.form.get('tags', '').split(',')
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                # Etiket varsa kullan, yoksa oluştur
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                new_prompt.tags.append(tag)
        
        # Dosya yüklemesi varsa işle
        if 'result_file' in request.files:
            file = request.files['result_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                new_prompt.result_file_path = f"uploads/{unique_filename}"
        
        # Veritabanına kaydet
        db.session.add(new_prompt)
        db.session.commit()
        
        flash('Prompt başarıyla eklendi!', 'success')
        return redirect(url_for('prompt.prompt_detail', id=new_prompt.id))
    
    # GET isteği - form sayfasını göster
    parent_id = request.args.get('parent_id', type=int)
    parent = None
    if parent_id:
        parent = Prompt.query.get_or_404(parent_id)
    
    tags = Tag.query.order_by(Tag.name).all()
    
    return render_template('prompt_form.html', prompt=None, parent=parent, tags=tags)

@prompt_bp.route('/prompts/<int:id>/edit', methods=['GET', 'POST'])
def prompt_edit(id):
    """Prompt düzenleme sayfası."""
    prompt = Prompt.query.get_or_404(id)
    
    if request.method == 'POST':
        # Form verilerini al ve promptu güncelle
        prompt.description = request.form.get('description')
        prompt.language = request.form.get('language')
        prompt.generator_ai = request.form.get('generator_ai')
        prompt.from_type = request.form.get('from_type')
        prompt.to_type = request.form.get('to_type')
        prompt.prompt = request.form.get('prompt')
        prompt.source = request.form.get('source')
        prompt.notes = request.form.get('notes')
        prompt.success_rating = request.form.get('success_rating', type=int, default=0)
        prompt.ai_parameters = request.form.get('ai_parameters')
        prompt.api_usage = request.form.get('api_usage')
        
        # Etiketleri güncelle
        prompt.tags.clear()
        tag_names = request.form.get('tags', '').split(',')
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                prompt.tags.append(tag)
        
        # Dosya yüklemesi varsa işle
        if 'result_file' in request.files:
            file = request.files['result_file']
            if file and file.filename and allowed_file(file.filename):
                # Eski dosyayı sil (varsa)
                if prompt.result_file_path:
                    old_file_path = os.path.join(current_app.config['BASEDIR'], 'static', prompt.result_file_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # Yeni dosyayı kaydet
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                prompt.result_file_path = f"uploads/{unique_filename}"
        
        # Veritabanını güncelle
        db.session.commit()
        
        flash('Prompt başarıyla güncellendi!', 'success')
        return redirect(url_for('prompt.prompt_detail', id=prompt.id))
    
    # GET isteği - form sayfasını göster
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('prompt_form.html', prompt=prompt, parent=None, tags=tags)

@prompt_bp.route('/prompts/<int:id>/delete', methods=['POST'])
def prompt_delete(id):
    """Prompt silme işlemi."""
    prompt = Prompt.query.get_or_404(id)
    
    # İlişkili dosyayı sil (varsa)
    if prompt.result_file_path:
        file_path = os.path.join(current_app.config['BASEDIR'], 'static', prompt.result_file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Veritabanından sil
    db.session.delete(prompt)
    db.session.commit()
    
    flash('Prompt başarıyla silindi!', 'success')
    return redirect(url_for('prompt.prompt_list'))

# prompt_routes.py dosyasında statistics fonksiyonunu aşağıdaki ile değiştirin

@prompt_bp.route('/statistics')
def statistics():
    """İstatistikler sayfası."""
    try:
        # En son istatistikleri al veya yeni istatistikleri hesapla
        stats = PromptStats.query.order_by(desc(PromptStats.date)).first()
        
        if not stats or (datetime.utcnow() - stats.date).days >= 1:
            # Yeni istatistikler hesapla
            stats_data = {}
            
            # Dil bazında sayım
            language_counts = db.session.query(
                Prompt.language, func.count(Prompt.id)
            ).group_by(Prompt.language).all()
            stats_data['language_counts'] = dict(language_counts)
            
            # AI üreteci bazında sayım
            ai_counts = db.session.query(
                Prompt.generator_ai, func.count(Prompt.id)
            ).group_by(Prompt.generator_ai).all()
            stats_data['ai_counts'] = dict(ai_counts)
            
            # From-to türleri bazında sayım
            conversion_counts = db.session.query(
                Prompt.from_type, Prompt.to_type, func.count(Prompt.id)
            ).group_by(Prompt.from_type, Prompt.to_type).all()
            stats_data['conversion_counts'] = {
                f"{from_type}->{to_type}": count 
                for from_type, to_type, count in conversion_counts
            }
            
            # Başarı puanı ortalamaları
            avg_ratings = db.session.query(
                Prompt.generator_ai, func.avg(Prompt.success_rating)
            ).filter(Prompt.success_rating > 0).group_by(Prompt.generator_ai).all()
            stats_data['avg_ratings'] = {ai: float(avg) for ai, avg in avg_ratings}
            
            # En popüler etiketler
            tag_counts = db.session.query(
                Tag.name, func.count(prompt_tags.c.prompt_id)
            ).join(prompt_tags).group_by(Tag.name).order_by(
                func.count(prompt_tags.c.prompt_id).desc()
            ).limit(10).all()
            stats_data['popular_tags'] = dict(tag_counts)
            
            # Yeni eklenen istatistik verisini kaydet
            new_stats = PromptStats(stats_data=json.dumps(stats_data))
            db.session.add(new_stats)
            db.session.commit()
            
            stats_data_json = stats_data
        else:
            # Mevcut istatistikleri kullan
            stats_data_json = json.loads(stats.stats_data)
        
        # Verileri kontrol et ve varsayılan değerler ekle
        if 'language_counts' not in stats_data_json or not stats_data_json['language_counts']:
            stats_data_json['language_counts'] = {'Veri Yok': 0}
        
        if 'ai_counts' not in stats_data_json or not stats_data_json['ai_counts']:
            stats_data_json['ai_counts'] = {'Veri Yok': 0}
            
        if 'conversion_counts' not in stats_data_json or not stats_data_json['conversion_counts']:
            stats_data_json['conversion_counts'] = {'Veri Yok': 0}
            
        if 'avg_ratings' not in stats_data_json or not stats_data_json['avg_ratings']:
            stats_data_json['avg_ratings'] = {'Veri Yok': 0}
            
        if 'popular_tags' not in stats_data_json or not stats_data_json['popular_tags']:
            stats_data_json['popular_tags'] = {'Veri Yok': 0}
        
        return render_template('statistics.html', stats=stats_data_json)
    except Exception as e:
        # Hata durumunda güvenli bir hata sayfası göster
        print(f"İstatistik sayfası yüklenirken hata: {e}")
        flash(f'İstatistikler yüklenirken bir hata oluştu: {str(e)}', 'danger')
        return render_template('statistics.html', stats={
            'language_counts': {'Veri Yok': 0},
            'ai_counts': {'Veri Yok': 0},
            'conversion_counts': {'Veri Yok': 0},
            'avg_ratings': {'Veri Yok': 0},
            'popular_tags': {'Veri Yok': 0}
        })

@prompt_bp.route('/statistics_old')
def statistics_old():
    """İstatistikler sayfası."""
    # En son istatistikleri al veya yeni istatistikleri hesapla
    stats = PromptStats.query.order_by(desc(PromptStats.date)).first()
    
    if not stats or (datetime.utcnow() - stats.date).days >= 1:
        # Yeni istatistikler hesapla
        stats_data = {}
        
        # Dil bazında sayım
        language_counts = db.session.query(
            Prompt.language, func.count(Prompt.id)
        ).group_by(Prompt.language).all()
        stats_data['language_counts'] = dict(language_counts)
        
        # AI üreteci bazında sayım
        ai_counts = db.session.query(
            Prompt.generator_ai, func.count(Prompt.id)
        ).group_by(Prompt.generator_ai).all()
        stats_data['ai_counts'] = dict(ai_counts)
        
        # From-to türleri bazında sayım
        conversion_counts = db.session.query(
            Prompt.from_type, Prompt.to_type, func.count(Prompt.id)
        ).group_by(Prompt.from_type, Prompt.to_type).all()
        stats_data['conversion_counts'] = {
            f"{from_type}->{to_type}": count 
            for from_type, to_type, count in conversion_counts
        }
        
        # Başarı puanı ortalamaları
        avg_ratings = db.session.query(
            Prompt.generator_ai, func.avg(Prompt.success_rating)
        ).filter(Prompt.success_rating > 0).group_by(Prompt.generator_ai).all()
        stats_data['avg_ratings'] = {ai: float(avg) for ai, avg in avg_ratings}
        
        # En popüler etiketler
        tag_counts = db.session.query(
            Tag.name, func.count(prompt_tags.c.prompt_id)
        ).join(prompt_tags).group_by(Tag.name).order_by(
            func.count(prompt_tags.c.prompt_id).desc()
        ).limit(10).all()
        stats_data['popular_tags'] = dict(tag_counts)
        
        # İstatistikleri veritabanına kaydet
        new_stats = PromptStats(stats_data=json.dumps(stats_data))
        db.session.add(new_stats)
        db.session.commit()
        
        stats_data_json = stats_data
    else:
        # Mevcut istatistikleri kullan
        stats_data_json = json.loads(stats.stats_data)
    
    return render_template('statistics.html', stats=stats_data_json)

@prompt_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Yüklenen dosyaları serve et."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
