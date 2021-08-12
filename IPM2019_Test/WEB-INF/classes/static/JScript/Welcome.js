/*************** Welcome Page **********************/

// function to call on click New qualifier page
// function create as part of story ST05
function callNewQualifierPage()
{
	window.location = 'TCO.html';
	localStorage.setItem("QualContent","New");
	parent.ifm_header.contentWindow.document.getElementById("href_home").style.display = 'block';
}

// function to call on click existing qualifier page
// function create as part of story ST06
function callExistingQualifierPage()
{
	window.location = 'TCO.html';
	localStorage.setItem("QualContent","Existing");
	parent.ifm_header.contentWindow.document.getElementById("href_home").style.display = 'block';
}

//function to disable home link
function disableHomeLbl()
{
	parent.ifm_header.contentWindow.document.getElementById("href_home").style.display = 'none';
	parent.ifm_header.contentWindow.document.getElementById("lbl_user").innerHTML = localStorage.getItem("username") + ",";
}