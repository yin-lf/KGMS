var toggleBtns = document.querySelectorAll('.js-formToggle');
for(var i = 0; i < toggleBtns.length; i++){ 
   
    toggleBtns[i].addEventListener("click",toggleForm);
}


var firstClick = true;

function toggleForm(){ 
   

    if(!firstClick){ 
   
        document.querySelector('.js-imageAnimate').classList.toggle("animate");
        document.querySelector('.js-imageAnimate').classList.toggle("animateOut");


        document.querySelector('.js-panel_content').classList.toggle("animate");
        document.querySelector('.js-panel_content').classList.toggle("animateOut");
    }
    else{ 
   
        firstClick = false;
        document.querySelector('.js-imageAnimate').classList.add("animate");
        document.querySelector('.js-panel_content').classList.add("animate");

    }
}