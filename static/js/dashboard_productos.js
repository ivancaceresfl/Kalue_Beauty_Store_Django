let ordenActual = { columna: null, ascendente: true };

function ordenarTabla(th) {
    const tabla = th.closest('table');
    const tbody = tabla.querySelector('tbody');
    const filas = Array.from(tbody.querySelectorAll('tr'));

    const indiceColumna = Array.from(th.parentNode.children).indexOf(th);
    const tipo = th.dataset.tipo; 
    const ascendente = (ordenActual.columna === indiceColumna) ? !ordenActual.ascendente : true;
    ordenActual = { columna: indiceColumna, ascendente };

    filas.sort((filaA, filaB) => {
        const valorA = filaA.children[indiceColumna].textContent.trim();
        const valorB = filaB.children[indiceColumna].textContent.trim();

        let comparacion;
        if (tipo === 'numero') {
            comparacion = parseFloat(valorA) - parseFloat(valorB);
        } else {
            comparacion = valorA.localeCompare(valorB, 'es', { sensitivity: 'base' });
        }
        return ascendente ? comparacion : -comparacion;
    });

    filas.forEach(fila => tbody.appendChild(fila));

    tabla.querySelectorAll('th.th-ordenable').forEach(t => t.classList.remove('th-asc', 'th-desc'));
    th.classList.add(ascendente ? 'th-asc' : 'th-desc');
}