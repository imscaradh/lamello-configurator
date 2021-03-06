$(function () {

    // -----------------------------------------------
    // 			function calls and configuration
    // -----------------------------------------------
    var canvas = $("#connectionPreview");
    var resultJson = null;
    var dataModel;
    var actualConnection = -1;
    var fillStyle = '#e6ca9b';
    var strokeStyle = '#3e3e3e';
    var minAngle = parseInt($("#angle input").attr("min"));
    var maxAngle = parseInt($("#angle input").attr("max"));
    var unit = 'mm';
    $.jCanvas.defaults.fromCenter = false;

    // functions called on page load
    initCanvas();
    initFormActions();
    initFormSubmitActions();
    pdfGeneration();

    // Call function(s) on window resize. This is used to recalculate the canvas.
    $( window ).resize(function() {
        initCanvas();
    });


    // -----------------------------------------------
    // 			function declarations	
    // -----------------------------------------------

    var originHeight;

    /**
     * Initialisation of the Canvas with the height and width of the div in the index.html
     */
    function initCanvas() {
        var ctx = ctx = canvas[0].getContext('2d');
        ctx.canvas.width = $(".preview").width();
        originHeight = $(".preview").height();
        ctx.canvas.height = originHeight;
    }

    /**
     * When the pagesize or the situationimage changes, this function will resize the canvas
     * @param height: the value of the change
     */
    function resizeCanvas(height) {
        var ctx = ctx = canvas[0].getContext('2d');
        ctx.canvas.height = originHeight + height;
        canvas.drawLayers();
    }

    /**
     * calls the drawMaterial for drawing the sitution on the canvas. This is done for each 3 parts
     * of the situation preview if there are 3 configured. After loading, a rotation will be performed
     * (to fit the case if we switch from one situation to another)
     */
    function drawShape() {
        canvas.removeLayers().drawLayers();

        var data = {{ connection_types_json|safe }};
        dataModel = data[actualConnection].fields;

        if(dataModel.height3 != 0) { drawMaterial('m3', dataModel.x3, dataModel.y3, dataModel.width3, dataModel.height3); }
        if(dataModel.height2 != 0) { drawMaterial('m2', dataModel.x2, dataModel.y2, dataModel.width2, dataModel.height2); }
        if(dataModel.height1 != 0) { drawMaterial('m1', dataModel.x1, dataModel.y1, dataModel.width1, dataModel.height1); }

        rotateMaterial($( "#angle input" ).val());
    }

    /**
     * Draws a rectangle on the canvas with the parameters below. A new layer will be created
     * to modify the rectangle easily.
     *
     * @param name: The layer-name
     * @param x: The x position in the canvas
     * @param y: The y position in the canvas
     * @param width: The width of rectangle to draw
     * @param height: The height of the rectangle to draw
     */
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

    /**
     * calculates the position of the variables "a" and "b" in the sitationimage. Here we have more complex calculations
     * for the b label: Because the rotation modifies the material with the b label, we have to transform this too. 
     * This is done with sin and cos functions, but it's not very nice at the moment (x and y positions are not in the middle
     * of the left-middle side of the rect). The two labels are layered analogous to the rectangles.
     *
     * @param material: Material name (is used for layering)
     */
    function drawText(material) {
        var m = canvas.getLayer(material);
        var angle = $("#angle input").val();

        var xOffset = 0;
        var yOffset = 0;
        if (material != 'm1' && actualConnection != 2) {
            xOffset = Math.cos((angle - 90) / 180 * Math.PI) * (m.width / 4);
            yOffset = Math.sin((angle - 90) / 180 * Math.PI) * (m.width / 4) + m.height / 4;
        } else {
            xOffset = m.width / 2 - 6;
            yOffset = m.height / 2 - 7;
        }
        var layerName = material + "-text";
        canvas.removeLayer(layerName).drawLayers();
        canvas.drawText({
            layer: true,
            name: layerName,
            fillStyle: strokeStyle,
            strokeWidth: 1,
            x: m.x - m.translateX + xOffset,
            y: m.y - m.translateY + yOffset,
            fontSize: 14,
            fontFamily: 'Verdana, sans-serif',
            text: (material == 'm1') ? 'a' : 'b'
        }).drawLayers();
    }

    /**
     * calculates the new position of x to scale the material m1 with the parameter width
     *
     * @param width: The new width of material 1
     */
    function scaleMaterial1(width) {
        var m1 = canvas.getLayer('m1');
        var newX = (actualConnection < 2) ? m1.x - (width - m1.width) : m1.x - (width - m1.width) / 2;

        canvas.setLayer('m1', {
            width: width,
            x: newX 
        }).drawLayers(); 
        dataModel.x1 = m1.x;
        drawText('m1');
    }

    /**
     * calculates the new position of y to scale the material m2 with the parameter height
     *
     * @param height: The new material 1 height
     */
    function scaleMaterial2(height) {
        var m2 = canvas.getLayer('m2');

        var newY = 0;
        // each situation has another calcultion for the y coordinate of the second material
        switch (actualConnection) {
            // Stumb edge: Because we have to scale "away" from the bottom-side of the rectangle,
            // we have to do some maths
            case 0:
                newY = dataModel.y2 - (height - m2.height); 
                break;
            // Bisectrix: The scaling does not need a special y coordinate
            case 1:
                newY = dataModel.y2;
                break;
            // T-connection: Because we are scaling "away+ from the bottom-side of the rectangle,
            // we have to do some maths
            case 2:
                newY = dataModel.y2 - (height - m2.height); 
                break;
            // Miter: Here we have a very special case, because there are 2 rectangles to scale.
            // Moreover we have to calculate a new y coordinate because we scale "away" from the
            // bottom-side of the rectangle.
            case 3:
                newY = m2.y - (height - m2.height);
                var m3 = canvas.getLayer('m3');
                var newX3 = m3.y - (height - m3.height);
                canvas.setLayer('m3', {
                    height: height,
                    y: newY
                })
                .drawLayers(); 
                dataModel.y3 = m3.y;
                break;
        }

        // Perform the scaling
        canvas.setLayer('m2', {
            height: height,
            y: newY
        })
        .drawLayers(); 

        // To display the oder stuff correctly, we have to perform a rotation and redraw the text
        // label for material 2
        dataModel.y2 = m2.y;
        dataModel.height2 = height;
        rotateMaterial($( "#angle input" ).val());
        drawText('m2');
    }

    /**
     * calculates the new positions of x and y after the rotation around the angle. 
     * @param angle: The input angle which should be displayed in the preview
     */
    function rotateMaterial(angle) {
        var m1 = canvas.getLayer('m1');
        var m2 = canvas.getLayer('m2');
        var m3 = canvas.getLayer('m3');

        var rotationAngle = parseInt(angle) + 90;
        var translateX = m2.translateX;
        var translateY = m2.translateY;
        var newX = m2.x;
        var newY = m2.y;

        // each situation has another calcultion for the rotation
        switch(actualConnection) {
            // Stumb edge: We have to perform a rotation on the top-left corner. This is possible if we
            // translate the rotation point from the middle to the top-left. This will be the case if
            // the angle if bigger than 90 degrees. If it's lower, then we have to rotate around the 
            // bottom-left corner.
            case 0:
                var alpha = angle - 90;
                var beta = 180 - angle;
                translateX = -m2.width / 2;
                translateY = (angle > 90) ? -m2.height / 2 : m2.height / 2;
                newX = dataModel.x2 - m2.width / 2;
                newY = (angle > 90) ? 
                    m1.y + m1.height - m2.height / Math.cos(alpha / 180 * Math.PI) -m2.height / 2 : 
                    dataModel.y2 + m2.height / 2;
                break;
            // Bisectrix: For the bisectix the rotation will be performed on the top-left corner of m2. 
            case 1:
                translateX = -m2.width / 2;
                translateY = -m2.height / 2;
                newX = dataModel.x2 - m2.width / 2;
                newY = dataModel.y2 - m2.height / 2;

                drawBisecConnectorHelpers(angle, m1, m2);
                break;
            // T-connection: The t-connection rotation will be peformed on the middle-bottom side of 
            // material 2.
            case 2:
                canvas.moveLayer('m2', 1).drawLayers();
                var a = Math.abs(90 - parseInt(angle));
                newY = dataModel.y2 + Math.tan(a / 180 * Math.PI) * m1.width / 2;
                break;
            // Miter: Because we are using two rectangles for representation of material 2, the 
            // rotation is a bit more complex. The rotation is performed on the bottom-middle side.
            case 3:
                translateX = dataModel.x1 - (dataModel.x2 + dataModel.width2 / 2);
                newX = dataModel.x2 + translateX;
                canvas.setLayer('m3', {
                    rotate: rotationAngle,
                    translateX: -translateX,
                    x: dataModel.x3 - translateX,
                    y: dataModel.y3
                }).drawLayers(); 
                drawText('m3');
                break;
            default:
                break;
        }

        // Draw the new m2 with the calculated values from above
        canvas.setLayer('m2', {
            rotate: rotationAngle,
            translateX: translateX,
            translateY: translateY,
            x: newX,
            y: newY
        }).drawLayers(); 

        //if the new height of m2 bigger than the old canvas size, the canvas must be resize
        var height = m2.width * Math.sin((angle -90) / 180 * Math.PI);
        if (height > 0 || (actualConnection == 1 && angle < 90)) {
            resizeCanvas(Math.abs(height));
        } else {
            resizeCanvas(0);
        }
        drawText('m1');
        if (actualConnection != 3) drawText('m2');
    }

    /**
     * Helper function to draw additional lines for the bisectrix connection-type.
     *
     * @param angle: The actual angle of bisectrix configuration
     * @param m1: Material 1 selector
     * @param m2: Material 2 selector
     */
    function drawBisecConnectorHelpers(angle, m1, m2) {
        var alpha = (180 - angle) / 2;
        var y2 = m1.y + m1.height + Math.tan(alpha / 180 * Math.PI) * m2.height;

        var beta = angle - 90;
        var x3 = dataModel.x2 - Math.sin(beta / 180 * Math.PI) * m2.height;
        var y3 = dataModel.y2 + Math.cos(beta / 180 * Math.PI) * m2.height;

        // Remove all the helper lines first
        canvas.removeLayer('bisec-helpers').drawLayers();
        canvas.removeLayer('bisec').drawLayers();
        canvas.removeLayer('bisec-hidem1').drawLayers();
        canvas.removeLayer('bisec-hidem2').drawLayers();

        // Draw the connection from the bottom-left edge of m1 to the 
        // bottom-left edge of m2. To allow to fill the materials with 
        // a specified color, we are closing this lines
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
            x4: dataModel.x2,   y4:dataModel.y2 
        });

        // This line is the bisectrix itselfs (connection between the two materials)
        canvas.drawLine({
            layer: true,
            name: 'bisec',
            strokeStyle: strokeStyle,
            strokeWidth: 1.2,
            x1: m1.x,       y1: y2,
            x2: dataModel.x2,   y2: dataModel.y2 
        });

        // The following two lines are a workaround to hide the rectangle ends.
        canvas.drawLine({
            layer: true,
            name: 'bisec-hidem1',
            strokeStyle: fillStyle,
            strokeWidth: 2,
            x1: m1.x + 0.6,   y1: m1.y + m1.height,
            x2: dataModel.x2 - 0.6,   y2: dataModel.y2 
        });

        var x2 = dataModel.x2 - Math.sin(beta / 180 * Math.PI) * (m2.height-0.6);
        var y2 = dataModel.y2 + Math.cos(beta / 180 * Math.PI) * (m2.height-0.6);
        canvas.drawLine({
            layer: true,
            name: 'bisec-hidem2',
            strokeStyle: fillStyle,
            strokeWidth: 3,
            x1: dataModel.x2,   y1: dataModel.y2,
            x2: x2,         y2: y2 
        });
        canvas.moveLayer('bisec', 999).drawLayers();
    }

    /**
     * Aggregation of all input form actions
     */
    function initFormActions() {

        // To prevent conversion inches <-> mm based on rounded values,
        // we are storing the whole floating-point number as variables.
        var m1_input = 40.00;
        var m2_input = 40.00;

        // This offset can be used to display the canvas situation preview 
        // smaller or bigger than the real inputs for the material height/width
        var realityOffset = 10;

        var angleSelector = $("#angle input");
        var m1Selector = $("#m1 input");
        var m2Selector = $("#m2 input");


        /*
         * This helper function is used to convert the input value
         * into a useful value to perform the canvas updates
         */
        function getValueToScale(value) {
            var result = parseInt(value) + realityOffset;
            if (unit != 'mm') {
                result *= 25.4;
            }
            return result;
        };

        /*
         * Here we are catching material 1 changes. To prevent the usage of
         * a checkbox which allows to configure if the materials are of the same
         * size, the material 2 input textfield is bind to the material 1 input
         * textfield until there will be another value filled up into the material
         * 2 input textfield.
         */
        m1Selector.on('input', function() {
            if ($(this).val() > 0) {   
                m2_input = m2Selector.val();
                if (m2_input == m1_input || actualConnection == 1) {
                    m2_input = $(this).val();
                    m2Selector.val(m2_input); 
                    scaleMaterial2(getValueToScale(m2_input));
                }
                m1_input = $(this).val();
                scaleMaterial1(getValueToScale(m1_input));
                rotateMaterial(angleSelector.val());
            }
        });

        /*
         * Here we are chatching material 2 changes. It works similiar to material 1 changes
         * with the difference that we are not stiching this field to another.
         */
        m2Selector.on('input', function() {
            if ($(this).val() > 0) {   
                m2_input = $(this).val();
                scaleMaterial2(getValueToScale(m2_input));
                rotateMaterial(angleSelector.val());
            }
        });

        /*
         * Here we are catching angle changes. It performs some basic validation and rotate
         * the material 2 afterward.
         */
        angleSelector.on('input', function() {
            var angle = $(this).val();
            if(minAngle <= angle && angle <= maxAngle) {
                $("div.errors").html("");
                rotateMaterial(angle);
            } else {
                $("div.errors").html("Angle must be between 40 and 140 degreees");
            }
        });

        /*
         * This method redraws the canvas according to the hovered situation.
         */
        $('.connection li').hover(function(e) {
            // TODO: Catch key press
            var $target = $(e.target);
            console.info("hovered " + $target.text());
            actualConnection = $(this).index();
            drawShape();
        });

        /*
         * This method applies the selection (workaround to use the predefined dropdown-menu,
         * which is no official html-input field
         */
        $('.connection a').click(function(e) {
            var targetText = $(e.target).text();
            var connector_name = $(e.target).attr("name");
            $('.connection .selected-text').html(targetText);
            $('input#connection_type').val(connector_name);
        });

        /*
         * Here we are listen if the unit is going to changed. The action call performs the 
         * conversion and updates the input fields immediately.
         */
        $("div.unit input[name='unit']").change(function(e) {		
            unit = $(e.target).val();
            $("span.lbl.unit").html(unit);		

            m1_input = (unit == "mm") ? m1_input * 25.4 : m1_input / 25.4;
            $("#m1 input").val(m1_input.toFixed(2));
            m2_input = (unit == "mm") ? m2_input * 25.4 : m2_input / 25.4;
            $("#m2 input").val(m2_input.toFixed(2));
        });
    }

    /**
     * Initialisation of the form submit. When click the button it calls the function create_post to send data
     * for calculation
     */
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

    /**
     * creates the post for the ajax call and send it to the calculation. If the call was successfull, 
     * We are going to fillup the html table with the calculated results (sent as json)
     */
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

    /**
     * When calculated a situation, this function update the result Table in the Configurator.
     * @param json: Json with the results
     */
    function updateResultTable(json) {
        var typeSelector = "div.sec-{0} td.{1} ";
        $("div.results").show();
        $.each(json, function(i, obj) {
            var cncSelector = typeSelector.format(i, "cnc");
            var cncPossible = obj.cnc.possible;
            var cncPosition = obj.cnc.position.toFixed(2);
            $(cncSelector + ".cnc-possible").html(cncPossible + '');
            $(cncSelector + ".cnc-val").html(cncPosition);

            for (j = 0; j <= 4; j+=2) {
                var zetaSelector = typeSelector.format(i, "zeta");
                var zetaPossible = obj.zeta[j + 'mm']['possible'];
                var zetaVal1 = obj.zeta[j + 'mm']['val'][0].toFixed(2);
                var zetaVal2 = obj.zeta[j + 'mm']['val'][1].toFixed(2);

                $(zetaSelector + ".pl-"+j+"mm td.possible").html(zetaPossible + '');
                $(zetaSelector + ".pl-"+j+"mm td.a").html(zetaVal1);
                $(zetaSelector + ".pl-"+j+"mm td.b").html(zetaVal2);
            }
        });
    }


    /**
     * This function get all datas for the PDF generation. These datas were send by a ajax call to the pdf service. 
     * When the call was successful it will save the PDF-Document. 
     */
    function pdfGeneration() {
        $('.pdf-btn').click(function(e) {
            var m1 = $('#m1 input').val();
            var m2 = $('#m2 input').val();
            var unit = $('span.lbl.unit').text();
            var angle = $('#angle input').val();
            var situation = $('#connection_type').val();
            var dataURL = canvas.get(0).toDataURL();

            var connectorToExport = $(e.target).attr('name');
            var section = $("div.sec-" + connectorToExport);

            var cncPossible = section.find("td.cnc .cnc-possible").html() == "true" ? "Yes" : "No";
            var cncPosition = section.find("td.cnc .cnc-val").html();

            var zeta0Possible = section.find("td.zeta tr.pl-0mm td.possible").html() == "true" ? "Yes" : "No";
            var zeta2Possible = section.find("td.zeta tr.pl-2mm td.possible").html() == "true" ? "Yes" : "No";
            var zeta4Possible = section.find("td.zeta tr.pl-4mm td.possible").html() == "true" ? "Yes" : "No";
            var zeta0a = section.find("td.zeta tr.pl-0mm td.a").html();
            var zeta0b = section.find("td.zeta tr.pl-0mm td.b").html();
            var zeta2a = section.find("td.zeta tr.pl-2mm td.a").html();
            var zeta2b = section.find("td.zeta tr.pl-2mm td.b").html();
            var zeta4a = section.find("td.zeta tr.pl-4mm td.a").html();
            var zeta4b = section.find("td.zeta tr.pl-4mm td.b").html();

            var data_json = {
                csrfmiddlewaretoken: '{{ csrf_token }}',
                m1: m1,
                m2: m2,
                unit: unit,
                angle: angle,
                situation: situation,
                dataURL: dataURL,
                connector: connectorToExport,
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
            };
            console.debug(data_json);

            $.ajax({
                url : "pdf/",
                type : "POST",
                data : data_json,

                success: function(data) {
                    var blob=new Blob([data]);
                    var link=document.createElement('a');
                    link.href=window.URL.createObjectURL(blob);
                    link.download="Configuration_"+ situation +".pdf";
                    link.click();
                },

                error : function() {
                    console.log("Fails");
                }
            });
        })
    }
});

/**
 * This prototype definition is an improvemnt to use a format method for strings like known in Java or C
 */
String.prototype.format = function() {
    var str = this;
    for (var i = 0; i < arguments.length; i++) {       
        var reg = new RegExp("\\{" + i + "\\}", "gm");             
        str = str.replace(reg, arguments[i]);
    }
    return str;
}
