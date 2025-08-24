# Academic Harvester 📚

Ferramenta leve para busca e análise de publicações acadêmicas, com exportação otimizada para o Tainacan.

## 🚀 Início Rápido

1. **Instale Python 3.10+** do [python.org](https://python.org)
2. **Extraia** os arquivos do projeto
3. **Execute** `iniciar.bat`
4. **Acesse** http://localhost:8501

## ✨ Características

- **Busca até 5000 publicações** por consulta
- **Duas fontes de dados**: CrossRef e OpenAlex
- **Deduplicação automática** - sem resultados repetidos
- **Filtros avançados**: ano, open access
- **Métricas bibliométricas**: h-index, g-index
- **Exportação para Tainacan** com Dublin Core

## 📖 Como Usar

1. Escolha o tipo de busca (Autor/Título/Palavra-chave)
2. Digite o termo de busca
3. Configure os filtros:
   - **From Year**: ano mínimo
   - **Open Access Only**: apenas acesso aberto
   - **Maximum Results**: até 5000
4. Clique em **Search**
5. Exporte para Excel

## 🔧 Configuração Avançada

### Grandes Volumes (1000+ resultados)
- Use **OpenAlex** (mais rápido)
- Seja específico nos termos
- Aguarde pacientemente (10 min para 5000)

### Para Tainacan
- Use a aba **"Importar_Tainacan"**
- Mapeie as colunas conforme o guia
- Configure DOI como identificador único

## 📊 Métricas Calculadas

- **Total de publicações**
- **Total de citações** 
- **Média de citações por artigo**
- **h-index**: impacto do pesquisador
- **g-index**: produtividade vs impacto

## 📁 Estrutura

```
academic_harvester/
├── app.py              # Interface principal
├── iniciar.bat         # Iniciar no Windows
├── requirements.txt    # Dependências
├── apis/              # Conectores CrossRef/OpenAlex
├── logic/             # Métricas e Dublin Core
└── data/resultados/   # Arquivos Excel
```

## 🛠️ Requisitos

- Windows 10 ou superior
- Python 3.10+
- 4GB RAM (8GB para 5000 resultados)
- Conexão internet estável

## 📚 Documentação Completa

- [Instruções de Instalação](instrucoes.txt)
- [Guia de Importação Tainacan](TAINACAN_IMPORT_GUIDE.md)
- [Guia para Grandes Buscas](LARGE_SCALE_SEARCH_GUIDE.md)
- [Changelog v3](CHANGELOG_v3.md)

## 🤝 Contribuindo

Projeto open source - contribuições são bem-vindas!

## 📝 Licença

Software livre para uso acadêmico.

---

**Desenvolvido para facilitar a gestão de repositórios acadêmicos e análises bibliométricas.**
