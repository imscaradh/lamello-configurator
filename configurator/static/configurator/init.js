$(function () {
    $('.connection a').hover(function(e) {
	var $target = $(e.target);
	console.info("hovered " + $target.text());
	$(".preview").html($target.text());
    });

    $('.connection a').click(function(e) {
	$('.connection .selected-text').html($(e.target).text());
    });

    function isConnectionPossible(m1, m2, angle) {
	console.info("Material 1: " + m1);
	console.info("Material 2: " + m2);
	console.info("Angle: " + angle);

	//TODO: Calculation
    }
});
