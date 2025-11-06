export const showAlert = (message, type = 'info') => {
    let alertContainer = document.createElement("div");
    // Añade la clase 'type' al contenedor principal, no solo al texto
    alertContainer.classList.add("alert-container", type); 
    
    let textAlert = document.createElement("p");
    textAlert.classList.add("alert-text");
    textAlert.textContent = message; // Asigna el mensaje al texto

    alertContainer.appendChild(textAlert);
    document.body.appendChild(alertContainer);

    // --- Efecto de Entrada ---
    // Fuerza un reflow del navegador para asegurar que la transición ocurra
    getComputedStyle(alertContainer).opacity; 
    alertContainer.classList.add('show');

    // --- Efecto de Salida y Limpieza ---
    setTimeout(() => {
        // Inicia la animación de salida
        alertContainer.classList.remove('show');
        alertContainer.classList.add('hide');

        // Espera a que termine la animación de salida (0.5s definido en CSS) 
        // antes de eliminar el elemento del DOM.
        setTimeout(() => {
            document.body.removeChild(alertContainer);
        }, 500); // 500ms = duración de la transición en el CSS
        
    }, 2000); // 2 segundos antes de empezar a desaparecer
};

// Ejemplo de uso:
// showAlert("¡Bienvenido a la página de música!", "info");
// showAlert("Canción guardada exitosamente", "success");
// showAlert("Error al cargar la playlist", "error");
