import ast

class O2Detector(ast.NodeVisitor):
    def __init__(self):
        self.viloes = []
        self.loop_depth = 0
        self.current_func = None
        
        # Dicionário de Regras Expandido
        self.regras = {
            'Pandas': {
                'append': ('Pandas: .append()', 'Cópia cara do DF.', 'Use lista + pd.concat().', 'pd.concat([df1, df2])'),
                'sort_values': ('Pandas: .sort_values()', 'Ordenação repetida.', 'Ordene antes do loop.', 'df.sort_values(by="col")'),
                'iterrows': ('Pandas: .iterrows()', 'Lento.', 'Use vetorização.', 'df["nova"] = df["a"] + df["b"]')
            },
            'Polars': {
                'vstack': ('Polars: .vstack()', 'Realoção cara.', 'Use Expression API.', 'pl.concat([df1, df2])'),
                'filter': ('Polars: .filter()', 'Perda de Lazy Eval.', 'Use Joins/GroupBy.', 'df.filter(...)'),
                'iter_rows': ('Polars: .iter_rows()', 'Quebra vetorização.', 'Use Expression API.', 'df.with_columns(...)')
            },
            'Spark': {
                'count': ('Spark: .count()', 'Action cara.', 'Calcule 1x.', 'df.agg(count("*"))'),
                'withColumn': ('Spark: .withColumn()', 'DAG ineficiente.', 'Use .select().', 'df.select(col("a"), col("b"))'),
                'collect': ('Spark: .collect()', 'Risco de OOM.', 'Evite trazer ao Driver.', 'df.take(n)'),
                'toPandas': ('Spark: .toPandas()', 'Transferência massiva.', 'Filtre antes.', 'df.filter(...).toPandas()')
            },
            'IO': {
                'execute': ('I/O: SQL em loop', 'Latência de banco.', 'Use bulk insert.', 'executemany(query, data)'),
                'get': ('I/O: HTTP em loop', 'Latência de rede.', 'Use sessões/async.', 'grequests.map(requests)')
            }
        }

    def visit_FunctionDef(self, node):
        old_func = self.current_func
        self.current_func = node.name
        self.generic_visit(node)
        self.current_func = old_func

    def visit_For(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    # Detecta: string += string ou lista += lista
    def visit_AugAssign(self, node):
        if self.loop_depth > 0 and isinstance(node.op, ast.Add):
            self.viloes.append({
                'linha': node.lineno, 'funcao': self.current_func or 'global',
                'vilao': 'Geral: Concatenação += em loop', 'problema': 'O(n²) por realocação.', 
                'solucao': 'Use "".join() ou list.append().', 'patch': 'list.append(item)'
            })
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.loop_depth > 0:
            nome = self._get_call_name(node)
            for lib, methods in self.regras.items():
                if nome in methods:
                    tipo, prob, sol, patch = methods[nome]
                    self.viloes.append({
                        'linha': node.lineno, 'funcao': self.current_func or 'global',
                        'vilao': tipo, 'problema': prob, 'solucao': sol, 'patch': patch
                    })
            
            # Regra específica: list.insert(0)
            if nome == 'insert' and self._is_insert_zero(node):
                self.viloes.append({
                    'linha': node.lineno, 'funcao': self.current_func or 'global',
                    'vilao': 'Geral: list.insert(0)', 'problema': 'Move todos os elementos.', 
                    'solucao': 'Use collections.deque.', 'patch': 'from collections import deque'
                })
        self.generic_visit(node)

    def _is_insert_zero(self, node):
        return len(node.args) > 0 and isinstance(node.args[0], ast.Constant) and node.args[0].value == 0

    def _get_call_name(self, node):
        if isinstance(node.func, ast.Attribute): return node.func.attr
        if isinstance(node.func, ast.Name): return node.func.id
        return ""

def analisar_arquivo(path):
    with open(path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    detector = O2Detector()
    detector.visit(tree)
    
    if detector.viloes:
        with open('relatorio_performance.md', 'w', encoding='utf-8') as f:
            f.write("# 🚀 Relatório de Performance\n\n")
            for v in detector.viloes:
                f.write(f"### 📍 Linha {v['linha']} | {v['vilao']}\n- **Problema:** {v['problema']}\n- **Solução:** {v['solucao']}\n- **Patch:** `{v['patch']}`\n\n")
        print(f"✅ Análise concluída: {len(detector.viloes)} vilões encontrados em 'relatorio_performance.md'.")
    else:
        print("✅ Código limpo!")

if __name__ == "__main__":
    import sys
    analisar_arquivo(sys.argv[1] if len(sys.argv) > 1 else 'seu_script.py')