# Metodologia Score v3

O Score v3 é o índice composto final da plataforma. Ele consolida o score da operadora em cinco dimensões com fallback para o score v2 normalizado quando um componente ainda não está disponível.

## Pesos

| Componente | Peso | Origem principal |
| --- | --- | --- |
| Core | 0,25 | SIB e crescimento de beneficiários |
| Regulatório | 0,25 | IGR, NIP, RN 623 e prudencial |
| Financeiro | 0,20 | DIOPS, FIP, VDA e glosa |
| Rede | 0,20 | Cobertura assistencial e vazios territoriais |
| Estrutural | 0,10 | CNES e cruzamentos estruturais |

## Fórmula

`score_v3_final = soma(componente_normalizado_i * peso_i)`

Quando um componente ainda não está plenamente disponível, a implementação usa `score_v2_normalizado` como fallback técnico para manter continuidade histórica. O indicador `score_completo` permanece `false` enquanto qualquer componente depende de estimativa.

## Fontes e camadas

- A base core vem de fatos operacionais da operadora.
- A base regulatória agrega os fatos regulatórios já modelados.
- A base financeira usa os fatos financeiros e a harmonização mensal/trimestral.
- A base de rede usa cobertura e vazio assistencial.
- A base estrutural será reforçada com CNES e TISS conforme a maturidade da fase 2.

## Versão

- `versao_metodologia = 'v3.0'`
- O ranking composto usa a mesma versão metodológica.

