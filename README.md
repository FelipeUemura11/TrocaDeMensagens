# Sistema de Troca de Mensagens Criptografadas

Este é um sistema de troca de mensagens seguro que utiliza criptografia RSA para garantir a confidencialidade e SHA-256 para garantir a integridade das mensagens.

## Arquitetura do Sistema

O sistema é composto por dois servidores:

1. **Servidor Receptor (app1.py)**
   - Porta: 5000
   - Responsável por receber e descriptografar as mensagens
   - Gerencia as chaves públicas e privadas
   - Verifica a integridade das mensagens
   - **Armazena o histórico completo das mensagens**

2. **Servidor Remetente (app2.py)**
   - Porta: 5001
   - Responsável por enviar mensagens criptografadas
   - Interface web para envio de mensagens
   - Gerencia a criptografia das mensagens
   - **Busca o histórico de mensagens do receptor e exibe na interface**

## Funcionalidades Implementadas

### Criptografia RSA
- Geração de pares de chaves (pública/privada)
- Criptografia de mensagens usando a chave pública
- Descriptografia de mensagens usando a chave privada

### Verificação de Integridade
- Geração de hash SHA-256 das mensagens
- Verificação de integridade no recebimento
- Detecção de possíveis manipulações

### Interface Web
- Formulário para envio de mensagens
- Feedback visual do status do envio
- Tratamento de erros e exceções
- **Ambas as interfaces exibem o mesmo histórico de mensagens, em tempo real**
- Mensagens enviadas pelo usuário local são destacadas

## Requisitos

- Python 3.x
- Flask
- Requests
- Bibliotecas padrão: hashlib, random, logging

## Como Executar

1. Inicie o servidor receptor:
```bash
python app1.py
```

2. Em outro terminal, inicie o servidor remetente:
```bash
python app2.py
```

3. Acesse as interfaces web em:
```
http://localhost:5000  # Receptor
http://localhost:5001  # Remetente
```

## Fluxo de Comunicação

1. O servidor remetente solicita a chave pública ao servidor receptor
2. O servidor receptor envia sua chave pública
3. O servidor remetente:
   - Criptografa a mensagem usando a chave pública
   - Gera um hash SHA-256 da mensagem original
   - Envia a mensagem criptografada e o hash
4. O servidor receptor:
   - Recebe a mensagem criptografada e o hash
   - Descriptografa a mensagem
   - Verifica a integridade usando o hash
   - Confirma o recebimento e armazena a mensagem no histórico
5. O servidor remetente busca periodicamente o histórico do receptor e exibe na interface

## Segurança

O sistema implementa várias camadas de segurança:

1. **Criptografia RSA**
   - Chaves de 512 bits
   - Exponente público padrão (65537)
   - Geração segura de números primos

2. **Verificação de Integridade**
   - Hash SHA-256 para cada mensagem
   - Verificação de manipulação
   - Rejeição de mensagens alteradas

3. **Tratamento de Erros**
   - Logs detalhados de operações
   - Tratamento de exceções
   - Mensagens de erro informativas

## Estrutura do Código

### app1.py (Servidor Receptor)
- Geração de chaves RSA
- Endpoint para obtenção da chave pública
- Webhook para recebimento de mensagens
- Verificação de integridade
- Descriptografia de mensagens
- **Armazena e fornece o histórico completo das mensagens**

### app2.py (Servidor Remetente)
- Interface web para envio de mensagens
- Obtenção da chave pública
- Criptografia de mensagens
- Geração de hash
- Envio de mensagens criptografadas
- **Busca e exibe o histórico do receptor**

## Logs e Monitoramento

O sistema utiliza logging para monitorar todas as operações:
- Debug: Operações normais
- Error: Falhas e exceções
- Info: Status de operações importantes

## Observações

- O chat é unidirecional: apenas o remetente envia mensagens para o receptor, mas ambos veem o mesmo histórico.
- Para um chat realmente bidirecional, seria necessário implementar o envio de mensagens do receptor para o remetente.
- O histórico é armazenado apenas em memória (será perdido ao reiniciar o servidor receptor).

## Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Envie um pull request

## Licença

Este projeto está sob a licença MIT.
