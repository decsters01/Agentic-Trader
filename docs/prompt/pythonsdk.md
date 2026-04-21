# Python

Para instalar a biblioteca OpenAlgo Python, use pip:

```bash
pip install openalgo
```

### Obter a Chave de API OpenAlgo

Certifique-se de que sua Aplicação OpenAlgo esteja em execução. Faça login na Aplicação OpenAlgo com credenciais válidas e obtenha a chave de API OpenAlgo.

Para parâmetros detalhados de funções, consulte a [Documentação da API](https://docs.openalgo.in/api-documentation/v1)

### Começando com OpenAlgo

Primeiro, importe a classe `api` da biblioteca OpenAlgo e inicialize-a com sua chave de API:

```python
from openalgo import api

# Substitua 'sua_chave_de_api_aqui' pela sua chave de API real
# Especifique a URL do host com seu domínio hospedado ou domínio ngrok.
# Se estiver executando localmente no Windows, use o valor de host padrão.
client = api(api_key='sua_chave_de_api_aqui', host='http://127.0.0.1:5000')

```

### Verificar Versão do OpenAlgo

```python
import openalgo 
openalgo.__version__
```

### Exemplos

Consulte a documentação sobre [constantes de ordem](https://docs.openalgo.in/api-documentation/v1/order-constants) e consulte a referência da API para detalhes sobre parâmetros opcionais.

### Exemplo PlaceOrder

Para colocar uma nova ordem a mercado:

```python
response = client.placeorder(
    strategy="Python",
    symbol="NHPC",
    action="BUY",
    exchange="NSE",
    price_type="MARKET",
    product="MIS",
    quantity=1
)
print(response)

```

Resposta de Ordem a Mercado

```json
{'orderid': '250408000989443', 'status': 'success'}
```

Para colocar uma nova ordem limitada:

```python
response = client.placeorder(
    strategy="Python",
    symbol="YESBANK",
    action="BUY",
    exchange="NSE",
    price_type="LIMIT",
    product="MIS",
    quantity="1",
    price="16",
    trigger_price="0",
    disclosed_quantity ="0",
)
print(response)
```

Resposta de Ordem Limitada

```json
{'orderid': '250408001003813', 'status': 'success'}
```

### Exemplo PlaceSmartOrder

Para colocar uma ordem inteligente considerando o tamanho atual da posição:

```python
response = client.placesmartorder(
    strategy="Python",
    symbol="TATAMOTORS",
    action="SELL",
    exchange="NSE",
    price_type="MARKET",
    product="MIS",
    quantity=1,
    position_size=5
)
print(response)

```

Resposta de Ordem Inteligente a Mercado

```json
{'orderid': '250408000997543', 'status': 'success'}
```

### Exemplo OptionsOrder

Para colocar ordem de opções ATM (No Dinheiro)

```python
response = client.optionsorder(
      strategy="python",
      underlying="NIFTY",
      exchange="NSE_INDEX",
      expiry_date="28OCT25",
      strike_int=50,
      offset="ATM",
      option_type="CE",
      action="BUY",
      quantity=75,
      pricetype="MARKET",
      product="NRML"
  )

print(response)
```

Resposta de Ordem de Opções

```json
{
  "exchange": "NFO",
  "offset": "ATM",
  "option_type": "CE",
  "orderid": "25102800000006",
  "status": "success",
  "symbol": "NIFTY28OCT2525950CE",
  "underlying": "NIFTY28OCT25FUT",
  "underlying_ltp": 25966.05
}
```

Para colocar ordem de opções ITM (Dentro do Dinheiro)

```python
response = client.optionsorder(
      strategy="python",
      underlying="NIFTY",
      exchange="NSE_INDEX",
      expiry_date="28OCT25",
      strike_int=50,
      offset="ITM4",
      option_type="PE",
      action="BUY",
      quantity=75,
      pricetype="MARKET",
      product="NRML"
  )

print(response)
```

Resposta de Ordem de Opções

```json
{
  "exchange": "NFO",
  "offset": "ITM4",
  "option_type": "PE",
  "orderid": "25102800000007",
  "status": "success",
  "symbol": "NIFTY28OCT2526150PE",
  "underlying": "NIFTY28OCT25FUT",
  "underlying_ltp": 25966.05
}
```

Para colocar ordem de opções OTM (Fora do Dinheiro)

```python
response = client.optionsorder(
      strategy="python",
      underlying="NIFTY",
      exchange="NSE_INDEX",
      expiry_date="28OCT25",
      strike_int=50,
      offset="OTM5",
      option_type="CE",
      action="BUY",
      quantity=75,
      pricetype="MARKET",
      product="NRML"
  )

print(response)
```

Resposta de Ordem de Opções

```json
{
  "exchange": "NFO",
  "mode": "analyze",
  "offset": "OTM5",
  "option_type": "CE",
  "orderid": "25102800000008",
  "status": "success",
  "symbol": "NIFTY28OCT2526200CE",
  "underlying": "NIFTY28OCT25FUT",
  "underlying_ltp": 25966.05
}
```

### Exemplo BasketOrder

Para colocar uma nova ordem em cesta:

```python
basket_orders = [
        {
            "symbol": "BHEL",
            "exchange": "NSE",
            "action": "BUY",
            "quantity": 1,
            "pricetype": "MARKET",
            "product": "MIS"
        },
        {
            "symbol": "ZOMATO",
            "exchange": "NSE",
            "action": "SELL",
            "quantity": 1,
            "pricetype": "MARKET",
            "product": "MIS"
        }
    ]
response = client.basketorder(orders=basket_orders)
print(response)
```

**Resposta de Ordem em Cesta**

```json
{
  "status": "success",
  "results": [
    {
      "symbol": "BHEL",
      "status": "success",
      "orderid": "250408000999544"
    },
    {
      "symbol": "ZOMATO",
      "status": "success",
      "orderid": "250408000997545"
    }
  ]
}

```

### Exemplo SplitOrder

Para colocar uma nova ordem fracionada:

```python
response = client.splitorder(
    symbol="YESBANK",
    exchange="NSE",
    action="SELL",
    quantity=105,
    splitsize=20,
    price_type="MARKET",
    product="MIS"
    )
print(response)

```

**Resposta SplitOrder**

```json
{
  "status": "success",
  "split_size": 20,
  "total_quantity": 105,
  "results": [
    {
      "order_num": 1,
      "orderid": "250408001021467",
      "quantity": 20,
      "status": "success"
    },
    {
      "order_num": 2,
      "orderid": "250408001021459",
      "quantity": 20,
      "status": "success"
    },
    {
      "order_num": 3,
      "orderid": "250408001021466",
      "quantity": 20,
      "status": "success"
    },
    {
      "order_num": 4,
      "orderid": "250408001021470",
      "quantity": 20,
      "status": "success"
    },
    {
      "order_num": 5,
      "orderid": "250408001021471",
      "quantity": 20,
      "status": "success"
    },
    {
      "order_num": 6,
      "orderid": "250408001021472",
      "quantity": 5,
      "status": "success"
    }
  ]
}

```

### Exemplo ModifyOrder

Para modificar uma ordem existente:

```python
response = client.modifyorder(
    order_id="250408001002736",
    strategy="Python",
    symbol="YESBANK",
    action="BUY",
    exchange="NSE",
    price_type="LIMIT",
    product="CNC",
    quantity=1,
    price=16.5
)
print(response)
```

**Resposta Modify Order**

```json
{'orderid': '250408001002736', 'status': 'success'}
```

### Exemplo CancelOrder

Para cancelar uma ordem existente:

```python
response = client.cancelorder(
    order_id="250408001002736",
    strategy="Python"
)
print(response)
```

**Resposta Cancelorder**

```json
{'orderid': '250408001002736', 'status': 'success'}
```

### Exemplo CancelAllOrder

Para cancelar todas as ordens abertas e acionar ordens pendentes

```python
response = client.cancelallorder(
    strategy="Python"
)
print(response)
```

**Resposta Cancelallorder**

```json
{
  "status": "success",
  "message": "Canceled 5 orders. Failed to cancel 0 orders.",
  "canceled_orders": [
    "250408001042620",
    "250408001042667",
    "250408001042642",
    "250408001043015",
    "250408001043386"
  ],
  "failed_cancellations": []
}

```

### Exemplo ClosePosition

Para fechar todas as posições abertas em várias exchanges

```python
response = client.closeposition(
    strategy="Python"
)
print(response)
```

**Resposta ClosePosition**

```json
{'message': 'All Open Positions Squared Off', 'status': 'success'}
```

### Exemplo OrderStatus

Para obter o Status Atual da Ordem

```python
response = client.orderstatus(
    order_id="250828000185002",
    strategy="Test Strategy"
    )
print(response)
```

**Resposta Orderstatus**

```json
{
  "data": {
    "action": "BUY",
    "average_price": 18.95,
    "exchange": "NSE",
    "order_status": "complete",
    "orderid": "250828000185002",
    "price": 0,
    "pricetype": "MARKET",
    "product": "MIS",
    "quantity": "1",
    "symbol": "YESBANK",
    "timestamp": "28-Aug-2025 09:59:10",
    "trigger_price": 0
  },
  "status": "success"
}
```

### Exemplo OpenPosition

Para obter a Posição Aberta Atual

```python
response = client.openposition(
            strategy="Test Strategy",
            symbol="YESBANK",
            exchange="NSE",
            product="MIS"
        )
print(response)
```

Resposta OpenPosition

```json
{'quantity': '-10', 'status': 'success'}
```

### Exemplo Quotes

```python
response = client.quotes(symbol="RELIANCE", exchange="NSE")
print(response)
```

**Resposta Quotes**

```json
{
  "status": "success",
  "data": {
    "open": 1172.0,
    "high": 1196.6,
    "low": 1163.3,
    "ltp": 1187.75,
    "ask": 1188.0,
    "bid": 1187.85,
    "prev_close": 1165.7,
    "volume": 14414545
  }
}
```

### Exemplo Depth

```python
response = client.depth(symbol="SBIN", exchange="NSE")
print(response)
```

**Resposta Depth**

```json
{
  "status": "success",
  "data": {
    "open": 760.0,
    "high": 774.0,
    "low": 758.15,
    "ltp": 769.6,
    "ltq": 205,
    "prev_close": 746.9,
    "volume": 9362799,
    "oi": 161265750,
    "totalbuyqty": 591351,
    "totalsellqty": 835701,
    "asks": [
      {
        "price": 769.6,
        "quantity": 767
      },
      {
        "price": 769.65,
        "quantity": 115
      },
      {
        "price": 769.7,
        "quantity": 162
      },
      {
        "price": 769.75,
        "quantity": 1121
      },
      {
        "price": 769.8,
        "quantity": 430
      }
    ],
    "bids": [
      {
        "price": 769.4,
        "quantity": 886
      },
      {
        "price": 769.35,
        "quantity": 212
      },
      {
        "price": 769.3,
        "quantity": 351
      },
      {
        "price": 769.25,
        "quantity": 343
      },
      {
        "price": 769.2,
        "quantity": 399
      }
    ]
  }
}

```

### Exemplo History

```python
response = client.history(symbol="SBIN", 
    exchange="NSE", 
    interval="5m", 
    start_date="2025-04-01", 
    end_date="2025-04-08"
    )
print(response)
```

**Resposta History**

```json
                            close    high     low    open  volume
timestamp                                                        
2025-04-01 09:15:00+05:30  772.50  774.00  763.20  766.50  318625
2025-04-01 09:20:00+05:30  773.20  774.95  772.10  772.45  197189
2025-04-01 09:25:00+05:30  775.15  775.60  772.60  773.20  227544
2025-04-01 09:30:00+05:30  777.35  777.50  774.85  775.15  134596
2025-04-01 09:35:00+05:30  778.00  778.00  776.25  777.50  145385
...                           ...     ...     ...     ...     ...
2025-04-08 14:00:00+05:30  768.25  770.70  767.85  768.50  142478
2025-04-08 14:05:00+05:30  769.10  769.80  766.60  768.15  128283
2025-04-08 14:10:00+05:30  769.05  769.85  768.40  769.10  119084
2025-04-08 14:15:00+05:30  770.05  770.50  769.05  769.05  158299
2025-04-08 14:20:00+05:30  769.95  770.50  769.40  770.05  125485

[437 rows x 5 columns]
```

### Exemplo Intervals

```python
response = client.intervals()
print(response)
```

**Resposta Intervals**

```json
{
  "status": "success",
  "data": {
    "months": [],
    "weeks": [],
    "days": ["D"],
    "hours": ["1h"],
    "minutes": ["10m", "15m", "1m", "30m", "3m", "5m"],
    "seconds": []
  }
}
```

### Exemplo Symbol

```python
response = client.symbol(
            symbol="RELIANCE",
            exchange="NSE"
            )
print(response)
```

**Resposta Symbols**

```json
{
  "status": "success",
  "data": {
    "id": 979,
    "name": "RELIANCE",
    "symbol": "RELIANCE",
    "brsymbol": "RELIANCE-EQ",
    "exchange": "NSE",
    "brexchange": "NSE",
    "instrumenttype": "",
    "expiry": "",
    "strike": -0.01,
    "lotsize": 1,
    "tick_size": 0.05,
    "token": "2885"
  }
}
```

### Exemplo Search

```python
response = client.search(query="NIFTY 25000 JUL CE",exchange="NFO")
print(response)
```

**Resposta Search**

```json
{
  "data": [
    {
      "brexchange": "NFO",
      "brsymbol": "NIFTY17JUL2525000CE",
      "exchange": "NFO",
      "expiry": "17-JUL-25",
      "instrumenttype": "OPTIDX",
      "lotsize": 75,
      "name": "NIFTY",
      "strike": 25000,
      "symbol": "NIFTY17JUL2525000CE",
      "tick_size": 0.05,
      "token": "47275"
    },
    {
      "brexchange": "NFO",
      "brsymbol": "FINNIFTY31JUL2525000CE",
      "exchange": "NFO",
      "expiry": "31-JUL-25",
      "instrumenttype": "OPTIDX",
      "lotsize": 65,
      "name": "FINNIFTY",
      "strike": 25000,
      "symbol": "FINNIFTY31JUL2525000CE",
      "tick_size": 0.05,
      "token": "54763"
    },
    {
      "brexchange": "NFO",
      "brsymbol": "NIFTY24JUL2525000CE",
      "exchange": "NFO",
      "expiry": "24-JUL-25",
      "instrumenttype": "OPTIDX",
      "lotsize": 75,
      "name": "NIFTY",
      "strike": 25000,
      "symbol": "NIFTY24JUL2525000CE",
      "tick_size": 0.05,
      "token": "49487"
    }
  ],
  "message": "Found 6 matching symbols",
  "status": "success"
}
```

### Exemplo OptionSymbol

Opção ATM (No Dinheiro)

```python
response = client.optionsymbol(
      underlying="NIFTY",
      exchange="NSE_INDEX",
      expiry_date="28OCT25",
      strike_int=50,
      offset="ATM",
      option_type="CE"
  )

print(response)
```

**Resposta OptionSymbol**

```json
{
  "status": "success",
  "symbol": "NIFTY28OCT2525950CE",
  "exchange": "NFO",
  "lotsize": 75,
  "tick_size": 0.05,
  "underlying_ltp": 25966.05
}
```

Opção ITM (Dentro do Dinheiro)

```python
response = client.optionsymbol(
      underlying="NIFTY",
      exchange="NSE_INDEX",
      expiry_date="28OCT25",
      strike_int=50,
      offset="ITM3",
      option_type="PE"
  )

print(response)
```

**Resposta OptionSymbol**

```json
{
  "status": "success",
  "symbol": "NIFTY28OCT2526100PE",
  "exchange": "NFO",
  "lotsize": 75,
  "tick_size": 0.05,
  "underlying_ltp": 25966.05
}
```

Opção OTM (Fora do Dinheiro)

```python
response = client.optionsymbol(
      underlying="NIFTY",
      exchange="NSE_INDEX",
      expiry_date="28OCT25",
      strike_int=50,
      offset="OTM4",
      option_type="CE"
  )

print(response)
```

**Resposta OptionSymbol**

```json
{
  "status": "success",
  "symbol": "NIFTY28OCT2526150CE",
  "exchange": "NFO",
  "lotsize": 75,
  "tick_size": 0.05,
  "underlying_ltp": 25966.05
}
```

### Exemplo OptionGreeks

```python
response = client.optiongreeks(
      symbol="NIFTY25NOV2526000CE",
      exchange="NFO",
      interest_rate=0.00,
      underlying_symbol="NIFTY",
      underlying_exchange="NSE_INDEX"
  )

print(response)
```

Resposta OptionGreeks

```
{
'days_to_expiry': 28.5071,
 'exchange': 'NFO',
 'expiry_date': '25-Nov-2025',
 'greeks': {'delta': 0.4967,
  'gamma': 0.000352,
  'rho': 9.733994,
  'theta': -7.919,
  'vega': 28.9489},
 'implied_volatility': 15.6,
 'interest_rate': 0.0,
 'option_price': 435,
 'option_type': 'CE',
 'spot_price': 25966.05,
 'status': 'success',
 'strike': 26000.0,
 'symbol': 'NIFTY25NOV2526000CE',
 'underlying': 'NIFTY'
}
```

### Exemplo Expiry

```python
response = client.expiry(
    symbol="NIFTY",
    exchange="NFO",
    instrumenttype="options"
)

response
```

**Resposta Expiry**

```
{'data': ['10-JUL-25',
  '17-JUL-25',
  '24-JUL-25',
  '31-JUL-25',
  '07-AUG-25',
  '28-AUG-25',
  '25-SEP-25',
  '24-DEC-25',
  '26-MAR-26',
  '25-JUN-26',
  '31-DEC-26',
  '24-JUN-27',
  '30-DEC-27',
  '29-JUN-28',
  '28-DEC-28',
  '28-JUN-29',
  '27-DEC-29',
  '25-JUN-30'],
 'message': 'Found 18 expiry dates for NIFTY options in NFO',
 'status': 'success'}
```

### Exemplo de Alerta Telegram

```python
response = client.telegram(
      username="<openalgo_loginid>",
      message="NIFTY crossed 26000!"
  )

print(response)
```

**Resposta de Alerta Telegram**

```json
{
  "message": "Notification sent successfully",
  "status": "success"
}
```

### Exemplo Funds

```python
response = client.funds()
print(response)
```

**Resposta Funds**

```json
{
  "status": "success",
  "data": {
    "availablecash": "320.66",
    "collateral": "0.00",
    "m2mrealized": "3.27",
    "m2munrealized": "-7.88",
    "utiliseddebits": "679.34"
  }
}

```

### Exemplo OrderBook

```python
response = client.orderbook()
print(response)
```

```json
{
  "status": "success",
  "data": {
    "orders": [
      {
        "action": "BUY",
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "orderid": "250408000989443",
        "product": "MIS",
        "quantity": "1",
        "price": 1186.0,
        "pricetype": "MARKET",
        "order_status": "complete",
        "trigger_price": 0.0,
        "timestamp": "08-Apr-2025 13:58:03"
      },
      {
        "action": "BUY",
        "symbol": "YESBANK",
        "exchange": "NSE",
        "orderid": "250408001002736",
        "product": "MIS",
        "quantity": "1",
        "price": 16.5,
        "pricetype": "LIMIT",
        "order_status": "cancelled",
        "trigger_price": 0.0,
        "timestamp": "08-Apr-2025 14:13:45"
      }
    ],
    "statistics": {
      "total_buy_orders": 2.0,
      "total_sell_orders": 0.0,
      "total_completed_orders": 1.0,
      "total_open_orders": 0.0,
      "total_rejected_orders": 0.0
    }
  }
}

```

### Exemplo TradeBook

```python
response = client.tradebook()
print(response)
```

Resposta TradeBook

```python
{
  "status": "success",
  "data": [
    {
      "action": "BUY",
      "symbol": "RELIANCE",
      "exchange": "NSE",
      "orderid": "250408000989443",
      "product": "MIS",
      "quantity": 0.0,
      "average_price": 1180.1,
      "timestamp": "13:58:03",
      "trade_value": 1180.1
    },
    {
      "action": "SELL",
      "symbol": "NHPC",
      "exchange": "NSE",
      "orderid": "250408001086129",
      "product": "MIS",
      "quantity": 0.0,
      "average_price": 83.74,
      "timestamp": "14:28:49",
      "trade_value": 83.74
    }
  ]
}

```

### Exemplo PositionBook

```python
response = client.positionbook()
print(response)
```

**Resposta PositionBook**

```json
{
  "status": "success",
  "data": [
    {
      "symbol": "NHPC",
      "exchange": "NSE",
      "product": "MIS",
      "quantity": "-1",
      "average_price": "83.74",
      "ltp": "83.72",
      "pnl": "0.02"
    },
    {
      "symbol": "RELIANCE",
      "exchange": "NSE",
      "product": "MIS",
      "quantity": "0",
      "average_price": "0.0",
      "ltp": "1189.9",
      "pnl": "5.90"
    },
    {
      "symbol": "YESBANK",
      "exchange": "NSE",
      "product": "MIS",
      "quantity": "-104",
      "average_price": "17.2",
      "ltp": "17.31",
      "pnl": "-10.44"
    }
  ]
}

```

### Exemplo Holdings

```python
response = client.holdings()
print(response)
```

Resposta Holdings

```json
{
  "status": "success",
  "data": {
    "holdings": [
      {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "product": "CNC",
        "quantity": 1,
        "pnl": -149.0,
        "pnlpercent": -11.1
      },
      {
        "symbol": "TATASTEEL",
        "exchange": "NSE",
        "product": "CNC",
        "quantity": 1,
        "pnl": -15.0,
        "pnlpercent": -10.41
      },
      {
        "symbol": "CANBK",
        "exchange": "NSE",
        "product": "CNC",
        "quantity": 5,
        "pnl": -69.0,
        "pnlpercent": -13.43
      }
    ],
    "statistics": {
      "totalholdingvalue": 1768.0,
      "totalinvvalue": 2001.0,
      "totalprofitandloss": -233.15,
      "totalpnlpercentage": -11.65
    }
  }
}

```

### Exemplo Analyzer Status

```python
response  = client.analyzerstatus()
print(response)
```

Resposta Analyzer Status

```json
{'data': {'analyze_mode': True, 'mode': 'analyze', 'total_logs': 2},
 'status': 'success'}
```

### Exemplo Analyzer Toggle

```python
# Alternar para modo análise (respostas simuladas)
response = client.analyzertoggle(mode=True)
print(response)
```

Resposta Analyzer Toggle

```
{'data': {'analyze_mode': True,
  'message': 'Analyzer mode switched to analyze',
  'mode': 'analyze',
  'total_logs': 2},
 'status': 'success'}
```

### Dados LTP (WebSocket Streaming)

```python
from openalgo import api
import time

# Inicializar cliente OpenAlgo
client = api(
    api_key="your_api_key",                  # Substitua pela sua chave de API OpenAlgo real
    host="http://127.0.0.1:5000",            # Host da API REST
    ws_url="ws://127.0.0.1:8765"             # Host WebSocket
)

# Definir instrumentos para assinar LTP
instruments = [
    {"exchange": "NSE", "symbol": "RELIANCE"},
    {"exchange": "NSE", "symbol": "INFY"}
]

# Função de callback para atualizações LTP
def on_ltp(data):
    print("LTP Update Received:")
    print(data)

# Conectar e assinar
client.connect()
client.subscribe_ltp(instruments, on_data_received=on_ltp)

# Executar por alguns segundos para receber dados
try:
    time.sleep(10)
finally:
    client.unsubscribe_ltp(instruments)
    client.disconnect()

```

### Quotes (WebSocket Streaming)

```python
from openalgo import api
import time

# Inicializar cliente OpenAlgo
client = api(
    api_key="your_api_key",                  # Substitua pela sua chave de API OpenAlgo real
    host="http://127.0.0.1:5000",            # Host da API REST
    ws_url="ws://127.0.0.1:8765"             # Host WebSocket
)

# Lista de instrumentos
instruments = [
    {"exchange": "NSE", "symbol": "RELIANCE"},
    {"exchange": "NSE", "symbol": "INFY"}
]

# Callback para atualizações de Quote
def on_quote(data):
    print("Quote Update Received:")
    print(data)

# Conectar e assinar to quote stream
client.connect()
client.subscribe_quote(instruments, on_data_received=on_quote)

# Manter o script em execução para receber dados
try:
    time.sleep(10)
finally:
    client.unsubscribe_quote(instruments)
    client.disconnect()

```

### Depth (WebSocket Streaming)

```python
from openalgo import api
import time

# Inicializar cliente OpenAlgo
client = api(
    api_key="your_api_key",                  # Substitua pela sua chave de API OpenAlgo real
    host="http://127.0.0.1:5000",            # Host da API REST
    ws_url="ws://127.0.0.1:8765"             # Host WebSocket
)

# Lista de instrumentos for depth
instruments = [
    {"exchange": "NSE", "symbol": "RELIANCE"},
    {"exchange": "NSE", "symbol": "INFY"}
]

# Callback para atualizações de profundidade de mercado
def on_depth(data):
    print("Market Depth Update Received:")
    print(data)

# Conectar e assinar to depth stream
client.connect()
client.subscribe_depth(instruments, on_data_received=on_depth)

# Executar por alguns segundos para coletar dados
try:
    time.sleep(10)
finally:
    client.unsubscribe_depth(instruments)
    client.disconnect()

```
