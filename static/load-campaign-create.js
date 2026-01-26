
window.onload = function() {
    console.log("test");

    var dropdown = document.getElementById('level');
    for (let i = 0; i < 20; i++) {
        var newOption = document.createElement('option');
        newOption.value = i + 1;
        newOption.innerHTML = i + 1;
        dropdown.appendChild(newOption);
    }
}
