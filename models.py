from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Etiketler ve promptlar arasındaki many-to-many ilişki için ara tablo
prompt_tags = db.Table(
    'prompt_tags',
    db.Column('prompt_id', db.Integer, db.ForeignKey('prompt.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Prompt(db.Model):
    """Prompt ve ilgili veri modeli."""
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    language = db.Column(db.String(20), index=True, default='Türkçe')  # Türkçe/İngilizce
    description = db.Column(db.Text, nullable=False)
    generator_ai = db.Column(db.String(100), index=True, nullable=False)  # Hangi AI kullanıldı
    from_type = db.Column(db.String(20), index=True, nullable=False)  # text/image/audio/video/other
    to_type = db.Column(db.String(20), index=True, nullable=False)    # text/image/audio/video/other
    prompt = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(255))  # Prompt kaynağı
    notes = db.Column(db.Text)
    
    # Yeni önerilen alanlar
    success_rating = db.Column(db.Integer, default=0)  # 0-5 arası başarı puanı
    result_file_path = db.Column(db.String(255))  # Oluşturulan içeriğin dosya yolu
    parent_id = db.Column(db.Integer, db.ForeignKey('prompt.id'))  # Versiyon takibi için
    ai_parameters = db.Column(db.Text)  # JSON olarak saklanabilir (temperature, top_p vb.)
    api_usage = db.Column(db.Text)  # JSON olarak token sayısı, kullanım ücreti vb.
    
    # İlişkiler
    tags = db.relationship('Tag', secondary=prompt_tags, 
                          backref=db.backref('prompts', lazy='dynamic'))
    versions = db.relationship('Prompt', 
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    
    def __repr__(self):
        return f'<Prompt {self.id}: {self.description[:30]}...>'
    
    @property
    def tag_list(self):
        """Etiketleri virgülle ayrılmış string olarak döndürür."""
        return ', '.join([tag.name for tag in self.tags])

class Tag(db.Model):
    """Etiket modeli."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Tag {self.name}>'

# Promptlar için istatistikleri önbelleğe alma (caching) sınıfı
class PromptStats(db.Model):
    """Prompt istatistiklerinin önbelleği."""
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    stats_data = db.Column(db.Text)  # JSON formatında istatistikler
    
    def __repr__(self):
        return f'<PromptStats {self.date}>'
