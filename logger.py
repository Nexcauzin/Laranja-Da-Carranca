import threading
from Sensor import Sensor
from acelerometro import pegaAcelerometro

# Nome da pasta que vai salvar os dados
# Formato da pasta deve ser:
# "caminho/para/pasta/EnsaioxRep{num}"
# Mantenha sempre o espaço entre {} vazio, o código vai criar pastas
# Numeradas automaticamente toda vez que rodar
Sensor.diretorio = "Logs/"
diretorio = Sensor.verifica_diretorio()

# Aqui que define os sensores
ARD_MEGA = Sensor('ARD_MEGA', 'COM5', 9600, ['Velocidade_ASA', 'Velocidade_SH'])
GPS = Sensor('GPS', '/dev/ttyS7', 9600, ['Hora', 'Latitude', 'Longitude', 'Altitude'])


# Ajuste os threadings de acordo com a classe
t1 = threading.Thread(target=PITOT.leituras(diretorio))
t2 = threading.Thread(target=GPS.leogepas(diretorio))
t3 = threading.Thread(target=pegaAcelerometro(diretorio))

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()
