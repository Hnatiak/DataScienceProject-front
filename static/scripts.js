document.getElementById('uploadForm').addEventListener('submit', function(event) {
    document.getElementById('loading-spinner').style.display = 'flex';
    document.getElementById('loading-spinner').style.alignItems = 'center';
    document.getElementById('loading-spinner').style.justifyContent = 'center';
    document.getElementById('loading-spinner').style.flexDirection = 'column';
    document.getElementById('loading-spinner').style.gap = '15px';
    event.target.querySelector('button[type="submit"]').disabled = true;
});

document.getElementById('form-ask-user').addEventListener('submit', function(event) {
    document.getElementById('loading-spinner').style.display = 'flex';
    document.getElementById('loading-spinner').style.alignItems = 'center';
    document.getElementById('loading-spinner').style.justifyContent = 'center';
    document.getElementById('loading-spinner').style.flexDirection = 'column';
    document.getElementById('loading-spinner').style.gap = '15px';
    event.target.querySelector('button[type="submit"]').disabled = true;
});

document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form.form-ask-user');
    var loadingSpinner = document.getElementById('loading-answear');

    form.addEventListener('submit', function() {
        loadingSpinner.style.display = 'flex';
        loadingSpinner.style.alignItems = 'center';
        loadingSpinner.style.justifyContent = 'center';
        loadingSpinner.style.flexDirection = 'column';
        loadingSpinner.style.gap = '15px';
    });
});

document.getElementById('pdf').addEventListener('change', function() {
    var fileName = this.files.length > 0 ? this.files[0].name : 'Нічого не вибрано';
    document.getElementById('fileName').textContent = fileName;
});