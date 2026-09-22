
let user = window.KORISNICKA_ULOGA ? { role: window.KORISNICKA_ULOGA } : null;

async function loadCurrentUser() {
    try {
        console.log('Učitavam podatke o korisniku...');
        const response = await fetch('/current-user/', {
            method: 'GET',
            credentials: 'same-origin'
        });
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        if (data.success) {
            user = data.user;
            console.log('Uspešno učitan korisnik:', user);
        } else {
            console.log('Korisnik nije ulogovan:', data.message);
        }
    } catch (error) {
        console.error('Greška pri učitavanju korisnika:', error);
    }
}

function napraviSelectZaProfesora(name, id, placeholderText) {
    const select = document.createElement('select');
    select.name = name;
    select.id = id;

    const praznaOpcija = document.createElement('option');
    praznaOpcija.value = '';
    praznaOpcija.textContent = placeholderText;
    select.appendChild(praznaOpcija);

    profesori.forEach(profesor => {
        const opcija = document.createElement('option');
        opcija.value = profesor.id;
        opcija.textContent = `${profesor.ime} ${profesor.prezime} — ${profesor.institucija}`;
        select.appendChild(opcija);
    });

    return select;
}

document.addEventListener("DOMContentLoaded", function () {

    const urlParams = new URLSearchParams(window.location.search);
    const formaParam = urlParams.get('forma');

    const dugmeZaPretraguStudenta            = document.getElementById('pretraziStudenta');
    const dugmeZaPretraguProfesora           = document.getElementById('pretraziProfesora');
    const studentskaForma                    = document.getElementById('studentska-forma');
    const formaZaDodavanjeNovogStudenta      = document.getElementById('dodaj-novo-studenta-forma');
    const dugmeZaDodavanjeNovogStudenta      = document.getElementById('dodajNovogStudenta');
    const profesorskaForma                   = document.getElementById('profesorska-forma');
    const meni                               = document.getElementById('meni');
    const sviStudentiIProfesori              = document.getElementById('sviStudentiISviProfesori');
    const formaZaDodavanjeNovogProfesora     = document.getElementById('dodaj-novog-profesora-forma');
    const dugmeZaDodavanjeNovogProfesora     = document.getElementById('dodajNovogProfesora');
    const formaZaAzuriranjeStudenta          = document.getElementById('azuriraj-informacije-o-studentu-forma');
    const formaPretraziAzuriratiStudenta     = document.getElementById('pretrazi-azuriraj-studenta-forma');
    const dugmeZaAzuriranjePodatakaOStudentu = document.getElementById('azurirajInformacijeOStudentu');
    const formaIzbrisiStudentaIzBaze         = document.getElementById('izbrisi-studenta-forma');
    const dugmeZaBrisanjeStudenta            = document.getElementById('izbrisiStudentaIzBaze');
    const formaIzbrisiProfeosraIzBaze        = document.getElementById('izbrisi-profesora-forma');
    const dugmeZaBrisanjeProfesora           = document.getElementById('izbrisiProfesoraIzBaze');
    const dugmeZanimljivosti                 = document.getElementById('zanimljivosti');
    const sekcija                            = document.getElementById('zanimljivosti-sekcija');
    const mentorstvo                         = document.getElementById("mentorstvo");
    const clanKomisije                       = document.getElementById("clan_komisije");
    const rekurzivno                         = document.getElementById("rekurzivno");
    const modal                              = document.getElementById('adminModal');
    const closeModalBtn                      = document.getElementById('closeModal');

    [
        studentskaForma,
        profesorskaForma,
        formaZaDodavanjeNovogStudenta,
        formaZaDodavanjeNovogProfesora,
        formaIzbrisiStudentaIzBaze,
        formaIzbrisiProfeosraIzBaze,
        formaZaAzuriranjeStudenta,
        formaPretraziAzuriratiStudenta
    ].forEach(f => { if (f) f.style.display = "none"; });

    function prikaziFormu(formaZaPrikaz) {
        [
            studentskaForma, profesorskaForma,
            formaZaDodavanjeNovogStudenta, formaZaDodavanjeNovogProfesora,
            formaIzbrisiStudentaIzBaze, formaIzbrisiProfeosraIzBaze
        ].forEach(f => { if (f) f.style.display = "none"; });

        if (formaZaPrikaz) {
            formaZaPrikaz.style.display = "block";
            formaZaPrikaz.querySelectorAll('.form-section').forEach(s => s.style.display = "block");
        }

        if (meni) meni.style.display = "none";
    }

   
    const imaRezultatePretrage = Array.from(urlParams.keys())
        .some(kljuc => kljuc !== 'forma' && urlParams.get(kljuc) !== '');

    let nekaFormaJePrikazana = false;

    if (formaParam === 'student') {
        nekaFormaJePrikazana = true;
        prikaziFormu(studentskaForma);
        if (imaRezultatePretrage) {
            studentskaForma.querySelectorAll('form').forEach(f => f.style.display = 'none');
        }
    }
    if (formaParam === 'profesor') {
        nekaFormaJePrikazana = true;
        prikaziFormu(profesorskaForma);
        if (imaRezultatePretrage) {
            profesorskaForma.querySelectorAll('form').forEach(f => f.style.display = 'none');
        }
    }
    if (formaParam === 'dodaj-studenta')   { nekaFormaJePrikazana = true; prikaziFormu(formaZaDodavanjeNovogStudenta); }
    if (formaParam === 'dodaj-profesora')  { nekaFormaJePrikazana = true; prikaziFormu(formaZaDodavanjeNovogProfesora); }
    if (formaParam === 'brisi-studenta')   { nekaFormaJePrikazana = true; prikaziFormu(formaIzbrisiStudentaIzBaze); }
    if (formaParam === 'brisi-profesora')  { nekaFormaJePrikazana = true; prikaziFormu(formaIzbrisiProfeosraIzBaze); }
    if (formaParam === 'pretrazi-azuriraj-studenta') { nekaFormaJePrikazana = true; prikaziFormu(formaPretraziAzuriratiStudenta); }
    if (formaParam === 'azuriraj-studenta') { nekaFormaJePrikazana = true; prikaziFormu(formaZaAzuriranjeStudenta); }


    const sviStudentiIProfesoriParam = urlParams.get('sviStudentiISviProfesori') === 'true';
    if (!nekaFormaJePrikazana && !sviStudentiIProfesoriParam && meni) {
        meni.style.display = '';
    }
---
    if (user && user.role === 'admin') {
        [
            dugmeZaAzuriranjePodatakaOStudentu,
            dugmeZaBrisanjeStudenta,
            dugmeZaBrisanjeProfesora,
            dugmeZaDodavanjeNovogStudenta,
            dugmeZaDodavanjeNovogProfesora
        ].forEach(dugme => { if (dugme) dugme.style.display = ''; });
    }

    function prikaziAdminModal() {
        modal.classList.remove('hidden');
    }

    closeModalBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    function zahtevajAdmina(callback) {
        return (event) => {
            if (!user || !user.role || user.role !== 'admin') {
                prikaziAdminModal();
                return;
            }
            callback(event);
        };
    }

    dugmeZanimljivosti.addEventListener('click', () => {
        meni.style.display = 'none';
        sekcija.style.display = 'block';

        if (sekcija.innerHTML.trim() === '') {
            sekcija.innerHTML = '<p style="text-align: center;">Учитавање...</p>';
            fetch('/zanimljivosti/')
                .then(response => response.text())
                .then(html => { sekcija.innerHTML = html; })
                .catch(error => {
                    sekcija.innerHTML = '<p style="text-align: center; color: red;">Грешка при учитавању података.</p>';
                    console.error('Error:', error);
                });
        }
    });

    dugmeZaAzuriranjePodatakaOStudentu.addEventListener('click', zahtevajAdmina(() => { window.location.href = '/student-graph?forma=pretrazi-azuriraj-studenta'; }));
    dugmeZaBrisanjeStudenta.addEventListener('click',           zahtevajAdmina(() => { window.location.href = '/student-graph?forma=brisi-studenta'; }));
    dugmeZaBrisanjeProfesora.addEventListener('click',          zahtevajAdmina(() => { window.location.href = '/student-graph?forma=brisi-profesora'; }));
    dugmeZaDodavanjeNovogStudenta.addEventListener('click',     zahtevajAdmina(() => { window.location.href = '/student-graph?forma=dodaj-studenta'; }));
    dugmeZaDodavanjeNovogProfesora.addEventListener('click',    zahtevajAdmina(() => { window.location.href = '/student-graph?forma=dodaj-profesora'; }));

    sviStudentiIProfesori.addEventListener('click', (event) => {
        event.preventDefault();
        window.location.href = '/student-graph?sviStudentiISviProfesori=true';
    });

    dugmeZaPretraguStudenta.addEventListener('click', (event) => {
        event.preventDefault();
        window.location.href = '/student-graph?forma=student';
    });

    dugmeZaPretraguProfesora.addEventListener('click', () => {
        window.location.href = '/student-graph?forma=profesor';
    });

    document.getElementById("statistika").addEventListener("click", function (event) {
        event.preventDefault();
        const ime_profesora = document.getElementById("ime_profesora").value;
        const prezime_profesora = document.getElementById("prezime_profesora").value;
        prikaziStatistiku(ime_profesora, prezime_profesora);
    });

    function prikaziRekurzivno() {
        if (mentorstvo.checked && clanKomisije.checked) {
            rekurzivno.disabled = false;
        } else {
            rekurzivno.disabled = true;
            rekurzivno.checked = false;
        }
    }

    mentorstvo.addEventListener("change", prikaziRekurzivno);
    clanKomisije.addEventListener("change", prikaziRekurzivno);

    let brojClanova = 1;
    document.getElementById('dodaj-novog-clana-dugme').addEventListener('click', function () {
        brojClanova++;
        const komisijaDiv = document.getElementById('clanovi-komisije');
        const noviClanDiv = document.createElement('div');
        noviClanDiv.classList.add('clan-komisije');
        const select = napraviSelectZaProfesora(
            `clanovi_komisije[]`,
            `clan_komisije_${brojClanova}`,
            `Изаберите члана комисије ${brojClanova}`
        );
        noviClanDiv.appendChild(select);
        komisijaDiv.appendChild(noviClanDiv);
    });

    let brojAzuriranihClanova = 1;
    document.getElementById('dodaj-novog-azuriranog-clana-dugme').addEventListener('click', function () {
        brojAzuriranihClanova++;
        const azuriranaKomisijaDiv = document.getElementById('clanovi-azurirane-komisije');
        const azuriraniNoviClanDiv = document.createElement('div');
        azuriraniNoviClanDiv.classList.add('clan-azurirane-komisije');
        const select = napraviSelectZaProfesora(
            `azurirani_clanovi_komisije[]`,
            `azurirani_clan_komisije_${brojAzuriranihClanova}`,
            `Изаберите члана комисије ${brojAzuriranihClanova}`
        );
        azuriraniNoviClanDiv.appendChild(select);
        azuriranaKomisijaDiv.appendChild(azuriraniNoviClanDiv);
    });

   
    loadCurrentUser().then(() => {
        const authStatus = document.getElementById('auth-status');
        if (authStatus) {
            if (user && user.role === 'admin') {
                authStatus.innerHTML =
                    '<span class="auth-text">Пријављени сте као <strong>администратор</strong></span>' +
                    '<a href="/logout/" class="auth-link">Одјави се</a>';
            } else {
                authStatus.innerHTML =
                    '<span class="auth-text">Пријављени сте са <strong>гост налогом</strong>. Ако желите да се пријавите као администратор, кликните</span>' +
                    '<a href="/login/" class="auth-link">Пријави се</a>';
            }
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const godinaOdbrane = document.getElementById('godina_odbrane');
    const godinaOd      = document.getElementById('godina_od');
    const godinaDo      = document.getElementById('godina_do');

    function toggleFields() {
        if (godinaOdbrane.value.trim() !== "") {
            godinaOd.disabled = true;
            godinaDo.disabled = true;
        } else {
            godinaOd.disabled = false;
            godinaDo.disabled = false;
        }

        if (godinaOd.value.trim() !== "" || godinaDo.value.trim() !== "") {
            godinaOdbrane.disabled = true;
        } else {
            godinaOdbrane.disabled = false;
        }
    }

    godinaOdbrane.addEventListener('input', toggleFields);
    godinaOd.addEventListener('input', toggleFields);
    godinaDo.addEventListener('input', toggleFields);
});
