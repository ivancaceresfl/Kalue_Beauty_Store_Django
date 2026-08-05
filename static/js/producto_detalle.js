function cambiarFoto(el, url) {
    document.getElementById('fotoPrincipal').src = url;
    document.querySelectorAll('.miniatura').forEach(m => m.classList.remove('activa'));
    el.classList.add('activa');
}

function seleccionarVariante(el) {
    document.querySelectorAll('.variante-btn').forEach(b => b.classList.remove('seleccionada'));
    el.classList.add('seleccionada');

    const precio     = el.dataset.precio;
    const variante   = el.dataset.variante;
    const disponible = el.dataset.disponible === 'true';

    document.getElementById('precioActual').textContent     = `Bs. ${precio}`;
    document.getElementById('disponibilidad').textContent   = disponible ? '✅ Disponible' : '❌ Agotado';

    const mensaje = encodeURIComponent(`Hola! Me interesa: ${PRODUCTO} — ${variante}`);
    document.getElementById('btnWhatsapp').href = `https://wa.me/${WHATSAPP}?text=${mensaje}`;
}