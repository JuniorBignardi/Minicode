# Análise estatística do Nível 1

Métrica **A**: corretos ÷ (corretos + errados), descartados fora (a pré-definida). Métrica **B**: estrita, por prompt; inavaliável conta como não correto e plano ilegível vale 0.
IC 95% por bootstrap sobre tarefas (5000 reamostras). Comparações pareadas: mesmas tarefas nos dois modelos.

## Teste real (60 prompts, 25 tarefas)

| modelo | A: valores corretos (IC 95%) | B estrita (IC 95%) |
|---|---|---|
| base | 10.2% (0 a 24) | 4.7% (0 a 11) |
| base+2 exemplos | 32.1% (18 a 47) | 23.3% (12 a 36) |
| ajustado (3 épocas) | 65.0% (55 a 76) | 60.3% (48 a 72) |
| ajustado (melhor ponto) | 67.5% (57 a 77) | 59.5% (47 a 71) |
| 14B | 67.4% (51 a 83) | 45.8% (31 a 61) |

Diferenças pareadas (em pontos percentuais; positivo = o primeiro é melhor):

| comparação | A: diferença (IC 95%) | A: P(dif ≤ 0) | B: diferença (IC 95%) | B: P(dif ≤ 0) |
|---|---|---|---|---|
| ajustado (3 épocas) − base | +54.8 (+39 a +69) | 0.000 | +55.6 (+44 a +67) | 0.000 |
| ajustado (3 épocas) − base+2 exemplos | +32.8 (+21 a +45) | 0.000 | +37.0 (+25 a +49) | 0.000 |
| ajustado (3 épocas) − 14B | -2.4 (-16 a +11) | 0.625 | +14.4 (+4 a +25) | 0.004 |
| ajustado (melhor ponto) − ajustado (3 épocas) | +2.5 (-5 a +9) | 0.242 | -0.8 (-7 a +5) | 0.589 |

## Teste sintético (80 prompts, 80 exercícios)

| modelo | A: valores corretos (IC 95%) | B estrita (IC 95%) |
|---|---|---|
| base | 9.2% (4 a 16) | 6.2% (3 a 10) |
| base+2 exemplos | 47.6% (39 a 57) | 36.3% (29 a 44) |
| ajustado (3 épocas) | 66.8% (61 a 73) | 64.2% (58 a 70) |
| ajustado (melhor ponto) | 71.5% (66 a 76) | 67.2% (61 a 73) |
| 14B | 69.8% (62 a 77) | 59.3% (51 a 67) |

Diferenças pareadas (em pontos percentuais; positivo = o primeiro é melhor):

| comparação | A: diferença (IC 95%) | A: P(dif ≤ 0) | B: diferença (IC 95%) | B: P(dif ≤ 0) |
|---|---|---|---|---|
| ajustado (3 épocas) − base | +57.6 (+50 a +65) | 0.000 | +58.1 (+52 a +64) | 0.000 |
| ajustado (3 épocas) − base+2 exemplos | +19.1 (+10 a +29) | 0.000 | +28.0 (+19 a +37) | 0.000 |
| ajustado (3 épocas) − 14B | -3.0 (-11 a +5) | 0.757 | +5.0 (-3 a +13) | 0.125 |
| ajustado (melhor ponto) − ajustado (3 épocas) | +4.7 (-0 a +9) | 0.027 | +3.0 (-2 a +8) | 0.127 |

## Planos com TODOS os casos corretos (um caso errado ou inavaliável tira o plano da conta; denominador = todos os prompts)

| modelo | real | sintético |
|---|---|---|
| base | 2/60 (3%) | 1/80 (1%) |
| base+2 exemplos | 8/60 (13%) | 5/80 (6%) |
| ajustado (3 épocas) | 12/60 (20%) | 14/80 (18%) |
| ajustado (melhor ponto) | 13/60 (22%) | 13/80 (16%) |
| 14B | 20/60 (33%) | 24/80 (30%) |
