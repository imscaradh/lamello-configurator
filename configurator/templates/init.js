$(function () {

    // -----------------------------------------------
    // 			function calls and configuration
    // -----------------------------------------------
    var data = {{ connection_types_json|safe }};
    var canvas = $("#connectionPreview");
    var resultJson = null;
    var model;

    var actualConnection = -1;

    $.jCanvas.defaults.fromCenter = false;
    var fillStyle = '#f2e8dd';
    var strokeStyle = '#000';
    var minAngle = parseInt($("#angle input").attr("min"));
    var maxAngle = parseInt($("#angle input").attr("max"));

    // functions called on page load
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

    var originHeight;
    function initCanvas() {
        var ctx = ctx = canvas[0].getContext('2d');
        ctx.canvas.width = $(".preview").width();
        originHeight = $(".preview").height();
        ctx.canvas.height = originHeight;
    }

    function resizeCanvas(height) {
        var ctx = ctx = canvas[0].getContext('2d');
        ctx.canvas.height = originHeight + height;
        canvas.drawLayers();
    }

    function initFormActions() {
        var m1_input = 40;
        var m2_input = 40;

        $( "#m1 input" ).on('input', function() {
            m2_input = $("#m2 input").val();
            if(m2_input == m1_input) {
                m2_input = $(this).val();
                $("#m2 input").val(m2_input); 
                scaleMaterial2(m2_input);
            }
            m1_input = $(this).val()
                scaleMaterial1(m1_input);
        });

        $( "#m2 input" ).on('input', function() {
            m2_input = $(this).val()
                scaleMaterial2(m2_input);
        });

        $( "#angle input" ).on('input', function() {
            var angle = $(this).val();
            if(minAngle <= angle && angle <= maxAngle) {
                $("div.errors").html("");
                rotateMaterial(angle);
            } else {
                $("div.errors").html("Angle must be between 40 and 140 degreees");
            }
        });

        $('.connection li').hover(function(e) {
            var $target = $(e.target);
            console.info("hovered " + $target.text());
            actualConnection = $(this).index();
            drawShape();
        });

        $('.connection a').click(function(e) {
            var targetText = $(e.target).text();
            var connector_name = $(e.target).attr("name");
            $('.connection .selected-text').html(targetText);
            $('input#connection_type').val(connector_name);
        });

        $("div.unit input[name='unit']").change(function(e) {		
            var unit = $(e.target).val();
            $("span.lbl.unit").html(unit);		

            m1_input = (unit == "mm") ? m1_input * 25.4 : m1_input / 25.4;
            $("#m1 input").val(m1_input.toFixed(2));
            m2_input = (unit == "mm") ? m2_input * 25.4 : m2_input / 25.4;
            $("#m2 input").val(m2_input.toFixed(2));
        });
    }

    function initFormSubmitActions() {
        // Submit post on submit
        $('#calculationForm').on('submit', function(event){
            event.preventDefault();
            if(actualConnection != -1) {
                create_post();
                $("div.errors").html("");  
            } else {
                $("div.errors").html("Please provide a connection!");
            }
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
        var typeSelector = "div.sec-{0} td.{1} ";
        $("div.results").show();
        $.each(json, function(i, obj) {
            var cncSelector = typeSelector.format(i, "cnc");
            var cncPossible = htmlBoilerplate.format("Possible", obj.cnc.possible);
            var cncPosition = htmlBoilerplate.format("Position", obj.cnc.position.toFixed(2));
            $(cncSelector).html("");
            $(cncSelector).append(cncPossible);
            $(cncSelector).append(cncPosition);

            var zetaSelector = typeSelector.format(i, "zeta");
            var zeta0 = htmlBoilerplate.format(" 0mm", obj.zeta['0mm']['possible'] + ", " + obj.zeta['0mm']['val'][0].toFixed(2));
            var zeta2 = htmlBoilerplate.format(" 2mm", obj.zeta['2mm']['possible'] + ", " + obj.zeta['2mm']['val'][0].toFixed(2));
            var zeta4 = htmlBoilerplate.format(" 4mm", obj.zeta['4mm']['possible'] + ", " + obj.zeta['4mm']['val'][0].toFixed(2));
            $(zetaSelector).html("");
            $(zetaSelector).append(zeta0);
            $(zetaSelector).append(zeta2);
            $(zetaSelector).append(zeta4);
        });

    };

    function drawShape() {
        canvas.removeLayers().drawLayers();

        model = data[actualConnection].fields;

        if(model.height3 != 0) { drawMaterial('m3', model.x3, model.y3, model.width3, model.height3); }
        if(model.height2 != 0) { drawMaterial('m2', model.x2, model.y2, model.width2, model.height2); }
        if(model.height1 != 0) { drawMaterial('m1', model.x1, model.y1, model.width1, model.height1); }

        rotateMaterial($( "#angle input" ).val());
    }

    function drawMaterial(name, x, y, width, height) {
        canvas.drawRect({
            layer: true, 
            name: name,
            fillStyle: fillStyle,
            strokeStyle: strokeStyle,
            strokeWidth: 1,
            rotate: 0,
            x: x, 
            y: y,
            width: width,
            height: height 
        });
    }

    function drawText(material) {
        var m = canvas.getLayer(material);
        var m2Xoffset = (material != 'm1') ? Math.cos(($( "#angle input" ).val() - 90) / 180 * Math.PI) * m.width + 30 : m.width + 10;
        var m2Yoffset = (material != 'm1') ? Math.sin(($( "#angle input" ).val() - 90) / 180 * Math.PI) * m.width : 0;
        var layerName = material + "-text";
        canvas.removeLayer(layerName).drawLayers();
        canvas.drawText({
            layer: true,
            name: layerName,
            fillStyle: strokeStyle,
            strokeWidth: 2,
            x: m.x - m.translateX + m2Xoffset, 
            y: m.y - m.translateY + m2Yoffset + m.height / 2 - 8,
            fontSize: 16,
            fontFamily: 'Verdana, sans-serif',
            text: (material == 'm1') ? 'a' : 'b'
        }).drawLayers();
    }

    function scaleMaterial1(width) {
        var m1 = canvas.getLayer('m1');
        var newX = (actualConnection < 2) ? m1.x - (width - m1.width) : m1.x - (width - m1.width) / 2;

        canvas.setLayer('m1', {
            width: width,
            x: newX 
        }).drawLayers(); 
        model.x1 = m1.x;
        drawText('m1');
    }

    function scaleMaterial2(height) {
        var m2 = canvas.getLayer('m2');

        var newY = 0;
        switch (actualConnection) {
            case 0:
                newY = model.y2 - (height - m2.height); 
                break;
            case 1:
                newY = model.y2;
                break;
            case 2:
                newY = model.y2 - (height - m2.height); 
                break;
            case 3:
                newY = m2.y - (height - m2.height);
                var m3 = canvas.getLayer('m3');
                var newX3 = m3.y - (height - m3.height);
                canvas.setLayer('m3', {
                    height: height,
                    y: newY
                })
                .drawLayers(); 
                model.y3 = m3.y;
                break;
        }

        canvas.setLayer('m2', {
            height: height,
            y: newY
        })
        .drawLayers(); 

        model.y2 = m2.y;
        model.height2 = height;
        rotateMaterial($( "#angle input" ).val());
        drawText('m2');
    }


    function rotateMaterial(angle) {
        var m1 = canvas.getLayer('m1');
        var m2 = canvas.getLayer('m2');
        var m3 = canvas.getLayer('m3');

        var rotationAngle = parseInt(angle) + 90;
        var translateX = m2.translateX;
        var translateY = m2.translateY;
        var newX = m2.x;
        var newY = m2.y;
        switch(actualConnection) {
            case 0:
                var alpha = angle - 90;
                var beta = 180 - angle;
                translateX = -m2.width / 2;
                translateY = (angle > 90) ? -m2.height / 2 : m2.height / 2;
                newX = model.x2 - m2.width / 2;
                newY = (angle > 90) ? 
                    m1.y + m1.height - m2.height / Math.cos(alpha / 180 * Math.PI) -m2.height / 2 : 
                    model.y2 + m2.height / 2;
                break;
            case 1:
                translateX = -m2.width / 2;
                translateY = -m2.height / 2;
                newX = model.x2 - m2.width / 2;
                newY = model.y2 - m2.height / 2;

                drawBisecConnectorHelpers(angle, m1, m2);
                break;
            case 2:
                canvas.moveLayer('m2', 1).drawLayers();
                var a = Math.abs(90 - parseInt(angle));
                newY = model.y2 + Math.tan(a / 180 * Math.PI) * m1.width / 2;
                break;
            case 3:
                // TODO: Prevent edge displaying
                translateX = model.x1 - (model.x2 + model.width2 / 2);
                newX = model.x2 + translateX;
                canvas.setLayer('m3', {
                    rotate: rotationAngle,
                    translateX: -translateX,
                    x: model.x3 - translateX,
                    y: model.y3
                }).drawLayers(); 
                drawText('m3');
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

        var height = m2.width * Math.sin((angle -90) / 180 * Math.PI);
        if (height > 0 || (actualConnection == 1 && angle < 90)) {
            resizeCanvas(Math.abs(height));
        } else {
            resizeCanvas(0);
        }
        drawText('m1');
        if (actualConnection != 3) drawText('m2');
    }

    function drawBisecConnectorHelpers(angle, m1, m2) {
        var alpha = (180 - angle) / 2;
        var y2 = m1.y + m1.height + Math.tan(alpha / 180 * Math.PI) * m2.height;

        var beta = angle - 90;
        var x3 = model.x2 - Math.sin(beta / 180 * Math.PI) * m2.height;
        var y3 = model.y2 + Math.cos(beta / 180 * Math.PI) * m2.height;

        canvas.removeLayer('bisec-helpers').drawLayers();
        canvas.removeLayer('bisec').drawLayers();
        canvas.removeLayer('bisec-hidem1').drawLayers();
        canvas.removeLayer('bisec-hidem2').drawLayers();
        // Draw to lines here
        canvas.drawLine({
            layer: true,
            name: 'bisec-helpers',
            fillStyle: fillStyle,
            strokeStyle: strokeStyle,
            strokeWidth: 1,
            closed: true,
            x1: m1.x,       y1: m1.y + m1.height,
            x2: m1.x,       y2: y2,
            x3: x3,         y3: y3,
            x4: model.x2,   y4:model.y2 
        });
        canvas.drawLine({
            layer: true,
            name: 'bisec',
            strokeStyle: strokeStyle,
            strokeWidth: 1.2,
            x1: m1.x,       y1: y2,
            x2: model.x2,   y2: model.y2 
        });
        // Hide rect ends
        canvas.drawLine({
            layer: true,
            name: 'bisec-hidem1',
            strokeStyle: fillStyle,
            strokeWidth: 2,
            x1: m1.x + 1,   y1: m1.y + m1.height,
            x2: model.x2 - 1,   y2: model.y2 
        });

        var x2 = model.x2 - Math.sin(beta / 180 * Math.PI) * (m2.height-1);
        var y2 = model.y2 + Math.cos(beta / 180 * Math.PI) * (m2.height-1);
        canvas.drawLine({
            layer: true,
            name: 'bisec-hidem2',
            strokeStyle: fillStyle,
            strokeWidth: 3,
            x1: model.x2,   y1: model.y2,
            x2: x2,         y2: y2 
        });
        canvas.moveLayer('bisec', 999).drawLayers();
    }


    function pdfGeneration() {
        $('.pdf-btn').click(function() {
            var $m1 = $('#m1 input').val();
            var $m2 = $('#m2 input').val();
            var unit = $('span.lbl.unit').text();
            unit = (unit == null ? "mm" : unit.substr(0, 2));
            var $angle = $('#angle input').val();
            var $situation = $('#connection_type').val();
            var dataURL = canvas.get(0).toDataURL();
            var connector = $(this).closest('tr').find('td:eq(0)').text();
            var cncString = $(this).closest('tr').find('td:eq(1)').text();
            var cncPossible = (cncString.indexOf('Possible: true') >= 0 ? "Yes" : "No");
            var cncPosition = cncString.split('true' || 'false')[1];
            cncPosition = (cncPosition == null ? "0" : cncPosition.substring(10,18));
            var zetaString = $(this).closest('tr').find('td:eq(2)').text();
            console.log("zeta: " + zetaString);
            var reg = /\b(\d+\.\d+)/g;
            var matches = getMatches(zetaString, reg, 1);
            console.log(matches);
            var zeta0Possible = (zetaString.indexOf('0mm: true') >= 0 ? "Yes" : "No");
            var zeta2Possible = (zetaString.indexOf('2mm: true') >= 0 ? "Yes" : "No");
            var zeta4Possible = (zetaString.indexOf('4mm: true') >= 0 ? "Yes" : "No");
            var zeta0a = (zeta0Possible == "Yes" ? matches[0] : "0");
            var zeta0b = 0; //(zeta0Possible == "Yes" ? zetaVal[2].substr(0, 8) : "0");
            var zeta2a = (zeta2Possible == "Yes" ? matches[1] : "0");
            var zeta2b = 0; //(zeta2Possible == "Yes" ? zetaVal[4].substr(0, 8) : "0");
            var zeta4a = (zeta4Possible == "Yes" ? matches[2] : "0");
            var zeta4b = 0; //(zeta4Possible == "Yes" ? zetaVal[6].substr(0, 8) : "0");
            console.log("m1: " + $m1);
            console.log("m2: " + $m2);
            console.log("unit:" + unit);
            console.log("angle: " + $angle);
            console.log("situation: " + $situation);
            console.log("b64String: " + dataURL);
            console.log("connector: " + connector);
            console.log("cnc: " + cncString);
            console.log("cnc: " + cncPossible);
            console.log("cnc: " + cncPosition);
            console.log("0mm: " + zeta0Possible);
            console.log("2mm: " + zeta2Possible);
            console.log("4mm: " + zeta4Possible);
            $.ajax({
                url : "pdf/",
                type : "POST",
                data : {
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    m1: $m1,
                    m2: $m2,
                    unit: unit,
                    angle: $angle,
                    situation: $situation,
                    dataURL: dataURL,
                    connector: connector,
                    cncPossible: cncPossible,
                    cncPosition: cncPosition,
                    zeta0: zeta0Possible,
                    zeta2: zeta2Possible,
                    zeta4: zeta4Possible,
                    zeta0a: zeta0a,
                    zeta0b: zeta0b,
                    zeta2a: zeta2a,
                    zeta2b: zeta2b,
                    zeta4a: zeta4a,
                    zeta4b: zeta4b
                },

                // handle a successful response
                success: function(data) {
                    var blob=new Blob([data]);
                    var link=document.createElement('a');
                    link.href=window.URL.createObjectURL(blob);
                    link.download="Configuration_"+ $situation +".pdf";
                    link.click();
                },

                // handle a non-successful response
                error : function() {
                    console.log("Fails");
                }
            });
        })
    }

    function getMatches(string, regex, index) {
        index || (index = 1); // default to the first capturing group
        var matches = [];
        var match;
        while (match = regex.exec(string)) {
            matches.push(match[index]);
        }
        return matches;
    }

    function searchPos(inputstr) {
        matches = reg.exec(inputstr);
        return matches;
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
