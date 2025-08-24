# Academic Harvester - Resumo do Projeto

## Estrutura Final do Projeto

```
academic_harvester/
│
├── app.py                          # Interface Streamlit principal
├── iniciar.bat                     # Script de inicialização Windows
├── instrucoes.txt                  # Instruções em português
├── requirements.txt                # Dependências Python
│
├── TAINACAN_IMPORT_GUIDE.md        # Guia de importação Tainacan
├── tainacan_mapping_example.json   # Exemplo de mapeamento
├── LARGE_SCALE_SEARCH_GUIDE.md     # Guia para grandes buscas
├── CHANGELOG_v2.md                 # Mudanças versão 2
├── CHANGELOG_v3.md                 # Mudanças versão 3
├── PROJECT_SUMMARY.md              # Este arquivo
│
├── apis/                           
│   ├── __init__.py                # Arquivo vazio (criar)
│   ├── crossref.py                # API CrossRef com paginação
│   └── openalex.py                # API OpenAlex com paginação
│
├── logic/                          
│   ├── __init__.py                # Arquivo vazio (criar)
│   ├── metrics.py                 # Cálculo h-index, g-index
│   └── dublin_mapper.py           # Mapeamento Dublin Core
│
└── data/                           
    └── resultados/                # Excel files salvos aqui
```

## Funcionalidades Principais

### 1. Busca Acadêmica
- ✅ Busca por Autor, Título ou Palavra-chave
- ✅ Duas fontes: CrossRef e OpenAlex
- ✅ Até 5000 resultados por busca
- ✅ Deduplicação automática

### 2. Filtros Avançados
- ✅ Filtro por ano (From Year)
- ✅ Filtro Open Access Only
- ✅ Configuração de máximo de resultados

### 3. Metadados Dublin Core
- ✅ 15 elementos padrão mapeados
- ✅ Metadados adicionais preservados
- ✅ Formatação para Tainacan

### 4. Métricas Bibliométricas
- ✅ Total de publicações
- ✅ Total de citações
- ✅ Média de citações
- ✅ h-index
- ✅ g-index

### 5. Exportação
- ✅ Excel com múltiplas abas
- ✅ Otimizado para Tainacan
- ✅ Campos em colunas separadas
- ✅ UTF-8 encoding

## Características Técnicas

### Performance
- Paginação automática
- Retry em caso de erro
- Deduplicação por DOI/ID/Título
- Progress tracking no console

### Limites
- CrossRef: 100 resultados/página
- OpenAlex: 200 resultados/página
- Máximo: 5000 resultados/busca
- Timeout: 30 segundos/request

### Compatibilidade
- Windows 10+
- Python 3.10+
- Excel 2010+
- Tainacan 0.18+

## Casos de Uso

### 1. Repositório Institucional
- Buscar publicações da instituição
- Filtrar apenas Open Access
- Importar no Tainacan

### 2. Revisão Sistemática
- Buscar por palavras-chave
- Coletar até 5000 artigos
- Analisar métricas

### 3. Portfolio Pessoal
- Buscar publicações próprias
- Calcular h-index
- Exportar para CV

### 4. Análise Bibliométrica
- Grandes volumes de dados
- Métricas de impacto
- Tendências temporais

## Diferenciais

### vs Publish or Perish
- ✅ 100% Open Source
- ✅ Sem instalação complexa
- ✅ Interface web moderna
- ✅ Exportação para Tainacan

### vs APIs diretas
- ✅ Interface amigável
- ✅ Deduplicação automática
- ✅ Cálculo de métricas
- ✅ Mapeamento Dublin Core

## Roadmap Futuro

### Curto Prazo
- [ ] Barra de progresso visual
- [ ] Cache local de buscas
- [ ] Mais fontes de dados

### Médio Prazo
- [ ] Interface multilíngue
- [ ] Análises visuais
- [ ] API própria

### Longo Prazo
- [ ] Machine Learning
- [ ] Recomendações
- [ ] Colaboração

## Créditos

Desenvolvido como ferramenta acadêmica livre para facilitar:
- Gestão de repositórios
- Análises bibliométricas
- Importação no Tainacan
- Acesso a metadados

## Licença

Este projeto é software livre e pode ser modificado conforme necessidade.