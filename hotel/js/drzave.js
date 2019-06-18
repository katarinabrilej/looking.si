function urediPoZvezdicah(){                 
    var elem = $("#seznam").find(".card").sort(zvezdice);
    $("#seznam").append(elem);
}

function zvezdice(a, b) {
    return a.id < b.id;
}
function zvezdice2(a, b) {
    var div1 = a.getElementsByTagName("div")[0];
    var div2 = div1.getElementsByTagName("div")[1];
    var div3 = div2.getElementsByTagName("div")[0];
    var h2 = div3.getElementsByTagName("h2")[0];
    a = h2.getElementsByTagName("a")[0]
    var div1 = b.getElementsByTagName("div")[0];
    var div2 = div1.getElementsByTagName("div")[1];
    var div3 = div2.getElementsByTagName("div")[0];
    var h2 = div3.getElementsByTagName("h2")[0];
    b = h2.getElementsByTagName("a")[0]
    if(a.textContent < b.textContent){
        return -1
    }else{return 1;} 
}

function urediPoAbecedi(){
     var elem = $("#seznam").find(".card").sort(zvezdice2);
     $("#seznam").append(elem);
}

function išči() {
    
    var input, filter, seznam, div, a, i, txtValue;
    input = document.getElementById('iskanje');
    filter = input.value.toUpperCase();
    seznam = document.getElementById("seznam");
    div = seznam.getElementsByClassName('card');

    for (i = 0; i < div.length; i++) {
        var div1 = div[i].getElementsByTagName("div")[0];
        var div2 = div1.getElementsByTagName("div")[1];
        var div3 = div2.getElementsByTagName("div")[0];
        var h2 = div3.getElementsByTagName("h2")[0];
        a = h2.getElementsByTagName("a")[0]
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
        div[i].style.display = "";
        } else {
        div[i].style.display = "none";
        }
    }
}


function zapolniSeznam(dolzina,seznam1){
    var seznam2 =[]
    for(var i = 0; i < seznam1.length; i++){
        seznam2.push(false);
    }
    return seznam2;
}

function filtriranje(pofiltriraniHoteli, cardBody, cardBodyParents, isCheckedUgodnosti){
    var pofiltriraniHoteliKoncna = [];
    var ugodnostiSo = zapolniSeznam(isCheckedUgodnosti.length,isCheckedUgodnosti);
    console.log(ugodnostiSo);
    for(hotel in pofiltriraniHoteli){
        var imaUgodnosti = true;
        for(ugodnost in isCheckedUgodnosti){
            for(i in cardBodyParents){
                if(pofiltriraniHoteli[hotel] == cardBodyParents[i]){
                    if(isCheckedUgodnosti[ugodnost] == cardBody[i]){
                        ugodnostiSo.pop();
                    }
                }
            }
        }
        if(ugodnostiSo.length == 0){
            pofiltriraniHoteliKoncna.push(pofiltriraniHoteli[hotel]);
            ugodnostiSo = zapolniSeznam(isCheckedUgodnosti.length,isCheckedUgodnosti);
        }
    }
    return pofiltriraniHoteliKoncna;
}

function filtriranje2(cardBody, cardBodyParents, isChecked){
    var pofiltriraniHoteli = [];

    for(filter in isChecked){
        for(var i = 0; i < cardBody.length; i++){
            if(isChecked[filter] == cardBody[i]){
                console.log(isChecked[filter] + " " + cardBodyParents[i])
                pofiltriraniHoteli.push(cardBodyParents[i]);
            }
        }
    }
    return pofiltriraniHoteli;

}


$(document).ready(function() {
  $('select').multipleSelect({
    selectAll: false,
    filter: true,
    filterPlaceholder: 'Najdi',
    maxHeight: 140
  });
 



    $("#potrdi").click(function(){
        var koncniHoteli = [];

        var isChecked = $(".form-check-input:checkbox:checked").map(function(){
            return $(this).val();
        }).get();
        console.log(isChecked);
        
        if(isChecked.length == 0){
            $(".card").fadeIn("slow");
            $("#nofilter").hide();
            return;
        }
        else $(".card").hide();
        
        var cardBody = $(".card-body").find("div").map(function(){
            return $(this).attr('class');
        }).get();
        console.log(cardBody);

        var cardBodyParents = $(".card-body").find("div").map(function(){
            return $(this).parent().closest('div').attr('id');
        }).get();
        console.log(cardBodyParents);

        var isCheckedZvezdice = $(".form-check-input-zvezdice:checkbox:checked").map(function(){
            return $(this).val();
        }).get();
       
        var isCheckedUgodnosti = $(".form-check-input-ugodnosti:checkbox:checked").map(function(){
            return $(this).val();
        }).get();
        
        var isCheckedNastanitev = $(".form-check-input-nastanitev:checkbox:checked").map(function(){
            return $(this).val();
        }).get();
    
        var isCheckedOkrožje = $(".form-check-input-okrožje:checkbox:checked").map(function(){
            return $(this).val();
        }).get();
        

        var isCheckedZnačilnosti = $(".form-check-input-značilnost:checkbox:checked").map(function(){
            return $(this).val();
        }).get();
        

        var isCheckedZnamenitosti = $(".form-check-input-znamenitost:checkbox:checked").map(function(){
            return $(this).val();
        }).get();
        

        var prviFilter = filtriranje2(cardBody,cardBodyParents,isChecked);
        prviFilter = [...new Set(prviFilter)];

        if(isCheckedOkrožje.length > 0){
            prviFilter = filtriranje2(cardBody,cardBodyParents,isCheckedOkrožje);
            prviFilter = [...new Set(prviFilter)];
            console.log(prviFilter + " prvi filter");
        }

        console.log(prviFilter + " prvi filter");

        var prviDrugi = prviFilter;
        if(isCheckedZnačilnosti.length > 0){
            var drugiFilter = filtriranje2(cardBody,cardBodyParents,isCheckedZnačilnosti);
            drugiFilter = [...new Set(drugiFilter)];
            console.log(drugiFilter + " drugiFilter");
            prviDrugi = prviFilter.filter(element => drugiFilter.includes(element));
        }

        console.log(prviDrugi + " prviDrugi filter");

        var prviDrugiTretji = prviDrugi;
        if(isCheckedZnamenitosti.length > 0){
            var tretjiFilter = filtriranje2(cardBody,cardBodyParents,isCheckedZnamenitosti);
            tretjiFilter = [...new Set(tretjiFilter)];
            console.log(tretjiFilter + " tretji filter");
            prviDrugiTretji = prviDrugi.filter(element => tretjiFilter.includes(element));
            
        }
        console.log(prviDrugiTretji + " prviDrugiTretji filter");

        var prviDrugiTretjiCetrti = prviDrugiTretji;
       if(isCheckedZvezdice.length > 0){
            var cetrtiFilter = filtriranje2(cardBody,cardBodyParents,isCheckedZvezdice);
            cetrtiFilter = [...new Set(cetrtiFilter)];
            console.log(cetrtiFilter + " tretji filter");
            prviDrugiTretjiCetrti = prviDrugiTretji.filter(element => cetrtiFilter.includes(element));
           
       }

       console.log(prviDrugiTretjiCetrti + " prviDrugiTretjiCetrti filter");

       var prviDrugiTretjiCetrtiPeti = prviDrugiTretjiCetrti;
       if(isCheckedNastanitev.length > 0){
            var petiFilter = filtriranje2(cardBody,cardBodyParents,isCheckedNastanitev);
            petiFilter = [...new Set(petiFilter)];
            console.log(petiFilter + " peti filter");
            prviDrugiTretjiCetrtiPeti = prviDrugiTretjiCetrti.filter(element => petiFilter.includes(element));
           
       }

       console.log(prviDrugiTretjiCetrtiPeti + " prviDrugiTretjiCetrtiPeti filter");

       koncniHoteli = filtriranje(prviDrugiTretjiCetrtiPeti,cardBody,cardBodyParents,isCheckedUgodnosti);
       if(koncniHoteli.length == 0){
            $("#nofilter").fadeIn("slow");
       }
        
        for(var i = 0; i < koncniHoteli.length;i++){
            $("#nofilter").hide();
            $( '.'+koncniHoteli[i] ).fadeIn("slow");
        }
        
    });
        
  

});
