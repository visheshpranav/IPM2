var tenuredata = "";
var nurseryata = "";
var GCdata = "";

var txt_filename = "";
var current_date =  new  Date().getFullYear() + '-' + ("0" + (new  Date().getMonth() + 1)).slice(-2) + '-' + ("0" + new  Date().getDate()).slice(-2);
if (sessionStorage.getItem("isOnline") == "true") {
	var filename = "";
	file_name = localStorage.getItem("ipm_appname") + "_" + sessionStorage.getItem("Imperative_name");
	if (localStorage.getItem("online_tp") == "false") {
		txt_filename = "online/" + file_name + "_ONL_HeapMemory_" + current_date + ".txt";
	} else {
		txt_filename = "online/" + file_name + "_TP_HeapMemory_" + current_date + ".txt";
	}
} else {
	var log_folder = localStorage.getItem("ipm_UserId") + "_" + localStorage.getItem("rep_id");
	var heap_file_name = localStorage.getItem("ipm_appname") + "_" + localStorage.getItem("reportname").toLowerCase() + "_HeapMemory.txt";
	//var filename = "Reports/"+log_folder+"/"+file_name+localStorage.getItem("ipm_appname") + "_" + localStorage.getItem("reportname").toLowerCase() + "_" + sessionStorage.getItem("Imperative_name")+ "_fail_response.txt";
	txt_filename = "Reports/" + log_folder + "/" + heap_file_name;
}

function goBack() {
	window.location.href = "IMP004.html";
}

function disableBackButton() {
	getObservation();
	if (sessionStorage.getItem("isOnline") == "true") {
		document.getElementById('Btn_back').style.display = 'none';
	} else {
		document.getElementById('Btn_back').style.display = 'block';
	}
}

function readTextFile() {
	//var file = "Reports/"+log_folder+"/"+heap_file_name;
	//var file = "Reports\\jun15_22_Anomaly.txt";
	var rawFile = new XMLHttpRequest();
	rawFile.open("GET", txt_filename, false);
	rawFile.setRequestHeader("Cache-Control", "no-cache");
	rawFile.setRequestHeader("Pragma", "no-cache");
	rawFile.onreadystatechange = function() {
		if (rawFile.readyState === 4) {
			if (rawFile.status === 200 || rawFile.status == 0) {
				var allText = rawFile.responseText;
				var ext_response_arr1 = allText.toString().split("\n");
				var ext_response_arr = allText.toString().split("=");
				console.log(ext_response_arr1);
				//console.log(ext_response_arr1[0].toString().split("=")[1].toString());
				//console.log(ext_response_arr[1].toString().substring(0, ext_response_arr[1].length - 6));
				usedtenuredata = "[" + ext_response_arr1[0].toString().split("=,")[1].toString() + "]";
				tenuredata = "[" + ext_response_arr1[1].toString().split("=,")[1].toString() + "]";
				nurseryata = "[" + ext_response_arr1[2].toString().split("=,")[1].toString() + "]";
				GCdata = "[" + ext_response_arr1[3].toString().split("=,")[1].toString() + "]";
				var obj = JSON.parse(GCdata);
				//console.log(obj);

			}

		}
	}
	rawFile.send();
}

'use strict';
$(function() {
	readTextFile();
	$.ajaxPrefilter(function(options, original_Options, jqXHR) {
		options.async = true;
	});
	requirejs.config({
		"baseUrl": "././JScript/",
		"paths": {
			"app": "././JScript/",
			'moment': 'moment.min',
			'underscore': 'underscore-min'
		}
	});

	require(['d3.chart'], function(d3Chart) {
		d3Chart.init({
			container: '#container',
			xDim: 'DateTime'
		});
		used_json_data = $.parseJSON(usedtenuredata);
		tenure_json_data = $.parseJSON(tenuredata);
		nursery_json_data = $.parseJSON(nurseryata);
		GC_json_data = $.parseJSON(GCdata);
		//console.log(tenure_json_data);
		d3Chart.addGraph({
			axisname: ['After'],
			id: 'Used Tenured(After)',
			type: 'analog',
			dataId: 513,
			yVal: ['After'],
			data: used_json_data
		});
		d3Chart.addGraph({
			axisname: ['After'],
			id: 'Free Tenured(After)',
			type: 'analog',
			dataId: 513,
			yVal: ['After'],
			data: tenure_json_data
		});
		d3Chart.addGraph({
			axisname: ['After'],
			id: 'Free Nursery(After)',
			type: 'analog',
			dataId: 513,
			yVal: ['After'],
			data: nursery_json_data
		});
		d3Chart.addGraph({
			axisname: ['GC Completed'],
			id: 'GC Completed',
			type: 'analog',
			dataId: 513,
			yVal: ['GC'],
			data: GC_json_data
		});
		//   d3Chart.addGraph({ id: 'DI', type: 'digital', name: 'Digital Input', dataId: 522, data: diData });

		//   d3Chart.addGraph({ id: 'Accel', type: 'analog', name: 'Accel', dataId: 522, yVal: ['X', 'Y', 'Z'], data: accelData });
		d3Chart.render();

		<!-- setTimeout(function () {	 -->
		<!-- d3Chart.reorderGraph('Accel', 'up'); -->
		<!-- }, 3000); -->

	});

});