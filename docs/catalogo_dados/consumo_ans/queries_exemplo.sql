-- Exemplos de consumo SQL - consumo_ans

select *
from consumo_ans.consumo_produto_plano
where competencia = 202501;

select registro_ans, codigo_plano, situacao, competencia
from consumo_ans.consumo_historico_plano
where registro_ans = '123456';

select registro_ans, trimestre, nivel_alerta, taxa_resolutividade
from consumo_ans.consumo_regulatorio_operadora_trimestre
where trimestre >= '202501';

select registro_ans, ano_base, idss_total, faixa_idss
from consumo_ans.consumo_idss
where ano_base >= 2023;

select registro_ans, trimestre, receita_total, despesa_total, rating_financeiro
from consumo_ans.consumo_financeiro_operadora_trimestre
where trimestre >= '202501';

select registro_ans, competencia, tipo_glosa, taxa_glosa_calculada
from consumo_ans.consumo_glosa_operadora_mensal
where competencia = 202501;

select codigo_tuss, descricao, grupo, subgrupo
from consumo_ans.consumo_tuss_procedimento_vigente
where codigo_tuss = '10101012';

select registro_ans, trimestre, tipo_regime, ativo, data_inicio
from consumo_ans.consumo_regime_especial_operadora_trimestral
where ativo = true;

-- Tabelas parciais ou bloqueadas devem ser consultadas apenas com ciencia
-- das limitacoes registradas no catalogo comercial.
select registro_ans, competencia, score_total, componente_core
from consumo_ans.consumo_score_operadora_mes
limit 100;
