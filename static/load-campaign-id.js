
window.onload = function() {
    console.log("loading campaign with id");

    var players = document.getElementById('player-list-wrapper');
    for(let i = 0; i < 2; i++) {
        console.log("player");
    }
    var newPlayer = document.createElement('a');
    newPlayer.innerHTML = "NEW PLAYER";
    newPlayer.src = "/campaigns";
    players.appendChild(newPlayer);

}
