import threading
from Arduino.Sensor import Sensor
from Acelerometro.acelerometro import pegaAcelerometro

# Nome da pasta que vai salvar os dados
# Formato da pasta deve ser:
# "caminho/para/pasta/EnsaioxRep{num}"
# Mantenha sempre o espaço entre {} vazio, o código vai criar pastas
# Numeradas automaticamente toda vez que rodar
Sensor.diretorio = "Logs/"
diretorio = Sensor.verifica_diretorio()

# Aqui que define os sensores
ARD_MEGA = Sensor('ARD_MEGA', 'COM5', 9600, ['Velocidade_ASA', 'Velocidade_SH'])
GPS = Sensor('GPS', '/dev/ttyS7', 9600, ['Hora', 'Latitude', 'Longitude', 'Altitude', 'Deslocamento'])


# Ajuste os threadings de acordo com a classe
t1 = threading.Thread(target=ARD_MEGA.leituras, args=(diretorio,))
t2 = threading.Thread(target=GPS.leogepas, args=(diretorio,))
t3 = threading.Thread(target=pegaAcelerometro, args=(diretorio,))

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()
