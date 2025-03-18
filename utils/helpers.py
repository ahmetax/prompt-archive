import os
import random
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

def register_template_filters(app):
    """Şablon filtrelerini kaydet."""
    
    @app.template_filter('format_date')
    def format_date(date, format='%d.%m.%Y %H:%M'):
        """Tarihleri formatlama için filtre."""
        if date:
            return date.strftime(format)
        return ''
    
    @app.template_filter('truncate_text')
    def truncate_text(text, length=100):
        """Metni belirli bir uzunlukta kesme filtresi."""
        if not text:
            return ''
        if len(text) <= length:
            return text
        return text[:length] + '...'
    
    @app.template_filter('get_file_extension')
    def get_file_extension(file_path):
        """Dosya uzantısını alma filtresi."""
        if not file_path:
            return ''
        return os.path.splitext(file_path)[1][1:].lower()
    
    @app.template_filter('is_image')
    def is_image(file_path):
        """Dosyanın resim olup olmadığını kontrol eden filtre."""
        if not file_path:
            return False
        ext = get_file_extension(file_path)
        return ext in ['jpg', 'jpeg', 'png', 'gif']
    
    @app.template_filter('is_video')
    def is_video(file_path):
        """Dosyanın video olup olmadığını kontrol eden filtre."""
        if not file_path:
            return False
        ext = get_file_extension(file_path)
        return ext in ['mp4', 'webm', 'avi', 'mov']
    
    @app.template_filter('is_audio')
    def is_audio(file_path):
        """Dosyanın ses olup olmadığını kontrol eden filtre."""
        if not file_path:
            return False
        ext = get_file_extension(file_path)
        return ext in ['mp3', 'wav', 'ogg']

def ensure_upload_directory(app):
    """Yükleme dizininin varlığını kontrol et ve yoksa oluştur."""
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

def allowed_file(filename):
    """Dosya uzantısının izin verilen uzantılardan biri olup olmadığını kontrol et."""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_prompt_suggestion(base_prompt, generator_ai, from_type, to_type):
    """Verilen parametreler ve veritabanındaki veriler doğrultusunda prompt önerisi oluştur."""
    from models import Prompt, db
    
    suggestions = []
    
    # Verilen promptla benzer promptları bul
    if base_prompt:
        similar_prompts = Prompt.query.filter(
            Prompt.prompt.ilike(f"%{base_prompt}%")
        ).order_by(db.func.random()).limit(3).all()
        
        for p in similar_prompts:
            if p.success_rating >= 3:  # Sadece başarılı promptları öner
                suggestions.append(p.prompt)
    
    # Generator AI ve dönüşüm türüne göre benzer promptları bul
    if generator_ai and from_type and to_type:
        type_prompts = Prompt.query.filter_by(
            generator_ai=generator_ai,
            from_type=from_type,
            to_type=to_type
        ).order_by(Prompt.success_rating.desc()).limit(3).all()
        
        for p in type_prompts:
            if p.success_rating >= 3 and p.prompt not in suggestions:
                suggestions.append(p.prompt)
    
    # Öneriler oluşturulamadıysa, yaratıcı bir öneri oluştur
    if not suggestions:
        ai_templates = {
            'text2image': [
                "{subject} {style} tarzında, {quality} kalitesinde, {details} detaylarla",
                "Yüksek çözünürlüklü {adjective} {subject}, {style} stili, {lighting} aydınlatma",
                "Bir {location} ortamında {action} yapan {subject}, {mood} atmosferi"
            ],
            'text2text': [
                "{tone} bir tonda {subject} hakkında {type} yaz",
                "{subject} konusunda {audience} için {word_count} kelimelik {type} oluştur",
                "{perspective} bakış açısıyla {subject} hakkında {format}"
            ],
            'text2video': [
                "{duration} süren, {subject} gösteren kısa bir video, {style} stil",
                "{motion} hareketiyle {subject} videoya dönüştür, {mood} atmosferi",
                "{camera} kamera açısından {action} yapan {subject}, {effects} efektlerle"
            ],
            'text2audio': [
                "{genre} tarzında {instrument} kullanarak {mood} bir melodi",
                "{voice} sesiyle {tone} tonda {script} seslendir",
                "{tempo} tempoda, {mood} hissi veren {length} saniye {genre} müzik"
            ]
        }
        
        template_key = f"{from_type}2{to_type}"
        if template_key in ai_templates:
            template = random.choice(ai_templates[template_key])
            
            # Şablonu doldur
            if 'text2image' in template_key:
                subjects = ['manzara', 'portre', 'natürmort', 'fantastik yaratık', 'şehir görünümü']
                styles = ['fotogerçekçi', 'yağlı boya', 'dijital sanat', 'anime', 'minimalist']
                qualities = ['ultra-yüksek', '4K', 'detaylı', 'profesyonel', 'stüdyo kalitesinde']
                details = ['ince', 'zengin', 'karmaşık', 'minimal', 'derin']
                adjectives = ['etkileyici', 'dramatik', 'sakin', 'renkli', 'karanlık']
                lightings = ['doğal', 'dramatik', 'yumuşak', 'kontrast', 'loş']
                locations = ['orman', 'şehir', 'okyanus kenarı', 'dağ zirvesi', 'fantastik dünya']
                actions = ['yürüyen', 'oturan', 'dans eden', 'uçan', 'düşünen']
                moods = ['mutlu', 'melankolik', 'gizemli', 'heyecanlı', 'sakin']
                
                suggestion = template.format(
                    subject=random.choice(subjects),
                    style=random.choice(styles),
                    quality=random.choice(qualities),
                    details=random.choice(details),
                    adjective=random.choice(adjectives),
                    lighting=random.choice(lightings),
                    location=random.choice(locations),
                    action=random.choice(actions),
                    mood=random.choice(moods)
                )
            elif 'text2text' in template_key:
                tones = ['resmi', 'samimi', 'akademik', 'mizahi', 'dramatik']
                subjects = ['yapay zeka', 'iklim değişikliği', 'sağlıklı yaşam', 'teknoloji', 'sanat']
                types = ['makale', 'hikaye', 'şiir', 'senaryo', 'mektup']
                audiences = ['çocuklar', 'yetişkinler', 'öğrenciler', 'profesyoneller', 'yaşlılar']
                word_counts = ['500', '1000', '2000', '300', '750']
                perspectives = ['birinci şahıs', 'üçüncü şahıs', 'felsefi', 'bilimsel', 'eleştirel']
                formats = ['diyalog', 'anlatı', 'liste', 'soru-cevap', 'deneme']
                
                suggestion = template.format(
                    tone=random.choice(tones),
                    subject=random.choice(subjects),
                    type=random.choice(types),
                    audience=random.choice(audiences),
                    word_count=random.choice(word_counts),
                    perspective=random.choice(perspectives),
                    format=random.choice(formats)
                )
            elif 'text2video' in template_key:
                durations = ['10 saniye', '30 saniye', '1 dakika', '15 saniye', '45 saniye']
                subjects = ['doğa manzarası', 'dans eden karakter', 'şehir turu', 'uzay yolculuğu', 'sualtı dünyası']
                styles = ['sinematik', 'animasyon', 'belgesel', 'müzik videosu', 'hızlandırılmış çekim']
                motions = ['akıcı', 'hızlı', 'yavaş', 'titreşimli', 'döngüsel']
                moods = ['neşeli', 'gizemli', 'dramatik', 'heyecanlı', 'romantik']
                cameras = ['havadan', 'göz hizasında', 'yakın çekim', 'geniş açı', 'takip']
                actions = ['koşan', 'dans eden', 'konuşan', 'uçan', 'yüzen']
                effects = ['ağır çekim', 'parıltılı', 'renkli geçişler', 'bulanıklaştırma', 'hızlandırma']
                
                suggestion = template.format(
                    duration=random.choice(durations),
                    subject=random.choice(subjects),
                    style=random.choice(styles),
                    motion=random.choice(motions),
                    mood=random.choice(moods),
                    camera=random.choice(cameras),
                    action=random.choice(actions),
                    effects=random.choice(effects)
                )
            elif 'text2audio' in template_key:
                genres = ['klasik', 'elektronik', 'caz', 'ambient', 'rock']
                instruments = ['piyano', 'gitar', 'synthesizer', 'orkestra', 'perküsyon']
                moods = ['sakin', 'enerjik', 'melankolik', 'heyecanlı', 'gizemli']
                voices = ['erkek', 'kadın', 'çocuk', 'robotik', 'derin']
                tones = ['ciddi', 'neşeli', 'dramatik', 'bilgilendirici', 'eğlenceli']
                scripts = ['hikaye', 'şiir', 'haber bülteni', 'bilimsel metin', 'diyalog']
                tempos = ['yavaş', 'orta', 'hızlı', 'değişken', 'ritmik']
                lengths = ['30', '60', '90', '120', '180']
                
                suggestion = template.format(
                    genre=random.choice(genres),
                    instrument=random.choice(instruments),
                    mood=random.choice(moods),
                    voice=random.choice(voices),
                    tone=random.choice(tones),
                    script=random.choice(scripts),
                    tempo=random.choice(tempos),
                    length=random.choice(lengths)
                )
            else:
                suggestion = "Özel bir prompt önerisi oluşturulamadı. Lütfen manuel olarak bir prompt girin."
            
            suggestions.append(suggestion)
        else:
            suggestions.append("Bu dönüşüm türü için henüz özel bir öneri şablonumuz yok.")
    
    # En iyi öneriyi seç ve döndür
    return random.choice(suggestions) if suggestions else "Prompt önerisi oluşturulamadı."

def init_app():
    """Uygulama ilk kez başlatıldığında çalıştırılacak fonksiyon."""
    from models import db, Tag
    
    # Temel etiketleri oluştur
    default_tags = [
        'portre', 'manzara', 'film', 'animasyon', 'gerçekçi', 
        'soyut', 'bilimkurgu', 'fantazi', 'minimalist', 'sanatsal',
        'profesyonel', 'eğitim', 'eğlence', 'belgesel', 'haber',
        'moda', 'mimari', 'müzik', 'spor', 'gıda'
    ]
    
    # Etiketleri veritabanına ekle
    for tag_name in default_tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
    
    db.session.commit()
