// Custom JavaScript for the advertisement website

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Image preview functionality
function previewImages(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var preview = document.getElementById('imagePreview');
            var img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'img-thumbnail mb-2';
            img.style.maxWidth = '200px';
            img.style.maxHeight = '200px';
            preview.appendChild(img);
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Search functionality with debouncing
let searchTimeout;
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                performSearch(searchInput.value);
            }, 500);
        });
    }
}

function performSearch(query) {
    if (query.length < 2) return;
    
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="alert alert-info">Хайлт илэрц олдсонгүй</div>';
        return;
    }
    
    results.forEach(function(result) {
        const resultItem = createSearchResultItem(result);
        resultsContainer.appendChild(resultItem);
    });
}

function createSearchResultItem(result) {
    const div = document.createElement('div');
    div.className = 'search-result-item p-3 border-bottom';
    
    const title = document.createElement('h6');
    title.textContent = result.title;
    title.className = 'mb-1';
    
    const category = document.createElement('small');
    category.textContent = result.category;
    category.className = 'text-muted d-block';
    
    const price = document.createElement('strong');
    price.textContent = result.price ? `${result.price.toLocaleString()} ₮` : 'Үнэ тохирно';
    price.className = 'text-primary d-block';
    
    div.appendChild(title);
    div.appendChild(category);
    div.appendChild(price);
    
    div.addEventListener('click', function() {
        window.location.href = `/ad/${result.id}`;
    });
    
    return div;
}

// Filter functionality
function setupFilters() {
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('change', function() {
            applyFilters();
        });
    }
}

function applyFilters() {
    const formData = new FormData(document.getElementById('filterForm'));
    const params = new URLSearchParams(formData);
    
    window.location.href = `${window.location.pathname}?${params.toString()}`;
}

// Advertisement actions
function saveAd(adId) {
    fetch(`/api/save-ad/${adId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Зар хадгалагдлаа', 'success');
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error saving ad:', error);
        showNotification('Алдаа гарлаа', 'error');
    });
}

function shareAd(adId) {
    const url = `${window.location.origin}/ad/${adId}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Зар хуваалцах',
            text: 'Та энэ зарыг үзнэ үү',
            url: url
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(url).then(function() {
            showNotification('Холбоос хуулагдлаа', 'success');
        });
    }
}

function reportAd(adId) {
    const reason = prompt('Та ямар шалтгаанаар репортлох вэ?');
    if (reason) {
        fetch(`/api/report-ad/${adId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ reason: reason })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Репорт илгээгдлээ', 'success');
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error reporting ad:', error);
            showNotification('Алдаа гарлаа', 'error');
        });
    }
}

// Utility functions
function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main .container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            alertDiv.remove();
        }, 5000);
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Price formatting
function formatPrice(price) {
    if (!price) return 'Үнэ тохирно';
    return new Intl.NumberFormat('mn-MN').format(price) + ' ₮';
}

// Date formatting
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('mn-MN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Lazy loading for images
function setupLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Infinite scroll for pagination
function setupInfiniteScroll() {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;
    
    const nextPageLink = paginationContainer.querySelector('.page-item.active + .page-item .page-link');
    if (!nextPageLink) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadMoreAds(nextPageLink.href);
                observer.unobserve(entry.target);
            }
        });
    });
    
    const sentinel = document.createElement('div');
    sentinel.style.height = '100px';
    paginationContainer.parentNode.insertBefore(sentinel, paginationContainer);
    observer.observe(sentinel);
}

function loadMoreAds(url) {
    fetch(url)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newAds = doc.querySelectorAll('.ad-card');
            
            const container = document.querySelector('.ads-container');
            newAds.forEach(ad => {
                ad.classList.add('fade-in');
                container.appendChild(ad);
            });
            
            // Update pagination
            const newPagination = doc.querySelector('.pagination');
            if (newPagination) {
                document.querySelector('.pagination').replaceWith(newPagination);
                setupInfiniteScroll();
            }
        })
        .catch(error => {
            console.error('Error loading more ads:', error);
        });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupSearch();
    setupFilters();
    setupLazyLoading();
    setupInfiniteScroll();
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Handle browser back/forward buttons
window.addEventListener('popstate', function(event) {
    if (event.state) {
        // Reload the page content based on the state
        window.location.reload();
    }
});

// Performance monitoring
window.addEventListener('load', function() {
    if (window.performance && window.performance.timing) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log('Page load time:', loadTime + 'ms');
    }
});
