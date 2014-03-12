function getAgencyInfo(agency_id) {
	url = '/get_agency_info/' + agency_id;
	console.log(url);
    $.ajax({
        url: url,
        type: 'POST'
    }).done(function(json) {
        console.log("Agency info retrieved!");
        buildUpdateTable(json);
    }).fail(function() {
        console.log("Agency info retrieval failed!");
    });
};

function buildUpdateTable(agency_json) {
	console.log("Building table!");
	$('.GTFS-table-container').empty();
	$('.disclaimer-container').removeClass('hidden');
	$('.GTFS-table-container')
		.append($('<div>')
			.attr('class', 'page-header')
			.append($('<h3>')
				.text('Select GTFS file \u2014 ' + agency_json.data.agency.name)
			)
		)
		.append($('<table>')
			.attr('class', 'table table-striped GTFS-table')
			.append($('<thead>')
				.append($('<tr>')
					.append($('<th>')
						.text('Description')
					)
					.append($('<th>')
						.text('Added')
					)
					.append($('<th>')
						.text('User')
					)
					.append($('<th>')
						.text('Select')
					)
				)
			)
			.append($('<tbody>'))
		);
	for(var i = 0; i < agency_json.data.datafiles.length; i++) {
		$('.GTFS-table tbody').append($('<tr>')
			.append($('<td>')
				.text(agency_json.data.datafiles[i].description)
			)
			.append($('<td>')
				.text(moment.unix(agency_json.data.datafiles[i].date_added).calendar())
			)
			.append($('<td>')
				.text(agency_json.data.datafiles[i].uploaded_by_user)
			)
			.append($('<td>')
				.append($('<a>')
					.attr('href', '#')
					.attr('onclick', 'confirmGTFSSelection("' + agency_json.data.datafiles[i].description + 
						'", "' + moment.unix(agency_json.data.datafiles[i].date_added).calendar() + 
						'", "' + agency_json.data.datafiles[i].uploaded_by_user + '"); return false;')
					.text('select')
				)
			)
		)
	}
};

function confirmGTFSSelection(description, date_added, user) {
	$('.GTFS-description').text('Description: ' + description + ', added by ' + 
		user + ' ' + date_added + '.');
	// $('.GTFS-date-added').text('Date Added: ' + moment.unix(agency_info.data.datafiles[i].date_added).format('MM-DD-YYYY'));
	// $('.GTFS-user').text('User: ' + agency_info.data.datafiles[i].uploaded_by_user);
	console.log('Modal displayed!');
	$(".modal").modal();
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