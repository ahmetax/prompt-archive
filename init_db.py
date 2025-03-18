"""
Bu script veritabanını oluşturur ve 
başlangıç için gerekli temel verileri ekler.
"""

import os
from datetime import datetime
from flask import Flask
from config import Config
from models import db, Tag, Prompt

def create_app():
    """Flask uygulamasını oluşturur."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_db():
    """Veritabanını oluşturur ve başlangıç verilerini ekler."""
    app = create_app()
    
    with app.app_context():
        # Veritabanını oluştur
        db.create_all()
        print("Veritabanı tabloları oluşturuldu.")
        
        # Temel etiketleri ekle
        tags = [
            'portre', 'manzara', 'film', 'animasyon', 'gerçekçi', 
            'soyut', 'bilimkurgu', 'fantazi', 'minimalist', 'sanatsal',
            'profesyonel', 'eğitim', 'eğlence', 'belgesel', 'haber',
            'moda', 'mimari', 'müzik', 'spor', 'gıda'
        ]
        
        for tag_name in tags:
            # Etiket yoksa ekle
            if not Tag.query.filter_by(name=tag_name).first():
                tag = Tag(name=tag_name)
                db.session.add(tag)
        
        # Örnek promptlar ekle
        example_prompts = [
            {
                'description': 'Dağ Manzarası',
                'language': 'Türkçe',
                'generator_ai': 'DALL-E 3',
                'from_type': 'text',
                'to_type': 'image',
                'prompt': 'Güneşin batışıyla birlikte altın rengi ışıkların aydınlattığı yüksek dağlar. Ön planda küçük bir göl, arka planda gökyüzünde birkaç bulut. Fotogerçekçi stil.',
                'source': 'Kendi oluşturuldu',
                'notes': 'Işık yansımaları çok başarılı. Dağların detayları gerçekçi.',
                'success_rating': 5,
                'tags': ['manzara', 'gerçekçi', 'sanatsal']
            },
            {
                'description': 'Bilimkurgu Robot Karakteri',
                'language': 'İngilizce',
                'generator_ai': 'Midjourney',
                'from_type': 'text',
                'to_type': 'image',
                'prompt': 'A highly detailed futuristic robot character with human-like features, standing in a neon-lit cyberpunk city. The robot has glowing blue eyes and metallic silver skin with some weathered parts. Cinematic lighting, shallow depth of field, 8k render.',
                'source': 'Midjourney örneklerinden uyarlandı',
                'notes': 'Robotun metalik yüzeyi ve mavi gözler iyi çalıştı, ancak arka plan biraz karışık.',
                'success_rating': 4,
                'tags': ['bilimkurgu', 'gerçekçi', 'animasyon']
            },
            {
                'description': 'Şiir Yazma',
                'language': 'Türkçe',
                'generator_ai': 'ChatGPT',
                'from_type': 'text',
                'to_type': 'text',
                'prompt': 'Doğanın uyanışını anlatan, her dizesi 7 heceli olan 4 kıtalık bir şiir yaz. Şiirde ilkbaharın getirdiği canlılık teması işlensin.',
                'source': 'Kendi oluşturuldu',
                'notes': 'Tema ve duygu aktarımı çok başarılı. Hece ölçüsü tam istediğim gibi.',
                'success_rating': 5,
                'tags': ['profesyonel', 'eğitim', 'sanatsal']
            },
            {
                'description': 'Kısa Film Senaryosu',
                'language': 'Türkçe',
                'generator_ai': 'Claude',
                'from_type': 'text',
                'to_type': 'text',
                'prompt': 'İki yabancının şehrin kalabalık bir meydanında tesadüfen karşılaşmasıyla başlayan ve günün sonunda tekrar ayrılmalarıyla biten 5 dakikalık bir kısa film senaryosu yaz. Diyaloglar minimal olsun, görsel anlatıma ağırlık verilsin.',
                'source': 'Senaryo yazım dersinden',
                'notes': 'Karakterlerin derinliği ve görsel anlatım çok iyi. Diyaloglar biraz uzun olmuş.',
                'success_rating': 4,
                'tags': ['film', 'profesyonel', 'eğlence']
            },
            {
                'description': 'Akustik Gitar Melodisi',
                'language': 'İngilizce',
                'generator_ai': 'Elevenlabs',
                'from_type': 'text',
                'to_type': 'audio',
                'prompt': 'Create a peaceful acoustic guitar melody with a slow tempo. The melody should evoke a sense of nostalgia and calmness, perfect for a sunset scene. Include some light finger-picking patterns and occasional harmonics. Duration should be around 45 seconds.',
                'source': 'Müzik üretimi araştırması',
                'notes': 'Ton ve duygu harika ancak parmak vuruş geçişleri biraz yapay.',
                'success_rating': 3,
                'tags': ['müzik', 'sanatsal', 'minimal']
            }
        ]
        
        for prompt_data in example_prompts:
            # Yeni prompt oluştur
            prompt = Prompt(
                description=prompt_data['description'],
                language=prompt_data['language'],
                generator_ai=prompt_data['generator_ai'],
                from_type=prompt_data['from_type'],
                to_type=prompt_data['to_type'],
                prompt=prompt_data['prompt'],
                source=prompt_data['source'],
                notes=prompt_data['notes'],
                success_rating=prompt_data['success_rating'],
                date=datetime.utcnow()
            )
            
            # Etiketleri ekle
            for tag_name in prompt_data['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    prompt.tags.append(tag)
            
            db.session.add(prompt)
        
        # Değişiklikleri kaydet
        db.session.commit()
        print("Temel veriler eklendi.")

if __name__ == '__main__':
    init_db()
    print("Veritabanı başlatıldı!")
