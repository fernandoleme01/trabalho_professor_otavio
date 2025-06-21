# Dados sobre o Mercado Imobiliário

## Mercado Tradicional

### Fontes de Dados
- **Índice FipeZAP**: Principal índice de preços de imóveis residenciais e comerciais com abrangência nacional. As variações dos preços são calculadas pela Fipe.
- **DataZap/Grupo OLX**: Fornece dados históricos e comparativos de preços de imóveis.
- **Secovi**: Sindicato da Habitação, fornece dados sobre taxas de juros e financiamento imobiliário.
- **IBRESP**: Instituto Brasileiro de Estudos e Pesquisas, fornece dados sobre tendências do mercado.
- **Banco Central do Brasil**: Dados sobre financiamento imobiliário e taxas de juros.
- **CBIC**: Câmara Brasileira da Indústria da Construção, fornece dados sobre o setor.
- **CRECI**: Conselho Regional de Corretores de Imóveis, dados sobre transações imobiliárias.
- **Registro de Imóveis do Brasil**: Dados oficiais sobre transações imobiliárias.

### Tendências Recentes
- Aumento de 1,87% nos preços dos imóveis residenciais à venda no primeiro trimestre de 2025, conforme o Índice FipeZAP.
- Alta dos preços dos imóveis tem limitado o poder de compra da classe média, empurrando-a para apartamentos menores.
- Taxas de juros do financiamento imobiliário estão na casa dos 11%, abaixo da Selic (13,25%).
- O segmento de imóveis de Médio e Alto Padrão apresentou aumento de 7,1% nas vendas, com 24.426 unidades vendidas.
- Capitais nordestinas registraram os maiores preços médios por unidade de luxo (cerca de R$ 3 milhões em Fortaleza, Salvador, Recife).

## Mercado de Leilões

### Fontes de Dados
- **Leilões Judiciais**: Site especializado em leilões judiciais de imóveis, veículos e outros bens.
- **Mega Leilões**: Plataforma de leilões judiciais e extrajudiciais online.
- **Zuk**: Empresa que promove leilões judiciais.
- **BTG Pactual**: Realizou levantamento sobre descontos em leilões.

### Características dos Leilões
- Os imóveis ofertados em leilões têm, em média, 43% de desconto em relação ao valor de mercado, segundo levantamento do BTG Pactual.
- Leilões judiciais podem oferecer descontos superiores a 50% do valor de mercado.
- Nova proposta de lei pode permitir vendas por menos de 50% do valor avaliado em casos específicos.
- No Rio de Janeiro, é comum arrematar imóveis por 60% do preço de mercado em leilões judiciais.
- Zuk promoveu leilões com descontos de até 62% diante da média de preços do mercado.
- Bradesco AF oferece imóveis com valores até 70% abaixo na segunda praça.
- Alguns leilões anunciam descontos de até 80% do valor de mercado.

## Metodologias de Avaliação de Imóveis

### NBR 14653 (ABNT)
A norma brasileira NBR 14653 regulamenta a avaliação de bens, incluindo imóveis, e estabelece os seguintes métodos:

1. **Método Comparativo Direto de Dados de Mercado**:
   - Compara o imóvel com outros semelhantes no mercado.
   - Utiliza fatores de homogeneização para ajustar as diferenças.
   - É o método mais utilizado e confiável quando há dados de mercado disponíveis.

2. **Método Evolutivo**:
   - Calcula o valor do imóvel somando o valor do terreno e das benfeitorias.
   - Considera o fator de comercialização que representa a valorização ou desvalorização do imóvel.

3. **Método Involutivo**:
   - Baseado no aproveitamento eficiente do bem.
   - Calcula o valor do imóvel com base no seu potencial de desenvolvimento.

4. **Método da Renda**:
   - Avalia o imóvel com base na capitalização da renda que ele é capaz de gerar.
   - Utilizado principalmente para imóveis comerciais e de investimento.

5. **Método do Custo de Reprodução**:
   - Calcula o valor do imóvel com base no custo necessário para reproduzi-lo.
   - Considera a depreciação física e funcional do imóvel.

### Aplicação nas Comparações
Para comparar valores de imóveis em leilões e no mercado tradicional, é recomendável:

1. Utilizar o Método Comparativo Direto de Dados de Mercado para estabelecer o valor de referência no mercado tradicional.
2. Comparar com o valor de avaliação e o valor de arrematação nos leilões.
3. Calcular o percentual de desconto em relação ao valor de mercado.
4. Analisar fatores que influenciam os descontos, como:
   - Estado de conservação do imóvel
   - Existência de ocupantes
   - Pendências jurídicas
   - Localização
   - Liquidez do mercado na região



## Pipeline Técnico de Extração de Dados

### Características do Sistema de Coleta

**Orquestração com Kestra**: Pipeline totalmente automatizado usando YAML para definição de workflows de extração de dados das diferentes fontes (leilões judiciais, VivaReal, IBGE, etc.).

**Bypass de Proteções**: Utilizado proxy para contornar Cloudflare e outros sistemas de proteção anti-bot, garantindo acesso consistente aos dados públicos.

**Processamento ETL**: Extração, transformação e carregamento de dados estruturados seguindo as melhores práticas de engenharia de dados:
- **Extract**: Coleta automatizada de dados de múltiplas fontes
- **Transform**: Normalização, limpeza e padronização dos dados coletados
- **Load**: Armazenamento em formato estruturado para análise

**Armazenamento em Camadas**: Implementa arquitetura Bronze/Silver para data lake:
- **Bronze**: Dados brutos coletados diretamente das fontes
- **Silver**: Dados limpos e normalizados prontos para análise

**Conformidade Ética**: Segue diretrizes de web scraping responsável:
- Respeito ao robots.txt dos sites
- Limitação de taxa de requisições
- Conformidade com LGPD
- Uso apenas de dados públicos

### Implementação Técnica

O pipeline automatizado permite:
1. Coleta periódica de dados de leilões e mercado tradicional
2. Processamento em tempo real das informações coletadas
3. Atualização automática dos datasets para análise
4. Monitoramento da qualidade dos dados
5. Geração de relatórios automatizados

Esta abordagem garante a reprodutibilidade do estudo e permite atualizações contínuas da análise comparativa entre valores de imóveis em leilões e no mercado tradicional.

