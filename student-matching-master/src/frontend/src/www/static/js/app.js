var SUCCESS_CODE = 1;
var FAILURE_CODE = -1;

var numStudentsToMatch = 0
var rangeRelevancyValues = {"0": "Not Used", "1": "Low", "2": "Medium", "3": "High"}

$('document').ready(function() {

    // ------------------------------------------
    // INITIAL POST FOR HOMEPAGE
    // ------------------------------------------

    $.post('/newMatchStep1').done(function(res) {
        $("#content").html(res)
        initialize()
    });

    // ------------------------------------------
    // SIDE MENU EVENT LISTENERS
    // ------------------------------------------

    // set buttons as active upon click
    $(".btn-sidebar").click(function(){
        $(".btn-sidebar").removeClass("btn-sidebar-active");
        $(this).addClass("btn-sidebar-active");
    });

    $("#newmatch-btn").click(function() {
        $.post('/newMatchStep1').done(function(res) {
            $("#content").html(res)
        });
    });

    $("#lastmatch-btn").click(function() {
        $.post('/lastMatch', function(res) {
            $("#content").html(res)
        })
        .done(function() {

            // get all the students from the database
            $("#gloader").show();
            $.post("/students", function(res) {
                $("#gloader").hide();
        		resJSON = JSON.parse(res)
        		if (resJSON.code == SUCCESS_CODE) {

        		    students = resJSON.students.data
        		    $("#last-match-table").bootstrapTable('load', students)

                    // select the first row on default.
                    $("#last-match-table tr[data-index='0'] td")[0].click()

                    // update the progress bar for the faculties at the bottom
                    $.post("/facultypercent").done(function(res) {

                        var data = JSON.parse(res).percentages.data;
                        data.forEach(function(faculty) {

                            faculty_name = faculty.faculty;
                            css_selector = faculty_name.split(" ")[0].toLowerCase();
                            percent = faculty.percent;

                            $(".progress-bar."+css_selector).css("width", percent+"%");
                            $(".progress-bar."+css_selector).attr("data-original-title", faculty_name + " (" + Math.floor(percent) + "%)");
                        });
                    });

        		} else {
        			console.log(resJSON.message);
        			console.log(resJSON.exception);
        		}
            }).done(function() {

                $("#content").find("#table-wrapper").find("div.bootstrap-table").find("label").find("input[data-field='is_mentor']").parent().hide()

                var roleFilterElem = "<div style=\"height:15px;\">" +
                                        "<p style=\"margin-right: 10px; display: inline\">Filter by role:</p>" +
                                        "<select id=\"role-filter\" style=\"font-size:0.8em; vertical-align:middle; height:25px; width: auto; display: inline;\" class=\"form-control\">" +
                                            "<option selected>All</option>" +
                                            "<option>Mentors</option>" +
                                            "<option>Mentees</option>" +
                                        "</select>" +
                                    "</div>"
                $("#content").find("#table-wrapper").find("div.bootstrap-table").find(".fixed-table-toolbar").find(".float-left").append(roleFilterElem);

                // filter by role dropdown listener
                $("#content").find("select#role-filter").on('change', function() {
                    var valSelected = $(this).val()
                    if (valSelected === "Mentors") {
                        // TODO
                        // $("#last-match-table").bootstrapTable("filterBy", {"is_mentor": "true"});
                        console.log(valSelected)

                    } else if (valSelected === "Mentees") {
                        // TODO
                        // $("#last-match-table").bootstrapTable("filterBy", {"is_mentor": "false"});
                        console.log(valSelected)

                    } else { // "All" was selected
                        $("#last-match-table").bootstrapTable("filterBy", {}); // working
                        console.log(valSelected)
                    }
                });
            });

            // TEST BUTTON: get all checked rows. to be used for the emailing and manual assignation functionality.
            // $("#test-btn").click(function () {
            //     console.log(JSON.stringify($("#last-match-table").bootstrapTable('getSelections')));
            //     $("#last-match-table").bootstrapTable('uncheckAll').find("tr").removeClass('selected');
            // })

            // row click listener
            var months = ["Sept", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
            $("#last-match-table").on('click-row.bs.table', function(e, row, trElem) {

                // create randomly generated line graph for tracked engagement
                $("#content #engagement-chart-wrapper").html("<canvas id=\"engagement-chart\"></canvas>")
                var ctx = $("#content").find("#engagement-chart")
                var myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: months,
                        datasets: [{
                            data: getRandomArr(months.length, 0, 6),
                            label: "Group",
                            borderColor: "#3e95cd",
                            fill: false,
                            borderWidth: 2,
                            pointBorderWidth: 2,
                            pointRadius: 2
                        }, {
                            data: getRandomArr(months.length, 0, 6),
                            label: "Faculty",
                            borderColor: "#c45850",
                            fill: false,
                            borderWidth: 2,
                            pointBorderWidth: 2,
                            pointRadius: 2
                        }]
                    },
                    options: { layout: { padding: { left: 0, right: 0, top: -9, bottom: -5 }},
                                title: { display: false, text: 'Mentor & Mentee Engagement' },
                                scales: { yAxes: [{ scaleLabel: { display: false,
                                                                    labelString: 'Engagement' }}],
                                        xAxes: [{ scaleLabel: { display: false,
                                                                labelString: 'Month' }}]},
                                tooltips: { enabled: false },
                                legend: { display: true, labels: { boxWidth: 15}},
                                responsive: true,
                                maintainAspectRatio: false }
                });

                // get group for the selected student
                $("#gloader").show();
    			$.ajax({
    				type: "POST",
    				url: "/get_group",
    				data: JSON.stringify({"student_id": row.student_id}),
    				contentType: 'application/json; charset=utf-8',
    			    success: function(res) {
                                $("#gloader").hide();
    					resData = JSON.parse(res);
    					//console.log(resData.group.data);
                        numMentees = resData.group.data.length - 1; // subtract the mentor

                        // reset the content for the different tables
                        $(".mentors-table").empty();
                        $(".mentees-table").empty();
                        $(".faculty-table").empty();

            			// update faculty name for this group
            			var facultyName = resData.group.data[0]["faculty"]
            			$(".faculty-table").append("<tr><td colspan=\"3\">" + facultyName + "</td></tr>");

            			// update number of mentees in the current group
            			$("div.current-group div.group-mentor table.group-table thead#mentees-header p.mentees-num").html("(" + numMentees + ")")

                        for (i = 0; i < resData.group.data.length; ++i) {
                            current_data = resData.group.data[i];

                            student_id = current_data["student_id"];
                            first_name = current_data["name"];
                            last_name = current_data["surname"];
                            class_n = "";

				            // highlight the student clicked
                            if (row.student_id == student_id) { class_n += "highlight-row"; }

                            line = "<tr class=\""+class_n+"\"><td>"+student_id+"</td><td>"+first_name+"</td><td>"+last_name+"</td></tr>";

                            if (current_data["is_mentor"]) { $(".mentors-table").append(line); } // add mentor to the table
				            else { $(".mentees-table").append(line); } // add mentees to the table
                        }

                        $(".current-group").show();
    				}
    			});

                // highlight selected row
                $('.row-selected').removeClass('row-selected');
                $(trElem).addClass('row-selected');
            });

            // remove row background setting on checkbox checked
            $("#last-match-table").on('check.bs.table', function(e, row, trElem) {
                $(this).find("tr").removeClass('selected')
            });

            // remove row background setting on checkbox unchecked
            $("#last-match-table").on('uncheck.bs.table	', function(e, row, trElem) {
                $(this).find("tr").removeClass('selected')
            });

            // add functionality to Faculty participation distribution bar
            var templateString = "<div class=\"tooltip\" role=\"tooltip\"><div class=\"arrow\"></div><div style=\"font-size:0.8em\" class=\"tooltip-inner\"></div></div>"
            $('[data-toggle="tooltip"]').tooltip({placement: "bottom", template: templateString})

            // add three-dot menu to table
            var menuElem = "<div class=\"dropdown\">" +
				"<img id=\"three-dot-menu-btn\" class=\"float-right\" src=\"../static/img/three-dot-menu.png\" style=\"height: 28px; padding: 5px 5px 5px 10px; cursor: pointer;\">" +
				"<div class=\"dropdown-content\">" +
					"<ul>" +
						"<li class=\"dropdown-list-el\" id=\"dropdown-email-btn\"><img style=\"height: 15px; margin-right: 10px; display:inline;\" src=\"../static/img/email-icon-black.png\"><p style=\"display:inline;\">E-mail Students</p</li>" +
                        "<li><hr></li>" +
						"<li class=\"dropdown-list-el\" id=\"dropdown-manual-assignation-btn\"><img style=\"height: 15px; margin-right: 10px; display:inline;\" src=\"../static/img/manual-asign-icon.png\"><p style=\"display:inline;\">Manual Assignation</p></li>" +
					"</ul>" +
				"</div>" +
			"</div>";
            $("#content").find("div#table-wrapper").find("div.left-panel").prepend(menuElem);


            $("#three-dot-menu-btn").click(function() {
    			$(".dropdown-content").toggle()
    		});

            // ---------dropdown menu event listeners---------

            //Email-dropdown
            $(".dropdown-content #dropdown-email-btn").click(function() {

                //Hide all the components
                $("#modal-email-students .main-components").hide()
                $("#modal-email-students .loading-components").hide()
                $("#modal-email-students .success-components").hide()
                $("#modal-email-students .error-components").hide()

                //check if there are any selected students
                if ($("#last-match-table").bootstrapTable('getSelections').length > 0){
                    //Ensure that only the needed info is displayed in the modal
                    $("#modal-email-students .main-components").show()
                }else{
                    //Display Error
                    $("#modal-email-students .error-components").show()
                }

                //Display a pop-up for emailing
                $('#modal-email-students').modal('show');

            });

            //Send an email to all the users checked on the table
            $("#email-students-btn").click(function(){
                //console.log("[TODO] Sending email...");
                console.log("email-students-btn clciked")

                $("#modal-email-students .main-components").hide()
                $("#modal-email-students .loading-components").show()
                $("#modal-email-students .success-components").hide()
                $("#modal-email-students .error-components").hide()

                //TODO send this to an actual email route in the server
                $.get("/sleeper").done(function(){
                    //success
                    $("#modal-email-students .loading-components").hide()
                    $("#modal-email-students .success-components").show()
                });

                //display all the emails
                $("#last-match-table").bootstrapTable('getSelections').forEach(function(ele){
	                   console.log(ele);
                })

                $("#last-match-table").bootstrapTable('uncheckAll').find("tr").removeClass('selected');

                //todo: send request with emails to server
            });

            $('#modal-manual-assignation').on('hidden.bs.modal', function () {
                if ($("#save-manual-assignation-btn").hasClass("mmm-btn-disabled")) { // matches have been saved
                    $("#last-match-table").bootstrapTable('uncheckAll').find("tr").removeClass('selected');
                }
            });

            $("#save-manual-assignation-btn").click(function() {

                $('#modal-manual-assignation').find('#save-manual-assignation-btn').addClass("mmm-btn-disabled").find('p').html("SAVED")

                // $('#modal-manual-assignation .modal-body').hide()
                // $('#modal-manual-assignation .modal-footer').hide()
                // $('#modal-manual-assignation .loader').show()
                // $.get("/sleeper").done(function(){
                //     //success
                //     $('#modal-manual-assignation .loader').hide()
                //     $('#modal-manual-assignation .modal-success-body').show()
                // });
            });

            $(".dropdown-content #dropdown-manual-assignation-btn").click(function() {
                // Update manual assignation modal box before showing.
                $('.manual-faculty').empty();
                $('.manual-mentee').empty();
                $('.manual-mentor select').empty();
                //var selected_student = parseInt($('tr.row-selected').attr('data-uniqueid'));

                var selectedStudents = $("#last-match-table").bootstrapTable('getSelections');
                // $("#last-match-table").bootstrapTable('uncheckAll').find("tr").removeClass('selected');

                $("#manual-table tbody").empty();

                var displayCount = 0;

                // for each selected (checked) student
                for (var idx = 0; idx < selectedStudents.length; ++idx) {

                    if (!selectedStudents[idx].is_mentor) {
                        displayCount++; // only count mentees
                    } else {
                        continue;
                    }

                    current_student = selectedStudents[idx].student_id;

                    $.post('/students/' + current_student).done(function(res) {
                        resData = JSON.parse(res);

                        studentData = resData.student.data[0];
                        // Get if current student is mentor.
                        var selected_student = studentData.student_id;
                        var is_mentor = studentData.is_mentor;
                        var sfaculty = studentData.faculty;
                        var sfullname = studentData.name + ' ' + studentData.surname;

                        // Get mentors for current faculty.
                        $.ajax({
                            type: "POST",
                            url: "/students/mentors",
                            data: JSON.stringify({"faculty": sfaculty }),
                            contentType: 'application/json; charset=utf-8',
                            success: function(res) {
                                var mentorsData = JSON.parse(res);

                                mentorsData = mentorsData.mentors.data;

                                $.ajax({
                                    type: "POST",
                                    url: "/get_group",
                                    data: JSON.stringify({"student_id": selected_student}),
                                    contentType: 'application/json; charset=utf-8',
                                    success: function(res) {
                                        grpData = JSON.parse(res);
                                        grpData = grpData.group.data;

                                        // Get current mentor.
                                        var mentorId = 0;
                                        for (var i = 0; i < grpData.length; ++i) {
                                            if (grpData[i].is_mentor) {
                                                mentorId = grpData[i].student_id;
                                                break;
                                            }
                                        }

                                        // create select element
                                        $("#manual-table tbody").append("<tr>" +
                                                "<td>" + sfaculty + "</td>" +
                                                "<td>" + sfullname + "</td>" +
                                                "<td><select onchange=\"manAssignationDropdownChanged()\" class=\"form-control\" id=\"select-" + selected_student + "\"></select></td>");

                                        // Create options for mentors, adding them to the select element
                                        // TODO: Change this to while loop or equivalent
                                        for (var i = 0; i < mentorsData.length; ++i) {

                                            (function (i){
                                                // get group for this mentor using API. Then, get number of group members -1 for number of mentees.
                                                var numMentees = 0;
                                                var mentorStudentId = mentorsData[i].student_id;
                                                var mentorFirstName = mentorsData[i].name;
                                                var mentorLastName = mentorsData[i].surname;
                                                $.ajax({
                                                    type: "POST",
                                                    url: "/get_group",
                                                    data: JSON.stringify({"student_id": mentorsData[i].student_id}),
                                                    contentType: 'application/json; charset=utf-8',
                                                    success: function(res) {

                                                        currMentorGroup = JSON.parse(res)
                                                        currMentorGroup = currMentorGroup.group.data
                                                        numMentees = currMentorGroup.length - 1;
                                                        //console.log(i, numMentees); // correct

                                                        var selected = '';
                                                        var currMentorSym = ''

                                                        // if (mentorsData[i].student_id == mentorId) {
                                                        if (mentorStudentId == mentorId) {
                                                            selected = 'selected=\"selected\"';
                                                            currMentorSym = "&starf;"
                                                        }

                                                        $('#select-' + selected_student).append('<option '
                                                                                                + selected + '>'
                                                                                                + mentorFirstName + ' '
                                                                                                + mentorLastName + ' '
                                                                                                + '(' + numMentees + ')' + ' '
                                                                                                + currMentorSym
                                                                                                + '</option>');
                                                    }
                                                });
                                            })(i);
                                        }
                                    }
                                });
                            }
                        });

                    });
                }

                if (displayCount > 0) {
                    $(".manual-section").show();
                    $(".manual-error").hide();
                    $('#modal-manual-assignation .modal-footer').show()
                    $("#save-manual-assignation-btn").show()
                } else {
                    $(".manual-section").hide();
                    $(".manual-error").show();
                    $('#modal-manual-assignation .modal-footer').hide()
                    $("#save-manual-assignation-btn").hide()
                }

                //display the manual assignation modal
                $('#modal-manual-assignation .modal-body').show()
                $('#modal-manual-assignation .modal-success-body').hide()
                $('#modal-manual-assignation .loader').hide()
                $('#modal-manual-assignation').modal('show');
            });

            $("html").click(function (test) {
            	var $elem = $(".dropdown-content");
            	if (test.target.id !== "three-dot-menu-btn") {
                    if ($elem.css("display") !== "none") { $elem.hide() }
                }
            });

        });
    });

    $("#mentorlogs-btn").click(function() {
        $.post('/mentorLogs').done(function(res) {
            $("#content").html(res)
        });
    });

    $("#feedback-btn").click(function() {
        $.post('/feedback').done(function(res) {
            $("#content").html(res)
        });
    });

    // ------------------------------------------
    // NEW MATCH - STEP 1
    // ------------------------------------------

    $("#content").on('change', '#mentor-file-input', function () {
        if (typeof this.files[0] == "undefined") {
            $("#mentor-filename").html("No file selected.").css("color", "red").css("font-family", "'Poppins', sans-serif")
        } else {
            $("#mentor-filename").html(this.files[0].name).css("color", "black").css("font-family", "'Inconsolata', monospace")
        }
    });

    $("#content").on('change', '#student-file-input', function () {

        if (typeof this.files[0] == "undefined") {
            $("#student-filename").html("No file selected.").css("color", "red").css("font-family", "'Poppins', sans-serif")
        } else {
            $("#student-filename").html(this.files[0].name).css("color", "black").css("font-family", "'Inconsolata', monospace")
        }
    });

    $("#content").on('submit', '#file-upload-form', function (e) {
        e.preventDefault();

        console.log("Submitting form...");

        var formData = new FormData(this);

        $.ajax({
            url: "/upload",
            type: 'POST',
            data: formData,
            success: function (res) {

                resData = JSON.parse(res)

                if (resData.code == SUCCESS_CODE) {

                    console.log(resData.message)
                    numStudentsToMatch = resData.numStudents

                    // ------------------------------------------
                    // NEW MATCH - STEP 2
                    // ------------------------------------------
                    $.post('/newMatchStep2').done(function(innerRes) {

                        innerResData = JSON.parse(innerRes)

                        // load main content for step 2
                        $("#content").html(innerResData.html)

                        // hide some contents
                        $("#step2-right-wrapper").css("display", "none");
                        $("#step2-buttons").css("display", "none");
                        $("#match-success-msg").css("display", "none");

                        // load questions' table
                        $("#questions-table-wrapper").append(innerResData.htmltable);

                        $("#questions-table tr").each(function () {

                                var currVal = $(this).find("input[type=range]").val()
                                $(this).find("label").text(rangeRelevancyValues[currVal])

                                $(this).find("input[type=range]").on('input change', function () {

                                    var selectedVal = this.value
                                    $(this).parent().find("label").text(rangeRelevancyValues[selectedVal])

                                    if (selectedVal == 0) {
                                        $(this).parent().find("label").css("color","lightgrey");
                                    } else if (selectedVal == 1) {
                                        $(this).parent().find("label").css("color","forestgreen");
                                    } else if (selectedVal == 2) {
                                        $(this).parent().find("label").css("color","goldenrod");
                                    } else if (selectedVal == 3) {
                                        $(this).parent().find("label").css("color","red");
                                    }
                                });
                        });
                    });

                } else {
                    // display error message.
                    $("#step1-errmsg").html(resData.message)
                }
            },
            cache: false,
            contentType: false,
            processData: false
        });
    });

    // ------------------------------------------
    // NEW MATCH - STEP 2
    // ------------------------------------------

    // "match" button is clicked
    $("#content").on('click', '#match-btn', function () {

        // initialize modal elements
        $('#modal-email-mentors').find("form").show()
        $('#modal-email-mentors').find(".modal-success-body").hide()

        // initialize button elements
    	$("#checkmark-icon").css("display","none")
    	$("#loading-icon").css("display","inline-block")
    	$("#step2-buttons").css("display", "none");
    	$("#match-success-msg n").html("");
    	$("#match-success-msg").css("display", "none");

    	// scroll to the top of the page
        $('html, body').animate({scrollTop: $("#step2-title").offset().top}, 0);

        // disable matching button
        $("#match-btn").attr('disabled','disabled').addClass("mmm-btn-disabled")

        // display loading message
        $("#step2-right-wrapper").css("display", "inline-block");
        $("#match-loading-msg n").html(numStudentsToMatch)

        // store table information in a json object
        var questionWeights = {'questions': []};
        $("#questions-table tbody tr").each(function() {
            var questionHeader = $(this).find("td.qheader").html();
            var questionWeight = $(this).find("input[type=range]").val()
            questionWeights.questions.push({'header': questionHeader, 'weight': questionWeight});
        });

        $("#gloader").show();
        $.ajax({
            type: 'POST',
            url: "/match",
            data: JSON.stringify(questionWeights),
            contentType: 'application/json; charset=utf-8',
            success: function (res) {

                resData = JSON.parse(res)
                numGroups = resData.numGroups

                // update ui upon match completion
                $("#match-success-msg").css("display", "block");
                $("#match-success-msg n").html(numGroups);
                $("#step2-buttons").css("display", "block");
                $("#loading-icon").toggle()
                $("#checkmark-icon").toggle()
                $("#gloader").hide();

                emails = []
                // event listener for automatic emailing for mentors, with a list of their mentees
                $("#step2-email-mentors").click(function() {
                    // get all the groups from the database
                    $.get("/groups", function(res) {
                        emails = []
                		resJSON = JSON.parse(res)

                		if (resJSON.code == SUCCESS_CODE) {
                		    groups = resJSON.groups.data

                            var menteesListStr = ""
                            groups.forEach(function (group, i) {

                                menteesListStr = ""
                                group.group.forEach(function(mentee, i) {
                                    menteesListStr += mentee.name + " " + mentee.surname + ", " + mentee.email  + "<br>"
                                });

                                // generate an email object with default values for to, from, subject and content
                                emailObj = createEmailObject();
                                emailObj.to = group.mentor.email
                                emailObj.content = menteesListStr

                                // additional field in order to customize the email content
                                emailObj.mentor = group.mentor

                                // add to all-emails array
                                emails.push(emailObj)
                            });

                		} else {
                			console.log(resJSON.message);
                			console.log(resJSON.exception);
                		}
                    })
                    .done(function() {
                        $('#modal-email-mentors').modal('show');
                        $("#modal-email-mentors #num-mentors-email").html(numGroups)
                    });
                }); // end on-click listener

        		$("#step2-edit-matches").click(function() {
        			 $("#lastmatch-btn").click();
        		});

                // re-enable matching button (clicking it again causes issues... will leave it disabled for now)
                $("#match-btn").removeClass("mmm-btn-disabled").removeAttr("disabled")
            }
        });
    });

    // triggered when the email is sent
    $("#content").on("submit", "#mentor-email-form", function(e) {

        // supress default form action
        e.preventDefault();

        // replace the modal content with loading icon
        $('#modal-email-mentors').find("form").hide()
        $("#modal-email-mentors").find("div.loading-components").show()

        // grab the current value of the text area
        textareaText = $(this).find("textarea").val();
        inputText = $(this).find("input").val();

        // complete the email object with updated values of subject and content
        emails.forEach(function (email, i) {
            customTextareaText = textareaText.replace("[FNAME]", email.mentor.name).replace("[LNAME]", email.mentor.surname).replace("[MLIST]", email.content)
            customInputText = inputText.replace("[FNAME]", email.mentor.name).replace("[LNAME]", email.mentor.surname)
            emails[i].content = customTextareaText;
            emails[i].subject = customInputText;
        });

        console.log(emails.length)

        // send emails
        // console.log(emails[0])
        $.ajax({
            type: "POST",
            url: "/send_email",
            data: JSON.stringify(emails),
            contentType: 'application/json; charset=utf-8',
            success: function(res) {
                resData = JSON.parse(res);
                if (resData.code == SUCCESS_CODE) {
                    console.log(resData.message);
                }
            }
        });

        $.get("/sleeper").done(function(){
            $("#modal-email-mentors .loading-components").hide()
            $("#modal-email-mentors .modal-success-body").show()
        });
    });

    $("#content").on('click', '#step2-download-btn', function() {
        $.get("/download");
    });

});

/**
 * Returns a random number between min (inclusive) and max (exclusive)
 */
function getRandomArr(n, min, max) {
    var a = []
    for (var i = 0; i < n; i++) {
        var randomNum = Math.random() * (max - min) + min;
        a.push(randomNum)
    }
    return a;
}

function rowStyle(row, index) {
    if (row.is_mentor == true) {
        return {
            css: {"background-color": "#F0F0F0"}
        };
    }
    return {};
}

//Initialize a bunch of elements on loading the main page
function initialize (){
    $("#gloader").hide(); //todo: uncomment
}

function createEmailObject() {

    var emailObj = new Object()
    emailObj.to = "to@test.com"
    emailObj.from = "noreply@test.com"
    emailObj.subject = ""
    emailObj.content = ""

    return emailObj
}

function manAssignationDropdownChanged() {
    $('#modal-manual-assignation').find('#save-manual-assignation-btn').removeClass("mmm-btn-disabled").find('p').html("SAVE")
}
