$(document).ready(function(){
    $('#recommendation-form').submit(function(event){
        event.preventDefault();
        var course = $('#course').val();
        $.ajax({
            url: '/recommend',
            method: 'POST',
            data: {course: course},
            success: function(response){
                var recommendedCourses = response.recommended_courses;
                $('#recommended-courses').empty();
                $('#recommended-courses').append('<h2>Recommended Courses:</h2>');


                $.each(recommendedCourses, function(index, course){
                    var link = recommendedLinks[index];
                    $('#recommended-courses').append('<p>' + course + ' <button onclick="goToLink(\'' + link + '\')">Go to Course</button></p>');
                });
            }
        });
    });
});
