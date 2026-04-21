# Formato de Símbolo

#### Padronização do Formato de Símbolo OpenAlgo

OpenAlgo padroniza a identificação de instrumentos financeiros por meio de um formato de símbolo comum para todas as bolsas e corretores, aprimorando a compatibilidade e simplificando o trading automatizado. Esta simbologia uniforme elimina a necessidade de os traders se adaptarem a formatos variados específicos de corretores, agilizando o desenvolvimento e execução de algoritmos. O formato integra identificadores-chave como símbolo base, data de vencimento e tipo de opção, garantindo comunicação consistente e livre de erros dentro dos sistemas de trading. Com OpenAlgo, desenvolvedores podem estender eficientemente as capacidades da plataforma enquanto traders focam na estratégia, não na sintaxe.

{% embed url="<https://www.youtube.com/watch?v=DcmDYpGYdJY>" %}

### Formato de Símbolo para Ações (Equity)

No contexto do OpenAlgo, símbolos de ações são construídos com base no símbolo base da ação.

**Exemplos:**

1. **Ações NSE para Infosys:** Dado o símbolo base `INFY`, o símbolo OpenAlgo para Infosys na Bolsa Nacional da Índia (NSE) seria `INFY`.
2. **Ações BSE para Tata Motors:** Com o símbolo base `TATAMOTORS`, o símbolo na Bolsa de Bombaim (BSE) seria `TATAMOTORS`.
3. **Ações NSE para State Bank of India:** Se o símbolo base é `SBIN`, o símbolo OpenAlgo na NSE seria `SBIN`.

### Formato de Símbolo para Futuros

Para futuros, a simbologia OpenAlgo especifica que o símbolo deve consistir no símbolo base seguido pela data de vencimento e "FUT" para denotar que é um contrato futuro.

**Formato:** `[Símbolo Base][Data de Vencimento]FUT`

Abaixo estão exemplos detalhados para vários contratos futuros:

**Futuros NSE:**

* **Exemplo:** Para futuros do Bank Nifty vencendo em abril de 2024, o símbolo seria `BANKNIFTY24APR24FUT`.

**Futuros BSE:**

* **Exemplo:** Para futuros do SENSEX vencendo em abril de 2024, o símbolo seria `SENSEX24APR24FUT`.

**Futuros de Moeda:**

* **Exemplo:** Para futuros de moeda USDINR vencendo em maio de 2024, o símbolo seria `USDINR10MAY24FUT`.

**Futuros MCX:**

* **Exemplo:** Para futuros de petróleo bruto na MCX vencendo em maio de 2024, o símbolo seria `CRUDEOILM20MAY24FUT`.

**Futuros IRC:**

* **Exemplo:** Para futuros de títulos do governo, especificamente o título 7,26% 2033 vencendo em abril de 2024, o símbolo no OpenAlgo seria `726GS203325APR24FUT`.

### Formato de Símbolo para Opções

Símbolos de opções no OpenAlgo são estruturados para incluir o símbolo base, a data de vencimento, o preço de exercício (strike) e se é uma opção de Compra (Call) ou Venda (Put).

**Formato:** `[Símbolo Base][Data de Vencimento][Preço de Exercício][Tipo de Opção]`

**Exemplos:**

**Opções de Índice NSE:**

* **Exemplo:** Para uma opção de compra (call) do Nifty com preço de exercício de 20.800, vencendo em 28 de março de 2024, o símbolo seria `NIFTY28MAR2420800CE`.

**Opções de Ações NSE:**

* **Exemplo:** Para uma opção de compra (call) da Vedanta Limited (VEDL) com preço de exercício de 292,50, vencendo em 25 de abril de 2024, o símbolo seria `VEDL25APR24292.5CE`.

**Opções de Moeda:**

* **Exemplo:** Para uma opção de compra (call) de Dólar Americano para Rupia Indiana (USDINR) com preço de exercício de 82, vencendo em 19 de abril de 2024, o símbolo seria `USDINR19APR2482CE`.

**Opções MCX:**

* **Exemplo:** Para uma opção de compra (call) de Petróleo Bruto com preço de exercício de 6.750, vencendo em 17 de abril de 2024, o símbolo seria `CRUDEOIL17APR246750CE`.

**Opções IRC:**

* **Exemplo:** Para uma opção de venda (put) de título do governo (726GS2032) com preço de exercício de 97, vencendo em 25 de abril de 2024, o símbolo seria `726GS203225APR2497PE`.

### Símbolos Comuns de Índices NSE (Código da Exchange: NSE_INDEX)

NIFTY
\
NIFTYNXT50
\
FINNIFTY
\
BANKNIFTY
\
MIDCPNIFTY
\
INDIAVIX

### Símbolos Comuns de Índices BSE (Código da Exchange: BSE_INDEX)

SENSEX
\
BANKEX
\
SENSEX50

### Códigos de Exchange

Os formatos de símbolo suportados no OpenAlgo permitem um sistema de identificação que denota onde o instrumento é negociado, junto com detalhes específicos que variam por tipo de instrumento:

* **NSE:** `NSE` para ações da Bolsa Nacional da Índia (National Stock Exchange).
* **BSE:** `BSE` para ações da Bolsa de Bombaim (Bombay Stock Exchange).
* **NFO:** `NFO` para Futuros e Opções da NSE.
* **BFO:** `BFO` para Futuros e Opções da BSE.
* **BCD:** `BCD` para Derivativos de Moeda da BSE.
* **CDS:** `CDS` para Derivativos de Moeda da NSE.
* **MCX:** `MCX` para commodities negociadas na Multi Commodity Exchange.
* **NSE_INDEX:** `NSE_INDEX` para índices na Bolsa Nacional da Índia.
* **BSE_INDEX:** `BSE_INDEX` para índices na Bolsa de Bombaim.

### Esquema de Banco de Dados (Símbolos Comuns)

Para desenvolvedores, entender o esquema de banco de dados é essencial para gerenciar dados efetivamente dentro do OpenAlgo:

1. **id:** Um identificador único para cada registro no banco de dados.
2. **symbol:** O símbolo de trading padrão do instrumento conforme a simbologia OpenAlgo.
3. **brsymbol:** O símbolo específico do corretor para o instrumento, se aplicável.
4. **name:** O nome comum do instrumento (ex: nome da empresa para ações).
5. **exchange:** O código identificador padrão da exchange (ex: NSE, BSE, MCX, CDS, etc.) onde o instrumento é negociado conforme a simbologia OpenAlgo.
6. **brexchange:** O identificador de exchange específico do corretor, se diferente do código padrão da exchange.
7. **token:** Um token ou código único atribuído ao instrumento, possivelmente para rastreamento interno ou identificação específica do corretor.
8. **expiry:** A data de vencimento para contratos derivativos, formatada conforme padrões do corretor/exchange.
9. **strike:** O preço de exercício para contratos de opções.
10. **lotsize:** O tamanho de lote padronizado para o instrumento, particularmente relevante para trading de derivativos.
11. **instrumenttype:** O tipo de instrumento (ex: ação, futuro, opção).
12. **tick_size:** O mínimo movimento de preço do instrumento na exchange.

<figure><img src="https://17901342-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FmBwEhITzgv0O0fEGIIRN%2Fuploads%2FvUWO49dLv5Pklo6qPtIV%2Fimage.png?alt=media&token=7cea9426-f5b9-4c29-b29f-a2e4b9ea7030" alt=""><figcaption></figcaption></figure>

Este esquema captura tanto a simbologia padrão OpenAlgo quanto informações potencialmente divergentes específicas do corretor, permitindo que algoritmos e traders operem em múltiplas plataformas sem confusão. Permite o armazenamento de metadados de instrumentos necessários para atividades de trading e garante que todos os instrumentos financeiros sejam identificáveis e seus detalhes de mercado estejam prontamente acessíveis.
