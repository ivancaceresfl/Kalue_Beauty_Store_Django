document.addEventListener('DOMContentLoaded', function() {
    const tabla = document.querySelector('.tabla-admin');
    if (!tabla) return;

    const headers = tabla.querySelectorAll('th');

    headers.forEach((th, index) => {
        const columnasOrdenables = [0, 2, 3, 4]; // #, Producto, Marca, Categoría
        if (!columnasOrdenables.includes(index)) return;

        th.style.cursor = 'pointer';
        th.title        = 'Click para ordenar';
        th.innerHTML   += ' <span class="orden-icono">↕️</span>';

        let direccion = 'asc';

        th.addEventListener('click', () => {
            const tbody = tabla.querySelector('tbody');
            const filas = Array.from(tbody.querySelectorAll('tr'));

            filas.sort((a, b) => {
                const celdaA = a.querySelectorAll('td')[index];
                const celdaB = b.querySelectorAll('td')[index];

                if (!celdaA || !celdaB) return 0;

                let valorA = celdaA.textContent.trim();
                let valorB = celdaB.textContent.trim();

                if (index === 0) {
                    valorA = parseInt(valorA) || 0;
                    valorB = parseInt(valorB) || 0;
                    return direccion === 'asc' ? valorA - valorB : valorB - valorA;
                }

                return direccion === 'asc'
                    ? valorA.localeCompare(valorB, 'es')
                    : valorB.localeCompare(valorA, 'es');
            });

            headers.forEach(h => {
                const icono = h.querySelector('.orden-icono');
                if (icono) icono.textContent = '↕️';
            });

            const icono = th.querySelector('.orden-icono');
            icono.textContent = direccion === 'asc' ? '⬆️' : '⬇️';

            direccion = direccion === 'asc' ? 'desc' : 'asc';

            filas.forEach(fila => tbody.appendChild(fila));
        });
    });
});