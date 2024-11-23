document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            const params = new URLSearchParams(currentUrl.search);
            
            if (this.value) {
                params.set('sort', this.value);
            } else {
                params.delete('sort');
            }
            
            currentUrl.search = params.toString();
            window.location.href = currentUrl.toString();
        });
    }
}); 