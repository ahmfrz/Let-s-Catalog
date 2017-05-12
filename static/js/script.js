$(".dropdown").hover(function() {
    $(this).addClass("open");
}, function() {
    $(this).removeClass("open");
});

$("#navbar li").hover(function() {
        $(this).addClass("active");
    },
    function() {
        $(this).removeClass("active");
    });

function loadData() {
    // var categoryURL = "http://localhost:8000/catalog/categories.json";
    var $nav_Categories = $("#nav-categories");
    var $nav_SubCategories = $("#nav-subCategories");
    var $nav_Brands = $("#nav-brands");

    var catTimeout = setTimeout(function() {
        $nav_Categories.text("Failed to get Category resources");
    }, 8000);

    var catalogURL = "http://localhost:8000/catalog.json";
    $.ajax({
        url: catalogURL,
        dataType: 'json',
        crossDomain: false,
        success: function(data) {
            var count = data.Categories.length > 5 ? 5 : data.Categories.length;
            for (var i = 0; i < count; i++) {
                var category = data.Categories[i].name;
                $nav_Categories.append("<td><a href='http://localhost:8000/catalog/" + category + "'>" + category + "</td>");

                $nav_SubCategories.append("<td id='tsub_" + i + "'></td>");
                $("#tsub_" + i).append("<ul class='nav-catalog-list' id='sub_" + i + "'></ul>");

                $nav_Brands.append("<td id='tbrand_" + i + "'></td>");
                $("#tbrand_" + i).append("<ul class='nav-catalog-list' id='brand_" + i + "'></ul>");


                var sub_count = data.Categories[i].data.length > 5 ? 5 : data.Categories[i].data.length;
                for (var s = 0; s < sub_count; s++) {
                    sub = data.Categories[i].data[s].name;
                    $("#sub_" + i).append("<li><a href='http://localhost:8000/catalog/" + category + "/" + sub + "'>" + sub + "</li>");
                    data.Brands.forEach(function(item) {
                        if (item.name == sub && item.data.length > 0) {
                            brand = item.data[0].name;
                            $("#brand_" + i).append("<li><a href='http://localhost:8000/catalog/" + category + "/" + sub + "/" + brand + "/products'>" + brand + "</li>");
                        }
                    })
                }
            }

            clearTimeout(catTimeout);
        }
    });
    // $.ajax({
    //     url: categoryURL,
    //     dataType: 'json',
    //     crossDomain: false,
    //     success: function(data) {
    //         var count = data.categories.length > 5 ? 5 : data.categories.length;
    //         for (var i = 0; i < count; i++) {
    //             var category = data.categories[i].name;
    //             $nav_Categories.append("<td><a href='http://localhost:8000/catalog/" + category + "'>" + category + "</td>");
    //             var subCategoryURL = "http://localhost:8000/catalog/" + category + "/subcategories.json";
    //             $.ajax({
    //                     url: subCategoryURL,
    //                     dataType: 'json',
    //                     crossDomain: false,
    //                     success: function(sub_data) {
    //                             $nav_SubCategories.append("<td id='category_" + i + "'></td>")
    //                             $("#category_" + i).append("<ul id='sub_list_" + i +"'></ul>");
    //                         var sub_count = sub_data.subcategories.length > 5 ? 5 : sub_data.subcategories.length;
    //                         for (var j = 0; j < sub_count; j++) {
    //                             var subcategory = sub_data.subcategories[j].name;
    //                             $("#sub_list_" + i).append("<li><a href='http://localhost:8000/catalog/" + category + "/" + subcategory + "'>" + subcategory + "</li>");
    //                             // $nav_SubCategories.append("<td><a href='http://localhost:8000/catalog/" + category + "/" + subcategory + "'>" + subcategory + "</td>");
    //                             var brandURL = "http://localhost:8000/catalog/" + category + "/" + subcategory + "/brands.json";
    //                             $.ajax({
    //                                 url: brandURL,
    //                                 dataType: 'json',
    //                                 crossDomain: false,
    //                                 success: function(brand_data) {
    //                                     var brand_count = brand_data.brands.length > 5 ? 5 : brand_data.brands.length;
    //                                     for (var k = 0; k < brand_count; k++) {
    //                                         brand = brand_data.brands[k].name
    //                                         $nav_Brands.append("<td><a href='http://localhost:8000/catalog/" + category + "/" + subcategory + "/brands'>" + brand + "</td>");
    //                                     }
    //                                 }
    //                             })
    //                         }
    //                     }
    //                 })
    //                 //var brandURL = "http://localhost:8000/catalog/" + + "/" + + "brands.json";
    //         }

    // clearTimeout(catTimeout);
    // }
    // });
}

loadData();
