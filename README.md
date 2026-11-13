# 🏆 Daylex Chests Overlay

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)

Un contador flotante (*overlay*) minimalista, de alto rendimiento y con diseño personalizado, creado especialmente para jugadores y creadores de contenido de **Fortnite** que buscan llevar un registro en tiempo real de sus rutas de farmeo y cofres abiertos.

---

## ✨ Características Principales

* **Interfaz Flotante Moderna:** Ventana sin bordes con estilo translúcido y oscuro, diseñada para mantenerse siempre visible sobre el juego sin estorbar la visión.
* **Detección Global de Teclas:** Escucha tu tecla de interacción incluso jugando a pantalla completa. Incluye un menú de configuración integrado (`⚙️`) para cambiar la tecla de registro al instante.
* **Métricas en Directo:**
  * **COFS/MIN:** Calcula automáticamente tu ritmo y velocidad promedio de apertura.
  * **SESIONES:** Controla cuántas partidas o rondas vas acumulando en tu sesión de juego.
  * **TEMPS:** Cronómetro activo que comienza a contar automáticamente al abrir el primer cofre.
  * **TOTAL ACUMULADO:** Un contador histórico persistente que almacena todas tus aperturas a lo largo del tiempo.
* **Historial Automático:** Al reiniciar la sesión (`↺`), el programa genera de forma automática un archivo de texto detallado dentro de la carpeta `historial/` con la fecha, hora, duración y ritmo de la partida.
* **Guardado Local:** Tus configuraciones (tecla elegida y total histórico) se guardan automáticamente en un archivo `config.json`.

---

## 🚀 Instalación y Uso

### Opción 1: Descarga directa (Recomendado)
1. Ve a la sección de **[Releases](../../releases)** de este repositorio y descarga el archivo ejecutable más reciente.
2. Colócalo en la carpeta de tu preferencia y ejecútalo.
3. Arrastra la ventana flotante hacia la esquina de tu pantalla donde te sea más cómodo jugar.

> **⚠️ Nota importante sobre el Antivirus (Falso Positivo):**  
> Al tratarse de una herramienta independiente que intercepta eventos globales del teclado para funcionar como overlay en juegos, **Windows Defender o tu navegador pueden mostrar una alerta preventiva (falso positivo)**. El código fuente es 100% abierto y transparente en este repositorio. Si aparece el aviso al descargar o abrir el archivo, simplemente haz clic en **"Más información"** y luego en **"Ejecutar de todas formas"** (o añade la carpeta a exclusiones).

---

### Opción 2: Ejecutar desde el Código Fuente

Si prefieres ejecutar el script directamente con Python o modificarlo:

1. **Clona o descarga este repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/daylex-chests-overlay.git](https://github.com/TU_USUARIO/daylex-chests-overlay.git)
   cd daylex-chests-overlay