$(document).ready(function() {

	$("div.review").on("click", function() {
		var clicked_obj = $(this);

		// Which pokemon was clicked? Like or dislike?
		var pokemon_id = $(this).attr('id');
		var review_type = $(this).children()[0].id;

		$.ajax({
			url: '/review',
			type: 'POST',
			data: JSON.stringify({ pokemon_id: pokemon_id, review_type: review_type}),
			contentType: "application/json; charset=utf-8",
        	dataType: "json",
			success: function(response){
				console.log(response);

				// Update the html rendered to reflect new count
				// Check which count to update
				if(review_type == "like") {
					clicked_obj.children()[0].innerHTML = " " + response.likes;
				} else {
					clicked_obj.children()[0].innerHTML = " " + response.dislikes;
				}
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
