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
};

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
};

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
};

function confirmGTFSSelection(description, date_added, user, fileURL) {
	var GTFS_description_full = description + ', added by ' + user + ' ' + 
		moment.unix(date_added).calendar() + '.';
	$('.GTFS-description').text(GTFS_description_full);
	$('#modal1').modal('show');
	$('#confirm').unbind('click');
	$('#confirm').click(function() {
        submitRequest(GTFS_description_full, fileURL, $('#name-input')[0].value,
        	$('#email-input')[0].value, $('#user-type-select')[0].value, 
        	$('#mailing-list-input').is(':checked'));
    });
};

function submitRequest(GTFS_description, fileURL, user_name, email, user_type, mailing_list) {
	var valid_request = validateRequest(user_name, email, user_type);
	if(!valid_request) {
		alert('Please correct errors and re-submit.');
	} else {
		$('#modal1').modal('hide');
		$('.user-email').text(email);
		$('#modal2').modal('show');
		url = '/process_selection';
		$.ajax({
	        url: url,
	        type: 'POST',
	        data: {
	           	GTFS_description: GTFS_description,
	        	fileURL: fileURL,
	        	agency_id: active_agency_id,
	        	user_name: user_name,
	        	email: email,
	        	user_type: user_type,
	        	mailing_list: mailing_list
	        }
	    }).done(function() {
	    	console.log('Request logged!');
	    }).fail(function() {
	        console.log('Request failed!');
	    });
	}
};

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
};

// function validateName()

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

function agencyReady() {
	if(active_agency) {
		fillAgencySelect(active_agency_state);
		$('#state-select')[0].value = active_agency_state;
		$('#agency-select')[0].value = active_agency_id;
	} else {
		fillAgencySelect('all');
		$('#state-select')[0].value = '';
		$('#agency-select')[0].value = '';
		$('#state-select')[0].focus();
	}
	$('#submit').click(function(){
		if($('#agency-select')[0].value === '') {
			addAlert('danger', true, 'Error: no agency selected.');
			$('#agency-select').focus();
		} else {
			window.location = '/agency/' + $('#agency-select')[0].value;
		}
	});
	$('#state-select').change(function() {
		$('#agency-select').find('option:not(:first)').remove();
		fillAgencySelect($('#state-select')[0].value);
   		$('#agency-select').focus();
  	});
  	$('#modal1').on('shown.bs.modal', function() {
  		$('#name-input').focus();
  	});
  	$('#modal2').on('shown.bs.modal', function() {
  		$('#close-modal2').focus();
  	});
};
