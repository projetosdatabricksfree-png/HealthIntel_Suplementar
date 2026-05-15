# Dicionario de dados - consumo_ans

Este documento e o dicionario comercial da camada `consumo_ans`. O catalogo
oficial de status fica em `catalogo_consumo_ans.yml`; tabelas `parcial`,
`vazia_bloqueada` ou `fora_do_escopo` nao devem ser vendidas como cobertura
completa.

## consumo_produto_plano

- Descricao: produtos e planos ANS por operadora.
- Fonte ANS: PDA caracteristicas de produtos e historico de planos.
- Periodicidade: mensal.
- Granularidade: `registro_ans + codigo_produto + competencia`.
- Chave: `registro_ans`, `codigo_produto`, `competencia`.
- Principais colunas: `nome_produto`, `segmentacao`, `tipo_contratacao`, `abrangencia_geografica`, `situacao_plano`.
- Datas/competencia: `competencia`, `data_situacao`.
- Limitacoes: depende da disponibilidade dos arquivos PDA oficiais.
- Exemplo SQL: `select * from consumo_ans.consumo_produto_plano where competencia = 202501;`

## consumo_historico_plano

- Descricao: historico de situacao dos planos por operadora.
- Fonte ANS: PDA historico de planos.
- Periodicidade: mensal.
- Granularidade: `registro_ans + codigo_plano + competencia`.
- Chave: `registro_ans`, `codigo_plano`, `competencia`.
- Principais colunas: `nome_plano`, `situacao`, `segmentacao`, `tipo_contratacao`, `uf`.
- Datas/competencia: `competencia`, `data_situacao`.
- Limitacoes: reflete o layout publicado pela ANS no arquivo carregado.
- Exemplo SQL: `select * from consumo_ans.consumo_historico_plano where registro_ans = '123456';`

## consumo_regulatorio_operadora_trimestre

- Descricao: visao regulatoria trimestral consolidada por operadora.
- Fonte ANS: NIP, IGR e taxa de resolutividade.
- Periodicidade: trimestral.
- Granularidade: `registro_ans + trimestre`.
- Chave: `registro_ans`, `trimestre`.
- Principais colunas: `qtd_reclamacoes`, `indice_reclamacao`, `demandas_nip`, `taxa_resolutividade`, `nivel_alerta`.
- Datas/competencia: `trimestre`.
- Limitacoes: consolida apenas fontes regulatorias oficiais carregadas.
- Exemplo SQL: `select * from consumo_ans.consumo_regulatorio_operadora_trimestre where trimestre = '202501';`

## consumo_igr

- Descricao: Indice de Garantia de Resolutividade por operadora.
- Fonte ANS: PDA IGR.
- Periodicidade: trimestral.
- Granularidade: `registro_ans + trimestre`.
- Chave: `registro_ans`, `trimestre`.
- Principais colunas: `total_reclamacoes`, `beneficiarios`, `igr`, `meta_igr`, `atingiu_meta`.
- Datas/competencia: `trimestre`.
- Limitacoes: campo `beneficiarios` segue a publicacao da fonte IGR, nao fecha SIB.
- Exemplo SQL: `select * from consumo_ans.consumo_igr where atingiu_meta = false;`

## consumo_nip

- Descricao: demandas NIP e resolutividade por operadora.
- Fonte ANS: PDA NIP.
- Periodicidade: trimestral.
- Granularidade: `registro_ans + trimestre`.
- Chave: `registro_ans`, `trimestre`.
- Principais colunas: `demandas_nip`, `demandas_resolvidas`, `taxa_intermediacao_resolvida`, `taxa_resolutividade`.
- Datas/competencia: `trimestre`.
- Limitacoes: nao substitui detalhe TISS nem SIB.
- Exemplo SQL: `select registro_ans, trimestre, demandas_nip from consumo_ans.consumo_nip;`

## consumo_idss

- Descricao: IDSS e componentes por operadora.
- Fonte ANS: PDA IDSS.
- Periodicidade: anual.
- Granularidade: `registro_ans + ano_base`.
- Chave: `registro_ans`, `ano_base`.
- Principais colunas: `idss_total`, `idqs`, `idga`, `idsm`, `idgr`, `faixa_idss`.
- Datas/competencia: `ano_base`.
- Limitacoes: defasagem natural da divulgacao anual da ANS.
- Exemplo SQL: `select * from consumo_ans.consumo_idss where ano_base >= 2023;`

## consumo_taxa_resolutividade_operadora_trimestral

- Descricao: taxa de resolutividade trimestral por operadora.
- Fonte ANS: PDA taxa de resolutividade.
- Periodicidade: trimestral.
- Granularidade: `registro_ans + trimestre`.
- Chave: `registro_ans`, `trimestre`.
- Principais colunas: `modalidade`, `taxa_resolutividade`, `n_reclamacao_resolvida`, `n_reclamacao_total`.
- Datas/competencia: `trimestre`.
- Limitacoes: depende da publicacao trimestral oficial.
- Exemplo SQL: `select * from consumo_ans.consumo_taxa_resolutividade_operadora_trimestral;`

## consumo_prudencial_operadora_trimestral

- Descricao: indicadores prudenciais por operadora.
- Fonte ANS: PDA indicadores prudenciais.
- Periodicidade: trimestral.
- Granularidade: `registro_ans + trimestre`.
- Chave: `registro_ans`, `trimestre`.
- Principais colunas: `margem_solvencia`, `capital_minimo_requerido`, `capital_disponivel`, `indice_liquidez`.
- Datas/competencia: `trimestre`.
- Limitacoes: nao altera regra contabil da fonte ANS.
- Exemplo SQL: `select * from consumo_ans.consumo_prudencial_operadora_trimestral where situacao_inadequada = true;`

## consumo_financeiro_operadora_trimestre

- Descricao: demonstracoes e indicadores financeiros trimestrais.
- Fonte ANS: DIOPS/FIP.
- Periodicidade: trimestral.
- Granularidade: `registro_ans + trimestre`.
- Chave: `registro_ans`, `trimestre`.
- Principais colunas: `receita_total`, `despesa_total`, `resultado_periodo`, `sinistralidade_liquida`, `rating_financeiro`.
- Datas/competencia: `trimestre`.
- Limitacoes: depende da conciliacao de DIOPS/FIP carregada no nucleo.
- Exemplo SQL: `select registro_ans, trimestre, receita_total from consumo_ans.consumo_financeiro_operadora_trimestre;`

## consumo_glosa_operadora_mensal

- Descricao: glosa mensal por operadora e tipo.
- Fonte ANS: PDA glosa.
- Periodicidade: mensal.
- Granularidade: `registro_ans + competencia + tipo_glosa`.
- Chave: `registro_ans`, `competencia`, `tipo_glosa`.
- Principais colunas: `qt_glosa`, `valor_glosa`, `valor_faturado`, `taxa_glosa_calculada`.
- Datas/competencia: `competencia`.
- Limitacoes: nao inclui TISS detalhado.
- Exemplo SQL: `select * from consumo_ans.consumo_glosa_operadora_mensal where competencia = 202501;`

## consumo_tuss_procedimento_vigente

- Descricao: terminologia TUSS oficial vigente.
- Fonte ANS: TUSS oficial.
- Periodicidade: versao vigente.
- Granularidade: `codigo_tuss`.
- Chave: `codigo_tuss`.
- Principais colunas: `descricao`, `versao_tuss`, `vigencia_inicio`, `grupo`, `subgrupo`.
- Datas/competencia: `versao_tuss`, `vigencia_inicio`.
- Limitacoes: TUSS nao e TISS; esta tabela permanece no escopo.
- Exemplo SQL: `select * from consumo_ans.consumo_tuss_procedimento_vigente where codigo_tuss = '10101012';`

## consumo_regime_especial_operadora_trimestral

- Descricao: regime especial fiscal/tecnico por operadora.
- Fonte ANS: PDA regime especial.
- Periodicidade: trimestral.
- Granularidade: `registro_ans + trimestre + tipo_regime`.
- Chave: `registro_ans`, `trimestre`, `tipo_regime`.
- Principais colunas: `ativo`, `data_inicio`, `data_fim`, `descricao`.
- Datas/competencia: `trimestre`, `data_inicio`, `data_fim`.
- Limitacoes: reflete eventos publicados pela ANS.
- Exemplo SQL: `select * from consumo_ans.consumo_regime_especial_operadora_trimestral where ativo = true;`

## consumo_rede_assistencial_municipio

- Descricao: rede assistencial por municipio e operadora.
- Fonte ANS: rede assistencial; DataSUS CNES para complementos.
- Periodicidade: mensal.
- Granularidade: `registro_ans + cd_municipio + competencia + segmento`.
- Chave: `registro_ans`, `cd_municipio`, `competencia`, `segmento`.
- Principais colunas: `qt_prestadores`, `densidade_por_10k`, `gap_leitos_cnes`, `classificacao_vazio`.
- Datas/competencia: `competencia`.
- Limitacoes: vazia_bloqueada; tabela zerada e componente CNES bloqueado enquanto a fonte DataSUS configurada retornar 404.
- Exemplo SQL: `select * from consumo_ans.consumo_rede_assistencial_municipio where uf = 'SP';`

## consumo_sip_assistencial_operadora

- Descricao: mapa assistencial SIP por operadora e municipio.
- Fonte ANS: PDA SIP mapa assistencial.
- Periodicidade: mensal.
- Granularidade: `registro_ans + cd_municipio + competencia + tipo_assistencial`.
- Chave: `registro_ans`, `cd_municipio`, `competencia`, `tipo_assistencial`.
- Principais colunas: `qt_beneficiarios`, `qt_eventos`, `indicador_cobertura_medio`.
- Datas/competencia: `competencia`.
- Limitacoes: vazia_bloqueada na validacao real; nao publicar ate a carga SIP produzir linhas em consumo_ans.
- Exemplo SQL: `select * from consumo_ans.consumo_sip_assistencial_operadora where competencia = 202501;`

## consumo_precificacao_plano

- Descricao: precificacao/NTRP por plano, faixa etaria e UF.
- Fonte ANS: painel de precificacao/NTRP.
- Periodicidade: mensal.
- Granularidade: `registro_ans + codigo_plano + competencia + faixa_etaria + sg_uf`.
- Chave: `registro_ans`, `codigo_plano`, `competencia`, `faixa_etaria`, `sg_uf`.
- Principais colunas: `vl_mensalidade_media`, `vl_mensalidade_min`, `vl_mensalidade_max`, `qt_beneficiarios`.
- Datas/competencia: `competencia`.
- Limitacoes: vazia_bloqueada na validacao real; nao publicar ate a carga NTRP produzir linhas em consumo_ans.
- Exemplo SQL: `select * from consumo_ans.consumo_precificacao_plano where sg_uf = 'SP';`

## consumo_ressarcimento_sus_operadora

- Descricao: ressarcimento ao SUS agregado por operadora.
- Fonte ANS: ressarcimento ao SUS.
- Periodicidade: mensal.
- Granularidade: `registro_ans + competencia`.
- Chave: `registro_ans`, `competencia`.
- Principais colunas: `qt_autorizacoes_total`, `vl_cobrado_total`, `vl_pago_total`, `vl_pendente_total`.
- Datas/competencia: `competencia`.
- Limitacoes: vazia_bloqueada na validacao real; nao publicar ate a carga de ressarcimento produzir linhas em consumo_ans.
- Exemplo SQL: `select * from consumo_ans.consumo_ressarcimento_sus_operadora where vl_pendente_total > 0;`

## consumo_beneficiarios_operadora_mes

- Descricao: beneficiarios por operadora e mes.
- Fonte ANS: SIB beneficiarios por operadora.
- Periodicidade: mensal.
- Granularidade: `registro_ans + competencia`.
- Chave: `registro_ans`, `competencia`.
- Principais colunas: `qt_beneficiarios`, `qt_beneficiario_medico`, `qt_beneficiario_odonto`.
- Datas/competencia: `competencia`.
- Limitacoes: parcial; SIB esta fora do escopo de conclusao desta sprint e nao deve ser vendido como completo.
- Exemplo SQL: `select * from consumo_ans.consumo_beneficiarios_operadora_mes limit 100;`

## consumo_beneficiarios_municipio_mes

- Descricao: beneficiarios e mercado por municipio.
- Fonte ANS: SIB beneficiarios por municipio.
- Periodicidade: mensal.
- Granularidade: `cd_municipio + competencia`.
- Chave: `cd_municipio`, `competencia`.
- Principais colunas: `qt_beneficiarios`, `qt_operadoras`, `hhi`, `score_oportunidade`.
- Datas/competencia: `competencia`.
- Limitacoes: parcial; depende de SIB, fora do escopo desta sprint.
- Exemplo SQL: `select * from consumo_ans.consumo_beneficiarios_municipio_mes limit 100;`

## consumo_oportunidade_municipio

- Descricao: oportunidade territorial por municipio.
- Fonte ANS: SIB + referencias IBGE.
- Periodicidade: mensal.
- Granularidade: `cd_municipio + competencia`.
- Chave: `cd_municipio`, `competencia`.
- Principais colunas: `qt_beneficiarios`, `hhi`, `score_oportunidade`, `operadora_dominante`.
- Datas/competencia: `competencia`.
- Limitacoes: parcial; metricas de beneficiarios dependem de SIB.
- Exemplo SQL: `select * from consumo_ans.consumo_oportunidade_municipio order by score_oportunidade desc;`

## consumo_operadora_360

- Descricao: visao consolidada da operadora por competencia.
- Fonte ANS: CADOP, regulatorio, financeiro, rede e SIB.
- Periodicidade: mensal.
- Granularidade: `registro_ans + competencia`.
- Chave: `registro_ans`, `competencia`.
- Principais colunas: `qt_beneficiarios`, `score_total`, `componente_regulatorio`, `componente_financeiro`, `componente_rede`.
- Datas/competencia: `competencia`.
- Limitacoes: parcial; colunas de beneficiarios e score core dependem de SIB.
- Exemplo SQL: `select * from consumo_ans.consumo_operadora_360 where registro_ans = '123456';`

## consumo_score_operadora_mes

- Descricao: score mensal por operadora.
- Fonte ANS: regulatorio, financeiro, rede e SIB.
- Periodicidade: mensal.
- Granularidade: `registro_ans + competencia`.
- Chave: `registro_ans`, `competencia`.
- Principais colunas: `score_total`, `faixa_score`, `componente_core`, `componente_regulatorio`, `componente_financeiro`.
- Datas/competencia: `competencia`.
- Limitacoes: parcial; componente core depende de SIB.
- Exemplo SQL: `select * from consumo_ans.consumo_score_operadora_mes order by score_total desc;`

## consumo_beneficiarios_cobertura_municipio

- Descricao: cobertura de beneficiarios por municipio.
- Fonte ANS: taxa de cobertura plano e SIB.
- Periodicidade: mensal.
- Granularidade: `cd_municipio + competencia + sg_uf`.
- Chave: `cd_municipio`, `competencia`, `sg_uf`.
- Principais colunas: `populacao_total`, `qt_beneficiarios`, `taxa_cobertura`.
- Datas/competencia: `competencia`.
- Limitacoes: vazia_bloqueada; tabela zerada e cobertura depende de SIB.
- Exemplo SQL: `select * from consumo_ans.consumo_beneficiarios_cobertura_municipio limit 100;`

## consumo_tiss_utilizacao_operadora_mes

- Descricao: utilizacao TISS por operadora.
- Fonte ANS: TISS subfamilias.
- Periodicidade: mensal.
- Granularidade: `registro_ans + competencia + tipo_tiss + sg_uf`.
- Chave: `registro_ans`, `competencia`, `tipo_tiss`, `sg_uf`.
- Principais colunas: `qt_eventos`, `vl_pago`, `vl_informado`, `qt_internacoes`.
- Datas/competencia: `competencia`.
- Limitacoes: fora do escopo desta sprint; nao publicar como completo.
- Exemplo SQL: nao aplicavel ao catalogo comercial desta sprint.

## consumo_plano_servico_opcional

- Descricao: servicos opcionais por plano.
- Fonte ANS: servicos opcionais de planos.
- Periodicidade: mensal.
- Granularidade: `registro_ans + codigo_plano + codigo_servico`.
- Chave: `registro_ans`, `codigo_plano`, `codigo_servico`.
- Principais colunas: `descricao_servico`, `tipo_servico`, `competencia`.
- Datas/competencia: `competencia`.
- Limitacoes: vazia_bloqueada ate confirmar carga real nao vazia.
- Exemplo SQL: nao publicar ate liberacao comercial.

## consumo_rede_acreditacao

- Descricao: operadoras e prestadores acreditados.
- Fonte ANS: operadora/prestador acreditado.
- Periodicidade: snapshot.
- Granularidade: `tipo_acreditado + registro_ans/cnes`.
- Chave: `tipo_acreditado`, `registro_ans`, `cnes`.
- Principais colunas: `acreditadora`, `nivel_acreditacao`, `data_acreditacao`, `data_validade`.
- Datas/competencia: datas de acreditacao e validade.
- Limitacoes: vazia_bloqueada ate confirmar carga real nao vazia.
- Exemplo SQL: nao publicar ate liberacao comercial.

## consumo_regulatorio_complementar_operadora

- Descricao: indicadores IAP/PFA por operadora.
- Fonte ANS: IAP/PFA.
- Periodicidade: mensal.
- Granularidade: `registro_ans + competencia + tipo_indicador`.
- Chave: `registro_ans`, `competencia`, `tipo_indicador`.
- Principais colunas: `categoria`, `indicador`, `valor_indicador`, `score`.
- Datas/competencia: `competencia`.
- Limitacoes: vazia_bloqueada ate confirmar carga real nao vazia.
- Exemplo SQL: nao publicar ate liberacao comercial.
