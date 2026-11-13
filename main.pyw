import sys
import os
import json
from datetime import datetime
import keyboard
from PySide6.QtCore import Qt, QTimer, QElapsedTimer, Signal, QObject
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QDialog
from PySide6.QtGui import QKeySequence, QIcon

CONFIG_FILE = "config.json"

class GlobalKeySignal(QObject):
    tecla_pulsada = Signal()

class SettingsDialog(QDialog):
    def __init__(self, current_key, parent=None):
        super().__init__(parent)
        self.nueva_tecla = current_key
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.Dialog | 
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(280, 160)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #170e33;
                border: 2px solid #522d8a;
                border-radius: 12px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(14, 14, 14, 14)

        lbl_titulo = QLabel("CONFIGURAR TECLA")
        lbl_titulo.setStyleSheet("color: #b1a2d6; font-weight: 900; font-size: 12px; border: none; background: transparent;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(lbl_titulo)

        self.lbl_info = QLabel(f"Tecla actual: [ {self.nueva_tecla.upper()} ]\n\nPresiona cualquier tecla...")
        self.lbl_info.setStyleSheet("color: #ffd21f; font-weight: 900; font-size: 12px; border: none; background: transparent;")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.lbl_info)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #990000;
                color: white;
                font-size: 11px;
                font-weight: 900;
                border-radius: 4px;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        container_layout.addWidget(btn_cancelar)

        main_layout.addWidget(container)

    def keyPressEvent(self, event):
        key_text = event.text()
        if not key_text or key_text.isspace():
            key_text = QKeySequence(event.key()).toString()
        
        if key_text:
            self.nueva_tecla = key_text.lower()
            self.accept()


class ChestOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.numero_sesion_actual = 1
        self.cofres_sesion = 0
        self.cofres_totales_historicos = 0
        self.en_curso = False
        self.hotkey_handler = None
        
        # Puente de señales entre el hilo de keyboard y la interfaz Qt
        self.signal_bridge = GlobalKeySignal()
        self.signal_bridge.tecla_pulsada.connect(self.registrar_cofre)

        # Cargar configuración y total histórico
        self.tecla_trigger, self.cofres_totales_historicos = self.cargar_configuracion()
        
        # Carpeta historial
        self.historial_dir = "historial"
        os.makedirs(self.historial_dir, exist_ok=True)

        self.elapsed_timer = QElapsedTimer()
        self.init_ui()
        self.actualizar_atajo_global()

    def cargar_configuracion(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    tecla = data.get("tecla", "f")
                    totales = data.get("cofres_totales", 0)
                    return tecla, totales
            except Exception:
                pass
        return "f", 0

    def guardar_configuracion(self):
        try:
            data = {
                "tecla": self.tecla_trigger,
                "cofres_totales": self.cofres_totales_historicos
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error al guardar config: {e}")

    def actualizar_atajo_global(self):
        if self.hotkey_handler is not None:
            try:
                keyboard.remove_hotkey(self.hotkey_handler)
            except Exception:
                pass
        try:
            self.hotkey_handler = keyboard.add_hotkey(
                self.tecla_trigger,
                lambda: self.signal_bridge.tecla_pulsada.emit()
            )
        except Exception as e:
            print(f"Error al registrar tecla {self.tecla_trigger}: {e}")

    def init_ui(self):
        self.setWindowFlags(
            Qt.Window | 
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(390, 210)
        self.move(50, 50)

        if os.path.exists("icono.ico"):
            self.setWindowIcon(QIcon("icono.ico"))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #170e33;
                border: 2px solid #522d8a;
                border-radius: 12px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(14, 10, 14, 12)
        container_layout.setSpacing(6)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(6)

        self.lbl_titulo = QLabel("COFRES ABIERTOS")
        self.lbl_titulo.setStyleSheet("color: #b1a2d6; font-weight: 900; font-size: 12px; border: none; background: transparent;")
        
        self.lbl_estado = QLabel("○ EN ESPERA")
        self.lbl_estado.setStyleSheet("color: #ff5555; font-weight: 900; font-size: 11px; border: none; background: transparent;")
        
        self.btn_config = QPushButton("⚙️")
        self.btn_config.setFixedSize(22, 22)
        self.btn_config.setStyleSheet("""
            QPushButton {
                background-color: #2b1759;
                color: white;
                font-size: 10px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background-color: #4a2994; }
        """)
        self.btn_config.clicked.connect(self.abrir_configuracion)

        self.btn_reset = QPushButton("↺")
        self.btn_reset.setFixedSize(22, 22)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #881111;
                color: white;
                font-size: 12px;
                font-weight: 900;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background-color: #bb1111; }
        """)
        self.btn_reset.clicked.connect(self.reset_contador)

        self.btn_cerrar = QPushButton("✕")
        self.btn_cerrar.setFixedSize(22, 22)
        self.btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #2b1759;
                color: #ffaaaa;
                font-size: 11px;
                font-weight: 900;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background-color: #cc2222; color: white; }
        """)
        self.btn_cerrar.clicked.connect(self.close)

        top_layout.addWidget(self.lbl_titulo)
        top_layout.addStretch()
        top_layout.addWidget(self.lbl_estado)
        top_layout.addWidget(self.btn_config)
        top_layout.addWidget(self.btn_reset)
        top_layout.addWidget(self.btn_cerrar)
        container_layout.addLayout(top_layout)

        # Número grande central (Cofres de la sesión actual)
        self.lbl_numero = QLabel(str(self.cofres_sesion))
        self.lbl_numero.setStyleSheet("color: #ffe600; font-weight: 900; font-size: 38px; border: none; background: transparent;")
        self.lbl_numero.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.lbl_numero)

        # Fila inferior: Las 3 tarjetas (1. Ritmo | 2. Sesión | 3. Temps)
        boxes_layout = QHBoxLayout()
        boxes_layout.setSpacing(6)

        box_style = """
            QWidget {
                background-color: #261752;
                border: 1px solid #5a329e;
                border-radius: 6px;
            }
        """

        # 1. Caja Ritmo (Izquierda)
        self.box_ritmo = QWidget()
        self.box_ritmo.setStyleSheet(box_style)
        v_ritmo = QVBoxLayout(self.box_ritmo)
        v_ritmo.setContentsMargins(4, 4, 4, 4)
        v_ritmo.setSpacing(2)
        
        self.val_ritmo = QLabel("0.0")
        self.val_ritmo.setStyleSheet("color: white; font-weight: 900; font-size: 12px; border: none; background: transparent;")
        self.val_ritmo.setAlignment(Qt.AlignCenter)
        
        lbl_r_txt = QLabel("COFS/MIN")
        lbl_r_txt.setStyleSheet("color: #bfaee6; font-size: 8px; font-weight: 900; border: none; background: transparent;")
        lbl_r_txt.setAlignment(Qt.AlignCenter)
        
        v_ritmo.addWidget(self.val_ritmo)
        v_ritmo.addWidget(lbl_r_txt)

        # 2. Caja Sesión (Centro)
        self.box_sesion = QWidget()
        self.box_sesion.setStyleSheet(box_style)
        v_sesion = QVBoxLayout(self.box_sesion)
        v_sesion.setContentsMargins(4, 4, 4, 4)
        v_sesion.setSpacing(2)
        
        self.val_sesion = QLabel(str(self.numero_sesion_actual))
        self.val_sesion.setStyleSheet("color: white; font-weight: 900; font-size: 12px; border: none; background: transparent;")
        self.val_sesion.setAlignment(Qt.AlignCenter)
        
        self.lbl_s_txt = QLabel("SESIONES")
        self.lbl_s_txt.setStyleSheet("color: #bfaee6; font-size: 8px; font-weight: 900; border: none; background: transparent;")
        self.lbl_s_txt.setAlignment(Qt.AlignCenter)
        
        v_sesion.addWidget(self.val_sesion)
        v_sesion.addWidget(self.lbl_s_txt)

        # 3. Caja Tiempo (Derecha)
        self.box_tiempo = QWidget()
        self.box_tiempo.setStyleSheet(box_style)
        v_tiempo = QVBoxLayout(self.box_tiempo)
        v_tiempo.setContentsMargins(4, 4, 4, 4)
        v_tiempo.setSpacing(2)
        
        self.val_tiempo = QLabel("0:00")
        self.val_tiempo.setStyleSheet("color: white; font-weight: 900; font-size: 12px; border: none; background: transparent;")
        self.val_tiempo.setAlignment(Qt.AlignCenter)
        
        lbl_t_txt = QLabel("TEMPS")
        lbl_t_txt.setStyleSheet("color: #bfaee6; font-size: 8px; font-weight: 900; border: none; background: transparent;")
        lbl_t_txt.setAlignment(Qt.AlignCenter)
        
        v_tiempo.addWidget(self.val_tiempo)
        v_tiempo.addWidget(lbl_t_txt)

        boxes_layout.addWidget(self.box_ritmo)
        boxes_layout.addWidget(self.box_sesion)
        boxes_layout.addWidget(self.box_tiempo)
        container_layout.addLayout(boxes_layout)

        # Etiqueta inferior para mostrar el Total Acumulado entre las sesiones
        self.lbl_historico = QLabel(f"TOTAL ACUMULADO: {self.cofres_totales_historicos} COFRES")
        self.lbl_historico.setStyleSheet("color: #ffd21f; font-size: 10px; font-weight: 900; border: none; background: transparent;")
        self.lbl_historico.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.lbl_historico)

        main_layout.addWidget(container)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.actualizar_reloj)
        self.ui_timer.start(1000)

    def abrir_configuracion(self):
        dialog = SettingsDialog(self.tecla_trigger, self)
        if dialog.exec() == QDialog.Accepted:
            self.tecla_trigger = dialog.nueva_tecla
            self.guardar_configuracion()
            self.actualizar_atajo_global()

    def registrar_cofre(self):
        if not self.en_curso:
            self.en_curso = True
            self.elapsed_timer.start()
            self.lbl_estado.setText("● EN CURSO")
            self.lbl_estado.setStyleSheet("color: #55ff55; font-weight: 900; font-size: 11px; border: none; background: transparent;")
        
        self.cofres_sesion += 1
        self.cofres_totales_historicos += 1 
        
        self.lbl_numero.setText(str(self.cofres_sesion))
        self.lbl_historico.setText(f"TOTAL ACUMULADO: {self.cofres_totales_historicos} COFRES")
        
        self.guardar_configuracion()

    def guardar_sesion_automatica(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = os.path.join(self.historial_dir, f"sesion_{self.numero_sesion_actual}_{timestamp}.txt")
        
        ritmo_actual = self.val_ritmo.text()
        
        try:
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                f.write("=== REGISTRO DE PARTIDA - DAYLEX SHOP ===\n")
                f.write(f"Fecha y Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Número de Sesión: Sesión {self.numero_sesion_actual}\n")
                f.write(f"Cofres en esta Sesión: {self.cofres_sesion}\n")
                f.write(f"Total Histórico Acumulado: {self.cofres_totales_historicos}\n")
                f.write(f"Ritmo Promedio: {ritmo_actual} COFS/MIN\n")
                f.write(f"Tecla Utilizada: {self.tecla_trigger}\n")
        except Exception as e:
            print(f"Error al guardar archivo automático: {e}")

    def reset_contador(self):
        if self.cofres_sesion > 0:
            self.guardar_sesion_automatica()

        self.numero_sesion_actual += 1
        self.cofres_sesion = 0
        self.en_curso = False
        
        self.lbl_numero.setText("0")
        self.val_sesion.setText(str(self.numero_sesion_actual))
        self.lbl_historico.setText(f"TOTAL ACUMULADO: {self.cofres_totales_historicos} COFRES")
        self.val_ritmo.setText("0.0")
        self.val_tiempo.setText("0:00")
        self.lbl_estado.setText("○ EN ESPERA")
        self.lbl_estado.setStyleSheet("color: #ff5555; font-weight: 900; font-size: 11px; border: none; background: transparent;")

    def actualizar_reloj(self):
        if self.en_curso:
            elapsed_ms = self.elapsed_timer.elapsed()
            seconds = elapsed_ms // 1000
            mins = seconds // 60
            secs = seconds % 60
            
            self.val_tiempo.setText(f"{mins}:{secs:02d}")
            
            minutos_totales = seconds / 60.0
            if minutos_totales > 0:
                ritmo = self.cofres_sesion / minutos_totales
                self.val_ritmo.setText(f"{ritmo:.1f}")

    def closeEvent(self, event):
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.dragPosition)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ChestOverlay()
    overlay.show()
    sys.exit(app.exec())