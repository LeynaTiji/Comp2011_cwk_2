$(document).ready(function () {
    $(".fa-star").on("click", function () {
        var clicked_obj = $(this);

        // retrieve data value attribute of stars clicked
        var rating = parseInt(clicked_obj.attr('data-value'), 10);

        $("#ratingValue").val(rating);

        // Colours star if clicked and dehighlights the star if not selected
        clicked_obj.addClass("selected").nextAll().addClass("selected");
        clicked_obj.prevAll().removeClass("selected");

    });

    // Colours star with hover and removes colour when mouse is moved
    $(".fa-star").on("mouseover", function () {
        var hover_obj = $(this);

        hover_obj.addClass("hover").nextAll().addClass("hover");
    }).on("mouseout", function () {
        $(".fa-star").removeClass("hover");
    });
});