function deleteOffer(offerId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette offre ?')) {
        fetch(`{{ url_for('admin.delete_offer', offer_id='') }}/${offerId}`, {
            method: 'POST', // Ou 'DELETE' selon ce que vous préférez
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()  // Ajoutez le token CSRF si nécessaire
            },
            body: JSON.stringify({})  // Ajoutez un corps si nécessaire
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert("Erreur lors de la suppression de l'offre.");
            }
        })
        .catch(error => console.error('Erreur:', error));
    }
}

function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    return csrfInput ? csrfInput.value : '';
}