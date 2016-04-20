$(function () {
    initCanvas();
    initSituationPreview();

    function initCanvas() {
        var canvas = $("#connectionPreview");

        // Resizing the canvas dynamically
        var ctx = ctx = canvas[0].getContext('2d');
        ctx.canvas.width = $(".preview").width();
        ctx.canvas.height = $(".preview").height();

    }

    function drawShape(num) {
        var canvas = $("#connectionPreview");
        canvas.clearCanvas();
        console.info("Index: " + num);

        switch (num) {
            case 0:
                canvas.drawArc({
                    draggable: true,
                    fillStyle: "green",
                    x: 100, y: 100,
                    radius: 50
                });
                break;
            case 1:
                canvas.drawEllipse({
                    fillStyle: '#c33',
                    x: 150, y: 100,
                    width: 200, height: 100
                });
                break;
            case 2:
                canvas.drawRect({
                    fillStyle: '#000',
                    x: 150, y: 100,
                    width: 200,
                    height: 100
                });
                break;
            case 3:
                // Draw a triangle
                canvas.drawPolygon({
                    strokeStyle: 'black',
                    strokeWidth: 4,
                    x: 200, y: 100,
                    radius: 50,
                    sides: 3
                });
                break;
            case 4:
                $('canvas').drawLine({
                    strokeStyle: '#000',
                    strokeWidth: 4,
                    rounded: true,
                    startArrow: true,
                    arrowRadius: 15,
                    arrowAngle: 90,
                    x1: 100, y1: 100,
                    x2: 150, y2: 125,
                    x3: 200, y3: 75
                });
                break;
            default:
                canvas.drawRect({
                    fillStyle: '#000',
                    x: 150, y: 100,
                    width: 200,
                    height: 100
                });
                break;
        }
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
