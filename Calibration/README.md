# Camera calibration

## calibrate.py
Is a tiny and simple interactive camera calibration application.

It calibrates pinhole cameras using chessboard pattern, computing their intrinsic matrix K and radial distortion coefficientes K1, K2 and K3.

calibrate.py is a short example for learning how calibration works.  You can easily adapt it to your specifics.

While running:

* space: grab a picture
* c: calibrates with grabbed pictures
* ESC: quit

After calibration you can continue grabbing more pictures and repeat the calibration.
Calibration results are shown in console.

![calibrate cam view](calibrate1.png)

![calibrate taken](calibrate2.png)
