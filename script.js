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

rollBtn.addEventListener("click", () => {
  diceElements.forEach(({ dice, label, min, max }) => {
    // Gira aleatoriamente
    const x = 360 * (Math.floor(Math.random() * 4) + 1);
    const y = 360 * (Math.floor(Math.random() * 4) + 1);
    dice.style.transform = `rotateX(${x}deg) rotateY(${y}deg)`;

    // Escolhe imagem aleatória no intervalo do dado
    setTimeout(() => {
      const number = Math.floor(Math.random() * (max - min + 1)) + min;
      dice.querySelector("img").src = `posições/${number}.png`;
      label.textContent = `Imagem "${number}"`;
    }, 1000);
  });
});
