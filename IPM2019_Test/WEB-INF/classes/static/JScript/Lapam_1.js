/*************** LAPAM Page **********************/
var Output_StringPath = "";
var startdateval ="";
var field_data = [];
var fieldval = "";
var usagepattern_chk = false, datacomb_chk = false, failureanal_chk = false, businesstran_chk = false;
var uploaded_filepath =""
var testalready_exists = /TAP 0/g;
var sapfile_chk = /FUP 0/;

//function to bind user name
function bindUserDetail()
{
	document.getElementById("logged_user").innerHTML = "<span class='glyphicon glyphicon-user'></span> " + localStorage.getItem("ipm_username");
	document.getElementById("logged_app").innerHTML = "<span class='glyphicon glyphicon-briefcase'></span> " + localStorage.getItem("ipm_appname");
	document.getElementById("log_report").style.display = "none";
	document.getElementById("fg_online").className = "off_ball";
}

//function to validate report name field
// function created as part of story ST05
function isValidreportname()
{ 
	var reportname_regex = /^[a-zA-Z0-9]{1}[0-9a-zA-Z_-]*$/;	
	var count_val = sessionStorage.getItem("LogType").split("\n");
	if(document.getElementById("Txt_reportname").value.trim() == "")
	{
		alert("Please enter 'Report Name'");
		return false;
	}
	else if(!document.getElementById("Txt_reportname").value.trim().match(reportname_regex))
	{
		alert("Please enter valid Report name");
		return false;
	}	
	else if(count_val.length > 0)
	{
		var failcount = 0;
		for (var file_i = 0; file_i < count_val.length; file_i++) {			
			var file_id = "Dlg_SMfile_" + file_i
			if(document.getElementById(file_id).value == "")
			{
				failcount++; 
			}
			else{
				if (document.getElementById(file_id).value.lastIndexOf(".") > 0) {
					fileExtension = document.getElementById(file_id).value.substring(document.getElementById(file_id).value.lastIndexOf(".") + 1, document.getElementById(file_id).value.length);
					
					if (fileExtension.toLowerCase() == "csv" || fileExtension.toLowerCase() == "xls" || fileExtension.toLowerCase() == "xlsx" || fileExtension.toLowerCase() == "zip" ||fileExtension.toLowerCase() == "log" ||fileExtension.toLowerCase() == "txt" ||fileExtension.toLowerCase() == "xml"||fileExtension.toLowerCase() == "001") {
						return true;
					}
					else {
						alert("Kindly select a valid file for upload");
						return false;
					}
				}
			}
		}
		if(failcount == count_val.length)
		{
			alert("Kindly upload a file to proceed further");
			return false;
		}
		else{
			return true;
		}
	}
	else
	{
		return true;
	}
}

// function to fetch report details
// function created as part of story ST06
function getExistingReportname()
{
	var xhttp = new XMLHttpRequest();
	var fd = new FormData();
	fd.append("prj_id",localStorage.getItem("ipm_appname"));	
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			var outputVal = this.responseText.trim();
			var output_mat = outputVal.match(/\[\]/g);
			if(outputVal != "" && output_mat != "[]")
			{
				var test_drp = document.getElementById("Drp_View_reportname");	
				var test_length = test_drp.options.length;
				for (i = 0; i < test_length; i++) {
				  test_drp.options[0] = null;
				}
				var project_name_arr = this.responseText.split("'");
				for (var prj_i=1; prj_i<project_name_arr.length ; prj_i=prj_i+2) {					
					var option = document.createdElement("option");
					option.text = project_name_arr[prj_i];
					test_drp.add(option, test_drp[0]);
				} 
			}
			else{
				alert("Kindly analyze a log file to view this page");
				document.getElementById("Btn_exist_proceed").disabled = true;
			}
		}
     };
     xhttp.open("POST", "../cgi-bin/getReportName.py",true);
     xhttp.send(fd);
}

// function to call on Home click
// function created as part of story ST04
function Logout()
{
	parent.window.location.href = "Home.html";
	localStorage.setItem("ipm_username","");
	localStorage.setItem("ipm_UserId","");
	localStorage.setItem("ipm_appname","");
	localStorage.setItem("rep_id","");	
	localStorage.setItem("reportname","");	
}
 
//function for uploading files
//function created as part of ST007
function upload_files(){
	if(isValidreportname())
	{	
		
		document.getElementById('top').style.display = 'block';
		var xhttp = new XMLHttpRequest();	
		var fd = new FormData();		
		var log_type=[];
		var log_files=[];
		var reportname = document.getElementById('Txt_reportname').value;
		localStorage.setItem("reportname",reportname);
		fd.append("Txt_reportname",reportname);
		fd.append("username",localStorage.getItem("ipm_username"));
		fd.append("userid",localStorage.getItem("ipm_UserId"));
		//var uploadedFile_len = document.getElementById("Dlg_filename").files.length;
		var count_val = sessionStorage.getItem("LogType").split("\n");
		
		xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			if(this.responseText.trim().toString() != "TAP 0, Report name already exists")
			{
				alert("Log Uploaded Successfully - Proceed to Pattern Match");
				document.getElementById('top').style.display = 'none';
				localStorage.setItem("uploaded_StringPath",this.responseText.toString().trim());
				document.getElementById('Txt_reportname').disabled = true;
				document.getElementById('Btn_upload').className = 'btn btn-light';
				document.getElementById('Btn_MatchPatt').className = 'btn btn-primary';
				document.getElementById("Btn_MatchPatt").style.cursor = "pointer";
				document.getElementById('Btn_MatchPatt').disabled = false;
				document.getElementById('Btn_upload').disabled = true;
				document.getElementById("Btn_upload").style.cursor = "not-allowed";
				//document.getElementById('Dlg_filename').disabled = true;
				document.getElementById("Btn_MatchPatt").focus();
				document.getElementById("log_report").style.display = "block";
				document.getElementById("log_report").innerHTML = "<span class='glyphicon glyphicon-file'></span> " + document.getElementById('Txt_reportname').value;
				//PatternMapping();
				if (localStorage.getItem("logtype_filename").split("-")[0] == "STAD")	
					{parse_sap()}
			}
			else
			{
				alert("Reportname already exists");
				document.getElementById('top').style.display = 'none';
				document.getElementById("Txt_reportname").focus();
				document.getElementById('Txt_reportname').disabled = false;
				document.getElementById('Btn_upload').className = 'btn btn-primary';
				document.getElementById('Btn_MatchPatt').className = 'btn btn-light';
				document.getElementById("Btn_MatchPatt").style.cursor = "not-allowed";
				document.getElementById("Btn_upload").style.cursor = "pointer";
				document.getElementById('Btn_MatchPatt').disabled = true;
				document.getElementById('Btn_upload').disabled = false;
			}
		}
		else if (this.readyState == 4 && this.status == 208) {
			alert("Fail to upload");
			document.getElementById('top').style.display = 'none';
			document.getElementById("Txt_reportname").focus();
			document.getElementById('Txt_reportname').disabled = false;
			document.getElementById('Btn_upload').className = 'btn btn-primary';
			document.getElementById('Btn_MatchPatt').className = 'btn btn-light';
			document.getElementById("Btn_MatchPatt").style.cursor = "not-allowed";
			document.getElementById("Btn_upload").style.cursor = "pointer";			
			document.getElementById('Btn_MatchPatt').disabled = true;		
			document.getElementById('Btn_upload').disabled = false;
			//document.getElementById('Dlg_filename').disabled = false;
		}
		};
		if(localStorage.getItem("ipm_appname") == "BOT")
		{			
			fd.append("NFR",document.getElementById('Dlg_SMfile_1').value);
			fd.append("Dlg_jsonfilename", document.getElementById("SMfile_1").files[0]);
			fd.append("Dlg_filename", document.getElementById("Dlg_SMfile_0").files[0]);	
			log_type.push("STAD-merged_output.csv");	
			log_type.push("NFR-NFR.csv");				
			fd.append("Log_type", log_type);
			localStorage.setItem("logtype_filename",log_type);
			xhttp.open("POST", "../cgi-bin/genNFR.py?user="+localStorage.getItem('username')+"&logname="+reportname+"", true);
		}
		else{
			for (var file_i = 0; file_i < count_val.length; file_i++) {
				var file_id = "Dlg_SMfile_" + file_i
				if(document.getElementById(file_id).value != "")
				{
					log_type.push(count_val[file_i].trim() + "-" + document.getElementById(file_id).files[0].name);
					//alert(log_type);
					//log_files.push();
					fd.append("Dlg_filename", document.getElementById(file_id).files[0]);
					//alert(log_files);
				}
			}
			fd.append("Log_type", log_type);
			localStorage.setItem("logtype_filename",log_type);
			xhttp.open("POST", "../cgi-bin/upload.py?user="+localStorage.getItem('username')+"&logname="+reportname+"", true);
		}
		xhttp.send(fd);
	}
}

	
function parse_sap()	
{   	
    //if(document.getElementById('chk_serverMet').checked)	
    //{	
        //parent.document.getElementById('top').style.display = 'block';	
        var xhttp = new XMLHttpRequest();	
        var fd = new FormData();	
        fd.append("Txt_testname",document.getElementById('Txt_reportname').value);	
        fd.append("userid",localStorage.getItem("ipm_UserId"));	
			
		if(document.getElementById('format_chx').checked)	
		{	
			localStorage.setItem("isStdFormat","German")	
				
		}	
		else	
		{	
			localStorage.setItem("isStdFormat","")	
		}		
			
		if(localStorage.getItem("ipm_appname") == "BOT")
		{
			fd.append("Stad_dir","merged_output.csv");
			fd.append("NFR_dir","NFR.csv");	
			fd.append("file_format","");	
		}
		else{			
			fd.append("Stad_dir",document.getElementById("Dlg_SMfile_0").files[0].name);
			fd.append("NFR_dir",document.getElementById("Dlg_SMfile_1").files[0].name);	
			fd.append("file_format",localStorage.getItem("isStdFormat"));	
		}
        
        fd.append("Server_dir","");	
        fd.append("prjid",localStorage.getItem("rep_id"));
		
		//fd.append("file_format","German");	
        xhttp.onreadystatechange = function() {      	
            if (this.readyState == 4 && this.status == 200) {	
                	
            }	
        };	
        xhttp.open("POST", "../cgi-bin/parse_SAP.py", true);	
        xhttp.send(fd);	
    /*}	
    else	
    {	
        alert("Please upload Servermetrics file to view");	
    }*/	
}

// function on click 'Pattern Match'
function PatternMapping()
{	
	document.getElementById('top').style.display = 'block';
	var xhttp = new XMLHttpRequest();
	var fd = new FormData();
	var isNoMatch = false;
	var reportname = document.getElementById('Txt_reportname').value;
	localStorage.setItem("reportname",reportname);	
	sessionStorage.setItem("isExisting", "false");
	fd.append("user_id",localStorage.getItem("ipm_UserId"));
	fd.append("rep_id","empty");
	fd.append("report_name",reportname);
	fd.append("function_name","mapping");
	fd.append("app_name",localStorage.getItem("ipm_appname"));
	/*if(localStorage.getItem("ipm_appname") == "BOT")
	{
		fd.append("uploaded_filename","STAD-merged_output.csv");		
	}
	else{
		fd.append("uploaded_filename",localStorage.getItem("logtype_filename"));
	}*/
	fd.append("uploaded_filename",localStorage.getItem("logtype_filename"));
	fd.append("mode","OFL");
	fd.append("Imp_id","empty");
	fd.append("observation","empty");
	fd.append("imp_name","empty");
	fd.append("start_date","empty");
	fd.append("end_date","empty");
	fd.append("search_key","empty");	
	
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {				
			document.getElementById('top').style.display = 'none';
			//alert(this.responseText.toString());
			document.getElementById('Txt_reportname').disabled = false;
			document.getElementById('Btn_upload').className = 'btn btn-primary';
			document.getElementById('Btn_MatchPatt').className = 'btn btn-light';
			document.getElementById("Btn_MatchPatt").style.cursor = "not-allowed";
			document.getElementById("Btn_upload").style.cursor = "pointer";
			document.getElementById('Btn_MatchPatt').disabled = true;
			document.getElementById('Btn_upload').disabled = false;
			document.getElementById("Txt_reportname").focus();			
			sessionStorage.setItem("Imperative_name", "");
			sessionStorage.setItem("Imperative_Id", "");
			if(this.responseText.toString() != "")
			{
				var response_list = this.responseText.toString().split("\n");
				var rep_id = "";
				for (var rep_i=1; rep_i<response_list.length-1 ; rep_i=rep_i+1)
				{
					if(response_list[rep_i].toString().trim().split(" - ")[0] == "Rep_id")
					{
						rep_id = response_list[rep_i].toString().trim().split(" - ")[1];
					}
					if(response_list[rep_i].toString().trim() == "No Patterns got match")
					{
						isNoMatch = true;
					}
				}
				var imp_string = response_list[response_list.length - 2];
				localStorage.setItem("rep_id",rep_id);	
				localStorage.setItem("WorkstreamName","All Workstreams");
			}			
			if(!isNoMatch)
			{		
				alert("Pattern Mined from the Log - Proceed to Imperative Views");		
				load_imperatives(imp_string);
			}
			else{
				alert("Pattern Mined from the Log - No Patterns are matched");
			}
		}
	};
	xhttp.open("POST", "../cgi-bin/Decrypt_PyFile.py", true);
	xhttp.send(fd);
}

// function to load imperatives
function load_imperatives(imp_string)
{	
	localStorage.setItem("Imp_List",imp_string);	
	sessionStorage.setItem("isExisting", "false");
	sessionStorage.setItem("isOnline", "false");
	document.getElementById("Div_NewQual").style.display = "none";
	document.getElementById("Div_ViewQual").style.display = "none";
	document.getElementById("div_imp_page").style.display = "block";	
	document.getElementById("div_imp_page").innerHTML = '<object type="text/html" style = "width:100%; height:700px;" data="Imperatives.html" ></object>';
}

// function to call on 'Get started'
function getStarted()
{
	var xhttp = new XMLHttpRequest();
	var fd = new FormData();
	document.getElementById('top').style.display = 'block';	
	document.getElementById("log_report").innerHTML = "";
	fd.append("app_name",localStorage.getItem("ipm_appname"));
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById('top').style.display = 'none';
			var outputVal = this.responseText.trim();
			sessionStorage.setItem("LogType", outputVal);
			if(outputVal != "")
			{		
				add_fields(outputVal);
				document.getElementById("Div_HomeHeader").style.display = "none";
				document.getElementById("Div_NewQual").style.display = "block";	
				document.getElementById("Div_ViewQual").style.display = "none";
				document.getElementById("div_imp_page").style.display = "none";
				document.getElementById("Txt_reportname").value = "";
				document.getElementById("Txt_reportname").disabled = false;			
				document.getElementById("Txt_reportname").focus();
				document.getElementById('Btn_upload').className = 'btn btn-primary';
				document.getElementById('Btn_MatchPatt').className = 'btn btn-light';
				document.getElementById("Btn_MatchPatt").style.cursor = "not-allowed";
				document.getElementById("Btn_upload").style.cursor = "pointer";
				document.getElementById('Btn_MatchPatt').disabled = true;
				document.getElementById('Btn_upload').disabled = false;
				document.getElementById("div_online_page").style.display = "none";	
				document.getElementById("fg_online").className = "off_ball";	
			}
			else{
				alert("Kindly analyze a log file to view this page");
				document.getElementById("Btn_exist_proceed").disabled = true;
			}
		}
     };
     xhttp.open("POST", "../cgi-bin/getLogType.py",true);
     xhttp.send(fd);
	//document.getElementById("StatusMode_lbl").innerHTML = "OFFLINE";
	//document.getElementById("togBtn").checked = false;
}


//function to add a dynamic input and browse file
function add_fields(outputVal){
	
	$('#Div_Addditional').empty();
	var e = document.getElementById('slt_count');
	var count_val = outputVal.split("\n");
	if(localStorage.getItem("ipm_appname") == "BOT")
	{
		document.getElementById("fs_atr").style.display = "block";
		var additional_inputfile = document.createElement('input');
		var file_id = "Dlg_SMfile_0"
		var lbl_id = "lbl0"
		additional_inputfile.setAttribute("id", file_id); 
		additional_inputfile.setAttribute("type", "file"); 
		additional_inputfile.setAttribute("name", "file"); 
		var adl_inputtextfile = document.createElement('select');
		var additional_labelfile = document.createElement('label');	
		additional_labelfile.setAttribute("id", lbl_id);
		var additional_inputtextfile = document.createElement('input');
		additional_inputtextfile.setAttribute("type", "text");
		document.getElementById("Div_Addditional").appendChild(additional_labelfile);
		document.getElementById("Div_Addditional").appendChild(additional_inputfile);
		var new_line = document.createElement('br');
		document.getElementById("Div_Addditional").appendChild(new_line);
		var new_line1 = document.createElement('br');
		document.getElementById("Div_Addditional").appendChild(new_line1);
		document.getElementById(lbl_id).style.cssFloat = "left";
		document.getElementById(lbl_id).style.width = "150px";
		document.getElementById(file_id).style.marginLeft = "10px";
		document.getElementById(file_id).style.cssFloat = "left"; 
		document.getElementById(file_id).style.top = '10px';
		document.getElementById(lbl_id).innerHTML = "STAD Type *: ";
		
		document.getElementById("fs_atr").style.display = "block";
		var additional_inputfile = document.createElement('input');
		var file_id = "Dlg_SMfile_1"
		var lbl_id = "lbl1"
		additional_inputfile.setAttribute("id", file_id); 
		additional_inputfile.setAttribute("type", "text"); 
		additional_inputfile.setAttribute("name", "file"); 
		var additional_labelfile = document.createElement('label');	
		additional_labelfile.setAttribute("id", lbl_id);
		document.getElementById("Div_Addditional").appendChild(additional_labelfile);
		document.getElementById("Div_Addditional").appendChild(additional_inputfile);
		var new_line = document.createElement('br');
		document.getElementById("Div_Addditional").appendChild(new_line);
		var new_line1 = document.createElement('br');
		document.getElementById("Div_Addditional").appendChild(new_line1);
		document.getElementById(lbl_id).style.cssFloat = "left";
		document.getElementById(lbl_id).style.width = "150px";
		document.getElementById(file_id).style.marginLeft = "10px";
		document.getElementById(file_id).style.cssFloat = "left"; 
		document.getElementById(file_id).style.top = '10px';
		document.getElementById(lbl_id).innerHTML = "NFR Value *: ";
		
		document.getElementById("fs_atr").style.display = "block";
		var additional_inputfile = document.createElement('input');
		var file_id = "SMfile_1"
		var lbl_id = "lbl2"
		additional_inputfile.setAttribute("id", file_id); 
		additional_inputfile.setAttribute("type", "file"); 
		additional_inputfile.setAttribute("name", "file");
		additional_inputfile.setAttribute("accept","application/json");
		var adl_inputtextfile = document.createElement('select');
		var additional_labelfile = document.createElement('label');	
		additional_labelfile.setAttribute("id", lbl_id);
		var additional_inputtextfile = document.createElement('input');
		additional_inputtextfile.setAttribute("type", "text");
		document.getElementById("Div_Addditional").appendChild(additional_labelfile);
		document.getElementById("Div_Addditional").appendChild(additional_inputfile);
		var new_line = document.createElement('br');
		document.getElementById("Div_Addditional").appendChild(new_line);
		var new_line1 = document.createElement('br');
		document.getElementById("Div_Addditional").appendChild(new_line1);
		document.getElementById(lbl_id).style.cssFloat = "left";
		document.getElementById(lbl_id).style.width = "150px";
		document.getElementById(file_id).style.marginLeft = "10px";
		document.getElementById(file_id).style.cssFloat = "left"; 
		document.getElementById(file_id).style.top = '10px';
		document.getElementById(lbl_id).innerHTML = "JSON File: ";
		
	}
	else{
		for (var file_i = 0; file_i < count_val.length; file_i++) {
			document.getElementById("fs_atr").style.display = "block";
			var additional_inputfile = document.createElement('input');
			var file_id = "Dlg_SMfile_" + file_i
			var lbl_id = "lbl" + file_i
			additional_inputfile.setAttribute("id", file_id); 
			additional_inputfile.setAttribute("type", "file"); 
			additional_inputfile.setAttribute("name", "file"); 
			var adl_inputtextfile = document.createElement('select');
			var additional_labelfile = document.createElement('label');	
			additional_labelfile.setAttribute("id", lbl_id);
			var additional_inputtextfile = document.createElement('input');
			additional_inputtextfile.setAttribute("type", "text");
			document.getElementById("Div_Addditional").appendChild(additional_labelfile);
			document.getElementById("Div_Addditional").appendChild(additional_inputfile);
			var new_line = document.createElement('br');
			document.getElementById("Div_Addditional").appendChild(new_line);
			var new_line1 = document.createElement('br');
			document.getElementById("Div_Addditional").appendChild(new_line1);
			document.getElementById(lbl_id).style.cssFloat = "left";
			document.getElementById(lbl_id).style.width = "150px";
			document.getElementById(file_id).style.marginLeft = "10px";
			document.getElementById(file_id).style.cssFloat = "left"; 
			document.getElementById(file_id).style.top = '10px';
			document.getElementById(lbl_id).innerHTML = count_val[file_i] + " Type: ";
		}
	}	
	/*var adl_inputbtn = document.createElement('input');
	adl_inputbtn.setAttribute("id", "btn_upload"); 
	adl_inputbtn.setAttribute("type", "button");
	adl_inputbtn.setAttribute("value", "Upload");
	adl_inputbtn.setAttribute("onclick", "upload_artifact()");
	document.getElementById("Div_Addditional").appendChild(adl_inputbtn);
	document.getElementById("btn_upload").style.top = '30px';
	document.getElementById("btn_upload").style.marginLeft = '300px';
	document.getElementById("btn_upload").style.marginBottom = '20px';*/
}

// function to fetch reports on click on 'Mine'
function getmine()
{
	document.getElementById("fg_online").className = "off_ball";	
	//document.getElementById("StatusMode_lbl").innerHTML = "OFFLINE";
	document.getElementById("Div_HomeHeader").style.display = "none";
	document.getElementById("Div_NewQual").style.display = "none";
	document.getElementById("Div_ViewQual").style.display = "block";
	document.getElementById("div_imp_page").style.display = "none";	
	document.getElementById("div_online_page").style.display = "none";	
	document.getElementById("Txt_reportname").value = "";
	document.getElementById("Txt_reportname").disabled = false;
	//document.getElementById("Dlg_filename").value = "";
	document.getElementById('Btn_upload').disabled = false;
	//document.getElementById("Dlg_filename").disabled = false;
	fetchReports();
}

// function to fetch report details
function fetchReports()
{
	var xhttp = new XMLHttpRequest();
	var fd = new FormData();
	document.getElementById('top').style.display = 'block';	
	fd.append("user_name",localStorage.getItem("ipm_username"));
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById('top').style.display = 'none';
			var outputVal = this.responseText.trim();
			if(outputVal != "")
			{
				var test_drp = document.getElementById("slt_view");	
				var test_length = test_drp.options.length;
				for (i = 0; i < test_length; i++) {
				  test_drp.options[0] = null;
				}
				var project_name_arr = this.responseText.split("\n");
				for (var prj_i=1; prj_i<project_name_arr.length-1 ; prj_i=prj_i+1)
				{					
					var option = document.createElement("option");
					option.text = project_name_arr[prj_i].split(",")[1];
						test_drp.add(option, test_drp[0]);
				} 
			}
			else{
				alert("Kindly analyze a log file to view this page");
				document.getElementById("Btn_exist_proceed").disabled = true;
			}
		}
     };
     xhttp.open("POST", "../cgi-bin/getLogNameForUser.py",true);
     xhttp.send(fd);
}

// function to get online data from elasticsearch
function getOnlineData()
{
	document.getElementById("fg_online").className = "ball";
	document.getElementById("Div_HomeHeader").style.display = "none";
	document.getElementById("Div_NewQual").style.display = "none";
	document.getElementById("Div_ViewQual").style.display = "none";
	document.getElementById("div_imp_page").style.display = "none";	
	document.getElementById("div_online_page").style.display = "block";	
	document.getElementById("Txt_reportname").value = "";
	document.getElementById("Txt_reportname").disabled = false;
	//document.getElementById("Dlg_filename").value = "";
	document.getElementById('Btn_upload').disabled = false;
	//document.getElementById("Dlg_filename").disabled = false;
	fetchOnlineImp();
}

// function to fetch online report details
function fetchOnlineImp()
{
	var xhttp = new XMLHttpRequest();
	var fd = new FormData();	
	sessionStorage.setItem("isOnline", "true");
	document.getElementById('top').style.display = 'block';
	fd.append("user_id",localStorage.getItem("ipm_UserId"));
	fd.append("appname",localStorage.getItem("ipm_appname"));
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById('top').style.display = 'none';							
			document.getElementById("Div_NewQual").style.display = "none";
			document.getElementById("Div_ViewQual").style.display = "none";
			document.getElementById("div_imp_page").style.display = "block";	
			document.getElementById("div_imp_page").innerHTML = '<object type="text/html" style = "width:100%; height:700px;" data="Imperatives.html" ></object>';
			//document.getElementById("log_report").innerHTML = "<span class='glyphicon glyphicon-file'></span> ONLINE";
			document.getElementById("log_report").innerHTML = "";
			localStorage.setItem("Imp_List",this.responseText.toString());
		}
     };
     xhttp.open("POST", "../cgi-bin/onlineGetImperative.py",true);
     xhttp.send(fd);
}

// function to fetch list of imperatives for the report
function fetchViewDetails()
{
	var xhttp = new XMLHttpRequest();
	var fd = new FormData();
	sessionStorage.setItem("isExisting", "true");
	sessionStorage.setItem("Imperative_name", "");
	sessionStorage.setItem("Imperative_Id", "");
	sessionStorage.setItem("isOnline", "false");
	fd.append("user_id",localStorage.getItem("ipm_UserId"));
	var e = document.getElementById('slt_view');
	var report_name = e.options[e.selectedIndex].text;	
	fd.append("report_name",report_name);	
	localStorage.setItem("reportname",report_name);
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			var response_txt = this.responseText.split("\n");
			$( "#div_imperatives" ).empty();
			var rep_id = response_txt[0].split("REP_ID - ")[1].toString().trim();
			localStorage.setItem("WorkstreamName","All Workstreams");
			localStorage.setItem("rep_id",rep_id);							
			document.getElementById("Div_NewQual").style.display = "none";
			document.getElementById("Div_ViewQual").style.display = "none";
			document.getElementById("log_report").style.display = "block";
			document.getElementById("log_report").innerHTML = "<span class='glyphicon glyphicon-file'></span> " + report_name;
			document.getElementById("div_imp_page").style.display = "block";	
			document.getElementById("div_imp_page").innerHTML = '<object type="text/html" style = "width:100%; height:700px;" data="Imperatives.html" ></object>';
			localStorage.setItem("Imp_List",this.responseText.toString());
		}
     };
     xhttp.open("POST", "../cgi-bin/getImperativesForReports.py",true);
     xhttp.send(fd);
}

// function to get list of imperatives 
function getImperativesList()
{
	var top_val = 20;
	sessionStorage.setItem("isForensic", "false");
	localStorage.setItem("online_tp", "false");
	localStorage.setItem("Selectedtime", "");
	if(sessionStorage.getItem("isOnline") =="true")
	{
		$('#daterange_onl').show();
	}
	else{
		$('#daterange_onl').hide();
	}
	if(sessionStorage.getItem("isExisting") =="true" || sessionStorage.getItem("isOnline") =="true")
	{		
		var imp_list = localStorage.getItem("Imp_List").split('\n');
		var link_data = "";
		for (var imp_i=1; imp_i<imp_list.length-1; imp_i = imp_i+1)
		{ 
			if(imp_list[imp_i].split(' - ')[0].trim().toUpperCase() != "IMP007")
			{
				if(imp_list[imp_i].split(' - ')[0].trim().toUpperCase() == "IMP016" || imp_list[imp_i].split(' - ')[0].trim().toUpperCase() == "IMP017" || imp_list[imp_i].split(' - ')[0].trim().toUpperCase() == "IMP018" || imp_list[imp_i].split(' - ')[0].trim().toUpperCase() == "IMP019" || imp_list[imp_i].split(' - ')[0].trim().toUpperCase() == "IMP020")
				{
					$('#download_btn').hide();
				}
				else{
					$('#download_btn').show();
				}
				
				top_val = top_val + 60;
				var link_color = imp_list[imp_i].split(' - ')[0]+'_bgcolor';
				var i_class = "fa "+imp_list[imp_i].split(' - ')[0]+" fa-fw fa-3x";
				link_data += '<a href="#" style="top: '+top_val+'px;" class="'+link_color+'" onclick="callImperatives(\''+imp_list[imp_i].split(' - ')[1].trim().toUpperCase()+'\', \''+imp_list[imp_i].split(' - ')[0].trim()+'\')"><i class="'+i_class+'" aria-hidden="true" style="font-size:20px"></i> '+imp_list[imp_i].split(' - ')[1]+'</a><br/>';
				//document.getElementById('Div_Imp_list').innerHTML = '<object type="text/html" style = "width:100%; height:100%" data="'+imp_list[imp_i].split(' - ')[0].trim()+'.html" ></object>'; 
				if(sessionStorage.getItem("isOnline") =="true" && imp_list[imp_i].split(' - ')[0].trim().toUpperCase() == "IMP004")
				{
					document.getElementById('Div_Imp_list').innerHTML = '<object type="text/html" style = "width:100%; height:100%" data="Anomaly.html" ></object>'; 
				}
				else{
					document.getElementById('Div_Imp_list').innerHTML = '<object type="text/html" style = "width:100%; height:100%" data="'+imp_list[imp_i].split(' - ')[0].trim()+'.html" ></object>'; 
				}
				document.getElementById('Hdr_imperative').innerHTML = imp_list[imp_i].split(' - ')[1].trim().toUpperCase();
				sessionStorage.setItem("Imperative_Id", imp_list[imp_i].split(' - ')[0].trim());
				document.getElementById('Div_Imp_list_img').style.backgroundImage =  "url('../images/"+imp_list[imp_i].split(' - ')[0].trim()+".png')";
				sessionStorage.setItem("Imperative_name", imp_list[imp_i].split(' - ')[1].trim().toLowerCase());
			}
			else{
				if(sessionStorage.getItem("isOnline") =="false")
				{
					top_val = top_val + 60;
					var link_color = imp_list[imp_i].split(' - ')[0]+'_bgcolor';
					var i_class = "fa "+imp_list[imp_i].split(' - ')[0]+" fa-fw fa-3x";
					link_data += '<a href="#" style="top: '+top_val+'px;" class="'+link_color+'" onclick="callImperatives(\''+imp_list[imp_i].split(' - ')[1].trim().toUpperCase()+'\', \''+imp_list[imp_i].split(' - ')[0].trim()+'\')"><i class="'+i_class+'" style="font-size:20px"></i> '+imp_list[imp_i].split(' - ')[1]+'</a><br/>';
					document.getElementById('Div_Imp_list').innerHTML = '<object type="text/html" style = "width:100%; height:100%" data="'+imp_list[imp_i].split(' - ')[0].trim().toUpperCase()+'.html" ></object>'; 
					document.getElementById('Hdr_imperative').innerHTML = imp_list[imp_i].split(' - ')[1].trim().toUpperCase();
					sessionStorage.setItem("Imperative_Id", imp_list[imp_i].split(' - ')[0].trim());
					document.getElementById('Div_Imp_list_img').style.backgroundImage =  "url('../images/"+imp_list[imp_i].split(' - ')[0].trim()+".png')";
					sessionStorage.setItem("Imperative_name", imp_list[imp_i].split(' - ')[1].trim().toLowerCase());
				}
			}
		}
		document.getElementById('Div_Imperative_sidenav').innerHTML = link_data;
	}
	else{
		var imp_list = localStorage.getItem("Imp_List").split('\'');
		var link_data = "";
		for (var imp_i=1; imp_i<imp_list.length; imp_i = imp_i+2)
		{ 
			top_val = top_val + 60;
			var link_color = imp_list[imp_i].split('-')[0]+'_bgcolor';
			var i_class = "fa "+imp_list[imp_i].split('-')[0]+" fa-fw fa-3x";
			link_data += '<a href="#" style="top: '+top_val+'px;" class="'+link_color+'" onclick="callImperatives(\''+imp_list[imp_i].split('-')[1].trim().toUpperCase()+'\', \''+imp_list[imp_i].split('-')[0]+'\')"><i class="'+i_class+'" style="font-size:20px"></i> '+imp_list[imp_i].split('-')[1]+'</a><br/>';
			document.getElementById('Div_Imp_list').innerHTML = '<object type="text/html" style = "width:100%; height:100%" data="'+imp_list[imp_i].split('-')[0].trim().toUpperCase()+'.html" ></object>'; 
			document.getElementById('Hdr_imperative').innerHTML = imp_list[imp_i].split('-')[1].trim().toUpperCase();
			sessionStorage.setItem("Imperative_Id", imp_list[imp_i].split('-')[0].trim());
			document.getElementById('Div_Imp_list_img').style.backgroundImage =  "url('../images/"+imp_list[imp_i].split('-')[0].trim()+".png')";
			sessionStorage.setItem("Imperative_name", imp_list[imp_i].split('-')[1].trim().toLowerCase());
		}
		document.getElementById('Div_Imperative_sidenav').innerHTML = link_data;
	}
}

// display imperatives
function callImperatives(Imp_val, Imp_id)
{
	sessionStorage.setItem("Imperative_name", Imp_val.toLowerCase());
	sessionStorage.setItem("Imperative_Id", Imp_id);	
	sessionStorage.setItem("isForensic", "false");
    document.getElementById("TA_Obs").style.display = "block";
    document.getElementById("Lbl_observation").style.display = "block";
	document.getElementById('Div_Imp_list_img').style.backgroundImage =  "url('../images/"+sessionStorage.getItem("Imperative_Id")+".png')";
	if(sessionStorage.getItem("isOnline") =="true" && Imp_id == "IMP004")
	{
		document.getElementById('Div_Imp_list').innerHTML = '<object type="text/html" style = "width:100%; height:100%" data="Anomaly.html" ></object>'; 
	}
	else{
		document.getElementById('Div_Imp_list').innerHTML = '<object type="text/html" style = "width:100%; height:100%" data="'+Imp_id+'.html" ></object>';
	}	 
	document.getElementById('Hdr_imperative').innerHTML = Imp_val.toUpperCase();
}

// get Observation details for the corresponding imperatives
function getObservation()
{
	parent.document.getElementById("Lbl_observation").innerHTML = "";
	parent.document.getElementById("TA_Obs").value = "";
	//document.getElementById('Div_Imp_list_img').style.backgroundImage =  "url('../images/"+sessionStorage.getItem("Imperative_name")+".png')";
	if(sessionStorage.getItem("isForensic") =="true" || sessionStorage.getItem("isOnline") =="true")
	{		
		parent.document.getElementById("TA_Obs").style.display = "none";
		parent.document.getElementById("Lbl_observation").style.display = "none";
		parent.document.getElementById("Lbl_char").style.display = "none";
		if(sessionStorage.getItem("isOnline") =="true")
		{
			parent.document.getElementById("Btn_save").style.display = "none";
		}
		else{
			parent.document.getElementById("Btn_save").style.display = "block";
		}
	}
	else{
		parent.document.getElementById("TA_Obs").style.display = "block";
		parent.document.getElementById("Lbl_observation").style.display = "block";
		parent.document.getElementById("Btn_save").style.display = "block";		
		parent.document.getElementById("Lbl_char").style.display = "block";
	}
	//if(sessionStorage.getItem("isExisting") =="true")
	//{
		var xhttp = new XMLHttpRequest();
		var fd = new FormData();
		sessionStorage.setItem("isExisting", "true");
		fd.append("user_id",localStorage.getItem("ipm_UserId"));
		fd.append("rep_id",localStorage.getItem("rep_id"));
		fd.append("Imperative_Id",sessionStorage.getItem("Imperative_Id"));
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {				
				var recommend_str = "";
				var obs_str = "";
				if(this.responseText.toString() != "")
				{
					var res_text = this.responseText;
					res_text = res_text.replace("(\"","(\'");
					res_text = res_text.replace("%\",","%\',");
					var response_arr = res_text.split("\'");
					console.log(response_arr);
					console.log(response_arr[1]);
					if(response_arr[1] != "")
					{
						var obs_response_txt = response_arr[1].split("\\n");
						for (var obs_j=0; obs_j<obs_response_txt.length; obs_j=obs_j+1)
						{ 
							if(obs_str != "")
							{
								obs_str = obs_str + "\n" + obs_response_txt[obs_j];
							}
							else{
								obs_str = obs_response_txt[obs_j];
							}
						}
						parent.document.getElementById("Lbl_observation").innerHTML = obs_str;		
					}
					if(response_arr[3] != "")
					{
						console.log(response_arr);
						console.log(response_arr[3]);
						var response_txt = response_arr[3].split("\\n");
						console.log(response_txt);
						for (var obs_i=0; obs_i<response_txt.length; obs_i=obs_i+1)
						{ 
							if(recommend_str != "")
							{
								recommend_str = recommend_str + "\n" + response_txt[obs_i];
							}
							else{
								recommend_str = response_txt[obs_i];
							}
						}				
						parent.document.getElementById("TA_Obs").value = recommend_str;
					}
				}				
			}
		 };
		 xhttp.open("POST", "../cgi-bin/getObservations.py",true);
		 xhttp.send(fd);
	//}
}

// function - save the observations for the corresponding imperatives
function saveObservation()
{
	if(sessionStorage.getItem("isForensic") =="false")
	{	
		var xhttp = new XMLHttpRequest();	
		var fd = new FormData();
		sessionStorage.setItem("isExisting", "true");
		fd.append("user_id",localStorage.getItem("ipm_UserId"));
		fd.append("rep_id",localStorage.getItem("rep_id"));
		fd.append("Imperative_Id",sessionStorage.getItem("Imperative_Id"));
		fd.append("Observation",document.getElementById("TA_Obs").value);
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				var response_txt = this.responseText.split("\n");	
				alert("Observation updated.");
			}
		 };
		 xhttp.open("POST", "../cgi-bin/saveObservations.py",true);
		 xhttp.send(fd);
	}
	else{
		var xhttp = new XMLHttpRequest();	
		var fd = new FormData();
		sessionStorage.setItem("isExisting", "true");
		fd.append("user_id",localStorage.getItem("ipm_UserId"));
		fd.append("rep_id",localStorage.getItem("rep_id"));		
		fd.append("description",document.getElementById("Div_Imp_list").childNodes[0].contentDocument.body.childNodes[1].value);
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				var response_txt = this.responseText.split("\n");	
				alert("Summary report updated.");
			}
		 };
		 xhttp.open("POST", "../cgi-bin/saveForensicData.py",true);
		 xhttp.send(fd);
	}
}

function getForensicData()
{
	sessionStorage.setItem("isForensic", "true");
	parent.document.getElementById("TA_Obs").style.display = "none";
	parent.document.getElementById("Lbl_observation").style.display = "none";
	parent.document.getElementById("Lbl_char").style.display = "none";
	if(sessionStorage.getItem("isExisting") =="true")
	{
		var xhttp = new XMLHttpRequest();
		var fd = new FormData();
		sessionStorage.setItem("isExisting", "true");
		fd.append("user_id",localStorage.getItem("ipm_UserId"));
		fd.append("rep_id",localStorage.getItem("rep_id"));
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				var response_txt = this.responseText.split("\n");
				var foren_str = "";
				for (var obs_i=0; obs_i<response_txt.length-1; obs_i=obs_i+1)
				{ 
					if(foren_str != "")
					{
						foren_str = foren_str + "\n" + response_txt[obs_i];
					}
					else{
						foren_str = response_txt[obs_i];
					}
				}
				document.getElementById("TA_FR").value = foren_str;				
			}
		 };
		 xhttp.open("POST", "../cgi-bin/getForensicData.py",true);
		 xhttp.send(fd);
	}
}

// function to download files on click 'Download' button
function clickDownload(){
	var filename = "";
	var Imp_val = sessionStorage.getItem("Imperative_Id");
	var report_folder = localStorage.getItem("ipm_UserId") + "_" + localStorage.getItem("rep_id");
	var file_name = localStorage.getItem("ipm_appname") + "_" + localStorage.getItem("reportname") + "_" + sessionStorage.getItem("Imperative_name");
	var online_file_name = localStorage.getItem("ipm_appname") + "_" + sessionStorage.getItem("Imperative_name");
	var current_date= new Date().getFullYear()+'-'+("0"+(new Date().getMonth()+1)).slice(-2)+'-'+("0"+new Date().getDate()).slice(-2);
	if(Imp_val == "IMP001")
	{
		if(sessionStorage.getItem("isOnline") =="true")
		{			
			if(localStorage.getItem("online_tp") == "false"){
				filename = "online\\"+online_file_name+"_ONL_"+current_date+".csv";
			}
			else{
				filename = "online\\"+online_file_name+"_TP_"+current_date+".csv";
			}
		}
		else {
		filename = "Reports\\" + report_folder + "\\"+file_name+".csv";
		}
	}
	else if(Imp_val == "IMP002" || Imp_val == "IMP005")
	{
		if(sessionStorage.getItem("isDrilldown") == "true")
		{
			if(sessionStorage.getItem("isOnline") =="true")
			{
				if(localStorage.getItem("online_tp") == "false"){
					filename = "online\\"+online_file_name+"_ONL_"+localStorage.getItem("serviceCall_selectedItem")+"_"+current_date+".csv";
				}
				else{
					filename = "online\\"+online_file_name+"_TP_"+localStorage.getItem("serviceCall_selectedItem")+"_"+current_date+".csv";
				}
			}
			else{
				filename = "Reports\\" + report_folder + "\\"+file_name+"_"+localStorage.getItem("serviceCall_selectedItem")+".csv";
			}
		}
		else
		{
			if(sessionStorage.getItem("isOnline") =="true")
			{			
				if(localStorage.getItem("online_tp") == "false"){
					filename = "online\\"+online_file_name+"_ONL_All_"+current_date+".csv";
				}
				else{
					filename = "online\\"+online_file_name+"_TP_All_"+current_date+".csv";
				}
			}
			else {
				filename = "Reports\\" + report_folder + "\\"+file_name+".csv";
			}
		}
	}
	else if(Imp_val == "IMP003")
	{
		if(localStorage.getItem("ipm_appname").toLowerCase() == "twa")
		{
			if(sessionStorage.getItem("isOnline") =="true")
			{			
				if(localStorage.getItem("online_tp") == "false"){
					filename = "online\\"+online_file_name+"_All_ONL_"+current_date+".csv";
				}
				else{
					filename = "online\\"+online_file_name+"_All_TP_"+current_date+".csv";
				}
			}
			else {
				filename = "Reports\\" + report_folder + "\\"+file_name+"_All.csv";
			}
		}
		else{
			filename = "Reports\\" + report_folder + "\\"+file_name+".csv";
		}
	}
	else if(Imp_val == "IMP004")
	{
		if(sessionStorage.getItem("isOnline") =="true")
		{			
			if(localStorage.getItem("online_tp") == "false"){
				filename = "online\\"+online_file_name+"_ONL_"+current_date+".csv";
			}
			else{
				filename = "online\\"+online_file_name+"_TP_"+current_date+".csv";
			}
		}
		else {
			filename = "Reports\\" + report_folder + "\\"+file_name+".csv";
		}
	}
	else if(Imp_val == "IMP006")
	{
		if(sessionStorage.getItem("isDrilldown") == "true")
		{
			if(sessionStorage.getItem("isOnline") =="true")
			{			
				if(localStorage.getItem("online_tp") == "false"){
					filename = "online\\"+online_file_name+"_ONL_"+sessionStorage.getItem("failurename")+"_"+current_date+".csv";
				}
				else{
					filename = "online\\"+online_file_name+"_TP_"+sessionStorage.getItem("failurename")+"_"+current_date+".csv";
				}
			}
			else {
				filename = "Reports\\" + report_folder + "\\"+file_name+"_"+sessionStorage.getItem("failurename")+".csv";
			}
		}
		else{
			if(sessionStorage.getItem("isOnline") =="true")
			{			
				if(localStorage.getItem("online_tp") == "false"){
					filename = "online\\"+online_file_name+"_ONL_AllFailures_"+current_date+".csv";
				}
				else{
					filename = "online\\"+online_file_name+"_TP_AllFailures_"+current_date+".csv";
				}
			}
			else {
				filename = "Reports\\" + report_folder + "\\"+file_name+"_AllFailures.csv";
			}
		}
	}
	else if(Imp_val == "IMP007")
	{
		filename = "Reports\\" + report_folder + "\\"+report_folder+"_summaryreport.txt";
	}
	/*else if(Imp_val == "IMP016")
	{
		filename = "online\\SAP\\IMP016.csv";
	}
	else if(Imp_val == "IMP017")
	{
		filename = "online\\SAP\\IMP016.csv";
	}
	else if(Imp_val == "IMP018")
	{
		filename = "Reports\\" + report_folder + "\\"+report_folder+"_summaryreport.txt";
	}
	else if(Imp_val == "IMP019")
	{
		filename = "Reports\\" + report_folder + "\\"+report_folder+"_summaryreport.txt";
	}
	else if(Imp_val == "IMP020")
	{
		filename = "Reports\\" + report_folder + "\\"+report_folder+"_summaryreport.txt";
	}*/
	else if(Imp_val == "IMP008")
	{
		if(localStorage.getItem("imp_tab") == "Usage")
		{
			if(sessionStorage.getItem("isOnline") =="true")
			{			
				if(localStorage.getItem("online_tp") == "false"){
					filename = "online\\"+online_file_name+"_ONL_"+localStorage.getItem("search_value")+"_"+current_date+".csv";
				}
				else{
					filename = "online\\"+online_file_name+"_TP_"+localStorage.getItem("search_value")+"_"+current_date+".csv";
				}
			}
			else {
				filename = "Reports\\" + report_folder + "\\"+file_name+"_"+localStorage.getItem("search_value")+".csv";
			}
		}
		if(localStorage.getItem("imp_tab") == "DataCombination")
		{
			if(sessionStorage.getItem("isOnline") =="true")
			{			
				if(localStorage.getItem("online_tp") == "false"){
					filename = "online\\"+online_file_name+"_ONL_"+ localStorage.getItem("serviceCall_selectedItem")+"_"+localStorage.getItem("search_value")+"_"+current_date+".csv";
				}
				else{
					filename = "online\\"+online_file_name+"_TP_"+ localStorage.getItem("serviceCall_selectedItem")+"_"+localStorage.getItem("search_value")+"_"+current_date+".csv";
				}
			}
			else {
				filename = "Reports\\" + report_folder + "\\"+file_name+"_"+ localStorage.getItem("serviceCall_selectedItem")+"_"+localStorage.getItem("search_value")+".csv";
			}
		}
	}		
	else if(Imp_val == "IMP016" || Imp_val == "IMP017" || Imp_val == "IMP018" || Imp_val == "IMP019")	
	{	
		filename = "online\\SAP\\" + Imp_val + ".csv";	
	}
	if(fileExists(filename))
	{
		if(Imp_val == "IMP007")
		{
			file_name = report_folder+"_summaryreport.txt";
			var element = document.createElement('a');
			  element.setAttribute('href', filename);
			  element.setAttribute('download', file_name);
			  element.style.display = 'none';
			  document.body.appendChild(element);
			  element.click();
			  document.body.removeChild(element);
		}
		else{
			window.open(filename, '_blank');
		}
	}
	else{
		alert("File does not exists");
	}
}

function fileExists(url) {
    if(url){
        var req = new XMLHttpRequest();
        req.open('GET', url, false);
        req.send();
        return req.status==200;
    } else {
        return false;
    }
}

/**** admin pages ****/
function CallAdminpages(htmlpage)
{
	document.getElementById("div_adminpage").innerHTML='<object type="text/html" style = "width:100%; height:100%" data="'+htmlpage+'" ></object>'; 
}