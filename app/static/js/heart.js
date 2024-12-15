$(document).ready(function () {

    // Set the CSRF token so not rejected by server
    var csrf_token = $('meta[name=csrf-token]').attr('content');
    // Configure ajaxSetup
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    // Attach a function to trigger when heart is clicked
    $(".fa-heart").on("click", function () {
        var clicked_obj = $(this);

        // gets value of heart, either 1 or 0
        var liked = clicked_obj.attr('data-value') === "1" ? 0 : 1;
        clicked_obj.attr('data-value', liked);

        // applies class to show heart has been clicked
        clicked_obj.toggleClass("selected", liked === 1)

        // gets value of film_id that was liked
        var film_id = clicked_obj.data('film-id');

        $.ajax({
            url: '/liked',
            type: 'POST',
            data: JSON.stringify({ film_id: film_id, liked: liked }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
        });

        // Colours heart with hover and removes colour when mouse is moved
        $(".fa-heart").on("mouseover", function () {
            var hover_obj = $(this);

            hover_obj.addClass("hover").nextAll().addClass("hover");
        }).on("mouseout", function () {
            $(".fa-heart").removeClass("hover");
        });
    });
});
