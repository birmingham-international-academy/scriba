$(document).ready(function () {
  var showLoader = function () {
    document.getElementById('loader').style.display = 'block';
    document.getElementById('content').style.display = 'none';
    document.getElementById('footer').style.display = 'none';
  };

  var hideLoader = function () {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('content').style.display = 'block';
    document.getElementById('footer').style.display = 'block';
  };

  var getJobsPoll = null;

  var getJobs = function () {
    $.get('/jobs/', function (response, status) {
      if (status !== 'nocontent') {
        $('#content').html(response);
        hideLoader();
        clearInterval(getJobsPoll);
      }
    });
  };

  $('#submit-assignment').on('click', function (event) {
    $.post('/assignments/', { text: $('#text').val() }, function (data) {
      if (data.assignment_type == 'D') {
        showLoader();
        getJobsPoll = setInterval(getJobs, 1500);
      } else {
        $('#title').text('Confirmation')
        $('#content').html($('#graded-assignment-confirmation').html())
      }
    });
  });
});


