// grafovi.js — funkcije za navigaciju i prikaz grafova

function cistiUrl() {
    return new URL(window.location.origin + window.location.pathname);
}

function prikaziGraf(ime, prezime,naslov) {
    const url = cistiUrl();
    url.searchParams.set('forma', 'student');
    url.searchParams.set('ime_studenta', ime);
    url.searchParams.set('prezime_studenta', prezime);
    url.searchParams.set('naslov_jednog', naslov);
    
    window.location.href = url.toString();
}

function prikaziStatistiku(ime, prezime) {
    const url = cistiUrl();
    url.searchParams.set('forma', 'profesor');
    url.searchParams.set('ime_profesora', ime);
    url.searchParams.set('prezime_profesora', prezime);
    window.location.href = url.toString();
}
