# Exemplos de Queries Efetivas - Academic Harvester

## 🎯 Queries que Retornam Muitos Resultados

### Para Autores Brasileiros

#### ❌ Query Problemática:
```
Search Type: Author
Query: Silva, J.
Results: ~30 (muito específico)
```

#### ✅ Query Melhorada:
```
Search Type: Author
Query: Silva
From Year: 2020
Results: ~5000+ (muito melhor!)
```

#### ✅ Alternativa com All Fields:
```
Search Type: All Fields
Query: Silva Brazil
Results: ~3000+
```

### Para Instituições

#### ❌ Query Problemática:
```
Search Type: Keyword
Query: USP
Results: ~50 (sigla muito curta)
```

#### ✅ Query Melhorada:
```
Search Type: Affiliation
Query: University of São Paulo
Results: ~5000+
```

#### ✅ Ou use variações:
```
Search Type: Affiliation
Query: Universidade de São Paulo
Results: ~4000+
```

### Para Temas de Pesquisa

#### ❌ Query Problemática:
```
Search Type: Title
Query: COVID-19 vaccination elderly Brazil
Results: ~10 (muito específico)
```

#### ✅ Query Melhorada - Opção 1:
```
Search Type: Keyword
Query: COVID-19 Brazil
Results: ~2000+
```

#### ✅ Query Melhorada - Opção 2:
```
Search Type: All Fields
Query: COVID vaccination Brazil
Results: ~1500+
```

#### ✅ Query Melhorada - Opção 3 (Advanced):
```
Mode: Advanced Search
Main Query: COVID-19
Affiliation: Brazil
From Year: 2020
Results: ~3000+
```

## 📚 Queries por Área do Conhecimento

### Ciências da Saúde
```
Search Type: All Fields
Query: cancer research Brazil
Source: OpenAlex
From Year: 2020
Expected Results: ~2000+
```

### Engenharia
```
Search Type: Keyword
Query: renewable energy Brazil
Source: OpenAlex
Document Types: [journal-article, conference-paper]
Expected Results: ~1500+
```

### Ciências Sociais
```
Search Type: All Fields
Query: social inequality Brazil
Source: OpenAlex
From Year: 2018
Expected Results: ~1000+
```

### Computação
```
Search Type: Keyword
Query: machine learning
Source: OpenAlex
From Year: 2022
Min Citations: 5
Expected Results: ~3000+
```

## 🏛️ Queries para Instituições Brasileiras

### Universidades Federais
```
# UFRJ
Search Type: Affiliation
Query: Federal University of Rio de Janeiro
Expected: ~3000+

# UFMG
Search Type: Affiliation
Query: Federal University of Minas Gerais
Expected: ~2500+

# UFRGS
Search Type: Affiliation
Query: Federal University of Rio Grande do Sul
Expected: ~2000+
```

### Universidades Estaduais
```
# USP
Search Type: Affiliation
Query: University of São Paulo
Expected: ~5000+

# UNICAMP
Search Type: Affiliation
Query: University of Campinas
Expected: ~3000+

# UNESP
Search Type: Affiliation
Query: São Paulo State University
Expected: ~2000+
```

### Institutos de Pesquisa
```
# Fiocruz
Search Type: Affiliation
Query: Oswaldo Cruz Foundation
Expected: ~1500+

# INPE
Search Type: Affiliation
Query: National Institute for Space Research
Expected: ~800+
```

## 🔬 Busca Avançada - Exemplos Complexos

### Exemplo 1: Colaboração Internacional
```
Mode: Advanced Search
Combine with: AND
Author Query: Santos
Affiliation Query: Harvard OR MIT OR Stanford
From Year: 2020
Expected: ~500+
```

### Exemplo 2: Pesquisa Multidisciplinar
```
Mode: Advanced Search
Combine with: OR
Title Query: artificial intelligence
Abstract Query: machine learning
Journal Query: Nature OR Science OR Cell
Expected: ~2000+
```

### Exemplo 3: Produção Regional
```
Mode: Advanced Search
Combine with: AND
Main Query: agriculture sustainability
Affiliation Query: Brazil OR Brasil
Open Access: Yes
From Year: 2021
Expected: ~1000+
```

## 💡 Dicas para Maximizar Resultados

### 1. Use Termos em Inglês
```
❌ "inteligência artificial"
✅ "artificial intelligence"
```

### 2. Evite Acentos em Nomes
```
❌ "José São Paulo"
✅ "Jose Sao Paulo"
```

### 3. Tente Variações de Nomes
```
Query 1: "University of São Paulo"
Query 2: "University of Sao Paulo"
Query 3: "USP Brazil"
```

### 4. Use All Fields para Buscas Amplas
```
Em vez de: Title = "specific term"
Use: All Fields = "broader term"
```

### 5. Combine Termos Relacionados
```
Mode: Advanced Search
Main Query: diabetes OR "diabetes mellitus"
Affiliation: Brazil OR Brasil
```

## 📊 Estratégias por Volume Desejado

### Para obter ~100 resultados:
- Use Author com nome completo
- Adicione ano específico
- Use título muito específico

### Para obter ~500 resultados:
- Use Keyword com 2-3 termos
- Período de 2-3 anos
- Uma instituição específica

### Para obter ~1000+ resultados:
- Use All Fields
- Termos gerais
- Período de 5+ anos
- Ou use Affiliation de universidade grande

### Para obter ~5000 resultados:
- Use termos muito gerais
- All Fields
- Período de 10+ anos
- Grandes instituições
- Temas populares (COVID, AI, cancer)

## ⚠️ Queries a Evitar

### Muito Restritivas:
```
❌ Title: "Specific therapeutic approach for rare disease in elderly Brazilian patients"
❌ Author: "Silva, J.A." AND Title: "COVID" AND Year: 2023
```

### Muito Genéricas (podem travar):
```
❌ All Fields: "the"
❌ Keyword: "a"
❌ All Fields: "" (vazio)
```

### Com Erros Comuns:
```
❌ Author: Silva, João Carlos (use apenas Silva ou "Silva, J")
❌ Affiliation: USP - Universidade (use nome completo)
❌ Title: COVID 19 (use COVID-19 com hífen)
```

## 🚀 Teste Rápido de Conectividade

Para verificar se o sistema está funcionando, use estas queries que sempre retornam resultados:

```
1. Search Type: All Fields
   Query: COVID-19
   Source: OpenAlex
   From Year: 2020
   Expected: ~5000+

2. Search Type: Keyword  
   Query: machine learning
   Source: OpenAlex
   Expected: ~5000+

3. Search Type: All Fields
   Query: Brazil  
   Source: CrossRef
   Expected: ~5000+
```

Se estas não retornarem resultados, verifique sua conexão com a internet!