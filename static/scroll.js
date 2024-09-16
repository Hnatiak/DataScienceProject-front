document.addEventListener("DOMContentLoaded", function() {
    function scrollToBottom() {
        const container = document.querySelector('.document-container-two');
        if (container) { // Переконайтесь, що контейнер існує
            container.scrollTop = container.scrollHeight;
        } else {
            console.log('Element not found: .document-container-two');
        }
    }

    // Прокрутка вниз після завантаження сторінки
    scrollToBottom();

    // Додати спостереження за змінами у випадку асинхронного додавання
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                scrollToBottom();
            }
        });
    });

    const container = document.querySelector('.document-container-two');
    if (container) {
        observer.observe(container, { childList: true, subtree: true });
    } else {
        console.log('Element not found: .document-container-two');
    }
});