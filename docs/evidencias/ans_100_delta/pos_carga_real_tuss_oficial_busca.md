# Evidência — TUSS Oficial

**Timestamp:** 2026-05-13T11:28:52Z

**Commit:** 072c13c


## Contagem TUSS vigente
```
 total_tuss_vigente

--------------------
              64654
(1 row)

```

## Duplicidade por codigo_tuss + versao_tuss
```
 codigo_tuss | versao_tuss | total

-------------+-------------+-------
(0 rows)

```

## Amostra por código
```
 codigo_tuss |                                                 descricao                                                  | versao_tuss | vigencia_inicio | vigencia_fim | is_tuss_vigente

-------------+------------------------------------------------------------------------------------------------------------+-------------+-----------------+--------------+-----------------
 0           | TRABALHO                                                                                                   | 202505      | 2006-08-14      |              | t
 1           | AMBULATORIAL                                                                                               | 202505      | 2021-08-01      |              | t
 10          | DRG                                                                                                        | 202505      | 2012-10-10      |              | t
 100095712   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE                                                      | 202505      | 2021-03-01      |              | t
 100095720   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOM856 INSERTO T56 CERALEPINE 12/14, COLO M¨¦DIO | 202505      | 2021-03-01      |              | t
 100095739   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOC854 INSERTOT54 CERALEPINE 12/14, COLO CURTO   | 202505      | 2021-03-01      |              | t
 100095747   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOC848 INSERTO T48 CERALEPINE 12/14, COLO CURTO  | 202505      | 2021-03-01      |              | t
 100095755   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOC862 INSERTO T62 CERALEPINE 12/14, COLO CURTO  | 202505      | 2021-03-01      |              | t
 100095763   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOC858 INSERTO T58 CERALEPINE 12/14, COLO CURTO  | 202505      | 2021-03-01      |              | t
 100095771   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOL848 INSERTO T48 CERALEPINE 12/14, COLO LONGO  | 202505      | 2021-03-01      |              | t
 100095780   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOC856 INSERTO T56 CERALEPINE 12/14, COLO CURTO  | 202505      | 2021-03-01      |              | t
 100095798   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOL862 INSERTO T62 CERALEPINE 12/14, COLO LONGO  | 202505      | 2021-03-01      |              | t
 100095801   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOL852 INSERTO T52 CERALEPINE 12/14, COLO LONGO  | 202505      | 2021-03-01      |              | t
 100095810   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOC860 INSERTO T60 CERALEPINE12/14, COLO CURTO   | 202505      | 2021-03-01      |              | t
 100095828   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOL860 INSERTO T60CERALEPINE 12/14, COLO LONGO   | 202505      | 2021-03-01      |              | t
 100095836   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOM858 INSERTO T58 CERALEPINE 12/14,COLO M¨¦DIO  | 202505      | 2021-03-01      |              | t
 100095844   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOC850 INSERTO T50 CERALEPINE 12/14,COLO CURTO   | 202505      | 2021-03-01      |              | t
 100095852   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOM854 INSERTO T54 CERALEPINE 12/14, COLO M¨¦DIO | 202505      | 2021-03-01      |              | t
 100095860   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOM852 INSERTO T52CERALEPINE 12/14, COLO M¨¦DIO  | 202505      | 2021-03-01      |              | t
 100095879   | FAMÍLIA INSERTO MOBILIDADE DUPLA CABEÇA DE CERALEPINE - HQNOM862 INSERTOT62 CERALEPINE 12/14, COLO M¨¦DIO  | 202505      | 2021-03-01      |              | t
(20 rows)

```

## Busca por descrição (consulta)
```
 codigo_tuss |                               descricao                               | versao_tuss | is_tuss_vigente

-------------+-----------------------------------------------------------------------+-------------+-----------------
 10101012    | CONSULTA EM CONSULTÓRIO (NO HORÁRIO NORMAL OU PREESTABELECIDO)        | 202505      | t
 10101020    | CONSULTA EM DOMICÍLIO                                                 | 202505      | t
 10101039    | CONSULTA EM PRONTO SOCORRO                                            | 202505      | t
 20101074    | AVALIAÇÃO NUTROLÓGICA (INCLUI CONSULTA)                               | 202505      | t
 20101082    | AVALIAÇÃO NUTROLÓGICA PRÉ E PÓS-CIRURGIA BARIÁTRICA (INCLUI CONSULTA) | 202505      | t
 20101090    | AVALIAÇÃO DA COMPOSIÇÃO CORPORAL POR ANTROPOMETRIA (INCLUI CONSULTA)  | 202505      | t
 4           | CONSULTA                                                              | 202505      | t
 50000055    | CONSULTA INDIVIDUAL AMBULATORIAL, EM TERAPIA OCUPACIONAL              | 202505      | t
 50000063    | CONSULTA INDIVIDUAL DOMICILIAR, EM TERAPIA OCUPACIONAL                | 202505      | t
 50000071    | CONSULTA INDIVIDUAL HOSPITALAR, EM TERAPIA OCUPACIONAL                | 202505      | t
 50000144    | CONSULTA AMBULATORIAL EM FISIOTERAPIA                                 | 202505      | t
 50000241    | CONSULTA DOMICILIAR EM FISIOTERAPIA                                   | 202505      | t
 50000349    | CONSULTA HOSPITALAR EM FISIOTERAPIA                                   | 202505      | t
 50000527    | CONSULTA HOSPITALAR DE ENFERMAGEM                                     | 202505      | t
 50000535    | CONSULTA DOMICILIAR DE ENFERMAGEM                                     | 202505      | t
 50000560    | CONSULTA AMBULATORIAL POR NUTRICIONISTA                               | 202505      | t
 50000578    | CONSULTA DOMICILIAR POR NUTRICIONISTA                                 | 202505      | t
 50000586    | CONSULTA INDIVIDUAL AMBULATORIAL DE FONOAUDIOLOGIA                    | 202505      | t
 50000594    | CONSULTA INDIVIDUAL DOMICILIAR DE FONOAUDIOLOGIA                      | 202505      | t
 50000608    | CONSULTA INDIVIDUAL HOSPITALAR DE FONOAUDIOLOGIA                      | 202505      | t
(20 rows)

```

## Contagem TUSS consumo
```
 total_tuss_consumo

--------------------
              64654
(1 row)

```

