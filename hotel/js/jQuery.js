<script>
	$("#custom-select").on("click",function(){
		$("#custom-select-option-box").toggle();
	});
	function toggleFillColor(obj) {
		$("#custom-select-option-box").show();
		if($(obj).prop('checked') == true) {
			$(obj).parent().css("background",'#c6e7ed');
		} else {
			$(obj).parent().css("background",'#FFF');
		}
	}
	$(".custom-select-option").on("click", function() {
		var checkboxObj = $(this).children("input");
		$(checkboxObj).prop("checked",true);
		toggleFillColor(checkboxObj);
	});
		
	$("body").on("click",function(e){
		if(e.target.id != "custom-select" && $(e.target).attr("class") != "custom-select-option") {
			$("#custom-select-option-box").hide();
		}
	});
	</script>