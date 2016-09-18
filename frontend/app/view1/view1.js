'use strict';

angular.module('myApp.view1', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/view1', {
    templateUrl: 'view1/view1.html',
    controller: 'View1Ctrl'
  });
}])

.controller('View1Ctrl', ['$scope', '$timeout', function($scope, $timeout) {

	firebase.database().ref('Group').on('value', function(snapshot){
		if(!snapshot.val()) return;
		$timeout(function(){
			$scope.group = snapshot.val();
			for (var key in $scope.group){
				if (!$scope.group[key].alarms) return;
				$scope.group[key].alarms.forEach(function(alarm){
					alarm.newDuration = alarm.duration;
					alarm.newSetoffTime = new Date(2016, 9, 18, alarm.setoffTime/100, alarm.setoffTime%100);

					alarm.setoffTime = formatAPMP((alarm.setoffTime));
					alarm.duration = alarm.duration / 60 + " min";
				});
				
			};
		});

	});

	$scope.changemode = function(key, newState){
		if (['time', 'follow', 'alarm'].indexOf(newState) === -1) return;
		firebase.database().ref('Group/' + key + '/').update({state: newState});
 	}

 	function formatAPMP(alarmTime) {
 		alarmTime = Number.parseInt(alarmTime);
    var hours 	= alarmTime/100;
    var minutes = alarmTime % 100;
    var ampm 	= hours >= 12 ? ' pm' : ' am';
    hours 		= hours % 12;
    hours 		= hours ? hours : 12; // the hour '0' should be '12'
    minutes 	= minutes < 10 ? '0' + minutes : minutes;
    var strTime = hours + ':' + minutes + ampm;
    return strTime;
}


}]);


