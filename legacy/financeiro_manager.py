# financeiro_manager.py
# Gerenciamento financeiro completo compatível com db_schema.py atualizado

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from db_schema import get_connection

class FinanceiroManager:
    def __init__(self):
        pass
    
    def criar_orcamento(self,
                        cliente_id: int,
                        descricao: str,
                        recomendacao_id: Optional[int] = None,
                        talhao_id: Optional[int] = None,
                        custo_insumos: float = 0.0,
                        custo_mao_obra: float = 0.0,
                        custo_equipamentos: float = 0.0,
                        custo_transporte: float = 0.0,
                        custo_administrativo: float = 0.0,
                        desconto_percentual: float = 0.0,
                        comissao_equipe_id: Optional[int] = None,
                        responsavel_tecnico_id: Optional[int] = None) -> Tuple[bool, str, Optional[int]]:
        
        try:
            valor_bruto = custo_insumos + custo_mao_obra + custo_equipamentos + custo_transporte + custo_administrativo
            desconto = valor_bruto * (desconto_percentual / 100.0)
            valor_total = valor_bruto - desconto
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO financeiro_orcamentos (
                    cliente_id, recomendacao_id, talhao_id, descricao,
                    custo_insumos, custo_mao_obra, custo_equipamentos, custo_transporte, custo_administrativo,
                    desconto_percentual, valor_total, status, data_validade,
                    comissao_equipe_id, responsavel_tecnico_id
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                cliente_id, recomendacao_id, talhao_id, descricao.strip(),
                float(custo_insumos), float(custo_mao_obra), float(custo_equipamentos),
                float(custo_transporte), float(custo_administrativo),
                float(desconto_percentual), float(valor_total), 'rascunho',
                (datetime.now() + timedelta(days=30)).isoformat(),
                comissao_equipe_id, responsavel_tecnico_id
            ))
            
            orcamento_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True, f"Orçamento #{orcamento_id} criado. Valor: R$ {valor_total:.2f}", orcamento_id
            
        except Exception as e:
            return False, f"Erro ao criar orçamento: {str(e)}", None
    
    def buscar_orcamento(self, orcamento_id: int) -> Optional[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM financeiro_orcamentos WHERE id = ?', (orcamento_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return dict(row)
    
    def listar_orcamentos(self, cliente_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM financeiro_orcamentos WHERE 1=1'
        params = []
        
        if cliente_id:
            query += ' AND cliente_id = ?'
            params.append(cliente_id)
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY data_emissao DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def aprovar_orcamento(self, orcamento_id: int) -> Tuple[bool, str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM financeiro_orcamentos WHERE id = ?', (orcamento_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, f"Orçamento #{orcamento_id} não encontrado."
        
        cursor.execute('''
            UPDATE financeiro_orcamentos 
            SET status = 'aprovado', data_aprovacao = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), orcamento_id))
        conn.commit()
        conn.close()
        return True, f"Orçamento #{orcamento_id} aprovado."
    
    def rejeitar_orcamento(self, orcamento_id: int) -> Tuple[bool, str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE financeiro_orcamentos SET status = ? WHERE id = ?', ('rejeitado', orcamento_id))
        conn.commit()
        conn.close()
        return True, f"Orçamento #{orcamento_id} rejeitado."
    
    def faturar_orcamento(self,
                          orcamento_id: int,
                          numero_nota: str = "",
                          serie_nota: str = "",
                          metodo_pagamento: str = "",
                          observacoes: str = "") -> Tuple[bool, str, Optional[int]]:
        
        orc = self.buscar_orcamento(orcamento_id)
        if not orc:
            return False, f"Orçamento #{orcamento_id} não encontrado.", None
        
        try:
            valor_bruto = orc['valor_total']
            impostos = valor_bruto * 0.15
            valor_liquido = valor_bruto - impostos
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO financeiro_faturamento (
                    orcamento_id, cliente_id, numero_nota, serie_nota,
                    valor_bruto, valor_liquido, impostos_retidos,
                    status_pagamento, metodo_pagamento, observacoes
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
            ''', (
                orcamento_id, orc['cliente_id'], numero_nota.strip(), serie_nota.strip(),
                float(valor_bruto), float(valor_liquido), float(impostos),
                'pendente', metodo_pagamento.strip(), observacoes.strip()
            ))
            
            faturamento_id = cursor.lastrowid
            
            cursor.execute('''
                UPDATE financeiro_orcamentos SET status = 'faturado' WHERE id = ?
            ''', (orcamento_id,))
            
            conn.commit()
            conn.close()
            return True, f"Faturamento #{faturamento_id} criado. Valor Líquido: R$ {valor_liquido:.2f}", faturamento_id
            
        except Exception as e:
            return False, f"Erro ao faturar: {str(e)}", None
    
    def buscar_faturamento(self, faturamento_id: int) -> Optional[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM financeiro_faturamento WHERE id = ?', (faturamento_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return dict(row)
    
    def listar_faturamentos(self, cliente_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM financeiro_faturamento WHERE 1=1'
        params = []
        
        if cliente_id:
            query += ' AND cliente_id = ?'
            params.append(cliente_id)
        if status:
            query += ' AND status_pagamento = ?'
            params.append(status)
        
        query += ' ORDER BY data_faturamento DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def marcar_pago(self, faturamento_id: int, data_pagamento: Optional[str] = None) -> Tuple[bool, str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM financeiro_faturamento WHERE id = ?', (faturamento_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, f"Faturamento #{faturamento_id} não encontrado."
        
        dp = data_pagamento or datetime.now().isoformat()
        cursor.execute('''
            UPDATE financeiro_faturamento 
            SET status_pagamento = 'pago', data_pagamento = ?
            WHERE id = ?
        ''', (dp, faturamento_id))
        conn.commit()
        conn.close()
        return True, f"Faturamento #{faturamento_id} marcado como pago."
    
    def marcar_parcial(self, faturamento_id: int, valor_pago: float) -> Tuple[bool, str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM financeiro_faturamento WHERE id = ?', (faturamento_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, f"Faturamento #{faturamento_id} não encontrado."
        
        cursor.execute('''
            UPDATE financeiro_faturamento 
            SET status_pagamento = 'parcial'
            WHERE id = ?
        ''', (faturamento_id,))
        conn.commit()
        conn.close()
        return True, f"Faturamento #{faturamento_id} marcado como pagamento parcial (R$ {valor_pago:.2f})."
    
    def cancelar_faturamento(self, faturamento_id: int) -> Tuple[bool, str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE financeiro_faturamento SET status_pagamento = 'cancelado' WHERE id = ?
        ''', (faturamento_id,))
        conn.commit()
        conn.close()
        return True, f"Faturamento #{faturamento_id} cancelado."
    
    def resumo_financeiro(self) -> Dict:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COALESCE(SUM(valor_total), 0) as total FROM financeiro_orcamentos WHERE status != ?', ('rejeitado',))
        total_orcado = cursor.fetchone()['total']
        
        cursor.execute('SELECT COALESCE(SUM(valor_liquido), 0) as total FROM financeiro_faturamento')
        total_faturado = cursor.fetchone()['total']
        
        cursor.execute('SELECT COALESCE(SUM(valor_liquido), 0) as total FROM financeiro_faturamento WHERE status_pagamento = ?', ('pago',))
        total_pago = cursor.fetchone()['total']
        
        cursor.execute('SELECT COALESCE(SUM(valor_liquido), 0) as total FROM financeiro_faturamento WHERE status_pagamento IN (?, ?)', ('pendente', 'parcial'))
        total_pendente = cursor.fetchone()['total']
        
        conn.close()
        return {
            'total_orcado': float(total_orcado),
            'total_faturado': float(total_faturado),
            'total_pago': float(total_pago),
            'total_pendente': float(total_pendente)
        }
    
    def evolucao_mensal(self, meses: int = 12) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', data_faturamento) as mes,
                COALESCE(SUM(valor_liquido), 0) as faturado,
                COALESCE(SUM(CASE WHEN status_pagamento = 'pago' THEN valor_liquido ELSE 0 END), 0) as pago
            FROM financeiro_faturamento
            WHERE data_faturamento >= date('now', ?)
            GROUP BY mes
            ORDER BY mes
        ''', (f'-{meses} months',))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def comissoes_pendentes(self) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                o.id as orcamento_id,
                o.cliente_id,
                o.descricao,
                o.valor_total,
                o.comissao_equipe_id,
                e.nome as equipe_nome,
                e.comissao_percentual,
                (o.valor_total * e.comissao_percentual / 100.0) as comissao_valor
            FROM financeiro_orcamentos o
            LEFT JOIN equipe e ON o.comissao_equipe_id = e.id
            WHERE o.status = 'faturado' AND o.comissao_equipe_id IS NOT NULL
            AND o.id NOT IN (
                SELECT orcamento_id FROM financeiro_faturamento 
                WHERE comissao_paga = 1 AND orcamento_id IS NOT NULL
            )
            ORDER BY o.data_emissao
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def pagar_comissao(self, orcamento_id: int) -> Tuple[bool, str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM financeiro_orcamentos WHERE id = ?', (orcamento_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, f"Orçamento #{orcamento_id} não encontrado."
        
        cursor.execute('''
            UPDATE financeiro_faturamento SET comissao_paga = 1 WHERE orcamento_id = ?
        ''', (orcamento_id,))
        conn.commit()
        conn.close()
        return True, f"Comissão do orçamento #{orcamento_id} marcada como paga."

if __name__ == "__main__":
    from db_schema import init_db
    init_db()
    
    fm = FinanceiroManager()
    
    ok, msg, oid = fm.criar_orcamento(
        cliente_id=1,
        descricao="Aplicação VRT - Soja 2026",
        custo_insumos=15000.0,
        custo_mao_obra=3500.0,
        custo_equipamentos=2000.0,
        custo_transporte=1200.0,
        custo_administrativo=800.0,
        desconto_percentual=5.0
    )
    logging.info(f"[ORCAMENTO] {ok}: {msg}")
    
    if oid:
        ok2, msg2 = fm.aprovar_orcamento(oid)
        logging.info(f"[APROVAR] {ok2}: {msg2}")
        
        ok3, msg3, fid = fm.faturar_orcamento(oid, numero_nota="0001", metodo_pagamento="PIX")
        logging.info(f"[FATURAR] {ok3}: {msg3}")
        
        if fid:
            ok4, msg4 = fm.marcar_pago(fid)
            logging.info(f"[PAGAR] {ok4}: {msg4}")
    
    resumo = fm.resumo_financeiro()
    logging.info(f"[RESUMO] Orçado: R$ {resumo['total_orcado']:.2f} | Faturado: R$ {resumo['total_faturado']:.2f} | Pago: R$ {resumo['total_pago']:.2f}")
    
    evo = fm.evolucao_mensal()
    logging.info(f"[EVOLUCAO] {len(evo)} meses retornados.")
    
    com = fm.comissoes_pendentes()
    logging.info(f"[COMISSOES] {len(com)} pendentes.")

