$(function () {

    // -----------------------------------------------
    // 			function calls and configuration
    // -----------------------------------------------
    var data = {{ connection_types_json|safe }};
    var canvas = $("#connectionPreview");
    var resultJson = null;
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
            var connector_name = $(e.target).attr("name");
            $('.connection .selected-text').html(targetText);
            $('input#connection_type').val(connector_name);
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
            var dataURL = canvas.get(0).toDataURL();
            console.log("b64String: " + dataURL);
            var connector = $(this).closest('tr').find('td:eq(0)').text();
            console.log("connector: " + connector);
            var cncString = $(this).closest('tr').find('td:eq(1)').text();
            var cncPossible = cncString.split('Position')[0];
            var cncPosition = cncString.split('true' || 'false')[1];
            console.log("cnc: " + cncString);
            console.log("cnc: " + cncPossible);
            console.log("cnc: " + cncPosition);
            var zetaString = $(this).closest('tr').find('td:eq(2)').text();
            var zeta0Possible = zetaString.indexOf('0mm: true') >= 0;
            var zeta2Possible = zetaString.indexOf('2mm: true') >= 0;
            var zeta4Possible = zetaString.indexOf('4mm: true') >= 0;
            console.log("zeta: " + zetaString);
            console.log("0mm: " + zeta0Possible);
            console.log("zeta: " + zeta2Possible);
            console.log("zeta: " + zeta4Possible);
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
