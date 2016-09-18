'use strict';

angular.module('myApp.view1', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/view1', {
    templateUrl: 'view1/view1.html',
    controller: 'View1Ctrl'
  });
}])

.controller('View1Ctrl', ['$scope', '$timeout', function($scope, $timeout) {

	var globalkey;
	firebase.database().ref('Group').on('value', function(snapshot){
		if(!snapshot.val()) return;
		$timeout(function(){
			$scope.group = snapshot.val();
			for (var key in $scope.group){
				if (!$scope.group[key].alarms) return;
				//format the alarms
				$scope.group[key].alarms.forEach(function(alarm){
					alarm.newDuration = alarm.duration/60;
					alarm.newSetoffTime = new Date(2016, 9, 18, alarm.setoffTime/100, alarm.setoffTime%100);
					alarm.setoffTime = formatAPMP((alarm.setoffTime));
					alarm.duration = Math.round(alarm.duration/60) + " min";
				});
				globalkey = key;

				$scope.group[key].newState = $scope.group[key].state;
				$scope.newState = $scope.group[key].state;
				$scope.group[key].warnings = [];
				
				//format the sleep/wake times
				if ($scope.group[key].waketime) {
					$scope.group[key].waketimeFormatted = formatAPMP($scope.group[key].waketime);
					$scope.group[key].newWakeTime = new Date(2016, 9, 19, $scope.group[key].waketime/100, $scope.group[key].waketime%100);
				} else {
					$scope.group[key].newWakeTime = new Date(2016, 9, 19, 7, 0);
					$scope.group[key].warnings.push("Please enter your approximate wakeup time.");
					
				}
				if ($scope.group[key].bedtime){
					$scope.group[key].bedtimeFormatted = formatAPMP($scope.group[key].bedtime);
					$scope.group[key].newBedTime = new Date(2016, 9, 19, $scope.group[key].bedtime/100, $scope.group[key].bedtime%100);
				} else {
					$scope.group[key].newBedTime = new Date(2016, 9, 19, 7, 0);
					$scope.group[key].warnings.push("Please enter your approximate bedtime.");
				}


				
			}
		}); // end timeout

	}); // end firebase retreive data

	$scope.changemode = function(key, newState, stateEdit){
		if (['time', 'follow', 'alarm'].indexOf(newState) === -1) return;
		firebase.database().ref('Group/' + key + '/').update({state: newState});
 	};

 	$scope.$watch('group.group1.newState', function(newValue, oldValue){
 		console.log(newValue);
 		if (newValue !== oldValue) {
 			firebase.database().ref('Group/group1/').update({state: newValue});
 		}
 		

 	});

 	// save alarm info to firebase
 	$scope.saveAlarmEdits = function(index, alarm, key){
 		if (!$scope.group[key].alarms[index]) return;

 		//get military time representation from alarm.newSetoffTime
 		var militaryTime = alarm.newSetoffTime.getHours() * 100 + alarm.newSetoffTime.getMinutes()%100;
 		//get new duration from input
 		var duration = parseInt(alarm.newDuration)*60;

 		//save it
 		firebase.database().ref('Group/' + key).once('value', function(snapshot){
 			if (!snapshot.val()) return;
 			var alarms = snapshot.val().alarms;
 			alarms[index] = {duration: duration, setoffTime: militaryTime};
 			firebase.database().ref('Group/' + key).update({alarms: alarms});
 			$timeout(function(){
 				alarm.edit=false;
 			});
 		});
 	};

 	$scope.changeAwakeTime = function(groupname, key){
 		if (!(groupname.newBedTime && groupname.newWakeTime)) return console.log("err");
 		var bedtime = groupname.newBedTime.getHours()*100 + groupname.newBedTime.getMinutes();
 		var waketime = groupname.newWakeTime.getHours()*100 + groupname.newWakeTime.getMinutes();
 		firebase.database().ref('Group/' + key).update({bedtime:bedtime, waketime: waketime});
 	};

 	function formatAPMP(alarmTime) {
 		alarmTime = Number.parseInt(alarmTime);
	    var hours 	= Math.floor(alarmTime/100);
	    var minutes = alarmTime % 100;
	    var ampm 	= hours >= 12 ? ' pm' : ' am';
	    hours 		= hours % 12;
	    hours 		= hours ? hours : 12; // the hour '0' should be '12'
	    minutes 	= minutes < 10 ? '0' + minutes : minutes;
	    var strTime = hours + ':' + minutes + ampm;
	    return strTime;
	}


}]);


