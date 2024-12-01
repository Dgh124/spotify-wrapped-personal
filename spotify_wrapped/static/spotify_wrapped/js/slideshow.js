let counter = 0;
let totalSlides = document.getElementsByClassName("slide-container").length;
const slides = document.getElementById("slides");
const status_bar = document.getElementById("status-bar");
const pauseButton = document.getElementById("pause-button");

let slide_progress = 0;
const slide_length = 10; // in seconds
let progress_interval = null;


const makeProgressInterval = (counter) => {
    return () => {
        slide_progress += 0.1;
        if (slide_progress >= 100) {
            show_slide(counter + 1);
            return;
        }
        if (status_bar.children.length === 0) {
            console.error("no children in status bar");
            return;
        }
        status_bar.children[counter].style.background = 
            `linear-gradient(to right, grey ${slide_progress}%, white ${slide_progress}%)`;
    }
};

const show_slide = (new_counter) => {
    totalSlides = document.getElementsByClassName("slide-container").length;
    if (totalSlides === 0 || status_bar.children.length === 0) {
        console.error("no slides loaded");
        return;
    }
    const previousCounter = counter;
    counter = (new_counter + totalSlides) % totalSlides;
    if (counter < 0) {
        counter = totalSlides - 1;
    }

    // Hide previous slide
    if (slides.children[previousCounter]) {
        slides.children[previousCounter].classList.remove('active');
    }
    slides.children[counter].classList.add('active');
    for (let i = 0; i < totalSlides; i++) {
		const bar = status_bar.children[i];
		if (i < counter) {
			bar.style.background = "linear-gradient(to right, white 0%, grey 0%)";
		} else {
			bar.style.background = "linear-gradient(to right, white 100%, grey 100%)";
		}

    }

    slide_progress = 0;
    clearInterval(progress_interval);
    progress_interval = setInterval(makeProgressInterval(counter), slide_length);
    pauseButton.classList.remove("paused");

    if (slides.children[counter].id == "games") {
        clearInterval(progress_interval);
    }
};

document.querySelector(".left-arrow").addEventListener("click", () => {
    show_slide(counter - 1);
});
document.querySelector(".right-arrow").addEventListener("click", () => {
    show_slide(counter + 1);
});
document.querySelector(".left-arrow").addEventListener("touchstart", () => {
    show_slide(counter - 1);
});
document.querySelector(".right-arrow").addEventListener("touchstart", () => {
    show_slide(counter + 1);
});

document.addEventListener("DOMContentLoaded", () => {
    show_slide(counter);
});

pauseButton.addEventListener("click", (e) => {
    if (pauseButton.classList.contains("paused")) {
        pauseButton.classList.remove("paused");
        clearInterval(progress_interval);
        progress_interval = setInterval(makeProgressInterval(counter), slide_length);
    } else {
        pauseButton.classList.add("paused");
        clearInterval(progress_interval);
    }
});

pauseButton.addEventListener("touchstart", (e) => {
    if (pauseButton.classList.contains("paused")) {
        pauseButton.classList.remove("paused");
        clearInterval(progress_interval);
        progress_interval = setInterval(makeProgressInterval(counter), slide_length);
    } else {
        pauseButton.classList.add("paused");
        clearInterval(progress_interval);
    }
});
