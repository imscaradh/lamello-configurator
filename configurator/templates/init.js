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

    $( "#m1 input" ).blur(function() {
        var m2 = $("#m2 input");
        if(m2.val() == "") {
            m2.val($(this).val()); 
        }
        updateMaterial1($(this).val());
    });

    $( "#m2 input" ).blur(function() {
        updateMaterial2($(this).val());
    });

    $( "#angle input" ).blur(function() {
        rotateMaterial2($(this).val());
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

        var data = {{ connection_types_json|safe }};
        var model = data[num].fields;

        drawMaterial('m1', model.x1, model.y1, model.width1, model.height1);
        drawMaterial('m2', model.x2, model.y2, model.width2, model.height2);
    }

    function drawMaterial(name, x, y, width, height) {
        canvas.drawRect({
            layer: true,
            name: name,
            strokeStyle: '#000',
            strokeWidth: 2,
            x: x, 
            y: y,
            width: width,
            height: height 
        });
    }

    function updateMaterial1(width) {
        var m1 = canvas.getLayer('m1');
        var offsetX = m1.x - (width - m1.width);
        canvas.setLayer('m1', {
            width: width,
            x: offsetX
        })
        .drawLayers(); 
    }

    function updateMaterial2(height) {
        var m2 = canvas.getLayer('m2');
        var offsetY = m2.y - (height- m2.height);
        canvas.setLayer('m2', {
            height: height
            //y: offsetY
        })
        .drawLayers(); 
    }

    function rotateMaterial2(angle) {
        var m2 = canvas.getLayer('m2');
        //FIXME: Improve
        var originY = 40;
        var offsetY = originY - Math.sin(angle/180*Math.PI) * m2.width;
        canvas.setLayer('m2', {
            rotate: -angle,
            y: offsetY
        })
        .drawLayers(); 
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
