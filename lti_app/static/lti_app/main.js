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
    showLoader();

    $.post('/assignments/', { text: $('#text').val() }, function (data) {
      // console.log(data);
      getJobsPoll = setInterval(getJobs, 1500);
    });
  });
});


