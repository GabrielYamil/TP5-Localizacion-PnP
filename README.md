TP5 - Localización de cámara mediante PnP y ArUco

Descripción

Este proyecto corresponde al Trabajo Práctico N.º 5 de Visión Artificial y tiene como objetivo estimar la pose de una cámara a partir de la detección de marcadores ArUco y del algoritmo Perspective-n-Point (PnP).

La aplicación detecta un marcador ArUco mediante la cámara, calcula la posición y orientación de la cámara respecto del sistema de coordenadas del marcador y actualiza su representación en un visualizador 3D utilizando Open3D.

De esta manera, cuando la cámara se mueve, su pose estimada se actualiza en tiempo real en la visualización.

Objetivos

Calibrar la cámara para obtener sus parámetros intrínsecos y coeficientes de distorsión.

Detectar marcadores ArUco mediante OpenCV.

Estimar la pose relativa entre la cámara y el marcador utilizando cv2.solvePnP().

Calcular la posición de la cámara en el sistema de coordenadas del marcador.

Representar la posición y orientación de la cámara en un entorno 3D con Open3D.

Actualizar la visualización mientras la cámara se mueve.

Tecnologías utilizadas

Python: lenguaje de programación.

OpenCV: procesamiento de imágenes, detección ArUco y estimación de pose.

NumPy: operaciones matriciales y cálculos numéricos.

Open3D: visualización 3D de la pose de la cámara.

Requisitos previos

Python instalado.

Una cámara conectada a la computadora.

Un marcador ArUco del diccionario DICT_4X4_50, con ID 0.

El tamaño físico del marcador debe coincidir con el configurado en el código. En esta implementación se utiliza un marcador de 10 × 10 cm.

Los parámetros de calibración de la cámara deben estar disponibles en Calibration/camera_calibration.npz.

Importante: los parámetros de calibración dependen de la cámara utilizada. Si se ejecuta el proyecto con otra cámara, se recomienda realizar una nueva calibración.

Instalación

1. Clonar el repositorio

git clone URL_DEL_REPOSITORIO
cd TP5-Localizacion-PnP

Reemplazar URL_DEL_REPOSITORIO por la URL del repositorio publicado en GitHub.

2. Crear un entorno virtual

En Windows, desde PowerShell:

python -m venv .venv

3. Activar el entorno virtual

.\.venv\Scripts\Activate.ps1

Si PowerShell no permite activar el entorno, se puede revisar la política de ejecución de scripts de Windows.

4. Instalar las dependencias

python -m pip install --upgrade pip
pip install -r requirements.txt

Calibración de la cámara

El directorio Calibration contiene el código y los archivos auxiliares para realizar la calibración.

La calibración permite obtener la matriz intrínseca de la cámara y sus coeficientes de distorsión. Estos parámetros se utilizan posteriormente para estimar la pose mediante PnP.

El archivo camera_calibration.npz contiene los parámetros de calibración utilizados por la aplicación de localización.

Si se necesita calibrar otra cámara, ejecutar el procedimiento de calibración y actualizar el archivo con los nuevos parámetros. Consultar también las instrucciones incluidas en Calibration/README.md.

Ejecución

Desde la raíz del proyecto, con el entorno virtual activado:

python Localization/generar_aruco.py

Este script permite generar el marcador ArUco utilizado en las pruebas, según la implementación incluida en el proyecto.

Para iniciar la detección y visualización de la pose:

python Localization/detectar_aruco.py

La aplicación utiliza la cámara conectada, detecta el marcador y muestra la imagen capturada junto con la visualización 3D de la pose estimada.

Si la cámara no se abre, puede ser necesario modificar el índice del dispositivo configurado en detectar_aruco.py.

Visualización 3D

La escena de Open3D incluye:

Plano gris: representa la superficie del marcador ArUco.

Ejes del mundo: representan el sistema de coordenadas de referencia asociado al marcador.

Esfera naranja: representa la posición estimada de la cámara.

Ejes móviles: representan la orientación de la cámara y se actualizan cuando esta se mueve.

La estimación de pose se realiza a partir de los puntos 3D conocidos del marcador y sus correspondientes puntos 2D detectados en la imagen.

La función cv2.solvePnP() obtiene la rotación y la traslación del marcador respecto de la cámara. A partir de esa transformación se calcula la pose de la cámara respecto del sistema de coordenadas del marcador.

Controles

Mover la cámara para observar cómo cambia la pose estimada en la visualización 3D.

Presionar ESC para cerrar la aplicación, según el comportamiento implementado en el script.

Posibles problemas

No se detecta el marcador: verificar la iluminación, el enfoque, la visibilidad del marcador y que su ID y diccionario coincidan con los configurados.

La cámara no se abre: revisar el índice de cámara utilizado en el código y cerrar otras aplicaciones que puedan estar usándola.

La posición estimada presenta pequeñas variaciones: pueden producirse fluctuaciones por ruido en la detección, movimiento o perspectiva. El código aplica un suavizado de la posición.

La pose no parece correcta: comprobar que la calibración corresponde a la cámara utilizada y que el tamaño físico configurado coincide con el tamaño real del marcador.