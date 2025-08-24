# Guia de Importação para o Tainacan

## Preparação dos Dados

### 1. Filtros Disponíveis
- **From Year**: Define o ano mínimo das publicações
- **Open Access Only**: Mostra apenas publicações de acesso aberto (recomendado para repositórios institucionais)

### 2. Estrutura da Planilha Excel

A planilha gerada está otimizada para importação no Tainacan com as seguintes características:

#### Aba "Importar_Tainacan"
Contém todos os metadados em colunas separadas:

**Campos Dublin Core (15 elementos padrão):**
- `dc:title` - Título do documento
- `dc:creator` - Autores (separados por ponto e vírgula)
- `dc:subject` - Assuntos/palavras-chave (separados por ponto e vírgula)
- `dc:description` - Resumo/abstract
- `dc:publisher` - Editora
- `dc:contributor` - Colaboradores (editores, financiadores, instituições)
- `dc:date` - Data de publicação completa
- `dc:type` - Tipo de documento (Text, Dataset, Software, etc.)
- `dc:format` - Formato (sempre "text" para publicações)
- `dc:identifier` - Identificadores (DOI, ISSN, ISBN)
- `dc:source` - Fonte/revista
- `dc:language` - Idioma
- `dc:relation` - Relações (volume, páginas, trabalhos relacionados)
- `dc:coverage` - Cobertura (países, período temporal)
- `dc:rights` - Direitos/licenças

**Campos Adicionais Importantes:**
- `doi` - DOI limpo
- `year` - Ano (numérico)
- `citations` - Número de citações
- `is_open_access` - Acesso aberto (Sim/Não)
- `open_access_url` - URL de acesso aberto
- `volume` - Volume
- `issue` - Número/edição
- `pages` - Páginas
- `issn` - ISSN
- `isbn` - ISBN
- `url` - URL principal
- `references_count` - Quantidade de referências
- `mesh_terms` - Termos MeSH (para publicações médicas)
- `sustainable_development_goals` - ODS relacionados

## Importação no Tainacan

### Passo 1: Preparar a Coleção
1. Crie uma nova coleção no Tainacan
2. Configure os metadados da coleção para corresponder aos campos da planilha

### Passo 2: Mapeamento de Metadados Recomendado

| Campo na Planilha | Tipo no Tainacan | Observações |
|-------------------|------------------|-------------|
| dc:title | Texto | Campo obrigatório |
| dc:creator | Texto | Múltiplos valores |
| dc:date | Data | Formato YYYY-MM-DD |
| dc:subject | Taxonomia | Criar vocabulário controlado |
| dc:description | Texto longo | Para abstracts |
| dc:identifier | Texto | Campo único |
| doi | Texto | Validador de DOI |
| is_open_access | Seleção | Opções: Sim/Não |
| citations | Numérico | Para ordenação |
| year | Numérico | Para filtros |

### Passo 3: Processo de Importação
1. No Tainacan, vá para sua coleção
2. Clique em "Importadores" → "CSV"
3. Faça upload do arquivo Excel (aba Importar_Tainacan)
4. Mapeie cada coluna para o metadado correspondente
5. Configure o identificador único (recomendado: dc:identifier ou doi)
6. Execute a importação

## Dicas Importantes

### Para Repositórios Institucionais
- Use sempre o filtro "Open Access Only"
- Priorize publicações com DOI válido
- Configure o campo `open_access_url` como link de acesso

### Para Bibliotecas Digitais
- Mantenha todos os metadados Dublin Core
- Use dc:subject para criar facetas de busca
- Configure dc:type para filtrar tipos de documento

### Validação de Dados
- Campos vazios são importados como strings vazias
- Booleanos são convertidos para "Sim/Não"
- Múltiplos valores são separados por ponto e vírgula
- Datas mantêm formato ISO quando disponível

### Filtros Recomendados no Tainacan
Após importação, configure filtros para:
- `year` (intervalo numérico)
- `is_open_access` (seleção)
- `dc:type` (checkbox)
- `dc:source` (busca textual)
- `citations` (intervalo numérico)

## Solução de Problemas

**Problema**: Caracteres especiais aparecem incorretos
**Solução**: A planilha usa UTF-8. Certifique-se que o Tainacan está configurado para UTF-8

**Problema**: Datas não são reconhecidas
**Solução**: Use o campo `year` (numérico) ao invés de `dc:date` se houver problemas

**Problema**: Autores não são separados corretamente
**Solução**: O campo dc:creator usa ponto e vírgula como separador

## Metadados Específicos por Fonte

### CrossRef
- Melhor para publicações tradicionais
- Inclui ISSN, ISBN, editores
- Não tem contagem de citações

### OpenAlex
- Inclui contagem real de citações
- Identifica publicações open access
- Fornece conceitos e instituições
- Inclui dados geográficos