# Assistente de Delivery com AWS Step Functions e Amazon Bedrock

Projeto serverless desenvolvido para o desafio **Criando um Assistente de Delivery com AWS Step Functions e Bedrock**.

A aplicação recebe pedidos por uma API, valida os dados, simula o pagamento, atualiza o status do delivery e usa o Amazon Bedrock para gerar uma mensagem personalizada para o cliente. Todo o fluxo é orquestrado pelo AWS Step Functions e provisionado como infraestrutura como código com AWS SAM.

## Arquitetura

```mermaid
flowchart LR
    C[Cliente] -->|POST /orders| API[Amazon API Gateway]
    API --> CREATE[Lambda CreateOrder]
    CREATE --> DB[(Amazon DynamoDB)]
    CREATE --> SF[AWS Step Functions]
    SF --> VALIDATE[Lambda ValidateOrder]
    SF --> BEDROCK[Amazon Bedrock\nAmazon Nova Micro]
    SF --> PAYMENT[Lambda ProcessPayment]
    SF --> STATUS[Lambda UpdateStatus]
    STATUS --> DB
    C -->|GET /orders/{orderId}| API
    API --> GET[Lambda GetOrder]
    GET --> DB
    SF --> LOGS[Amazon CloudWatch Logs]
```

## Funcionalidades implementadas

- API REST para criar e consultar pedidos;
- persistência dos pedidos e do histórico de status no DynamoDB;
- validação de campos obrigatórios e itens do pedido;
- geração de mensagem personalizada com Amazon Bedrock;
- simulação de pagamento com cenários de aprovação e falha;
- fluxo assíncrono com estados de preparação, saída para entrega e conclusão;
- tratamento de falhas, tentativas automáticas e mensagem de fallback caso o Bedrock não responda;
- logs do Step Functions no CloudWatch;
- infraestrutura definida com AWS SAM/CloudFormation;
- testes unitários e workflow de integração contínua no GitHub Actions.

## Fluxo do pedido

```text
RECEIVED
   ↓
VALIDATED
   ↓
PAYMENT_PENDING
   ↓
PAYMENT_APPROVED
   ↓
PREPARING
   ↓
OUT_FOR_DELIVERY
   ↓
DELIVERED
```

Caminhos de erro previstos:

```text
FAILED_VALIDATION
PAYMENT_FAILED
```

## Estrutura do repositório

```text
.
├── .github/workflows/ci.yml
├── docs/architecture.md
├── events/
│   ├── create-order.json
│   └── create-order-payment-failure.json
├── src/
│   ├── create_order/app.py
│   ├── get_order/app.py
│   ├── process_payment/app.py
│   ├── update_status/app.py
│   └── validate_order/app.py
├── statemachine/delivery.asl.json
├── tests/
├── Makefile
├── requirements-dev.txt
├── samconfig.toml.example
└── template.yaml
```

## Pré-requisitos

- conta AWS;
- AWS CLI configurada;
- AWS SAM CLI;
- Python 3.12;
- Docker, apenas caso seja utilizado `sam local`;
- região com suporte ao Amazon Bedrock e ao modelo escolhido.

O modelo padrão é `amazon.nova-micro-v1:0`. Ele pode ser alterado no parâmetro `BedrockModelId` durante o deploy.

## Deploy

### 1. Validar e compilar

```bash
sam validate
sam build
```

### 2. Primeiro deploy guiado

```bash
sam deploy --guided
```

Sugestão de respostas:

```text
Stack Name: delivery-assistant
AWS Region: us-east-1
Parameter BedrockModelId: amazon.nova-micro-v1:0
Confirm changes before deploy: Y
Allow SAM CLI IAM role creation: Y
Save arguments to configuration file: Y
```

### 3. Obter a URL da API

Ao final do deploy, o output `DeliveryApiUrl` mostrará a URL base.

## Criar um pedido

```bash
curl -X POST "https://SEU_ENDPOINT/orders" \
  -H "Content-Type: application/json" \
  -d @events/create-order.json
```

Resposta esperada:

```json
{
  "orderId": "uuid-do-pedido",
  "status": "RECEIVED",
  "executionArn": "arn:aws:states:...",
  "message": "Pedido recebido e enviado para processamento."
}
```

## Consultar um pedido

```bash
curl "https://SEU_ENDPOINT/orders/UUID_DO_PEDIDO"
```

Resposta resumida:

```json
{
  "orderId": "uuid-do-pedido",
  "status": "DELIVERED",
  "assistantMessage": "Seu pedido foi confirmado...",
  "history": [
    {"status": "RECEIVED", "timestamp": "..."},
    {"status": "VALIDATED", "timestamp": "..."}
  ]
}
```

## Simular falha no pagamento

Use o arquivo de exemplo:

```bash
curl -X POST "https://SEU_ENDPOINT/orders" \
  -H "Content-Type: application/json" \
  -d @events/create-order-payment-failure.json
```

Também é possível incluir `"simulateFailure": true` dentro do objeto `payment`.

## Executar os testes

```bash
python -m pip install -r requirements-dev.txt
pytest -q
ruff check src tests
```

Ou:

```bash
make test
```

## Segurança e boas práticas

- o projeto não recebe nem armazena número completo de cartão, CVV ou credenciais bancárias;
- a integração de pagamento é apenas simulada;
- dados sensíveis não são enviados ao Amazon Bedrock;
- permissões IAM são limitadas aos recursos necessários;
- logs não registram endereço completo nem informações de pagamento;
- em produção, recomenda-se adicionar autenticação, WAF, criptografia com chave KMS gerenciada pelo cliente, idempotência e integração com um provedor de pagamentos real.

## Custos

O deploy pode gerar cobranças pelos serviços utilizados, principalmente Step Functions, Lambda, DynamoDB, API Gateway, CloudWatch e inferências do Amazon Bedrock. Exclua a stack após os testes:

```bash
sam delete
```

## Referências

- AWS Step Functions: https://aws.amazon.com/pt/step-functions/
- Exemplos de Step Functions: https://github.com/aws-samples/aws-stepfunctions-examples
- Integração Step Functions e Amazon Bedrock: https://docs.aws.amazon.com/step-functions/latest/dg/connect-bedrock.html
- AWS SAM com Step Functions: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-step-functions-in-sam.html
- Amazon Nova no Bedrock: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-micro.html

## Autor

**Luis Felipe Ramalho Carvalho**

Projeto criado para fins educacionais e demonstração prática de arquitetura serverless na AWS.
