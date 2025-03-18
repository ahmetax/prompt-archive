/**
 * Prompt Arşivi - Ana JavaScript dosyası
 */

document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips başlat
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Flash mesajları için otomatik kapatma
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000); // 5 saniye sonra kapat
    });
    
    // Textarea otomatik genişletme
    const autoResizeTextareas = document.querySelectorAll('textarea.auto-resize');
    autoResizeTextareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight + 2) + 'px';
        });
        
        // Sayfa yüklendiğinde de çalıştır
        textarea.dispatchEvent(new Event('input'));
    });
    
    // Dosya yükleme önizlemesi
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const previewContainer = this.parentElement.querySelector('.file-preview');
            if (!previewContainer) return;
            
            previewContainer.innerHTML = '';
            
            // Dosya türüne göre önizleme oluştur
            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.classList.add('img-thumbnail', 'mt-2');
                img.style.maxHeight = '200px';
                img.file = file;
                previewContainer.appendChild(img);
                
                const reader = new FileReader();
                reader.onload = (function(aImg) {
                    return function(e) {
                        aImg.src = e.target.result;
                    };
                })(img);
                reader.readAsDataURL(file);
            } else if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.classList.add('img-thumbnail', 'mt-2');
                video.style.maxHeight = '200px';
                video.controls = true;
                previewContainer.appendChild(video);
                
                const reader = new FileReader();
                reader.onload = (function(aVideo) {
                    return function(e) {
                        aVideo.src = e.target.result;
                    };
                })(video);
                reader.readAsDataURL(file);
            } else if (file.type.startsWith('audio/')) {
                const audio = document.createElement('audio');
                audio.classList.add('w-100', 'mt-2');
                audio.controls = true;
                previewContainer.appendChild(audio);
                
                const reader = new FileReader();
                reader.onload = (function(aAudio) {
                    return function(e) {
                        aAudio.src = e.target.result;
                    };
                })(audio);
                reader.readAsDataURL(file);
            } else {
                const fileInfo = document.createElement('div');
                fileInfo.classList.add('alert', 'alert-info', 'mt-2');
                fileInfo.innerHTML = `<i class="fas fa-file me-2"></i>${file.name} (${formatFileSize(file.size)})`;
                previewContainer.appendChild(fileInfo);
            }
        });
    });
    
    // Format alanları için etiket ve ipucu oluşturma 
    const formatFields = document.querySelectorAll('[data-format]');
    formatFields.forEach(function(field) {
        const format = field.getAttribute('data-format');
        
        if (format === 'json') {
            field.addEventListener('blur', function() {
                try {
                    if (this.value) {
                        const formattedJson = JSON.stringify(JSON.parse(this.value), null, 2);
                        this.value = formattedJson;
                    }
                } catch (e) {
                    console.error('JSON formatlama hatası:', e);
                }
            });
        }
    });
    
    // Özel prompt öneri butonları
    const suggestButtons = document.querySelectorAll('.suggest-prompt-btn');
    suggestButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const targetInput = document.querySelector(this.getAttribute('data-target'));
            if (!targetInput) return;
            
            const data = {
                generator_ai: document.querySelector('#generator_ai').value,
                from_type: document.querySelector('#from_type').value,
                to_type: document.querySelector('#to_type').value,
                base_prompt: targetInput.value
            };
            
            fetch('/api/suggest-prompt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.suggestion) {
                    targetInput.value = data.suggestion;
                    targetInput.dispatchEvent(new Event('input')); // Autosize için
                }
            })
            .catch(error => {
                console.error('Öneri API hatası:', error);
            });
        });
    });
});

/**
 * Dosya boyutunu formatlama
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Metni panoya kopyalama
 */
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    // Başarı bildirimi
    showNotification('Kopyalandı!', 'success');
}

/**
 * Bildirim gösterme
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed bottom-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s ease';
        
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, duration);
}

/**
 * Etiket seçimi
 */
function toggleTag(tagElement) {
    tagElement.classList.toggle('bg-primary');
    tagElement.classList.toggle('bg-secondary');
    
    // Etiket giriş alanını güncelle
    const tagsInput = document.querySelector('#tags');
    if (!tagsInput) return;
    
    const tagName = tagElement.textContent.trim();
    const currentTags = tagsInput.value.split(',').map(t => t.trim()).filter(t => t);
    
    if (tagElement.classList.contains('bg-primary')) {
        // Ekle
        if (!currentTags.includes(tagName)) {
            currentTags.push(tagName);
        }
    } else {
        // Çıkar
        const index = currentTags.indexOf(tagName);
        if (index !== -1) {
            currentTags.splice(index, 1);
        }
    }
    
    tagsInput.value = currentTags.join(', ');
}
