import serial
import time
import cv2
import mediapipe as mp
import numpy as np
import warnings

def ler_mao(desafios_todo, desafios_completed, game_comu_queue):
    warnings.filterwarnings("ignore")

    desafios_mapper = {
        'A': {
            'esperado': [range(80, 101), range(95, 101), range(0, 10), range(0, 10), range(0, 10)],
            'desc': "L"
        },
        'B': {
            'esperado': [range(0, 101), range(95, 101), range(0, 10), range(0, 10), range(95, 101)],
            'desc': "Rock and Roll"
        },
        'C': {
            'esperado': [range(0, 101), range(0, 15), range(90, 101), range(0, 15), range(0, 15)],
            'desc': "Dedo do meio"
        },
        'D': {
            'esperado': [range(0, 101), range(0, 10), range(0, 10), range(0, 10), range(95, 101)],
            'desc': "Chá"
        },
        'E': {
            'esperado': [range(0, 101), range(15, 101), range(15, 101), range(0, 14), range(0, 14)],
            'desc': "Paz"
        }
    }

    # Inicializa a comunicação serial -> UTILIZE A PORTA 'COM' CORRESPONDENTE
    # arduino = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)

    # Inicializa o MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_draw = mp.solutions.drawing_utils


    # Função para calcular distâncias entre dois pontos
    def calc_distance(point1, point2):
        return np.linalg.norm(np.array(point1) - np.array(point2))


    # Função para calcular a abertura dos dedos usando distâncias e verificação de posição
    def calc_opening_dist(landmarks):
        distances = []

        # Coordenada X do punho (landmark 0) - tratamento especial do polegar
        fist_x = landmarks[0][0]

        # Calcular a abertura do polegar usando a distância horizontal (eixo X) entre a ponta do polegar e o punho
        horizontal_distance_thumb = abs(landmarks[4][0] - fist_x)  # Apenas diferença no eixo X
        thumb_opening = min(100, max(0, int((horizontal_distance_thumb / 0.2) * 100)))  # Normaliza para 0-100
        distances.append(thumb_opening)

        # Calcular a abertura dos outros dedos (indicador, médio, anelar, mindinho)
        fingers = [(8, 5), (12, 9), (16, 13), (20, 17)]  # Ponta e base dos dedos

        for tip, base in fingers:
            # Verificar se a ponta do dedo está abaixo da base (eixo Y)
            if landmarks[tip][1] >= landmarks[base][1]:  # Coordenada Y da ponta >= base
                finger_opening = 0
            else:
                finger_distance = calc_distance(landmarks[tip], landmarks[base])
                finger_opening = min(100, max(0, int((finger_distance / 0.2) * 100)))  # Normaliza para 0-100
            distances.append(finger_opening)

        return distances


    # def sendList(aberturaDedos: list, arduino: serial.Serial) -> None:
    #     mensagem = ','.join(map(str, aberturaDedos))
    #     arduino.write((mensagem + '\n').encode())


    # Capturando a imagem da webcam
    cap = cv2.VideoCapture(0)

    # Verifica se a câmera foi aberta corretamente
    if not cap.isOpened():
        print("Erro ao abrir a câmera.")
        exit()

    # Controle para o intervalo de envio de dados
    last_sent_time = time.time()
    send_interval = .075  # Intervalo de envio de dados em segundos

    finger_opening = [0, 0, 0, 0, 0]
    esperado = [[150, 200], [150, 200], [150, 200], [150, 200], [150, 200]]
    flag_desafio = False
    flag_continuar = False

    while True:
        success, image = cap.read()

        if not success:
            print("Erro ao capturar a imagem da câmera.")
            continue

        # Convertendo a imagem de BGR para RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if not desafios_todo.empty() and flag_continuar:
            desafio = desafios_todo.get()
            desafio_flag = True
            if isinstance(desafio, dict):
                esperado = desafios_mapper.get(desafio.get('nome')).get('esperado')

        atual = [finger_opening[i] in esperado[i] for i in range(5)]
        if False not in atual and desafio and desafio_flag:
            desafios_completed.put(desafio)
            desafio_flag = False
            desafio = None

        # Processando a imagem com o MediaPipe
        result = hands.process(image_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Obtendo os landmarks da mão
                landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]

                # Calculando a abertura dos dedos usando distâncias e verificando a posição
                finger_opening = calc_opening_dist(landmarks)

                # Controle para enviar dados a cada intervalo especificado
                # current_time = time.time()
                # if current_time - last_sent_time > send_interval:
                #     sendList(finger_opening, arduino)
                #     last_sent_time = current_time

                # Exibir os valores de abertura dos dedos na tela
                for idx, abertura in enumerate(finger_opening):
                    cv2.putText(image, f'Dedo {idx + 1}: {abertura}', (10, 30 + idx * 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)


        # Exibindo a imagem com os landmarks desenhados
        cv2.imshow('MediaPipe Hands', image)

        # Processa eventos da janela OpenCV, como fechamento da janela
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        class bcolors:
            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKCYAN = '\033[96m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'

        if not game_comu_queue.empty():
            message = game_comu_queue.get()
            if isinstance(message, dict):
                if message.get('body').get('message') == "desafios_list":
                    flag_continuar = False
                    print('\n' * 15)
                    desafios = message.get('body').get('desafios')
                    for desafio in desafios:
                        print(desafios_mapper.get(desafio.get('nome')).get('desc'))
                        time.sleep(0.4)
                    time.sleep(len(desafios)*0.4 + 1)
                    print('\n'*15)
                    flag_continuar = True
                if message.get('body').get('message') == "desafio_all_ended":
                    print(bcolors.OKGREEN + "Desafio concluído\n" + bcolors.ENDC)
                    print("Pontuação final: ", message.get('body').get('score'))
                if message.get('body').get('status') == "game_ended":
                    break

    cap.release()
    cv2.destroyAllWindows()