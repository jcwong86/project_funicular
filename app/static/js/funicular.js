//var agency_json

// function getAgencyInfo(agency_id) {
// 	url = '/get_agency_info/' + agency_id;
//     $.ajax({
//         url: url,
//         type: 'POST'
//     }).done(function(json) {
//     	//agency_json = json;
//         buildUpdateTable(json);
//     }).fail(function() {
//         console.log("Agency info retrieval failed!");
//     });
// };

// function buildUpdateTable(agency_json) {
// 	$('.GTFS-table-container').empty();
// 	$('.disclaimer-container').removeClass('hidden');
// 	$('.GTFS-table-container')
// 		.append($('<div>')
// 			.attr('class', 'page-header')
// 			.append($('<h3>')
// 				.text('Select GTFS file \u2014 ' + agency_json.data.agency.name)
// 			)
// 		)
// 		.append($('<table>')
// 			.attr('class', 'table table-striped GTFS-table')
// 			.append($('<thead>')
// 				.append($('<tr>')
// 					.append($('<th>')
// 						.text('Description')
// 					)
// 					.append($('<th>')
// 						.text('Added')
// 					)
// 					.append($('<th>')
// 						.text('User')
// 					)
// 					.append($('<th>')
// 						.text('Select')
// 					)
// 				)
// 			)
// 			.append($('<tbody>'))
// 		);
// 	for(var i = 0; i < agency_json.data.datafiles.length; i++) {
// 		$('.GTFS-table tbody').append($('<tr>')
// 			.append($('<td>')
// 				.text(agency_json.data.datafiles[i].description)
// 			)
// 			.append($('<td>')
// 				.text(moment.unix(agency_json.data.datafiles[i].date_added).calendar())
// 			)
// 			.append($('<td>')
// 				.text(agency_json.data.datafiles[i].uploaded_by_user)
// 			)
// 			.append($('<td>')
// 				.append($('<a>')
// 					.attr('href', '#')
// 					.attr('onclick', 'confirmGTFSSelection("' + agency_json.data.datafiles[i].description + 
// 						'", "' + moment.unix(agency_json.data.datafiles[i].date_added).calendar() + 
// 						'", "' + agency_json.data.datafiles[i].uploaded_by_user + 
// 						'", "' + agency_json.data.datafiles[i].fileURL + '"); return false;')
// 					.text('select')
// 				)
// 			)
// 		)
// 	}
// };

function confirmGTFSSelection(description, date_added, user, fileURL) {
	var GTFS_description_full = description + ', added by ' + user + ' ' + 
		moment.unix(date_added).calendar() + '.';
	// $('.GTFS-date-added').text('Date Added: ' + moment.unix(agency_info.data.datafiles[i].date_added).format('MM-DD-YYYY'));
	// $('.GTFS-user').text('User: ' + agency_info.data.datafiles[i].uploaded_by_user);
	$('.GTFS-description').text(GTFS_description_full);
	$("#modal1").modal('show')
	$("#confirm").unbind("click");
	$("#confirm").click(function() {
        submitRequest($('#email-input')[0].value, GTFS_description_full, fileURL);
    });
};

// function addAlert(type, dismissable, message) {
// 	$('.flash-container').append($('<div>')
// 		.append($('<button>')
// 			// .attr('type', 'button')
// 			// .attr('class', 'close')
// 			// .attr('data-dismiss', 'alert')
// 			// .text('x')
// 			// //.text('&times;')
// 		)
// 		.attr('class', 'alert alert-info alert-dismissable')
// 		.text(message)
// 	);
// };

function submitRequest(email, GTFS_description, fileURL) {
	var valid_email = validateEmail(email)
	if(!valid_email) {
		alert('Please enter a valid email address'); //change this from an alert to an on-page notification
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