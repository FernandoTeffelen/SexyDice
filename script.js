const rollBtn = document.getElementById("rollBtn");

// Dados e rótulos
const diceElements = [
  { dice: document.getElementById("dice1"), label: document.getElementById("label1"), min: 1, max: 11 },
  { dice: document.getElementById("dice2"), label: document.getElementById("label2"), min: 12, max: 22 },
  { dice: document.getElementById("dice3"), label: document.getElementById("label3"), min: 23, max: 33 },
  { dice: document.getElementById("dice4"), label: document.getElementById("label4"), min: 34, max: 44 },
  { dice: document.getElementById("dice5"), label: document.getElementById("label5"), min: 45, max: 55 },
  { dice: document.getElementById("dice6"), label: document.getElementById("label6"), min: 56, max: 66 },
];

// Embaralha um array
function shuffleArray(array) {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

// Converte número para ordinal em português
function ordinal(n) {
  const ordinais = [
    "Primeira",
    "Segunda",
    "Terceira",
    "Quarta",
    "Quinta",
    "Sexta",
  ];
  return ordinais[n - 1] || n;
}

rollBtn.addEventListener("click", () => {
  const resultados = [];

  diceElements.forEach(({ dice, min, max }, index) => {
    const x = 360 * (Math.floor(Math.random() * 4) + 1);
    const y = 360 * (Math.floor(Math.random() * 4) + 1);
    dice.style.transform = `rotateX(${x}deg) rotateY(${y}deg)`;

    setTimeout(() => {
      const number = Math.floor(Math.random() * (max - min + 1)) + min;
      dice.querySelector("img").src = `posições/${number}.png`;
      resultados.push(index);

      if (resultados.length === 6) {
        const ordemAleatoria = shuffleArray([0, 1, 2, 3, 4, 5]);

        ordemAleatoria.forEach((dadoIndex, posicao) => {
          const label = diceElements[dadoIndex].label;
          let destaque;

          if (posicao === 0) {
            destaque = `<span class="primeiro">${ordinal(posicao + 1)}</span>`;
          } else if (posicao === 1) {
            destaque = `<span class="segundo">${ordinal(posicao + 1)}</span>`;
          } else if (posicao === 2) {
            destaque = `<span class="terceiro">${ordinal(posicao + 1)}</span>`;
          } else {
            destaque = `<span class="sublinhado">${ordinal(posicao + 1)}</span>`;
          }

          label.innerHTML = `<span class="prefixo">Sugestão: </span>${destaque} colocada`;
        });
      }
    }, 1000);
  });
});