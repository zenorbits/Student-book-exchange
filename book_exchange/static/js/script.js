document.addEventListener('DOMContentLoaded', () => {
    // 1. Image preview functionality
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            } else {
                imagePreview.src = '#';
                imagePreview.style.display = 'none';
            }
        });
    }

    // 2. Form validation for Post/Edit Ad
    const adForm = document.getElementById('ad-form');
    if (adForm) {
        adForm.addEventListener('submit', function(e) {
            const priceInput = document.getElementById('price');
            if (parseFloat(priceInput.value) < 0) {
                e.preventDefault();
                alert('Price cannot be negative.');
            }
        });
    }

    // 3. Live filtering on Homepage
    const searchInput = document.getElementById('search-input');
    const subjectFilter = document.getElementById('subject-filter');
    const conditionFilter = document.getElementById('condition-filter');
    const listingsGrid = document.getElementById('listings-grid');

    if (listingsGrid) {
        const fetchListings = () => {
            const search = searchInput.value;
            const subject = subjectFilter.value;
            const condition = conditionFilter.value;

            const url = new URL('/api/listings', window.location.origin);
            if (search) url.searchParams.append('search', search);
            if (subject) url.searchParams.append('subject', subject);
            if (condition) url.searchParams.append('condition', condition);

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    listingsGrid.innerHTML = '';
                    if (data.length === 0) {
                        listingsGrid.innerHTML = '<div class="col-12"><p class="text-center text-muted">No books found matching your criteria.</p></div>';
                        return;
                    }

                    data.forEach(book => {
                        const imagePath = book.image_path ? `/static/${book.image_path}` : 'https://via.placeholder.com/300x200?text=No+Image';
                        const card = `
                            <div class="col-md-4 mb-4">
                                <div class="card h-100 book-card position-relative">
                                    <img src="${imagePath}" class="card-img-top" alt="${book.title}">
                                    <div class="card-body d-flex flex-column">
                                        <h5 class="card-title">${book.title}</h5>
                                        <h6 class="card-subtitle mb-2 text-muted">By ${book.author}</h6>
                                        <p class="card-text mb-1"><strong>Price:</strong> $${book.price.toFixed(2)}</p>
                                        <p class="card-text mb-1"><span class="badge bg-info text-dark">${book.subject || 'General'}</span> <span class="badge bg-secondary">${book.condition}</span></p>
                                        <div class="mt-auto pt-3">
                                            <a href="/listing/${book.id}" class="btn btn-primary w-100">View Details</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                        listingsGrid.insertAdjacentHTML('beforeend', card);
                    });
                })
                .catch(error => console.error('Error fetching listings:', error));
        };

        // Add event listeners for live filtering
        if (searchInput) searchInput.addEventListener('input', fetchListings);
        if (subjectFilter) subjectFilter.addEventListener('change', fetchListings);
        if (conditionFilter) conditionFilter.addEventListener('change', fetchListings);
        
        // Initial load
        fetchListings();
    }
});
