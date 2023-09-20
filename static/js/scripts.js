$(function () {
    $(".btn-bookmark").on("click", function (e) {
        e.preventDefault();
        const url = $(this).attr("data-url");

        $.ajax({
            method: "POST",
            url: url,
            data: {
                postPk: $(this).attr("data-pk"),
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
            },
            success: function (response) {
                if (response.message == "bookmarked") {
                    $(".bi").removeClass("bi-bookmark").addClass("bi-bookmark-check-fill");
                }
                else if (response.message == "bookmark removed") {
                    $(".bi").removeClass("bi-bookmark-check-fill").addClass("bi-bookmark");
                }
            }
        })
    })
})
