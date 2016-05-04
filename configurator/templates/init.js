$(function () {

    // -----------------------------------------------
    // 			function calls and configuration
    // -----------------------------------------------
    var data = {{ connection_types_json|safe }};
    var canvas = $("#connectionPreview");
    $.jCanvas.defaults.fromCenter = false;

    // functions called on page load
    initSituationPreview();
    initCanvas();
    initFormActions();
    initFormSubmitActions();
    pdfGeneration();

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

    function initFormActions() {
        $( "#m1 input" ).blur(function() {
            var m2 = $("#m2 input");
            if(m2.val() == "") {
                m2.val($(this).val()); 
                scaleMaterial2($(this).val());
            }
            scaleMaterial1($(this).val());
        });

        $( "#m2 input" ).blur(function() {
            scaleMaterial2($(this).val());
        });

        $( "#angle input" ).blur(function() {
            //rotateMaterial2($(this).val());
        });
    }

    function initFormSubmitActions() {
        // Submit post on submit
        $('#calculationForm').on('submit', function(event){
            event.preventDefault();
            create_post();
        });
    }

    // AJAX for posting
    function create_post() {
        var serializedForm = $("#calculationForm").serialize();
        console.log("ajax submit with data [" + serializedForm + "] is in progress..."); 
        $.ajax({
            url : "calc/",
            type : "POST",
            data : serializedForm,

            // handle a successful response
            success : function(json) {
                console.log(json); // log the returned json to the console
                $(".cnc p#cncNum").html(json);
            },

            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };

    function drawShape(num) {
        canvas.removeLayers().drawLayers();

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

    function scaleMaterial1(width) {
        var m1 = canvas.getLayer('m1');
        var m2 = canvas.getLayer('m2');
        var offsetX = m1.x - (width - m1.width);
        canvas.setLayer('m1', {
            width: width,
            x: offsetX
        }).drawLayers(); 
    }

    function scaleMaterial2(height) {
        var m2 = canvas.getLayer('m2');
        var offsetY = m2.y - (height - m2.height);
        canvas.setLayer('m2', {
            height: height,
            y: offsetY
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
            var targetText = $(e.target).text();
            $('.connection .selected-text').html(targetText);
            $('input#connection_type').val(targetText);
        });
    }

    function pdfGeneration() {
        $('.pdf-btn').click(function() {
            var $m1 = $('#m1 input').val();
            console.log("m1: " + $m1);
            var $m2 = $('#m2 input').val();
            console.log("m2: " + $m2);
            var $angle = $('#angle input').val();
            console.log("angle: " + $angle);
            var $situation = $('#connection_type').val();
            console.log("situation: " + $situation);
            //var $canvas = document.getElementById('#connectionPreview');
            //var b64String = $canvas.toDataURL();
            //console.log("b64String: " + b64String);
            $.ajax({
            url : "pdf/",
            type : "POST",
            data : {
                m1: $m1,
                m2: $m2,
                angle: $angle,
                situation: $situation,
                //b64String: b64String
            },

           // handle a successful response
            success : function() {
                console.log("success");
            },

            // handle a non-successful response
            error : function() {
                console.log("Fails");
            }
        });

        })
    }
});
