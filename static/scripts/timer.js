// Set the date we're counting down to
let countDownDate = new Date("4 18, 2020 21:15:30").getTime();

// Update the count down every 1 second
let x = setInterval(function() {

    // Get todays date and time
    let now = new Date().getTime();
    
    // Find the distance between now an the count down date
    let distance = countDownDate - now;
    
    // Time calculations for days, hours, minutes and seconds
    let days = Math.floor(distance / (1000 * 60 * 60 * 24));
    let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    let seconds = Math.floor((distance % (1000 * 60)) / 1000);
    
    // Output the result in an element with id="demo"
    let message = "Cоревнование начнётся через ";
    if (days > 0){
    	message += days + " д ";
    }
    message += hours + " ч "
    + minutes + " м " + seconds + " сек";
    document.getElementById("timer").innerHTML = message;
    // If the count down is over, write some text 
    if (distance < 0) {
        clearInterval(x);
        document.getElementById("timer").innerHTML = "EXPIRED";
    }
}, 1000);