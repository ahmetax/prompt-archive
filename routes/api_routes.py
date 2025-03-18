import json
from flask import Blueprint, jsonify, request
from sqlalchemy import desc

from models import db, Prompt, Tag, prompt_tags  # prompt_tags eklendi
from utils.helpers import generate_prompt_suggestion

# Blueprint tanımı
api_bp = Blueprint('api', __name__)

@api_bp.route('/prompts', methods=['GET'])
def get_prompts():
    """API: Tüm promptları getir."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
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
    pagination = query.paginate(page=page, per_page=per_page)
    
    # Sonuçları formatla
    prompts = []
    for prompt in pagination.items:
        prompts.append({
            'id': prompt.id,
            'date': prompt.date.isoformat(),
            'language': prompt.language,
            'description': prompt.description,
            'generator_ai': prompt.generator_ai,
            'from_type': prompt.from_type,
            'to_type': prompt.to_type,
            'prompt': prompt.prompt,
            'source': prompt.source,
            'notes': prompt.notes,
            'success_rating': prompt.success_rating,
            'tags': [tag.name for tag in prompt.tags],
            'result_file_path': prompt.result_file_path,
            'parent_id': prompt.parent_id,
            'ai_parameters': prompt.ai_parameters,
            'api_usage': prompt.api_usage
        })
    
    return jsonify({
        'prompts': prompts,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

@api_bp.route('/tags', methods=['GET'])
def get_tags():
    """API: Tüm etiketleri getir."""
    tags = Tag.query.order_by(Tag.name).all()
    
    result = [{'id': tag.id, 'name': tag.name} for tag in tags]
    return jsonify(result)

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """API: İstatistikleri getir."""
    # Dil bazında sayım
    language_counts = db.session.query(
        Prompt.language, db.func.count(Prompt.id)
    ).group_by(Prompt.language).all()
    
    # AI üreteci bazında sayım
    ai_counts = db.session.query(
        Prompt.generator_ai, db.func.count(Prompt.id)
    ).group_by(Prompt.generator_ai).all()
    
    # From-to türleri bazında sayım
    conversion_counts = db.session.query(
        Prompt.from_type, Prompt.to_type, db.func.count(Prompt.id)
    ).group_by(Prompt.from_type, Prompt.to_type).all()
    
    # Başarı puanı ortalamaları
    avg_ratings = db.session.query(
        Prompt.generator_ai, db.func.avg(Prompt.success_rating)
    ).filter(Prompt.success_rating > 0).group_by(Prompt.generator_ai).all()
    
    # En popüler etiketler
    tag_counts = db.session.query(
        Tag.name, db.func.count(prompt_tags.c.prompt_id)
    ).join(prompt_tags).group_by(Tag.name).order_by(
        db.func.count(prompt_tags.c.prompt_id).desc()
    ).limit(10).all()
    
    result = {
        'language_counts': {lang: count for lang, count in language_counts},
        'ai_counts': {ai: count for ai, count in ai_counts},
        'conversion_counts': {f"{from_type}->{to_type}": count for from_type, to_type, count in conversion_counts},
        'avg_ratings': {ai: float(avg) for ai, avg in avg_ratings},
        'popular_tags': {tag: count for tag, count in tag_counts}
    }
    
    return jsonify(result)

@api_bp.route('/suggest-prompt', methods=['POST'])
def suggest_prompt():
    """API: Prompt önerisi oluştur."""
    data = request.get_json()
    
    # İstek verilerinden parametreleri al
    base_prompt = data.get('base_prompt', '')
    generator_ai = data.get('generator_ai', '')
    from_type = data.get('from_type', '')
    to_type = data.get('to_type', '')
    
    # Öneriyi oluştur
    suggestion = generate_prompt_suggestion(base_prompt, generator_ai, from_type, to_type)
    
    return jsonify({'suggestion': suggestion})

@api_bp.route('/prompts/<int:id>', methods=['GET'])
def get_prompt(id):
    """API: Belirli bir promptu getir."""
    prompt = Prompt.query.get_or_404(id)
    
    result = {
        'id': prompt.id,
        'date': prompt.date.isoformat(),
        'language': prompt.language,
        'description': prompt.description,
        'generator_ai': prompt.generator_ai,
        'from_type': prompt.from_type,
        'to_type': prompt.to_type,
        'prompt': prompt.prompt,
        'source': prompt.source,
        'notes': prompt.notes,
        'success_rating': prompt.success_rating,
        'tags': [tag.name for tag in prompt.tags],
        'result_file_path': prompt.result_file_path,
        'parent_id': prompt.parent_id,
        'ai_parameters': prompt.ai_parameters,
        'api_usage': prompt.api_usage
    }
    
    # Varsa versiyonları da dahil et
    versions = []
    if prompt.parent_id:
        # Bu bir alt versiyon, ana promptu ve diğer versiyonları al
        parent = prompt.parent
        versions = [
            {'id': v.id, 'description': v.description, 'date': v.date.isoformat()}
            for v in parent.versions.all()
        ]
    else:
        # Bu bir ana prompt, tüm alt versiyonları al
        versions = [
            {'id': v.id, 'description': v.description, 'date': v.date.isoformat()}
            for v in prompt.versions.all()
        ]
    
    result['versions'] = versions
    
    return jsonify(result)
