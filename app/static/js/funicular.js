var agency_json;

function getAgencies(url) {
	url = url;
    $.ajax({
        url: url,
        type: 'GET',
        async: false
    }).done(function(json) {
        agency_json = json;
        fillStateSelect();
    }).fail(function() {
        console.log("Agency info retrieval failed!");
    });
}

function fillStateSelect() {
	stateList = [];
	for (i = 0; i < agency_json.data.length; i++) {
		if(stateList.indexOf(agency_json.data[i].state) === -1) {
			stateList.push(agency_json.data[i].state);
		}
	}
	stateList.sort();
	for(i = 0; i < stateList.length; i++) {
		$('#state-select').append('<option value="' + stateList[i] + '">' +
				stateList[i] + '</option>');
	}
}

function fillAgencySelect(state) {
	agencyList = [];
	for (i = 0; i < agency_json.data.length; i++) {
		if (state === 'all') {
			agencyList.push([agency_json.data[i].dataexchange_id,
				agency_json.data[i].name]);
		} else {
			if (agency_json.data[i].state === state) {
				agencyList.push([agency_json.data[i].dataexchange_id,
					agency_json.data[i].name]);
			}
		}
	}
	agencyList.sort();
	for(i = 0; i < agencyList.length; i++) {
		$('#agency-select').append('<option value="' + agencyList[i][0] + '">' +
				agencyList[i][1] + '</option>');
	}
}

function confirmGTFSSelection(description, date_added, user, fileURL) {
	var GTFS_description_full = description + ', added by ' + user + ' ' +
		moment.unix(date_added).calendar() + '.';
	if(user === 'funicular user') {
		agency_id = 'custom file';
	} else {
		agency_id = active_agency_id;
	}
	$('.GTFS-description').text(GTFS_description_full);
	$('#modal1').modal('show');
	$('#confirm').unbind('click');
	$('#confirm').click(function() {
        submitRequest(GTFS_description_full, fileURL, agency_id,
			$('#name-input')[0].value, $('#email-input')[0].value,
			$('#user-type-select')[0].value,
			$('#mailing-list-input').is(':checked'));
    });
}

function submitRequest(GTFS_description, fileURL, agency_id, user_name, email, user_type, mailing_list) {
	var valid_request = validateRequest(user_name, email, user_type);
	if(!valid_request) {
		alert('Please correct errors and re-submit.');
	} else {
		$('#modal1').modal('hide');
		$('.user-email').text(email);
		url = '/process_selection';
		$.ajax({
			url: url,
			type: 'POST',
			data: {
				GTFS_description: GTFS_description,
				fileURL: fileURL,
				agency_id: agency_id,
				user_name: user_name,
				email: email,
				user_type: user_type,
				mailing_list: mailing_list
			}
		}).done(function(str_queue_position) {
			if (str_queue_position === "reject") {
				$('#modal3').modal('show');
				console.log('Request not logged. Request for this email address already exists.');
			} else {
				$('#max-wait').text(getMaxWait(parseInt(str_queue_position)));
				$('#modal2').modal('show');
				console.log('Request logged!');
			}
		}).fail(function() {
			console.log('Request failed!');
		});
	}
}

function validateRequest(name, email, user_type) {
	valid = true;
	if(name === '') {
		$('#name-form-group').addClass('has-error');
		valid = false;
	}
	var atpos=email.indexOf('@');
	var dotpos=email.lastIndexOf('.');
	if (atpos<1 || dotpos<atpos+2 || dotpos+2>=email.length) {
		$('#email-form-group').addClass('has-error');
		valid = false;
	} else {
		$('#email-form-group').removeClass('has-error');
	}
	if(user_type === '') {
		$('#user-type-form-group').addClass('has-error');
		valid = false;
	}
	return valid;
}

function getMaxWait(position) {
	return 'Your file is #' + position + ' in the queue. Processing should ' +
			'be complete in no more than ' + 30 * position + ' minutes.';
}

function addAlert(type, dismissable, message) {
	var d_str = '';
	var button_html = '';
	if(dismissable) {
		d_str = 'dismissable';
		button_html = '<button type="button" class="close" data-dismiss="alert">&times;</button>';
	}
	var string = '<div class="alert alert-%TYPE% alert-%DISMISSABLE%">\
		%BUTTON_HTML%\
		%MESSAGE%\
		</div>';
	string = string.replace(/%TYPE%/, type);
	string = string.replace(/%DISMISSABLE%/, d_str);
	string = string.replace(/%BUTTON_HTML%/, button_html);
	string = string.replace(/%MESSAGE%/, message);
	$('.flash-container').append(string);
}

function SelectGTFSReady() {
	fillAgencySelect('all');
	$('#state-select')[0].value = '';
	$('#agency-select')[0].value = '';
	$('#submit-existing').click(function(){
		if($('#agency-select')[0].value === '') {
			addAlert('danger', true, 'Error: no agency selected.');
			$('#agency-select').focus();
		} else {
			window.location = '/agency/' + $('#agency-select')[0].value;
		}
	});
	$('#submit-url').click(function() {
		if($('#custom-GTFS-url')[0].value.slice(-4) !== '.zip') {
			addAlert('danger', true, 'Error: URL must point to a .zip file.');
			$('#custom-GTFS-url').focus();
		} else {
			confirmGTFSSelection($('#custom-GTFS-file-description')[0].value,
				moment().format('X'), 'funicular user',
				$('#custom-GTFS-url')[0].value);
		}
	});
	$('#submit-file').click(function() {
		if($('#custom-GTFS-file')[0].value.slice(-4) !== '.zip') {
			addAlert('danger', true, 'Error: Uploaded file must have a .zip extension.');
			$('#custom-GTFS-file').focus();
		// } else {
		// 	confirmGTFSSelection($('#custom-GTFS-url-description')[0].value,
		// 		moment().format('X'), 'funicular user',
		// 		$('#custom-GTFS-url')[0].value);
		}
	});
	// add GTFS file upload functionality
	$('#state-select').change(function() {
		$('#agency-select').find('option:not(:first)').remove();
		fillAgencySelect($('#state-select')[0].value);
		$('#agency-select').focus();
	});
	modalReady();
}

function modalReady() {
	$('#modal1').on('shown.bs.modal', function() {
		$('#name-input').focus();
	});
	$('#modal2').on('shown.bs.modal', function() {
		$('#close-modal2').focus();
	});
	$('#modal3').on('shown.bs.modal', function() {
		$('#close-modal3').focus();
	});
}
