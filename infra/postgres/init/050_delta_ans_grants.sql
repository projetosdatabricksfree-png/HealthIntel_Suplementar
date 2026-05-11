-- Sprint 41: Delta ANS 100% — Grants de acesso para roles de serviço
-- Aplica GRANT SELECT nas tabelas api_ans e consumo_ans novas do Sprint 41
-- Execute após dbt build --select tag:delta_ans_100

-- Produtos e Planos (Onda 1)
GRANT SELECT ON api_ans.api_produto_plano TO healthintel_api_user;
GRANT SELECT ON api_ans.api_historico_plano TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_produto_plano TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_produto_plano TO healthintel_premium_user;

-- TUSS Oficial (Onda 2)
GRANT SELECT ON api_ans.api_tuss_procedimento_vigente TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_tuss_procedimento_vigente TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_tuss_procedimento_vigente TO healthintel_premium_user;

-- TISS Subfamílias (Onda 3)
GRANT SELECT ON api_ans.api_tiss_ambulatorial_operadora_mes TO healthintel_api_user;
GRANT SELECT ON api_ans.api_tiss_hospitalar_operadora_mes TO healthintel_api_user;
GRANT SELECT ON api_ans.api_tiss_plano_mes TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_tiss_utilizacao_operadora_mes TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_tiss_utilizacao_operadora_mes TO healthintel_premium_user;

-- SIP (Onda 4)
GRANT SELECT ON api_ans.api_sip_assistencial_operadora TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_sip_assistencial_operadora TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_sip_assistencial_operadora TO healthintel_premium_user;

-- Ressarcimento SUS (Onda 5)
GRANT SELECT ON api_ans.api_ressarcimento_sus_operadora_plano TO healthintel_api_user;
GRANT SELECT ON api_ans.api_ressarcimento_beneficiario_abi TO healthintel_api_user;
GRANT SELECT ON api_ans.api_ressarcimento_hc TO healthintel_api_user;
GRANT SELECT ON api_ans.api_ressarcimento_cobranca_arrecadacao TO healthintel_api_user;
GRANT SELECT ON api_ans.api_ressarcimento_indice_pagamento TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_ressarcimento_sus_operadora TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_ressarcimento_sus_operadora TO healthintel_premium_user;

-- Precificação/NTRP (Onda 6)
GRANT SELECT ON api_ans.api_painel_precificacao TO healthintel_api_user;
GRANT SELECT ON api_ans.api_reajuste_agrupamento TO healthintel_api_user;
GRANT SELECT ON api_ans.api_ntrp_area_comercializacao TO healthintel_api_user;
GRANT SELECT ON api_ans.api_ntrp_vcm_faixa_etaria TO healthintel_api_user;
GRANT SELECT ON api_ans.api_valor_comercial_medio_municipio TO healthintel_api_user;
GRANT SELECT ON api_ans.api_faixa_preco TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_precificacao_plano TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_precificacao_plano TO healthintel_premium_user;

-- Rede/Prestadores (Onda 7)
GRANT SELECT ON api_ans.api_operadora_cancelada TO healthintel_api_user;
GRANT SELECT ON api_ans.api_operadora_acreditada TO healthintel_api_user;
GRANT SELECT ON api_ans.api_prestador_acreditado TO healthintel_api_user;
GRANT SELECT ON api_ans.api_produto_prestador_hospitalar TO healthintel_api_user;
GRANT SELECT ON api_ans.api_operadora_prestador_nao_hospitalar TO healthintel_api_user;
GRANT SELECT ON api_ans.api_alteracao_rede_hospitalar TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_rede_acreditacao TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_rede_acreditacao TO healthintel_premium_user;

-- Regulatórios Complementares (Onda 8)
GRANT SELECT ON api_ans.api_penalidade_operadora TO healthintel_api_user;
GRANT SELECT ON api_ans.api_garantia_atendimento TO healthintel_api_user;
GRANT SELECT ON api_ans.api_peona_sus TO healthintel_api_user;
GRANT SELECT ON api_ans.api_promoprev TO healthintel_api_user;
GRANT SELECT ON api_ans.api_rpc_operadora_mes TO healthintel_api_user;
GRANT SELECT ON api_ans.api_iap TO healthintel_api_user;
GRANT SELECT ON api_ans.api_pfa TO healthintel_api_user;
GRANT SELECT ON api_ans.api_programa_qualificacao_institucional TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_regulatorio_complementar_operadora TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_regulatorio_complementar_operadora TO healthintel_premium_user;

-- Beneficiários/Cobertura (Onda 9)
GRANT SELECT ON api_ans.api_beneficiario_regiao_geografica TO healthintel_api_user;
GRANT SELECT ON api_ans.api_beneficiario_informacao_consolidada TO healthintel_api_user;
GRANT SELECT ON api_ans.api_taxa_cobertura_plano TO healthintel_api_user;
GRANT SELECT ON consumo_ans.consumo_beneficiarios_cobertura_municipio TO healthintel_consumo_user;
GRANT SELECT ON consumo_ans.consumo_beneficiarios_cobertura_municipio TO healthintel_premium_user;
