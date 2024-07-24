import threading
from Arduino.Sensor import Sensor
from acelerometro import pegaAcelerometro

# Nome da pasta que vai salvar os dados
# Formato da pasta deve ser:
# "caminho/para/pasta/EnsaioxRep"
# Mantenha sempre o espaço entre {} vazio, o código vai criar pastas
# Numeradas automaticamente toda vez que rodar
Sensor.diretorio = "LogsTeste1/"
diretorio = Sensor.verifica_diretorio()

# Aqui que define os sensores
ARD_MEGA = Sensor('POT', '/dev/ttyUSB1', 9600, ['Potencia', 'Tensao','Corrrnte', 'Throttle', 'pwm_out', 'interval' ])
# = Sensor('GPS', '/dev/ttyS2', 9600, ['Hora', 'Latitude', 'Longitude', 'Altitude'])
#TRACAO = Sensor('TRACAO', 'COM7', 57600, ['Tração'])

# Ajuste os threadings de acordo com a classe
t1 = threading.Thread(target=ARD_MEGA.leituras, args=(diretorio,))
#t2 = threading.Thread(target=GPS.leogepas, args=(diretorio,))
#t3 = threading.Thread(target=TRACAO.leituras, args=(diretorio,))
t4 = threading.Thread(target=pegaAcelerometro, args=(diretorio,))

t1.start()
#t2.start()
#t3.start()
t4.start()

t1.join()
#t2.join()
#t3.join()
t4.join()