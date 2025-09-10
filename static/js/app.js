function activeMenuOption(href) {
    $(".app-menu .nav-link")
    .removeClass("active")
    .removeAttr('aria-current')

    $(`[href="${(href ? href : "#/")}"]`)
    .addClass("active")
    .attr("aria-current", "page")
}

const app = angular.module("angularjsApp", ["ngRoute"])
app.config(function ($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix("")

    $routeProvider
    .when("/", {
        templateUrl: "/app",
        controller: "appCtrl"
    })
    .when("/rentas", {
        templateUrl: "/rentas",
        controller: "rentasCtrl"
    })
    .when("/clientes", {
        templateUrl: "/clientes",
        controller: "clientesCtrl"
    })
    // .when("/decoraciones", {
    //     templateUrl: "/decoraciones",
    //     controller: "decoracionesCtrl"
    // })

    .otherwise({
        redirectTo: "/"
    })
})
app.run(["$rootScope", "$location", "$timeout", function($rootScope, $location, $timeout) {
    function actualizarFechaHora() {
        lxFechaHora = DateTime
        .now()
        .setLocale("es")

        $rootScope.angularjsHora = lxFechaHora.toFormat("hh:mm:ss a")
        $timeout(actualizarFechaHora, 1000)
    }

    $rootScope.slide = ""

    actualizarFechaHora()

    $rootScope.$on("$routeChangeSuccess", function (event, current, previous) {
        $("html").css("overflow-x", "hidden")
        
        const path = current.$$route.originalPath

        if (path.indexOf("splash") == -1) {
            const active = $(".app-menu .nav-link.active").parent().index()
            const click  = $(`[href^="#${path}"]`).parent().index()

            if (active != click) {
                $rootScope.slide  = "animate__animated animate__faster animate__slideIn"
                $rootScope.slide += ((active > click) ? "Left" : "Right")
            }

            $timeout(function () {
                $("html").css("overflow-x", "auto")

                $rootScope.slide = ""
            }, 1000)

            activeMenuOption(`#${path}`)
        }
    })
}])

// CAMBIAR EN BASE QUE VISTA VA PRIMERO(esta rentas)
app.controller("appCtrl", function ($scope, $http) {
    $("#frmInicioSesion").submit(function (event) {
        event.preventDefault()
        $.post("iniciarSesion", $(this).serialize(), function (respuesta) {
            if (respuesta.length) {
                alert("Iniciaste Sesión")
                window.location = "/#/rentas"

                return
            }

            alert("Usuario y/o Contraseña Incorrecto(s)")
        })
    })
})

app.controller("rentasCtrl", function ($scope, $http) {
    function buscarRentas() {
        $.get("/tbodyRentas", function (trsHTML) {
            $("#tbodyRentas").html(trsHTML)
        })
    }

    buscarRentas()
// PUSHER

    // Enable pusher logging - don't include this in production
    Pusher.logToConsole = true;

    var pusher = new Pusher('b51b00ad61c8006b2e6f', {
      cluster: 'us2'
    });

    var channel = pusher.subscribe("canalRentas")
    channel.bind("eventoRentas", function(data) {
        // alert(JSON.stringify(data))
        buscarRentas()
    })

    $(document).on("submit", "#frmRenta", function (event) {
        event.preventDefault()

        $.post("/renta", {
            id: "",
            cliente: $("#txtIdCliente").val(),
            traje: $("#txtIdTraje").val(),
            descripcion: $("#txtDescripcion").val(),
            fechahorainicio: $("#txtFechaInicio").val(),
            fechahorafin: $("#txttxtFechaFin").val(),

        })
    })

// MODAL
    // $(document).on("click", ".btn-ingredientes", function (event) {
    //     const id = $(this).data("id")

    //     $.get(`/productos/ingredientes/${id}`, function (html) {
    //         modal(html, "Ingredientes", [
    //             {html: "Aceptar", class: "btn btn-secondary", fun: function (event) {
    //                 closeModal()
    //             }}
    //         ])
    //     })
    // })
})

app.controller("clientesCtrl", function ($scope, $http) {

    function cargarTablaClientes() {
        $.get("/tbodyClientes", function(html) {
            $("#tbodyClientes").html(html);
        });
    }

    cargarTablaClientes();

    Pusher.logToConsole = true;
    var pusher = new Pusher("bf79fc5f8fe969b1839e", { cluster: "us2" });
    var channel = pusher.subscribe("canalClientes");
    channel.bind("eventoClientes", function(data) {
        cargarTablaClientes();
    });

     $(document).on("click", "#btnBuscarCliente", function() {
        const busqueda = $("#txtBuscarCliente").val().trim();

        if(busqueda === "") {
            cargarTablaClientes();
            return;
        }

        $.get("/api/clientes/buscar", { busqueda: busqueda }, function(registros) {
            let trsHTML = "";
            registros.forEach(cliente => {
                trsHTML += `
                    <tr>
                        <td>${cliente.idCliente}</td>
                        <td>${cliente.nombreCliente}</td>
                        <td>${cliente.telefono}</td>
                        <td>${cliente.correoElectronico}</td>
                        <td>
                            <button class="btn btn-danger btn-sm btn-eliminar" data-id="${cliente.idCliente}">Eliminar</button>
                        </td>
                    </tr>
                `;
            });
            $("#tbodyClientes").html(trsHTML);
        }).fail(function(xhr){
            console.error("Error al buscar clientes:", xhr.responseText);
        });
    });

    // Permitir Enter en input
    $("#txtBuscarCliente").on("keypress", function(e) {
        if(e.which === 13) {
            $("#btnBuscarCliente").click();
        }
    });

    $(document).on("submit", "#frmCliente", function (event) {
        event.preventDefault();

        $.post("/cliente", {
            id: "",
            nombreCliente: $("#txtNombreCliente").val(),
            telefono: $("#txtTelefono").val(),
            correoElectronico: $("#txtCorreoElectronico").val(),
        }, function(response){
            console.log("Cliente guardado correctamente");
            $("#frmCliente")[0].reset();
            cargarTablaClientes(); 
        }).fail(function(xhr){
            console.error("Error al guardar cliente:", xhr.responseText);
        });
    });

    $(document).on("click", "#tbodyClientes .btn-eliminar", function(){
        const id = $(this).data("id");
        if(confirm("¿Deseas eliminar este cliente?")) {
            $.post("/clientes/eliminar", {id: id}, function(response){
                console.log("Cliente eliminado correctamente");
                cargarTablaClientes(); 
            }).fail(function(xhr){
                console.error("Error al eliminar cliente:", xhr.responseText);
            });
        }
    });

});



// app.controller("decoracionesCtrl", function ($scope, $http) {
//     function buscarDecoraciones() {
//         $.get("/tbodyDecoraciones", function (trsHTML) {
//             $("#tbodyDecoraciones").html(trsHTML)
//         })
//     }

//     buscarDecoraciones()
    
//     // Enable pusher logging - don't include this in production
//     Pusher.logToConsole = true

//     var pusher = new Pusher("e57a8ad0a9dc2e83d9a2", {
//       cluster: "us2"
//     })

//     var channel = pusher.subscribe("canalDecoraciones")
//     channel.bind("eventoDecoraciones", function(data) {
//         // alert(JSON.stringify(data))
//         buscarDecoraciones()
//     })

//     $(document).on("submit", "#frmDecoracion", function (event) {
//         event.preventDefault()

//         $.post("/decoracion", {
//             id: "",
//             nombre: $("#txtNombre").val(),
//             precio: $("#txtPrecio").val(),
//             existencias: $("#txtExistencias").val(),
//         })
//     })
// })

const DateTime = luxon.DateTime
let lxFechaHora

document.addEventListener("DOMContentLoaded", function (event) {
    const configFechaHora = {
        locale: "es",
        weekNumbers: true,
        // enableTime: true,
        minuteIncrement: 15,
        altInput: true,
        altFormat: "d/F/Y",
        dateFormat: "Y-m-d",
        // time_24hr: false
    }

    activeMenuOption(location.hash)
})
