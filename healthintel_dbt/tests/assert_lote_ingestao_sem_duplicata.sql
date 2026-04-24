select hash_arquivo, count(*) as total_sucesso
from plataforma.lote_ingestao
where status in ('sucesso', 'sucesso_com_alertas')
group by 1
having count(*) > 1
