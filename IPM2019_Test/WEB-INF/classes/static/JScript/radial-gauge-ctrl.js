app.controller('RadialGaugeCtrl', ['$scope', function ($scope) {
	var val = localStorage.getItem("gauge_value");
	console.log(val);
    $scope.value = Number(val);
    $scope.upperLimit = 100;
    $scope.lowerLimit = 0;
    $scope.unit = "%";
    $scope.precision = 0;
    $scope.ranges = [
        {
            min: 0,
            max: 20,
            color: '#DEDEDE'
        },
        {
            min: 21,
            max: 40,
            color: '#8DCA2F'
        },
        {
            min: 41,
            max: 60,
            color: '#FDC702'
        },
        {
            min: 61,
            max: 80,
            color: '#FF7700'
        },
        {
            min: 81,
            max: 100,
            color: '#C50200'
        }
    ];


}]);
