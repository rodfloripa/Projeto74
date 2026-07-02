import ast

class O2Detector(ast.NodeVisitor):
    def __init__(self):
        self.viloes = []
        self.loop_depth = 0
        self.current_func = None
        # Dicionário completo de regras
        self.regras = {
            'Pandas': {
                'append': ('df.append em loop', 'Cópia cara.', 'Use lista + pd.concat().', 'df_list.append(df); pd.concat(df_list)'),
                'sort_values': ('.sort_values em loop', 'Ordenação repetida.', 'Ordene antes do loop.', 'df.sort_values(...)'),
                'iterrows': ('.iterrows()', 'Performance extremamente lenta.', 'Use vetorização (numpy) ou .apply().', 'df["nova"] = df["a"] + df["b"]'),
                'apply': ('.apply(lambda) em loop', 'Execução no interpretador Python.', 'Use funções nativas do Pandas/Numpy.', 'df["col"].str.lower()')
            },
            'Polars': {
                'concat': ('pl.concat em loop', 'Realocação de memória.', 'Acumule em lista.', 'pl.concat(lista_dfs)'),
                'filter': ('.filter em loop', 'Perda de Lazy Evaluation.', 'Use filtros no select/lazy.', 'df.filter(pl.col("a") > x)'),
                'iter_rows': ('.iter_rows()', 'Quebra a vetorização.', 'Use a Expression API.', 'df.with_columns(pl.col("a") * 2)'),
                'with_columns': ('.with_columns em loop', 'Múltiplos planos lógicos.', 'Combine todas as expressões em um único comando.', 'df.with_columns([pl.col("a")+1, pl.col("b")+2])')
            },
            
        
            'Spark': {
                'count': ('.count() em loop', 'Action cara que dispara Job.', 'Evite contagens parciais.', 'df.agg(count("*"))'),
                'withColumn': ('.withColumn em loop', 'Plano (DAG) ineficiente.', 'Use .select() único.', 'df.select(col("a"), col("b"))'),
                'collect': ('.collect() em loop', 'Risco de OOM no Driver.', 'Evite trazer ao Driver.', 'df.take(n)'),
                'join': ('.join()', 'Shuffle pesado.', 'Use broadcast().', 'df.join(broadcast(df_p), "id")'),
                'toPandas': ('.toPandas()', 'Transferência massiva.', 'Filtre antes.', 'df.filter(...).limit(100).toPandas()'),
                'udf': ('UDF em loop', 'Impede Catalyst Optimizer.', 'Use funções nativas.', 'pyspark.sql.functions.col(...)')
            },
            'Geral': {
                'insert': ('list.insert(0) em loop', 'Move elementos toda vez.', 'Use collections.deque.', 'from collections import deque')
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

    def visit_Call(self, node):
        if self.loop_depth > 0:
            nome = self._get_call_name(node)
            for lib, methods in self.regras.items():
                if nome in methods:
                    tipo, prob, sol, patch = methods[nome]
                    self.viloes.append({
                        'linha': node.lineno, 'funcao': self.current_func or 'global',
                        'vilao': f"{lib}: {tipo}", 'problema': prob, 
                        'solucao': sol, 'patch': patch
                    })
        self.generic_visit(node)

    def _get_call_name(self, node):
        return node.func.attr if isinstance(node.func, ast.Attribute) else (node.func.id if isinstance(node.func, ast.Name) else "")

def gerar_relatorio(viloes):
    with open('relatorio_performance.md', 'w', encoding='utf-8') as f:
        f.write("# Relatório de Performance: Anti-patterns Detectados\n\n")
        for v in viloes:
            f.write(f"### Linha {v['linha']} | {v['vilao']}\n")
            f.write(f"- **Problema:** {v['problema']}\n")
            f.write(f"- **Solução:** {v['solucao']}\n")
            f.write(f"- **Patch sugerido:** `{v['patch']}`\n\n")

def analisar_arquivo(path):
    with open(path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    detector = O2Detector()
    detector.visit(tree)
    if detector.viloes:
        gerar_relatorio(detector.viloes)
        print(f"✅ Análise completa: {len(detector.viloes)} vilões detectados. Veja 'relatorio_performance.md'.")
    else:
        print("✅ Código limpo! Nenhuma violação detectada.")

if __name__ == "__main__":
    import sys
    analisar_arquivo(sys.argv[1] if len(sys.argv) > 1 else 'seu_script.py')