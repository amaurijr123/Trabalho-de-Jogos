# Pato Sentinela

Tower defense baseado no exemplo de estados e eventos do Trab3, usando Pygame
e o sprite original. Proteja o ninho no centro da arena durante oito ondas.

## Executar

Na raiz do repositorio, com Python 3.10 ou superior. A dependencia pygame-ce
fornece o modulo pygame e funciona com o Python 3.14 deste ambiente:

```powershell
python -m pip install -r Trab3/requirements.txt
python Trab3/main.py
```

## Controles

- Mouse: mirar; segurar botao esquerdo ou Espaco: disparar.
- 1: arma rapida, dano 1, intervalo de 0,18 segundos.
- 2: canhao, dano 4, intervalo de 0,7 segundos.
- 3: arma eletrica, dano 1 e atordoamento por 1,2 segundos.
- P: pausar; R: reiniciar; Esc: sair.

A cada oito abates, ganha cinco segundos de cadencia dobrada.
Apos receber dano, o jogador fica invencivel e pisca por um segundo.
Inimigos de borda dourada possuem mais vida e menor velocidade.

## Implementacao

`entities.py` aplica State nas armas (`WeaponState`, `Cannon`, `Electric`)
e nos inimigos (`Approaching`, `Aiming`, `Stunned`). Invencibilidade e power-up
sao estados temporizados independentes da arma. Inimigos interrompem o ataque
quando atordoados e voltam a se aproximar ao terminar o efeito.

O `EventHandler` original de `util.py` conecta objetos ao controlador `Game`:

| Evento | Origem | Resultado |
| --- | --- | --- |
| Shoot | Arma | Cria projetil |
| SpawnEnemy | Ondas | Registra inimigo |
| Collision | Detector | Aplica dano e remove projetil |
| DestroyObj | Inimigo ou projetil | Remove objeto |
| AttackPlayer | Inimigo mirando | Solicita dano no jogador |
| EnemyKilled | Inimigo | Soma pontos e conta abates |
| PowerUp | Contador de abates | Ativa cadencia dobrada |
| PlayerDamaged | Jogador | Cria efeito visual |

Movimento e temporizadores usam segundos. Colisoes consideram o segmento
percorrido pelo projetil entre quadros. Reiniciar limpa os observadores para
evitar assinaturas duplicadas. `player.py` e `bullet.py` preservam os exemplos
originais para comparacao; o jogo usa `entities.py`.

Teste de abertura com encerramento automatico: `python Trab3/main.py --frames 120`.
Testes de comportamento: `python -m unittest discover -s Trab3 -p "test_*.py"`.
