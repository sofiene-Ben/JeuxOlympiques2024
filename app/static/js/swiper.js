// // var swiper = new Swiper(".mySwiper", {
// //     slidesPerView: 3,
// //     spaceBetween: 10,
// //     // slidesPerGroup: 1,
// //     loop: true,
// //     loopFillGroupWithBlank: true,
// //     pagination: {
// //       el: ".swiper-pagination",
// //       clickable: true,
// //     },
// //     navigation: {
// //       nextEl: ".swiper-button-next",
// //       prevEl: ".swiper-button-prev",
// //     },
// //   });
//   // Créez une media query pour détecter les écrans de moins de 768px de largeur
// const mediaQuery = window.matchMedia('(max-width: 768px)');
// const mediaQuery2 = window.matchMedia('(max-width: 990px)');


// // Fonction de callback qui sera appelée lorsque la media query change
// function handleTabletChange(e) {
//     if (e.matches) {
//         // Si la media query correspond, appliquez des actions spécifiques
//         var swiper = new Swiper(".mySwiper", {
//             slidesPerView: 1,
//             spaceBetween: 10,
//             // slidesPerGroup: 1,
//             loop: true,
//             loopFillGroupWithBlank: true,
//             pagination: {
//               el: ".swiper-pagination",
//               clickable: true,
//             },
//             navigation: {
//               nextEl: ".swiper-button-next",
//               prevEl: ".swiper-button-prev",
//             },
//           });
        
//         // Exécutez le code que vous souhaitez exécuter pour cette taille d’écran
//     } else {
//         // Si la media query ne correspond plus
//         var swiper = new Swiper(".mySwiper", {
//             slidesPerView: 2,
//             spaceBetween: 10,
//             slidesPerGroup: 1,
//             loop: true,
//             loopFillGroupWithBlank: true,
//             pagination: {
//               el: ".swiper-pagination",
//               clickable: true,
//             },
//             navigation: {
//               nextEl: ".swiper-button-next",
//               prevEl: ".swiper-button-prev",
//             },
//           });
        
//         // Exécutez le code pour la taille d’écran large
//     } else {

//     }
// }

// // Vérifiez initialement l'état de la media query
// handleTabletChange(mediaQuery);
// handleTabletChange(mediaQuery2);


// // Écoutez les changements de la media query
// mediaQuery.addEventListener('change', handleTabletChange);


// Créez les media queries pour détecter les écrans de différentes tailles
const mediaQueryTablet = window.matchMedia('(max-width: 768px)');
const mediaQueryDesktop = window.matchMedia('(max-width: 990px)');

// Fonction de callback qui sera appelée lorsque la media query change
function updateSwiper() {
    // Supprimez les instances précédentes de Swiper si nécessaire
    if (window.mySwiper) {
        window.mySwiper.destroy(true, true);
    }

    // Définir slidesPerView en fonction de la media query
    let slidesPerView = 3; // Par défaut pour les écrans larges

    if (mediaQueryTablet.matches) {
        slidesPerView = 1; // Pour les écrans de taille <= 768px
    } else if (mediaQueryDesktop.matches) {
        slidesPerView = 2; // Pour les écrans de taille <= 990px
    }

    // Créez le Swiper avec la configuration adaptée
    window.mySwiper = new Swiper(".mySwiper", {
        slidesPerView: slidesPerView,
        spaceBetween: 10,
        loop: true,
        loopFillGroupWithBlank: true,
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
    });
}

// Vérifiez initialement l'état des media queries
updateSwiper();

// Écoutez les changements des media queries
mediaQueryTablet.addEventListener('change', updateSwiper);
mediaQueryDesktop.addEventListener('change', updateSwiper);

