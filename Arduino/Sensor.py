import csv, os, serial
from datetime import datetime, timedelta

class Sensor:
    # Atributos da Classe
    DIRETORIO = "Logs/"
    HISTORICO_COORDENADAS = [[-9.326506, -40.470119], [[-9.326506, -40.470119]]] # Valores iniciais aleatórios, os 2 primeiros dados devem ser desconsiderados no tratamento

    def __init__(self, nome, porta, baud, colunas):
        self.nome = nome
        self.porta = porta
        self.baud = baud
        self.colunas = colunas

    @staticmethod
    def verifica_diretorio():
        num = 1
        diretorio_atual = [Sensor.DIRETORIO, num]
        while os.path.exists(f"{diretorio_atual[0]}{diretorio_atual[1]}"):
            num+=1
            diretorio_atual[1] = num
            
        nome_definitivo = str(f"{diretorio_atual[0]}{diretorio_atual[1]}")
        os.makedirs(nome_definitivo)
        return nome_definitivo

    def leituras(self, diretorio):
        with serial.Serial(self.porta, self.baud) as ser:
            # O Try vem  # Isso aqui é apenas para teste, o rx_size e tx_size
            with open(f'{diretorio}/{self.nome}.csv', mode='w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.colunas)
                writer.writeheader()

                while True:
                    leitura = ser.readline().strip()
                    dados = leitura.split(b',')
                    dados_float = [float(dado) for dado in dados]

                    # Dict comprehension
                    row_data = {coluna: dado_float for coluna, dado_float in zip(self.colunas, dados_float)}
                    #row_data = dict(zip(self.colunas, dados_float)) # Forma que tava
                    print(row_data)
                    writer.writerow(row_data)
                    csv_file.flush()
            # O except vem aqui

    

    def converte_horario(self, time_gps):
        time_gps = datetime.strptime(time_gps, "%H%M%S.%f")

        tempo_brasil = time_gps - timedelta(hours=3)

        if (tempo_brasil.month > 2 and tempo_brasil.month < 10) or \
                (tempo_brasil.month == 2 and tempo_brasil.day < 20 and tempo_brasil.weekday() == 6) or \
                (tempo_brasil.month == 10 and tempo_brasil.day > 20 and tempo_brasil.weekday() == 6):
            tempo_brasil = tempo_brasil + timedelta(hours=1)

        return tempo_brasil.strftime("%H:%M:%S")

    def leogepas(self, diretorio):

        with serial.Serial(self.porta, self.baud, timeout=1) as ser:
            with open(f'{diretorio}/{self.nome}.csv', mode='w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.colunas)
                writer.writeheader()

                while True:
                    try:
                        leitura = ser.readline().decode('utf-8', errors="ignore").strip()

                        if leitura.startswith('$GPGGA'):
                            dados = leitura.split(',')

                            if len(dados) >= 15:
                                grauslatitude = str(dados[2])
                                dir_latitude = dados[3]
                                latitude = int(grauslatitude[:2]) + float(grauslatitude[2:]) / 60
                                if dir_latitude == 'S':
                                    latitude = -latitude

                                grauslongitude = str(dados[4])
                                dir_longitute = dados[5]
                                longitude = int(grauslongitude[:3]) + float(grauslongitude[3:]) / 60
                                if dir_longitute == 'W':
                                    longitude = -longitude

                                altitude = dados[9]

                                hora = self.converte_horario(dados[1])
                                gps = [hora, latitude, longitude, altitude]

                                row_data = dict(zip(self.colunas, gps))
                                print(row_data)
                                writer.writerow(row_data)
                                csv_file.flush()
                    except:
                        row_data = dict(zip(self.colunas, [0,0,0,0]))
                        print(row_data)
                        writer.writerow(row_data)
                        csv_file.flush()
                        


