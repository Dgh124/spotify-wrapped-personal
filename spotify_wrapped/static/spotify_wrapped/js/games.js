let audioContext, audioBuffers, currentSource;

function createGame(gameData) {
new p5((sketch) => {
    let rows, cols;
    const sqSize = 50;
    const maxAlbums = 5;

    let snake;
    let direction, growth;
    let questionNo, questions;
    let lastMoveTime, moveInterval;


    sketch.preload = () => {
        // loads the question images into the object
        const albumHasPreviewUrl = (album) => {
            return album.tracks.filter(track => track.preview_url !== "None").length > 0
        };

        questions = [];
        for (let i = 0; i < window.albums.length && questions.length < 5; i++) {
            const qcount = questions.length;
            // skip questions which don't have a preview song clip
            while (i < window.albums.length && !albumHasPreviewUrl(window.albums[i])) {
                i++;
            }
            if (i === window.albums.length) break;

            questions.push({
                "index": i,
                "answer": window.albums[i].name,
                "images": [
                    sketch.loadImage(window.albums[i].tracks[0].album_image),
                ],
            });

            // get the image of the two poison apples (no overlaps)
            let decoy1 = decoy2 = Math.floor(Math.random()*window.albums.length);
            while (decoy1 === i) {
                decoy1 = Math.floor(Math.random()*window.albums.length);
            }
            while (decoy2 === decoy1 || decoy2 === i) {
                decoy2 = Math.floor(Math.random()*window.albums.length);
            }

            questions[qcount].images.push(
                sketch.loadImage(window.albums[decoy1].tracks[0].album_image)
            );
            questions[qcount].images.push(
                sketch.loadImage(window.albums[decoy2].tracks[0].album_image)
            )
        }
        console.log(questions);
    }

    sketch.setup = () => {
        const canvasParent = document.getElementById("games");
        const canvasWidth = sqSize*Math.floor(window.innerWidth/sqSize);
        const canvasHeight = sqSize*(Math.floor(window.innerHeight/sqSize)-1);
        sketch.createCanvas(canvasWidth, canvasHeight)
            .parent(canvasParent);
        updateGridDimensions();

        start();

        activateStartMenu();
    }

    function start() {
        // it should take five seconds to cross the screen's shortest length
        lastMoveTime = 0;
        moveInterval = Math.floor(5*1000/Math.min(rows, cols));

        // 0: LEFT; 1: UP; 2: RIGHT; 3: DOWN;
        direction = Math.floor(Math.random()*4);
        // 1 block snake at the center of screen
        snake = [[Math.floor(cols/2), Math.floor(rows/2)]];
        growth = 3;
        questionNo = 0;
        window.gameState = 0;

        const overlapping = (oldCords, newCord) => 
            oldCords.filter(cord => cord[0] === newCord[0] && cord[1] === newCord[1])
                .length > 0;

        for (let i = 0; i < maxAlbums; i++) {
            const idx = questions[i].index;
            questions[i].locations = [];
            for (let j = 0; j < 3; j++) {
                let newCord = randomCoords();
                while (overlapping(questions[i].locations, newCord))
                    newCord = randomCoords();
                questions[i].locations.push(newCord);
            }
        }
        window.currentSource?.stop();
    }

    window.gameSetup = () => {
        start();
    }

    sketch.draw = () => {
        sketch.background(255);
        drawGrid();

        if (window.gameState === 1) {
            drawSnake();
            drawApples();

            const currentTime = sketch.millis();
            if (currentTime - lastMoveTime < moveInterval) return;
            lastMoveTime = currentTime;

            moveSnake();
        }
    }

    sketch.windowResized = () => {
        sketch.resizeCanvas(window.innerWidth, window.innerHeight);
        updateGridDimensions();
    }

    sketch.keyPressed = () => {
        const left_keys  = ["ArrowLeft",  'a', 'h'];
        const up_keys    = ["ArrowUp",    'w', 'k'];
        const right_keys = ["ArrowRight", 'd', 'l'];
        const down_keys  = ["ArrowDown",  's', 'j'];

        let newDirection = direction;
        if (left_keys.includes(sketch.key) && direction !== 2) {
            newDirection = 0; // LEFT
        } else if (up_keys.includes(sketch.key) && direction !== 3) {
            newDirection = 1; // UP
        } else if (right_keys.includes(sketch.key) && direction !== 0) {
            newDirection = 2; // RIGHT
        } else if (down_keys.includes(sketch.key) && direction !== 1) {
            newDirection= 3; // DOWN
        }

        if (newDirection === direction) return;
        if (window.gameState !== 1) return;

        direction = newDirection;
        moveSnake();
        lastMoveTime = sketch.millis();
    }

    let startX, startY;
    sketch.touchStarted = (event) => {
        if (event.touches) {
            startX = event.touches[0].pageX;
            startY = event.touches[0].pageY;
        } else if (event.pageX && event.pageY) {
            startX = event.pageX;
            startY = event.pageY;
        }
    }

    sketch.touchEnded = (event) => {
        let endX, endY;
        if (event.changedTouches) {
            endX = event.changedTouches[0].pageX;
            endY = event.changedTouches[0].pageY;
        } else if (event.pageX && event.pageY) {
            endX = event.pageX;
            endY = event.pageY;
        }

        let diffX = endX - startX;
        let diffY = endY - startY;
        let newDirection = direction;

        const swipeThreshold = 25;
        // determine if it was a horizontal or vertical swipe
        if (Math.abs(diffX) > Math.abs(diffY)) {
            console.log("Horizontal swipe");
            // horizontal swipe
            if (diffX < -swipeThreshold) {
                newDirection = 0;
            }
            else if (diffX > swipeThreshold) {
                newDirection = 2;
            }
        } else {
            console.log("Vertical swipe");
            // vertical swipe
            if (diffY < -swipeThreshold) {
                newDirection = 1;
            } else if (diffY > swipeThreshold) {
                newDirection = 3;
            }
        }

        if (newDirection % 2 === direction % 2) return;
        direction = newDirection;
        moveSnake();
        lastMoveTime = sketch.millis();

        return false;
    }


    function playAudio(idx) {
        // if (idx < 0 || idx >= audioBuffers.length) return;
        if (questionNo > 0 && questionNo < questions.length) {
            window.currentSource.stop();
        }

        const buffer = audioBuffers[idx];
        if (!buffer) {
            console.error('Audio buffer not found:', idx);
            return;
        }

        source = window.audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(window.audioContext.destination);
        source.start(0);
        window.currentSource = source;
    }


    function checkCollisions(newPoint) {
        if (appleCollision(newPoint)) {
            growth += 3;
            // win state
            if (++questionNo === questions.length) {
                window.gameState = 3;
                activateWinMenu();
                window.currentSource.stop();
                playAudio(audioBuffers.length-2);
                return;
            }
            playAudio(questionNo);
        } else if (
            poisonAppleCollision(newPoint) ||
            outOfBounds(newPoint) ||
            hitSelf(newPoint)
        ) {
            window.gameState = 2;
            activateLossMenu();
            window.currentSource.stop();
            playAudio(audioBuffers.length-1);
        }

    }

    function updateGridDimensions() {
        rows = Math.floor(sketch.height / sqSize);
        cols = Math.floor(sketch.width / sqSize);
    }

    function randomCoords() {
        return [Math.floor(Math.random()*cols), Math.floor(Math.random()*rows)];
    }

    function drawGrid() {
        sketch.fill("#FCBE65");
        sketch.stroke("FFFFF0");
        sketch.strokeWeight(2);
        sketch.rectMode(sketch.CORNER);
        for (let col = 0; col < cols; col++) {
            for (let row = 0; row < rows; row++) {
                sketch.square(col*sqSize, row*sqSize, sqSize);
            }
        }
    }

    function drawSnake() {
        sketch.fill("#FC659D");
        sketch.stroke("#FFFFF0");
        sketch.strokeWeight(2);
        for (let point of snake) {
            sketch.square(point[0]*sqSize, point[1]*sqSize, sqSize);
        }
    }

    function moveSnake() {
        if (!snake) return;
        let newPoint = [...snake[0]];
        if (direction === 0) newPoint[0] -= 1;
        else if (direction === 1) newPoint[1] -= 1;
        else if (direction === 2) newPoint[0] += 1;
        else if (direction === 3) newPoint[1] += 1;
        checkCollisions(newPoint);

        snake.unshift(newPoint);
        // if the snake has to grow, don't pop off the tail
        if (growth > 0) growth--;
        else snake.pop();
    }

    function outOfBounds(newPoint) {
        return newPoint[0] < 0 || newPoint[0] >= cols
            || newPoint[1] < 0 || newPoint[1] >= rows;
    }

    function hitSelf(newPoint) {
        return snake.filter(cord => (
            cord[0] === newPoint[0] && cord[1] === newPoint[1]
        )).length > 0;
    }

    function drawApples() {
        sketch.rectMode(sketch.CENTER);
        for (let i = 0; i < 3; i++) {
            sketch.image(questions[questionNo].images[i], 	
                questions[questionNo].locations[i][0]*sqSize,
                questions[questionNo].locations[i][1]*sqSize,
                sqSize, sqSize
            );
        }
    }

    function appleCollision(newPoint) {
        return questions[questionNo].locations[0][0] === newPoint[0]
            && questions[questionNo].locations[0][1] === newPoint[1];
    }
    function poisonAppleCollision(newPoint) {
        return (questions[questionNo].locations[1][0] === newPoint[0]
            && questions[questionNo].locations[1][1] === newPoint[1]) ||
            (questions[questionNo].locations[2][0] === newPoint[0]
                && questions[questionNo].locations[2][1] === newPoint[1])
    }


    window.audioContextInit = () => {
        // initialize audio context
        audioBuffers = Array(questions.length + 2);
        if (!window.audioContext) {
            window.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        const loadAudio = (url, idx) => (
            fetch(url)
            .then(response => response.arrayBuffer())
            .then(arrayBuffer => window.audioContext.decodeAudioData(arrayBuffer))
            .then(audioBuffer => {
                audioBuffers[idx] = audioBuffer;
            })
            .catch(e => console.error('Error loading audio:', e))
        );
        Promise.all([...questions.map((q, idx) => loadAudio(
            window.albums[q.index].tracks[0].preview_url, idx
        )),
            loadAudio(winGameLink, audioBuffers.length-2),
            loadAudio(loseGameLink, audioBuffers.length-1),
        ])
            .then(() => gameState === 1 && playAudio(0));

        
    }
});
}

(() => {
    const startMenu = document.getElementById("startGame");
    startMenu.children.item(2)
        .addEventListener("click", (e) => {
            startMenu.classList.add("hidden");
            window.gameState = 1;
            // play the first song
            (window.audioContextInit || (() => console.warn("audio context not initialized")))();
        });

    const lossMenu = document.getElementById("lostGame");
    lossMenu.children.item(2)
        .addEventListener("click", (e) => {
            lossMenu.classList.add("hidden");
            window.gameSetup();
            window.gameState = 1;
            (window.audioContextInit || (() => console.warn("audio context not initialized")))();
        });

    const winMenu = document.getElementById("wonGame");
    winMenu.children.item(2)
        .addEventListener("click", (e) => {
            winMenu.classList.add("hidden");
            window.gameSetup();
            window.gameState = 1;
            (window.audioContextInit || (() => console.warn("audio context not initialized")))();
        });
})();

function unhideMenu(menuId) {
    document.getElementById(menuId)
        .classList.remove("hidden");
}

function activateStartMenu() {
    unhideMenu("startGame");
}

function activateLossMenu() {
    unhideMenu("lostGame");
}

function activateWinMenu() {
    unhideMenu("wonGame");
}
