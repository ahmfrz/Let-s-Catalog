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
            if(count == 0)
                {
                    $("#nav-catalog").removeClass("catalog");
                    $nav_Categories.append("<td>No data</td>");
                }
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
}

function signInCallback(authResult) {
    if (authResult['code']) {
        // Hide the sign in button
        $('#signinButton').attr('style', 'display:none');
        // Send the one-time-use code to the server, if the server responds,
        // write a 'login successful' message to the web page and then redirect
        // back to the main restaurants page

        state = $("#state").data().value;
        $.ajax({
            type: 'POST',
            url: '/gconnect?state=' + state,
            processData: false,
            data: authResult['code'],
            contentType: 'application/octet-stream; charset=utf-8',
            success: function(result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    $('#result').html('<h1>Login successful </br>' + result + '</br> redirecting!</h1>');
                    setTimeout(function() {
                        window.location.href = '/index';
                    }, 4000);
                } else if (authResult['error']) {
                    console.log("There was an error " + authResult['error']);
                } else {
                    $('#result').html('Failed to make a server-side call. Check your configuration and console.');
                }
            },
            error: function(result){
                $('#result').html('Server error');
            }
        })
    }
}

loadData();
