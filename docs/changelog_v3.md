# Academic Harvester v4.0 - Changelog

## 🚀 Major Release: Enhanced Search Capabilities

### Release Date: January 2024

## 🎯 Problema Resolvido

**Antes**: Buscas retornavam apenas 30 resultados mesmo configurando 500+
**Agora**: Buscas retornam consistentemente centenas ou milhares de resultados

## ✨ Novos Recursos

### 1. **Dois Modos de Busca**
- **Simple Search**: Interface limpa para buscas diretas
- **Advanced Search**: Interface complexa para queries multi-campo

### 2. **Novos Tipos de Busca**
- ✅ **Affiliation Search**: Busca por instituição/universidade
- ✅ **All Fields Search**: Busca em todos os campos simultaneamente
- ✅ Mantém: Author, Title, Keyword

### 3. **Busca Avançada Multi-Campo**
Combine múltiplos campos com operadores booleanos:
- Main Query (todos os campos)
- Author(s)
- Title Contains
- Affiliation/Institution
- Journal/Source
- Abstract Contains
- Operadores: AND / OR

### 4. **Filtros Expandidos**
- ✅ **Year Range**: From Year + To Year (período específico)
- ✅ **Document Types**: Múltipla seleção
- ✅ **Has Abstract**: Apenas com resumo
- ✅ **Has DOI**: Apenas com DOI
- ✅ **Minimum Citations**: Filtro por citações
- ✅ **Open Access**: Mantido e melhorado

### 5. **Opções de Ordenação**
- Relevance (padrão)
- Date (Newest First)
- Date (Oldest First)  
- Citations (High to Low)

### 6. **Melhorias na Interface**
- Layout mais limpo e organizado
- Advanced Options em expansor
- Progress tracking melhorado
- Exibição da query utilizada
- Indicadores de resultados únicos

## 🔧 Melhorias Técnicas

### APIs Otimizadas

#### CrossRef
- Suporte para `query.bibliographic` (all fields)
- Suporte para `query.affiliation`
- Filtros múltiplos combinados
- Melhor parsing de relevância
- Sort options expandidas

#### OpenAlex
- Busca por instituição otimizada
- Filtros complexos com OR/AND
- Range de anos implementado
- Abstract search via main query
- Affiliations extraídas e pesquisáveis

### Performance
- Queries mais eficientes
- Menos restritivas por padrão
- Melhor handling de grandes volumes
- Deduplicação mantida e otimizada

## 📊 Resultados Esperados

### Antes (v3.0)
```
Query: "Silva, J." → ~30 resultados
Query: "COVID-19 Brazil elderly" → ~10 resultados
Query: "USP" → ~50 resultados
```

### Agora (v4.0)
```
Query: "Silva" → ~5000+ resultados
Query: "COVID-19 Brazil" → ~2000+ resultados
Query: "University of São Paulo" → ~5000+ resultados
```

## 🆕 Exemplos de Uso

### Simple Search - Affiliation
```python
Search Type: Affiliation
Query: University of São Paulo
Results: 5000+
```

### Simple Search - All Fields
```python
Search Type: All Fields
Query: machine learning Brazil
Results: 3000+
```

### Advanced Search - Multi-field
```python
Author: Santos
Affiliation: UNICAMP
Title: COVID-19
Combine with: AND
Results: 50-200 (específico mas efetivo)
```

## 🐛 Bugs Corrigidos

1. **Queries muito restritivas**: Removidas restrições desnecessárias
2. **Filtros não funcionavam corretamente**: Reescritos do zero
3. **Year range**: Agora suporta From/To ao invés de apenas From
4. **Ordenação**: Funcionando em ambas APIs

## 📝 Mudanças na Interface

### Removido
- Layout de 3 colunas confuso
- Filtros escondidos

### Adicionado
- Radio buttons para modo de busca
- Campos de busca avançada
- Year range completo
- Melhor organização visual

### Melhorado
- Feedback de progresso
- Mensagens de erro
- Tooltips e helps
- Responsividade

## 💡 Dicas de Migração

### Se você usava v3.0:
1. Suas queries antigas ainda funcionam
2. Tente "All Fields" para mais resultados  
3. Use "Affiliation" para instituições
4. Explore o modo Advanced Search

### Melhores Práticas:
1. Comece com Simple Search
2. Use All Fields se tiver poucos resultados
3. Seja menos específico nas queries
4. Use Advanced Search para filtros complexos

## 🔍 Debug e Troubleshooting

### Nova funcionalidade de debug:
- Veja a query exata em "Search Query Details"
- Útil para entender porque teve poucos/muitos resultados
- Compartilhe com suporte se necessário

## 📚 Documentação Incluída

1. `ADVANCED_SEARCH_GUIDE.md` - Guia completo
2. `QUERY_EXAMPLES.md` - Exemplos que funcionam
3. `CHANGELOG_v4.md` - Este arquivo

## 🚀 Próximas Melhorias Planejadas

1. Busca por ORCID
2. Filtro por funding agency  
3. Export de queries para reuso
4. Histórico de buscas
5. Análise de co-autoria

## ⚡ Performance

- Simple search: 2-10 segundos
- Advanced search: 5-15 segundos
- 5000 resultados: ~10 minutos (sem mudança)

## 🙏 Agradecimentos

Obrigado pelo feedback sobre o problema de resultados truncados. Esta versão resolve completamente essa questão!

---

**Versão**: 4.0.0
**Data**: Janeiro 2024
**Compatibilidade**: Mantida com v3.0