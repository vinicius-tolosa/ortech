window.toggleTheme = function() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    html.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
};

document.addEventListener("DOMContentLoaded", function() {
    const catalogSliders = document.querySelectorAll('.product-slider');
    catalogSliders.forEach(slider => {
        const images = slider.querySelectorAll('.product-slide-img');
        if (images.length > 1) {
            let currentIndex = 0;
            setInterval(() => {
                images[currentIndex].classList.remove('active');
                currentIndex = (currentIndex + 1) % images.length;
                images[currentIndex].classList.add('active');
            }, 3000);
        }
    });

    const detailSlides = document.querySelectorAll('.slider-img');
    if (detailSlides.length > 0) {
        let currentSlideIndex = 0;
        let autoSlideTimer = null;

        function showSlide(index) {
            const dots = document.querySelectorAll('.dot');
            if (index >= detailSlides.length) { currentSlideIndex = 0; }
            else if (index < 0) { currentSlideIndex = detailSlides.length - 1; }
            else { currentSlideIndex = index; }

            detailSlides.forEach((slide, i) => {
                slide.classList.toggle('active', i === currentSlideIndex);
            });

            dots.forEach((dot, i) => {
                dot.classList.toggle('active', i === currentSlideIndex);
            });
        }

        window.moveSlide = function(step) {
            showSlide(currentSlideIndex + step);
            resetAutoSlide();
        };

        window.goToSlide = function(element) {
            const index = parseInt(element.getAttribute('data-index'), 10);
            showSlide(index);
            resetAutoSlide();
        };

        function startAutoSlide() {
            if (detailSlides.length > 1) {
                autoSlideTimer = setInterval(() => {
                    showSlide(currentSlideIndex + 1);
                }, 3500);
            }
        }

        function resetAutoSlide() {
            if (autoSlideTimer) {
                clearInterval(autoSlideTimer);
                startAutoSlide();
            }
        }

        showSlide(0);
        startAutoSlide();
    }
});

const subcategoriesData = {
    relogio: [
        { value: "smartwatch", text: "Smartwatch" },
        { value: "analogico", text: "Relógio Analógico" }
    ],
    acessorio: [
        { value: "celular", text: "Acessório para Celulares" },
        { value: "relogios", text: "Acessório para Relógios" },
        { value: "diverso", text: "Acessórios Diversos" }
    ]
};

window.updateSubcategories = function(selectedSub = "") {
    const categorySelect = document.getElementById('product-category');
    const subcategorySelect = document.getElementById('product-subcategory');
    if (!categorySelect || !subcategorySelect) return;
    const selectedCategory = categorySelect.value;

    subcategorySelect.innerHTML = '<option value="">Selecione o tipo...</option>';

    if (subcategoriesData[selectedCategory]) {
        subcategoriesData[selectedCategory].forEach(sub => {
            const option = document.createElement('option');
            option.value = sub.value;
            option.textContent = sub.text;
            if (sub.value === selectedSub) {
                option.selected = true;
            }
            subcategorySelect.appendChild(option);
        });
    }
};

window.updateEditSubcategories = function(selectedSub = "") {
    const categorySelect = document.getElementById('edit-product-category');
    const subcategorySelect = document.getElementById('edit-product-subcategory');
    if (!categorySelect || !subcategorySelect) return;
    const selectedCategory = categorySelect.value;

    subcategorySelect.innerHTML = '<option value="">Selecione o tipo...</option>';

    if (subcategoriesData[selectedCategory]) {
        subcategoriesData[selectedCategory].forEach(sub => {
            const option = document.createElement('option');
            option.value = sub.value;
            option.textContent = sub.text;
            if (sub.value === selectedSub) {
                option.selected = true;
            }
            subcategorySelect.appendChild(option);
        });
    }
};

window.openEditModalFromButton = function(button) {
    window.openEditModal(
        button.getAttribute('data-id'),
        button.getAttribute('data-name'),
        button.getAttribute('data-sku'),
        button.getAttribute('data-price'),
        button.getAttribute('data-discount'),
        button.getAttribute('data-colors'),
        button.getAttribute('data-category'),
        button.getAttribute('data-subcategory'),
        button.getAttribute('data-image'),
        button.getAttribute('data-description') // Capturando a descrição
    );
};

window.previewSlotImage = function(input, slotNum) {
    const slot = document.getElementById(`slot-${slotNum}`);
    if (slot && input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let img = slot.querySelector('img');
            if (!img) {
                img = document.createElement('img');
                slot.appendChild(img);
            }
            img.src = e.target.result;
            slot.classList.add('has-image');
        };
        reader.readAsDataURL(input.files[0]);
    }
};

window.clearSlot = function(event, slotNum) {
    event.stopPropagation();
    const slot = document.getElementById(`slot-${slotNum}`);
    if (slot) {
        const input = slot.querySelector('input[type="file"]');
        if (input) input.value = '';
        const img = slot.querySelector('img');
        if (img) img.remove();
        slot.classList.remove('has-image');
    }
};

window.previewEditSlotImage = function(input, slotNum) {
    const slot = document.getElementById(`edit-slot-${slotNum}`);
    if (slot && input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let img = slot.querySelector('img');
            if (!img) {
                img = document.createElement('img');
                slot.appendChild(img);
            }
            img.src = e.target.result;
            slot.removeAttribute('data-existing-url');
            slot.classList.add('has-image');
        };
        reader.readAsDataURL(input.files[0]);
    }
};

window.clearEditSlot = function(event, slotNum) {
    event.stopPropagation();
    const slot = document.getElementById(`edit-slot-${slotNum}`);
    if (slot) {
        const input = slot.querySelector('input[type="file"]');
        if (input) input.value = '';
        const img = slot.querySelector('img');
        if (img) img.remove();
        slot.removeAttribute('data-existing-url');
        slot.classList.remove('has-image');
    }
};

window.openEditModal = function(id, name, sku, price, discount, colors, category, subcategory, imageUrls, description) {
    const idInput = document.getElementById('edit-product-id');
    const nameInput = document.getElementById('edit-name');
    const skuInput = document.getElementById('edit-sku');
    const priceInput = document.getElementById('edit-price');
    const discountInput = document.getElementById('edit-discount');
    const colorsInput = document.getElementById('edit-colors');
    const descriptionInput = document.getElementById('edit-description'); // Campo de descrição do modal
    const catSelect = document.getElementById('edit-product-category');
    const modal = document.getElementById('editModal');

    if (idInput) idInput.value = id;
    if (nameInput) nameInput.value = name;
    if (skuInput) skuInput.value = sku;
    if (priceInput) priceInput.value = price;
    if (discountInput) discountInput.value = discount;
    if (colorsInput) colorsInput.value = colors;
    if (descriptionInput) descriptionInput.value = description || ''; // Inserindo a descrição no textarea
    
    if (catSelect) {
        catSelect.value = category;
        window.updateEditSubcategories(subcategory);
    }

    for (let i = 1; i <= 6; i++) {
        const slot = document.getElementById(`edit-slot-${i}`);
        if (slot) {
            const input = slot.querySelector('input[type="file"]');
            if (input) input.value = '';
            const img = slot.querySelector('img');
            if (img) img.remove();
            slot.removeAttribute('data-existing-url');
            slot.classList.remove('has-image');
        }
    }

    if (imageUrls) {
        const urls = imageUrls.split(',');
        urls.forEach((url, index) => {
            const slotNum = index + 1;
            if (slotNum <= 6) {
                const slot = document.getElementById(`edit-slot-${slotNum}`);
                if (slot) {
                    let img = slot.querySelector('img');
                    if (!img) {
                        img = document.createElement('img');
                        slot.appendChild(img);
                    }
                    const cleanUrl = url.trim();
                    img.src = cleanUrl;
                    slot.setAttribute('data-existing-url', cleanUrl);
                    slot.classList.add('has-image');
                }
            }
        });
    }
    
    if (modal) modal.style.display = 'flex';
};

window.closeEditModal = function() {
    const modal = document.getElementById('editModal');
    if (modal) modal.style.display = 'none';
};

window.prepareEditFormSubmit = function() {
    const container = document.getElementById('edit-existing-images-container');
    if (!container) return;
    container.innerHTML = '';
    
    for (let i = 1; i <= 6; i++) {
        const slot = document.getElementById(`edit-slot-${i}`);
        if (slot) {
            const existingUrl = slot.getAttribute('data-existing-url');
            const hasImg = slot.querySelector('img');
            
            if (existingUrl && hasImg) {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'kept_existing_images';
                hiddenInput.value = existingUrl;
                container.appendChild(hiddenInput);
            }
        }
    }
};