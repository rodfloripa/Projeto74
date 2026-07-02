
<div align="justify">

# Detector de Anti-patterns de Performance com AST

## 1. Visão Geral

Este projeto implementa um analisador estático utilizando `ast` para identificar anti-patterns de performance em código Python, especialmente chamadas custosas executadas dentro de loops. O detector percorre a árvore sintática do programa sem executá-lo e gera automaticamente um relatório em Markdown contendo os problemas encontrados, explicações e sugestões de correção.

## 2. Estrutura

```text
projeto/
├── cod_eficiente.py
├── seu_script.py
├── relatorio_performance.md
└── README.md
```

## 3. Funcionamento

O fluxo é composto por cinco etapas:

1. Leitura do arquivo Python.
2. Conversão para AST.
3. Percurso da árvore com `ast.NodeVisitor`.
4. Comparação das chamadas encontradas com o dicionário de regras.
5. Geração do relatório `relatorio_performance.md`.

## 4. Classe Principal

A classe `O2Detector` herda de `ast.NodeVisitor` e sobrescreve os métodos responsáveis por visitar funções, loops e chamadas de funções. Durante a visita, mantém o controle da profundidade dos loops e identifica operações potencialmente custosas.

## 5. Base de Regras

As regras estão organizadas por biblioteca (Pandas, Polars, Spark e estruturas nativas do Python). Cada entrada contém o nome do anti-pattern, a justificativa, a solução recomendada e um exemplo de patch.

## 6. Complexidade

O analisador percorre cada nó da AST apenas uma vez.

| Operação | Complexidade |
|----------|--------------|
| Parsing | O(N) |
| Percorrer AST | O(N) |
| Consulta às regras | O(1) |
| Total | **O(N)** |

## 7. Como Executar

Para analisar um arquivo específico:

```bash
python cod_eficiente.py meu_codigo.py
```

Exemplo:

```bash
python cod_eficiente.py exemplo.py
```

Caso nenhum arquivo seja informado:

```bash
python cod_eficiente.py
```

Nesse caso será analisado automaticamente `seu_script.py`.

## 8. Saída

Se forem encontrados problemas:

```text
✅ Análise completa: X vilões detectados.
Veja 'relatorio_performance.md'.
```

Caso contrário:

```text
✅ Código limpo! Nenhuma violação detectada.
```

## 9. Conclusão

O projeto demonstra o uso de análise estática baseada em AST para detectar gargalos de desempenho de forma automática. Além de ser uma ferramenta útil para inspeção de código, constitui um excelente projeto de portfólio por reunir conceitos de compiladores, estruturas de dados e engenharia de software.

</div>
