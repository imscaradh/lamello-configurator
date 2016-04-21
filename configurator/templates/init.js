$(function () {

    // -----------------------------------------------
    // 			function calls and configuration
    // -----------------------------------------------
    var canvas = $("#connectionPreview");
    $.jCanvas.defaults.fromCenter = false;

    // functions called on page load
    initSituationPreview();
    initCanvas();

    // functions called on page resize
    $( window ).resize(function() {
        initCanvas();
    });


    // -----------------------------------------------
    // 			function declarations	
    // -----------------------------------------------

    function initCanvas() {
        // Resizing the canvas dynamically
        var ctx = ctx = canvas[0].getContext('2d');
        console.debug("Resized canvas: " + $(".preview").width() + "x" + $(".preview").height());
        ctx.canvas.width = $(".preview").width();
        ctx.canvas.height = $(".preview").height();
    }

    function drawShape(num) {
        canvas.clearCanvas();
        console.info("Index: " + num);

        var data = {{ connection_types_json|safe }};
        var model = data[num].fields;

        drawMaterial(model.x1, model.y1, model.width1, model.height1);
        drawMaterial(model.x2, model.y2, model.width2, model.height2);
    }

    function drawMaterial(x, y, width, height) {
        canvas.drawRect({
            strokeStyle: '#000',
            strokeWidth: 2,
            x: x, 
            y: y,
            width: width,
            height: height 
        });
    }

    function initSituationPreview() {
        $('.connection li').hover(function(e) {
            var $target = $(e.target);
            console.info("hovered " + $target.text());
            drawShape($(this).index());
        });

        $('.connection a').click(function(e) {
            $('.connection .selected-text').html($(e.target).text());
        });
    }

    function isConnectionPossible(m1, m2, angle) {
        console.info("Material 1: " + m1);
        console.info("Material 2: " + m2);
        console.info("Angle: " + angle);

        //TODO: Calculation
    }
});
