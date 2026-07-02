# Relatório de Performance: Anti-patterns Detectados

### Linha 9 | Geral: list.insert(0) em loop
- **Problema:** Move elementos toda vez.
- **Solução:** Use collections.deque.
- **Patch sugerido:** `from collections import deque`

### Linha 24 | Pandas: .sort_values em loop
- **Problema:** Ordenação repetida.
- **Solução:** Ordene antes do loop.
- **Patch sugerido:** `df.sort_values(...)`

### Linha 25 | Pandas: df.append em loop
- **Problema:** Cópia cara.
- **Solução:** Use lista + pd.concat().
- **Patch sugerido:** `df_list.append(df); pd.concat(df_list)`

### Linha 30 | Polars: .filter em loop
- **Problema:** Perda de Lazy Evaluation.
- **Solução:** Use filtros no select/lazy.
- **Patch sugerido:** `df.filter(pl.col("a") > x)`

### Linha 34 | Spark: .count() em loop
- **Problema:** Action cara que dispara Job.
- **Solução:** Evite contagens parciais.
- **Patch sugerido:** `df.agg(count("*"))`

### Linha 35 | Spark: .withColumn em loop
- **Problema:** Plano (DAG) ineficiente.
- **Solução:** Use .select() único.
- **Patch sugerido:** `df.select(col("a"), col("b"))`

