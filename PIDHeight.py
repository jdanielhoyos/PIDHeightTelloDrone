from djitellopy import Tello
import cv2
import time
import threading
import os
drone = Tello()
drone.connect()
drone.takeoff()
drone.streamon()
#Check battery
def bat():
    while True:
        time.sleep(10)
        print(drone.get_battery())
        if drone.get_battery()<30:
            drone.land()
            break
    os._exit(1)
c = threading.Thread(name='background', target=bat)
c.start()


def mystream():
    while True:
        myFrame = drone.get_frame_read()
        myFrame = myFrame.frame
        img = cv2.resize(myFrame,(720,480))
        cv2.imshow('Imagen',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            drone.land()
            break
    os._exit(1)
b = threading.Thread(name='background', target=mystream)
b.start()


#PID control for keep height
Kp = 2
Kd = 2
Ki = 0.1
tiempo = []      #Inicializar el vector tiempo
height = []      #Inicializar el vector altura
error = []       #Inicializar el vector error en la altura
sumatoria = 0       #Inicializar el valor de la "integral"
desired_height = 120      #zdes en cm
tiempo.append(time.clock())         #agregar al vector el tiempo actual
height.append(drone.get_distance_tof())     #agregar al vector la altura actual
time.sleep(0.15)        #Esperar 0.15s
tiempo.append(time.clock())         #agregar al vector el tiempo actual
height.append(drone.get_distance_tof())       #agregar al vector la altura actual
error.append(desired_height-height[-1])       #agregar al vector el primer error en la altura
while True:        #Ciclo infinito
    height.append(drone.get_distance_tof())       #agregar al vector la altura actual
    tiempo.append(time.clock())                 #agregar al vector el tiempo actual
    error.append(desired_height-height[-1])         #agregar al vector el error de la altura actual
    deltaError = error[-1]-error[-2]              #calcular el delta del error en la altura
    deltatiempo = tiempo[-1]-tiempo[-2]               #calcular el delta del tiempo en la toma de estos datos
    sumatoria = sumatoria+(tiempo[-1]-tiempo[-2])*(error[-1]-error[-2])         #sumar como va la integral
    vel_updown=Kp*error[-1]+Ki*sumatoria+Kd*(deltaError/deltatiempo)       #calcular el valor del control u(t)
    drone.send_rc_control(0, 0, round(vel_updown), 0)       #Enviar la roden de esta velocidad
    time.sleep(0.1)         #Esperar 0.1s para no saturar el drone
