
let numberCount;
let result;


document.getElementById("inc").onclick = function(){
    numberCount = document.getElementById("counter").textContent;
    numberCount = Number(numberCount);
    result = numberCount + 1
    document.getElementById("counter").textContent = result
}

document.getElementById("dec").onclick = function(){
    numberCount = document.getElementById("counter").textContent;
    numberCount = Number(numberCount);
    result = numberCount - 1
    document.getElementById("counter").textContent = result
}

document.getElementById("reset").onclick = function(){
    document.getElementById("counter").textContent = 0
}