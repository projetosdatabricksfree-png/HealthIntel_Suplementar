# Análise de Viabilidade - Reajuste Coletivo

O dataset de reajuste coletivo não tem, no momento, uma publicação estruturada consistente para ingestão automatizada com o mesmo padrão dos demais datasets ANS.

## Conclusão

- Publicação estruturada em CSV não foi confirmada como fonte regular.
- A disponibilidade tende a depender de páginas HTML, PDFs ou tabelas soltas no portal público.
- Isso impede a criação segura de um DAG de ingestão determinístico sem parser específico e validação humana.

## Decisão

- Manter o dataset como item documentado e reavaliar quando houver fonte estruturada.
- Não introduzir DAG nem staging automático até haver contrato físico estável.

