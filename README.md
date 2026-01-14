# Co-evolution_of_robots
python project for the 'Optimization for Artificial Intelligence' exam

- Like “robot wars”, two robots are fighting against each other and the winner is the surviving one.
- Define a set of actions (move, shoot, etc.) and sensors inputs
- Co-evolve GP individuals that controls the robots
- Also possible using small neural networks with NEAT

## Structure
project/
│
├── main.py              # NEAT loop + eval_genomes
├── arena.py             # physics + rules
├── robot.py             # robot state + actions
├── sensors.py           # perception layer
├── neat_controller.py   # genome → network → action
└── neat_config.txt      # NEAT parameters

## Flow
main
 └─ NEAT population
     └─ genome
         └─ NEATController
             └─ Sensors
                 └─ Arena + Robot




## Explain of the flow
1️⃣ Preparazione

L’utente avvia il programma.

NEAT crea una popolazione iniziale di robot, ognuno con un cervello artificiale diverso (network neurale) generato casualmente.

Ogni robot ha una posizione iniziale nell’arena, salute piena e sensori attivi (es. distanza dal nemico, angolo, energia).

2️⃣ Simulazione di una generazione

Per ogni genome della popolazione:

Posizionamento dei robot

Due robot controllati dallo stesso genome o da genome diversi vengono messi nell’arena.

Loop di step

I robot leggono i loro sensori (posizione avversario, distanza dai bordi, energia).

La rete neurale del robot riceve questi input e produce un’azione:

Movimento avanti/indietro

Rotazione (gira a sinistra/destra)

Sparo

Il robot applica l’azione.

L’arena verifica:

Se i robot rimangono dentro i confini

Se un colpo ha colpito l’avversario

Aggiorna la salute di ciascun robot

Fine dello scontro

Quando uno dei robot muore o si raggiunge un numero massimo di step:

Si calcola il fitness del genome:

più danni inflitti → fitness più alto

meno danni subiti → fitness più alto

scontri rapidi e vittorie costanti → premiati

3️⃣ Evoluzione della popolazione

NEAT prende tutti i genome e:

Seleziona i migliori secondo il fitness

Combina i geni (crossover)

Applica mutazioni (cambia pesi o struttura della rete)

Si genera la nuova generazione di robot/genome.

4️⃣ Ripetizione

Tutto il processo si ripete per il numero di generazioni specificato.

Ogni generazione dovrebbe migliorare i robot, perché NEAT favorisce i genome con performance migliori.

5️⃣ Risultato finale

Alla fine delle generazioni, NEAT restituisce il miglior genome → il robot “vincente”.

Questo robot sa muoversi, ruotare e sparare in modo efficace per sopravvivere più a lungo e colpire l’avversario.

## Setup & Run

Prerequisiti:
- Python `>= 3.9`

Setup rapido:
- Creare ed attivare un virtualenv, installare dipendenze ed eseguire:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Output atteso:
- Log dell’evoluzione NEAT per `GENERATIONS` generazioni.
- Salvataggio del miglior genome in `best_robot.pkl`.
- Test del migliore contro avversari casuali con stampa delle fitness.