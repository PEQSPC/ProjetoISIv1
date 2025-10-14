# ProjetoISIv1
Trabalho da Disciplina de Integração de Sistemas de Informação (ISI) pretende-se focar a aplicação e experimentação de ferramentas em processos de ETL (Extract, Transformation and Load), inerentes a processos de Integração de Sistemas de informação ao nível dos dados.

# Tecnologias Usadas
- NodeRed -> [NodeRed Windows](nodered.org/docs/getting-started/windows) uses node.js and npm packages
- NodeRed UI builder with vue.js
- Python -> Python 3.14.0
- Mosquitto MQTT
- Git

# Comandos Git
[Geeks git Commands](https://www.geeksforgeeks.org/git/working-on-git-bash/)


# PASSOS
- Install Node-Red
- Install Mosquitto Broker
- Add [MQTT-Simulator](https://github.com/DamascenoRafael/mqtt-simulator) to be a publisher for mqtt
- Install node red dashboard
- Config node-red to be a subscriber and then ETL the json objets to the node-red-dashboard 

# Exemplo de sensores simulados
|     Sensor       |     Tipo de   dado         |     Unidade     |     Intervalo   de emissão    |     Exemplo de   payload                  |
|------------------|----------------------------|-----------------|-------------------------------|-------------------------------------------|
|     Produção     |     Peças por   minuto     |     pcs/min     |     5 s                       |     {   "estacao": 1, "producao": 58 }    |
|     Paragem      |     Tempo parado           |     segundos    |     evento                    |     {   "estacao": 1, "paragem": 15 }     |
|     Stock        |     Nível de   stock       |     %           |     10 s                      |     {   "estacao": 1, "stock": 73 }       |
|     Qualidade    |     Peças   defeituosas    |     %           |     10 s                      |     {   "estacao": 1, "defeitos": 4 }     |



# Arquitetura do Projeto

Publisher: DamascenoRafael (via mqtt-simulator)

Broker: Mosquitto ->(netstap -a) TCP 127.0.0.1:1883 DESKTOP-I0EE5MC:0 LISTENING

Subscriber: Node-RED with node red dashboard