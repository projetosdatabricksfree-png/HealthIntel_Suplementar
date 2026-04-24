# Guia consumo_ans

`consumo_ans` e a camada de entrega final para clientes com acesso PostgreSQL direto. O HealthIntel entrega dados curados; o cliente escolhe a ferramenta de consumo.

## Acesso

- Schema: `consumo_ans`
- Role de grupo: `healthintel_cliente_reader`
- Permissao: read-only em `consumo_ans`
- Sem acesso a `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans` e `plataforma`

Usuarios `LOGIN` por cliente devem ser provisionados fora do DDL base, usando processo administrativo com segredo fora do repositorio.
