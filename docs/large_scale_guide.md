# Guia para Buscas em Larga Escala

## Configuração Recomendada por Tipo de Busca

### 1. Busca por Autor Específico
```
Search Type: Author
Query: "Silva, João"
Data Source: OpenAlex (mais rápido)
From Year: 2015
Open Access: Opcional
Maximum Results: 1000
```
**Tempo estimado**: 2-3 minutos

### 2. Busca por Palavra-chave Ampla
```
Search Type: Keyword
Query: "machine learning"
Data Source: OpenAlex
From Year: 2020
Open Access: Yes (reduz volume)
Maximum Results: 2000
```
**Tempo estimado**: 4-5 minutos

### 3. Busca Completa de Instituição
```
Search Type: Keyword
Query: "University of São Paulo"
Data Source: OpenAlex
From Year: 2018
Open Access: No
Maximum Results: 5000
```
**Tempo estimado**: 10-15 minutos

## Estratégias para Grandes Volumes

### Estratégia 1: Busca Incremental por Ano
Ao invés de buscar 10 anos de uma vez:

1. **Primeira busca**: 2023-2024 (500 resultados)
2. **Segunda busca**: 2021-2022 (500 resultados)
3. **Terceira busca**: 2019-2020 (500 resultados)
4. Combine os Excel depois

### Estratégia 2: Refinamento Progressivo
1. **Busca inicial**: 100 resultados para testar
2. **Se relevante**: 500 resultados
3. **Se ainda relevante**: 2000 resultados
4. **Busca final**: 5000 resultados

### Estratégia 3: Divisão por Tipo
Para autores prolíficos ou temas amplos:

1. **Articles only**: adicione "type:article" na busca
2. **Conference papers**: busque separadamente
3. **Books/chapters**: busque separadamente

## Otimizações de Performance

### Para CrossRef
- Evite buscas muito genéricas
- Use aspas para nomes exatos: "João Silva"
- Adicione instituição se souber: "João Silva University"

### Para OpenAlex
- Mais eficiente para grandes volumes
- Melhor para filtrar por citações
- Ideal para análises bibliométricas

## Monitoramento Durante a Busca

### Indicadores de Progresso
```
"Fetched 100 unique results so far..."
"Fetched 200 unique results so far..."
"Fetched 300 unique results so far..."
```

### Sinais de Problemas
- Busca parada no mesmo número por muito tempo
- Mensagens de retry frequentes
- Erro de timeout após 3 tentativas

## Processamento Pós-Busca

### Para 1000+ Resultados
1. **Verifique duplicatas**: O sistema remove automaticamente
2. **Ordene por relevância**: Use a coluna de citações
3. **Filtre por ano**: Se ainda houver muito volume
4. **Exporte em partes**: Se o Excel ficar muito grande

### Limites do Excel
- Excel 2010+: 1.048.576 linhas
- Recomendado: máximo 10.000 linhas por aba
- Se ultrapassar: divida em múltiplos arquivos

## Exemplos de Queries Eficientes

### Busca de Autor Brasileira
```
"Silva, Maria" AND Brazil
"Santos, J" universidade
"Oliveira, Paulo" USP
```

### Busca de Instituição
```
"Universidade de São Paulo"
"UNICAMP" OR "Universidade Estadual de Campinas"
"UFRJ" medicine
```

### Busca Temática Focada
```
"COVID-19" Brazil 2020
"machine learning" agriculture
"sustentabilidade" energias renováveis
```

## Troubleshooting

### Busca Muito Lenta
1. Reduza Maximum Results
2. Use filtros mais específicos
3. Tente em horários alternativos
4. Mude de CrossRef para OpenAlex

### Muitos Resultados Irrelevantes
1. Use aspas para termos exatos
2. Adicione ano mínimo mais recente
3. Ative "Open Access Only"
4. Refine com AND/OR na query

### Excel Não Abre
1. Arquivo muito grande (>100MB)
2. Abra em software alternativo
3. Importe direto no Tainacan
4. Use Python/R para processar

## Melhores Práticas

### Antes da Busca
✓ Teste com 100 resultados primeiro
✓ Anote os parâmetros usados
✓ Verifique espaço em disco
✓ Feche outros programas

### Durante a Busca
✓ Não interrompa o processo
✓ Mantenha conexão estável
✓ Monitore o progresso
✓ Aguarde com paciência

### Após a Busca
✓ Verifique estatísticas de deduplicação
✓ Salve o Excel imediatamente
✓ Faça backup do arquivo
✓ Documente os parâmetros usados

## Casos de Uso Específicos

### Levantamento Institucional
1. Busque por nome da instituição
2. Maximum Results: 5000
3. Exporte tudo
4. Filtre por departamento no Excel

### Revisão Sistemática
1. Use múltiplas palavras-chave
2. Documente cada busca
3. Maximum Results: 2000 por termo
4. Combine e deduplique depois

### Análise de Impacto
1. Use OpenAlex (tem citações)
2. From Year: últimos 5 anos
3. Maximum Results: 3000
4. Ordene por citações

### Portfolio Pessoal
1. Busque seu nome completo
2. Adicione variações do nome
3. Maximum Results: 500
4. Revise manualmente