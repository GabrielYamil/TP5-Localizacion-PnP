import cv2

diccionario = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)

id_marcador = 0  # ID del marcador a generar

tamanio = 1000

marcador = cv2.aruco.generateImageMarker(diccionario, id_marcador, tamanio)

cv2.imwrite("maruco_id0.png", marcador)

print("Marcador ArUco generado correctamente.")
print("Se ha guardado como 'maruco_id0.png'.")
print("Diccionario utilizado: DICT_4X4_50.")
print("ID del marcador: 0.")