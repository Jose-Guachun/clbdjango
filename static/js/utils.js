$(function () {
    $('.bloqueo').click(function () {
         bloqueointerface();
    })
})
function bloqueointerface() {
    $.blockUI({
        message: '<span class="spinner-border text-secondary" role="status" aria-hidden="true" style="width: 5rem; height: 5rem;"></span>',
        css: {
            backgroundColor: 'transparent',
            border: '0',
            zIndex: 9999999
        },
        overlayCSS: {
            backgroundColor: 'rgba(17,17,17,0.23)',
            opacity: 0.8,
            zIndex: 9999990
        }
    });
}

function mensajeSuccess(titulo, mensaje) {
    Swal.fire(titulo, mensaje, 'success')
}

function mensajeWarning(titulo, mensaje) {
    Swal.fire(titulo, mensaje, 'warning')
}

function mensajeDanger(titulo, mensaje) {
    Swal.fire(titulo, mensaje, 'error')
}

function alertaSuccess(mensaje, time = 5000) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'success',
        title: mensaje,
        showConfirmButton: false,
        timer: time
    })
}

function alertaWarning(mensaje, time = 5000) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'warning',
        title: mensaje,
        showConfirmButton: false,
        timer: time
    })
}

function alertaDanger(mensaje, time = 5000) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'error',
        title: mensaje,
        showConfirmButton: false,
        timer: time
    })
}

function alertaInfo(mensaje, time = 5000) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'info',
        title: mensaje,
        showConfirmButton: false,
        timer: time
    })
}