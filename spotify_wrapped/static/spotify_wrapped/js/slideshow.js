// slideshow.js

let counter = 0;
const slides = document.getElementById("slides");
const totalSlides = slides.children.length;
const statusBar = document.getElementById("status-bar");
const pauseButton = document.getElementById("pause-button");

let slideProgress = 0;
const slideLength = 10; // in seconds
let progressInterval = null;

// Function to create progress interval
const makeProgressInterval = (currentCounter) => {
    return () => {
        slideProgress += 0.1;
        if (slideProgress >= 100) {
            showSlide(currentCounter + 1);
            return;
        }
        if (statusBar.children.length === 0) {
            console.error("No children in status bar");
            return;
        }
        statusBar.children[currentCounter].style.background =
            `linear-gradient(to right, grey ${slideProgress}%, white ${slideProgress}%)`;
    };
};

// Function to show a specific slide
const showSlide = (newCounter) => {
    const previousCounter = counter;
    counter = (newCounter + totalSlides) % totalSlides;

    // Correct negative modulo
    if (counter < 0) {
        counter = totalSlides - 1;
    }

    // Hide previous slide
    if (slides.children[previousCounter]) {
        slides.children[previousCounter].classList.remove('active');
    }

    // Show current slide
    slides.children[counter].classList.add('active');

    // Update the status bar
    for (let i = 0; i < totalSlides; i++) {
        const bar = statusBar.children[i];
        if (i < counter) {
            bar.style.background = "linear-gradient(to right, grey 100%, white 100%)";
        } else if (i === counter) {
            bar.style.background = "linear-gradient(to right, grey 0%, white 0%)";
        } else {
            bar.style.background = "linear-gradient(to right, white 100%, grey 100%)";
        }
    }

    // Reset slide progress
    slideProgress = 0;
    clearInterval(progressInterval);

    // Start progress interval if not paused and not on "games" slide
    if (!pauseButton.classList.contains("paused") && slides.children[counter].id !== "games") {
        progressInterval = setInterval(makeProgressInterval(counter), 100);
    }

    pauseButton.classList.remove("paused");
};

// Navigation arrow event listeners
document.querySelector(".left-arrow").addEventListener("click", () => {
    showSlide(counter - 1);
});
document.querySelector(".right-arrow").addEventListener("click", () => {
    showSlide(counter + 1);
});

// Pause button toggle
pauseButton.addEventListener("click", () => {
    if (pauseButton.classList.contains("paused")) {
        pauseButton.classList.remove("paused");
        if (slides.children[counter].id !== "games") {
            progressInterval = setInterval(makeProgressInterval(counter), 100);
        }
    } else {
        pauseButton.classList.add("paused");
        clearInterval(progressInterval);
    }
});

// Initialize the slideshow when the document is ready
document.addEventListener("DOMContentLoaded", () => {
    // Show the first slide
    slides.children[counter].classList.add('active');
    showSlide(counter);
});
