

// clicker code. 


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


// guessing game code

let submitButton = document.getElementById("submitButton");
let input = document.getElementById("guessingGameInput");
let resultGame = document.getElementById("result");
let running = false;
let guess;
let guessingNumber;


submitButton.onclick = function(){
    if(!running){
        guessingNumber = Math.floor(Math.random() * 100);
    }
    running = true
    guess = Number(input.value)
    if(isNaN(guess) || guess < 0 || guess > 100){
        resultGame.textContent = "That is not a valid number"
    }
    else{
        if(guess === guessingNumber){
            resultGame.textContent = `That is correct! The number was ${guessingNumber}!`
            running = false
        }
        else if(guess < guessingNumber){
            resultGame.textContent = "Too low!"
        }
        else if(guess > guessingNumber){
            resultGame.textContent = "Too high!"
        }
    }
    
    console.log(guessingNumber)
}

