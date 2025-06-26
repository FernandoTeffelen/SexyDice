document.addEventListener("DOMContentLoaded", () => {
    const rollBtn = document.getElementById("rollBtn");
    const diceCountSelector = document.getElementById("diceCountSelector");
    const allDiceBlocks = document.querySelectorAll(".dice-block");

    const historyLimits = {
        1: 20,
        2: 15,
        3: 10,
        6: 5
    };
    let rollHistory = new Map();

    const diceConfigs = {
        1: [{ min: 1, max: 66 }],
        2: [{ min: 1, max: 33 }, { min: 34, max: 66 }],
        3: [{ min: 1, max: 22 }, { min: 23, max: 44 }, { min: 45, max: 66 }],
        6: [{ min: 1, max: 11 }, { min: 12, max: 22 }, { min: 23, max: 33 }, { min: 34, max: 44 }, { min: 45, max: 55 }, { min: 56, max: 66 }]
    };

    let activeDiceElements = [];

    const updateDiceView = (count) => {
        rollHistory.clear();
        const config = diceConfigs[count];
        activeDiceElements = [];

        allDiceBlocks.forEach((block, index) => {
            if (index < count) {
                block.style.display = "flex";
                const diceId = index + 1;
                const diceData = {
                    dice: document.getElementById(`dice${diceId}`),
                    label: document.getElementById(`label${diceId}`),
                    title: block.querySelector('.dice-title'),
                    ...config[index]
                };
                activeDiceElements.push(diceData);
                diceData.title.textContent = `Dado ${diceId}`;
                diceData.label.innerHTML = `Posições de <br> ${diceData.min} a ${diceData.max}`;
            } else {
                block.style.display = "none";
            }
        });

        if (count == 1) {
            activeDiceElements[0].title.textContent = "Dado Único";
        }
    };

    const shuffleArray = (array) => {
        const copy = [...array];
        for (let i = copy.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [copy[i], copy[j]] = [copy[j], copy[i]];
        }
        return copy;
    };

    const ordinal = (n) => {
        const ordinais = ["Primeira", "Segunda", "Terceira", "Quarta", "Quinta", "Sexta"];
        return ordinais[n - 1] || `${n}ª`;
    };

    rollBtn.addEventListener("click", () => {
        // --- MUDANÇA 1: Desabilita o botão para prevenir cliques múltiplos ---
        rollBtn.disabled = true;

        const promises = activeDiceElements.map(({ dice, min, max }) => {
            // --- MUDANÇA 2: Lógica de Promise mais robusta com fallback ---
            return new Promise(resolve => {
                let resolved = false;

                // Função que finaliza a animação e resolve a promise
                const onFinish = () => {
                    if (resolved) return; // Garante que será executado apenas uma vez
                    resolved = true;
                    
                    dice.removeEventListener("transitionend", onFinish);

                    // Lógica de sorteio com memória (anti-repetição)
                    const dieId = dice.id;
                    const currentHistory = rollHistory.get(dieId) || [];
                    const diceCount = parseInt(diceCountSelector.value, 10);
                    const limit = historyLimits[diceCount];
                    let number;
                    let attempts = 0;
                    const maxAttempts = 50;

                    do {
                        number = Math.floor(Math.random() * (max - min + 1)) + min;
                        attempts++;
                    } while (currentHistory.includes(number) && attempts < maxAttempts);

                    currentHistory.push(number);
                    if (currentHistory.length > limit) {
                        currentHistory.shift();
                    }
                    rollHistory.set(dieId, currentHistory);

                    dice.querySelector("img").src = `${STATIC_FILES_PATH}posições/${number}.png`;
                    resolve();
                };

                // Adiciona o listener para o fim da transição
                dice.addEventListener("transitionend", onFinish);

                // Adiciona um timer de segurança (fallback). Se o evento de transição falhar,
                // este timer garante que o código continuará após 1.1 segundos.
                setTimeout(onFinish, 1100); // A animação dura 1s (1000ms)

                // Inicia a animação
                const x = 360 * (Math.floor(Math.random() * 4) + 1);
                const y = 360 * (Math.floor(Math.random() * 4) + 1);
                dice.style.transform = `rotateX(${x}deg) rotateY(${y}deg)`;
            });
        });

        Promise.all(promises).then(() => {
            const diceIndexes = Array.from(Array(activeDiceElements.length).keys());
            const ordemAleatoria = shuffleArray(diceIndexes);

            ordemAleatoria.forEach((dadoIndex, posicao) => {
                const label = activeDiceElements[dadoIndex].label;
                const numeroOrdinal = ordinal(posicao + 1);
                let destaque;

                if (posicao === 0) destaque = `<span class="primeiro">${numeroOrdinal}</span>`;
                else if (posicao === 1) destaque = `<span class="segundo">${numeroOrdinal}</span>`;
                else if (posicao === 2) destaque = `<span class="terceiro">${numeroOrdinal}</span>`;
                else destaque = `<span class="sublinhado">${numeroOrdinal}</span>`;

                label.innerHTML = `Sugestão:  ${ destaque }  colocada`;
            });
        }).finally(() => {
            // --- MUDANÇA 3: Reabilita o botão no final de tudo, com sucesso ou erro ---
            rollBtn.disabled = false;
        });
    });

    diceCountSelector.addEventListener("change", (event) => {
        const count = parseInt(event.target.value, 10);
        updateDiceView(count);
    });

    updateDiceView(parseInt(diceCountSelector.value, 10));
});