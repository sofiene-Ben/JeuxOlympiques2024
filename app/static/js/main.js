function toggleMenu() {
    const nav = document.querySelector('nav');
    nav.classList.toggle('open');
}

function redirectToOffers() {
    window.location.href = "/offers";
}

function redirectToEditPassword() {
    window.location.href = "/change-password";
}

function redirectToEditProfile() {
    window.location.href = "/edit-profile";
}