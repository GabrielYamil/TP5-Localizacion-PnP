import cv2
import numpy as np
import open3d as o3d
import copy

from pathlib import Path
from collections import deque

# ==================================================
# 1. CONFIGURACION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
CALIBRATION_FILE = (
    BASE_DIR.parent / "Calibration" / "camera_calibration.npz"
)

DICCIONARIO = cv2.aruco.DICT_4X4_50
ID_MARCADOR = 0
TAMANO_MARCADOR = 0.10  # metros

LONGITUD_EJES_MUNDO = 0.08
LONGITUD_EJES_CAMARA = 0.05
RADIO_CAMARA = 0.015

INTERVALO_CONSOLA = 15
CANTIDAD_PROMEDIO = 10

# ==================================================
# 2. CARGAR CALIBRACION
# ==================================================

datos = np.load(CALIBRATION_FILE)
K = datos["K"]
distCoef = datos["distCoef"]

print("Calibracion cargada.")
print(f"Resolucion: {datos['width']} x {datos['height']}")
print(f"Error medio de reproyeccion: {float(datos['meanError']):.4f} px")

# ==================================================
# 3. PREPARAR DETECTOR ARUCO
# ==================================================

diccionario = cv2.aruco.getPredefinedDictionary(DICCIONARIO)
parametros = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(diccionario, parametros)

mitad = TAMANO_MARCADOR / 2

# Esquinas del marcador en su propio sistema de coordenadas.
# El origen se encuentra en el centro del marcador.
puntos_marcador = np.array([
    [-mitad,  mitad, 0],
    [ mitad,  mitad, 0],
    [ mitad, -mitad, 0],
    [-mitad, -mitad, 0]
], dtype=np.float32)

# ==================================================
# 4. PREPARAR ESCENA 3D
# ==================================================

visualizador = o3d.visualization.Visualizer()
visualizador.create_window(
    window_name="Localizacion 3D de la camara",
    width=1000,
    height=700
)

# Sistema de coordenadas fijo del mundo.
ejes_mundo = o3d.geometry.TriangleMesh.create_coordinate_frame(
    size=LONGITUD_EJES_MUNDO,
    origin=[0, 0, 0]
)
visualizador.add_geometry(ejes_mundo)

# Plano del marcador: 10 x 10 cm, centrado en el origen.
plano_marcador = o3d.geometry.TriangleMesh.create_box(
    width=TAMANO_MARCADOR,
    height=TAMANO_MARCADOR,
    depth=0.001
)
plano_marcador.translate([-mitad, -mitad, -0.0005])
plano_marcador.paint_uniform_color([0.65, 0.65, 0.65])
plano_marcador.compute_vertex_normals()
visualizador.add_geometry(plano_marcador)


# Geometrias base de la camara, ubicadas inicialmente en el origen
ejes_camara_base = o3d.geometry.TriangleMesh.create_coordinate_frame(
    size=LONGITUD_EJES_CAMARA
)

esfera_camara_base = o3d.geometry.TriangleMesh.create_sphere(
    radius=RADIO_CAMARA
)
esfera_camara_base.paint_uniform_color([1.0, 0.45, 0.05])

# Copias que se mostraran en la escena
ejes_camara = copy.deepcopy(ejes_camara_base)
esfera_camara = copy.deepcopy(esfera_camara_base)

visualizador.add_geometry(ejes_camara)
visualizador.add_geometry(esfera_camara)

# Vista inicial del mundo.
vista = visualizador.get_view_control()
vista.set_lookat([0, 0, 0])
vista.set_front([1, -1, -1])
vista.set_up([0, 0, 1])
vista.set_zoom(0.7)


# Historial para suavizar pequenas variaciones de posicion.
historial_posiciones = deque(maxlen=CANTIDAD_PROMEDIO)

# ==================================================
# 5. ABRIR CAMARA
# ==================================================

cam = cv2.VideoCapture(1)

if not cam.isOpened():
    visualizador.destroy_window()
    raise RuntimeError("No se pudo abrir la camara.")

contador = 0

try:
    while True:

        ret, frame = cam.read()

        if not ret:
            print("No se pudo leer la imagen de la camara.")
            break

        esquinas, ids, rechazados = detector.detectMarkers(frame)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, esquinas, ids)

            for i, id_detectado in enumerate(ids.flatten()):

                if id_detectado != ID_MARCADOR:
                    continue

                # ------------------------------------------
                # 6. ESTIMAR POSE CON PnP
                # ------------------------------------------

                resultado, rvec, tvec = cv2.solvePnP(
                    puntos_marcador,
                    esquinas[i].reshape(4, 2),
                    K,
                    distCoef
                )

                if not resultado:
                    continue
                
                # Dibujar los ejes del marcador sobre la imagen real
                cv2.drawFrameAxes(
                    frame,
                    K,
                    distCoef,
                    rvec,
                    tvec,
                    0.03
                )

                # X_camara = R_cm * X_marcador + t_cm
                R_cm, _ = cv2.Rodrigues(rvec)

                # Transformacion inversa:
                # coordenadas de camara expresadas en el mundo.
                R_mc = R_cm.T
                posicion = (-R_mc @ tvec).flatten()

                # Suavizar solo la posicion.
                historial_posiciones.append(posicion)
                posicion_suavizada = np.mean(
                    historial_posiciones, axis=0
                )

                # ------------------------------------------
                # 7. ACTUALIZAR OBJETOS 3D
                # ------------------------------------------

                # Construir la pose absoluta de la camara en el mundo.
                T_nueva = np.eye(4)
                T_nueva[:3, :3] = R_mc
                T_nueva[:3, 3] = posicion_suavizada

                # Crear copias nuevas desde las geometrias originales.
                # Asi no acumulamos transformaciones anteriores.
                nuevos_ejes = copy.deepcopy(ejes_camara_base)
                nueva_esfera = copy.deepcopy(esfera_camara_base)

                # Ubicar ambas geometrias en la pose actual de la camara.
                nuevos_ejes.transform(T_nueva)
                nueva_esfera.transform(T_nueva)

                # Quitar de la escena los objetos de la pose anterior.
                visualizador.remove_geometry(
                    ejes_camara,
                    reset_bounding_box=False
                )
                visualizador.remove_geometry(
                    esfera_camara,
                    reset_bounding_box=False
                )

                # Guardar las nuevas geometrias.
                ejes_camara = nuevos_ejes
                esfera_camara = nueva_esfera

                # Agregar los objetos actualizados a la escena.
                visualizador.add_geometry(
                    ejes_camara,
                    reset_bounding_box=False
                )
                visualizador.add_geometry(
                    esfera_camara,
                    reset_bounding_box=False
                )

                x, y, z = posicion_suavizada

                texto = (
                    f"Camara en mundo (m): "
                    f"X={x:.3f} Y={y:.3f} Z={z:.3f}"
                )

                cv2.putText(
                    frame,
                    texto,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

                if contador % INTERVALO_CONSOLA == 0:
                    print(texto)

        else:
            cv2.putText(
                frame,
                "Marcador no detectado",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )

        cv2.imshow("Deteccion ArUco", frame)

        # Mantener activa la ventana 3D.
        sigue_abierta = visualizador.poll_events()
        visualizador.update_renderer()

        if not sigue_abierta:
            break

        contador += 1

        # ESC cierra ambas ventanas.
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    cam.release()
    cv2.destroyAllWindows()
    visualizador.destroy_window()
    print("Programa finalizado.")