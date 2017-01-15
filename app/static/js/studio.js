/* ----

    theStudio.js: Make a painting

    The Studio example allows the user to click a few buttons and create a modern
    masterpiece ala Diebenkorn, Rothko, Motherwell, Newman, etc. You know, those
    50s guys that obsessed over truth.


    To-do:
        The important ones:
        - clean up and minimize where possible
        - browser handling
        - should there be another canvas layer for shapes?

        The ones I'm going to put off:
        - make random looper a high-order function
        - fix context calls -- made too repeatedly
        - redo the whole thing to take OOP into account LOL
            - Objects: Studio, Painting, Painter, Assistants
        - error handling

        The not so important ones:
        - additional shape functions
        - animate warning colors
        - make context and canvas variables global (why doesn't it work?)

---- */

$(document).ready(function() {
	/* Sets studio size based on browser width to constrain canvas to screen */
    setStudioSize();

    /* Lets user drag painting around within the studio */
    $("#painting").draggable({containment: "#studio", scroll: false});
    $("#moreinfo").draggable({containment: "#studio", scroll: false});
    $("button").hover(function() {
        $(this).toggleClass("buttonHover");
    });
    /* Toggles info canvas */
    $("#moreinfoLink").click(function() {
        toggleInfo();
    });
    /*$("#moreinfo").click(function() {
        var txt = $("#moreinfo").is(":visible") ? "Gimmie the deets." : "Cool, I'll get back to painting now";
        $("#moreinfoLink").text(txt);

        toggleInfo();
    });*/
    $("#advancedOptionsLink").click(function() {
        $("#advancedOptions_bg").slideToggle();
        $("#advancedOptions").slideToggle();
    });
});


/* This is like a main function, for the decision-making-impaired */
function doEverything() {
    if ($("#moreinfo").css("visibility") == "visible") {
        $("#moreinfo").css("visibility", "hidden");
    }

    /* Reset current canvas */
    trash();

    var width = randomNum(3, maxWidth());
    var height = randomNum(3, maxWidth());

    buildStretcher(width, height);
    setStudioSize();
    setBackground();
    drawRectangles();
    /*drawTriangle();*/
    drawGesture();
    drawLines();
}


/* ----

    Some studio assitants

---- */

/* The informers */


/* Returns width and height of canvas for limiting random numbers */
function getWidth() {return $("#paintingBg").width();}
function getHeight() {return $("#paintingBg").height();}

/* Gets context
    Note: This is used repeatedly, there must be a better way */
function getBgContext() {
    var canvas = document.getElementById("paintingBg");
    var context = canvas.getContext("2d");
    return context;
}
function getMgContext() {
    var canvas = document.getElementById("paintingMg");
    var context = canvas.getContext("2d");
    return context;
}
function getFgContext() {
    var canvas = document.getElementById("paintingFg");
    var context = canvas.getContext("2d");
    return context;
}

/* Makes sure user input is valid and subtly warns if not */
function checkInput(width, height) {
    var width = document.forms["userOptions"]["canvasUserWidth"].value;
    var height = document.forms["userOptions"]["canvasUserHeight"].value;

    if (width >= 901 || height >= 901 || width <= 49 || height <= 49 || width == NaN || height == NaN) {
        $("#warning").css("color", "red");
    }
    else {
        if ($("#warning").css("color") == "rgb(255, 0, 0)") {
            $("#warning").css("color", "black");
        }
        trash();
        return [width, height];
    }
}

/* Will be used to give the add some shapes function a shape function call
	- Currently returns function choice as a string which doesn't work */
function findShape() {
    var actions = ["drawTriangle", "drawCircle", "drawSquare", "drawPolygon", "drawRectangle"];
    var action = actions[randomNum(1)];
    while (action == undefined) {
    	action = actions[randomNum(1)];
    }
    return action;
}

/* Sets max dimensions -- may be used later to adjust based on screen width */
function maxWidth() {return 900;}
function maxHeight() {return 900;}

/* The randoms */

/* Gets a random number, though I think at the moment still inaccurately */
function randomNum(digits, limit) {
    digits = Math.pow(10, digits);
    if (limit) {
        limit = limit + 10;
        var number = limit;
        while(number >= limit) {
            number = Math.floor(Math.random() * digits);
        }
        return number;
    }
    else {
        number = Math.floor(Math.random() * digits);
        return number;
    }
}
function randomColor() {return "#" + randomNum(7, 999999);}


/* The assistants */

function buildStretcher(width, height) {
    var newWidth;
    var newHeight;

    /* Check where dimensions are coming from */
    if (width != undefined && height != undefined) {
        while (width < 40 || width > maxWidth() || height < 40 || height > maxWidth() || width >= (4 * height) || height >= (4 * width)) {
            width = randomNum(3, maxWidth());
            height = randomNum(3, maxWidth());
        }
        newWidth = width;
        newHeight = height;
    }
    else {
        var dimensions = checkInput();
        newWidth = dimensions[0];
        newHeight = dimensions[1];
    }

    setWidth(newWidth);
    setHeight(newHeight);
    /*centerCanvas();*/
    if ($("#moreinfo").css("visibility") == "visible") {$("#moreinfo").css("visibility", "hidden");}
    toggleCanvas("show");
}
function setWidth(newWidth) {
    var canvasBg = document.getElementById("paintingBg");
    canvasBg.width = newWidth;
    var canvasMg = document.getElementById("paintingMg");
    canvasMg.width = newWidth;
    var canvasFg = document.getElementById("paintingFg");
    canvasFg.width = newWidth;
}
function setHeight(newHeight) {
    var canvasBg = document.getElementById("paintingBg");
    canvasBg.height = newHeight;
    var canvasMg = document.getElementById("paintingMg");
    canvasMg.height = newHeight;
    var canvasFg = document.getElementById("paintingFg");
    canvasFg.height = newHeight;
}
/* This doesn't work like I want it to yet */
function centerCanvas() {
    $("#paintingBg").css("left", "15%");
    $("#paintingBg").css("top", "15%");
    $("#paintingMg").css("left", "15%");
    $("#paintingMg").css("top", "15%");
    $("#paintingFg").css("left", "15%");
    $("#paintingFg").css("top", "15%");
}
/* This is no longer being used because it would stretch the image
function rotate() {
    var canvasBgWidth = getWidth();
    var canvasBgHeight = getHeight();

    function swapDimensions() {
        var newWidth = getHeight();
        var newHeight = getWidth();

        $("#paintingBg").width(Math.floor(newWidth));
        $("#paintingBg").height(Math.floor(newHeight));
        $("#paintingMg").width(Math.floor(newWidth));
        $("#paintingMg").height(Math.floor(newHeight));
        $("#paintingFg").width(Math.floor(newWidth));
        $("#paintingFg").height(Math.floor(newHeight));
    }
    swapDimensions();
}*/
/* Show or hide canvas */
function toggleCanvas(option) {
    if(option == "hide") {
        $("#paintingBg").css("visibility", "hidden");
        $("#paintingMg").css("visibility", "hidden");
        $("#paintingFg").css("visibility", "hidden");
    }
    else if(option == "show") {
        $("#paintingBg").css("visibility", "visible");
        $("#paintingMg").css("visibility", "visible");
        $("#paintingFg").css("visibility", "visible");
    }
}
/* Will set global variables (somehow) that other functions will test against */
function setAdvanced() {
    var oneColor = document.forms["advancedOptions"]["linesOneColor"].value;
    var fillShapes = document.forms["advancedOptions"]["fillShapes"].value;

    if (oneColor.checked == true) {
    	var oneColor = true;
    }
    if (fillShapes.checked == true) {
    	var fillShapes = true;
    }
    return [oneColor, fillShapes];
}
function resetAdvanced() {

}
/* Get window dimension and set studio sized appropriately */
function getWindowDimensions() {return[$(window).height(), $(window).width()];}
function setStudioSize() {
    var dimensions = getWindowDimensions();
    var studioHeight = dimensions[0];
    var studioWidth = dimensions[1] - 350;
    $("#studio").css("width", studioWidth);
    $("#studio").css("height", studioHeight);
    console.log("Studio width is: " + $("#studio").css("width") + " and height is " + $("#studio").css("height"));
}

/* Deal with reest form */
function reset() {
    var resetBg = document.forms["resetOptions"]["resetBg"];
    var resetMg = document.forms["resetOptions"]["resetMg"];
    var resetFg = document.forms["resetOptions"]["resetFg"];

    if (resetBg.checked == true) {
        var contextBg = getBgContext();
        setBackground("white");
        resetBg.checked = false;
    }
    if (resetMg.checked == true) {
        var contextMg = getMgContext();
        contextMg.clearRect(0, 0, getWidth(), getHeight());
        resetMg.checked = false;
    }
    if (resetFg.checked == true) {
        var contextFg = getFgContext();
        contextFg.clearRect(0, 0, getWidth(), getHeight());
        resetFg.checked = false;
    }
}

/* Make the painting go away */
function trash() {
    var contextBg = getBgContext();
    var contextMg = getMgContext();
    var contextFg = getFgContext();
    contextBg.clearRect(0, 0, getWidth(), getHeight());
    contextMg.clearRect(0, 0, getWidth(), getHeight());
    contextFg.clearRect(0, 0, getWidth(), getHeight());
    setWidth(0);
    setHeight(0);
    toggleCanvas("hide");
}

/* dang this is ugly */
function toggleInfo() {
    /* If the more info pane is hidden, display it, and show or hide the painting */
    if ($("#moreinfo").css("visibility") == "hidden") {
        $("#moreinfo").css("visibility", "visible");
        $("#moreinfoLink").text("Cool, I'll get back to painting now.");
        if ($("#paintingBg").css("visibility") == "visible") {
            toggleCanvas("hide");
        }
        else {toggleCanvas("hide");}
    }
    /* If it's visible, hide it, and show or hide the painting */
    else if ($("#moreinfo").css("visibility") == "visible") {
    	$("#moreinfoLink").text("Gimmie the deets.");
        $("#moreinfo").css("visibility", "hidden");
        if ($("#paintingBg").css("visibility") == "visible") {
            toggleCanvas("show");
        }
        else if (getWidth() <= 49 && $("#paintingBg").css("visibility") == "hidden") {
            toggleCanvas("hide");
        }
        else {
            toggleCanvas("show");
        }
    }
}


/* ----

    The painters

    To-do:
        - Line colors and sizes reset by beginning and closing the path on each iteration.
          If there's a way to make that toggleable, or less chaotic, that would be good.
        - Consolidate looping functions into one

*/
function setBackground(color) {
    var context = getBgContext();

    if (color != undefined) {
        context.fillStyle = color;
        context.fillRect(0, 0, getWidth() + 2, getHeight() + 2);
    }
    else {
        context.fillStyle = randomColor();
        context.fillRect(0, 0, getWidth() + 2, getHeight() + 2);
    }
}
function drawRectangles() {
    var context = getMgContext();
    var numMoves = randomNum(1);
    var i = 0;
    for (; i < numMoves; i++) {
        drawRectangle(context, 4, getWidth(), getHeight());
    }
}
/* Action is a string now which doesn't work */
function drawShapes() {
	var action = findShape();
	action();

	drawTriangle();
	drawPolygon();
}
function drawLines() {
    var i = 0;
    var numLines = randomNum(2, 5);
    for (; i < numLines; i++) {
        drawLine();
    }
}
function drawRectangle(context, digits, widthLimit, heightLimit) {
    var opacity = 0;
    var shapeWidth = randomNum(digits, widthLimit);
    var shapeHeight = randomNum(digits, heightLimit);
    var left = randomNum(2, getWidth());
    var top = randomNum(2, getHeight());
    context.fillStyle = randomColor();
    context.fillRect(left, top, shapeWidth, shapeHeight);
}
function drawTriangle() {
	var context = getMgContext();
	var pointA = randomNum(3, getWidth());
	var pointB = randomNum(3, getWidth());
	var x = randomNum(3, getWidth());
	var y = randomNum(3, getWidth());

    context.beginPath();
    context.moveTo(x, y);
    context.lineTo(pointA, x);
    context.lineTo(pointA ,pointB);
    context.fillStyle = randomColor();
    context.fill();
}
function drawLine() {
    var context = getFgContext();
    context.beginPath();
    context.moveTo(randomNum(4, getWidth()), randomNum(4, getHeight()));
    context.lineTo(randomNum(4, getWidth()), randomNum(4, getHeight()));
    context.lineWidth = randomNum(1);
    context.strokeStyle = randomColor();
    context.stroke();
    context.closePath;
}
function drawGesture() {
    var context = getFgContext();
    var numCurves = 0;
    while (numCurves < 2) {
        numCurves = randomNum(1);
    }
    var i = 0;

    context.beginPath();
    context.moveTo(randomNum(3, getWidth()), randomNum(3, getHeight()));

    /* Make bezier curves */
    for (; i < numCurves; i++) {
        context.bezierCurveTo(randomNum(2.75, getWidth()), randomNum(2.75, getWidth()), randomNum(2.75, getWidth()), randomNum(2.75, getWidth()), randomNum(2.75, getWidth()), randomNum(2.75, getWidth()));
    }

    context.fillStyle = randomColor();
    context.lineWidth = randomNum(1);
    context.strokeStyle = randomColor();
    context.stroke();
    context.closePath();
}

/* Canvas is getting a little out of hand, may forgo these */
function drawSquare() {

}
function drawCircle() {

}
function drawPolygon() {

}

/* Add some keyboard conrols causy why not */
$("#canvasUserHeight").keypress(function(event){
    if(event.which == 13) {
        console.log("You pressed enter");
        buildStretcher();
    }
});
