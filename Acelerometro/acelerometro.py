import kalman_filter
import smbus
from time import sleep  #
import math

# Variáveis para a conexão I2C
bus = smbus.SMBus(2)  # Número do I2C utilizado
Device_Address = 0x68  # Endereço do acelerômetro no I2C

# Variáveis de correção
Fator_x = 0.5755287971
Fator_y = 0.5980265673
Fator_z = 0.5540265036

# Registradores do acelerômetro (vindos do Datasheet)
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# Variáveis para o Filtro de Kalman
KalmanAngleRoll = 0
KalmanAnglePitch = 0


def MPU_Init():
    
    # Escrever no registro de taxa de amostragem
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    # Escrever no registro de gerenciamento de energia
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    # Escrever no registro de configuração
    bus.write_byte_data(Device_Address, CONFIG, 0x05)
    
    bus.write_byte_data(Device_Address, 0x1C, 0x10) # Configurando acelerometro para 8g

    # Escrever no registro de configuração do giroscópio
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 0x08)

    # Escrever no registro de habilitação de interrupção
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)


def read_raw_data(addr):
    # Isso porque acelerômetro e giroscópio têm 16 bit, divide em parte baixa (8 bits menos significativos) e parte alta (8 bits mais significativos)
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)

    # Concatenar maior e menor valor
    value = ((high << 8) | low)

    # Para obter o valor assinado do MPU6050
    if (value > 32768):
        value = value - 65536
    return value


## Fim das configurações do sensor
def pegaAcelerometro(diretorio):
	with open(f'{diretorio}/acelerometro.csv', mode='w', newline='') as csv_file:
		MPU_Init()
		writer = csv.DictWriter(csv_file, fieldnames=['Roll', 'Pitch'])
		writer.writeheader()
		while True:
			
			# Lendo acelerometro
			acc_x = read_raw_data(ACCEL_XOUT_H)
			acc_y = read_raw_data(ACCEL_YOUT_H)
			acc_z = read_raw_data(ACCEL_ZOUT_H)

			# Lendo giroscópio
			gyro_x = read_raw_data(GYRO_XOUT_H)
			gyro_y = read_raw_data(GYRO_YOUT_H)
			gyro_z = read_raw_data(GYRO_ZOUT_H)

			# Convertendo as medidas para valores físicos
			AccX = (acc_x / 4096)#/9.81 + Fator_x
			AccY = (acc_y / 4096)#/9.81 + Fator_y
			AccZ = (acc_z / 4096)#/9.81 + Fator_z
			RateRoll = gyro_x / 65.5
			RatePitch = gyro_y / 65.5
			RateYaw = gyro_z / 65.5

			# Calculando as taxas de ângulo
			try:
				AngleRoll = math.atan(AccZ/AccY)*180/math.pi - 89.11
				AnglePitch = math.atan(AccZ/AccX)*180/math.pi + 85.62
				
				if AngleRoll <= -90:
					AngleRoll += 180
					
				if AnglePitch >= 90:
					AnglePitch -= 180
				
			except:
				AngleRoll = 0
				AnglePitch = 0

			KalmanUncertaintyAngleRoll = 2*2
			KalmanUncertaintyAnglePitch = 2*2

			# Roll
			Roll_Output = kalman_filter.kalman_1d(KalmanAngleRoll, KalmanUncertaintyAngleRoll, RateRoll, AngleRoll)
			KalmanAngleRoll= Roll_Output[0]
			KalmanUncertaintyAngleRoll = Roll_Output[1]

			# Pitch
			Pitch_Output = kalman_filter.kalman_1d(KalmanAnglePitch, KalmanUncertaintyAnglePitch, RatePitch, AnglePitch)
			KalmanAnglePitch = Pitch_Output[0]
			KalmanUncertaintyAnglePitch = Pitch_Output[1]
			
			dados = f'{KalmanAngleRoll},{KalmanAnglePitch}'
			dados_float = list(map(float, dados))

			row_data = dict(zip(['Roll', 'Pitch'], dados_float))
			print(row_data)
			writer.writerow(row_data)
			csv_file.flush()

			#print(f'Roll: {KalmanAngleRoll}º | Pitch: {KalmanAnglePitch}º')

			# Esse print é para a calibração dos sensores
			# Basicamente o valor mostrado precisa ser = 1.00 para a posição do sensor nos eixos, serve para
			# Pegar um fator de correção para o cálculo dos ângulos
			# Comenta quando não usar
			#print(f'AccX [g] = {AccX} | AccY [g] = {AccY} | AccZ = {AccZ}')

			# Printando na tela os valores de ângulo atual
			#print(f'Roll angle [º] = {AngleRoll} | Pitch angle [º] = {AnglePitch}')

			sleep(0.1) # Delay do código, por padrão estamos usando 0.1 na telemetria
