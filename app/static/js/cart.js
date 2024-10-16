// cart.js

document.addEventListener('DOMContentLoaded', function () {
    // Écouter les clics sur les boutons "Ajouter au panier"
    document.querySelectorAll('.add-to-cart-button').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Empêche la redirection par défaut
            const offerId = button.dataset.offerId; // Récupérer l'ID de l'offre à partir de l'attribut data-offer-id
            addToCart(offerId); // Appeler la fonction pour ajouter au panier
        });
    });

    //   // Écouter les clics sur les boutons d'incrémentation et de décrémentation
    //   document.querySelectorAll('.update-cart').forEach(button => {
    //     button.addEventListener('click', (event) => {
    //         const itemId = button.getAttribute('data-id');
    //         const action = button.getAttribute('data-action');
    //         updateCart(itemId, action);
    //     });
    // });

    // Écouter les clics sur les boutons de suppression du panier
    // document.querySelectorAll('.remove-from-cart').forEach(button => {
    //     button.addEventListener('click', (event) => {
    //         const itemId = button.getAttribute('data-id');
    //         removeFromCart(itemId);
    //     });
    // });
});


// ############### ad to cart
function addToCart(offerId) {
    fetch(`/add_to_cart/${offerId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken() // Gestion du CSRF si nécessaire
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Récupérer la réponse JSON
        }
        throw new Error('Erreur lors de l\'ajout au panier.');
    })
    .then(data => {
        if (data.success) {
            alert(data.message); // Afficher un message de succès
            // updateCart(offerId); // Mettre à jour l'affichage du panier si nécessaire
        } else {
            alert('Erreur : ' + data.message); // Afficher un message d'erreur
        }
    })
    .catch(error => console.error('Erreur:', error));
}


// function updateCart(offerId, action) {
//     fetch(`/update_panier/${offerId}`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCsrfToken() // Gestion du CSRF si nécessaire
//         },
//         body: JSON.stringify({ action: action }) // Envoie l'action en JSON
//     })
//     .then(response => {
//         if (response.ok) {
//             return response.json(); // Récupérer la réponse JSON
//         }
//         throw new Error('Erreur lors de la mise à jour du panier.');
//     })
//     .then(data => {
//         if (data.success) {
//             // Logique pour mettre à jour le DOM
//         } else {
//             alert('Erreur : ' + data.message); // Afficher un message d'erreur
//         }
//     })
//     .catch(error => console.error('Erreur:', error));
// }
 
// ####################################################################
// ####################################################################

// function removeFromCart(itemId) {
//     fetch(`/remove_from_panier/${itemId}`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCsrfToken() // Gestion du CSRF si nécessaire
//         }
//     })
//     .then(response => {
//         if (response.ok) {
//             return response.json(); // Récupérer la réponse JSON
//         }
//         throw new Error('Erreur lors de la suppression du produit.');
//     })
//     .then(data => {
//         if (data.success) {
//             // Supprimer la ligne correspondante du tableau
//             const row = document.querySelector(`tr[data-id='${itemId}']`);
//             row.remove(); // Retirer la ligne du tableau
//             // Mettre à jour le total général si nécessaire
//             document.querySelector('h3').textContent = `Total : ${data.new_total} €`;
//         } else {
//             alert('Erreur : ' + data.message); // Afficher un message d'erreur
//         }
//     })
//     .catch(error => console.error('Erreur:', error));
// }

function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    return csrfInput ? csrfInput.value : '';
}

// function updateCartItemDisplay(offerId, item) {
//     const quantiteElement = document.getElementById(`quantite-${offerId}`);
//     const totalElement = document.getElementById(`total-${offerId}`);
    
//     if (item) {
//         quantiteElement.textContent = item.quantite;
//         totalElement.textContent = (item.quantite * item.price).toFixed(2);
//     } else {
//         removeCartItem(offerId);
//     }
// }

// function removeCartItem(offerId) {
//     const row = document.querySelector(`[data-id="${offerId}"]`).closest('tr');
//     if (row) {
//         row.remove();
//     }
// }



// document.querySelectorAll('.update-panier-form').forEach(form => {
//     form.addEventListener('submit', function(e) {
//         e.preventDefault(); // Empêche le rechargement de la page
//         const formData = new FormData(form);

//         fetch(form.action, {
//             method: 'POST',
//             body: formData
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 // Met à jour le total dans l'affichage
//                 document.getElementById(`quantite-${form.action.split('/').pop()}`).textContent = data.total;
//                 // Tu pourrais aussi mettre à jour le total du panier ici
//             } else {
//                 alert('Erreur lors de la mise à jour du panier.');
//             }
//         })
//         .catch(error => console.error('Erreur:', error));
//     });
// });
// function debounce(func, delay) {
//     let timeout;
//     return function(...args) {
//         const context = this;
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func.apply(context, args), delay);
//     };
// }

// document.querySelectorAll('.update-panier-form').forEach(form => {
//     form.addEventListener('click', debounce((event) => {
//         if (event.target.classList.contains('update-cart')) {
//             event.preventDefault(); // Empêche le comportement par défaut du bouton
            
//             console.log('Bouton cliqué'); // Log pour vérifier si l'événement se déclenche

//             const itemId = form.querySelector('input[name="item_id"]').value;
//             const action = event.target.getAttribute('data-action'); // Récupérer l'action

//             // Effectuer une requête AJAX pour mettre à jour le panier
//             fetch(`/update_panier/${itemId}`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/x-www-form-urlencoded',
//                     'X-CSRFToken': form.querySelector('input[name="csrf_token"]').value
//                 },
//                 body: new URLSearchParams({ action: action }) // Envoie l'action en tant que paramètre de formulaire
//             })
//             .then(response => {
//                 if (!response.ok) {
//                     throw new Error('Erreur réseau');
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 console.log('Réponse du serveur:', data); // Log pour vérifier la réponse du serveur
//                 if (data.success) {
//                     // Mettre à jour la quantité dans le DOM si besoin
//                     // alert(data.message || 'Aucun message fourni');
//                     document.getElementById(`quantite-${itemId}`).textContent = data.newQuantity;
//                     document.getElementById(`total-${itemId}`).textContent = data.total;

//                 } else {
//                     alert('Erreur : ' + data.message); // Afficher un message d'erreur
//                 }
//             })
//             .catch(error => console.error('Erreur:', error));
//         }
//     }, 300)); // Utilisation d'un debounce pour limiter les appels
// });



