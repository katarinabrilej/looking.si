$(document).ready(function() {
        var $this = $('.dodaj-komentar');
        var $window = $(window);
        var $from = $("#hotel-podrobnosti"); 
        var $startPos = $from.offset().top + $from.height();
       $window.on('scroll', function(){
            if ($window.scrollTop() >= $startPos) { 
                console.log("prva " +$startPos)
                $this.css({
                    position: 'sticky',
                    top: '100px', 
                });
            } 
        })
        var črta = $(".vl");
        črta.css({
            height: $(".card-komentar").height(),
        })
})