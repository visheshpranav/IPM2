 /*************** Login Page **********************/
//declare Variable
var Project = "";
var Role = "";
var Metrics = "";

// function to validate user and password fields
function validate()
{
	if(isValidCredntial())
	{
		var xhttp = new XMLHttpRequest();
		var user = document.getElementById("Txt_Username").value.trim();
		var pwd = document.getElementById("Txt_Password").value.trim();

		var fd = new FormData();
		fd.append("Txt_Username",user);
		fd.append("Txt_Password",pwd);
		localStorage.setItem("ipm_username",user);

		xhttp.addEventListener("error", login_error, false);
		xhttp.onreadystatechange = function() {
			
			if ((this.readyState == 4) && (this.status == 200))
			{
				var response_arr = this.responseText.split("\n");
				var response_txt = response_arr[0].split(" ");
				response_code = response_txt[0];
				response_code = response_code.trim()
				if(response_code == "UAP1")
				{
					if(user == "admin" && pwd == "admin")
					{
						window.location = 'Admin/Admin_Home.html';
						if(response_txt[1] != "")
						{
							userid = response_txt[1];
						}
						if(response_txt[2] != "")
						{
							appname = response_txt[2];
						}
					}
					else{
						if(response_txt[1] != "")
						{
							userid = response_txt[1];
						}
						if(response_txt[2] != "")
						{
							appname = response_txt[2];
						}						
						if(response_txt[3] != "")
						{
							role = response_txt[3];
						}
						//window.location = 'Main.html';
						var appname_arr = response_arr[1].split("'");
						var user_drp = document.getElementById("slt_app");	
						var test_length = user_drp.options.length;
						for (i = 0; i < test_length; i++) {
						  user_drp.options[0] = null;
						}
						for (var res_i=1; res_i<appname_arr.length ; res_i=res_i+2) {					
							var option = document.createElement("option");
							option.text = appname_arr[res_i].replace(/[,\(\)\']/g,"");
							user_drp.add(option, user_drp[0]);
						}						
						document.getElementById("slt_app").disabled = false;
						document.getElementById("slt_app").style.backgroundColor = "#e8f0fe";
					}

					localStorage.setItem("ipm_username",user);
					localStorage.setItem("ipm_UserId",userid);
					localStorage.setItem("ipm_appname",appname);
					localStorage.setItem("ipm_Role",role);
				}
				else
				{
					if(response_code == "UAP0")
					{
						alert("Please enter a valid UserName and Password");
					}
				}
			}
			
			
		};
		xhttp.open("POST", "../cgi-bin/userAuth.py?user="+user, true);
		xhttp.send(fd);
	}
}


function movetoMainPage()
{
	var Appname = $('#slt_app :selected').text();
	localStorage.setItem("ipm_appname",Appname);
	window.location = 'Main.html';				
}


// function to validate the username and password field
function isValidCredntial()
{
	//var re = new RegExp("^[a-z][a-z0-9_]*");
	if(document.getElementById("Txt_Username").value.trim() == "")
	{
		alert("Please enter 'User Name'");
		return false;
	}
	else if(document.getElementById("Txt_Password").value.trim() == "")
	{
		alert("Please enter 'Password'");
		return false;
	}
	else
	{
		return true;
	}
}

// function to login error message
function login_error() {
	alert("Enter valid login credential");
}