# Otimizador de Rede para Jogos

Este aplicativo otimiza a conexão de rede do Windows para melhorar a experiência em jogos online, reduzindo latência e aumentando a estabilidade da conexão.

## Funcionalidades

- **Interface gráfica amigável** com monitoramento em tempo real
- **Estatísticas de rede** (ping, perda de pacotes) com indicadores visuais
- **Otimizações abrangentes**:
  - Configuração de QoS (Quality of Service)
  - Otimização de MTU
  - Desativação do algoritmo de Nagle
  - Configuração de buffers de rede
  - Otimização de DNS
  - Desativação de serviços desnecessários
  - Ajustes de TCP avançados

## Requisitos

- Windows 10 ou superior
- Python 3.6 ou superior
- Privilégios de administrador

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências necessárias:

```
pip install -r requirements.txt
```

## Como Usar

1. Execute o programa como administrador:

```
python network_optimizer.py
```
Para criar um executável rode:
```
python setup.py
```
2. Use o botão "Iniciar Monitoramento" para verificar as estatísticas atuais da sua rede
3. Clique em "Iniciar Otimização de Rede" para aplicar todas as otimizações
4. Acompanhe o progresso e os logs na interface

## Observações Importantes

- O programa requer privilégios de administrador para modificar configurações do sistema
- Algumas otimizações podem exigir reinicialização para ter efeito completo
- As configurações são otimizadas para jogos online, podendo não ser ideais para outros usos

## Possíveis Melhorias Futuras

- Opções para personalizar as otimizações
- Testes de velocidade completos
- Perfis para diferentes jogos
- Função para reverter as alterações
- Mais métricas de monitoramento em tempo real
