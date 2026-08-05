let categoriaActual = 'todos';

function filtrarCategoria(categoria, btn) {
    categoriaActual = categoria;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('activo'));
    btn.classList.add('activo');
    document.querySelectorAll('.tabs-sub').forEach(s => s.style.display = 'none');
    if (categoria !== 'todos') {
        const sub = document.getElementById('sub-' + categoria);
        if (sub) sub.style.display = 'flex';
    }
    document.querySelectorAll('.tarjeta').forEach(tarjeta => {
        tarjeta.style.display =
            (categoria === 'todos' || tarjeta.dataset.categoria === categoria)
            ? 'block' : 'none';
    });
    document.getElementById('campoBusqueda').value = '';
}

function filtrarSub(sub, btn) {
    document.querySelectorAll('.subtab').forEach(t => t.classList.remove('activo'));
    btn.classList.add('activo');
    document.querySelectorAll('.tarjeta').forEach(tarjeta => {
        tarjeta.style.display =
            tarjeta.dataset.subcategoria === sub ? 'block' : 'none';
    });
}

function buscar() {
    const texto = document.getElementById('campoBusqueda').value.toLowerCase();
    document.querySelectorAll('.tarjeta').forEach(tarjeta => {
        const nombre = tarjeta.querySelector('h3').textContent.toLowerCase();
        const enCategoria = categoriaActual === 'todos' || tarjeta.dataset.categoria === categoriaActual;
        if (texto.length === 0) {
            tarjeta.style.display = enCategoria ? 'block' : 'none';
        } else {
            tarjeta.style.display =
                enCategoria && nombre.includes(texto) ? 'block' : 'none';
        }
    });
}