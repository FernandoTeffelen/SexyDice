document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("promoVideo");
    const replayIcon = document.getElementById("replayIcon");
    const videoWrapper = document.getElementById("videoWrapper");

    let loopCount = 0;
    const maxLoops = 1;

    // Função que é chamada quando o vídeo termina
    video.addEventListener("ended", () => {
        loopCount++;
        if (loopCount < maxLoops) {
            // Se ainda não atingiu 3 loops, toca de novo
            video.play();
        } else {
            // Se já tocou 3 vezes:
            // 1. Volta o vídeo para o frame inicial. ESSA É A MUDANÇA!
            video.currentTime = 0;
            // 2. Mostra o ícone de replay sobre o frame inicial.
            replayIcon.style.display = "flex";
        }
    });

    // Função que é chamada quando o usuário clica no container do vídeo
    videoWrapper.addEventListener("click", () => {
        // Se o vídeo estiver pausado e os loops tiverem terminado, o clique vai reiniciar
        if (video.paused && loopCount >= maxLoops) {
            loopCount = 0;
            replayIcon.style.display = "none";
            video.play();
        }
    });
});