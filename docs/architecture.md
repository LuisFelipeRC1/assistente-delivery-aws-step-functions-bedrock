# Arquitetura e decisões técnicas

## Objetivo

Automatizar o ciclo de um pedido de delivery usando serviços gerenciados e serverless da AWS, mantendo o projeto simples o suficiente para demonstração acadêmica e completo o suficiente para representar um fluxo real.

## Componentes

### Amazon API Gateway

Expõe dois endpoints:

- `POST /orders`: recebe um pedido e inicia a máquina de estados;
- `GET /orders/{orderId}`: consulta o status atual e o histórico.

### AWS Lambda

- `CreateOrderFunction`: cria o identificador, salva o pedido e inicia o workflow;
- `ValidateOrderFunction`: aplica regras de validação;
- `ProcessPaymentFunction`: simula uma integração de pagamento;
- `UpdateStatusFunction`: mantém status, histórico e mensagem do assistente;
- `GetOrderFunction`: consulta o pedido no DynamoDB.

### AWS Step Functions

É o elemento central de orquestração. O workflow controla decisões, tentativas, caminhos de falha, esperas e chamadas aos demais serviços.

### Amazon Bedrock

O Step Functions invoca diretamente o modelo configurado por meio da integração otimizada `bedrock:invokeModel`. O modelo recebe somente o ID do pedido e seus itens, sem dados sensíveis de pagamento ou endereço completo.

### Amazon DynamoDB

Armazena o estado atual do pedido, a mensagem do assistente e o histórico de transições. O modo `PAY_PER_REQUEST` evita a necessidade de provisionar capacidade para o exemplo.

### Amazon CloudWatch

Recebe os logs completos das execuções da máquina de estados, permitindo visualizar entradas, saídas, falhas e tentativas.

## Decisões importantes

1. **Execução assíncrona:** a criação retorna HTTP 202 e um `executionArn`; o cliente consulta o resultado depois.
2. **Pagamento simulado:** nenhuma informação bancária real é processada.
3. **Fallback de IA:** uma indisponibilidade do Bedrock não interrompe o pedido.
4. **Modelo configurável:** o ID do modelo é um parâmetro do CloudFormation.
5. **Infraestrutura como código:** todos os recursos são reproduzíveis por meio do AWS SAM.
6. **Observabilidade:** o Step Functions possui logging e tracing habilitados.

## Melhorias para produção

- Amazon Cognito ou outro provedor de identidade;
- AWS WAF e limitação de requisições;
- idempotência por chave fornecida pelo cliente;
- EventBridge para eventos de domínio;
- SNS, SES ou integração de WhatsApp para notificações;
- API de pagamento real e uso de tokenização;
- DLQ e alarmes do CloudWatch;
- KMS com chaves gerenciadas pelo cliente;
- Amazon Bedrock Guardrails;
- testes de integração e pipeline de deploy por ambiente.
