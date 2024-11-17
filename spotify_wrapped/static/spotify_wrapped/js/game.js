function createGame(gameData) {
    new p5((sketch) => {
	let rows, cols;
	const sqSize = 50;
	const maxAlbums = 5;
	
	let snake;
	let direction;
	let questionNo;
	let questions;
	let growth;
	let gameState;
	let lastMoveTime, moveInterval;
	
	sketch.preload = () => {
	    // loads the question images into the object
	    const albumHasPreviewUrl = (album) => (
		album.tracks.filter(track => track.preview_url !== "").length > 0
	    );

	    questions = [];
	    for (let i = 0; i < window.albums.length && questions.length < 5; i++) {
		const qcount = questions.length;
		// skip questions which don't have a preview song clip
		while (i < window.albums.length && !albumHasPreviewUrl(window.albums[i])) {
		    i++;
		}
		if (i === window.albums.length) break;

		questions.push({});
		questions[qcount].index = i;	
		questions[qcount].images = [
		    sketch.loadImage(window.albums[i].tracks[0].album_image)
		];

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
		)
		questions[qcount].images.push(
		    sketch.loadImage(window.albums[decoy2].tracks[0].album_image)
		)
	    }
	}

	sketch.setup = () => {
	    const canvasParent = document.getElementById("games");
	    const albums = window.albums;
	    const canvasWidth = sqSize*Math.floor(window.innerWidth/sqSize);
	    const canvasHeight = sqSize*Math.floor(window.innerHeight/sqSize);
	    sketch.createCanvas(canvasWidth, canvasHeight)
		.parent(canvasParent);
	    updateGridDimensions();
	    // it should take three seconds to cross the screen's shortest length
	    lastMoveTime = 0;
	    moveInterval = Math.floor(3*1000/Math.min(rows, cols));

	    // 0: LEFT; 1: UP; 2: RIGHT; 3: DOWN;
	    direction = Math.floor(Math.random()*4);
	    // 1 block snake at the center of screen
	    snake = [[Math.floor(cols/2), Math.floor(rows/2)]];
	    growth = 3;
	    questionNo = 0;
	    gameState = 0;

	    const overlapping = (oldCords, newCord) => 
		oldCords.filter(cord => cord[0] === newCord[0] && cord[1] === newCord[1])
		    .length > 0;

	    for (let i = 0; i < maxAlbums; i++) {
		const idx = questions[i].index;
		questions[i].song = sketch.createAudio(window.albums[idx].tracks[0].preview_url);

		questions[i].locations = [];
		for (let j = 0; j < 3; j++) {
		    let newCord = randomCoords();
		    while (overlapping(questions[i].locations, newCord))
			newCord = randomCoords();
		    questions[i].locations.push(newCord);
		}
	    }

	    // questions[0].song.play();
	}

	sketch.draw = () => {
	    sketch.background(255);
	    drawGrid();
	    drawSnake();
	    drawApples();

	    if (gameState === 0) {
		drawOpeningMenu();
	    } else if (gameState === 2) {
		drawLossMenu();
	    } else if (gameState === 3) {
		drawWinMenu();
	    }
		
	    const currentTime = sketch.millis();
	    if (currentTime - lastMoveTime < moveInterval) return;
	    lastMoveTime = currentTime;

	    if (gameState === 1) {
		moveSnake();
		if (appleCollision()) {
		    growth += 3;
		    questions[questionNo].song.stop();
		    if (++questionNo === questions.length) {
			gameState = 3;
			return;
		    }
		    questions[questionNo].song.play();
		}
		if (poisonAppleCollision()) {
		    gameState = 2;
		}
		if (gameState === 2) {
		    questions[questionNo].song.stop();
		}
	    }
	}

	sketch.windowResized = () => {
	    sketch.resizeCanvas(window.innerWidth, window.innerHeight);
	    updateGridDimensions();
	    sketch.setup();
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

	    direction = newDirection;
	    lastMoveTime -= 100000;
	}

	// sketch.rect(sketch.width/2, sketch.height*13/16, Math.max(sketch.width, sketch.height)/4, sketch.height*3/32);
	sketch.mousePressed = () => {
	    const boxWidth = Math.max(sketch.width, sketch.height)/4;
	    const boxHeight = sketch.height*3/32;
	    const leftEdge = sketch.width/2-boxWidth/2;
	    const rightEdge = sketch.width/2+boxWidth/2;
	    const topEdge = sketch.height*13/16-boxHeight/2;
	    const bottomEdge = sketch.height*13/16+boxHeight/2;

	    if (sketch.mouseX > leftEdge && sketch.mouseY < rightEdge
		&& sketch.mouseY > topEdge && sketch.mouseY < bottomEdge) {
		questions[0].song.play();
		gameState = 1;
		lastMoveTime = sketch.millis();
	    }
	}
	
	let startX, startY;
	sketch.touchStarted = (event) => {
	    if (event.changedTouches) {
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

	    if (newDirection === direction) return;
	    direction = newDirection;
	    lastMoveTime -= 100000;

	    return false;
	}
		
	// function playCurrentSong() {
	//     if (questionNo >= questions.length) return;
	//
	//     currentSong = questions[questionNo].song;
	//     currentSong.play();
	//     
	//     currentSong.onended(() => console.log("HERE"));
	//     console.log(currentSong);
	// }
	//
	function drawOpeningMenu() {
	    sketch.fill(255);
	    sketch.stroke(0);
	    sketch.strokeWeight(2);
	    sketch.rectMode(sketch.CENTER);
	    sketch.rect(sketch.width/2, sketch.height/2, sketch.width*3/4, sketch.height*3/4);

	    sketch.fill(0);
	    sketch.textAlign(sketch.CENTER);
	    sketch.textFont('Fredoka');
	    const dim = Math.min(sketch.width, sketch.height);
	    const title = "Snake Wrapped";
	    sketch.textSize(dim/12);
	    sketch.text(title, sketch.width/2, sketch.height*1/4, sketch.width*5/8, sketch.height/4);

	    const desc = "How well do you know your music? If the " +
			    "snake eats the cover of the song playing, " +
			    "you move on. The wrong one, and you lose. " +
			    "Good Luck!"
	    sketch.textSize(dim/20);
	    sketch.textFont('Montserrat');
	    sketch.rectMode(sketch.CORNER);
	    sketch.text(desc, sketch.width*3/16, sketch.height*5/16, sketch.width*5/8, sketch.height*3/8);
	    
	    
	    sketch.rectMode(sketch.CENTER);
	    sketch.fill("white");
	    sketch.rect(sketch.width/2, sketch.height*13/16, Math.max(sketch.width, sketch.height)/4, sketch.height*3/32);

	    sketch.fill("black");
	    sketch.text("START?", sketch.width/2, sketch.height*13/16);
	}

	function drawLossMenu() {

	}

	function drawWinMenu() {

	}

	function updateGridDimensions() {
	    rows = Math.floor(sketch.height / sqSize);
	    cols = Math.floor(sketch.width / sqSize);
	}
	
	function randomCoords() {
	    return [Math.floor(Math.random()*cols), Math.floor(Math.random()*rows)];
	}

	function drawGrid() {
	    sketch.fill("#FFCBA4");
	    sketch.stroke("#000");
	    sketch.strokeWeight(2);
	    sketch.rectMode(sketch.CORNER);
	    for (let col = 0; col < cols; col++) {
		for (let row = 0; row < rows; row++) {
		    sketch.square(col*sqSize, row*sqSize, sqSize);
		}
	    }
	}

	function drawSnake() {
	    sketch.fill("#F00");
	    sketch.stroke("#000");
	    sketch.strokeWeight(2);
	    for (let point of snake) {
		sketch.square(point[0]*sqSize, point[1]*sqSize, sqSize);
	    }
	}

	function moveSnake() {
	    let newPoint = [...snake[0]];
	    if (direction == 0) newPoint[0] -= 1;
	    else if (direction == 1) newPoint[1] -= 1;
	    else if (direction == 2) newPoint[0] += 1;
	    else if (direction == 3) newPoint[1] += 1;
	    if (outOfBounds(newPoint) || hitSelf(newPoint)) {
		gameState = 2;
	    }

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

	function appleCollision() {
	    return questions[questionNo].locations[0][0] === snake[0][0]
		&& questions[questionNo].locations[0][1] === snake[0][1];
	}
	function poisonAppleCollision() {
	    return (questions[questionNo].locations[1][0] === snake[0][0]
		    && questions[questionNo].locations[1][1] === snake[0][1]) ||
		   (questions[questionNo].locations[2][0] === snake[0][0]
		    && questions[questionNo].locations[2][1] === snake[0][1])
	}
    });

}
