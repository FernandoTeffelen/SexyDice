document.addEventListener("DOMContentLoaded", () => {
    const rollBtn = document.getElementById("rollBtn");
    const diceCountSelector = document.getElementById("diceCountSelector");
    const allDiceBlocks = document.querySelectorAll(".dice-block");

    // ALTERAÇÃO AQUI: Trocamos a configuração de 4 dados pela de 3.
    const diceConfigs = {
        1: [{ min: 1, max: 66 }],
        2: [{ min: 1, max: 33 }, { min: 34, max: 66 }],
        3: [{ min: 1, max: 22 }, { min: 23, max: 44 }, { min: 45, max: 66 }],
        6: [{ min: 1, max: 11 }, { min: 12, max: 22 }, { min: 23, max: 33 }, { min: 34, max: 44 }, { min: 45, max: 55 }, { min: 56, max: 66 }]
    };

    // Array que armazenará os dados atualmente visíveis
    let activeDiceElements = [];

    // Função para atualizar a visualização dos dados
    const updateDiceView = (count) => {
        const config = diceConfigs[count];
        activeDiceElements = []; // Limpa os dados ativos

        allDiceBlocks.forEach((block, index) => {
            if (index < count) {
                block.style.display = "flex"; // Mostra o bloco do dado

                const diceId = index + 1;
                const diceData = {
                    dice: document.getElementById(`dice${diceId}`),
                    label: document.getElementById(`label${diceId}`),
                    title: block.querySelector('.dice-title'),
                    ...config[index]
                };
                activeDiceElements.push(diceData);

                // Atualiza o título e o rótulo do dado
                diceData.title.textContent = `Dado ${diceId}`;
                diceData.label.innerHTML = `Posições de <br> ${diceData.min} a ${diceData.max}`;

            } else {
                block.style.display = "none"; // Esconde o bloco do dado
            }
        });

        // Caso especial para 1 dado
        if (count == 1) {
            activeDiceElements[0].title.textContent = "Dado Único";
        }
    };

    // Função para embaralhar um array
    const shuffleArray = (array) => {
        const copy = [...array];
        for (let i = copy.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [copy[i], copy[j]] = [copy[j], copy[i]];
        }
        return copy;
    };

    // Função para converter número para ordinal
    const ordinal = (n) => {
        const ordinais = ["Primeira", "Segunda", "Terceira", "Quarta", "Quinta", "Sexta"];
        return ordinais[n - 1] || `${n}ª`;
    };

    // Evento de clique no botão de girar
    rollBtn.addEventListener("click", () => {
        const promises = activeDiceElements.map(({ dice, min, max }) => {
            return new Promise(resolve => {
                const x = 360 * (Math.floor(Math.random() * 4) + 1);
                const y = 360 * (Math.floor(Math.random() * 4) + 1);
                dice.style.transform = `rotateX(${x}deg) rotateY(${y}deg)`;

                const onTransitionEnd = () => {
                    dice.removeEventListener("transitionend", onTransitionEnd);
                    const number = Math.floor(Math.random() * (max - min + 1)) + min;
                    dice.querySelector("img").src = `posições/${number}.png`;
                    resolve();
                };
                dice.addEventListener("transitionend", onTransitionEnd);
            });
        });

        // Atualiza os rótulos de sugestão após todas as animações
        Promise.all(promises).then(() => {
            const diceIndexes = Array.from(Array(activeDiceElements.length).keys());
            const ordemAleatoria = shuffleArray(diceIndexes);

            ordemAleatoria.forEach((dadoIndex, posicao) => {
                const label = activeDiceElements[dadoIndex].label;
                let destaque;

                if (posicao === 0) destaque = `<span class="primeiro">${ordinal(posicao + 1)}</span>`;
                else if (posicao === 1) destaque = `<span class="segundo">${ordinal(posicao + 1)}</span>`;
                else if (posicao === 2) destaque = `<span class="terceiro">${ordinal(posicao + 1)}</span>`;
                else destaque = `<span class="sublinhado">${ordinal(posicao + 1)}</span>`;

                label.innerHTML = `Sugestão: ${destaque} colocada`;
            });
        });
    });

    // Evento de mudança no seletor de dados
    diceCountSelector.addEventListener("change", (event) => {
        const count = parseInt(event.target.value, 10);
        updateDiceView(count);
    });

    // Inicializa a visualização com o valor padrão do seletor
    updateDiceView(parseInt(diceCountSelector.value, 10));
});