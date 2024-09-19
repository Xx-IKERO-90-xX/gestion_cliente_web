let btnCopyTel = document.getElementById("btnCopyTel");
let btnCopyEmail = document.getElementById("btnCopyEmail");

let telefono = document.getElementById("telInput");
let correo = document.getElementById("emailInput");

console.log(navigator);
console.log(telefono);
console.log(correo);

/**
 * Almacena la instruccion para copiar el numero de telefono al portapapeles.
 */
function copyTelefono() {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(telefono.value).then(function () {
            let btnClassList = document.getElementById("btnCopyTel").classList;
            btnClassList.remove("btn-secondary");
            btnClassList.add("btn-success");

            setTimeout(function () {
                btnClassList.remove("btn-success");
                btnClassList.add("btn-secondary");
            }, 3000);
        });
    }
    else {
        telefono.select();
        telefono.setSelectionRange(0, 99999);

        document.execCommand("copy");
        /** .then(function () {
            let btnClassList = document.getElementById("btnCopyTel").classList;
            btnClassList.remove("btn-secondary");
            btnClassList.add("btn-success");

            setTimeout(function () {
                btnClassList.remove("btn-success");
                btnClassList.add("btn-secondary");
            }, 3000);

        });**/
    }
}

/**
 * Almacena la instruccion para copiar el correo al portapapeles.
 */
function copyEmail() {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(correo.value).then(function () {
            let btnClassList = document.getElementById("btnCopyEmail").classList;
            btnClassList.remove("btn-secondary");
            btnClassList.add("btn-success");

            setTimeout(function () {
                btnClassList.remove("btn-success");
                btnClassList.add("btn-secondary");
            }, 3000)
        });
    }
    else {
        correo.select();
        correo.setSelectionRange(0, 99999);

        document.execCommand("copy");
        /** 
        .then(function () {
            let btnClassList = document.getElementById("btnCopyEmail").classList;
            btnClassList.remove("btn-secondary");
            btnClassList.add("btn-success");

            setTimeout(function () {
                btnClassList.remove("btn-success");
                btnClassList.add("btn-secondary");
            }, 3000)
        })*/
    }
}

btnCopyTel.addEventListener("click", copyTelefono);
btnCopyEmail.addEventListener("click", copyEmail);