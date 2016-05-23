$(function () {

    // -----------------------------------------------
    // 			function calls and configuration
    // -----------------------------------------------
    var data = {{ connection_types_json|safe }};
    var canvas = $("#connectionPreview");
    var resultJson = null;
    var originX = 0;
    var originY = 0;
    var actualConnection = -1;

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
            rotateMaterial2($(this).val());
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

            success : function(json) {
                console.log(json);
                $.resultJson = json;
                updateResultTable(json);
                $("div.errors").hide();
            },

            error : function(xhr,errmsg,err) {
                console.log(xhr.status);
                $("div.results").hide();
                $("div.errors").show();
                $("div.errors").html("Error occured. Please try it again or contact administrator");
            }
        });
    };

    function updateResultTable(json) {
        var htmlBoilerplate = '<div><span class="{0}">{0}: </span><span class="{0}-val">{1}</span></div>';
        var typeSelector = "table.connectors tr.{0} td.{1} ";
        $("div.results").show();
        $.each(json, function(i, obj) {
            var cncSelector = typeSelector.format(i, "cnc");
            var cncPossible = htmlBoilerplate.format("Possible", obj.cnc.possible);
            var cncPosition = htmlBoilerplate.format("Position", obj.cnc.position);
            $(cncSelector).html("");
            $(cncSelector).append(cncPossible);
            $(cncSelector).append(cncPosition);

            var zetaSelector = typeSelector.format(i, "zeta");
            var zeta0 = htmlBoilerplate.format("0mm", obj.zeta['0mm']['possible'] + ", " + obj.zeta['0mm']['val']);
            var zeta2 = htmlBoilerplate.format("2mm", obj.zeta['2mm']['possible'] + ", " + obj.zeta['0mm']['val']);
            var zeta4 = htmlBoilerplate.format("4mm", obj.zeta['4mm']['possible'] + ", " + obj.zeta['0mm']['val']);
            $(zetaSelector).html("");
            $(zetaSelector).append(zeta0);
            $(zetaSelector).append(zeta2);
            $(zetaSelector).append(zeta4);
        });

    };

    function drawShape(num) {
        canvas.removeLayers().drawLayers();

        var model = data[num].fields;

        drawMaterial('m2', model.x2, model.y2, model.width2, model.height2);
        drawMaterial('m1', model.x1, model.y1, model.width1, model.height1);

        originX = canvas.getLayer('m2').x;
        originY = canvas.getLayer('m2').y;
    }

    function drawMaterial(name, x, y, width, height) {
        canvas.drawRect({
            layer: true, 
            name: name,
            fillStyle: '#FFF',
            strokeStyle: '#000',
            strokeWidth: 1,
            rotate: 0,
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
        var offsetY = (height - m2.height);
        canvas.setLayer('m2', {
            height: height,
            y: m2.y - offsetY,
        })
        .drawLayers(); 
        originY = originY - offsetY;
        rotateMaterial2($( "#angle input" ).val());
    }


    function rotateMaterial2(angle) {
        var m1 = canvas.getLayer('m1');
        var m2 = canvas.getLayer('m2');

        var rotationAngle = parseInt(angle) + 90;
        var translateX = m2.translateX;
        var translateY = m2.translateY;
        var newX = m2.x;
        var newY = m2.y;
        switch(actualConnection) {
            case 0:
                var alpha = angle - 90;
                var offsetX = (angle > 90) ? Math.abs(Math.sin(alpha / 180 * Math.PI)) * m2.height : 0;
                var beta = 180 - angle;
                // Precision not correct
                var offsetY = (angle > 90) ? m2.height / Math.abs(Math.sin(beta / 180 * Math.PI)) - m2.height : 0;
                translateX = -m2.width / 2;
                translateY = m2.height / 2;
                newX = originX - m2.width / 2 - offsetX;
                newY = originY + m2.height / 2 - offsetY;
                break;
            case 1:
                translateX = -m2.width / 2;
                translateY = -m2.height / 2;
                newX = originX - m2.width / 2;
                newY = originY - m2.height / 2;
                break;
            case 2:
                canvas.moveLayer('m2', 1).drawLayers();
                var a = Math.abs(90 - parseInt(angle));
                newY = originY + Math.tan(a / 180 * Math.PI) * m1.width / 2;
                break;
            case 3:
                break;
            default:
                break;
        }

        canvas.setLayer('m2', {
            rotate: rotationAngle,
            translateX: translateX,
            translateY: translateY,
            x: newX,
            y: newY
        }).drawLayers(); 
    }

    function initSituationPreview() {
        $('.connection li').hover(function(e) {
            var $target = $(e.target);
            console.info("hovered " + $target.text());
            var index = $(this).index();
            drawShape(index);
            actualConnection = index;
        });

        $('.connection a').click(function(e) {
            var targetText = $(e.target).text();
            var connector_name = $(e.target).attr("name");
            $('.connection .selected-text').html(targetText);
            $('input#connection_type').val(connector_name);
        });
    }

    function pdfGeneration() {
        $('.pdf-btn').click(function() {
            var $m1 = $('#m1 input').val();
            var $m2 = $('#m2 input').val();
            var $angle = $('#angle input').val();
            var $situation = $('#connection_type').val();
            var dataURL = canvas.get(0).toDataURL();
            var connector = $(this).closest('tr').find('td:eq(0)').text();
            var cncString = $(this).closest('tr').find('td:eq(1)').text();
            var cncPossible = cncString.split('Position')[0];
            var cncPosition = cncString.split('true' || 'false')[1];
            var zetaString = $(this).closest('tr').find('td:eq(2)').text();
            var zeta0Possible = zetaString.indexOf('0mm: true') >= 0;
            var zeta2Possible = zetaString.indexOf('2mm: true') >= 0;
            var zeta4Possible = zetaString.indexOf('4mm: true') >= 0;
            $.ajax({
            url : "pdf/",
            type : "POST",
            data : {
                csrfmiddlewaretoken: '{{ csrf_token }}',
                m1: $m1,
                m2: $m2,
                angle: $angle,
                situation: $situation,
                dataURL: dataURL,
                connector: connector,
                cncPossible: cncPossible,
                cncPosition: cncPosition,
                zeta0: zeta0Possible,
                zeta2: zeta2Possible,
                zeta4: zeta4Possible
            },

           // handle a successful response
            success: function(data) {
                var blob=new Blob([data]);
                var link=document.createElement('a');
                link.href=window.URL.createObjectURL(blob);
                link.download="Konfiguration_"+ connector + "_"+ $situation +".pdf";
                link.click();
            },

            // handle a non-successful response
            error : function() {
                console.log("Fails");
            }
        });
        })
    }
});

String.prototype.format = function() {
  var str = this;
  for (var i = 0; i < arguments.length; i++) {       
    var reg = new RegExp("\\{" + i + "\\}", "gm");             
    str = str.replace(reg, arguments[i]);
  }
  return str;
}
