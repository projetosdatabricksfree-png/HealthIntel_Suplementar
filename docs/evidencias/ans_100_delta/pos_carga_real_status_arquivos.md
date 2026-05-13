# Evidência — Status plataforma.arquivo_fonte_ans

**Timestamp:** 2026-05-13T11:28:52Z

**Commit:** 072c13c


## Status por família
```
     familia     |   status   | total_arquivos

-----------------+------------+----------------
 produtos_planos | carregado  |              5
 produtos_planos | erro_carga |              3
 sip             | carregado  |              1
 tuss            | carregado  |              1
(4 rows)

```

## Status geral
```
   status   | total_arquivos

------------+----------------
 carregado  |              7
 erro_carga |              3
(2 rows)

```

## Famílias delta ANS
```
     familia     | sucesso | erro | pendente | total

-----------------+---------+------+----------+-------
 produtos_planos |       5 |    3 |        0 |     8
 sip             |       1 |    0 |        0 |     1
 tuss            |       1 |    0 |        0 |     1
(3 rows)

```

## Todas as famílias distintas
```
     familia

-----------------
 produtos_planos
 sip
 tuss
(3 rows)

```

