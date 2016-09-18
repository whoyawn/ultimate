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
		});

	});

	$scope.changemode = function(key, newState){
		if (['time', 'follow', 'alarm'].indexOf(newState) === -1) return;
		firebase.database().ref('Group/' + key + '/').update({state: newState});
 	}

}]);