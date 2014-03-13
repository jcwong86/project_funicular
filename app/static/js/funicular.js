function confirmGTFSSelection(description, date_added, user, fileURL) {
	var GTFS_description_full = description + ', added by ' + user + ' ' + 
		moment.unix(date_added).calendar() + '.';
	$('.GTFS-description').text(GTFS_description_full);
	$("#modal1").modal('show')
	$("#confirm").unbind("click");
	$("#confirm").click(function() {
        submitRequest($('#email-input')[0].value, GTFS_description_full, fileURL);
    });
};

function submitRequest(email, GTFS_description, fileURL) {
	var valid_email = validateEmail(email)
	if(!valid_email) {
		alert('Please enter a valid email address'); //change this from an alert to an on-page notification?
	} else {
		$("#modal1").modal('hide')
		url = '/process_selection';
		$.ajax({
	        url: url,
	        type: 'POST',
	        data: {email: email,
	        	GTFS_description: GTFS_description,
	        	fileURL: fileURL
	        }
	    }).done(function() {
	    	$('.user-email').text(email)
			$('#modal2').modal('show');
	    }).fail(function() {
	        console.log('Request failed!');
	    });
	}
};

function validateEmail(email) {
	var atpos=email.indexOf('@');
	var dotpos=email.lastIndexOf('.');
	if (atpos<1 || dotpos<atpos+2 || dotpos+2>=email.length) {
		return false;
	} else {
		return true;
	}
};

function addAlert(type, dismissable, message) {
	var d_str = '';
	var button_html = '';
	if(dismissable) {
		d_str = 'dismissable'
		button_html = '<button type="button" class="close" data-dismiss="alert">&times;</button>'
	};
	var string = '<div class="alert alert-%TYPE% alert-%DISMISSABLE%">\
		%BUTTON_HTML%\
	    %MESSAGE%\
	    </div>';
	string = string.replace(/%TYPE%/, type);
	string = string.replace(/%DISMISSABLE%/, d_str);
	string = string.replace(/%BUTTON_HTML%/, button_html);
	string = string.replace(/%MESSAGE%/, message);
	$('.flash-container').append(string);
};