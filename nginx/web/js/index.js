// =============================
// Importamos la función de alertas
// =============================
import { showAlert } from "./alert.js";
import { API_BASE_URL } from "./config.js";

// =============================
// Referencias al DOM
// =============================
const search_button = document.getElementById("search-button");
const urlInput = document.getElementById("url");
const result = document.getElementById("result");

// =============================
// Evento principal: búsqueda de video
// =============================
search_button.addEventListener("click", async function() {
	search_button.textContent = "Buscando...";
	search_button.disabled = true;
	
	const url = urlInput.value.trim();
	
	if (!url) {
		search_button.textContent = "Buscar";
		search_button.disabled = false;
		showAlert("Falta la URL. Inténtelo nuevamente.", "error");
		return;
	}
	
	try {
		showAlert("Extrayendo información del video...", "info");
		
		const res = await fetch(`${API_BASE_URL}/api/search`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ url })
		});
		
		const contentType = res.headers.get("content-type");
		
		if (!contentType || !contentType.includes("application/json")) {
			const textResponse = await res.text();
			console.error("Respuesta no-JSON:", textResponse);
			throw new Error("El servidor devolvió un error inesperado (no JSON). Ver consola.");
		}
		
		const data = await res.json();
		
		if (!res.ok || !data.success) {
			throw new Error(data.error || data.details || 'Error desconocido en el servidor.');
		}
		
		console.log('Información extraída:', data);
		showAlert(`Video encontrado: ${data.metadata.title}`, "success");
		
		displayResults(data);
		
	} catch (err) {
		console.error('Error en la búsqueda:', err);
		showAlert(`Error: ${err.message}`, "error");
	} finally {
		search_button.textContent = "Buscar";
		search_button.disabled = false;
	}
});

// =============================
// Mostrar resultados en pantalla
// =============================
function displayResults(data) {
	result.innerHTML = '';
	
	const resultHTML = `
		<div class="result-card">
			<!-- Miniatura -->
			<div class="result-thumbnail">
				<img src="${escapeHtml(data.metadata.thumbnail)}" alt="${escapeHtml(data.metadata.title)}">
			</div>
			
			<!-- Información del video -->
			<div class="result-info">
				<h3 class="result-title">${escapeHtml(data.metadata.title)}</h3>
				<p><strong>Canal:</strong> ${escapeHtml(data.metadata.artist || "Desconocido")}</p>
				<p><strong>Duración:</strong> ${escapeHtml(data.metadata.duration || "N/A")}</p>
				${data.metadata.views ? `
				<p><strong>Vistas:</strong> ${formatViews(data.metadata.views)}</p>
				` : ''}
			</div>
			
			<!-- Información del audio -->
			<div class="result-audio-info">
				<h4>Audio disponible</h4>
				<p><strong>Calidad:</strong> ${escapeHtml(data.audio_info.quality || "N/A")}</p>
				<p><strong>Bitrate:</strong> ${escapeHtml(data.audio_info.bitrate || "N/A")}</p>
				<p><strong>Codec:</strong> ${escapeHtml(data.audio_info.codec || "N/A")}</p>
				<p><strong>Formato:</strong> ${escapeHtml(data.audio_info.format || "N/A")}</p>
				<p><strong>Tamaño estimado:</strong> ~${escapeHtml(data.audio_info.estimated_size_mb || "?")} MB</p>
			</div>
			
			<!-- Botones de descarga -->
			<div class="result-download">
				<a href="${data.download_endpoint}" 
				   class="download-button download-normal" 
				   download="${sanitizeFilename(data.metadata.title)}.mp3"
				   data-title="${escapeHtml(data.metadata.title)}">
					⬇️ Descargar MP3
				</a>
				
				<button 
				   class="download-button enhanced download-enhanced" 
				   data-endpoint="${data.download_enhanced_endpoint}"
				   data-filename="${sanitizeFilename(data.metadata.title)}_enhanced.mp3"
				   data-title="${escapeHtml(data.metadata.title)}">
					✨ Descargar Mejorado
				</button>
			</div>
			
			<!-- Nota -->
			<div class="result-note">
				<p><em>${escapeHtml(data.note || "")}</em></p>
				<p><em><strong>Mejorado:</strong> incluye normalización, EQ y compresión (tarda más).</em></p>
			</div>
		</div>
	`;
	
	result.innerHTML = resultHTML;
	attachDownloadListeners();
	result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// =============================
// Funciones auxiliares
// =============================

// Escapa texto para evitar inyección HTML
function escapeHtml(text) {
	if (text === undefined || text === null) return "";
	const div = document.createElement('div');
	div.textContent = text;
	return div.innerHTML;
}

// Limpia nombres de archivo
function sanitizeFilename(filename) {
	return filename.replace(/[^a-z0-9_\-]/gi, '_');
}

// ✅ Formatea número de vistas
function formatViews(views) {
	if (typeof views !== "number") {
		const parsed = parseInt(views, 10);
		if (isNaN(parsed)) return views;
		views = parsed;
	}
	if (views >= 1_000_000) return (views / 1_000_000).toFixed(1) + "M";
	if (views >= 1_000) return (views / 1_000).toFixed(1) + "K";
	return views.toString();
}

// =============================
// Listeners para descargas
// =============================
function attachDownloadListeners() {
	// Descarga normal
	const normalButton = document.querySelector('.download-normal');
	if (normalButton) {
		normalButton.addEventListener('click', async function (e) {
			e.preventDefault();
			const title = this.getAttribute('data-title');
			const downloadUrl = this.getAttribute('href');
			const filename = this.getAttribute('download');
			await handleDownload(downloadUrl, filename, title, "original");
		});
	}

	// Descarga mejorada
	const enhancedButton = document.querySelector('.download-enhanced');
	if (enhancedButton) {
		enhancedButton.addEventListener('click', async function (e) {
			e.preventDefault();
			const endpoint = this.getAttribute('data-endpoint');
			const filename = this.getAttribute('data-filename');
			const title = this.getAttribute('data-title');
			await handleDownload(endpoint, filename, title, "mejorado");
		});
	}
}

// =============================
// Manejo unificado de descargas
// =============================
async function handleDownload(endpoint, filename, title, tipo) {
	console.log(`[INFO] Iniciando descarga ${tipo} de: ${title}`);

	const modal = createProgressModal(title, tipo);
	document.body.appendChild(modal);

	try {
		updateProgressModal(`Preparando descarga ${tipo}...`, 10);

		const response = await fetch(endpoint);
		if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);

		updateProgressModal(
			tipo === "mejorado"
				? "Procesando audio (normalización, EQ, compresión)..."
				: "Descargando archivo...",
			tipo === "mejorado" ? 50 : 40
		);

		const blob = await response.blob();
		updateProgressModal("Guardando archivo...", 90);

		const url = window.URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = filename;
		document.body.appendChild(a);
		a.click();

		setTimeout(() => {
			window.URL.revokeObjectURL(url);
			document.body.removeChild(a);
		}, 100);

		updateProgressModal("¡Descarga completada!", 100);

		setTimeout(() => {
			closeProgressModal();
			showAlert(`Descarga ${tipo} completada: "${title}"`, "success");
		}, 1000);
	} catch (error) {
		console.error(`[ERROR] Descarga ${tipo} falló:`, error);
		closeProgressModal();
		showAlert(`Error al descargar (${tipo}): ${error.message}`, "error");
	}
}

// =============================
// Modal de progreso
// =============================
function createProgressModal(title, tipo) {
	const modal = document.createElement('div');
	modal.id = 'progress-modal';
	modal.className = 'progress-modal';

	modal.innerHTML = `
		<div class="progress-modal-content">
			<h3 class="progress-title">
				${tipo === "mejorado" ? "✨ Descarga mejorada" : "⬇️ Descarga original"}
			</h3>
			<p class="progress-subtitle">${escapeHtml(title)}</p>
			<div class="progress-bar-container">
				<div class="progress-bar" id="progress-bar"></div>
			</div>
			<p class="progress-text" id="progress-text">Iniciando...</p>
		</div>
	`;

	return modal;
}

function updateProgressModal(text, percentage) {
	const progressBar = document.getElementById('progress-bar');
	const progressText = document.getElementById('progress-text');

	if (progressBar) progressBar.style.width = percentage + '%';
	if (progressText) progressText.textContent = text;
}

function closeProgressModal() {
	const modal = document.getElementById('progress-modal');
	if (modal) modal.remove();
}
