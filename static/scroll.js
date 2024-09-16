// document.addEventListener("DOMContentLoaded", function() {
//     const container = document.querySelector('.document-container');

//     function adjustHeight() {
//         if (container.scrollHeight < 730) {
//             container.style.height = '730px';
//         } else {
//             container.style.height = 'none';
//         }
//     }

//     adjustHeight();

//     const observer = new MutationObserver(adjustHeight);
//     observer.observe(container, { childList: true, subtree: true });
// });


document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector('.document-container');

    function createMessageComponent() {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message-component');
        messageDiv.textContent = 'Оберіть pdf-файл, щоб розпочати чаклунство';
        return messageDiv;
    }

    function removeMessageComponent() {
        const messageDiv = container.querySelector('.message-component');
        if (messageDiv) {
            messageDiv.remove();
        }
    }

    function adjustHeight() {
        if (container.scrollHeight < 730) {
            container.style.height = '730px';
            container.style.display = 'flex';
            container.style.justifyContent = 'center';
            container.style.alignItems = 'center';
            if (!container.querySelector('.message-component')) {
                container.appendChild(createMessageComponent());
            }
        } else {
            container.style.height = 'none';
            removeMessageComponent();
        }
    }

    adjustHeight();

    const observer = new MutationObserver(adjustHeight);
    observer.observe(container, { childList: true, subtree: true });
});

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